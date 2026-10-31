import os
os.environ['OPENBLAS_NUM_THREADS']='2'
os.environ['OMP_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np
O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130';SRC=S/'roles/role4/R010'
START=datetime.fromisoformat('2026-10-31T12:58:35+08:00');DEADLINE=START+timedelta(minutes=12)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate():
    if now()>=DEADLINE:raise RuntimeError('R009 deadline')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def jsdefault(x):
    if isinstance(x,np.generic):return x.item()
    raise TypeError(type(x).__name__)
def save(n,x):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2,default=jsdefault);f.write('\n')
def table(n,x):
    with (O/n).open('x',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(x[0]),lineterminator='\n');wr.writeheader();wr.writerows(x)
def group(meta,tn,case,story,di=None):
    found=[]
    for gid,g in meta['tables'][tn]['groups'].items():
        k=g['keys']
        if k.get('Output Case')!=case or k.get('Story')!=story:continue
        if 'Case Type' in k and k['Case Type']!='NonModHist':continue
        if di is not None and k.get('Diaphragm')!=di:continue
        if di is None and k.get('Location')!='Bottom':continue
        found.append(gid)
    assert len(found)==1,(tn,case,story,di,found)
    return found[0]
def metric(t,y,p,sr,absolute=False):
    i=int(np.argmax(abs(y)));j=int(np.argmax(abs(p)));a=float(abs(y[i]));b=float(abs(p[j]))
    x={'native_absolute_peak':a,'predicted_absolute_peak':b,'peak_relative_error':b/a-1,'native_peak_time_s':float(t[i]),'predicted_peak_time_s':float(t[j]),'peak_time_shift_s':float(t[j]-t[i]),'native_value_at_native_peak':float(y[i]),'prediction_at_native_peak':float(p[i]),'native_value_at_prediction_peak':float(y[j]),'prediction_at_prediction_peak':float(p[j]),'native_peak_SourceRow':int(sr[i])}
    x['absolute_curve_NRMSE' if absolute else 'NRMSE']=float(np.linalg.norm(abs(p)-abs(y))/np.linalg.norm(y) if absolute else np.linalg.norm(p-y)/np.linalg.norm(y))
    return x
gate();mf=json.loads((SRC/'delivery-manifest.json').read_text(encoding='utf-8'))
for e in mf['outputs']+mf['inputs']+mf['new_local_only_arrays']:
    p=Path(e['path']) if 'path' in e else SRC/e['name'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256'],str(p)
smallp=Path(next(x['path'] for x in mf['inputs'] if x['path'].endswith('controlled_small_tables.json')))
small=json.loads(smallp.read_text(encoding='utf-8'))
own=S/'roles/role2/R003';oldmf=json.loads((own/'manifest.json').read_text(encoding='utf-8'))
massp=own/'independent-identification-before-comparison-36.csv';entry=next(e for e in oldmf['files'] if e['name']==massp.name);assert sha(massp)==entry['sha256']
massrows=rows(massp);keys=sorted({(int(x['Story'].removeprefix('Story')),x['Diaphragm']) for x in massrows});index={('Story'+str(st),di):i for i,(st,di) in enumerate(keys)}
my=np.zeros(18)
for x in massrows:
    if x['direction']=='Y':my[index[x['Story'],x['Diaphragm']]]=float(x['identified_mass_kg'])
cm_entry=json.loads((own/'early-independent-results.json').read_text(encoding='utf-8'))['sources_used'][1];cmp=Path(cm_entry['path']);assert sha(cmp)==cm_entry['sha256']
px=np.full((18,300),np.nan);py=px.copy()
for x in rows(cmp):
    assert x['CaseType']=='LinModRitz';i=index[x['Story'],x['Diaphragm']];j=int(x['Mode'])-1
    px[i,j]=float(x['UX_native_mm'])*.001;py[i,j]=float(x['UY_native_mm'])*.001
pf=small['Modal Participation Factors'];ph=pf[1][1];assert pf[2][1][ph.index('ModalMass')]=='kN-m-s²'
mrmap={int(x[ph.index('Mode')]):float(x[ph.index('ModalMass')])*1000 for _,x in pf[3:]}
period=small['Modal Periods And Frequencies'];wh=period[1][1];wm={int(x[wh.index('Mode')]):float(x[wh.index('CircFreq')]) for _,x in period[3:]}
w=np.array([wm[i] for i in range(1,301)]);mr=np.array([mrmap[i] for i in range(1,301)])
gamma=(my@py)/mr;B=np.array([np.sum(my[[st>=cut for st,_ in keys],None]*py[[st>=cut for st,_ in keys]],axis=0)*gamma for cut in range(1,13)])
admissionp=Path(next(x['path'] for x in mf['inputs'] if x['path'].endswith('Y-input-admission-and-X-reuse-evidence-3.csv')));admission={x['Y_case']:x for x in rows(admissionp)}
assert len(admission)==3
base=Path(next(x['path'] for x in mf['inputs'] if x['path'].endswith('response_cache_manifest.json'))).parent
meta={.05:json.loads((base/'原生0数据缓存/manifest.json').read_text(encoding='utf-8')),.08:json.loads((base/'response_cache_manifest.json').read_text(encoding='utf-8'))};nb={.05:base/'原生0数据缓存',.08:base}
cmout=[];sfout=[];pairings=[];states={};coefferr={'Gamma_Y':0.,'B_Y':0.};prederr={'CM_m':0.,'E_kN':0.,'Q_kN':0.};trutherr=0.
for case in ('SHW3Y','SHW4Y','RH4Y'):
    a=admission[case];xcase=a['reuse_scalar_X_input_from'];assert a['input_scale_factor_change']=='1.0' and a['InitialCondition']=='Unstressed' and a['prior5_8_input_all_samples_equal']=='True' and a['independent_new_earthquake_record']=='False'
    for zeta in (.05,.08):
        gate();ref=next(x for x in mf['source_unit_kernel_references'] if x['Y_case']==case and x['zeta']==zeta);assert ref['source_scalar_case']==xcase and not ref['source_s_sdot_omega_duplicated']
        assert sha(Path(ref['unit_kernel_path']))==ref['unit_kernel_sha256']
        with np.load(ref['unit_kernel_path'],allow_pickle=False) as u,np.load(ref['new_Y_output_path'],allow_pickle=False) as z:
            assert all(k not in z.files for k in ('s_unitGamma','sdot_unitGamma','omega'))
            t=u['t'];s=u['s_unitGamma'];v=u['sdot_unitGamma'];assert np.array_equal(t,z['t']) and np.array_equal(w,u['omega']) and len(t)==int(a['n'])
            assert np.all(s[0]==0) and np.all(v[0]==0) and np.allclose(np.diff(t),.02,atol=1e-12,rtol=0)
            for name,ownvalue in [('Gamma_Y',gamma),('B_Y',B)]:
                coefferr[name]=max(coefferr[name],float(np.max(abs(z[name]-ownvalue))));assert np.allclose(z[name],ownvalue,rtol=1e-12,atol=1e-9)
            ux=s@(px*gamma).T;uy=s@(py*gamma).T;g=s*w**2;E=g@B.T/1000;Q=(g+v*(2*zeta*w))@B.T/1000
            for name,pred,key in [('CM_predicted_UX_m',ux,'CM_m'),('CM_predicted_UY_m',uy,'CM_m'),('shear_elastic_inertia_predicted_kN',E,'E_kN'),('shear_classical_balance_predicted_kN',Q,'Q_kN')]:
                er=float(np.max(abs(pred-z[name])));prederr[key]=max(prederr[key],er);assert er<(1e-12 if key=='CM_m' else 1e-6)
            # Single-mode peaks for UPC, without producing any mode-by-story-time tensors.
            U=np.sum(np.max(abs(g),axis=0)[None,:]*abs(B)/1000,axis=1)
            P=np.max(abs(E),axis=0);PQ=np.max(abs(Q),axis=0)
            tc=meta[zeta]['tables']['Diaphragm CM Displacements'];tf=meta[zeta]['tables']['Story Forces'];cc=tc.get('columns',tc.get('value_columns'));fc=tf.get('columns',tf.get('value_columns'))
            assert fc.index('VY')!=fc.index('VX')
            nativeP=[];nativeT=[]
            with np.load(nb[zeta]/tc['cache'],allow_pickle=False) as nc,np.load(nb[zeta]/tf['cache'],allow_pickle=False) as nf:
                for j,(story,di) in enumerate(keys):
                    story='Story'+str(story);gid=group(meta[zeta],'Diaphragm CM Displacements',case,story,di);arr=nc[gid];assert np.array_equal(arr[:,cc.index('Time')],t)
                    truth=arr[:,[cc.index('UX'),cc.index('UY')]]*.001;trutherr=max(trutherr,float(np.max(abs(truth-z['CM_native_'+story+'_'+di+'_UX_UY_m']))))
                    for k,(axis,pred) in enumerate([('UX',ux),('UY',uy)]):cmout.append({'Case':case,'scalar_kernel_case':xcase,'zeta':zeta,'Story':story,'Diaphragm':di,'Axis':axis,**metric(t,truth[:,k],pred[:,j],arr[:,cc.index('SourceRow')])})
                    pairings.append({'Case':case,'source_scalar_case':xcase,'zeta':zeta,'table':'Diaphragm CM Displacements','Story':story,'Diaphragm_or_Location':di,'group_id':gid,'native_n':len(arr),'saved_n':len(t),'time_vectors_exact':True,'source_row_first':int(arr[0,cc.index('SourceRow')]),'source_row_last':int(arr[-1,cc.index('SourceRow')])})
                for j in range(12):
                    story='Story'+str(j+1);gid=group(meta[zeta],'Story Forces',case,story);arr=nf[gid];assert np.array_equal(arr[:,fc.index('Time')],t)
                    truth=arr[:,fc.index('VY')];trutherr=max(trutherr,float(np.max(abs(truth-z['shear_native_'+story+'_VY_kN']))));nativeP.append(float(max(abs(truth))));nativeT.append(float(t[np.argmax(abs(truth))]))
                    for label,pred in [('elastic_inertia',E),('classical_balance',Q)]:sfout.append({'Case':case,'scalar_kernel_case':xcase,'zeta':zeta,'Story':story,'operator':label,**metric(t,truth,pred[:,j],arr[:,fc.index('SourceRow')],True)})
                    pairings.append({'Case':case,'source_scalar_case':xcase,'zeta':zeta,'table':'Story Forces','Story':story,'Diaphragm_or_Location':'Bottom','group_id':gid,'native_n':len(arr),'saved_n':len(t),'time_vectors_exact':True,'source_row_first':int(arr[0,fc.index('SourceRow')]),'source_row_last':int(arr[-1,fc.index('SourceRow')])})
            states[case,zeta]={'U':U,'P':P,'C':P/U,'PQ':PQ,'nativeP':np.array(nativeP),'nativeT':np.array(nativeT),'ET':t[np.argmax(abs(E),axis=0)],'QT':t[np.argmax(abs(Q),axis=0)]}
assert len(cmout)==216 and len(sfout)==144 and len(pairings)==180 and trutherr==0
table('independent-Y-CM-metrics-216.csv',cmout);table('independent-Y-VY-absolute-metrics-144.csv',sfout);table('independent-Y-time-source-pairings-180.csv',pairings)
paired=[];upcout=[]
for case in ('SHW3Y','SHW4Y','RH4Y'):
    a=states[case,.05];b=states[case,.08]
    for j in range(12):
        dn=100*(1-b['nativeP'][j]/a['nativeP'][j]);de=100*(1-b['P'][j]/a['P'][j]);dq=100*(1-b['PQ'][j]/a['PQ'][j]);ru=b['U'][j]/a['U'][j];rc=b['C'][j]/a['C'][j];rp=b['P'][j]/a['P'][j]
        paired.append({'Case':case,'Story':'Story'+str(j+1),'native_peak5_VY_kN':float(a['nativeP'][j]),'native_peak8_VY_kN':float(b['nativeP'][j]),'E_peak5_kN':float(a['P'][j]),'E_peak8_kN':float(b['P'][j]),'Q_peak5_kN':float(a['PQ'][j]),'Q_peak8_kN':float(b['PQ'][j]),'native_peak_decrease_percent':float(dn),'E_reference_peak_decrease_percent':float(de),'Q_reference_peak_decrease_percent':float(dq),'E_minus_native_decrease_pp':float(de-dn),'Q_minus_native_decrease_pp':float(dq-dn),'native5_peak_s':float(a['nativeT'][j]),'native8_peak_s':float(b['nativeT'][j]),'E5_peak_s':float(a['ET'][j]),'E8_peak_s':float(b['ET'][j]),'Q5_peak_s':float(a['QT'][j]),'Q8_peak_s':float(b['QT'][j])})
        upcout.append({'Case':case,'Story':'Story'+str(j+1),'U5_kN':float(a['U'][j]),'U8_kN':float(b['U'][j]),'P5_kN':float(a['P'][j]),'P8_kN':float(b['P'][j]),'C5':float(a['C'][j]),'C8':float(b['C'][j]),'U8_over_U5':float(ru),'C8_over_C5':float(rc),'P8_over_P5':float(rp),'ratio_identity_error':float(rp-ru*rc)})
table('independent-Y-peak-decrease-36.csv',paired);table('independent-Y-E-UPC-36.csv',upcout)
errs={};checks=0;failures=[]
for ownrows,targetfile,key in [(cmout,'Y-CM-direct-forward-errors-216.csv',('Case','zeta','Story','Diaphragm','Axis')),(sfout,'Y-VY-two-operator-absolute-diagnostics-144.csv',('Case','zeta','Story','operator')),(paired,'Y-all12-threewaves-native-E-Q-peak-decrease-36.csv',('Case','Story')),(upcout,'Y-all12-threewaves-E-UPC-36.csv',('Case','Story'))]:
    target={tuple(float(x[k]) if k=='zeta' else x[k] for k in key):x for x in rows(SRC/targetfile)}
    for x in ownrows:
        ref=target[tuple(x[k] for k in key)]
        for k,v in x.items():
            if k in key or k=='scalar_kernel_case':continue
            er=abs(v-float(ref[k]));errs[k]=max(errs.get(k,0.),er);checks+=1
            if er>1e-8*max(1,abs(float(ref[k]))):failures.append({'key':str(tuple(x[k] for k in key)),'field':k,'error':er})
pt={(x['Case'],float(x['zeta']),x['table'],x['Story'],x['Diaphragm_or_Location']):x for x in rows(SRC/'Y-native-exact-time-pairing-180.csv')}
for x in pairings:
    ref=pt[x['Case'],x['zeta'],x['table'],x['Story'],x['Diaphragm_or_Location']]
    assert x['group_id']==ref['group_id'] and x['native_n']==int(ref['native_n']) and x['saved_n']==int(ref['saved_n']) and ref['time_vectors_exact']=='True'
e=[x for x in sfout if x['operator']=='elastic_inertia'];q=[x for x in sfout if x['operator']=='classical_balance']
save('key-results.json',{'completed':now().isoformat(),'CM_rows':216,'VY_rows':144,'exact_time_groups':180,'paired_peak_decrease_rows':36,'E_UPC_rows':36,'numeric_checks':checks,'must_count':len(failures),'failures':failures,'metric_max_abs_differences':errs,'coefficient_max_abs_differences':coefferr,'saved_output_rebuild_max_abs_differences':prederr,'native_cache_max_abs_difference':trutherr,'CM_signed_NRMSE_max':max(x['NRMSE'] for x in cmout),'CM_peak_error_max_abs':max(abs(x['peak_relative_error']) for x in cmout),'E_absolute_curve_NRMSE_max':max(x['absolute_curve_NRMSE'] for x in e),'E_peak_error_max_abs':max(abs(x['peak_relative_error']) for x in e),'Q_absolute_curve_NRMSE_max':max(x['absolute_curve_NRMSE'] for x in q),'Q_peak_error_max_abs':max(abs(x['peak_relative_error']) for x in q),'E_minus_native_decrease_max_abs_pp':max(abs(x['E_minus_native_decrease_pp']) for x in paired),'worst_E_native_decrease_pair':max(paired,key=lambda x:abs(x['E_minus_native_decrease_pp'])),'main_and_cross_CM_axes_retained':True,'actual_native_force_column':'VY, not VX','scalar_kernels_reused_without_copy_or_new_ODE':True,'independent_events':3,'new_RK4':False,'source_code_imported':False})
print(json.dumps(json.loads((O/'key-results.json').read_text(encoding='utf-8')),ensure_ascii=False))
