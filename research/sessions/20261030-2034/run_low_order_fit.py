import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
import csv,json,hashlib,datetime,importlib.util
import numpy as np
S=Path(__file__).resolve().parent;R=S.parents[2];O=S/'root-R001-low-order';O.mkdir(exist_ok=False)
L=O/'local-cache';L.mkdir()
(L/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
def now():return datetime.datetime.now(datetime.timezone.utc)
assert now()<datetime.datetime.fromisoformat('2026-10-30T14:34:43+00:00')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,d):
 with (O/n).open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cs(n,rows):
 with (O/n).open('x',encoding='utf-8-sig',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def mod(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
loaderp=R/'research/sessions/20261025-1337/roles/role6/R001/load_inputs.py'
cfgp=loaderp.with_name('input-config.json');cfg=json.loads(cfgp.read_text(encoding='utf-8'))
helperp=Path(cfg['modal_linear_py']);helper=mod(helperp,'ml19')
inputs=sorted({cfgp,loaderp,helperp,Path(cfg['derived_npz']),Path(cfg['omega_source']['path'])}|{Path(q['npz'])for q in cfg['output_groups']},key=str)
source=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in inputs]
train=['SHW3X','SHW4X'];hold='RH4X';stories=['Story5','Story12'];cases=train+[hold]
rules={'time_utc':now().isoformat(),'primary':'N12_elastic_rc1e-10','N':[12,6],'rcond':[1e-10,1e-8],'operators':['elastic','balance'],'train_native5_only':train,'holdout_native5':hold,'target_native8_fixed_map_all':cases,'no_target_refit':True,'no_sign_gain_time_adjustment':True,'initial_q_v':0,'zeta':[.05,.08],'scope':'linear modal output reference fitting,not certified physical modal decomposition; all configurations retained, no operator selection on8results','case_identity':'SHW3 not alias SHW7','source':source,'script_sha256':sha(Path(__file__))}
js('input-rules-freeze.json',rules)
cfg,om,data=mod(loaderp,'ld19').load_inputs()
assert len(om)==300 and set(data)==set(cases)
sources={}
for q in cfg['output_groups']:
 with np.load(q['npz'],allow_pickle=False)as z:
  arr=z[q['group_id']];key=(q['group_keys']['Output Case'],q['group_keys']['Story'],q['state'])
  sources[key]=arr[:,-1].astype(int)
metrics=[];coefrows=[];modepeaks=[];anchors=[];groups=[];models={};traces={};primary_summaries=[]
started=now()
for N in [12,6]:
 w=om[:N];states={}
 for case in cases:
  t=data[case]['t'];ag=data[case]['ag'];assert np.allclose(np.diff(t),.02,rtol=0,atol=1e-12)
  for zeta in [.05,.08]:
   Q,V,_=helper.states(ag,w,zeta,.02);states[case,zeta]=(Q,V)
 for operator in ['elastic','balance']:
  X={}
  for (case,zeta),(Q,V)in states.items():X[case,zeta]=Q*w*w if operator=='elastic' else Q*w*w+V*(2*zeta*w)
  Xt=np.vstack([X[c,.05]for c in train]);Yt=np.vstack([np.column_stack([data[c]['Y0'][s]for s in stories])for c in train])
  for rc in [1e-10,1e-8]:
   vid=f'N{N}_{operator}_rc{rc:g}'
   m=helper.fit_map(Xt,Yt,rcond=rc);active=m['active'];raw=np.zeros((N,2));raw[active]=m['coef']/m['scale'][active,None]
   models[vid]={'N':N,'operator':operator,'rcond':rc,'rank':m['rank'],'singular_values':m['singular_values'].tolist(),'active':active.tolist(),'training_scale':m['scale'].tolist(),'raw_output_coef':raw.tolist()}
   for j,story in enumerate(stories):
    for ir in range(N):coefrows.append({'variant':vid,'Story':story,'Mode':ir+1,'omega_rad_s':float(w[ir]),'raw_signed_output_coefficient':float(raw[ir,j]),'active':bool(active[ir]),'identity':'fitted fixed output map coefficient,not certified modal shear coefficient'})
   for case in cases:
    for zeta,ys in [(.05,'Y0'),(.08,'Y3')]:
     A=X[case,zeta];pred=helper.predict_map(m,A);terms=A[:,:,None]*raw[None,:,:]
     assert float(np.max(abs(terms.sum(1)-pred)))<1e-6
     for j,story in enumerate(stories):
      t=data[case]['t'];native=data[case][ys][story];yh=pred[:,j];den=float(np.linalg.norm(native));assert den>0
      ni=int(np.argmax(abs(native)));pi=int(np.argmax(abs(yh)));npk=float(abs(native[ni]));ppk=float(abs(yh[pi]))
      row={'variant':vid,'N':N,'operator':operator,'rcond':rc,'rank':m['rank'],'Case':case,'Story':story,'zeta':zeta,'evaluation':'train5' if zeta==.05 and case in train else ('heldout5' if zeta==.05 else 'fixed_map8'),'NRMSE':float(np.linalg.norm(yh-native)/den),'native_peak_kN':npk,'predicted_peak_kN':ppk,'peak_relative_error':ppk/npk-1,'native_peak_time_s':float(t[ni]),'predicted_peak_time_s':float(t[pi]),'native_peak_SourceRow':int(sources[case,story,'0' if zeta==.05 else '3'][ni]),'pred_at_native_peak_kN':float(yh[ni]),'signed_residual_at_native_peak_kN':float(native[ni]-yh[ni]),'identity':'fitted-model prediction checked against native signed Bottom VX'}
      metrics.append(row)
      if vid==rules['primary']:primary_summaries.append(row)
      if vid==rules['primary']:
       v=terms[:,:,j];g=np.column_stack([v[:,start:min(start+3,N)].sum(1)for start in range(0,N,3)])
       for ir in range(N):
        idx=int(np.argmax(abs(v[:,ir])));modepeaks.append({'Case':case,'Story':story,'zeta':zeta,'Mode':ir+1,'own_abs_peak_kN':float(abs(v[idx,ir])),'signed_at_own_peak_kN':float(v[idx,ir]),'own_peak_time_s':float(t[idx]),'identity':'primary fitted reference term,not unique true single-mode response'})
       for anchor,i in [('native_peak',ni),('predicted_peak',pi)]:
        sv=float(v[i].sum());av=float(abs(v[i]).sum());gv=g[i]
        a={'Case':case,'Story':story,'zeta':zeta,'anchor':anchor,'time_s':float(t[i]),'native_kN':float(native[i]),'prediction_sum_kN':sv,'residual_native_minus_prediction_kN':float(native[i]-sv),'sum_abs_terms_kN':av,'chi_terms':None if av==0 else 1-abs(sv)/av,'identity':'reference terms at same time,not exact native decomposition'}
        a.update({f'mode{k+1}_kN':float(v[i,k])for k in range(N)});anchors.append(a)
        gabs=float(abs(gv).sum());groups.append({'Case':case,'Story':story,'zeta':zeta,'anchor':anchor,'time_s':float(t[i]),'g1_modes1to3_kN':float(gv[0]),'g2_modes4to6_kN':float(gv[1]),'g3_modes7to9_kN':float(gv[2]),'g4_modes10to12_kN':float(gv[3]),'sum_kN':float(gv.sum()),'chi_groups':None if gabs==0 else 1-abs(float(gv.sum()))/gabs,'identity':'fitted frequency-ordered mode groups,not independently identified physical coordinates'})
       tag=f'{case}__{story}__z{zeta:g}'
       traces[tag+'__t']=t;traces[tag+'__native']=native;traces[tag+'__prediction']=yh;traces[tag+'__terms']=v
cs('prediction-errors-96.csv',metrics);cs('fixed-output-coefficients.csv',coefrows);cs('primary-modal-reference-peaks.csv',modepeaks);cs('primary-critical-time-terms.csv',anchors);cs('primary-critical-time-groups.csv',groups)
assert len(metrics)==96 and len(models)==8
js('models-small.json',models)
stability=[]
for operator in ['elastic','balance']:
 for story,j in [('Story5',0),('Story12',1)]:
  a=np.array(models[f'N12_{operator}_rc1e-10']['raw_output_coef'])[:6,j];b=np.array(models[f'N6_{operator}_rc1e-10']['raw_output_coef'])[:,j]
  c=np.array(models[f'N12_{operator}_rc1e-08']['raw_output_coef'])[:,j];d=np.array(models[f'N12_{operator}_rc1e-10']['raw_output_coef'])[:,j]
  stability.append({'operator':operator,'Story':story,'first6_coef_N6_vs_N12_relative_L2':float(np.linalg.norm(a-b)/max(np.linalg.norm(a),1e-300)),'N12_rcond_change_relative_L2':float(np.linalg.norm(c-d)/max(np.linalg.norm(d),1e-300))})
cs('coefficient-stability.csv',stability)
np.savez_compressed(L/'primary-reference-traces.npz',**traces)
assert all(sha(Path(q['path']))==q['sha256']for q in source)
summary={'actual_started_utc':started.isoformat(),'completed_utc':now().isoformat(),'runtime_seconds':(now()-started).total_seconds(),'variants':8,'prediction_rows':96,'primary':rules['primary'],'primary_validation':[q for q in primary_summaries if q['evaluation']!='train5'],'coefficient_stability':stability,'all_sources_unchanged':True,'full_arrays_local_only':True,'identity':'fitted-model; independent numerical/physical interpretation audit pending'}
js('results.json',summary)
js('manifest.json',{'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(O.iterdir())if p.is_file()],'local_only_array':{'path':'local-cache/primary-reference-traces.npz','bytes':(L/'primary-reference-traces.npz').stat().st_size,'sha256':sha(L/'primary-reference-traces.npz')}})
print(json.dumps({'rows':len(metrics),'variants':8,'primary_validation':[{k:q[k]for k in ('Case','Story','evaluation','NRMSE','peak_relative_error')}for q in summary['primary_validation']],'stability':stability,'runtime_seconds':summary['runtime_seconds']},ensure_ascii=False))

