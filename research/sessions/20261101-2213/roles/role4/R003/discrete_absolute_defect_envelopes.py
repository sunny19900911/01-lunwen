import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
from time import perf_counter
import csv,json,hashlib
import numpy as np

O=Path(__file__).resolve().parent; P=O.parent/'R001'; Q=O.parent/'R002'; R=O.parents[5]
L=O/'local-cache'; L.mkdir(exist_ok=False); (L/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
def stamp(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def js(name,v):
    with (O/name).open('x',encoding='utf-8') as f: json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cs(name,rows):
    with (O/name).open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def rd(p): return list(csv.DictReader(p.open(encoding='utf-8-sig')))
start=perf_counter(); prior=json.loads((P/'input-prediction-rules-freeze.json').read_text(encoding='utf-8'))
base=Path(prior['inputs'][0]['path']); sens=Path(json.loads((P/'results.json').read_text(encoding='utf-8'))['local_only_output']['path'])
policyfile=O.parents[2]/'engineering-policy-freeze-v001.json';policy=json.loads(policyfile.read_text(encoding='utf-8')); Dreq=policy['demonstration_Dreq'];Wmax=policy['width_limit_D_fraction']; targets=prior['target_zetas']
inputs=[base,sens,P/'prediction-freeze-manifest.json',P/'all300-layer-peak-predictions-96.csv',Q/'baseline-only-coth-bound-prediction-intervals-96.csv',policyfile]
bindings=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in inputs]
js('method-and-inputs-freeze.json',dict(start_observed_utc='2026-11-01T14:56:29+00:00',first8min_deadline_utc='2026-11-01T15:04:29+00:00',hard15min_deadline_utc='2026-11-01T15:11:29+00:00',method_frozen_utc=stamp(),code_sha256=sha(Path(__file__)),inputs=bindings,targets=targets,orders=[1,2],case='SHW3X known case, all target results previously seen in R002; no blind-validation claim',defect='d[n]=A_c*xhat[n]+b_c[n]-xhat[n+1], both q and v components',bound='Q[n]=sum(j=0..n-1) abs(E11((n-1-j)dt))*abs(dq[j])+abs(E12((n-1-j)dt))*abs(dv[j]); E_story[n]=sum abs(B)*omega^2/1000*Q[n]',peak_interval='L=max_n max(0,abs(Vhat[n])-E[n]); U=max_n(abs(Vhat[n])+E[n])',roundoff='local defect 64eps magnitude guard; kernels 128eps magnitude guard; FFT absolute guard 1e-12 times kernelL1*inputL1 per mode, separately recorded. Conservative engineering guards, not interval arithmetic or rigorous libm certificate.',scope='sampled exact piecewise-linear-input state recurrence; continuous-time extrema not covered; no signed error convolution; no target state solve',no_target_arrays_opened_this_round=True,no_threshold_tuning=True))
with np.load(base,allow_pickle=False) as a:
    t=a['t'].copy();ag=a['ag'].copy();s0=a['s_unitGamma'].copy();v0=a['sdot_unitGamma'].copy();om=a['omega'].copy();B=a['B_direct'].copy()
with np.load(sens,allow_pickle=False) as a:
    Z=a['z_unit'].copy();ZD=a['zdot_unit'].copy();W=a['w_unit'].copy();WD=a['wdot_unit'].copy()
    frozenV={(z,o):a[f'z{z:g}_order{o}_shear_inertia_kN'].copy() for z in targets for o in [1,2]}
dt=float(np.median(np.diff(t)));N=len(t);assert N==2691 and np.max(abs(np.diff(t)-dt))<1e-9
V0=(s0*om**2)@B.T/1000;P0=np.max(abs(V0),axis=0);C=abs(B)*om**2/1000;eps=np.finfo(float).eps
sl=(ag[1:]-ag[:-1])/dt;k=om**2;vp=-sl[:,None]/k
coth={(float(d['target_zeta']),int(d['Taylor_order']),d['Story']):d for d in rd(Q/'baseline-only-coth-bound-prediction-intervals-96.csv')}
boundrows=[];cost=[];checks=[];arrays={'t':t};envs={};calcstart=perf_counter();nfft=1<<(2*(N-1)-1).bit_length()
for z in targets:
    zclock=perf_counter();a=z*om;wd=om*np.sqrt(1-z*z);tau=np.arange(N-1)[:,None]*dt;dec=np.exp(-tau*a);co=np.cos(tau*wd);si=np.sin(tau*wd)/wd
    Kq=abs(dec*(co+a*si));Kv=abs(dec*si)
    Kqg=Kq+128*eps*dec*(abs(co)+abs(a*si)+1);Kvg=Kv+128*eps*dec*(abs(si)+1/om)
    qf=np.fft.rfft(Kqg,n=nfft,axis=0);vf=np.fft.rfft(Kvg,n=nfft,axis=0)
    dec1=np.exp(-a*dt);si1=np.sin(wd*dt)/wd;co1=np.cos(wd*dt)
    A11=dec1*(co1+a*si1);A12=dec1*si1;A21=-k*A12;A22=dec1*(co1-a*si1)
    qp0=-ag[:-1,None]/k+2*a*sl[:,None]/k**2;qp1=-ag[1:,None]/k+2*a*sl[:,None]/k**2
    kernel_seconds=perf_counter()-zclock
    for order in [1,2]:
        cc=perf_counter();delta=z-.05;s=s0+delta*Z+(delta**2/2*W if order==2 else 0);v=v0+delta*ZD+(delta**2/2*WD if order==2 else 0)
        sq=s[:-1]-qp0;sv=v[:-1]-vp
        dq=A11*sq+A12*sv+qp1-s[1:];dv=A21*sq+A22*sv+vp-v[1:]
        dqguard=64*eps*(abs(A11*sq)+abs(A12*sv)+abs(qp1)+abs(s[1:]))
        dvguard=64*eps*(abs(A21*sq)+abs(A22*sv)+abs(vp)+abs(v[1:]))
        aq=abs(dq)+dqguard;av=abs(dv)+dvguard;defectsec=perf_counter()-cc;fc=perf_counter()
        convq=np.fft.irfft(qf*np.fft.rfft(aq,n=nfft,axis=0),n=nfft,axis=0)[:N-1]
        convv=np.fft.irfft(vf*np.fft.rfft(av,n=nfft,axis=0),n=nfft,axis=0)[:N-1]
        fftguard=1e-12*(np.sum(Kqg,axis=0)*np.sum(aq,axis=0)+np.sum(Kvg,axis=0)*np.sum(av,axis=0))
        Qenv=np.zeros_like(s0);Qenv[1:]=np.maximum(0,convq+convv)+fftguard
        fftsec=perf_counter()-fc;pc=perf_counter();E=Qenv@C.T;projsec=perf_counter()-pc;Vhat=frozenV[z,order]
        reconstruct=float(np.max(abs((s*om**2)@B.T/1000-Vhat)));assert reconstruct<1e-8
        # Independent direct positive convolution checks: low, controlling, high modes, fixed a priori.
        for m in [0,1,9,12,49,99,199,299]:
            direct=np.convolve(Kqg[:,m],aq[:,m])[:N-1]+np.convolve(Kvg[:,m],av[:,m])[:N-1]
            err=float(np.max(abs(convq[:,m]+convv[:,m]-direct)))
            checks.append(dict(target_zeta=z,Taylor_order=order,Mode=m+1,FFT_direct_max_abs_difference_m=err,FFT_guard_m=float(fftguard[m]),difference_within_guard=bool(err<=fftguard[m]+1e-25)))
        envs[z,order]=E;arrays[f'z{z:g}_order{order}_story_E_kN']=E
        arrays[f'z{z:g}_order{order}_selected_modes_2_10_13_Q_m']=Qenv[:,[1,9,12]]
        for j in range(12):
            ph=float(np.max(abs(Vhat[:,j])));lo=float(np.max(np.maximum(0,abs(Vhat[:,j])-E[:,j])));up=float(np.max(abs(Vhat[:,j])+E[:,j]));DL=1-up/P0[j];DU=1-lo/P0[j];width=DU-DL
            deci='meets' if DL>=Dreq else ('insufficient' if DU<Dreq else 'uncertain');mask=abs(Vhat[:,j])+E[:,j]>=lo
            regions=int(np.count_nonzero(mask & np.r_[True,~mask[:-1]]));old=coth[z,order,'Story'+str(j+1)];oldwidth=float(old['D_interval_width'])
            boundrows.append(dict(target_zeta=z,Taylor_order=order,Story='Story'+str(j+1),P0_kN=float(P0[j]),predicted_peak_kN=ph,P_lower_kN=lo,P_upper_kN=up,D_lower=DL,D_upper=DU,D_interval_width=width,interval_decision=deci,width_status='acceptable' if width<=Wmax else 'too_wide',operational_full_recompute=bool(deci=='uncertain' or width>Wmax),coth_D_interval_width=oldwidth,width_ratio_to_coth=width/oldwidth,wider_than_coth=bool(width>oldwidth+1e-12),max_time_dependent_E_kN=float(np.max(E[:,j])),FFT_guard_story_kN=float(fftguard@C[j]),potential_peak_region_components=regions,potential_peak_time_samples=int(mask.sum()),potential_peak_first_s=float(t[np.flatnonzero(mask)[0]]),potential_peak_last_s=float(t[np.flatnonzero(mask)[-1]]),Dreq_demo=Dreq,Wmax_demo=Wmax,basis='absolute exact-discrete state defect kernels, floating guards; sampled times only'))
        cost.append(dict(target_zeta=z,Taylor_order=order,kernel_and_kernel_FFT_seconds_shared_per_target=kernel_seconds if order==1 else 0.,prediction_and_defect_seconds=defectsec,absolute_convolution_FFT_seconds=fftsec,story_projection_seconds=projsec,candidate_core_seconds=defectsec+fftsec+projsec+(kernel_seconds if order==1 else 0.),new_target_state_solves=0,nfft=nfft,modal_defect_steps=(N-1)*300,note='full time-varying modal defect evaluated, not a cheap scalar test; validation/direct checks and IO excluded from core'))
cs('baseline-only-discrete-envelope-intervals-96.csv',boundrows);cs('FFT-vs-direct-positive-convolution-checks-64.csv',checks);cs('measured-envelope-cost-8.csv',cost)
np.savez_compressed(L/'baseline-only-discrete-envelopes.npz',**arrays)
js('envelopes-frozen-before-target-open.json',dict(frozen_utc=stamp(),method_sha256=sha(O/'method-and-inputs-freeze.json'),interval_csv_sha256=sha(O/'baseline-only-discrete-envelope-intervals-96.csv'),array_sha256=sha(L/'baseline-only-discrete-envelopes.npz'),no_target_response_arrays_opened_this_round=True,new_target_state_solves=0,case_previously_known=True,all_envelope_stage_seconds=perf_counter()-calcstart,core_measured_seconds=sum(d['candidate_core_seconds'] for d in cost)))

# Only after envelope freeze, open the four already frozen R002 target arrays.
index=json.loads((Q/'reference-truth-array-index.json').read_text(encoding='utf-8'));evalrows=[];truthread=[]
for entry in index:
    z=entry['zeta'];path=Path(entry['path']);tc=perf_counter();assert sha(path)==entry['sha256']
    with np.load(path,allow_pickle=False) as a:
        assert np.array_equal(a['t'],t) and np.array_equal(a['omega'],om) and np.array_equal(a['B_direct'],B)
        truth=a['shear_elastic_inertia_predicted_kN' if z==.08 else 'shear_elastic_inertia_kN'].copy()
    truthread.append(dict(target_zeta=z,read_verify_seconds=perf_counter()-tc,path=str(path),sha256=entry['sha256']))
    for order in [1,2]:
        E=envs[z,order];error=abs(frozenV[z,order]-truth)
        for j in range(12):
            row=next(d for d in boundrows if d['target_zeta']==z and d['Taylor_order']==order and d['Story']=='Story'+str(j+1));Pt=float(np.max(abs(truth[:,j])));Dt=1-Pt/P0[j];uncovered=error[:,j]-E[:,j]
            evalrows.append({**row,'true_reference_peak_kN':Pt,'true_reference_D':float(Dt),'true_insufficient':bool(Dt<Dreq),'true_adverse':bool(Dt<0),'peak_covered':bool(row['P_lower_kN']-1e-8<=Pt<=row['P_upper_kN']+1e-8),'curve_covered_all_samples':bool(np.max(uncovered)<=1e-8),'max_error_minus_envelope_kN':float(np.max(uncovered)),'uncovered_samples_tolerance1e8':int(np.count_nonzero(uncovered>1e-8)),'insufficient_action_miss':bool(Dt<Dreq and row['interval_decision']=='meets'),'false_insufficient':bool(Dt>=Dreq and row['interval_decision']=='insufficient'),'adverse_action_miss':bool(Dt<0 and row['interval_decision']=='meets'),'adverse_risk_miss':bool(Dt<0 and row['D_lower']>=0)})
cs('discrete-envelope-coverage-width-decisions-96.csv',evalrows)
priority=[d for d in evalrows if d['Story'] in ['Story5','Story12']];cs('Story5-Story12-discrete-envelope-priority-16.csv',priority)
print('PRIORITY_SAVED '+stamp(),flush=True)
summary=[];building=[]
for z in targets:
    for order in [1,2]:
        rows=[d for d in evalrows if d['target_zeta']==z and d['Taylor_order']==order]
        summary.append(dict(target_zeta=z,Taylor_order=order,layers=12,peak_coverage=sum(d['peak_covered'] for d in rows)/12,curve_coverage=sum(d['curve_covered_all_samples'] for d in rows)/12,median_D_width_pp=100*float(np.median([d['D_interval_width'] for d in rows])),max_D_width_pp=100*max(d['D_interval_width'] for d in rows),median_width_ratio_to_coth=float(np.median([d['width_ratio_to_coth'] for d in rows])),wider_than_coth_count=sum(d['wider_than_coth'] for d in rows),meets=sum(d['interval_decision']=='meets' for d in rows),insufficient=sum(d['interval_decision']=='insufficient' for d in rows),uncertain=sum(d['interval_decision']=='uncertain' for d in rows),too_wide=sum(d['width_status']=='too_wide' for d in rows),operational_recompute_count=sum(d['operational_full_recompute'] for d in rows),insufficient_action_misses=sum(d['insufficient_action_miss'] for d in rows),false_insufficient=sum(d['false_insufficient'] for d in rows),true_adverse_count=sum(d['true_adverse'] for d in rows),adverse_action_misses=sum(d['adverse_action_miss'] for d in rows),adverse_risk_misses=sum(d['adverse_risk_miss'] for d in rows),adverse_miss_rate='N/A: no true adverse case' if not any(d['true_adverse'] for d in rows) else 'see counts'))
        building.append(dict(target_zeta=z,Taylor_order=order,whole_building_mathematical_decision='meets' if all(d['interval_decision']=='meets' for d in rows) else ('insufficient' if any(d['interval_decision']=='insufficient' for d in rows) else 'uncertain'),flagged_floors=sum(d['operational_full_recompute'] for d in rows),additional_building_state_solve_if_policy_requires=int(any(d['operational_full_recompute'] for d in rows)),note='one state solve covers all floors; a mathematically insufficient building can separately be rejected without solve if rejection is the chosen action'))
cs('discrete-vs-coth-summary-8.csv',summary);cs('candidate-level-building-accounting-8.csv',building)
js('results.json',dict(completed_utc=stamp(),summary=summary,truth_array_reads=truthread,new_exact_target_state_solves=0,unchanged_input_hashes=all(sha(Path(d['path']))==d['sha256'] for d in bindings),FFT_direct_checks_all_within_guard=all(d['difference_within_guard'] for d in checks),FFT_direct_max_difference_m=max(d['FFT_direct_max_abs_difference_m'] for d in checks),priority_saved_utc=stamp(),core_envelope_seconds=sum(d['candidate_core_seconds'] for d in cost),total_script_seconds=perf_counter()-start,source_case_known=True,continuous_time_certificate=False,rigorous_floating_point_certificate=False))
print(json.dumps(dict(summary=summary,priority=[{k:d[k] for k in ['target_zeta','Taylor_order','Story','D_lower','D_upper','interval_decision','width_status','operational_full_recompute']} for d in priority]),ensure_ascii=False,indent=2))
