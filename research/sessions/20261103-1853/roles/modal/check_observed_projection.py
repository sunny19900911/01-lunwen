from pathlib import Path
import json,csv,hashlib,datetime,os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2')
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[4];W=R.parent/'W5-重燃双塔连体';L=H/'local-cache';L.mkdir(exist_ok=True)
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sources=[]
def bind(p):sources.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)});return p
P=R/'research/sessions/20261031-1130/roles/role4'
cm_path=bind(R/'research/sessions/20261022-1856/roles/role4/R001/local-cache/CM-signed-all300-5400.csv')
mass_path=bind(P/'R002/identified-masses-before-old-comparison-36.csv')
coeff_path=bind(P/'R004/actual300-frozen-forward-coefficients-300.csv')
cm=read(cm_path);mass=read(mass_path);coef=read(coeff_path)
keys=sorted({(x['Story'],x['Diaphragm'])for x in mass},key=lambda x:(int(x[0][5:]),x[1]))
assert len(keys)==18 and len(cm)==5400
cmmap={(int(x['Mode']),x['Story'],x['Diaphragm']):x for x in cm}
mm={(x['Axis'],x['Story'],x['Diaphragm']):float(x['identified_mass_kg'])for x in mass}
A=np.vstack([np.array([[float(cmmap[r,*k]['U'+ax+'_converted_m'])for r in range(1,301)]for k in keys])for ax in ['X','Y']])
m=np.array([mm[ax,*k]for ax in ['X','Y']for k in keys]);mr=np.array([float(x['mr_kg_m2'])for x in coef])
rows=np.array([1,12]);T=(A[:,rows].T*m[None,:])/mr[rows,None];G=T@A
assert G.shape==(2,300)
gram=[];couplings=[]
for ir,r in enumerate([2,13]):
    g=G[ir].copy();diag=float(g[r-1]);g[r-1]=0
    gram.append({'Mode':r,'observed_fraction_diagonal':diag,'cross_coupling_L2':float(np.linalg.norm(g)),'largest_abs_cross_coupling':float(np.max(abs(g))),'largest_coupled_Mode':int(np.argmax(abs(g)))+1,'scope':'mass observation projection, not full FE Gram or actual q'})
    for j in np.argsort(abs(g))[::-1][:10]:couplings.append({'target_Mode':r,'source_Mode':int(j)+1,'normalized_observation_Gram':float(g[j])})
metrics=[]
for case in ['RH4X','SHW4X']:
    path=bind(P/f'R004/local-cache/actual300-{case}-z0.05-factorized-reference.npz')
    with np.load(path,allow_pickle=False)as z:
        assert np.allclose(A[:18],z['phi_X'],rtol=0,atol=0)and np.allclose(A[18:],z['phi_Y'],rtol=0,atol=0)
        t=z['t'];q=z['s_unitGamma']*z['Gamma_X'][None,:]
        observed_ref=q@A.T
        projected=observed_ref@T.T
        truth=q[:,rows]
        # Same-time projection decomposition: diagonal loss plus all other modal mixing.
        diagpart=truth*np.array([G[0,1],G[1,12]])[None,:]
        mixed=projected-diagpart
        for j,r in enumerate([2,13]):
            y=truth[:,j];v=projected[:,j];p=int(np.argmax(abs(y)));pp=int(np.argmax(abs(v)))
            metrics.append({'Case':case,'reference_zeta':.05,'Mode':r,'NRMSE_observation_projection_vs_known_q_ref':float(np.linalg.norm(v-y)/np.linalg.norm(y)),'known_q_ref_peak_abs':float(np.max(abs(y))),'projection_peak_abs':float(np.max(abs(v))),'projection_peak_relative_difference':float(np.max(abs(v))/np.max(abs(y))-1),'q_ref_peak_time_s':float(t[p]),'projection_peak_time_s':float(t[pp]),'mixing_RMS_over_true_q_RMS':float(np.linalg.norm(mixed[:,j])/np.linalg.norm(y)),'scope':'known linear-reference benchmark; no actual nonlinear q ground truth'})
        np.savez_compressed(L/f'{case}-known-reference-projection-diagnostic.npz',t=t,q_ref_selected=truth,q_projection_selected=projected,mixing_selected=mixed)
core=W/'research/maxwell-20261017/experiments/R001/core-cache';manifest_path=bind(core/'manifest.json');manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
tab=manifest['tables']['Diaphragm CM Displacements'];cols=tab['columns'];cache_path=bind(core/tab['cache']);assert dict(zip(tab['headers'],tab['units']))['UX']=='mm'
allgroups={(v['keys']['Output Case'],v['keys']['Story'],v['keys']['Diaphragm']):k for k,v in tab['groups'].items()}
actual_summary=[]
with np.load(cache_path,allow_pickle=False)as z:
    for case in ['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']:
        groups=[z[allgroups[case,*k]]for k in keys];t=groups[0][:,cols.index('Time')]
        assert all(np.array_equal(t,a[:,cols.index('Time')])for a in groups)
        u=np.column_stack([a[:,cols.index('U'+ax)]*.001 for ax in ['X','Y']for a in groups])
        assert u.shape==(len(t),36)
        q_observed=u@T.T
        np.savez_compressed(L/f'{case}-actual-CM-observation-projection-NOT-actual-q.npz',t=t,q_observed_2_13=q_observed)
        for j,r in enumerate([2,13]):
            y=q_observed[:,j];ii=int(np.argmax(abs(y)))
            actual_summary.append({'Case':case,'Mode':r,'n':len(t),'observed_projection_peak_abs':float(abs(y[ii])),'observed_projection_peak_time_s':float(t[ii]),'label':'CM observation projection only; not recovered actual FNA q or modal shear'})
for name,rr in [('projection-Gram-selected-2.csv',gram),('largest-modal-mixing-20.csv',couplings),('known-reference-projection-errors-4.csv',metrics),('actual-observation-projection-summary-12.csv',actual_summary)]:
    with(H/name).open('x',encoding='utf-8',newline='')as f:cw=csv.DictWriter(f,fieldnames=list(rr[0]));cw.writeheader();cw.writerows(rr)
oldrank=json.loads((P/'R003/results.json').read_text(encoding='utf-8'))
result={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'sources':sources,'single_new_test':'observed-CM mass projection for modes2/13; Gram mixing plus previously solved known-q_ref benchmark and actual observation projections','formula':'q_obs[r]=mr[r]^-1*sum_18(mX*phiX_r*UX_actual +mY*phiY_r*UY_actual); q_obs=G_observed*q only under the retained span and observed-mass model','old_static_result_reused_not_recomputed':{'shape':oldrank['C_shape'],'rank':oldrank['C_rank'],'null_dimension':oldrank['C_nullspace_dimension']},'selected_Gram':gram,'known_reference_tests':metrics,'actual_projection_rows':len(actual_summary),'actual_q_recovered':False,'actual_modal_shear_recovered':False,'new_ODE_or_output_fits':0,'new_raw_workbooks_read':0,'actual_CM_groups_read':108,'all_arrays_local_only':True,'new_actual_projection_values_not_for_paper_real_q':True}
(H/'projection-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'Gram':gram,'known_reference_errors':metrics,'actual_projection_rows':len(actual_summary),'actual_q_recovered':False},ensure_ascii=False))
