from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def cs(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
 assert (O/n).stat().st_size<1000000
def js(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
ref=json.loads((P/'R004/results.json').read_text(encoding='utf-8'));pairpath=P/'R005/all12-threewaves-UPC-paired-36.csv';ancpath=P/'R005/all12-four-anchors-both-zeta-signed-reference-288.csv';pairs=read(pairpath);anc=read(ancpath)
sources=[Path(d['path']) for d in ref['arrays_local_only']]+[pairpath,ancpath];bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sources]
for d in ref['arrays_local_only']:assert sha(Path(d['path']))==d['sha256']
js('input-rules-freeze.json',dict(start_observed_utc='2026-10-31T04:24:53+00:00',deadline_utc='2026-10-31T04:32:53+00:00',frozen_utc=datetime.now(timezone.utc).isoformat(),inputs=bindings,delta='max_t abs(abs(E_ref)-abs(native)); observed amplitude deviation only, not signed force residual or fullFE error bound',native_anchor_deviation='abs(E_ref(tau))-abs(native(tau)), report signed amplitude difference and its absolute magnitude',ratio_observed_scale='(delta8 + native_ratio*delta5)/P_ref5; an a-posteriori observed-amplitude ratio scale, not prospective fullFE uncertainty bound',chi='1-abs(E_ref)/sum_r abs(v_ref_r), all300 same-time terms; undefined if sumabs=0',beta='v_ref_i/E_ref and remaining295 sum/E_ref; undefined exactly E=0, preserve negative and >1',anchors='reuse all288 R005 anchor labels and fixed5 modes unchanged; native sign unaligned, no native signed-force residual',no_new_ODE_fit_or_CM_recalculation=True))
states=[];extraanchors=[];maxclosure=maxnegates=maxErebuild=0.;undefined=negative=overone=0
for info in ref['arrays_local_only']:
 path=Path(info['path']);case=path.name.split('-')[1];z=float(path.name.split('-z')[1].split('-')[0])
 with np.load(path,allow_pickle=False) as a:
  t=a['t'];E=a['shear_elastic_inertia_predicted_kN'];s=a['s_unitGamma'];w=a['omega'];B=a['B_direct']
  for st in range(1,13):
   story='Story'+str(st);j=st-1;y=a['shear_native_'+story+'_kN'];e=E[:,j];d=abs(e)-abs(y);ii=int(np.argmax(abs(d)));pn=float(np.max(abs(y)));pr=float(np.max(abs(e)));pair=next(d for d in pairs if d['Case']==case and d['Story']==story)
   out=dict(Case=case,Story=story,zeta=z,delta_abs_inf_observed_amplitude_kN=float(abs(d[ii])),delta_over_native_peak=abs(float(d[ii]))/pn,delta_max_time_s=float(t[ii]),delta_max_sample_index=ii,reference_abs_at_delta_time_kN=float(abs(e[ii])),native_abs_at_delta_time_kN=float(abs(y[ii])),native_absolute_peak_kN=pn,reference_absolute_peak_kN=pr,absolute_peak_amplitude_difference_kN=abs(pr-pn),peak_difference_le_observed_delta=bool(abs(pr-pn)<=abs(d[ii])+1e-8))
   for label,tt in [('native5_peak',float(pair['native5_peak_s'])),('native8_peak',float(pair['native8_peak_s']))]:
    ix=np.flatnonzero(np.isclose(t,tt,rtol=0,atol=1e-9));assert len(ix)==1;it=int(ix[0]);out[label+'_time_s']=tt;out[label+'_amplitude_difference_refminusnative_kN']=float(d[it]);out[label+'_absolute_observed_amplitude_deviation_kN']=float(abs(d[it]))
   out['scope']='observed absolute-amplitude deviation only; eta unknown; not signed force residual or fullFE bound';states.append(out)
  for row in anc:
   if row['Case']!=case or float(row['zeta'])!=z:continue
   j=int(row['Story'][5:])-1;ix=np.flatnonzero(np.isclose(t,float(row['time_s']),rtol=0,atol=1e-9));assert len(ix)==1;it=int(ix[0]);vv=B[j]*w*w*s[it]/1000;total=float(vv.sum());Sabs=float(abs(vv).sum());maxErebuild=max(maxErebuild,abs(total-float(E[it,j])),abs(total-float(row['reference_sum_signed_kN'])));top=[int(row[f'fixed5_rank{k}_Mode'])-1 for k in range(1,6)];rest=[i for i in range(300) if i not in top]
   rr={**row,'sum_abs_all300_signed_reference_terms_kN':Sabs,'chi_same_time_all300':1-abs(total)/Sabs if Sabs else None,'reference_E_denominator_kN':total,'beta_status':'defined' if total!=0 else 'undefined_E_zero'}
   beta=[]
   for k,ir in enumerate(top,1):
    b=float(vv[ir]/total) if total!=0 else None;rr[f'fixed5_rank{k}_beta']=b;beta.append(b)
    if b is not None:negative+=b<0;overone+=b>1;maxnegates=max(maxnegates,abs(float((-vv[ir])/(-total))-b))
   br=float(vv[rest].sum()/total) if total!=0 else None;rr['remaining295_sum_beta']=br
   if total!=0:rr['top5_plus_remaining_beta_sum']=float(sum(beta)+br);maxclosure=max(maxclosure,abs(rr['top5_plus_remaining_beta_sum']-1))
   else:rr['top5_plus_remaining_beta_sum']=None;undefined+=1
   native=float(a['shear_native_'+row['Story']+'_kN'][it]);dd=abs(total)-abs(native);rr['same_time_amplitude_difference_refminusnative_kN']=dd;rr['same_time_absolute_observed_amplitude_deviation_kN']=abs(dd);rr['signed_native_force_residual_unaligned']=None;rr['scope']='all300 same-time reference chi/beta; native eta unverified; amplitude deviation is not signed force residual';extraanchors.append(rr)
cs('observed-amplitude-delta-and-native-anchor-deviations-72.csv',states);cs('same-time-chi-beta-and-observed-amplitude-288.csv',extraanchors)
paired=[]
for pair in pairs:
 case=pair['Case'];story=pair['Story'];d5=next(d for d in states if d['Case']==case and d['Story']==story and d['zeta']==.05);d8=next(d for d in states if d['Case']==case and d['Story']==story and d['zeta']==.08)
 p5=float(pair['P5_reference_peak_kN']);rn=float(pair['native_peak8_kN'])/float(pair['native_peak5_kN']);rr=float(pair['P8_reference_peak_kN'])/p5;disc=abs(rr-rn);scale=(d8['delta_abs_inf_observed_amplitude_kN']+rn*d5['delta_abs_inf_observed_amplitude_kN'])/p5;assert disc<=scale+1e-12
 paired.append(dict(Case=case,Story=story,delta5_abs_inf_observed_amplitude_kN=d5['delta_abs_inf_observed_amplitude_kN'],delta8_abs_inf_observed_amplitude_kN=d8['delta_abs_inf_observed_amplitude_kN'],delta5_over_native5_peak=d5['delta_over_native_peak'],delta8_over_native8_peak=d8['delta_over_native_peak'],reference_peak_decrease_percent=float(pair['reference_peak_decrease_percent']),native_peak_decrease_percent=float(pair['native_peak_decrease_percent']),signed_decrease_discrepancy_percentage_points=float(pair['reference_minus_native_decrease_percentage_points']),absolute_peak_ratio_discrepancy=disc,absolute_decrease_discrepancy_percentage_points=100*disc,observed_amplitude_ratio_mismatch_scale=scale,observed_amplitude_decrease_mismatch_scale_percentage_points=100*scale,ratio_discrepancy_le_observed_scale=bool(disc<=scale+1e-12),scope='observed absolute-amplitude mismatch scale, not fullFE error bound'))
cs('peak-decrease-discrepancy-and-observed-scales-36.csv',paired);cs('Story5-Story12-decrease-and-observed-scales-6.csv',[d for d in paired if d['Story'] in ['Story5','Story12']]);cs('Story5-Story12-same-time-chi-beta-48.csv',[d for d in extraanchors if d['Story'] in ['Story5','Story12']])
summary=dict(completed_utc=datetime.now(timezone.utc).isoformat(),state_delta_rows=72,paired_rows=36,anchor_beta_rows=288,undefined_E_zero_rows=undefined,negative_top5_beta_values=negative,top5_beta_over_one_values=overone,max_beta_partition_sum_error=maxclosure,max_common_sign_reversal_beta_difference=maxnegates,max_rebuilt_E_difference_kN=maxErebuild,max_delta_state=max(states,key=lambda d:d['delta_abs_inf_observed_amplitude_kN']),max_normalized_delta_state=max(states,key=lambda d:d['delta_over_native_peak']),max_abs_decrease_discrepancy_pair=max(paired,key=lambda d:d['absolute_decrease_discrepancy_percentage_points']),max_beta=max((d[f'fixed5_rank{k}_beta'] for d in extraanchors for k in range(1,6) if d[f'fixed5_rank{k}_beta'] is not None),default=None),min_beta=min((d[f'fixed5_rank{k}_beta'] for d in extraanchors for k in range(1,6) if d[f'fixed5_rank{k}_beta'] is not None),default=None),priority=[d for d in paired if d['Story'] in ['Story5','Story12']],source_hashes_unchanged=all(sha(p)==b['sha256'] for p,b in zip(sources,bindings)))
js('results.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
