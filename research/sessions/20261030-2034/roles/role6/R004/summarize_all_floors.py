"""Full-floor frozen-table/cache summary only; no fitting or array export."""
from pathlib import Path
import csv,json,hashlib
from datetime import datetime,timezone,timedelta
import numpy as np
HERE=Path(__file__).resolve().parent
SESSION=HERE.parents[2]
SOURCE=SESSION/"roles/role4/R003"
START="2026-10-30T21:11:05+08:00"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readjson(p):return json.loads(p.read_text(encoding="utf-8"))
def cs(name,rows):
    with (HERE/name).open("x",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
manifest=readjson(SOURCE/"delivery-manifest.json")
names=["all12-same-time-low-high-residual-288.csv","all12-low-high-N24-to-N36-144.csv",
       "native-all12-peak-change-36.csv","all12-prediction-errors-144.csv"]
sources=[];tables={}
for name in names:
    path=SOURCE/name
    expected=next(r["sha256"] for r in manifest["files"] if r["name"]==name)
    assert sha(path)==expected
    sources.append({"path":str(path),"sha256":expected})
    with path.open(encoding="utf-8-sig",newline="") as f:tables[name]=list(csv.DictReader(f))
cache=SOURCE/manifest["local_only_array"]["path"]
assert sha(cache)==manifest["local_only_array"]["sha256"]
sources.append({"path":str(cache),"sha256":manifest["local_only_array"]["sha256"]})
peaks={(r["Story"],r["Case"],float(r["zeta"])):r for r in tables[names[0]] if r["N"]=="36" and r["anchor"]=="native_peak"}
stability={(r["Story"],r["Case"],float(r["zeta"]),r["group"]):r for r in tables[names[1]]}
native={(r["Story"],r["Case"]):r for r in tables[names[2]]}
errors={(r["Story"],r["Case"],float(r["zeta"])):r for r in tables[names[3]] if r["N"]=="36"}
assert len(peaks)==72 and len(native)==36 and len(stability)==144
rows=[];anchor_records=[];max_identity=0.;max_group_prediction_closure=0.
with np.load(cache,allow_pickle=False) as z:
    for floor in range(1,13):
        story=f"Story{floor}"
        for case in ["SHW3X","SHW4X","RH4X"]:
            n=native[story,case]
            row={"Story":story,"Case":case,"N":36,"operator":"elastic",
                "native_peak_reduction_percent":float(n["native_peak_decrease_percent"])}
            signals={}
            for damp,label in [(.05,"5"),(.08,"8")]:
                p=peaks[story,case,damp]
                tag=f"N36__{case}__{story}__z{damp:g}"
                t,y,lo,hi,pred=[z[tag+"__"+k] for k in ["t","native","low1to12","represented_high13plus","prediction"]]
                closure=float(np.max(abs(lo+hi-pred)))
                max_group_prediction_closure=max(max_group_prediction_closure,closure)
                assert closure<max(1e-8,5e-11*float(np.max(abs(pred))))
                idx=int(np.argmax(abs(y)));assert t[idx]==float(p["time_s"])
                assert abs(lo[idx]-float(p["low1to12_kN"]))<1e-8
                assert abs(hi[idx]-float(p["represented_high13plus_kN"]))<1e-8
                l,h,total,res,yn=[float(p[k]) for k in ["low1to12_kN","represented_high13plus_kN","prediction_kN","residual_native_minus_prediction_kN","native_kN"]]
                assert abs(l+h+res-yn)<max(1e-8,5e-11*abs(yn)) and yn!=0
                ratios=[l/yn,h/yn,res/yn]
                flags=[]
                for item,value in zip(["low","high","residual"],ratios):
                    if value<0:flags.append(item+"_reverse")
                    if value>1:flags.append(item+"_over1")
                row.update({f"native{label}_peak_time_s":float(p["time_s"]),f"native{label}_signed_peak_kN":yn,
                    f"low{label}_at_native_peak_kN":l,f"high{label}_at_native_peak_kN":h,
                    f"prediction{label}_at_native_peak_kN":total,f"residual{label}_at_native_peak_kN":res,
                    f"low{label}_signed_over_native":ratios[0],f"high{label}_signed_over_native":ratios[1],
                    f"residual{label}_signed_over_native":ratios[2],
                    f"chi{label}_at_native_peak":float(p["two_reference_group_cancellation"]),
                    f"flags{label}":";".join(flags),f"N36_NRMSE{label}":float(errors[story,case,damp]["NRMSE"])})
                signals[damp]={"t":t,"y":y,"g":np.column_stack([lo,hi]),"p":pred,"idx":idx}
                for group,short in [("low1to12","low"),("represented_high13plus","high")]:
                    s=stability[story,case,damp,group]
                    row[f"N24to36_{short}{label}_difference_over_native_L2"]=float(s["difference_L2_over_native_L2"])
                    row[f"N24to36_{short}{label}_difference_over_N24_group_L2"]=float(s["difference_L2_over_N24_group_L2"])
                    row[f"N24to36_{short}{label}_difference_RMS_kN"]=float(s["difference_RMS_kN"])
                assert abs(sum(ratios)-1)<5e-11
            old,new=signals[.05],signals[.08]
            assert np.array_equal(old["t"],new["t"])
            a5=np.max(abs(old["g"]),axis=0);a8=np.max(abs(new["g"]),axis=0)
            assert min(a5)>0 and min(a8)>0
            h5,h8=old["g"]/a5,new["g"]/a8
            amp=(a8-a5)*(h8+h5)/2;wave=(a8+a5)*(h8-h5)/2
            max_identity=max(max_identity,float(np.max(abs(new["g"]-old["g"]-amp-wave))))
            for j,short in enumerate(["low","high"]):
                row[f"{short}_A5_kN"]=float(a5[j]);row[f"{short}_A8_kN"]=float(a8[j])
                row[f"{short}_group_amplitude_reduction_percent"]=float(100*(1-a8[j]/a5[j]))
                row[f"{short}_normalized_waveform_L2_change"]=float(np.linalg.norm(h8[:,j]-h5[:,j])/np.linalg.norm(h5[:,j]))
            for damp,anchor in [(.05,"native5_peak"),(.08,"native8_peak")]:
                idx=signals[damp]["idx"];av=float(amp[idx].sum());wv=float(wave[idx].sum())
                row[f"{anchor}_symmetric_amplitude_sum_kN"]=av
                row[f"{anchor}_normalized_waveform_sum_kN"]=wv
                row[f"{anchor}_wave_opposes_amplitude"]=av*wv<0
                anchor_records.append({"Story":story,"Case":case,"anchor":anchor,"amp":av,"wave":wv,
                    "opposes":av*wv<0})
            row["scope"]="signed fitted output groups; native=low+represented_high+residual; ownstate peaks differ; no energy-share meaning"
            rows.append(row)
assert len(rows)==36 and max_identity<1e-7
cs("all12-three-input-summary-36.csv",rows)
floor_summary=[]
for i in range(1,13):
    s=f"Story{i}";r=[x for x in rows if x["Story"]==s]
    hr=[x[f"high{d}_signed_over_native"] for x in r for d in ["5","8"]]
    lr=[x[f"low{d}_signed_over_native"] for x in r for d in ["5","8"]]
    rr=[x[f"residual{d}_signed_over_native"] for x in r for d in ["5","8"]]
    floor_summary.append({"Story":s,"signed_high_over_native_range":[min(hr),max(hr)],
        "signed_low_over_native_range":[min(lr),max(lr)],"signed_residual_over_native_range":[min(rr),max(rr)],
        "chi_max":max(x[f"chi{d}_at_native_peak"] for x in r for d in ["5","8"]),
        "N24to36_low_over_native_max":max(x[f"N24to36_low{d}_difference_over_native_L2"] for x in r for d in ["5","8"]),
        "N24to36_high_over_native_max":max(x[f"N24to36_high{d}_difference_over_native_L2"] for x in r for d in ["5","8"]),
        "native_reductions":{x["Case"]:x["native_peak_reduction_percent"] for x in r}})
peakstats=[{"Story":x["Story"],"Case":x["Case"],"zeta":d/100,
    "chi":x[f"chi{label}_at_native_peak"],"lowratio":x[f"low{label}_signed_over_native"],
    "highratio":x[f"high{label}_signed_over_native"],"residualratio":x[f"residual{label}_signed_over_native"]}
    for x in rows for d,label in [(5,"5"),(8,"8")]]
amp_increase=[{"Story":x["Story"],"Case":x["Case"],"group":g,"amplitude_reduction_percent":x[f"{g}_group_amplitude_reduction_percent"]}
              for x in rows for g in ["low","high"] if x[f"{g}_group_amplitude_reduction_percent"]<0]
result={"status":"candidate full-floor interpretation; role2 numerical audit pending","start_local":START,
    "completed_local":datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
    "sources":sources,"row_count":36,"floor_summary":floor_summary,
    "peak_summary":{"n":72,"low_magnitude_exceeds_high_count":sum(abs(x["lowratio"])>abs(x["highratio"]) for x in peakstats),
        "opposite_low_high_count":sum(x["lowratio"]*x["highratio"]<0 for x in peakstats),
        "zero_chi_count":sum(abs(x["chi"])<=1e-12 for x in peakstats),
        "positive_chi_entries":[x for x in peakstats if x["chi"]>1e-12],
        "max_chi":max(peakstats,key=lambda x:x["chi"]),
        "low_ratio_over1_count":sum(x["lowratio"]>1 for x in peakstats),
        "high_ratio_over1_count":sum(x["highratio"]>1 for x in peakstats)},
    "amplitude_increases":amp_increase,
    "group_amplitude_reduction_ranges":{g:[min(x[f"{g}_group_amplitude_reduction_percent"] for x in rows),max(x[f"{g}_group_amplitude_reduction_percent"] for x in rows)] for g in ["low","high"]},
    "same_anchor_waveform_opposes_amplitude_count":sum(x["opposes"] for x in anchor_records),
    "same_anchor_count":len(anchor_records),"symmetric_identity_max_abs_error_kN":max_identity,
    "max_existing_group_prediction_float_closure_kN":max_group_prediction_closure,
    "closure_check_tolerance":"max(1e-8 kN,5e-11*signal_peak); check only, no effect on signed classification",
    "scope":"all twelve floors, three native X inputs, both damping states; represented fitted low/high groups only, not true modal or energy fractions; no full arrays exported"}
with (HERE/"results.json").open("x",encoding="utf-8") as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False)
print(json.dumps({k:result[k] for k in ["completed_local","floor_summary","peak_summary","amplitude_increases","group_amplitude_reduction_ranges","same_anchor_waveform_opposes_amplitude_count","symmetric_identity_max_abs_error_kN"]},ensure_ascii=False,indent=2))
