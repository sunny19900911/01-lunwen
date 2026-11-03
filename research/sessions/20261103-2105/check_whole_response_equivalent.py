from pathlib import Path
import numpy as np,csv,json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];O=S/'roles/equivalent/R002';O.mkdir(parents=True,exist_ok=True)
assert not (O/'whole-response-device-8.csv').exists()
P=R/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R006-device-distribution'
meta=json.loads((P/'local_history_manifest_r006.json').read_text(encoding='utf-8'))
with (R/'research/sessions/20261019-2045/roles/data/R001-link-geometry-88.csv').open(encoding='utf-8-sig',newline='')as f:G={(r['Story'],r['Link']):r for r in csv.DictReader(f)}
rows=[];nn=[];ll=[]
with np.load(P/'local_paired_histories_r006.npz',allow_pickle=False)as z:
 for a in sorted([r for r in meta['arrays']if r['Story']=='Story10'and r['Case']=='RH4Y'],key=lambda r:r['Link']):
  ar=z[a['key']];cc=a['columns'];t=ar[:,cc.index('t_s')];p=ar[:,cc.index('P_I_kN')];u=ar[:,cc.index('U1_m')];v=np.sign(p)*(abs(p)/477)**(1/.3)
  ce=float(np.trapezoid(p*v,t)/np.trapezoid(v*v,t));k=500000;fl=np.empty_like(p);fl[0]=p[0]
  for i,dt in enumerate(np.diff(t),1):
   decay=np.exp(-k*dt/ce);fl[i]=decay*fl[i-1]+ce*(-np.expm1(-k*dt/ce))*(u[i]-u[i-1])/dt
  ny=float(G[('Story10',a['Link'])]['ny']);nn.append(ny*p);ll.append(ny*fl)
  rows.append({'Link':a['Link'],'ny':ny,'c_eq_whole_response_kN_s_per_m':ce,'tau_s':ce/k,'whole_relative_RMS':float(np.linalg.norm(fl-p)/np.linalg.norm(p)),'native_abs_peak_kN':float(max(abs(p))),'linear_prescribed_u_abs_peak_kN':float(max(abs(fl)))})
qn=np.sum(nn,axis=0);ql=np.sum(ll,axis=0);anchors=[]
for tt in [16.62,21.64]:
 ix=int(np.argmin(abs(t-tt)));anchors.append({'time_s':tt,'native_QD_kN':float(qn[ix]),'linear_whole_response_QD_kN':float(ql[ix]),'native_branch_absolute_sum_kN':float(sum(abs(a[ix])for a in nn)),'linear_branch_absolute_sum_kN':float(sum(abs(a[ix])for a in ll))})
for name,rr in [('whole-response-device-8.csv',rows),('whole-response-QD-two-times.csv',anchors)]:
 with (O/name).open('x',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
hold=t>15
result={'at':datetime.datetime.now().astimezone().isoformat(),'whole_QD_relative_RMS':float(np.linalg.norm(ql-qn)/np.linalg.norm(qn)),'late_QD_relative_RMS_NOT_holdout':float(np.linalg.norm((ql-qn)[hold])/np.linalg.norm(qn[hold])),'anchors':anchors,'same_abs_order_t2_greater_t1':bool(abs(anchors[1]['linear_whole_response_QD_kN'])>abs(anchors[0]['linear_whole_response_QD_kN'])),'coefficient_used_entire_actual_record':True,'not_independent_validation':True,'not_new_story_QT':True,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'policy_sha256':hashlib.sha256((S/'equivalent-response-level-addendum.json').read_bytes()).hexdigest()}
(O/'whole-response-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
