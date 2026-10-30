import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime, timezone, timedelta
import csv, hashlib, importlib.util, json, traceback
import numpy as np

O=Path(__file__).parent; R=O.parents[5]
S=R/'research/sessions/20261030-2034'; SOURCE=S/'roles/role4/R003'
START=datetime.fromisoformat('2026-10-30T21:10:59+08:00')
DEADLINE=START+timedelta(minutes=10)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def save(name,value):
    with (O/name).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n')
def gate(stage):
    if now()>=DEADLINE: raise RuntimeError('deadline at '+stage)
def loadmod(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def main():
    gate('start')
    manifest=json.loads((SOURCE/'delivery-manifest.json').read_text(encoding='utf-8'))
    for e in manifest['files']:
        b=(SOURCE/e['name']).read_bytes()
        assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256'],e['name']
    save('guard.json',{'started':START.isoformat(),'deadline':DEADLINE.isoformat(),
        'manifest_verified_at':now().isoformat(),'source_frozen':manifest['frozen_Asia_Shanghai'],
        'verified_files':len(manifest['files']), 'science_started_after_manifest_check':True,
        'precheck_reads':'metadata, README and CSV header inspected before hash check; no calculation before verification',
        'source_scripts_imported':False,'target_refits':0})
    rules=json.loads((SOURCE/'input-rules-freeze.json').read_text(encoding='utf-8'))
    verified=[]
    for e in rules['inputs']:
        gate('source hashes'); b=Path(e['path']).read_bytes()
        assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256'],e['path']
        verified.append({'path':e['path'],'sha256':e['sha256']})
    cfg,w,dat=loadmod(R/'research/sessions/20261025-1337/roles/role6/R001/load_inputs.py','old_loader').load_inputs()
    states=loadmod(Path(cfg['modal_linear_py']),'state_kernel').states; w=w[:36]
    stories=tuple('Story'+str(i) for i in range(1,13)); cases=('SHW3X','SHW4X','RH4X')
    train=cases[:2]; native={}; locators=[]
    # Select exact groups independently from the two native small-cache manifests.
    base=Path(next(e['path'] for e in rules['inputs'] if e['path'].endswith('response_cache_manifest.json'))).parent
    for state,mp in [('0',base/'原生0数据缓存/manifest.json'),('3',base/'response_cache_manifest.json')]:
        meta=json.loads(mp.read_text(encoding='utf-8'))['tables']['Story Forces']
        columns=meta.get('value_columns',meta.get('columns'))
        assert columns==['Time','P','VX','VY','T','MX','MY','SourceRow']
        assert meta['units'][meta['headers'].index('VX')]=='kN'
        npz=mp.parent/meta['cache']
        with np.load(npz,allow_pickle=False) as z:
            for case in cases:
                for story in stories:
                    gate('native group load')
                    matches=[(gid,g) for gid,g in meta['groups'].items() if g['keys'].get('Story')==story and g['keys'].get('Location')=='Bottom' and g['keys'].get('Output Case')==case and (state!='0' or g['keys'].get('Case Type')=='NonModHist')]
                    assert len(matches)==1,(state,case,story,matches)
                    gid,g=matches[0]; a=z[gid].copy(); t=dat[case]['t']; sr=a[:,7]
                    assert a.shape==(len(t),8) and g['n']==len(t)
                    assert np.isfinite(a).all() and np.array_equal(a[:,0],t)
                    assert np.allclose(np.diff(t),.02,atol=1e-12,rtol=0)
                    assert np.array_equal(sr,np.rint(sr)) and len(np.unique(sr))==len(sr)
                    native[case,state,story]=a
                    locators.append({'state':state,'Case':case,'Story':story,'npz':str(npz),'group_id':gid,'keys':g['keys'],'n':len(t),'t0':float(t[0]),'t1':float(t[-1]),'SourceRow_first':int(sr[0]),'SourceRow_last':int(sr[-1]),'VX_unit':'kN','grid_exact':True,'SourceRow_unique_integer':True})
    save('native-group-checks-72.json',locators)
    X={}
    for c in cases:
        for zeta in (.05,.08):
            gate('states'); q,_,_=states(dat[c]['ag'],w,zeta,.02); X[c,zeta]=q*w**2
    XT=np.concatenate([X[c,.05] for c in train])
    YT=np.concatenate([np.column_stack([native[c,'0',s][:,2] for s in stories]) for c in train])
    scale=np.linalg.norm(XT,axis=0); assert np.all(scale>0)
    gate('one multioutput lstsq')
    beta,_,rank,sv=np.linalg.lstsq(XT/scale,YT,rcond=1e-10)
    raw=beta/scale[:,None]; coefsha=hashlib.sha256(raw.tobytes()).hexdigest(); out=[]
    assert rank==36
    for case,zeta in [('RH4X',.05),('SHW3X',.08),('SHW4X',.08),('RH4X',.08)]:
        gate('prediction'); pred=X[case,zeta]@raw; state='0' if zeta==.05 else '3'
        for j,story in enumerate(stories):
            a=native[case,state,story]; y=a[:,2]; p=pred[:,j]
            i=int(np.argmax(abs(y))); k=int(np.argmax(abs(p))); pk=float(abs(y[i])); pp=float(abs(p[k]))
            out.append({'N':36,'Story':story,'Case':case,'zeta':zeta,'NRMSE':float(np.linalg.norm(p-y)/np.linalg.norm(y)),'native_peak_kN':pk,'predicted_peak_kN':pp,'peak_relative_error':pp/pk-1,'native_peak_time_s':float(a[i,0]),'predicted_peak_time_s':float(a[k,0]),'native_peak_SourceRow':int(a[i,7]),'predicted_peak_SourceRow':int(a[k,7]),'coef_sha256':coefsha})
        assert hashlib.sha256(raw.tobytes()).hexdigest()==coefsha
    # Preserve all independent numbers before looking up the delivered metrics.
    with (O/'independent-validation-48.csv').open('x',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');wr.writeheader();wr.writerows(out)
    save('independent-fit-small.json',{'computed_at':now().isoformat(),'rank':int(rank),'condition':float(sv[0]/sv[-1]),'sigma_min_over_max':float(sv[-1]/sv[0]),'normalization':'training-column L2','train_cases':train,'train_zeta':.05,'holdout':'RH4X entire record','target_refits':0,'raw_coefficients':raw.tolist(),'coefficient_sha256':coefsha,'shared_components':'frozen input loader and approved SDOF states kernel only'})
    worst5=max((x for x in out if x['zeta']==.05),key=lambda x:x['NRMSE'])
    worst8=max((x for x in out if x['zeta']==.08),key=lambda x:x['NRMSE'])
    save('worst-first.json',{'completed':now().isoformat(),'worst_holdout5':worst5,'worst_target8':worst8})
    targetrows=rows(SOURCE/'all12-prediction-errors-144.csv')
    target={(x['Story'],x['Case'],float(x['zeta'])):x for x in targetrows if int(x['N'])==36}
    fields=['NRMSE','native_peak_kN','predicted_peak_kN','peak_relative_error','native_peak_time_s','predicted_peak_time_s']
    differences={k:0. for k in fields}; failures=[]; count=0
    for x in out:
        y=target[x['Story'],x['Case'],x['zeta']]
        for key in fields:
            e=abs(x[key]-float(y[key]));differences[key]=max(differences[key],e);count+=1
            if e>=1e-8*max(1.,abs(float(y[key]))):failures.append({'Story':x['Story'],'Case':x['Case'],'zeta':x['zeta'],'field':key,'independent':x[key],'delivered':float(y[key]),'abs_difference':e})
        assert x['native_peak_SourceRow']==int(y['native_peak_SourceRow'])
    # N24 and N36 summary arithmetic only; no N24 regression or stored-basis recovery.
    arithmetic=[]
    summary=rows(SOURCE/'all12-validation-summary-24.csv')
    save('summary-schema.json',{'columns':list(summary[0]),'first':summary[0]})
    for n in (24,36):
        for story in stories:
            rs=[x for x in targetrows if int(x['N'])==n and x['Story']==story]
            hold=next(float(x['NRMSE']) for x in rs if x['Case']=='RH4X' and float(x['zeta'])==.05)
            z8=[float(x['NRMSE']) for x in rs if float(x['zeta'])==.08]
            arithmetic.append({'N':n,'Story':story,'holdout5_NRMSE':hold,'target8_min_NRMSE':min(z8),'target8_max_NRMSE':max(z8)})
    save('derived-summary-arithmetic-24.json',arithmetic)
    save('checks.json',{'completed':now().isoformat(),'validation_rows':len(out),'numeric_checks':count,'numeric_must_count':len(failures),'failures':failures,'max_abs_difference':differences,'native_groups_checked':len(locators),'source_hashes_verified':verified,'native_peak_SourceRow_checks':48,'target_refits':0,'not_audited':'N24 regression; low/high decomposition and cancellation curves; original workbook SourceRow content (only frozen cache locator checked)'})
    print(json.dumps({'completed':now().isoformat(),'rows':len(out),'checks':count,'must':len(failures),'max_abs_difference':differences,'worst5':worst5,'worst8':worst8},ensure_ascii=False))

try:main()
except Exception as exc:
    save('failure-guard.json',{'at':now().isoformat(),'error':str(exc),'traceback':traceback.format_exc(),'status':'partial; use existing small outputs only'})
    raise
