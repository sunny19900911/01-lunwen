"""QS2 same-time/modal-amplitude postprocessing only; saved H2 states, no ODE."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
P=Path(__file__).resolve().parent;F=json.loads((P/'R004-input-freeze.json').read_text(encoding='utf-8'))
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def csvout(name,rows):
 p=P/name;assert not p.exists()
 with p.open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
cache={};sources=[];errors=[]
for src,pos in zip(F['source_summaries'],F['positions']):
 sf=P/src['file'];assert sha(sf)==src['sha256'];s=json.loads(sf.read_text(encoding='utf-8'));state=Path(s['source_state']['path']);assert sha(state)==s['source_state']['sha256']
 with np.load(state) as f:a=f['trajectory']
 t=a[:,0];u=a[:,1:4];M=np.array(s['mass']);phi=np.array(s['phi_columns_mass_normalized']);q=u@M@phi;ell=np.array([-1.,1.,0.]);coef=ell@phi;terms=q*coef;direct=u@ell
 err=float(np.max(abs(terms.sum(axis=1)-direct)));assert err<1e-12
 cache[pos]={'t':t,'q':q,'terms':terms,'y':direct,'coef':coef};errors.append(err);sources.append(s['source_state'])
assert np.array_equal(cache[0]['t'],cache[1]['t'])
t=cache[0]['t'];anchors=sorted({int(round(x/F['h']))+d for x in F['common_required_times'] for d in F['nearby_index_offsets']});common=[];diff=[]
for i in anchors:
 for pos in F['positions']:
  c=cache[pos];v=c['terms'][i];den=float(np.sum(abs(v)));total=float(c['y'][i]);tag='required_common_peak_time' if any(abs(float(t[i])-x)<1e-12 for x in F['common_required_times']) else 'nearby_common_time'
  common.append({'position':pos,'scheme':'none' if pos==0 else 'device_story1','index0':i,'time_nondimensional':float(t[i]),'anchor':tag,'mode1_signed':float(v[0]),'mode2_signed':float(v[1]),'mode3_signed':float(v[2]),'sum_modes':float(np.sum(v)),'QS2_direct':total,'sum_abs_terms':den,'abs_sum_over_sum_abs':abs(total)/den if den else None})
 v=cache[1]['terms'][i]-cache[0]['terms'][i]
 diff.append({'index0':i,'time_nondimensional':float(t[i]),'device_minus_none_mode1':float(v[0]),'device_minus_none_mode2':float(v[1]),'device_minus_none_mode3':float(v[2]),'device_minus_none_total':float(cache[1]['y'][i]-cache[0]['y'][i]),'none_total':float(cache[0]['y'][i]),'device_total':float(cache[1]['y'][i]),'device_abs_minus_none_abs':float(abs(cache[1]['y'][i])-abs(cache[0]['y'][i]))})
peaks=[]
for mode in range(3):
 row={'mode':mode+1,'QS2_output_coefficient':float(cache[0]['coef'][mode])}
 for pos,name in [(0,'none'),(1,'story1')]:
  c=cache[pos];v=c['terms'][:,mode];i=int(np.argmax(abs(v)));row.update({name+'_absolute_peak':float(abs(v[i])),name+'_signed_at_peak':float(v[i]),name+'_peak_time':float(t[i]),name+'_q_absolute_peak':float(np.max(abs(c['q'][:,mode])))})
 row['story1_over_none_amplitude_ratio']=row['story1_absolute_peak']/row['none_absolute_peak'] if row['none_absolute_peak']>0 else None
 row['signed_peak_change_percent']=100*(row['story1_over_none_amplitude_ratio']-1) if row['story1_over_none_amplitude_ratio'] is not None else None
 peaks.append(row)
csvout('R004-common-time-terms.csv',common);csvout('R004-common-time-differences.csv',diff);csvout('R004-whole-window-mode-peaks.csv',peaks)
lo,hi=F['plot_window'];ii=np.flatnonzero((t>=lo)&(t<=hi));local=[]
for i in ii:
 row={'time_nondimensional':float(t[i])}
 for pos,name in [(0,'none'),(1,'story1')]:
  for k in range(3):row[name+f'_mode{k+1}']=float(cache[pos]['terms'][i,k])
  row[name+'_total']=float(cache[pos]['y'][i])
 local.append(row)
csvout('R004-local-curves.csv',local)
out={'sources':sources,'state_reconstruction_errors':errors,'full_window':[float(t[0]),float(t[-1])],'saved_nodes_each':len(t),'common_rows':len(common),'common_time_count':len(anchors),'plot_rows':len(local),'required_common_values':[x for x in diff if any(abs(x['time_nondimensional']-v)<1e-12 for v in F['common_required_times'])],'whole_window_modal_peaks':peaks,'new_ODE_runs':0,'scope':'posthoc fixed-basis QS2 modal terms, not isolated modal dynamics or unique causal attribution'}
(P/'R004-numeric-summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(out,ensure_ascii=False))
