import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,importlib.util
import numpy as np
O=Path(__file__).resolve().parent;R=O.parents[5];P=O.parent/'R001';L=O/'local-cache';L.mkdir(exist_ok=False);(L/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,d):
 with (O/n).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cs(n,rows):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def mod(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prior=json.loads((P/'input-rules-freeze.json').read_text(encoding='utf-8'));oldmodel=json.loads((P/'models-small-N24.json').read_text(encoding='utf-8'))['N24_elastic_rc1e-10'];olderrors=read(P/'prediction-errors-N24-24.csv');oldtrace=P/'local-cache/N24-two-operator-traces.npz';oldmanifest=json.loads((P/'delivery-manifest.json').read_text(encoding='utf-8'))
assert sha(oldtrace)==oldmanifest['local_only_array']['sha256']
for b in prior['source']:assert sha(Path(b['path']))==b['sha256']
extra=[P/'models-small-N24.json',P/'prediction-errors-N24-24.csv',oldtrace]
js('input-rules-freeze.json',{'start_observed_utc':'2026-10-30T12:51:00+00:00','deadline_utc':'2026-10-30T13:01:00+00:00','frozen_utc':datetime.now(timezone.utc).isoformat(),'N':36,'operator':'elastic','rcond':[1e-10,1e-8],'train_native5':['SHW3X','SHW4X'],'holdout_native5':'RH4X','predict_native8_fixed_map_all':True,'no_N24_or_other_N_refit':True,'ag_no_extra_multiplier':True,'source':prior['source'],'frozen_N24_inputs':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in extra],'common_group_boundaries':[[1,3],[4,6],[7,12],[13,24]],'comparison':'curve difference L2 over native L2 and over N24 own group L2, also absolute RMS kN','scope':'one bounded extension stability check, fitted-model only; no later N scan','code_sha256':sha(Path(__file__))})
lp=R/'research/sessions/20261025-1337/roles/role6/R001/load_inputs.py';cfg,om,data=mod(lp,'n36loader').load_inputs();helper=mod(Path(cfg['modal_linear_py']),'n36helper');w=om[:36];cases=['SHW3X','SHW4X','RH4X'];stories=['Story5','Story12'];X={}
for case in cases:
 for z in [.05,.08]:
  Q,V,_=helper.states(data[case]['ag'],w,z,.02);X[case,z]=Q*w*w
Xt=np.vstack([X[c,.05] for c in cases[:2]]);Yt=np.vstack([np.column_stack([data[c]['Y0'][s] for s in stories]) for c in cases[:2]])
metrics=[];models={};coeff=[];groups=[];traces={};saved={};raw24=np.array(oldmodel['raw_output_coef']);conditions=[]
for rc in [1e-10,1e-8]:
 m=helper.fit_map(Xt,Yt,rcond=rc);raw=np.zeros((36,2));raw[m['active']]=m['coef']/m['scale'][m['active'],None];vid=f'N36_elastic_rc{rc:g}';sv=m['singular_values'];conditions.append({'variant':vid,'rank':m['rank'],'active_count':int(m['active'].sum()),'scaled_full_condition':float(sv[0]/sv[-1]),'scaled_retained_condition':float(sv[0]/sv[m['rank']-1]),'scaled_singular_max':float(sv[0]),'scaled_singular_min':float(sv[-1])})
 models[vid]={'N':36,'operator':'elastic','rcond':rc,'rank':m['rank'],'singular_values':sv.tolist(),'active':m['active'].tolist(),'training_scale':m['scale'].tolist(),'raw_output_coef':raw.tolist()}
 for j,story in enumerate(stories):
  for ir in range(36):coeff.append({'variant':vid,'Story':story,'Mode':ir+1,'omega_rad_s':float(w[ir]),'raw_signed_output_coefficient':float(raw[ir,j]),'active':bool(m['active'][ir])})
 for case in cases:
  for z,ys in [(.05,'Y0'),(.08,'Y3')]:
   xx=X[case,z];pred=helper.predict_map(m,xx);terms=xx[:,:,None]*raw[None,:,:];assert np.max(abs(terms.sum(1)-pred))<1e-6
   for j,story in enumerate(stories):
    y=data[case][ys][story];yh=pred[:,j];t=data[case]['t'];ni=int(np.argmax(abs(y)));pi=int(np.argmax(abs(yh)));old=next(q for q in olderrors if q['operator']=='elastic' and q['Story']==story and q['Case']==case and float(q['zeta'])==z)
    metrics.append({'variant':vid,'N':36,'operator':'elastic','rcond':rc,'rank':m['rank'],'Case':case,'Story':story,'zeta':z,'evaluation':'train5' if z==.05 and case in cases[:2] else ('heldout5' if z==.05 else 'fixed_map8'),'NRMSE':float(np.linalg.norm(yh-y)/np.linalg.norm(y)),'native_peak_kN':float(np.max(abs(y))),'predicted_peak_kN':float(np.max(abs(yh))),'peak_relative_error':float(np.max(abs(yh))/np.max(abs(y))-1),'native_peak_time_s':float(t[ni]),'predicted_peak_time_s':float(t[pi]),'native_peak_SourceRow':old['native_peak_SourceRow'],'frozen_N24_NRMSE':float(old['NRMSE']),'NRMSE_change_N36_minus_N24':float(np.linalg.norm(yh-y)/np.linalg.norm(y))-float(old['NRMSE']),'scope':'fixed output reference fit; no true modal identifiability claim'})
    tag=f'{vid}__{case}__{story}__z{z:g}';traces[tag+'__t']=t;traces[tag+'__native']=y;traces[tag+'__prediction']=yh;traces[tag+'__terms']=terms[:,:,j];saved[vid,case,story,z]=(yh,terms[:,:,j])
 cs('early-'+vid+'-errors-12.csv',[q for q in metrics if q['variant']==vid]);print('EARLY_'+vid+' '+datetime.now(timezone.utc).isoformat(),flush=True)
cs('prediction-errors-N36-24.csv',metrics);cs('models-condition-2.csv',conditions);cs('fixed-output-coefficients-N36-144.csv',coeff);js('models-small-N36.json',models)
print('ALL_N36_ERROR_TABLE_SAVED '+datetime.now(timezone.utc).isoformat(),flush=True)
with np.load(oldtrace,allow_pickle=False) as previous:
 for rc in [1e-10,1e-8]:
  vid=f'N36_elastic_rc{rc:g}'
  for case in cases:
   for z in [.05,.08]:
    for story in stories:
     tag=f'elastic__{case}__{story}__z{z:g}';oldterms=previous[tag+'__terms'];y=previous[tag+'__native'];assert np.array_equal(y,data[case]['Y0' if z==.05 else 'Y3'][story]);assert np.array_equal(previous[tag+'__t'],data[case]['t'])
     yh,newterms=saved[vid,case,story,z];it=int(np.argmax(abs(y)));den=float(np.linalg.norm(y))
     for first,last in [(1,3),(4,6),(7,12),(13,24)]:
      a=oldterms[:,first-1:last].sum(1);b=newterms[:,first-1:last].sum(1);diff=b-a;own=float(np.linalg.norm(a))
      groups.append({'variant':vid,'Case':case,'Story':story,'zeta':z,'group':f'{first}to{last}','N24_group_RMS_kN':float(np.sqrt(np.mean(a*a))),'N36_group_RMS_kN':float(np.sqrt(np.mean(b*b))),'difference_RMS_kN':float(np.sqrt(np.mean(diff*diff))),'difference_L2_over_native_L2':float(np.linalg.norm(diff)/den),'difference_L2_over_N24_group_L2':float(np.linalg.norm(diff)/own) if own else None,'native_RMS_kN':float(np.sqrt(np.mean(y*y))),'native_peak_time_s':float(data[case]['t'][it]),'N24_group_signed_at_native_peak_kN':float(a[it]),'N36_group_signed_at_native_peak_kN':float(b[it]),'scope':'same fitted frequency-ordered group, no selection or physical contribution claim'})
cs('N24-to-N36-common-group-curves-96.csv',groups)
stability=[]
for story,j in [('Story5',0),('Story12',1)]:
 a=np.array(models['N36_elastic_rc1e-10']['raw_output_coef'])[:,j];b=np.array(models['N36_elastic_rc1e-08']['raw_output_coef'])[:,j]
 stability.append({'Story':story,'N36_rcond_raw_coef_relative_L2':float(np.linalg.norm(a-b)/np.linalg.norm(a)),'max_abs_prediction_rcond_difference_kN':max(float(np.max(abs(saved['N36_elastic_rc1e-10',c,story,z][0]-saved['N36_elastic_rc1e-08',c,story,z][0]))) for c in cases for z in [.05,.08])})
cs('rcond-stability-2.csv',stability);np.savez_compressed(L/'N36-elastic-two-rcond-traces.npz',**traces)
for q in prior['source']:assert sha(Path(q['path']))==q['sha256']
assert sha(oldtrace)==oldmanifest['local_only_array']['sha256']
js('results.json',{'completed_utc':datetime.now(timezone.utc).isoformat(),'N_only':36,'variants':2,'prediction_rows':24,'common_group_rows':96,'condition':conditions,'rcond_stability':stability,'validation':[q for q in metrics if q['evaluation']!='train5'],'no_N6_N12_N24_refit':True,'native8_not_refitted':True,'all_arrays_local_only':True,'sources_unchanged':True})
print(json.dumps({'conditions':conditions,'rcond_stability':stability,'validation':[{k:q[k] for k in ['variant','Story','Case','evaluation','NRMSE','peak_relative_error','NRMSE_change_N36_minus_N24']} for q in metrics if q['evaluation']!='train5']}))
