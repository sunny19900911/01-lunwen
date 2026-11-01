import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from time import perf_counter
from datetime import datetime,timezone
import ast,json,csv,importlib.util
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R004';S=O.parents[2]
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def cs(n,rows):
    with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
# Replay only baseline/derivatives/frozen predictions/bounds. Reuse the four measured
# reference costs for conditional analyses; never regenerate finite target states.
clock=perf_counter();a=json.loads((S/'roles/role6/R002/assembled-v001/static-interface.json').read_text(encoding='utf-8'));om=np.array(a['omega12']);B=np.array(a['B3x12']);record=S/'roles/role3/R002/local-cache/H-E12140.AT2';ag=np.array([float(v) for line in record.read_text(encoding='ascii').splitlines()[4:] for v in line.split()])*386.4;dt=.005;N=len(ag);t=np.arange(N)*dt;commonprep=perf_counter()-clock
sp=importlib.util.spec_from_file_location('baseline_timing_only',Path('C:/Users/mj528/.codex/skills/etabs-response-analysis/scripts/modal_linear.py'));helper=importlib.util.module_from_spec(sp);sp.loader.exec_module(helper)
clock=perf_counter();s0,v0,_=helper.states(ag,om,.05,dt);baseline=perf_counter()-clock
# Import only the two pure coefficient functions through AST, never R004 top-level code.
tree=ast.parse((P/'public_baseline_sensitivity_predictions.py').read_text(encoding='utf-8'));funcs=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['mul','coefficients']],type_ignores=[]);exec(compile(funcs,'frozen_R004_coefficients_only','exec'),globals())
clock=perf_counter();E11,E12,E21,E22=coefficients(.05);setup=perf_counter()-clock;k=om**2;c=.1*om;Z=np.zeros_like(s0);ZD=np.zeros_like(s0);W=np.zeros_like(s0);WD=np.zeros_like(s0)
clock=perf_counter()
for n in range(1,N):
    slope=(ag[n]-ag[n-1])/dt;qp0=-ag[n-1]/k+c*slope/k**2;vp=-slope/k;dqp=2*om*slope/k**2;dq=s0[n-1]-qp0;dv=v0[n-1]-vp;dz=Z[n-1]-dqp;zd=ZD[n-1];Z[n]=E11[0]*dz+E12[0]*zd+E11[1]*dq+E12[1]*dv+dqp;ZD[n]=E21[0]*dz+E22[0]*zd+E21[1]*dq+E22[1]*dv
firsttime=perf_counter()-clock;clock=perf_counter()
for n in range(1,N):
    slope=(ag[n]-ag[n-1])/dt;qp0=-ag[n-1]/k+c*slope/k**2;vp=-slope/k;dqp=2*om*slope/k**2;dq=s0[n-1]-qp0;dv=v0[n-1]-vp;dz=Z[n-1]-dqp;zd=ZD[n-1];W[n]=E11[0]*W[n-1]+E12[0]*WD[n-1]+2*E11[1]*dz+2*E12[1]*zd+E11[2]*dq+E12[2]*dv;WD[n]=E21[0]*W[n-1]+E22[0]*WD[n-1]+2*E21[1]*dz+2*E22[1]*zd+E21[2]*dq+E22[2]*dv
secondtime=perf_counter()-clock
# Verification comparisons are explicitly outside measured method sections.
with np.load(P/'local-cache/baseline-sensitivities-and-frozen-predictions.npz',allow_pickle=False) as aa:
    maxstate=max(float(np.max(abs(x-aa[key]))) for x,key in [(s0,'s_unit'),(v0,'sdot_unit'),(Z,'z_unit'),(ZD,'zdot_unit'),(W,'w_unit'),(WD,'wdot_unit')]);frozenpred={(z,o):aa[f'z{z:g}_order{o}_shear_kip'].copy() for z in [.06,.07,.08,.10] for o in [1,2]}
with np.load(P/'local-cache/frozen-discrete-envelopes.npz',allow_pickle=False) as aa:frozenenv={(z,o):aa[f'z{z:g}_order{o}_E_kip'].copy() for z in [.06,.07,.08,.10] for o in [1,2]}
assert maxstate<1e-10
V0=(s0*om**2)@B.T;P0=np.max(abs(V0),axis=0);nfft=1<<(2*(N-1)-1).bit_length();eps=np.finfo(float).eps;Cabs=abs(B)*om**2;sl=np.diff(ag)/dt;vp=-sl[:,None]/k;rows=[];maxpred=maxenv=0.
for z in [.06,.07,.08,.10]:
    clock=perf_counter();alpha=z*om;wd=om*np.sqrt(1-z*z);tau=np.arange(N-1)[:,None]*dt;dec=np.exp(-tau*alpha);co=np.cos(tau*wd);si=np.sin(tau*wd)/wd;Kq=abs(dec*(co+alpha*si));Kv=abs(dec*si);Kqg=Kq+128*eps*dec*(abs(co)+abs(alpha*si)+1);Kvg=Kv+128*eps*dec*(abs(si)+1/om);qf=np.fft.rfft(Kqg,n=nfft,axis=0);vf=np.fft.rfft(Kvg,n=nfft,axis=0);dec1=np.exp(-alpha*dt);si1=np.sin(wd*dt)/wd;co1=np.cos(wd*dt);A11=dec1*(co1+alpha*si1);A12=dec1*si1;A21=-k*A12;A22=dec1*(co1-alpha*si1);qp0=-ag[:-1,None]/k+2*alpha*sl[:,None]/k**2;qp1=-ag[1:,None]/k+2*alpha*sl[:,None]/k**2;kernel=perf_counter()-clock
    for order in [1,2]:
        clock=perf_counter();delta=z-.05;sh=s0+delta*Z+(delta**2/2*W if order==2 else 0);vh=v0+delta*ZD+(delta**2/2*WD if order==2 else 0);V=(sh*om**2)@B.T;Ph=np.max(abs(V),axis=0);predtime=perf_counter()-clock;clock=perf_counter();sq=sh[:-1]-qp0;sv=vh[:-1]-vp;dq=A11*sq+A12*sv+qp1-sh[1:];dv=A21*sq+A22*sv+vp-vh[1:];aq=abs(dq)+64*eps*(abs(A11*sq)+abs(A12*sv)+abs(qp1)+abs(sh[1:]));av=abs(dv)+64*eps*(abs(A21*sq)+abs(A22*sv)+abs(vp)+abs(vh[1:]));defect=perf_counter()-clock;clock=perf_counter();conv=np.fft.irfft(qf*np.fft.rfft(aq,n=nfft,axis=0),n=nfft,axis=0)[:N-1]+np.fft.irfft(vf*np.fft.rfft(av,n=nfft,axis=0),n=nfft,axis=0)[:N-1];fg=1e-12*(np.sum(Kqg,axis=0)*np.sum(aq,axis=0)+np.sum(Kvg,axis=0)*np.sum(av,axis=0));Qenv=np.zeros_like(sh);Qenv[1:]=np.maximum(0,conv)+fg;E=Qenv@Cabs.T;bound=perf_counter()-clock;clock=perf_counter();lo=np.max(np.maximum(0,abs(V)-E),axis=0);up=np.max(abs(V)+E,axis=0);DL=1-up/P0;DU=1-lo/P0;decision=np.where(DL>=.1,'meets',np.where(DU<.1,'insufficient','uncertain'));width=DU-DL;action='reject' if np.any(decision=='insufficient') else ('pass' if np.all(decision=='meets') and np.all(width<=.05) else 'recompute');oldrule=bool(np.any(decision=='uncertain') or np.any(width>.05));rr=2*om*delta**2*ZD if order==1 else om*delta**3*WD;Ecoth=Cabs@(np.max(abs(rr),axis=0)/(om**2*np.tanh(np.pi*z/(2*np.sqrt(1-z*z)))));policytime=perf_counter()-clock
        rows.append(dict(target_zeta=z,Taylor_order=order,kernel_setup_seconds_standalone_method=kernel,predicted_motion_output_peak_seconds=predtime,defect_seconds=defect,positive_FFT_and_projection_seconds=bound,interval_coth_and_policy_seconds=policytime,candidate_prediction_core_seconds=kernel+predtime+defect+bound+policytime,v001_recompute=int(oldrule),v002_action=action,v002_recompute=int(action=='recompute')))
        maxpred=max(maxpred,float(np.max(abs(V-frozenpred[z,order]))));maxenv=max(maxenv,float(np.max(abs(E-frozenenv[z,order]))))
assert maxpred<1e-8 and maxenv<1e-8
cs('per-candidate-frozen-pipeline-replay-cost-8.csv',rows);refs=rd(O/'complete-candidate-measured-cost-4.csv');rtime={float(d['target_zeta']):float(d['complete_candidate_core_seconds']) for d in refs};direct=commonprep+sum(rtime.values());summary=[]
for order in [1,2]:
    prep=commonprep+baseline+setup+firsttime+(secondtime if order==2 else 0);rr=[d for d in rows if d['Taylor_order']==order];predict=sum(d['candidate_prediction_core_seconds'] for d in rr)
    for policy in ['v001','v002']:
        needed=[d['target_zeta'] for d in rr if d[policy+'_recompute']];conditional=sum(rtime[z] for z in needed);total=prep+predict+conditional
        summary.append(dict(Taylor_order=order,policy=policy,common_input_preparation_seconds=commonprep,baseline_state_seconds=baseline,derivative_coefficient_setup_seconds=setup,first_derivative_seconds=firsttime,second_derivative_seconds=secondtime if order==2 else 0.,all4_candidate_prediction_and_bound_seconds=predict,triggered_building_solves=len(needed),triggered_target_zetas=';'.join(f'{z:g}' for z in needed),triggered_complete_analysis_measured_seconds=conditional,total_measured_component_seconds=total,direct4_complete_core_plus_commonprep_seconds=direct,method_to_direct_cost_ratio=total/direct,cost_measurement='sum of actual same-runtime measured components, NOT single uninterrupted end-to-end stopwatch; target solves reused as measured costs, not rerun',validation_and_artifact_IO_excluded=True))
cs('fair-complete-pipeline-vs-direct-cost-4.csv',summary)
js('pipeline-cost-results.json',dict(completed_utc=datetime.now(timezone.utc).isoformat(),summary=summary,baseline_replay_solves=1,first_second_derivative_replays=2,new_finite_target_state_solves=0,max_replay_baseline_derivative_difference=maxstate,max_replay_prediction_difference_kip=maxpred,max_replay_envelope_difference_kip=maxenv,kernel_sharing='joint two-order replay shares kernels, but each standalone method comparison charged its full kernel setup once per target',commonprep='raw record parsing/scaling and static-interface read; same once for direct and each method',excluded='Python startup/import/AST parse, source hashes, independent verification, second physical-cut check, optional archival array serialization; reported separately in R005 results/notes',no_speedup_claim=all(d['method_to_direct_cost_ratio']>=1 for d in summary)))
print(json.dumps(dict(summary=summary,max_replay_state_difference=maxstate,max_replay_envelope_difference_kip=maxenv),ensure_ascii=False,indent=2))
