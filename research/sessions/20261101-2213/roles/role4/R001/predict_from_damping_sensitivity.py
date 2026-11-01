import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,importlib.util
import numpy as np
O=Path(__file__).resolve().parent;R=O.parents[5];OLD=R/'research/sessions/20261031-1130/roles/role4/R004';source=OLD/'local-cache/actual300-SHW3X-z0.05-factorized-reference.npz';helperpath=Path('C:/Users/mj528/.codex/skills/etabs-response-analysis/scripts/modal_linear.py');L=O/'local-cache';L.mkdir(exist_ok=False);(L/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cs(n,rows):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
manifest=json.loads((OLD/'delivery-manifest-v002.json').read_text(encoding='utf-8'));binding=next(d for d in manifest['local_only_arrays'] if d['path']==str(source));assert sha(source)==binding['sha256'];bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in [source,helperpath]];targets=[.06,.07,.08,.10];epslist=[1e-4,5e-5];selected=np.array([1,9,12]);zeta0=.05;dt=.02
js('input-prediction-rules-freeze.json',dict(start_observed_utc='2026-11-01T14:21:56+00:00',first8min_deadline_utc='2026-11-01T14:29:56+00:00',hard15min_deadline_utc='2026-11-01T14:36:56+00:00',rules_frozen_utc=datetime.now(timezone.utc).isoformat(),inputs=bindings,code_sha256=sha(Path(__file__)),source_case='SHW3X',baseline_zeta=zeta0,target_zetas=targets,mode_sets=['2,10,13 only','all300'],prediction_orders=[1,2],method='analytic first/second zeta derivatives of exact piecewise-linear-input discrete state propagator; derivative states driven using frozen baseline s/sdot; no explicit Euler/Newmark approximation',initial_conditions='cached s0/v0=0; z/zdot/w/wdot=0, ag[0] retained',derivative_check_only=dict(central_perturbations=epslist,zetas=[zeta0-h for h in epslist]+[zeta0+h for h in epslist],meaning='infinitesimal-neighborhood derivative check, not finite target evaluation'),shear='B*omega^2*s/1000, fixed physical-source elastic inertia reference, absolute peak over entire saved grid',engineering_demo_required_reduction=.10,target_response_arrays_read=False,target_truth_generated=False,no_fit=True))
with np.load(source,allow_pickle=False) as a:
 t=a['t'].copy();ag=a['ag'].copy();s0=a['s_unitGamma'].copy();v0=a['sdot_unitGamma'].copy();om=a['omega'].copy();B=a['B_direct'].copy();G=a['Gamma_X'].copy();px=a['phi_X'].copy();py=a['phi_Y'].copy()
assert s0.shape==v0.shape==(len(t),300) and np.all(s0[0]==0) and np.all(v0[0]==0) and np.allclose(np.diff(t),dt,atol=1e-9,rtol=0)
def mul(a,b):return np.stack([a[0]*b[0],a[1]*b[0]+a[0]*b[1],a[2]*b[0]+2*a[1]*b[1]+a[0]*b[2]])
def coefficients(z):
 d=np.sqrt(1-z*z);wd=om*d;wd1=-om*z/d;wd2=-om/d**3;theta=wd*dt;th1=wd1*dt;th2=wd2*dt;sn=np.sin(theta);co=np.cos(theta)
 eco=np.stack([co,-sn*th1,-co*th1**2-sn*th2]);esn=np.stack([sn,co*th1,-sn*th1**2+co*th2]);inv=np.stack([1/wd,-wd1/wd**2,2*wd1**2/wd**3-wd2/wd**2]);si=mul(esn,inv);ee=np.exp(-z*om*dt);ej=np.stack([ee,-om*dt*ee,(om*dt)**2*ee]);zsi=np.stack([z*om*si[0],om*(si[0]+z*si[1]),om*(2*si[1]+z*si[2])]);E11=mul(ej,eco+zsi);E12=mul(ej,si);E21=-(om**2)*E12;E22=mul(ej,eco-zsi);return E11,E12,E21,E22
E11,E12,E21,E22=coefficients(zeta0);Z=np.zeros_like(s0);ZD=np.zeros_like(s0);W=np.zeros_like(s0);WD=np.zeros_like(s0);k=om**2;c=2*zeta0*om;maxbaseq=maxbasev=0.
for n in range(1,len(t)):
 slope=(ag[n]-ag[n-1])/dt;qp0=-ag[n-1]/k+c*slope/k**2;qp1=-ag[n]/k+c*slope/k**2;vp=-slope/k;dqp=2*om*slope/k**2;dq=s0[n-1]-qp0;dv=v0[n-1]-vp;dz=Z[n-1]-dqp;zd=ZD[n-1]
 baseq=E11[0]*dq+E12[0]*dv+qp1;basev=E21[0]*dq+E22[0]*dv+vp;maxbaseq=max(maxbaseq,float(np.max(abs(baseq-s0[n]))));maxbasev=max(maxbasev,float(np.max(abs(basev-v0[n]))))
 Z[n]=E11[0]*dz+E12[0]*zd+E11[1]*dq+E12[1]*dv+dqp;ZD[n]=E21[0]*dz+E22[0]*zd+E21[1]*dq+E22[1]*dv
 W[n]=E11[0]*W[n-1]+E12[0]*WD[n-1]+2*E11[1]*dz+2*E12[1]*zd+E11[2]*dq+E12[2]*dv;WD[n]=E21[0]*W[n-1]+E22[0]*WD[n-1]+2*E21[1]*dz+2*E22[1]*zd+E21[2]*dq+E22[2]*dv
assert maxbaseq<1e-12 and maxbasev<1e-11 and all(np.isfinite(x).all() for x in [Z,ZD,W,WD])
sp=importlib.util.spec_from_file_location('exact_local_check',helperpath);helper=importlib.util.module_from_spec(sp);sp.loader.exec_module(helper);checks=[]
for h in epslist:
 plus,pv,_=helper.states(ag,om,zeta0+h,dt);minus,mv,_=helper.states(ag,om,zeta0-h,dt);fd1=(plus-minus)/(2*h);fd2=(plus-2*s0+minus)/h**2
 for i in range(300):
  ez=float(np.linalg.norm(fd1[:,i]-Z[:,i]));ew=float(np.linalg.norm(fd2[:,i]-W[:,i]));nz=float(np.linalg.norm(Z[:,i]));nw=float(np.linalg.norm(W[:,i]));checks.append(dict(Mode=i+1,omega_rad_s=float(om[i]),local_check_h=h,z_L2=float(nz),first_derivative_FD_L2_error=ez,first_derivative_relative_L2_error=ez/nz if nz else None,w_L2=float(nw),second_derivative_FD_L2_error=ew,second_derivative_relative_L2_error=ew/nw if nw else None,meaning='local derivative verification only, not target truth'))
cs('local-infinitesimal-derivative-checks-600.csv',checks)
selectedchecks=[d for d in checks if d['Mode'] in [2,10,13]];assert max(d['first_derivative_relative_L2_error'] for d in selectedchecks)<1e-4 and max(d['second_derivative_relative_L2_error'] for d in selectedchecks)<1e-3
Vbase=(s0*om**2)@B.T/1000;V3base=(s0[:,selected]*om[selected]**2)@B[:,selected].T/1000;peak0=np.max(abs(Vbase),axis=0);peak3=np.max(abs(V3base),axis=0);i0=np.argmax(abs(Vbase),axis=0);coefx=px*G;coefy=py*G;baseUX=s0@coefx.T;baseUY=s0@coefy.T;keys=sorted([(f'Story{i}','D1') for i in range(1,13)]+[(f'Story{i}','D2') for i in range(3,9)],key=lambda q:(int(q[0][5:]),q[1]));assert len(keys)==18
early=[];full=[];motion=[];cmpeaks=[];predarrays={}
for target in targets:
 delta=target-zeta0
 for order in [1,2]:
  s=s0+delta*Z+(delta*delta/2*W if order==2 else 0);v=v0+delta*ZD+(delta*delta/2*WD if order==2 else 0);V=(s*om**2)@B.T/1000;V3=(s[:,selected]*om[selected]**2)@B[:,selected].T/1000;ux=s@coefx.T;uy=s@coefy.T;tag=f'z{target:g}_order{order}';predarrays[tag+'_shear_inertia_kN']=V;predarrays[tag+'_CM_UX_m']=ux;predarrays[tag+'_CM_UY_m']=uy
  for st in range(12):
   ip=int(np.argmax(abs(V[:,st])));Ppred=float(abs(V[ip,st]));ip3=int(np.argmax(abs(V3[:,st])));p3=float(abs(V3[ip3,st]));full.append(dict(Case='SHW3X',modes='all300',target_zeta=target,Taylor_order=order,Story='Story'+str(st+1),baseline5_peak_kN=float(peak0[st]),predicted_peak_kN=Ppred,predicted_decrease_percent=100*(1-Ppred/peak0[st]),predicted_below10pct_demo=bool(Ppred/peak0[st]>.9),predicted_adverse_peak=bool(Ppred>peak0[st]),baseline5_peak_time_s=float(t[i0[st]]),predicted_peak_time_s=float(t[ip]),prediction_abs_at_baseline_peak_kN=float(abs(V[i0[st],st])),status='prediction frozen without target response or target truth'))
   early.append(dict(Case='SHW3X',modes='2;10;13 only',target_zeta=target,Taylor_order=order,Story='Story'+str(st+1),baseline3mode_peak_kN=float(peak3[st]),predicted3mode_peak_kN=p3,predicted3mode_decrease_percent=100*(1-p3/peak3[st]),predicted_peak_time_s=float(t[ip3]),scope='selected-three-mode motion only, not full-story accuracy claim'))
  for i in range(300):
   ip=int(np.argmax(abs(s[:,i])));motion.append(dict(Mode=i+1,omega_rad_s=float(om[i]),target_zeta=target,Taylor_order=order,baseline_unit_s_abspeak_m=float(np.max(abs(s0[:,i]))),predicted_unit_s_abspeak_m=float(abs(s[ip,i])),predicted_q_reference_abspeak=abs(float(G[i]*s[ip,i])),predicted_unit_s_peak_time_s=float(t[ip]),predicted_unit_velocity_abspeak_m_s=float(np.max(abs(v[:,i]))),scope='baseline sensitivity motion prediction; no finite target truth'))
  for ax,arr,base in [('UX',ux,baseUX),('UY',uy,baseUY)]:
   for j,key in enumerate(keys):
    ip=int(np.argmax(abs(arr[:,j])));baseP=float(np.max(abs(base[:,j])));Pp=float(abs(arr[ip,j]));cmpeaks.append(dict(Story=key[0],Diaphragm=key[1],Axis=ax,target_zeta=target,Taylor_order=order,baseline5_peak_m=baseP,predicted_peak_m=Pp,predicted_peak_time_s=float(t[ip]),predicted_peak_ratio=Pp/baseP if baseP else None,scope='CM motion from baseline derivatives only, no target comparison'))
cs('early-three-mode-target-predictions-96.csv',early);print('EARLY_THREE_MODE_PREDICTIONS_SAVED '+datetime.now(timezone.utc).isoformat(),flush=True);cs('all300-layer-peak-predictions-96.csv',full);cs('all300-unit-modal-motion-predictions-2400.csv',motion);cs('selected2-10-13-motion-predictions-24.csv',[d for d in motion if d['Mode'] in [2,10,13]]);cs('all18-CM-motion-peak-predictions-288.csv',cmpeaks)
out=L/'baseline-analytic-sensitivities-and-frozen-predictions.npz';np.savez_compressed(out,t=t,z_unit=Z,zdot_unit=ZD,w_unit=W,wdot_unit=WD,**predarrays)
summary=dict(completed_utc=datetime.now(timezone.utc).isoformat(),baseline_primal_step_max_abs_q_error_m=maxbaseq,baseline_primal_step_max_abs_v_error_m_s=maxbasev,modes=300,selected_modes=[2,10,13],derivative_check_rows=600,first_derivative_selected_max_relative_error=max(d['first_derivative_relative_L2_error'] for d in selectedchecks),second_derivative_selected_max_relative_error=max(d['second_derivative_relative_L2_error'] for d in selectedchecks),first_derivative_all300_max_relative_error=max(d['first_derivative_relative_L2_error'] for d in checks),second_derivative_all300_max_relative_error=max(d['second_derivative_relative_L2_error'] for d in checks),full_layer_prediction_rows=96,early_three_mode_rows=96,motion_rows=2400,CM_motion_peak_rows=288,finite_target_truth_generated=False,target8_response_array_opened=False,local_only_output=dict(path=str(out),bytes=out.stat().st_size,sha256=sha(out)),source_baseline_reused=True,source_SHA_unchanged=all(sha(Path(d['path']))==d['sha256'] for d in bindings))
js('results.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
