"""Frozen-coefficient diagnostics only. No fit_map/lstsq or new coefficients."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS","2")
from pathlib import Path
import csv,json,hashlib,importlib.util
from datetime import datetime,timezone,timedelta
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
BASE=ROOT/"research/sessions/20261030-2034/root-R001-low-order"
START="2026-10-30T20:42:22+08:00"
def loadmod(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj
def csvout(name,rows):
    with (HERE/name).open("x",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def jsonout(name,obj):
    with (HERE/name).open("x",encoding="utf-8") as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False)
modelpath=BASE/"models-small.json"
models=json.loads(modelpath.read_text(encoding="utf-8"))
loader=ROOT/"research/sessions/20261025-1337/roles/role6/R001/load_inputs.py"
cfg,om,data=loadmod(loader,"loader_group019").load_inputs()
helper=loadmod(Path(cfg["modal_linear_py"]),"helper_group019")
svrows=[]
for name,m in models.items():
    s=np.array(m["singular_values"])
    assert m["rank"]==m["N"] and all(m["active"])
    svrows.append({"variant":name,"N":m["N"],"operator":m["operator"],"rcond":m["rcond"],
        "rank":m["rank"],"smax_RMS_column_normalized":float(s[0]),"smin_RMS_column_normalized":float(s[-1]),
        "smin_over_smax":float(s[-1]/s[0]),"condition_2_RMS_column_normalized":float(s[0]/s[-1]),
        "singular_values":json.dumps(s.tolist(),separators=(",",":"))})
features={}
for case,d in data.items():
    for z in [.05,.08]:
        Q,V,_=helper.states(d["ag"],om[:12],z,.02)
        features[case,z,"elastic"]=Q*om[:12]**2
        features[case,z,"balance"]=Q*om[:12]**2+V*(2*z*om[:12])
cache=BASE/"local-cache/primary-reference-traces.npz"
max_cache_diff=0.
terms={}
with np.load(cache,allow_pickle=False) as nativecache:
    for name,m in models.items():
        raw=np.array(m["raw_output_coef"])
        for case,d in data.items():
            for z in [.05,.08]:
                v=features[case,z,m["operator"]][:,:m["N"],None]*raw[None,:,:]
                terms[name,case,z]=v
                if name=="N12_elastic_rc1e-10":
                    for j,story in enumerate(["Story5","Story12"]):
                        old=nativecache[f"{case}__{story}__z{z:g}__terms"]
                        max_cache_diff=max(max_cache_diff,float(np.max(abs(v[:,:,j]-old))))
assert max_cache_diff<1e-7
groups=[("modes1to3",0,3),("modes4to6",3,6)]
amplitudes=[]
for (name,case,z),v in terms.items():
    for j,story in enumerate(["Story5","Story12"]):
        y=data[case]["Y0" if z==.05 else "Y3"][story]
        for group,i,k in groups:
            g=v[:,i:k,j].sum(1)
            amplitudes.append({"variant":name,"Case":case,"Story":story,"zeta":z,"group":group,
                "group_peak_kN":float(np.max(abs(g))),"native_peak_kN":float(np.max(abs(y))),
                "group_L2_over_native_L2":float(np.linalg.norm(g)/np.linalg.norm(y)),
                "group_peak_over_native_peak":float(np.max(abs(g))/np.max(abs(y)))})
comparisons=[]
for op in ["elastic","balance"]:
    for rc in ["1e-10","1e-08"]:
        comparisons.append(("N6_to_N12",f"N6_{op}_rc{rc}",f"N12_{op}_rc{rc}"))
    for n in [6,12]:
        comparisons.append(("rcond_change",f"N{n}_{op}_rc1e-10",f"N{n}_{op}_rc1e-08"))
diffrows=[]
for label,left,right in comparisons:
    for case,d in data.items():
        for z in [.05,.08]:
            for j,story in enumerate(["Story5","Story12"]):
                y=d["Y0" if z==.05 else "Y3"][story]
                for group,i,k in groups:
                    a=terms[left,case,z][:,i:k,j].sum(1)
                    b=terms[right,case,z][:,i:k,j].sum(1)
                    delta=b-a
                    diffrows.append({"comparison":label,"left":left,"right":right,"operator":models[right]["operator"],
                        "Case":case,"Story":story,"zeta":z,"group":group,
                        "group_difference_L2_over_native_L2":float(np.linalg.norm(delta)/np.linalg.norm(y)),
                        "group_difference_peak_kN":float(np.max(abs(delta))),
                        "group_difference_peak_over_native_peak":float(np.max(abs(delta))/np.max(abs(y))),
                        "group_difference_L2_over_right_group_L2":float(np.linalg.norm(delta)/max(np.linalg.norm(b),1e-300)),
                        "left_group_peak_kN":float(np.max(abs(a))),"right_group_peak_kN":float(np.max(abs(b)))})
coefrows=[]
for op in ["elastic","balance"]:
    a=np.array(models[f"N6_{op}_rc1e-10"]["raw_output_coef"])
    b=np.array(models[f"N12_{op}_rc1e-10"]["raw_output_coef"])[:6]
    for j,story in enumerate(["Story5","Story12"]):
        for i in range(6):
            coefrows.append({"operator":op,"Story":story,"Mode":i+1,"coef_N6":float(a[i,j]),
                "coef_N12":float(b[i,j]),"signed_difference_N12_minus_N6":float(b[i,j]-a[i,j]),
                "relative_to_abs_N12":float(abs(b[i,j]-a[i,j])/abs(b[i,j])) if b[i,j]!=0 else None,
                "identity":"fitted output reference coefficient; no physical single-mode certification"})
csvout("group-differences-192.csv",diffrows)
csvout("group-scales-192.csv",amplitudes)
csvout("normalized-singular-values-8.csv",svrows)
csvout("first6-coefficient-changes-24.csv",coefrows)
summary=[]
for op in ["elastic","balance"]:
    for story in ["Story5","Story12"]:
        for group,_,_ in groups:
            r=[x for x in diffrows if x["comparison"]=="N6_to_N12" and x["operator"]==op and x["Story"]==story and x["group"]==group]
            a=[x for x in amplitudes if x["variant"]==f"N12_{op}_rc1e-10" and x["Story"]==story and x["group"]==group]
            summary.append({"operator":op,"Story":story,"group":group,
                "N_change_L2_over_native_range":[min(x["group_difference_L2_over_native_L2"] for x in r),max(x["group_difference_L2_over_native_L2"] for x in r)],
                "N_change_L2_over_group_range":[min(x["group_difference_L2_over_right_group_L2"] for x in r),max(x["group_difference_L2_over_right_group_L2"] for x in r)],
                "N_change_peak_over_native_peak_max":max(x["group_difference_peak_over_native_peak"] for x in r),
                "N_change_peak_kN_max":max(x["group_difference_peak_kN"] for x in r),
                "N12_group_L2_over_native_range":[min(x["group_L2_over_native_L2"] for x in a),max(x["group_L2_over_native_L2"] for x in a)]})
assert len(diffrows)==len(amplitudes)==192 and len(coefrows)==24
result={"status":"candidate numerical diagnostics; independent review pending","start_local":START,
    "completed_local":datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
    "sources":[{"path":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in [modelpath,cache,loader,Path(cfg["modal_linear_py"])]],
    "primary_recomputed_terms_max_abs_vs_root_cache_kN":max_cache_diff,
    "max_rcond_change_L2_over_native":max(x["group_difference_L2_over_native_L2"] for x in diffrows if x["comparison"]=="rcond_change"),
    "summary":summary,"svd":svrows,"coefficient_changes":coefrows,
    "method":"Fixed existing coefficients only. At most12 independent modal kernels per case/state; no fitting, source models unchanged.",
    "scope":"Group stability within declared N/operator/SVD variants, not true physical single-mode uniqueness. Story12 large total-model error blocks fine decomposition."}
jsonout("results.json",result)
print(json.dumps({k:result[k] for k in ["completed_local","primary_recomputed_terms_max_abs_vs_root_cache_kN","max_rcond_change_L2_over_native","summary"]},ensure_ascii=False,indent=2))
