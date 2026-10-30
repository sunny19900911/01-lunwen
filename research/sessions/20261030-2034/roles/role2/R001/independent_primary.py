import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone,timedelta
import importlib.util,csv,json,hashlib
import numpy as np
O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261030-2034';ROOTOUT=S/'root-R001-low-order'
START=datetime.fromisoformat('2026-10-30T20:42:20+08:00')
now=lambda:datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
def gate():
 if now()>=START+timedelta(minutes=10):raise RuntimeError('task deadline')
def module(p,n):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def save(n,x):
 with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
gate();lp=R/'research/sessions/20261025-1337/roles/role6/R001/load_inputs.py';cfg,w,dat=module(lp,'audit_loader').load_inputs();w=w[:12];states=module(Path(cfg['modal_linear_py']),'audit_states').states
train=('SHW3X','SHW4X');stories=('Story5','Story12');X={}
for case in train+('RH4X',):
 gate();t=dat[case]['t'];assert np.allclose(np.diff(t),.02,rtol=0,atol=1e-12)
 for z in [.05,.08]:
  q,v,a=states(dat[case]['ag'],w,z,.02);X[case,z]=q*(w*w)
# Independent column L2 normalization; no call to helper fit_map/predict_map.
XT=np.concatenate([X[c,.05] for c in train]);YT=np.concatenate([np.stack([dat[c]['Y0'][s] for s in stories],axis=1) for c in train]);scale=np.linalg.norm(XT,axis=0);active=scale>scale.max()*1e-14
beta,_,rank,sval=np.linalg.lstsq(XT[:,active]/scale[active],YT,rcond=1e-10);raw=np.zeros((12,2));raw[active]=beta/scale[active,None]
coef_sha=hashlib.sha256(raw.tobytes()).hexdigest();rr=[]
for case,z in [('RH4X',.05),('SHW3X',.08),('SHW4X',.08),('RH4X',.08)]:
 pred=X[case,z]@raw
 for j,story in enumerate(stories):
  y=dat[case]['Y0' if z==.05 else 'Y3'][story];v=pred[:,j];ii=int(np.argmax(abs(y)));jj=int(np.argmax(abs(v)));pk=float(abs(y[ii]));pp=float(abs(v[jj]));rr.append({'Case':case,'Story':story,'zeta':z,'NRMSE':float(np.linalg.norm(v-y)/np.linalg.norm(y)),'native_peak_kN':pk,'predicted_peak_kN':pp,'peak_relative_error':pp/pk-1,'native_peak_time_s':float(dat[case]['t'][ii]),'predicted_peak_time_s':float(dat[case]['t'][jj]),'coef_sha256':coef_sha})
 assert hashlib.sha256(raw.tobytes()).hexdigest()==coef_sha
with (O/'independent-eight.csv').open('x',encoding='utf-8',newline='') as f:wri=csv.DictWriter(f,fieldnames=list(rr[0]),lineterminator='\n');wri.writeheader();wri.writerows(rr)
save('independent-fit-small.json',{'computed_at':now().isoformat(),'rank':int(rank),'singular_values':sval.tolist(),'raw_coefficients':raw.tolist(),'normalization':'independent training-column L2 norm, not helper.fit_map','train_families':list(train),'holdout':'RH4X','target_refits':0,'coefficient_sha256':coef_sha,'active':active.tolist(),'no_root_script_imported':True,'shared_component':'approved SDOF states kernel and frozen input loader only'})
# Compare only these8 rows (at least24 requested numbers), no repeat96 fitting.
with (ROOTOUT/'prediction-errors-96.csv').open(encoding='utf-8-sig',newline='') as f:target={(x['Case'],x['Story'],float(x['zeta'])):x for x in csv.DictReader(f) if x['variant']=='N12_elastic_rc1e-10'}
errs={};checks=0
for x in rr:
 y=target[x['Case'],x['Story'],x['zeta']]
 for key in ['NRMSE','native_peak_kN','predicted_peak_kN','peak_relative_error','native_peak_time_s','predicted_peak_time_s']:
  e=abs(x[key]-float(y[key]));errs[key]=max(errs.get(key,0.),e);assert e<1e-8*max(1.,abs(float(y[key]))),(key,x,y,e);checks+=1
# Independent native grid/output source-row check, retaining signed force.
unit_checks=[]
for d in cfg['output_groups']:
 with np.load(d['npz'],allow_pickle=False) as z:a=z[d['group_id']]
 c=d['group_keys']['Output Case'];st=d['group_keys']['Story'];state=d['state'];assert d['group_keys'].get('Location','Bottom')=='Bottom';assert np.array_equal(a[:,d['time_column']],dat[c]['t']);assert np.array_equal(a[:,d['signed_VX_column']],dat[c]['Y'+state][st]);unit_checks.append({'Case':c,'Story':st,'state':state,'grid_exact':True,'signed_VX_exact':True,'group':d['group_keys'],'field_metadata':{k:v for k,v in d.items() if 'unit' in k.lower() or k in ['columns','headers']}})
rules=json.loads((ROOTOUT/'input-rules-freeze.json').read_text(encoding='utf-8'));verified=[]
for x in rules['source']:
 data=Path(x['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==x['sha256'];verified.append({'path':x['path'],'sha256':x['sha256']})
save('checks.json',{'completed':now().isoformat(),'numeric_checks':checks,'must_count':0,'max_abs_difference':errs,'native_groups_checked':unit_checks,'sources_verified':verified,'scope':'8 primary rows only; no other7config refit; fitted reference accuracy not unique physical modal identification'})
print(json.dumps({'completed':now().isoformat(),'checks':checks,'max_abs_difference':errs,'eight':rr,'native_groups':len(unit_checks),'source_hashes':len(verified)},ensure_ascii=False))
