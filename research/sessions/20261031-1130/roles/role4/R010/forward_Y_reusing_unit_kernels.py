import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent;R=O.parents[5];D=R.parent/'W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016';L=O/'local-cache';L.mkdir(exist_ok=False);(L/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def cs(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
 assert (O/n).stat().st_size<1000000
def js(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
X=json.loads((P/'R004/results.json').read_text(encoding='utf-8'));Xrule=json.loads((P/'R004/input-rules-freeze.json').read_text(encoding='utf-8'));actual=Path(next(d['path'] for d in Xrule['sources'] if d['path'].endswith('controlled_small_tables.json')));masspath=P/'R002/identified-masses-before-old-comparison-36.csv';admitpath=P/'R009/Y-input-admission-and-X-reuse-evidence-3.csv';admit=read(admitpath);paths={.05:D/'原生0数据缓存/manifest.json',.08:D/'response_cache_manifest.json'};manifest={z:json.loads(p.read_text(encoding='utf-8')) for z,p in paths.items()}
sources=[actual,masspath,admitpath,*paths.values()]+[Path(d['path']) for d in X['arrays_local_only']]
for z,md in manifest.items():
 for tb in ['Diaphragm CM Displacements','Story Forces']:sources.append(paths[z].parent/md['tables'][tb]['cache'])
sources=list(dict.fromkeys(sources));bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sources]
for d in X['arrays_local_only']:assert sha(Path(d['path']))==d['sha256']
js('input-rules-freeze.json',dict(start_observed_utc='2026-10-31T04:48:53+00:00',deadline_utc='2026-10-31T05:00:53+00:00',frozen_utc=datetime.now(timezone.utc).isoformat(),sources=bindings,code_sha256=sha(Path(__file__)),source_case_mapping={d['Y_case']:d['reuse_scalar_X_input_from'] for d in admit},inputs='same scalar function/SF/time/initial state admitted in R009; reuse exact saved actual300 s/sdot/omega, no new ODE or SF/g multipliers',Y_coefficients='GammaY=(mY dot phiY)/mr; BY_s=GammaY*sum_above(mY*phiY), CM UX/UY output uses matching phiX/phiY times GammaY',native='all18 CM UX/UY mm to m and all12 Bottom VY kN; all180 time vectors must exactly equal saved t, missing not filled',shear='E and Q retain reference direction; eta unverified, absolute curve and absolute peak diagnostics only; no sign/gain/time selection',optional_UPC='E only, 36pairs, U=sum independent single-mode reference peaks, C=P/U',storage='source unit kernels referenced by path and SHA, not duplicated; new local arrays store GammaY/BY and outputs/native values only',scope='same three earthquake functions, different input direction; not six independent events, no actual Maxwell/SHW7 relabeling',no_ODE_fit=True))
md=json.loads(actual.read_text(encoding='utf-8'));head=md['Modal Participation Factors'][1][1];pf={int(d[1][1]):dict(SourceRow=d[0],**dict(zip(head,d[1]))) for d in md['Modal Participation Factors'][3:] if d[1][0]=='Modal'};period={int(d[1][1]):dict(zip(md['Modal Periods And Frequencies'][1][1],d[1])) for d in md['Modal Periods And Frequencies'][3:] if d[1][0]=='Modal'};mr=np.array([1000*float(pf[i]['ModalMass']) for i in range(1,301)]);omega_actual=np.array([float(period[i]['CircFreq']) for i in range(1,301)]);mass=read(masspath);keys=sorted({(d['Story'],d['Diaphragm']) for d in mass},key=lambda k:(int(k[0][5:]),k[1]));assert len(keys)==18;my=np.array([float(next(d['identified_mass_kg'] for d in mass if d['Axis']=='Y' and (d['Story'],d['Diaphragm'])==k)) for k in keys])
def metrics(y,p,t,absdiag=False):
 i=int(np.argmax(abs(y)));j=int(np.argmax(abs(p)));a=float(abs(y[i]));b=float(abs(p[j]));den=float(np.linalg.norm(y));return dict(NRMSE=float(np.linalg.norm(abs(p)-abs(y) if absdiag else p-y)/den) if den else None,native_absolute_peak=a,predicted_absolute_peak=b,peak_relative_error=b/a-1 if a else None,native_peak_time_s=float(t[i]),predicted_peak_time_s=float(t[j]),peak_time_shift_s=float(t[j]-t[i]),native_value_at_native_peak=float(y[i]),prediction_at_native_peak=float(p[i]),native_value_at_prediction_peak=float(y[j]),prediction_at_prediction_peak=float(p[j]))
cmerr=[];forceerr=[];timechecks=[];failures=[];arrays=[];kernelrefs=[];peaks={};uco={};coefwritten=False
for case in ['SHW3Y','SHW4Y','RH4Y']:
 xc=next(d['reuse_scalar_X_input_from'] for d in admit if d['Y_case']==case)
 for z in [.05,.08]:
  source=next(d for d in X['arrays_local_only'] if f'-{xc}-z{z:g}-' in d['path']);path=Path(source['path'])
  with np.load(path,allow_pickle=False) as old:
   t=old['t'];s=old['s_unitGamma'];v=old['sdot_unitGamma'];om=old['omega'];px=old['phi_X'];py=old['phi_Y'];assert np.array_equal(om,omega_actual) and np.all(s[0]==0) and np.all(v[0]==0);S=my@py;G=S/mr;B=np.array([(my*np.array([int(k[0][5:])>=cut for k in keys]))@py*G for cut in range(1,13)])
   if not coefwritten:cs('actual300-Y-forward-physical-coefficients-300.csv',[dict(Mode=i+1,omega_rad_s=float(om[i]),mr_kg_m2=float(mr[i]),Sy_kg_m=float(S[i]),GammaY_per_m=float(G[i]),ModalMass_SourceRow=pf[i+1]['SourceRow'],scope='Y physical-source coefficients, linear reference only') for i in range(300)]);coefwritten=True
   ux=s@(px*G).T;uy=s@(py*G).T;E=s*om**2;Q=E+v*(2*z*om);shear={'elastic_inertia':E@B.T/1000,'classical_balance':Q@B.T/1000};tr=dict(t=t,Gamma_Y=G,B_Y=B,CM_predicted_UX_m=ux,CM_predicted_UY_m=uy,shear_elastic_inertia_predicted_kN=shear['elastic_inertia'],shear_classical_balance_predicted_kN=shear['classical_balance']);nativeCM={};nativeF={};rowsCM={};rowsF={}
   for tabname in ['Diaphragm CM Displacements','Story Forces']:
    tab=manifest[z]['tables'][tabname];cols=tab.get('columns',tab.get('value_columns'));units=dict(zip(tab['headers'],tab['units']));cache=paths[z].parent/tab['cache'];isCM=tabname.startswith('Diaphragm');groups={(g['keys']['Output Case'],g['keys']['Story'],g['keys'].get('Diaphragm',g['keys'].get('Location'))):gid for gid,g in tab['groups'].items()};targets=keys if isCM else [('Story'+str(i),'Bottom') for i in range(1,13)]
    assert units['UX']==units['UY']=='mm' if isCM else units['VY']=='kN'
    with np.load(cache,allow_pickle=False) as zz:
     for k in targets:
      gid=groups.get((case,*k))
      if gid is None:failures.append(dict(Case=case,zeta=z,table=tabname,key=str(k),reason='group absent; not filled'));continue
      a=zz[gid];tt=a[:,cols.index('Time')];ok=np.array_equal(tt,t);timechecks.append(dict(Case=case,source_scalar_case=xc,zeta=z,table=tabname,Story=k[0],Diaphragm_or_Location=k[1],group_id=gid,native_n=len(tt),saved_n=len(t),time_vectors_exact=ok))
      if not ok:failures.append(dict(Case=case,zeta=z,table=tabname,key=str(k),reason='time mismatch; no fill or intersection'));continue
      if isCM:nativeCM[k]=a[:,[cols.index('UX'),cols.index('UY')]]*.001;rowsCM[k]=a[:,cols.index('SourceRow')].astype(int)
      else:nativeF[k[0]]=a[:,cols.index('VY')].copy();rowsF[k[0]]=a[:,cols.index('SourceRow')].astype(int)
   for j,k in enumerate(keys):
    if k not in nativeCM:continue
    yy=nativeCM[k];tr[f'CM_native_{k[0]}_{k[1]}_UX_UY_m']=yy
    for ia,(ax,pred) in enumerate([('UX',ux[:,j]),('UY',uy[:,j])]):
     d=metrics(yy[:,ia],pred,t);ni=int(np.argmax(abs(yy[:,ia])));cmerr.append(dict(Case=case,scalar_kernel_case=xc,zeta=z,Story=k[0],Diaphragm=k[1],Axis=ax,unit='m',**d,native_peak_SourceRow=int(rowsCM[k][ni]),scope='Y input signed CM motion; retrospective direct physical reference, not actual FNA q'))
   cs(f'early-CM-{case}-z{z:g}-36.csv',[d for d in cmerr if d['Case']==case and d['zeta']==z]);print(f'EARLY_CM {case} {z} '+datetime.now(timezone.utc).isoformat(),flush=True)
   amp=abs(B)*(om**2*np.max(abs(s),axis=0))[None,:]/1000
   for op,yp in shear.items():
    for j in range(12):
     story='Story'+str(j+1)
     if story not in nativeF:continue
     y=nativeF[story];tr['shear_native_'+story+'_VY_kN']=y;d=metrics(y,yp[:,j],t,True);d['absolute_curve_NRMSE']=d.pop('NRMSE');ni=int(np.argmax(abs(y)));forceerr.append(dict(Case=case,scalar_kernel_case=xc,zeta=z,Story=story,Axis='Y',Location='Bottom',operator=op,unit='kN',**d,native_peak_SourceRow=int(rowsF[story][ni]),eta_mapping='unverified; no sign trials',scope='native VY absolute curve/peak only; no fullFE elastic identity acceptance'));peaks[case,z,story,op]=d
     if op=='elastic_inertia':U=float(amp[j].sum());Pp=d['predicted_absolute_peak'];uco[case,z,story]=dict(U=U,P=Pp,C=Pp/U)
   out=L/f'Y-output-{case}-z{z:g}.npz';np.savez_compressed(out,**tr);arrays.append(dict(path=str(out),bytes=out.stat().st_size,sha256=sha(out)));kernelrefs.append(dict(Y_case=case,zeta=z,source_scalar_case=xc,unit_kernel_path=str(path),unit_kernel_sha256=source['sha256'],new_Y_output_path=str(out),source_s_sdot_omega_duplicated=False))
cs('Y-CM-direct-forward-errors-216.csv',cmerr);cs('Y-VY-two-operator-absolute-diagnostics-144.csv',forceerr);cs('Y-native-exact-time-pairing-180.csv',timechecks)
if failures:cs('Y-failed-native-pairings.csv',failures)
js('early-primary-output-counts.json',dict(completed_utc=datetime.now(timezone.utc).isoformat(),CM_rows=len(cmerr),force_rows=len(forceerr),time_groups=len(timechecks),failures=failures,no_new_ODE=True))
pairs=[];upc=[]
for case in ['SHW3Y','SHW4Y','RH4Y']:
 for j in range(1,13):
  story='Story'+str(j);e5=peaks[case,.05,story,'elastic_inertia'];e8=peaks[case,.08,story,'elastic_inertia'];q5=peaks[case,.05,story,'classical_balance'];q8=peaks[case,.08,story,'classical_balance'];pn5=e5['native_absolute_peak'];pn8=e8['native_absolute_peak'];rn=pn8/pn5;re=e8['predicted_absolute_peak']/e5['predicted_absolute_peak'];rq=q8['predicted_absolute_peak']/q5['predicted_absolute_peak'];pairs.append(dict(Case=case,Story=story,native_peak5_VY_kN=pn5,native_peak8_VY_kN=pn8,E_peak5_kN=e5['predicted_absolute_peak'],E_peak8_kN=e8['predicted_absolute_peak'],Q_peak5_kN=q5['predicted_absolute_peak'],Q_peak8_kN=q8['predicted_absolute_peak'],native_peak_decrease_percent=100*(1-rn),E_reference_peak_decrease_percent=100*(1-re),Q_reference_peak_decrease_percent=100*(1-rq),E_minus_native_decrease_pp=100*(rn-re),Q_minus_native_decrease_pp=100*(rn-rq),native5_peak_s=e5['native_peak_time_s'],native8_peak_s=e8['native_peak_time_s'],E5_peak_s=e5['predicted_peak_time_s'],E8_peak_s=e8['predicted_peak_time_s'],Q5_peak_s=q5['predicted_peak_time_s'],Q8_peak_s=q8['predicted_peak_time_s'],scope='same3 scalar functions Y direction, native absolute peaks; no six-event claim'))
  a=uco[case,.05,story];b=uco[case,.08,story];upc.append(dict(Case=case,Story=story,U5_kN=a['U'],U8_kN=b['U'],P5_kN=a['P'],P8_kN=b['P'],C5=a['C'],C8=b['C'],U8_over_U5=b['U']/a['U'],C8_over_C5=b['C']/a['C'],P8_over_P5=b['P']/a['P'],ratio_identity_error=b['P']/a['P']-b['U']/a['U']*b['C']/a['C'],scope='Y elastic inertia reference UPC, not actual FNA modal unique decomposition'))
cs('Y-all12-threewaves-native-E-Q-peak-decrease-36.csv',pairs);cs('Y-all12-threewaves-E-UPC-36.csv',upc);cs('Y-Story5-Story12-peak-decrease-6.csv',[d for d in pairs if d['Story'] in ['Story5','Story12']])
summary=[]
for case in ['SHW3Y','SHW4Y','RH4Y']:
 for z in [.05,.08]:
  for ax in ['UX','UY']:
   rr=[d for d in cmerr if d['Case']==case and d['zeta']==z and d['Axis']==ax];summary.append(dict(Case=case,zeta=z,quantity=ax,operator='CM_motion',rows=len(rr),median_NRMSE=float(np.median([d['NRMSE'] for d in rr])),max_NRMSE=max(d['NRMSE'] for d in rr),max_abs_peak_relative_error=max(abs(d['peak_relative_error']) for d in rr)))
  for op in ['elastic_inertia','classical_balance']:
   rr=[d for d in forceerr if d['Case']==case and d['zeta']==z and d['operator']==op];summary.append(dict(Case=case,zeta=z,quantity='Bottom_VY_absolute',operator=op,rows=len(rr),median_NRMSE=float(np.median([d['absolute_curve_NRMSE'] for d in rr])),max_NRMSE=max(d['absolute_curve_NRMSE'] for d in rr),max_abs_peak_relative_error=max(abs(d['peak_relative_error']) for d in rr)))
cs('Y-forward-summary-24.csv',summary);js('unit-kernel-reuse-6.json',kernelrefs);js('results.json',dict(completed_utc=datetime.now(timezone.utc).isoformat(),CM_rows=len(cmerr),force_rows=len(forceerr),native_time_groups=len(timechecks),all_native_times_exact=all(d['time_vectors_exact'] for d in timechecks),failures=failures,peak_decrease_pairs=36,UPC_pairs=36,summary=summary,unit_kernel_sources=kernelrefs,local_only_Y_outputs=arrays,no_new_ODE=True,no_fit=True,unit_s_sdot_not_copied=True,sources_unchanged=all(sha(p)==d['sha256'] for p,d in zip(sources,bindings))))
print(json.dumps(dict(CM_rows=len(cmerr),force_rows=len(forceerr),pairs=36,failures=failures,summary=summary),ensure_ascii=False,indent=2))
