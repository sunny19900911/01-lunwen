import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,importlib.util
import numpy as np
O=Path(__file__).resolve().parent;S=O.parents[2];R=O.parents[5];ROOT=S/'root-R001-low-order';L=O/'local-cache';L.mkdir(exist_ok=False);(L/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
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
root_rules=json.loads((ROOT/'input-rules-freeze.json').read_text(encoding='utf-8'));root_models=json.loads((ROOT/'models-small.json').read_text(encoding='utf-8'));root_errors=read(ROOT/'prediction-errors-96.csv')
for b in root_rules['source']:assert sha(Path(b['path']))==b['sha256']
lp=R/'research/sessions/20261025-1337/roles/role6/R001/load_inputs.py';cfgp=lp.with_name('input-config.json');cfg=json.loads(cfgp.read_text(encoding='utf-8'));hp=Path(cfg['modal_linear_py'])
js('input-rules-freeze.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'start_observed_utc':'2026-10-30T12:42:39+00:00','deadline_utc':'2026-10-30T12:52:39+00:00','root_rules':{'path':str(ROOT/'input-rules-freeze.json'),'sha256':sha(ROOT/'input-rules-freeze.json')},'source':root_rules['source'],'additional_frozen_inputs':[{'path':str(p),'sha256':sha(p)} for p in [ROOT/'models-small.json',ROOT/'prediction-errors-96.csv']],'N':24,'operators':['elastic','balance'],'rcond':1e-10,'train_native5':['SHW3X','SHW4X'],'holdout_native5':'RH4X','predict_native8_all_without_refit':['SHW3X','SHW4X','RH4X'],'scale_and_active_from_training_only':True,'ag_units':'loader already m/s^2, no additional multiplier','initial_q_v':0,'no_N6_N12_refit':True,'scope':'new N24 fitted-model extension only, not true modal decomposition','code_sha256':sha(Path(__file__))})
helper=mod(hp,'n24helper');cfg,om,data=mod(lp,'n24loader').load_inputs();assert len(om)==300
w=om[:24];cases=['SHW3X','SHW4X','RH4X'];stories=['Story5','Story12'];train=cases[:2];states={}
for case in cases:
 assert np.allclose(np.diff(data[case]['t']),.02,rtol=0,atol=1e-12)
 for z in [.05,.08]:states[case,z]=helper.states(data[case]['ag'],w,z,.02)[:2]
metrics=[];coeff=[];models={};allX={};groupchanges=[];coefchanges=[];traces={};maxsum=0.
for op in ['elastic','balance']:
 X={key:Q*w*w if op=='elastic' else Q*w*w+V*(2*key[1]*w) for key,(Q,V) in states.items()};allX[op]=X
 Xt=np.vstack([X[c,.05] for c in train]);Yt=np.vstack([np.column_stack([data[c]['Y0'][s] for s in stories]) for c in train]);m=helper.fit_map(Xt,Yt,rcond=1e-10)
 raw=np.zeros((24,2));raw[m['active']]=m['coef']/m['scale'][m['active'],None];vid=f'N24_{op}_rc1e-10';n12vid=f'N12_{op}_rc1e-10';n12=np.array(root_models[n12vid]['raw_output_coef'])
 models[vid]={'N':24,'operator':op,'rcond':1e-10,'rank':m['rank'],'singular_values':m['singular_values'].tolist(),'active':m['active'].tolist(),'training_scale':m['scale'].tolist(),'raw_output_coef':raw.tolist()}
 for j,story in enumerate(stories):
  for ir in range(24):coeff.append({'variant':vid,'Story':story,'Mode':ir+1,'omega_rad_s':float(w[ir]),'raw_signed_output_coefficient':float(raw[ir,j]),'active':bool(m['active'][ir]),'identity':'fixed fitted output coefficient, not certified modal shear coefficient'})
  for count in [6,12]:
   a=raw[:count,j];b=n12[:count,j];den=float(np.linalg.norm(b));coefchanges.append({'operator':op,'Story':story,'common_prefix_modes':count,'N12_coef_L2':den,'N24_prefix_coef_L2':float(np.linalg.norm(a)),'relative_L2_change_vs_frozen_N12':float(np.linalg.norm(a-b)/den) if den else None,'sign_changed_coefficients':int(np.sum(a*b<0)),'N24_rank':m['rank'],'N12_rank':root_models[n12vid]['rank']})
 for case in cases:
  for z,ys in [(.05,'Y0'),(.08,'Y3')]:
   xx=X[case,z];pred=helper.predict_map(m,xx);terms=xx[:,:,None]*raw[None,:,:];maxsum=max(maxsum,float(np.max(abs(terms.sum(1)-pred))));assert maxsum<1e-6
   for j,story in enumerate(stories):
    t=data[case]['t'];y=data[case][ys][story];yh=pred[:,j];ni=int(np.argmax(abs(y)));pi=int(np.argmax(abs(yh)));npk=float(abs(y[ni]));ppk=float(abs(yh[pi]));ref=next(q for q in root_errors if q['variant']==n12vid and q['Case']==case and q['Story']==story and float(q['zeta'])==z)
    metrics.append({'variant':vid,'N':24,'operator':op,'rcond':1e-10,'rank':m['rank'],'Case':case,'Story':story,'zeta':z,'evaluation':'train5' if z==.05 and case in train else ('heldout5' if z==.05 else 'fixed_map8'),'NRMSE':float(np.linalg.norm(yh-y)/np.linalg.norm(y)),'native_peak_kN':npk,'predicted_peak_kN':ppk,'peak_relative_error':ppk/npk-1,'native_peak_time_s':float(t[ni]),'predicted_peak_time_s':float(t[pi]),'pred_at_native_peak_kN':float(yh[ni]),'signed_residual_at_native_peak_kN':float(y[ni]-yh[ni]),'frozen_N12_NRMSE':float(ref['NRMSE']),'NRMSE_change_N24_minus_N12':float(np.linalg.norm(yh-y)/np.linalg.norm(y))-float(ref['NRMSE']),'frozen_N12_peak_relative_error':float(ref['peak_relative_error']),'identity':'fitted model fixed5-to8 map, not true modal terms'})
    tag=f'{op}__{case}__{story}__z{z:g}';traces[tag+'__t']=t;traces[tag+'__native']=y;traces[tag+'__prediction']=yh;traces[tag+'__terms']=terms[:,:,j]
 # Save both small operator blocks as soon as each is computed.
 cs('early-'+op+'-errors-12.csv',[q for q in metrics if q['operator']==op]);print('EARLY_'+op.upper()+'_TABLE '+datetime.now(timezone.utc).isoformat(),flush=True)
cs('prediction-errors-N24-24.csv',metrics);cs('fixed-output-coefficients-N24-96.csv',coeff);cs('prefix-coefficient-change-vs-N12-8.csv',coefchanges);js('models-small-N24.json',models)
print('ALL_N24_ERROR_TABLE_SAVED '+datetime.now(timezone.utc).isoformat(),flush=True)
for op in ['elastic','balance']:
 raw=np.array(models[f'N24_{op}_rc1e-10']['raw_output_coef']);n12=np.array(root_models[f'N12_{op}_rc1e-10']['raw_output_coef'])
 for case in cases:
  for z in [.05,.08]:
   xx=allX[op][case,z]
   for j,story in enumerate(stories):
    y=data[case]['Y0' if z==.05 else 'Y3'][story];it=int(np.argmax(abs(y)))
    for start,end in [(0,3),(3,6),(6,9),(9,12),(0,6),(0,12)]:
     old=xx[:,start:end]@n12[start:end,j];new=xx[:,start:end]@raw[start:end,j];den=float(np.linalg.norm(old))
     groupchanges.append({'operator':op,'Case':case,'Story':story,'zeta':z,'group_modes':f'{start+1}to{end}','N12_group_RMS_kN':float(np.sqrt(np.mean(old*old))),'N24_group_RMS_kN':float(np.sqrt(np.mean(new*new))),'group_curve_relative_L2_change':float(np.linalg.norm(new-old)/den) if den else None,'native_peak_time_s':float(data[case]['t'][it]),'N12_group_signed_at_native_peak_kN':float(old[it]),'N24_group_signed_at_native_peak_kN':float(new[it]),'scope':'same frequency-ordered group of fitted terms, not uniquely identified true modal group'})
cs('common-prefix-group-curve-change-144.csv',groupchanges)
np.savez_compressed(L/'N24-two-operator-traces.npz',**traces)
for b in root_rules['source']:assert sha(Path(b['path']))==b['sha256']
assert len(metrics)==24 and len(coeff)==96 and len(groupchanges)==144
js('results.json',{'completed_utc':datetime.now(timezone.utc).isoformat(),'N':24,'variants':2,'prediction_rows':24,'rank_by_operator':{op:models[f'N24_{op}_rc1e-10']['rank'] for op in ['elastic','balance']},'max_terms_sum_prediction_error_kN':maxsum,'validation_rows':[q for q in metrics if q['evaluation']!='train5'],'coefficient_changes':coefchanges,'all_root_sources_unchanged':True,'N12_or_N6_refitted':False,'native8_refitted':False,'full_arrays_local_only':True,'identity':'fitted-model, numerical and modal-identifiability interpretation review pending'})
print(json.dumps({'rank':{op:models[f'N24_{op}_rc1e-10']['rank'] for op in ['elastic','balance']},'validation':[{k:q[k] for k in ['operator','Case','Story','evaluation','NRMSE','peak_relative_error','NRMSE_change_N24_minus_N12']} for q in metrics if q['evaluation']!='train5'],'coefficient_changes':coefchanges}))
