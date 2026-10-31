import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np
O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130';SRC=S/'roles/role4/R004'
START=datetime.fromisoformat('2026-10-31T12:18:14+08:00');DEADLINE=START+timedelta(minutes=12)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate():
    if now()>=DEADLINE:raise RuntimeError('R005 deadline')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(n,x):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def table(n,x):
    with (O/n).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(x[0]),lineterminator='\n');w.writeheader();w.writerows(x)
def find(meta,table_name,case,story,diaphragm=None):
    ts=meta['tables'][table_name];matches=[]
    for gid,g in ts['groups'].items():
        k=g['keys']
        if k.get('Output Case')!=case or k.get('Story')!=story:continue
        if 'Case Type' in k and k['Case Type']!='NonModHist':continue
        if diaphragm is not None and k.get('Diaphragm')!=diaphragm:continue
        if diaphragm is None and k.get('Location')!='Bottom':continue
        matches.append((gid,g))
    assert len(matches)==1,(table_name,case,story,diaphragm,len(matches))
    return matches[0]
def metrics(t,y,p,sourcerow,absolute_curve=False):
    i=int(np.argmax(abs(y)));j=int(np.argmax(abs(p)));py=float(abs(y[i]));pp=float(abs(p[j]))
    d={'native_absolute_peak':py,'predicted_absolute_peak':pp,'peak_relative_error':pp/py-1,'native_peak_time_s':float(t[i]),'predicted_peak_time_s':float(t[j]),'peak_time_shift_s':float(t[j]-t[i]),'native_value_at_native_peak':float(y[i]),'prediction_at_native_peak':float(p[i]),'native_value_at_prediction_peak':float(y[j]),'prediction_at_prediction_peak':float(p[j]),'native_peak_SourceRow':int(sourcerow[i]),'native_at_predicted_peak_SourceRow':int(sourcerow[j])}
    d['absolute_curve_NRMSE' if absolute_curve else 'NRMSE']=float(np.linalg.norm(abs(p)-abs(y))/np.linalg.norm(y) if absolute_curve else np.linalg.norm(p-y)/np.linalg.norm(y))
    return d
gate();mf=json.loads((SRC/'delivery-manifest-v002.json').read_text(encoding='utf-8'))
for entry in mf['outputs']+mf['inputs']+mf['local_only_arrays']:
    p=Path(entry['path']) if 'path' in entry else SRC/entry['name']
    assert p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256'],str(p)
entries=mf['inputs'];get=lambda suffix:Path(next(x['path'] for x in entries if x['path'].endswith(suffix)))
small=json.loads(get('controlled_small_tables.json').read_text(encoding='utf-8'))
cmshape=readcsv(get('CM-signed-all300-5400.csv'))
massp=S/'roles/role2/R003/independent-identification-before-comparison-36.csv';ownmf=json.loads((massp.parent/'manifest.json').read_text(encoding='utf-8'))
e=next(x for x in ownmf['files'] if x['name']==massp.name);assert sha(massp)==e['sha256']
massrows=readcsv(massp);keys=sorted({(int(x['Story'].removeprefix('Story')),x['Diaphragm']) for x in massrows});ki={('Story'+str(st),di):j for j,(st,di) in enumerate(keys)}
assert len(keys)==18
mx=np.zeros(18)
for x in massrows:
    if x['direction']=='X':mx[ki[x['Story'],x['Diaphragm']]]=float(x['identified_mass_kg'])
px=np.full((18,300),np.nan);py=px.copy()
for x in cmshape:
    assert x['CaseType']=='LinModRitz';i=ki[x['Story'],x['Diaphragm']];j=int(x['Mode'])-1
    px[i,j]=float(x['UX_native_mm'])*.001;py[i,j]=float(x['UY_native_mm'])*.001
pf=small['Modal Participation Factors'];ph=pf[1][1];pt=small['Modal Periods And Frequencies'];oh=pt[1][1]
massmodal={int(x[ph.index('Mode')]):float(x[ph.index('ModalMass')])*1000 for _,x in pf[3:]};wmap={int(x[oh.index('Mode')]):float(x[oh.index('CircFreq')]) for _,x in pt[3:]}
w=np.array([wmap[i] for i in range(1,301)]);mr=np.array([massmodal[i] for i in range(1,301)])
gamma=(mx@px)/mr;B=np.array([np.sum(mx[[st>=cut for st,_ in keys],None]*px[[st>=cut for st,_ in keys]],axis=0)*gamma for cut in range(1,13)])
cfg=json.loads(get('input-config.json').read_text(encoding='utf-8'));base=Path(cfg['data_root'])
metadata={.05:json.loads((base/'原生0数据缓存/manifest.json').read_text(encoding='utf-8')),.08:json.loads((base/'response_cache_manifest.json').read_text(encoding='utf-8'))}
nativebase={.05:base/'原生0数据缓存',.08:base}
truth_input=np.load(cfg['derived_npz'],allow_pickle=False)
cmrows=[];sfrows=[];group_rows=[];coeff_errors={'phi_X':0.,'phi_Y':0.,'Gamma_X':0.,'B_direct':0.};prediction_errors={'CM_m':0.,'elastic_kN':0.,'balance_kN':0.};native_cache_maxdiff=0.
for case in ('SHW3X','SHW4X','RH4X'):
    for zeta in (.05,.08):
        gate();entry=next(x for x in mf['local_only_arrays'] if ('actual300-'+case+'-z'+str(zeta)+'-') in x['path'])
        with np.load(entry['path'],allow_pickle=False) as z:
            t=z['t'];ag=z['ag'];q=z['s_unitGamma'];v=z['sdot_unitGamma']
            assert q.shape==v.shape==(len(t),300) and np.array_equal(z['omega'],w)
            assert np.array_equal(t,truth_input[cfg['cases'][case]['t_key']]) and np.array_equal(ag,truth_input[cfg['cases'][case]['ag_key']])
            assert np.allclose(np.diff(t),.02,rtol=0,atol=1e-12) and np.all(q[0]==0) and np.all(v[0]==0)
            for name,ind in [('phi_X',px),('phi_Y',py),('Gamma_X',gamma),('B_direct',B)]:
                er=float(np.max(abs(z[name]-ind)));coeff_errors[name]=max(coeff_errors[name],er)
                assert np.allclose(z[name],ind,rtol=1e-12,atol=1e-10)
            UX=q@(px*gamma).T;UY=q@(py*gamma).T
            E=(q*w**2)@B.T/1000;Q=(q*w**2+v*(2*zeta*w))@B.T/1000
            for name,pred,label in [('CM_predicted_UX_m',UX,'CM_m'),('CM_predicted_UY_m',UY,'CM_m'),('shear_elastic_inertia_predicted_kN',E,'elastic_kN'),('shear_classical_balance_predicted_kN',Q,'balance_kN')]:
                er=float(np.max(abs(z[name]-pred)));prediction_errors[label]=max(prediction_errors[label],er)
                assert er<(1e-12 if label=='CM_m' else 1e-6)
            meta=metadata[zeta];mb=nativebase[zeta]
            tc=meta['tables']['Diaphragm CM Displacements'];ts=meta['tables']['Story Forces']
            cc=tc.get('columns',tc.get('value_columns'));sc=ts.get('columns',ts.get('value_columns'))
            with np.load(mb/tc['cache'],allow_pickle=False) as nc,np.load(mb/ts['cache'],allow_pickle=False) as ns:
                for j,(story,di) in enumerate(keys):
                    story='Story'+str(story);gid,_=find(meta,'Diaphragm CM Displacements',case,story,di);a=nc[gid]
                    assert np.array_equal(a[:,cc.index('Time')],t)
                    native=a[:,[cc.index('UX'),cc.index('UY')]]*.001
                    native_cache_maxdiff=max(native_cache_maxdiff,float(np.max(abs(native-z['CM_native_'+story+'_'+di+'_UX_UY_m']))))
                    for k,(axis,pred) in enumerate([('UX',UX),('UY',UY)]):
                        cmrows.append({'Case':case,'zeta':zeta,'Story':story,'Diaphragm':di,'Axis':axis,**metrics(t,native[:,k],pred[:,j],a[:,cc.index('SourceRow')])})
                    group_rows.append({'Case':case,'zeta':zeta,'table':'CM','Story':story,'location':di,'group':gid,'time_exact':True})
                for j in range(12):
                    story='Story'+str(j+1);gid,_=find(meta,'Story Forces',case,story);a=ns[gid];assert np.array_equal(a[:,sc.index('Time')],t)
                    y=a[:,sc.index('VX')];native_cache_maxdiff=max(native_cache_maxdiff,float(np.max(abs(y-z['shear_native_'+story+'_kN']))))
                    for label,pred in [('elastic_inertia',E),('classical_balance',Q)]:
                        row={'Case':case,'zeta':zeta,'Story':story,'operator':label,**metrics(t,y,pred[:,j],a[:,sc.index('SourceRow')],True)}
                        row['unmapped_signed_NRMSE_diagnostic_only']=float(np.linalg.norm(pred[:,j]-y)/np.linalg.norm(y));sfrows.append(row)
                    group_rows.append({'Case':case,'zeta':zeta,'table':'SF','Story':story,'location':'Bottom','group':gid,'time_exact':True})
assert len(cmrows)==216 and len(sfrows)==144 and len(group_rows)==180 and native_cache_maxdiff==0
table('independent-CM-metrics-216.csv',cmrows);table('independent-shear-absolute-metrics-144.csv',sfrows);table('independent-native-groups-180.csv',group_rows)
save('independent-rebuild-checks.json',{'completed':now().isoformat(),'coefficient_max_abs_errors':coeff_errors,'saved_output_vs_independent_rebuild_max_abs_errors':prediction_errors,'native_saved_vs_source_cache_max_abs_difference':native_cache_maxdiff,'gamma_basis':'CM mass projection / ModalMass SI; no raw PF gain','no_output_fit':True})
targets=[(cmrows,readcsv(SRC/'CM-direct-forward-errors-216.csv'),('Case','zeta','Story','Diaphragm','Axis')),(sfrows,readcsv(SRC/'shear-two-operator-absolute-diagnostics-144.csv'),('Case','zeta','Story','operator'))]
metric_checks=0;errs={};failures=[]
for ind,tar,key in targets:
    lookup={tuple(float(x[k]) if k=='zeta' else x[k] for k in key):x for x in tar}
    for x in ind:
        ref=lookup[tuple(x[k] for k in key)]
        for k,val in x.items():
            if k in key or k=='unmapped_signed_NRMSE_diagnostic_only':continue
            er=abs(val-float(ref[k]));metric_checks+=1;errs[k]=max(errs.get(k,0.),er)
            if er>1e-8*max(1.,abs(float(ref[k]))):failures.append({'key':str(tuple(x[k] for k in key)),'field':k,'error':er})
        assert x['native_peak_SourceRow']==int(ref['native_peak_SourceRow']) and x['native_at_predicted_peak_SourceRow']==int(ref['native_at_predicted_peak_SourceRow'])
Erows=[x for x in sfrows if x['operator']=='elastic_inertia'];Qrows=[x for x in sfrows if x['operator']=='classical_balance']
save('metric-checks.json',{'completed':now().isoformat(),'CM_rows':216,'shear_rows':144,'numeric_checks':metric_checks,'must_count':len(failures),'failures':failures,'max_abs_metric_differences':errs,'CM_signed_NRMSE_max':max(x['NRMSE'] for x in cmrows),'CM_absolute_peak_relative_error_max_abs':max(abs(x['peak_relative_error']) for x in cmrows),'elastic_absolute_curve_NRMSE_max':max(x['absolute_curve_NRMSE'] for x in Erows),'elastic_peak_error_max_abs':max(abs(x['peak_relative_error']) for x in Erows),'balance_absolute_curve_NRMSE_max':max(x['absolute_curve_NRMSE'] for x in Qrows),'balance_peak_error_max_abs':max(abs(x['peak_relative_error']) for x in Qrows),'unmapped_elastic_signed_NRMSE_range':[min(x['unmapped_signed_NRMSE_diagnostic_only'] for x in Erows),max(x['unmapped_signed_NRMSE_diagnostic_only'] for x in Erows)],'scope':'CM signed metrics; shear absolute-curve diagnostics only; no eta sign mapping inferred'})
print(json.dumps(json.loads((O/'metric-checks.json').read_text(encoding='utf-8')),ensure_ascii=False))
