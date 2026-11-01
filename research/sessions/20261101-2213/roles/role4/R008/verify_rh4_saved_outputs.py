from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cs(n,rows):
    with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rules=json.loads((O/'input-method-freeze.json').read_text(encoding='utf-8'));freeze=json.loads((O/'prediction-S-envelope-freeze.json').read_text(encoding='utf-8'));res=json.loads((O/'results.json').read_text(encoding='utf-8'));idx=json.loads((O/'target-array-index.json').read_text(encoding='utf-8'));assert all(sha(Path(d['path']))==d['sha256'] for d in rules['inputs']);assert all(sha(Path(d['path']))==d['sha256'] for d in freeze['files']);assert sha(Path(freeze['local_array']['path']))==freeze['local_array']['sha256'];assert all(sha(Path(d['path']))==d['sha256'] for d in idx)
with np.load(freeze['local_array']['path'],allow_pickle=False) as a:
    t=a['t'].copy();ag=a['ag'].copy();om=a['omega'].copy();B=a['B'].copy();s0=a['s0'].copy();Z=a['Z'].copy();V0=a['V0'].copy();VZ=a['VZ'].copy();PV={(z,o):a[f'z{z:g}_order{o}_V'].copy() for z in [.06,.07] for o in [1,2]};EE={(z,o):a[f'z{z:g}_order{o}_E'].copy() for z in [.06,.07] for o in [1,2]}
sr=rd(O/'baseline-S-ranked-floors-12.csv');mm=rd(O/'all-mode-signed-S-sources-3600.csv');ref=rd(O/'exact-reference-floor-peaks-24.csv');comp=rd(O/'prediction-vs-reference-48.csv');interval=rd(O/'interval-coverage-and-decision-validation-48.csv');candidates=rd(O/'candidate-decision-validation-4.csv');ranks=rd(O/'posterior-S-vs-reference-ranks-24.csv');maxclosure=maxS=maxpeak=maxmetric=0.;strictmiss=0
P0=np.max(abs(V0),axis=0)
for j in range(12):
    story=f'Story{j+1}';r=next(d for d in sr if d['Story']==story);amp=abs(V0[:,j]);act=np.flatnonzero(amp==P0[j]);g=np.sign(V0[:,j])*VZ[:,j];p=float(np.max(g[act]));ctrl=act[g[act]==p];Sc=-p/P0[j];maxS=max(maxS,abs(Sc-float(r['S_percent_per_damping_pp'])));assert ';'.join(str(int(n)) for n in ctrl)==r['controller_indices']
    for ci,n in enumerate(ctrl):
        c=-np.sign(V0[n,j])*(B[j]*om**2/1000)*Z[n]/P0[j];mr=[d for d in mm if d['Story']==story and int(d['controller_number'])==ci+1];assert len(mr)==300;maxclosure=max(maxclosure,abs(c.sum()-Sc));assert max(abs(c[int(d['Mode'])-1]-float(d['c_improvement_percent_per_damping_pp'])) for d in mr)<1e-12
assert maxS<1e-12 and maxclosure<1e-11
for entry in idx:
    z=entry['target_zeta']
    with np.load(entry['path'],allow_pickle=False) as a:
        assert np.array_equal(t,a['t']) and np.array_equal(ag,a['ag']) and np.array_equal(om,a['omega']) and np.array_equal(B,a['B']);q=a['s'].copy();V=a['V'].copy()
    assert np.max(abs(V-(q*om**2)@B.T/1000))<1e-10
    for j in range(12):
        story=f'Story{j+1}';ip=int(np.argmax(abs(V[:,j])));Pk=float(abs(V[ip,j]));D=1-Pk/P0[j];rr=next(d for d in ref if float(d['target_zeta'])==z and d['Story']==story);maxpeak=max(maxpeak,abs(Pk-float(rr['reference_peak_kN'])));assert abs(D-float(rr['reference_D']))<1e-12 and float(rr['reference_signed_peak_kN'])==float(V[ip,j]);assert float(rr['reference_peak_time_s'])==float(t[ip])
        for o in [1,2]:
            ir=next(d for d in interval if float(d['target_zeta'])==z and int(d['Taylor_order'])==o and d['Story']==story);pr=next(d for d in comp if float(d['target_zeta'])==z and int(d['Taylor_order'])==o and d['Story']==story);ph=float(np.max(abs(PV[z,o][:,j])));lo=float(np.max(np.maximum(0,abs(PV[z,o][:,j])-EE[z,o][:,j])));up=float(np.max(abs(PV[z,o][:,j])+EE[z,o][:,j]));maxmetric=max(maxmetric,abs(ph/Pk-1-float(pr['peak_relative_error'])),abs(lo-float(ir['P_lower_kN'])),abs(up-float(ir['P_upper_kN'])));strictmiss+=int(np.count_nonzero(abs(PV[z,o][:,j]-V[:,j])>EE[z,o][:,j]));DL=1-up/P0[j];DU=1-lo/P0[j];decision='meets' if DL>=.1 else ('insufficient' if DU<.1 else 'uncertain');assert decision==ir['decision_status'];assert (ir['v001_recompute']=='True')==(decision=='uncertain' or DU-DL>.05)
assert maxpeak==0 and maxmetric<1e-10
for r in candidates:
    z=float(r['target_zeta']);o=int(r['Taylor_order']);ir=[d for d in interval if float(d['target_zeta'])==z and int(d['Taylor_order'])==o];action='reject' if any(d['decision_status']=='insufficient' for d in ir) else ('pass' if all(d['decision_status']=='meets' and d['width_status']=='acceptable' for d in ir) else 'recompute');assert action==r['v002_action']
inversionrows=[]
for z in [.06,.07]:
    for i,a in enumerate(sr):
        for b in sr[i+1:]:
            da=next(d for d in ranks if float(d['target_zeta'])==z and d['Story']==a['Story']);db=next(d for d in ranks if float(d['target_zeta'])==z and d['Story']==b['Story'])
            if (float(a['S_percent_per_damping_pp'])-float(b['S_percent_per_damping_pp']))*(float(da['reference_D'])-float(db['reference_D']))<0:inversionrows.append(dict(target_zeta=z,baseline_slower_floor=a['Story'],baseline_faster_floor=b['Story'],S_slower=float(a['S_percent_per_damping_pp']),S_faster=float(b['S_percent_per_damping_pp']),reference_D_of_baseline_slower=float(da['reference_D']),reference_D_of_baseline_faster=float(db['reference_D'])))
cs('posterior-rank-inversion-pairs-4.csv',inversionrows);miss=[d for d in comp if d['point_miss_insufficient']=='True'];cs('point-insufficient-miss-cases-1.csv',miss)
fft=rd(O/'positive-FFT-direct-checks-16.csv');assert len(fft)==16 and all(d['within_guard']=='True' for d in fft)
verification=dict(completed_utc=datetime.now(timezone.utc).isoformat(),baseline_S_rows_verified=12,modal_source_rows_verified=3600,max_modal_closure_error=maxclosure,reference_peak_rows_verified=24,prediction_interval_rows_verified=48,candidate_actions_verified=4,max_peak_difference_kN=maxpeak,max_predicted_metric_difference=maxmetric,strict_uncovered_samples=strictmiss,rank_inversion_pairs_verified=len(inversionrows),FFT_direct_checks=16,source_and_frozen_prediction_hashes_unchanged=True,reference_array_hashes_unchanged=True,extra_target_state_solves=0,old8_response_read=False,original_producer_exit=0,original_failure_stage=None,this_script_reads_saved_results_without_recomputing_targets=True,independent_role2_review_pending=True)
js('verification.json',verification)

print(json.dumps(verification,ensure_ascii=False,indent=2))
