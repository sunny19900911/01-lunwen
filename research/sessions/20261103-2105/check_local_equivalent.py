from pathlib import Path
import json,csv,hashlib,datetime
import numpy as np
S=Path(__file__).resolve().parent;R=S.parents[2];O=S/'roles/equivalent';O.mkdir(parents=True,exist_ok=True)
assert not (O/'equivalent-device-8.csv').exists()
P=R/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R006-device-distribution'
F=P/'local_paired_histories_r006.npz';M=P/'local_history_manifest_r006.json'
G=R/'research/sessions/20261019-2045/roles/data/R001-link-geometry-88.csv'
policy=json.loads((S/'equivalent-policy-freeze.json').read_text(encoding='utf-8'));hm=json.loads(M.read_text(encoding='utf-8'))
with G.open(encoding='utf-8-sig',newline='')as f:g={(r['Story'],r['Link']):r for r in csv.DictReader(f)}
records=[a for a in hm['arrays']if a['Story']=='Story10'and a['Case']=='RH4Y'];assert len(records)==8
K=policy['spring_k_kN_per_m'];c=policy['nonlinear_c'];alpha=policy['alpha'];rows=[];native=[];linear=[];nativeP=[];linearP=[]
def integ(v,t):return float(np.trapezoid(v,t))
with np.load(F,allow_pickle=False)as z:
 for a in sorted(records,key=lambda x:x['Link']):
  ar=z[a['key']];cols=a['columns'];t=ar[:,cols.index('t_s')];p=ar[:,cols.index('P_I_kN')];u=ar[:,cols.index('U1_m')]
  assert np.array_equal(p,ar[:,cols.index('P_J_kN')])and np.all(np.diff(t)>0)
  vv=np.sign(p)*(abs(p)/c)**(1/alpha);train=(t>=0)&(t<=15);hold=t>15
  den=integ(vv[train]**2,t[train]);assert den>0
  ceq=integ(p[train]*vv[train],t[train])/den;assert ceq>0
  fl=np.empty_like(p);fl[0]=p[0]
  for i,dt in enumerate(np.diff(t),1):
   dec=np.exp(-K*dt/ceq);one=-np.expm1(-K*dt/ceq)
   fl[i]=dec*fl[i-1]+ceq*one*(u[i]-u[i-1])/dt
  ny=float(g[('Story10',a['Link'])]['ny']);r={'Link':a['Link'],'ny':ny,'c_eq_kN_s_per_m':ceq,'tau_s':ceq/K,'training_work_dashpot_kNm':integ(p[train]*vv[train],t[train]),'native_total_port_work_training_kNm':float(np.sum(.5*(p[1:][train[1:]]+p[:-1][train[1:]])*np.diff(u)[train[1:]])),'training_relative_RMS':float(np.linalg.norm(fl[train]-p[train])/np.linalg.norm(p[train])),'holdout_relative_RMS':float(np.linalg.norm(fl[hold]-p[hold])/np.linalg.norm(p[hold])),'native_abs_peak_kN':float(max(abs(p))),'linear_prescribed_u_abs_peak_kN':float(max(abs(fl)))}
  for tt in policy['anchors_s']:
   ix=int(np.argmin(abs(t-tt)));assert abs(t[ix]-tt)<1e-9
   r[f'native_P_at_{tt}_kN']=float(p[ix]);r[f'linear_P_at_{tt}_kN']=float(fl[ix])
  rows.append(r);native.append(ny*p);linear.append(ny*fl);nativeP.append(p);linearP.append(fl)
qn=np.sum(native,axis=0);ql=np.sum(linear,axis=0);anchor=[]
for tt in policy['anchors_s']:
 ix=int(np.argmin(abs(t-tt)));anchor.append({'time_s':tt,'native_QD_kN':float(qn[ix]),'linear_prescribed_u_QD_kN':float(ql[ix]),'native_branch_absolute_sum_kN':float(sum(abs(a[ix])for a in native)),'linear_branch_absolute_sum_kN':float(sum(abs(a[ix])for a in linear)),'native_QD_abs_kN':float(abs(qn[ix])),'linear_QD_abs_kN':float(abs(ql[ix]))})
qcache=R/'research/sessions/20261019-2045/roles/data/local-cache/R002-native-horizontal/paired-layer-histories.npz'
with np.load(qcache,allow_pickle=False)as z:
 aa=z['Story10__RH4Y__Y'];assert np.array_equal(t,aa[:,0]);assert np.max(abs(qn-aa[:,2]))<1e-10
def wr(name,rr):
 with (O/name).open('x',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
wr('equivalent-device-8.csv',rows);wr('equivalent-QD-two-times.csv',anchor)
(O/'local-cache').mkdir(exist_ok=True)
np.savez_compressed(O/'local-cache/equivalent-native-u.npz',t=t,native_P=np.array(nativeP),linear_P=np.array(linearP),native_QD=qn,linear_QD=ql)
result={'at':datetime.datetime.now().astimezone().isoformat(),'native_QD_full_reproduction_max_abs_error_kN':float(np.max(abs(qn-aa[:,2]))),'anchors':anchor,'nonzero_Y_devices':sum(abs(r['ny'])>1e-12 for r in rows),'coefficient_training_ends_before_both_anchors':True,'local_prescribed_u_QD_holdout_relative_RMS':float(np.linalg.norm((ql-qn)[hold])/np.linalg.norm(qn[hold])),'native_abs_QD_time_ordering_t2_gt_t1':bool(abs(qn[np.argmin(abs(t-21.64))])>abs(qn[np.argmin(abs(t-16.62))])),'linear_abs_QD_time_ordering_t2_gt_t1':bool(abs(ql[np.argmin(abs(t-21.64))])>abs(ql[np.argmin(abs(t-16.62))])),'QT_linear_not_computed':True,'equivalent_global_zeta_not_identifiable_from_local_8_devices':True,'force_QD_not_story_QT':True,'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in [F,M,G,S/'equivalent-policy-freeze.json']], 'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(O/'equivalent-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
