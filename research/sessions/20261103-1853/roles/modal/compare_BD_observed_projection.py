from pathlib import Path
import csv,json,hashlib,datetime
import numpy as np
H=Path(__file__).resolve().parent;R=H.parents[4];W=R.parent/'W5-重燃双塔连体';L=H/'local-cache'
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
P=R/'research/sessions/20261031-1130/roles/role4'
prior=json.loads((H/'projection-results.json').read_text(encoding='utf-8'))
cm=read(Path(prior['sources'][0]['path']));mass=read(Path(prior['sources'][1]['path']));co=read(Path(prior['sources'][2]['path']))
keys=sorted({(x['Story'],x['Diaphragm'])for x in mass},key=lambda k:(int(k[0][5:]),k[1]))
cmd={(int(x['Mode']),x['Story'],x['Diaphragm']):x for x in cm};mmd={(x['Axis'],x['Story'],x['Diaphragm']):float(x['identified_mass_kg'])for x in mass}
A=np.vstack([np.array([[float(cmd[r,*k]['U'+ax+'_converted_m'])for r in [2,13]]for k in keys])for ax in ['X','Y']])
m=np.array([mmd[ax,*k]for ax in ['X','Y']for k in keys]);mr=np.array([float(co[i]['mr_kg_m2'])for i in [1,12]])
T=(A.T*m[None,:])/mr[:,None]
folder=W/'02-数据/增阻尼多目标研究-20261016/原生0数据缓存';mp=folder/'manifest.json';manifest=json.loads(mp.read_text(encoding='utf-8'))
tab=manifest['tables']['Diaphragm CM Displacements'];cols=tab['columns'];units=dict(zip(tab['headers'],tab['units']));assert units['UX']==units['UY']=='mm'
index={(v['keys']['Output Case'],v['keys']['Story'],v['keys']['Diaphragm']):k for k,v in tab['groups'].items()}
cache=folder/tab['cache'];hash_before=sha(cache);summary=[];anchors=[]
requested=[('RH4X','Story8',21.66,21.60),('RH4Y','Story10',16.62,21.64)]
with np.load(cache,allow_pickle=False)as z:
    for case in ['RH4X','RH4Y','SHW4X','SHW4Y','SHW7X','SHW7Y']:
        groups=[z[index[case,*k]]for k in keys];t=groups[0][:,cols.index('Time')]
        assert all(np.array_equal(t,a[:,cols.index('Time')])for a in groups)
        u=np.column_stack([a[:,cols.index('U'+ax)]*.001 for ax in ['X','Y']for a in groups]);b=u@T.T
        with np.load(L/f'{case}-actual-CM-observation-projection-NOT-actual-q.npz',allow_pickle=False)as zz:
            assert np.array_equal(t,zz['t']);d=zz['q_observed_2_13']
        np.savez_compressed(L/f'{case}-BD-common-actual-basis-observation-projection.npz',t=t,B_projection=b,D_projection=d)
        for j,r in enumerate([2,13]):
            ib=int(np.argmax(abs(b[:,j])));idd=int(np.argmax(abs(d[:,j])));pb=float(abs(b[ib,j]));pd=float(abs(d[idd,j]))
            summary.append({'Case':case,'Mode':r,'n':len(t),'B_projection_abs_peak':pb,'D_projection_abs_peak':pd,'D_over_B_projection_peak':pd/pb if pb else None,'projection_peak_reduction_percent':100*(1-pd/pb)if pb else None,'B_projection_peak_time_s':float(t[ib]),'D_projection_peak_time_s':float(t[idd]),'identity':'Both states projected on same actual-D300 CM basis; neither series is certified actual q or shear'})
        for c,story,tb,td in requested:
            if c!=case:continue
            for label,tt in [('requested_B_shear_peak',tb),('requested_D_shear_peak',td)]:
                ii=np.flatnonzero(np.isclose(t,tt,rtol=0,atol=1e-10));assert len(ii)==1;ix=int(ii[0])
                for j,r in enumerate([2,13]):anchors.append({'Case':case,'Story':story,'anchor':label,'requested_time_s':tt,'saved_time_s':float(t[ix]),'Mode':r,'B_projection_at_time':float(b[ix,j]),'D_projection_at_time':float(d[ix,j]),'D_minus_B_projection':float(d[ix,j]-b[ix,j]),'identity':'provided shear-peak anchor; projection value only, not modal shear'})
assert sha(cache)==hash_before
for name,rr in [('BD-common-basis-projection-peaks-12.csv',summary),('BD-common-basis-two-control-anchors-8.csv',anchors)]:
    with(H/name).open('x',encoding='utf-8',newline='')as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
out={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'new_source':{'path':str(cache),'bytes':cache.stat().st_size,'sha256':hash_before,'source_manifest':str(mp),'source_manifest_sha256':sha(mp)},'same_basis_and_weights':True,'basis':'actual D signed300 CM shape, modes2/13; actual identified 18-point directional masses','B_own_modal_basis_not_assumed_equal':True,'base_CM_groups_read':108,'all_B_D_time_vectors_exact':True,'rows':len(summary),'anchor_rows':len(anchors),'anchors_are_root_requested_not_new_shear_peak_search':True,'new_ODE_fit_or_raw_workbook':0,'actual_q_or_modal_shear_claim':False,'selected_peak_rows':[x for x in summary if x['Case']in['RH4X','RH4Y']],'anchors':anchors}
(H/'BD-projection-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected_peak_rows':out['selected_peak_rows'],'anchors':anchors},ensure_ascii=False))
