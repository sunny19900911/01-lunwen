import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
from time import perf_counter,process_time
import json,csv,hashlib,importlib.util
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent;S=O.parents[2];R=O.parents[5];L=O/'local-cache';L.mkdir(exist_ok=False);(L/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cs(n,rows):
    with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
start=perf_counter();cpu0=process_time();policy=S/'engineering-input-envelope-policy-freeze-v001.json';alg=P/'R007/shw4_baseline_prediction_then_two_targets.py';helperpath=Path('C:/Users/mj528/.codex/skills/etabs-response-analysis/scripts/modal_linear.py');old=R/'research/sessions/20261031-1130/roles/role4/R004';oldmanifest=json.loads((old/'delivery-manifest-v002.json').read_text(encoding='utf-8'));cases=['SHW3X','SHW4X','RH4X'];zs=[.06,.07,.08,.10];newzs=[.08,.10];dt=.02;Dreq=.10;Wmax=.05
cache={c:Path(json.loads((P/r/'prediction-S-envelope-freeze.json').read_text(encoding='utf-8'))['local_array']['path']) for c,r in [('SHW4X','R007'),('RH4X','R008')]};old8={c:old/f'local-cache/actual300-{c}-z0.08-factorized-reference.npz' for c in ['SHW4X','RH4X']};old8binding={c:next(d for d in oldmanifest['local_only_arrays'] if Path(d['path'])==old8[c]) for c in old8}
sources=[policy,alg,helperpath,old/'delivery-manifest-v002.json']+list(cache.values())+[P/'R003/baseline-only-discrete-envelope-intervals-96.csv',P/'R001/all300-layer-peak-predictions-96.csv',P/'R006/baseline-sensitivity-ranked-floors-15.csv',P/'R007/baseline-S-ranked-floors-12.csv',P/'R008/baseline-S-ranked-floors-12.csv',P/'R007/frozen-discrete-intervals-48.csv',P/'R008/frozen-discrete-intervals-48.csv',P/'R007/frozen-candidate-peak-predictions-48.csv',P/'R008/frozen-candidate-peak-predictions-48.csv'];bindings=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sources]
js('input-method-envelope-rules-freeze.json',dict(start_observed_utc='2026-11-01T16:00:47+00:00',first8min_deadline_utc='2026-11-01T16:08:47+00:00',hard15min_deadline_utc='2026-11-01T16:15:47+00:00',rules_frozen_utc=now(),inputs=bindings,code_sha256=sha(Path(__file__)),cases=cases,new_predictions_for=['SHW4X','RH4X'],new_prediction_targets=newzs,new_derivative_solves=0,reused8_expected=old8binding,new_target_state_solves=['SHW4X .10','RH4X .10'],ordering='all new individual predictions and intervals plus merged envelope intervals/actions frozen BEFORE opening any old8 array or generating new10',model='fixed all300 X linear basis and B; original SI ag no extra SF/g; zeroIC nominaldt.02 from caches',method='exact existing R007 prediction/bound block, no derivative recomputation; sample-grid engineering FP guards',objective='additional selected-input absolute peak envelope; maxL/maxU over case peaks, not same-time waveform or average; previous per-input objectives unchanged',S_env='max force derivative among exact baseline controlling cases, then -divide by P0env; not min S',cost='perf_counter wall and process_time CPU recorded prospectively, sources/IO/checks separately; no assumed acceleration',not_blind='old8 and historical inputs previously seen; no independent event/generalization or Y claim'))
text=alg.read_text(encoding='utf-8');i=text.index('arrays=dict(t=t,ag=ag');j=text.index("cs('frozen-candidate-peak-predictions-48.csv'",i);block=text[i:j];newpred=[];newbounds=[];ncost=[];newfft=[];state={};newV={};newE={};arrays=[];readwall=readcpu=0.
for case in ['SHW4X','RH4X']:
    w0=perf_counter();c0=process_time()
    with np.load(cache[case],allow_pickle=False) as a:data={key:a[key].copy() for key in ['t','ag','omega','B','s0','v0','Z','ZD','W','WD']}
    readwall+=perf_counter()-w0;readcpu+=process_time()-c0;assert np.max(abs(np.diff(data['t'])-dt))<1e-9 and data['s0'].shape[1]==300;state[case]=data
    ns=dict(np=np,perf_counter=perf_counter,targets=newzs,dt=dt,t=data['t'],ag=data['ag'],om=data['omega'],B=data['B'],s0=data['s0'],v0=data['v0'],Z=data['Z'],ZD=data['ZD'],W=data['W'],WD=data['WD'],k=data['omega']**2)
    w0=perf_counter();c0=process_time();exec(compile(block.replace("'SHW4X'",repr(case)),'frozen_R007_prediction_and_bound_block','exec'),ns);elapsed=perf_counter()-w0;cpuelapsed=process_time()-c0
    newpred+=ns['prows'];newbounds+=ns['bounds'];newfft+=[dict(Case=case,**d) for d in ns['fftchecks']];ncost.append(dict(Case=case,targets='.08;.10',orders='1;2',wall_seconds_with_direct_FFT_checks=elapsed,process_CPU_seconds_with_direct_FFT_checks=cpuelapsed,core_wall_seconds=sum(d['core_seconds'] for d in ns['cost']),new_derivatives=0,new_target_solves=0))
    aa={'t':data['t']}
    for z in newzs:
        for order in [1,2]:newV[case,z,order]=ns['pred'][z,order];newE[case,z,order]=ns['env'][z,order];aa[f'z{z:g}_order{order}_V']=newV[case,z,order];aa[f'z{z:g}_order{order}_E']=newE[case,z,order]
    out=L/f'{case}-new8-10-predictions-envelopes.npz';np.savez_compressed(out,**aa);arrays.append(dict(path=str(out),sha256=sha(out),bytes=out.stat().st_size))
cs('new-individual-peak-predictions-96.csv',newpred);cs('new-individual-discrete-intervals-96.csv',newbounds);cs('new-prediction-bound-work-2.csv',ncost);cs('positive-FFT-direct-checks-32.csv',newfft)

# Normalize existing and new individual tables without reading any new reference.
individual=[]
def append_individual(case,br,pr):
    for b in br:
        z=float(b['target_zeta']);o=int(b['Taylor_order']);story=b['Story'];p=next(d for d in pr if float(d['target_zeta'])==z and int(d['Taylor_order'])==o and d['Story']==story);p0=float(b['P0_kN']);lo=float(b['P_lower_kN']);up=float(b['P_upper_kN']);ph=float(p.get('Phat_kN',p.get('predicted_peak_kN')));dl=1-up/p0;du=1-lo/p0;status='meets' if dl>=Dreq else ('insufficient' if du<Dreq else 'uncertain');individual.append(dict(Case=case,target_zeta=z,Taylor_order=o,Story=story,P0_kN=p0,Phat_kN=ph,L_kN=lo,U_kN=up,D_lower=dl,D_upper=du,D_width=du-dl,decision_status=status,width_status='acceptable' if du-dl<=Wmax else 'too_wide',v001_recompute=bool(status=='uncertain' or du-dl>Wmax)))
append_individual('SHW3X',rd(P/'R003/baseline-only-discrete-envelope-intervals-96.csv'),rd(P/'R001/all300-layer-peak-predictions-96.csv'))
for c,r in [('SHW4X','R007'),('RH4X','R008')]:append_individual(c,rd(P/r/'frozen-discrete-intervals-48.csv'),rd(P/r/'frozen-candidate-peak-predictions-48.csv'));append_individual(c,[d for d in newbounds if d['Case']==c],[d for d in newpred if d['Case']==c])
assert len(individual)==288
sdata={'SHW3X':[d for d in rd(P/'R006/baseline-sensitivity-ranked-floors-15.csv') if d['Case']=='SHW3X_fixed300'],'SHW4X':rd(P/'R007/baseline-S-ranked-floors-12.csv'),'RH4X':rd(P/'R008/baseline-S-ranked-floors-12.csv')};baseenv=[];P0env={}
for st in range(1,13):
    story=f'Story{st}';bb={c:next(d['P0_kN'] for d in individual if d['Case']==c and d['Story']==story) for c in cases};peak=max(bb.values());active=[c for c in cases if bb[c]==peak];ss={c:float(next(d['S_percent_per_damping_pp'] for d in sdata[c] if d['Story']==story)) for c in cases};prime=max(-ss[c]*bb[c] for c in active);Sc=-prime/peak;P0env[story]=peak;baseenv.append(dict(Story=story,P0env_kN=peak,baseline_controlling_inputs=';'.join(active),exact_input_tie_count=len(active),S_env_percent_per_damping_pp=Sc,min_individual_S_percent_per_damping_pp=min(ss.values()),source_S=';'.join(f'{c}:{ss[c]:.12g}' for c in cases),baseline_control_times_s=';'.join(c+':'+next(d.get('right_controller_times_s',d.get('controller_times_s','')) for d in sdata[c] if d['Story']==story) for c in active)))
for d in baseenv:d['env_slow_rank']=1+sum(e['S_env_percent_per_damping_pp']<d['S_env_percent_per_damping_pp'] for e in baseenv)
env=[];envcandidates=[];strong=[]
for z in zs:
    for o in [1,2]:
        for st in range(1,13):
            story=f'Story{st}';rr=[d for d in individual if d['target_zeta']==z and d['Taylor_order']==o and d['Story']==story];lo=max(d['L_kN'] for d in rr);up=max(d['U_kN'] for d in rr);ph=max(d['Phat_kN'] for d in rr);p0=P0env[story];dl=1-up/p0;du=1-lo/p0;width=du-dl;status='meets' if dl>=Dreq else ('insufficient' if du<Dreq else 'uncertain');potential=[d['Case'] for d in rr if d['U_kN']>=lo]
            env.append(dict(target_zeta=z,Taylor_order=o,Story=story,P0env_kN=p0,Phat_env_kN=ph,L_env_kN=lo,U_env_kN=up,D_env_point=1-ph/p0,D_env_lower=dl,D_env_upper=du,D_env_width=width,decision_status=status,width_status='acceptable' if width<=Wmax else 'too_wide',v001_recompute=bool(status=='uncertain' or width>Wmax),predicted_peak_controlling_inputs=';'.join(d['Case'] for d in rr if d['Phat_kN']==ph),potential_controlling_inputs=';'.join(potential),min_individual_D_lower=min(d['D_lower'] for d in rr),min_individual_D_upper=min(d['D_upper'] for d in rr)))
        rr=[d for d in env if d['target_zeta']==z and d['Taylor_order']==o];ir=[d for d in individual if d['target_zeta']==z and d['Taylor_order']==o]
        def action(rows,lower,upper,width):return 'reject' if any(d[upper]<Dreq for d in rows) else ('pass' if all(d[lower]>=Dreq and d[width]<=Wmax for d in rows) else 'recompute')
        envcandidates.append(dict(target_zeta=z,Taylor_order=o,envelope_candidate_action=action(rr,'D_env_lower','D_env_upper','D_env_width'),strong_each_input_candidate_action=action(ir,'D_lower','D_upper','D_width'),envelope_meets_floors=sum(d['decision_status']=='meets' for d in rr),envelope_insufficient_floors=sum(d['decision_status']=='insufficient' for d in rr),envelope_uncertain_floors=sum(d['decision_status']=='uncertain' for d in rr),envelope_too_wide_floors=sum(d['width_status']=='too_wide' for d in rr),envelope_v001_flagged_floors=sum(d['v001_recompute'] for d in rr),analysis_scope_if_recompute='one candidate assessment across all3 listed inputs; up to3 state histories, not one solve per floor'))
cs('all-individual-frozen-intervals-288.csv',individual);cs('baseline-input-envelope-S-12.csv',baseenv);cs('input-envelope-frozen-intervals-96.csv',env);cs('input-envelope-and-strong-objective-actions-8.csv',envcandidates)
js('prediction-and-envelope-freeze.json',dict(frozen_utc=now(),new_target_solves=0,old8_arrays_opened=False,new_derivative_solves=0,new_local_arrays=arrays,files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(O.glob('*.csv'))],prediction_read_wall_seconds=readwall,prediction_read_CPU_seconds=readcpu,additional_input_envelope_policy_sha256=sha(policy)))
print('ALL_PREDICTIONS_AND_ENVELOPE_FROZEN '+now(),flush=True)

# Reference stage starts only after all predictions/envelope/actions were frozen.
spec=importlib.util.spec_from_file_location('two_new10_references',helperpath);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);trutharrays={};newtruth=[];tindex=[];tcost=[]
for case in ['SHW4X','RH4X']:
    d=state[case];om=d['omega'];B=d['B'];t=d['t'];ag=d['ag'];p0=np.max(abs((d['s0']*om**2)@B.T/1000),axis=0)
    for z in newzs:
        w0=perf_counter();c0=process_time()
        if z==.08:
            assert sha(old8[case])==old8binding[case]['sha256']
            with np.load(old8[case],allow_pickle=False) as a:
                assert np.array_equal(t,a['t']) and np.array_equal(ag,a['ag']) and np.array_equal(om,a['omega']) and np.array_equal(B,a['B_direct']);V=a['shear_elastic_inertia_predicted_kN'].copy();q=a['s_unitGamma'].copy()
            path=old8[case];kind='known old8 reuse, no state solve'
        else:
            q,v,_=helper.states(ag,om,z,dt);V=(q*om**2)@B.T/1000;path=L/f'{case}-new-exact10.npz';kind='new exact10 state solve'
        corewall=perf_counter()-w0;corecpu=process_time()-c0;assert np.max(abs(V-(q*om**2)@B.T/1000))<1e-8;trutharrays[case,z]=V;ip=np.argmax(abs(V),axis=0);pk=abs(V[ip,np.arange(12)])
        for j in range(12):newtruth.append(dict(Case=case,target_zeta=z,Story=f'Story{j+1}',P0_kN=float(p0[j]),reference_peak_kN=float(pk[j]),reference_D=float(1-pk[j]/p0[j]),reference_signed_peak_kN=float(V[ip[j],j]),reference_peak_time_s=float(t[ip[j]]),reference_origin=kind))
        if z==.10:np.savez_compressed(path,t=t,ag=ag,omega=om,B=B,s=q,V=V)
        tindex.append(dict(Case=case,target_zeta=z,path=str(path),sha256=sha(path),bytes=path.stat().st_size,new_state_solve=int(z==.10),origin=kind));tcost.append(dict(Case=case,target_zeta=z,reference_read_or_solve_projection_wall_seconds=corewall,reference_read_or_solve_projection_CPU_seconds=corecpu,new_state_solve=int(z==.10),note='read/hash for reused8; solve+projection for new10; archive writing and validation excluded'))
cs('new-or-reused-individual-reference-peaks-48.csv',newtruth);js('reference-array-index-4.json',tindex);cs('reference-stage-cost-4.csv',tcost)
comparisons=[]
for pr in newpred:
    case=pr['Case'];z=pr['target_zeta'];o=pr['Taylor_order'];j=int(pr['Story'][5:])-1;V=trutharrays[case,z][:,j];vh=newV[case,z,o][:,j];E=newE[case,z,o][:,j];rr=next(d for d in newtruth if d['Case']==case and d['target_zeta']==z and d['Story']==pr['Story']);br=next(d for d in newbounds if d['Case']==case and d['target_zeta']==z and d['Taylor_order']==o and d['Story']==pr['Story']);D=rr['reference_D'];comparisons.append(dict(Case=case,target_zeta=z,Taylor_order=o,Story=pr['Story'],predicted_D=pr['predicted_D'],reference_D=D,peak_relative_error=pr['Phat_kN']/rr['reference_peak_kN']-1,point_insufficient_miss=bool(D<Dreq and pr['predicted_D']>=Dreq),point_false_adverse=bool(D>=0 and pr['predicted_D']<0),true_adverse=bool(D<0),curve_covered_strict=bool(np.all(abs(vh-V)<=E)),strict_uncovered_samples=int(np.count_nonzero(abs(vh-V)>E)),peak_covered=bool(br['P_lower_kN']<=rr['reference_peak_kN']<=br['P_upper_kN']),interval_insufficient_miss=bool(D<Dreq and br['decision_status']=='meets'),interval_false_insufficient=bool(D>=Dreq and br['decision_status']=='insufficient'),width=br['D_width'],decision_status=br['decision_status'],width_status=br['width_status']))
cs('new-individual-prediction-validation-96.csv',comparisons)

alltruth=[]
for d in rd(P/'R002/exact-reference-truth-peaks-48.csv'):alltruth.append(dict(Case='SHW3X',target_zeta=float(d['target_zeta']),Story=d['Story'],P0_kN=float(d['baseline_peak_kN']),reference_peak_kN=float(d['exact_reference_peak_kN']),reference_D=float(d['exact_reference_decrease_percent'])/100,reference_peak_time_s=float(d['exact_reference_peak_time_s'])))
for case,r in [('SHW4X','R007'),('RH4X','R008')]:
    for d in rd(P/r/'exact-reference-floor-peaks-24.csv'):alltruth.append(dict(Case=case,target_zeta=float(d['target_zeta']),Story=d['Story'],P0_kN=float(d['P0_kN']),reference_peak_kN=float(d['reference_peak_kN']),reference_D=float(d['reference_D']),reference_peak_time_s=float(d['reference_peak_time_s'])))
for d in newtruth:alltruth.append({k:d[k] for k in ['Case','target_zeta','Story','P0_kN','reference_peak_kN','reference_D','reference_peak_time_s']})
assert len(alltruth)==144;envtruth=[];envvalidation=[]
for z in zs:
    for st in range(1,13):
        story=f'Story{st}';rr=[d for d in alltruth if d['target_zeta']==z and d['Story']==story];pk=max(d['reference_peak_kN'] for d in rr);Denv=1-pk/P0env[story];Dmin=min(d['reference_D'] for d in rr);row=dict(target_zeta=z,Story=story,P0env_kN=P0env[story],reference_envelope_peak_kN=pk,reference_envelope_D=Denv,reference_controlling_inputs=';'.join(d['Case'] for d in rr if d['reference_peak_kN']==pk),min_individual_reference_D=Dmin,min_individual_controlling_inputs=';'.join(d['Case'] for d in rr if d['reference_D']==Dmin),envelope_minus_min_individual_D=Denv-Dmin);envtruth.append(row)
        for o in [1,2]:
            e=next(d for d in env if d['target_zeta']==z and d['Taylor_order']==o and d['Story']==story);envvalidation.append({**e,**{k:row[k] for k in ['reference_envelope_peak_kN','reference_envelope_D','reference_controlling_inputs','min_individual_reference_D','envelope_minus_min_individual_D']},'peak_covered':bool(e['L_env_kN']<=pk<=e['U_env_kN']),'point_insufficient_miss':bool(Denv<Dreq and e['D_env_point']>=Dreq),'interval_insufficient_miss':bool(Denv<Dreq and e['decision_status']=='meets'),'interval_false_insufficient':bool(Denv>=Dreq and e['decision_status']=='insufficient'),'true_envelope_adverse':bool(Denv<0),'actual_input_among_potential':all(c in e['potential_controlling_inputs'].split(';') for c in row['reference_controlling_inputs'].split(';'))})
cv=[]
for c in envcandidates:
    z=c['target_zeta'];rr=[d for d in envtruth if d['target_zeta']==z];truepass=all(d['reference_envelope_D']>=Dreq for d in rr);strongpass=all(d['min_individual_reference_D']>=Dreq for d in rr);act=c['envelope_candidate_action'];cv.append({**c,'true_envelope_all12_meet':truepass,'true_strong_each_input_all12_meet':strongpass,'envelope_false_pass':bool(not truepass and act=='pass'),'envelope_false_reject':bool(truepass and act=='reject'),'min_envelope_reference_D':min(d['reference_envelope_D'] for d in rr),'min_strong_reference_D':min(d['min_individual_reference_D'] for d in rr)})
cs('all-individual-reference-peaks-144.csv',alltruth);cs('input-envelope-reference-peaks-and-strong-objective-48.csv',envtruth);cs('input-envelope-interval-and-objective-validation-96.csv',envvalidation);cs('input-envelope-candidate-validation-8.csv',cv)
js('results.json',dict(completed_utc=now(),new_derivative_solves=0,new_target_state_solves=2,reused8_arrays=2,all_individual_rows=288,all_truth_rows=144,envelope_interval_rows=96,envelope_truth_rows=48,new_individual_all_curve_covered=all(d['curve_covered_strict'] for d in comparisons),new_individual_all_peak_covered=all(d['peak_covered'] for d in comparisons),envelope_all_peak_covered=all(d['peak_covered'] for d in envvalidation),all_actual_controlling_inputs_in_potential=all(d['actual_input_among_potential'] for d in envvalidation),candidate_validation=cv,baseline_envelope=baseenv,wall_total_seconds=perf_counter()-start,process_CPU_total_seconds=process_time()-cpu0,unchanged_bound_source_hashes=all(sha(Path(d['path']))==d['sha256'] for d in bindings),FFT_direct_all_pass=all(d['within_guard'] for d in newfft),new_individual_point_miss_count=sum(d['point_insufficient_miss'] for d in comparisons),envelope_point_miss_count=sum(d['point_insufficient_miss'] for d in envvalidation),envelope_interval_miss_count=sum(d['interval_insufficient_miss'] for d in envvalidation),envelope_false_reject_count=sum(d['envelope_false_reject'] for d in cv)))
print(json.dumps(dict(candidate_validation=cv,baseline_envelope=baseenv),ensure_ascii=False,indent=2))
