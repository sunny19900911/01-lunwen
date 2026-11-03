"""Baseline-only local peak selection, then actual-scheme checking; no solver."""
from pathlib import Path
import json,csv,hashlib,datetime
import numpy as np
S=Path(__file__).resolve().parent;R=S.parents[2];W=R.parent/'W5-重燃双塔连体'
O=S/'roles/screen';O.mkdir(parents=True,exist_ok=True)
assert not (O/'screening-216.csv').exists(),'Preserve completed output'
policy=json.loads((S/'near-peak-policy-freeze.json').read_text(encoding='utf-8'))
B=W/'02-数据/增阻尼多目标研究-20261016/原生0数据缓存';D=W/'research/maxwell-20261017/experiments/R001/core-cache'
mb=json.loads((B/'manifest.json').read_text(encoding='utf-8'));md=json.loads((D/'manifest.json').read_text(encoding='utf-8'))
tb=mb['tables']['Story Forces'];td=md['tables']['Story Forces']
cb=tb.get('columns',tb.get('value_columns'));cd=td.get('columns',td.get('value_columns'))
def mapping(tb):return {tuple(g['keys'][x]for x in ['Output Case','Story','Location']):k for k,g in tb['groups'].items()}
kb=mapping(tb);kd=mapping(td)
def local_peaks(y):
 # Collapse plateaux by first saved point, then use neighboring distinct levels.
 start=np.r_[0,np.flatnonzero(np.diff(y)!=0)+1];v=y[start]
 return start[(v>=np.r_[-np.inf,v[:-1]])&(v>=np.r_[v[1:],-np.inf])]
def write(name,rr):
 with (O/name).open('x',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
rows=[];frozen=[];checks=[]
with np.load(B/tb['cache'],allow_pickle=False)as zb:
 for case in ['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']:
  for story in range(1,13):
   key=(case,f'Story{story}','Bottom');a=zb[kb[key]];t=a[:,cb.index('Time')];b=a[:,cb.index('V'+case[-1])]
   assert np.isfinite(b).all()and np.all(np.diff(t)>0)
   pb=float(np.max(abs(b)));lp=local_peaks(abs(b));ib=int(np.argmax(abs(b)))
   for eps in policy['sensitivity_gap_fractions']:
    ix=lp[abs(b[lp])>=(1-eps)*pb];assert len(ix)>0
    for j in ix:frozen.append({'Case':case,'Story':story,'epsilon':eps,'index':int(j),'time_s':float(t[j]),'B_signed_kN':float(b[j]),'baseline_gap_percent':100*(pb-abs(float(b[j])))/pb,'B_SourceRow':int(a[j,cb.index('SourceRow')])})
   checks.append((case,story,t.copy(),b.copy(),pb,ib))
write('baseline-candidates-frozen.csv',frozen)
freeze={'at':datetime.datetime.now().astimezone().isoformat(),'actual_arrays_read_before_freeze':0,'candidate_csv_sha256':hashlib.sha256((O/'baseline-candidates-frozen.csv').read_bytes()).hexdigest(),'policy_sha256':hashlib.sha256((S/'near-peak-policy-freeze.json').read_bytes()).hexdigest()}
(O/'candidate-freeze.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with np.load(D/td['cache'],allow_pickle=False)as zd:
 for case,story,t,b,pb,ib in checks:
  a=zd[kd[(case,f'Story{story}','Bottom')]];assert np.array_equal(t,a[:,cd.index('Time')])
  d=a[:,cd.index('V'+case[-1])];ip=int(np.argmax(abs(d)));pd=float(abs(d[ip]));lp=local_peaks(abs(b))
  for eps in policy['sensitivity_gap_fractions']:
   ix=lp[abs(b[lp])>=(1-eps)*pb];jj=int(ix[np.argmax(abs(d[ix]))]);candidate_peak=float(abs(d[jj]));dist=np.min(abs(t[ix]-t[ip]));err=100*(pd-candidate_peak)/pd
   mask=np.any(abs(t[:,None]-t[ix][None,:])<=policy['local_time_neighborhood_s']+1e-9,axis=1)
   near_peak=float(np.max(abs(d[mask])));nearerr=100*(pd-near_peak)/pd
   bc=float(abs(b[ip]));gap=100*(pb-bc)/pb
   b1=pb;b2=bc;d1=abs(float(d[ib]));d2=pd;delta1=b1-d1;delta2=b2-d2
   resid=(d2-d1)-((delta1-delta2)-(b1-b2));assert abs(resid)<1e-9
   rows.append({'Case':case,'Story':story,'epsilon_percent':100*eps,'n_candidates':len(ix),'t_B_s':float(t[ib]),'t_D_s':float(t[ip]),'P_B_kN':pb,'P_D_kN':pd,'B_at_actual_peak_abs_kN':bc,'baseline_gap_at_actual_peak_percent':gap,'best_candidate_time_s':float(t[jj]),'candidate_actual_peak_kN':candidate_peak,'missed_actual_peak_percent':err,'exact_saved_peak_capture':bool(err<=policy['exact_capture_tolerance_relative']*100),'peak_error_le_1_percent':bool(err<=1+1e-10),'actual_peak_near_candidate_010s':bool(dist<=.1+1e-9),'closest_candidate_distance_s':float(dist),'neighborhood_actual_peak_kN':near_peak,'neighborhood_missed_peak_percent':nearerr,'neighborhood_exact_peak_capture':bool(nearerr<=policy['exact_capture_tolerance_relative']*100),'neighborhood_error_le_1_percent':bool(nearerr<=1+1e-10),'original_gap_kN':b1-b2,'reduction_difference_kN':delta1-delta2,'actual_peak_vs_old_time_kN':d2-d1,'two_time_identity_residual_kN':resid,'D_SourceRow_at_own_peak':int(a[ip,cd.index('SourceRow')])})
write('screening-216.csv',rows)
summary=[]
for eps in policy['sensitivity_gap_fractions']:
 rr=[x for x in rows if x['epsilon_percent']==100*eps];assert len(rr)==72
 summary.append({'epsilon_percent':100*eps,'records':72,'candidate_count_total':sum(x['n_candidates']for x in rr),'candidate_count_median':float(np.median([x['n_candidates']for x in rr])),'candidate_count_max':max(x['n_candidates']for x in rr),'exact_capture':sum(x['exact_saved_peak_capture']for x in rr),'peak_error_le_1_percent':sum(x['peak_error_le_1_percent']for x in rr),'near_010s':sum(x['actual_peak_near_candidate_010s']for x in rr),'neighborhood_exact_capture':sum(x['neighborhood_exact_peak_capture']for x in rr),'neighborhood_error_le_1_percent':sum(x['neighborhood_error_le_1_percent']for x in rr),'maximum_peak_miss_percent':max(x['missed_actual_peak_percent']for x in rr),'maximum_neighborhood_peak_miss_percent':max(x['neighborhood_missed_peak_percent']for x in rr)})
write('screening-summary-3.csv',summary)
result={'completed':datetime.datetime.now().astimezone().isoformat(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rows':len(rows),'baseline_only_freeze':freeze,'summary':summary,'source_hashes':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [B/tb['cache'],D/td['cache']]],'not_prediction':True,'no_ODE_no_raw_workbook':True}
(O/'screening-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
