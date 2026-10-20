"""Posterior amplitude-only reference on two saved H2 trajectories; no ODE."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
P=Path(__file__).resolve().parent;F=json.loads((P/'R005-input-freeze.json').read_text(encoding='utf-8'))
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def write_csv(name,rows):
 p=P/name;assert not p.exists()
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
for s in F['inputs']:assert sha(P/s['file'])==s['sha256']
cache=[];sources=[];error=[]
for name in ['R003-none-summary.json','R003-story1-summary.json']:
 s=json.loads((P/name).read_text(encoding='utf-8'));src=Path(s['source_state']['path']);assert sha(src)==s['source_state']['sha256']
 with np.load(src) as f:a=f['trajectory']
 t=a[:,0];u=a[:,1:4];M=np.array(s['mass']);phi=np.array(s['phi_columns_mass_normalized']);ell=np.array([-1.,1.,0.]);terms=(u@M@phi)*(ell@phi);direct=u@ell
 err=float(np.max(abs(terms.sum(axis=1)-direct)));assert err<1e-12
 cache.append({'t':t,'terms':terms,'y':direct,'M':M,'phi':phi});sources.append(s['source_state']);error.append(err)
assert np.array_equal(cache[0]['t'],cache[1]['t']) and np.array_equal(cache[0]['M'],cache[1]['M']) and np.array_equal(cache[0]['phi'],cache[1]['phi'])
t=cache[0]['t'];v0=cache[0]['terms'];vd=cache[1]['terms'];peak0=np.max(abs(v0),axis=0);peakd=np.max(abs(vd),axis=0);assert np.all(peak0>0)
ratios=peakd/peak0;vr=v0*ratios;yr=vr.sum(axis=1);reference_modal_peak_match=float(np.max(abs(np.max(abs(vr),axis=0)-peakd)));assert reference_modal_peak_match<1e-12
with (P/'R004-whole-window-mode-peaks.csv').open(encoding='utf-8') as f:old=list(csv.DictReader(f))
assert np.max(abs(ratios-np.array([float(r['story1_over_none_amplitude_ratio']) for r in old])))<1e-12
Y={'none_full':cache[0]['y'],'posterior_amplitude_only_reference':yr,'actual_device_story1':cache[1]['y']};P0=float(np.max(abs(Y['none_full'])));rows=[]
for label,y in Y.items():
 i=int(np.argmax(abs(y)));peak=float(abs(y[i]));rows.append({'output':label,'QS2_absolute_peak':peak,'QS2_signed_at_peak':float(y[i]),'peak_time_nondimensional':float(t[i]),'peak_over_none':peak/P0,'peak_change_from_none_percent':100*(peak/P0-1),'definition':'sum a_k Vnone,k artificial reference' if label=='posterior_amplitude_only_reference' else 'direct complete saved-state QS2'})
common=[]
for when in F['common_times']:
 i=int(round(when/F['h']));assert abs(float(t[i])-when)<1e-12
 common.append({'time_nondimensional':float(t[i]),**{label:float(y[i]) for label,y in Y.items()},'reference_minus_actual_signed':float(yr[i]-cache[1]['y'][i]),'reference_abs_minus_actual_abs':float(abs(yr[i])-abs(cache[1]['y'][i]))})
mode=[]
for k in range(3):mode.append({'mode':k+1,'none_mode_absolute_peak':float(peak0[k]),'actual_device_mode_absolute_peak':float(peakd[k]),'a_k':float(ratios[k]),'reference_mode_absolute_peak':float(np.max(abs(vr[:,k]))),'reference_actual_waveform_max_abs_difference':float(np.max(abs(vr[:,k]-vd[:,k])))})
write_csv('R005-three-output-peaks.csv',rows);write_csv('R005-common-time-values.csv',common);write_csv('R005-mode-scale-and-waveform-check.csv',mode)
out={'sources':sources,'saved_nodes':len(t),'window':[float(t[0]),float(t[-1])],'same_M_Phi_and_grid':True,'full_reconstruction_max_abs_error':max(error),'reference_modal_peak_matches_actual_max_abs_error':reference_modal_peak_match,'reference_actual_output_max_abs_difference':float(np.max(abs(yr-cache[1]['y']))),'peak_rows':rows,'common_rows':common,'mode_scales':mode,'new_ODE_runs':0,'interpretation':'artificial posterior reference only, no independent causal or realizability/phase-angle claim'}
(P/'R005-numeric-summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(out,ensure_ascii=False))
