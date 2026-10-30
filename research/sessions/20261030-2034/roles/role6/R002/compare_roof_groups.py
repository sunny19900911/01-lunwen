"""Existing N12/N24 coefficients and caches only; no fitting or new kernels."""
from pathlib import Path
import csv,json,hashlib
from datetime import datetime,timezone,timedelta
import numpy as np
HERE=Path(__file__).resolve().parent
SESSION=HERE.parents[2]
BASE=SESSION/"root-R001-low-order"
EXT=SESSION/"roles/role4/R001"
START="2026-10-30T20:49:25+08:00"
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cs(name,rows):
    with (HERE/name).open("x",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(name,obj):
    with (HERE/name).open("x",encoding="utf-8") as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False)
m12=read(BASE/"models-small.json")
m24=read(EXT/"models-small-N24.json")
manifest=read(EXT/"delivery-manifest.json")
cache=EXT/"local-cache/N24-two-operator-traces.npz"
assert sha(cache)==manifest["local_only_array"]["sha256"]
assert sha(EXT/"models-small-N24.json")==next(x["sha256"] for x in manifest["files"] if x["name"]=="models-small-N24.json")
with (BASE/"prediction-errors-96.csv").open(encoding="utf-8-sig",newline="") as f:
    oldmetrics={(r["variant"],r["Case"],r["Story"],float(r["zeta"])):r for r in csv.DictReader(f)}
prefixrows=[];newrows=[];resrows=[];max12metricerr=0.;max12cacheerr=0.;maxidentity=0.
with np.load(cache,allow_pickle=False) as z24,np.load(BASE/"local-cache/primary-reference-traces.npz",allow_pickle=False) as z12:
    for op in ["elastic","balance"]:
        a=np.array(m12[f"N12_{op}_rc1e-10"]["raw_output_coef"])[:,1]
        b=np.array(m24[f"N24_{op}_rc1e-10"]["raw_output_coef"])[:,1]
        assert np.all(b[:12]!=0)
        for case in ["SHW3X","SHW4X","RH4X"]:
            for z in [.05,.08]:
                tag=f"{op}__{case}__Story12__z{z:g}"
                t,y=z24[tag+"__t"],z24[tag+"__native"]
                v24=z24[tag+"__terms"]
                # Same frozen unit kernels: scale each existing term by the old/new coefficient ratio.
                v12=v24[:,:12]*(a/b[:12])[None,:]
                p12,p24=v12.sum(1),v24.sum(1)
                assert np.max(abs(p24-z24[tag+"__prediction"]))<1e-8
                if op=="elastic":
                    previous=z12[f"{case}__Story12__z{z:g}__terms"]
                    max12cacheerr=max(max12cacheerr,float(np.max(abs(v12-previous))))
                ref=oldmetrics[(f"N12_{op}_rc1e-10",case,"Story12",z)]
                norm=float(np.linalg.norm(y));peak=float(np.max(abs(y)));i=int(np.argmax(abs(y)))
                e12=float(np.linalg.norm(y-p12)/norm);e24=float(np.linalg.norm(y-p24)/norm)
                max12metricerr=max(max12metricerr,abs(e12-float(ref["NRMSE"])))
                g24=[]
                for group,j,k in [("1to3",0,3),("4to6",3,6),("7to12",6,12)]:
                    old,new=v12[:,j:k].sum(1),v24[:,j:k].sum(1)
                    g24.append(new)
                    delta=new-old
                    prefixrows.append({"operator":op,"Case":case,"Story":"Story12","zeta":z,"group":group,
                        "N12_group_peak_kN":float(np.max(abs(old))),"N24_group_peak_kN":float(np.max(abs(new))),
                        "N24_group_L2_over_native":float(np.linalg.norm(new)/norm),
                        "difference_L2_over_native":float(np.linalg.norm(delta)/norm),
                        "difference_L2_over_N24_group":float(np.linalg.norm(delta)/max(np.linalg.norm(new),1e-300)),
                        "difference_peak_over_native_peak":float(np.max(abs(delta))/peak),
                        "native_peak_time_s":float(t[i]),"native_signed_peak_kN":float(y[i]),
                        "N12_group_at_native_peak_kN":float(old[i]),"N24_group_at_native_peak_kN":float(new[i])})
                new=v24[:,12:24].sum(1);prefix=v24[:,:12].sum(1);dprefix=prefix-p12
                r12,r24=y-p12,y-p24;d=dprefix+new
                maxidentity=max(maxidentity,float(np.max(abs((r12-r24)-d))))
                g24.append(new)
                signed=np.array([g[i] for g in g24]);abs_sum=float(np.sum(abs(signed)))
                term_abs=float(np.sum(abs(v24[i])))
                newrows.append({"operator":op,"Case":case,"Story":"Story12","zeta":z,
                    "new_group":"13to24","new_group_peak_kN":float(np.max(abs(new))),
                    "new_group_RMS_kN":float(np.sqrt(np.mean(new**2))),
                    "new_group_L2_over_native":float(np.linalg.norm(new)/norm),
                    "new_group_peak_over_native_peak":float(np.max(abs(new))/peak),
                    "native_peak_time_s":float(t[i]),"native_signed_peak_kN":float(y[i]),
                    "g1to3_at_native_peak_kN":float(signed[0]),"g4to6_at_native_peak_kN":float(signed[1]),
                    "g7to12_at_native_peak_kN":float(signed[2]),"g13to24_at_native_peak_kN":float(signed[3]),
                    "N12_prediction_at_native_peak_kN":float(p12[i]),"N24_prediction_at_native_peak_kN":float(p24[i]),
                    "native_minus_N12_at_peak_kN":float(r12[i]),"native_minus_N24_at_peak_kN":float(r24[i]),
                    "chi_4groups_same_native_peak":None if abs_sum==0 else 1-abs(float(signed.sum()))/abs_sum,
                    "chi_24terms_same_native_peak":None if term_abs==0 else 1-abs(float(p24[i]))/term_abs,
                    "new_group_extension_stability":"not yet checked beyondN24; not unique physical contribution"})
                # Exact squared-error identity; these terms are accounting, not separate causal effects.
                new_gain=float((2*np.dot(r12,new)-np.dot(new,new))/norm**2)
                prefix_gain=float((2*np.dot(r12,dprefix)-np.dot(dprefix,dprefix))/norm**2)
                interaction=float(-2*np.dot(dprefix,new)/norm**2)
                reduction=e12**2-e24**2
                assert abs(new_gain+prefix_gain+interaction-reduction)<1e-12
                resrows.append({"operator":op,"Case":case,"Story":"Story12","zeta":z,
                    "N12_NRMSE":e12,"N24_NRMSE":e24,"actual_squared_NRMSE_decrease":reduction,
                    "prefix_change_L2_over_native":float(np.linalg.norm(dprefix)/norm),
                    "new_group_L2_over_native":float(np.linalg.norm(new)/norm),
                    "cosine_N12_residual_vs_new_group":float(np.dot(r12,new)/max(np.linalg.norm(r12)*np.linalg.norm(new),1e-300)),
                    "algebra_new_group_squared_error_gain":new_gain,
                    "algebra_prefix_change_squared_error_gain":prefix_gain,
                    "algebra_cross_term":interaction,
                    "scope":"exact algebraic error accounting, no isolated physical causal attribution"})
assert max12cacheerr<1e-8 and max12metricerr<1e-12 and maxidentity<1e-8
cs("roof-prefix-groups-36.csv",prefixrows)
cs("roof-new13to24-amplitudes-and-native-peak-12.csv",newrows)
cs("roof-residual-accounting-12.csv",resrows)
summ=[]
for op in ["elastic","balance"]:
    for group in ["1to3","4to6","7to12"]:
        r=[x for x in prefixrows if x["operator"]==op and x["group"]==group]
        summ.append({"operator":op,"group":group,
            "difference_L2_over_native_range":[min(x["difference_L2_over_native"] for x in r),max(x["difference_L2_over_native"] for x in r)],
            "difference_L2_over_N24_group_range":[min(x["difference_L2_over_N24_group"] for x in r),max(x["difference_L2_over_N24_group"] for x in r)]})
result={"status":"candidate existing-coefficient diagnostic; independent review pending","actual_start_local":START,
    "completed_local":datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
    "method":"N24cached terms times frozenN12/N24 coefficient ratio reconstruct same-kernel N12; no fitting or new SDOF calculation",
    "source_files":[{"path":str(p),"sha256":sha(p)} for p in [BASE/"models-small.json",EXT/"models-small-N24.json",cache]],
    "max_reconstructed_N12_terms_vs_root_elastic_cache_kN":max12cacheerr,
    "max_reconstructed_N12_NRMSE_vs_root_all_operators":max12metricerr,
    "max_residual_correction_identity_kN":maxidentity,
    "prefix_summary":summ,"new_group":newrows,"residual_summary":resrows,
    "N36_entry_status":"to be recorded at administrative freeze; no waiting or refit"}
js("results.json",result)
print(json.dumps({"completed":result["completed_local"],"prefix":summ,"new13to24":[{k:r[k] for k in ["operator","Case","zeta","new_group_L2_over_native","g13to24_at_native_peak_kN","native_signed_peak_kN","chi_4groups_same_native_peak"]} for r in newrows],"residual":[{k:r[k] for k in ["operator","Case","zeta","N12_NRMSE","N24_NRMSE","prefix_change_L2_over_native","new_group_L2_over_native","cosine_N12_residual_vs_new_group"]} for r in resrows]},ensure_ascii=False,indent=2))
