"""Existing elastic N24/N36 caches: merged groups and cross-state same-time identities."""
from pathlib import Path
import json,csv,hashlib
from datetime import datetime,timezone,timedelta
import numpy as np
HERE=Path(__file__).resolve().parent
SESSION=HERE.parents[2]
P24=SESSION/"roles/role4/R001"
P36=SESSION/"roles/role4/R002"
START="2026-10-30T21:02:27+08:00"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cs(name,rows):
    with (HERE/name).open("x",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(name,obj):
    with (HERE/name).open("x",encoding="utf-8") as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False)
sources=[]
for folder,modelname in [(P24,"models-small-N24.json"),(P36,"models-small-N36.json")]:
    man=read(folder/"delivery-manifest.json")
    for file,expected in [(folder/modelname,next(r["sha256"] for r in man["files"] if r["name"]==modelname)),
                          (folder/man["local_only_array"]["path"],man["local_only_array"]["sha256"])]:
        assert sha(file)==expected
        sources.append({"path":str(file),"sha256":expected})
traces={}
with np.load(P24/"local-cache/N24-two-operator-traces.npz",allow_pickle=False) as a,np.load(P36/"local-cache/N36-elastic-two-rcond-traces.npz",allow_pickle=False) as b:
    for vid,source,prefix in [("N24_rc1e-10",a,"elastic"),("N36_rc1e-10",b,"N36_elastic_rc1e-10"),("N36_rc1e-08",b,"N36_elastic_rc1e-08")]:
        for case in ["SHW3X","SHW4X","RH4X"]:
            for z in [.05,.08]:
                tag=f"{prefix}__{case}__Story12__z{z:g}"
                t,y,v,p=[source[tag+"__"+name] for name in ["t","native","terms","prediction"]]
                groups=np.column_stack([v[:,:12].sum(1),v[:,12:].sum(1)])
                assert np.max(abs(groups.sum(1)-p))<1e-7
                traces[vid,case,z]={"t":t,"y":y,"g":groups,"p":p}
stability=[]
for rc in ["1e-10","1e-08"]:
    vid=f"N36_rc{rc}"
    for case in ["SHW3X","SHW4X","RH4X"]:
        for z in [.05,.08]:
            a,b=traces["N24_rc1e-10",case,z],traces[vid,case,z]
            assert np.array_equal(a["t"],b["t"]) and np.array_equal(a["y"],b["y"])
            y=a["y"]
            for j,group in enumerate(["low1to12","high13plus"]):
                old,new=a["g"][:,j],b["g"][:,j];d=new-old
                stability.append({"comparison":"N24_to_"+vid,"Case":case,"Story":"Story12","zeta":z,"group":group,
                    "N24_modes":"1to12" if j==0 else "13to24","N36_modes":"1to12" if j==0 else "13to36",
                    "N24_peak_kN":float(np.max(abs(old))),"N36_peak_kN":float(np.max(abs(new))),
                    "difference_L2_over_native":float(np.linalg.norm(d)/np.linalg.norm(y)),
                    "difference_L2_over_N24_group":float(np.linalg.norm(d)/np.linalg.norm(old)),
                    "difference_peak_kN":float(np.max(abs(d))),
                    "difference_peak_over_native_peak":float(np.max(abs(d))/np.max(abs(y))),
                    "N24_NRMSE":float(np.linalg.norm(a["p"]-y)/np.linalg.norm(y)),
                    "N36_NRMSE":float(np.linalg.norm(b["p"]-y)/np.linalg.norm(y))})
same_time=[];decomp=[];amplitudes=[];max_identity=0.
for vid in ["N24_rc1e-10","N36_rc1e-10","N36_rc1e-08"]:
    for case in ["SHW3X","SHW4X","RH4X"]:
        old,new=[traces[vid,case,z] for z in [.05,.08]]
        assert np.array_equal(old["t"],new["t"])
        A5=np.max(abs(old["g"]),axis=0);A8=np.max(abs(new["g"]),axis=0)
        assert min(A5)>0 and min(A8)>0
        h5,h8=old["g"]/A5[None,:],new["g"]/A8[None,:]
        amp=(A8-A5)[None,:]*(h8+h5)/2
        wave=(A8+A5)[None,:]*(h8-h5)/2
        err=float(np.max(abs((new["g"]-old["g"])-amp-wave)))
        max_identity=max(max_identity,err)
        for j,group in enumerate(["low1to12","high13plus"]):
            amplitudes.append({"variant":vid,"Case":case,"Story":"Story12","group":group,
                "A5_kN":float(A5[j]),"A8_kN":float(A8[j]),"A8_over_A5":float(A8[j]/A5[j]),
                "amplitude_reduction":float(1-A8[j]/A5[j]),
                "identity":"peak of fitted group full signed history; not native unique modal peak"})
        for anchor,idx in [("native5_peak",int(np.argmax(abs(old["y"])))),("native8_peak",int(np.argmax(abs(new["y"]))))]:
            denom5=float(np.sum(abs(old["g"][idx])));denom8=float(np.sum(abs(new["g"][idx])))
            row={"variant":vid,"Case":case,"Story":"Story12","anchor":anchor,"time_s":float(old["t"][idx]),
                "low5_same_t_kN":float(old["g"][idx,0]),"high5_same_t_kN":float(old["g"][idx,1]),
                "low8_same_t_kN":float(new["g"][idx,0]),"high8_same_t_kN":float(new["g"][idx,1]),
                "prediction5_same_t_kN":float(old["p"][idx]),"prediction8_same_t_kN":float(new["p"][idx]),
                "native5_same_t_kN":float(old["y"][idx]),"native8_same_t_kN":float(new["y"][idx]),
                "chi5_same_t":1-abs(float(old["g"][idx].sum()))/denom5 if denom5 else None,
                "chi8_same_t":1-abs(float(new["g"][idx].sum()))/denom8 if denom8 else None,
                "prediction_change_same_t_kN":float(new["p"][idx]-old["p"][idx]),
                "sum_symmetric_amplitude_terms_kN":float(amp[idx].sum()),
                "sum_normalized_waveform_terms_kN":float(wave[idx].sum()),
                "native_change_same_t_kN":float(new["y"][idx]-old["y"][idx]),
                "scope":"both states sampled at one common native anchor; not subtraction of ownpeak terms"}
            assert abs(row["prediction_change_same_t_kN"]-row["sum_symmetric_amplitude_terms_kN"]-row["sum_normalized_waveform_terms_kN"])<1e-7
            same_time.append(row)
            for j,group in enumerate(["low1to12","high13plus"]):
                decomp.append({"variant":vid,"Case":case,"Story":"Story12","anchor":anchor,"time_s":row["time_s"],"group":group,
                    "A5_kN":float(A5[j]),"A8_kN":float(A8[j]),"v5_same_t_kN":float(old["g"][idx,j]),
                    "v8_same_t_kN":float(new["g"][idx,j]),"h5_same_t":float(h5[idx,j]),"h8_same_t":float(h8[idx,j]),
                    "delta_v_same_t_kN":float(new["g"][idx,j]-old["g"][idx,j]),
                    "symmetric_amplitude_term_kN":float(amp[idx,j]),"normalized_waveform_term_kN":float(wave[idx,j]),
                    "sum_decomposition_kN":float(amp[idx,j]+wave[idx,j]),"scope":"exact group signal identity; waveform term is not pure phase"})
cs("merged-low-high-stability-24.csv",stability)
cs("cross-state-native-anchors-18.csv",same_time)
cs("symmetric-group-decomposition-36.csv",decomp)
cs("group-amplitudes-18.csv",amplitudes)
summary=[]
for group in ["low1to12","high13plus"]:
    r=[x for x in stability if x["group"]==group]
    summary.append({"group":group,"L2_difference_over_native_range":[min(x["difference_L2_over_native"] for x in r),max(x["difference_L2_over_native"] for x in r)],
        "L2_difference_over_N24_group_range":[min(x["difference_L2_over_N24_group"] for x in r),max(x["difference_L2_over_N24_group"] for x in r)],
        "max_peak_difference_kN":max(x["difference_peak_kN"] for x in r),
        "max_peak_difference_over_native_peak":max(x["difference_peak_over_native_peak"] for x in r)})
rc_difference=max(float(np.max(abs(traces["N36_rc1e-10",c,z]["g"]-traces["N36_rc1e-08",c,z]["g"]))) for c in ["SHW3X","SHW4X","RH4X"] for z in [.05,.08])
result={"status":"candidate merged-group diagnostic; independent review pending","actual_start_local":START,
    "completed_local":datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
    "operator":"elastic only, common available N24/N36 operator; no balance extrapolation",
    "no_new_fit_or_kernels":True,"sources":sources,"stability_summary":summary,
    "N36_max_abs_group_difference_between_rconds_kN":rc_difference,
    "full_time_symmetric_identity_max_abs_error_kN":max_identity,
    "formula":"v=A h; delta_v=delta_A*(h8+h5)/2+(A8+A5)*(h8-h5)/2; A=max_t abs(v); separate identical-time anchors",
    "same_time_rows":same_time,"amplitude_rows":amplitudes,
    "scope":"finite N24/N36 fitted-group stability, no individual high-mode uniqueness, no pure-phase attribution"}
js("results.json",result)
print(json.dumps({"completed":result["completed_local"],"stability":summary,"rcond_group_difference":rc_difference,"identity_error":max_identity,
    "N36_main_amplitudes":[x for x in amplitudes if x["variant"]=="N36_rc1e-10"],
    "N36_main_anchors":[{k:x[k] for k in ["Case","anchor","time_s","low5_same_t_kN","high5_same_t_kN","low8_same_t_kN","high8_same_t_kN","chi5_same_t","chi8_same_t","sum_symmetric_amplitude_terms_kN","sum_normalized_waveform_terms_kN"]} for x in same_time if x["variant"]=="N36_rc1e-10"]},ensure_ascii=False,indent=2))
