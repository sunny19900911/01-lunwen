import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,importlib.util
import numpy as np
O=Path(__file__).resolve().parent;R=O.parents[5];P=O.parent;D=R.parent/'W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016';B=D/'原生0数据缓存';L=O/'local-cache';L.mkdir(exist_ok=False);(L/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,d):
 with (O/n).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cs(n,rows):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
rules24=json.loads((P/'R001/input-rules-freeze.json').read_text(encoding='utf-8'));old24=json.loads((P/'R001/models-small-N24.json').read_text(encoding='utf-8'))['N24_elastic_rc1e-10'];old36=json.loads((P/'R002/models-small-N36.json').read_text(encoding='utf-8'))['N36_elastic_rc1e-10']
oldmetrics={24:read(P/'R001/prediction-errors-N24-24.csv'),36:read(P/'R002/prediction-errors-N36-24.csv')};oldmodels={24:old24,36:old36};tracepaths={24:P/'R001/local-cache/N24-two-operator-traces.npz',36:P/'R002/local-cache/N36-elastic-two-rcond-traces.npz'}
src=[Path(q['path']) for q in rules24['source']]+[B/'manifest.json',D/'response_cache_manifest.json',P/'R001/models-small-N24.json',P/'R002/models-small-N36.json',P/'R001/prediction-errors-N24-24.csv',P/'R002/prediction-errors-N36-24.csv',*tracepaths.values()]
src=list(dict.fromkeys(src));bindings=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in src]
for q in rules24['source']:assert sha(Path(q['path']))==q['sha256']
js('input-rules-freeze.json',{'start_observed_utc':'2026-10-30T13:03:10+00:00','deadline_utc':'2026-10-30T13:13:10+00:00','frozen_utc':datetime.now(timezone.utc).isoformat(),'inputs':bindings,'N':[24,36],'operator':'elastic','rcond':1e-10,'train_native5_only':['SHW3X','SHW4X'],'holdout5':'RH4X','native8_no_refit':True,'old_Story5_Story12_coefficients_predictions_metrics_reused':True,'new_outputs':['Story'+str(i) for i in range(1,13) if i not in [5,12]],'basis_reuse':'recover common stored unit basis from frozen per-mode term divided by its frozen coefficient, choosing larger absolute coefficient across original two floors; no signal fit or scaling estimation; reconstruct both old outputs to verify','new_fits':'one multioutput least squares per N, ten outputs only','groups':'1to12 and represented13plus (13to24 for N24,13to36 for N36); signed output terms, not energy shares','source_row_and_Time_preserved':True,'full_arrays_local_only':True,'code_sha256':sha(Path(__file__))})
hp=Path(next(q['path'] for q in rules24['source'] if q['path'].endswith('modal_linear.py')));spec=importlib.util.spec_from_file_location('allfloorhelper',hp);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
cases=['SHW3X','SHW4X','RH4X'];stories=['Story'+str(i) for i in range(1,13)];newstories=[s for s in stories if s not in ['Story5','Story12']];meta={.05:json.loads((B/'manifest.json').read_text(encoding='utf-8'))['tables']['Story Forces'],.08:json.loads((D/'response_cache_manifest.json').read_text(encoding='utf-8'))['tables']['Story Forces']}
native={};time={};sourceRows={}
for z,md in meta.items():
 cols=md.get('columns',md.get('value_columns'));path=(B if z==.05 else D)/md['cache'];keys={(g['keys']['Output Case'],g['keys']['Story'],g['keys']['Location']):k for k,g in md['groups'].items()}
 with np.load(path,allow_pickle=False) as zz:
  for case in cases:
   for s in stories:
    a=zz[keys[case,s,'Bottom']];t=a[:,cols.index('Time')]
    if case in time:assert np.array_equal(time[case],t)
    else:time[case]=t.copy()
    native[case,s,z]=a[:,cols.index('VX')].copy();sourceRows[case,s,z]=a[:,cols.index('SourceRow')].astype(int)
nativepairs=[]
for case in cases:
 for s in stories:
  a=native[case,s,.05];b=native[case,s,.08];i=int(np.argmax(abs(a)));j=int(np.argmax(abs(b)));nativepairs.append({'Case':case,'Story':s,'Location':'Bottom','Axis':'X','peak5_kN':float(abs(a[i])),'peak8_kN':float(abs(b[j])),'native_peak_decrease_percent':100*(1-float(abs(b[j])/abs(a[i]))),'peak5_time_s':float(time[case][i]),'peak8_time_s':float(time[case][j]),'V8_at_5peak_kN':float(b[i]),'V5_at_8peak_kN':float(a[j]),'source_row5':int(sourceRows[case,s,.05][i]),'source_row8':int(sourceRows[case,s,.08][j])})
cs('native-all12-peak-change-36.csv',nativepairs)
preds={};lows={};highs={};models={};metrics=[];coefrows=[];basischecks=[];traces={}
for N in [24,36]:
 om=oldmodels[N];oldraw=np.array(om['raw_output_coef']);X={};oldtraces={}
 with np.load(tracepaths[N],allow_pickle=False) as zz:
  for case in cases:
   for z in [.05,.08]:
    prefix=lambda s:f'elastic__{case}__{s}__z{z:g}' if N==24 else f'N36_elastic_rc1e-10__{case}__{s}__z{z:g}'
    oldtraces[case,z]=[(zz[prefix(s)+'__prediction'].copy(),zz[prefix(s)+'__terms'].copy()) for s in ['Story5','Story12']]
    terms=np.stack([q[1] for q in oldtraces[case,z]],axis=2);pick=np.argmax(abs(oldraw),axis=1);den=oldraw[np.arange(N),pick];assert np.all(den!=0)
    xx=terms[:,np.arange(N),pick]/den[None,:];X[case,z]=xx
    for j,s in enumerate(['Story5','Story12']):
     err=float(np.max(abs(xx@oldraw[:,j]-oldtraces[case,z][j][0])));assert err<1e-6
     assert np.array_equal(zz[prefix(s)+'__native'],native[case,s,z]) and np.array_equal(zz[prefix(s)+'__t'],time[case]);basischecks.append({'N':N,'Case':case,'zeta':z,'Story':s,'max_old_prediction_reconstruction_error_kN':err})
 Xt=np.vstack([X[c,.05] for c in cases[:2]]);Yt=np.vstack([np.column_stack([native[c,s,.05] for s in newstories]) for c in cases[:2]]);fit=helper.fit_map(Xt,Yt,rcond=1e-10);rawnew=np.zeros((N,10));rawnew[fit['active']]=fit['coef']/fit['scale'][fit['active'],None];assert fit['rank']==om['rank']
 raw=np.zeros((N,12))
 for j,s in enumerate(stories):raw[:,j]=oldraw[:,['Story5','Story12'].index(s)] if s in ['Story5','Story12'] else rawnew[:,newstories.index(s)]
 models[f'N{N}']={'rank':fit['rank'],'rcond':1e-10,'new_fitted_outputs':newstories,'reused_frozen_outputs':['Story5','Story12'],'singular_values':fit['singular_values'].tolist(),'training_scale':fit['scale'].tolist(),'active':fit['active'].tolist(),'Story_order':stories,'raw_coef_all12':raw.tolist()}
 for j,s in enumerate(stories):
  for mode in range(N):coefrows.append({'N':N,'Story':s,'Mode':mode+1,'raw_coefficient':float(raw[mode,j]),'origin':'frozen_prior_fit' if s in ['Story5','Story12'] else 'new10_output_fit_native5_only'})
 for case in cases:
  for z in [.05,.08]:
   prednew=helper.predict_map(fit,X[case,z]);xx=X[case,z]
   for j,s in enumerate(stories):
    if s in ['Story5','Story12']:
     oldpred,terms=oldtraces[case,z][['Story5','Story12'].index(s)];yp=oldpred;lo=terms[:,:12].sum(1);hi=terms[:,12:].sum(1);old=next(q for q in oldmetrics[N] if q.get('operator','elastic')=='elastic' and float(q['rcond'])==1e-10 and q['Case']==case and q['Story']==s and float(q['zeta'])==z)
    else:
     yp=prednew[:,newstories.index(s)];lo=xx[:,:12]@raw[:12,j];hi=xx[:,12:]@raw[12:,j];old=None
    assert np.max(abs(lo+hi-yp))<1e-6;y=native[case,s,z];ni=int(np.argmax(abs(y)));pi=int(np.argmax(abs(yp)));nr=float(np.linalg.norm(yp-y)/np.linalg.norm(y));pk=float(np.max(abs(yp))/np.max(abs(y))-1)
    if old:assert abs(nr-float(old['NRMSE']))<1e-12 and abs(pk-float(old['peak_relative_error']))<1e-12
    pair=next(q for q in nativepairs if q['Case']==case and q['Story']==s)
    metrics.append({'N':N,'Story':s,'Case':case,'zeta':z,'operator':'elastic','rcond':1e-10,'rank':fit['rank'],'evaluation':'train5' if z==.05 and case in cases[:2] else ('heldout5' if z==.05 else 'fixed_map8'),'fit_origin':'frozen_Story5_12_reused' if old else 'new10_outputs','NRMSE':nr,'native_peak_kN':float(np.max(abs(y))),'predicted_peak_kN':float(np.max(abs(yp))),'peak_relative_error':pk,'native_peak_time_s':float(time[case][ni]),'predicted_peak_time_s':float(time[case][pi]),'native_peak_SourceRow':int(sourceRows[case,s,z][ni]),'native_peak_decrease5to8_percent':pair['native_peak_decrease_percent'],'scope':'signed Bottom VX fitted-model, not true modal decomposition'})
    key=(N,case,s,z);preds[key]=yp;lows[key]=lo;highs[key]=hi;tag=f'N{N}__{case}__{s}__z{z:g}';traces[tag+'__t']=time[case];traces[tag+'__native']=y;traces[tag+'__prediction']=yp;traces[tag+'__low1to12']=lo;traces[tag+'__represented_high13plus']=hi;traces[tag+'__residual']=y-yp
 cs(f'early-N{N}-all12-errors-72.csv',[q for q in metrics if q['N']==N]);print(f'EARLY_N{N}_72_ROWS '+datetime.now(timezone.utc).isoformat(),flush=True)
cs('all12-prediction-errors-144.csv',metrics);cs('all12-fixed-coefficients-720.csv',coefrows);js('all12-models-small.json',models);cs('basis-recovery-checks-24.csv',basischecks)
print('ALL12_144_ERROR_ROWS_SAVED '+datetime.now(timezone.utc).isoformat(),flush=True)
changes=[];anchors=[];summary=[]
for s in stories:
 for N in [24,36]:
  rr=[q for q in metrics if q['N']==N and q['Story']==s and q['evaluation']=='fixed_map8'];hh=next(q for q in metrics if q['N']==N and q['Story']==s and q['evaluation']=='heldout5')
  summary.append({'N':N,'Story':s,'heldout5_NRMSE':hh['NRMSE'],'fixed8_NRMSE_min':min(q['NRMSE'] for q in rr),'fixed8_NRMSE_max':max(q['NRMSE'] for q in rr),'fixed8_peak_error_min':min(q['peak_relative_error'] for q in rr),'fixed8_peak_error_max':max(q['peak_relative_error'] for q in rr)})
 for case in cases:
  for z in [.05,.08]:
   y=native[case,s,z];den=float(np.linalg.norm(y))
   for label,arr in [('low1to12',lows),('represented_high13plus',highs)]:
    a=arr[24,case,s,z];b=arr[36,case,s,z];own=float(np.linalg.norm(a));changes.append({'Story':s,'Case':case,'zeta':z,'group':label,'N24_group_RMS_kN':float(np.sqrt(np.mean(a*a))),'N36_group_RMS_kN':float(np.sqrt(np.mean(b*b))),'difference_RMS_kN':float(np.sqrt(np.mean((b-a)**2))),'difference_L2_over_native_L2':float(np.linalg.norm(b-a)/den),'difference_L2_over_N24_group_L2':float(np.linalg.norm(b-a)/own) if own else None,'N24_last_mode':24,'N36_last_mode':36,'scope':'represented fitted high blocks have different upper truncation; no energy-share meaning'})
   for N in [24,36]:
    yp=preds[N,case,s,z];lo=lows[N,case,s,z];hi=highs[N,case,s,z]
    for label,it in [('native_peak',int(np.argmax(abs(y)))),('predicted_peak',int(np.argmax(abs(yp))))]:
     absolute=float(abs(lo[it])+abs(hi[it]));anchors.append({'N':N,'Story':s,'Case':case,'zeta':z,'anchor':label,'time_s':float(time[case][it]),'native_kN':float(y[it]),'low1to12_kN':float(lo[it]),'represented_high13plus_kN':float(hi[it]),'prediction_kN':float(yp[it]),'residual_native_minus_prediction_kN':float(y[it]-yp[it]),'two_reference_group_cancellation':1-abs(float(lo[it]+hi[it]))/absolute if absolute!=0 else None,'scope':'same-time signed fitted output partition plus residual, not energy or true modal force shares'})
cs('all12-validation-summary-24.csv',summary);cs('all12-low-high-N24-to-N36-144.csv',changes);cs('all12-same-time-low-high-residual-288.csv',anchors)
np.savez_compressed(L/'all12-low-high-reference-traces.npz',**traces)
for path,b in zip(src,bindings):assert sha(path)==b['sha256']
js('results.json',{'completed_utc':datetime.now(timezone.utc).isoformat(),'counts':{'error_rows':144,'native_pair_rows':36,'validation_summary':24,'group_curve_changes':144,'same_time_anchors':288,'coefficient_rows':720},'new_fits':2,'new_outputs_per_fit':10,'old_Story5_12_fits_reused':True,'old_Story5_12_metrics_reproduced_without_refit':True,'basis_recovery_max_error_kN':max(q['max_old_prediction_reconstruction_error_kN'] for q in basischecks),'rank':{k:q['rank'] for k,q in models.items()},'all_sources_unchanged':True,'native8_no_refit':True,'all_arrays_local_only':True})
print(json.dumps({'error_rows':144,'new_fits':2,'new_outputs_each':10,'ranks':{k:q['rank'] for k,q in models.items()},'summary':summary}))
