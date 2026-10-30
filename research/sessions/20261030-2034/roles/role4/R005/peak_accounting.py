from pathlib import Path
from datetime import datetime,timezone
import json,csv,hashlib
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R003'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rule=json.loads((O/'cache-key-verification.json').read_text(encoding='utf-8'))
cache=Path(rule['cache_path']);assert sha(cache)==rule['cache_sha256']
src=P/'native-all12-peak-change-36.csv';srcsha=sha(src)
baseline=list(csv.DictReader(src.open(encoding='utf-8-sig')));assert len(baseline)==36
out=[];rechecks=[]
with np.load(cache,allow_pickle=False) as a:
    for case in rule['cases']:
        for story in rule['stories']:
            k5=f'N36__{case}__{story}__z0.05__';k8=f'N36__{case}__{story}__z0.08__'
            t=a[k5+'t'];v5=a[k5+'native'];v8=a[k8+'native'];assert np.array_equal(t,a[k8+'t'])
            i=int(np.argmax(abs(v5)));j=int(np.argmax(abs(v8)));P5=float(abs(v5[i]));P8=float(abs(v8[j]));assert P5>0
            s0=int(np.sign(v5[i]));s8=int(np.sign(v8[j]));v8t0=float(v8[i]);v5t8=float(v5[j]);D=float(s0*(v5[i]-v8[i]));M=float(P8-s0*v8[i]);net=P5-P8;err=net-(D-M)
            assert M>=0 and abs(err)<1e-9
            tol=1e-9*max(1,P8)
            oldstill=bool(abs(abs(v8[i])-P8)<=tol);signstill=bool(abs(s0*v8[i]-P8)<=tol)
            d=dict(Case=case,Story=story,Location='Bottom',Axis='X',P5_kN=P5,P8_kN=P8,t0_5pct_abspeak_s=float(t[i]),t8_8pct_abspeak_s=float(t[j]),peak_time_shift_s=float(t[j]-t[i]),s0=s0,s8=s8,V5_t0_kN=float(v5[i]),V8_t0_kN=v8t0,V5_t8_kN=v5t8,V8_t8_kN=float(v8[j]),D_same_time_signed_decrease_kN=D,M_peak_reselection_correction_kN=M,net_peak_decrease_kN=net,D_over_P5=D/P5,M_over_P5=M/P5,net_decrease_over_P5=net/P5,D_percent_P5=100*D/P5,M_percent_P5=100*M/P5,net_peak_decrease_percent=100*net/P5,time_argmax_changed=i!=j,old_anchor_still_8pct_abspeak=oldstill,old_anchor_still_8pct_signed_control=signstill,M_zero_within_tolerance=M<=tol,control_sign_changed=s0!=s8,abspeak5_exact_tie_count=int(np.count_nonzero(abs(v5)==P5)),abspeak8_exact_tie_count=int(np.count_nonzero(abs(v8)==P8)),identity_error_kN=err)
            b=next(q for q in baseline if q['Case']==case and q['Story']==story)
            diffs={key:float(d[field])-float(b[key]) for key,field in [('peak5_kN','P5_kN'),('peak8_kN','P8_kN'),('peak5_time_s','t0_5pct_abspeak_s'),('peak8_time_s','t8_8pct_abspeak_s'),('V8_at_5peak_kN','V8_t0_kN'),('V5_at_8peak_kN','V5_t8_kN'),('native_peak_decrease_percent','net_peak_decrease_percent')]}
            assert max(abs(x) for x in diffs.values())<1e-9
            d['native_SourceRow5']=int(b['source_row5']);d['native_SourceRow8']=int(b['source_row8'])
            out.append(d);rechecks.append(dict(Case=case,Story=story,max_difference_vs_R003=max(abs(x) for x in diffs.values())))
with (O/'native-peak-accounting-all12-36.csv').open('x',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
rank=sorted(out,key=lambda d:d['M_over_P5'],reverse=True);best=rank[0];zeros=[d for d in out if d['M_zero_within_tolerance']]
summary=dict(completed_utc=datetime.now(timezone.utc).isoformat(),rows=len(out),no_peak_reselection_count=len(zeros),no_time_argmax_change_count=sum(not d['time_argmax_changed'] for d in out),old_anchor_still_abspeak_count=sum(d['old_anchor_still_8pct_abspeak'] for d in out),control_sign_changed_count=sum(d['control_sign_changed'] for d in out),max_identity_error_kN=max(abs(d['identity_error_kN']) for d in out),max_recheck_difference_vs_R003=max(d['max_difference_vs_R003'] for d in rechecks),strongest_peak_reselection_by_M_over_P5=best,top5=[{k:d[k] for k in ['Case','Story','t0_5pct_abspeak_s','t8_8pct_abspeak_s','D_percent_P5','M_percent_P5','net_peak_decrease_percent']} for d in rank[:5]],no_reselection_rows=[dict(Case=d['Case'],Story=d['Story'],t0_s=d['t0_5pct_abspeak_s'],t8_s=d['t8_8pct_abspeak_s'],M_kN=d['M_peak_reselection_correction_kN']) for d in zeros],source_native_table=dict(path=str(src),sha256=srcsha),source_cache=dict(path=str(cache),sha256=rule['cache_sha256']),method='native algebraic peak accounting; no causal phase shares, fit, order extension or trace output')
assert sha(src)==srcsha and sha(cache)==rule['cache_sha256']
(O/'results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
