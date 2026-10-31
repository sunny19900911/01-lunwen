import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,importlib.util
import numpy as np
O=Path(__file__).resolve().parent;R=O.parents[5];P=O.parent;D=R.parent/'W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016';L=O/'local-cache';L.mkdir(exist_ok=False);(L/'.gitignore').write_text('*\n!.gitignore\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def cs(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def js(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def module(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
prior=json.loads((P/'R002/input-rules-freeze.json').read_text(encoding='utf-8'));modpath=Path(prior['inputs'][0]['path']);cmpath=Path(prior['inputs'][1]['path']);masspath=P/'R002/identified-masses-before-old-comparison-36.csv';loadpath=R/'research/sessions/20261025-1337/roles/role6/R001/load_inputs.py';configpath=loadpath.with_name('input-config.json');helperpath=Path('C:/Users/mj528/.codex/skills/etabs-response-analysis/scripts/modal_linear.py');cfg=json.loads(configpath.read_text(encoding='utf-8'))
manifestpaths={.05:D/'原生0数据缓存/manifest.json',.08:D/'response_cache_manifest.json'};manifests={z:json.loads(p.read_text(encoding='utf-8')) for z,p in manifestpaths.items()};dirs={.05:D/'原生0数据缓存',.08:D}
sourcepaths=[modpath,cmpath,masspath,loadpath,configpath,helperpath,Path(cfg['derived_npz']),Path(cfg['omega_source']['path']),*manifestpaths.values()]
for z,md in manifests.items():
 for tb in ['Diaphragm CM Displacements','Story Forces']:sourcepaths.append(dirs[z]/md['tables'][tb]['cache'])
sourcepaths=list(dict.fromkeys(sourcepaths));bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sourcepaths]
js('input-rules-freeze.json',dict(start_observed_utc='2026-10-31T04:11:33+00:00',primary_deadline_utc='2026-10-31T04:23:33+00:00',hard_deadline_utc='2026-10-31T04:26:33+00:00',frozen_utc=datetime.now(timezone.utc).isoformat(),sources=bindings,actual300_fixed_basis=True,input='existing exact load_inputs.py unchanged; ag m/s2, dt=.02, zero initial, inherited SHW4 input tail convention',cases=['SHW3X','SHW4X','RH4X'],zeta=[.05,.08],Gamma='Sx/mr from identified actual-CM directional masses; no native PF SI gain',CM='sum(phiUX or phiUY times Gamma*s), m; compare native cm mm times .001; all18 positions, both axes',B='S_aboveX*Gamma directly, kg; compare with previous invariant B but no adjustment',shear_operators=['elastic_inertia=omega2*s','classical_balance=omega2*s+2*zeta*omega*sdot'],shear_sign_mapping_eta=None,shear_sign_policy='reference positive = rcut^T K u; native Bottom VX retained in native sign. No ± search. Only absolute-curve/absolute-peak numerical diagnostics; no signed-force validation claim',CM_time_policy='exact vector equality required; no fill, time shifting, interpolation or truncation to intersection',model_identity='actual300 controlled Ritz basis vs old D baseline5/direct8 M/K not fully identical; posterior independent output comparison, not blind test or actual FNA q',storage='full arrays factorized in local-cache only: unit modal s/sdot, Gamma, phi and B retain every modal term exactly without replicated story-mode-time tensors',no_fit=True))
config,oldomega,data=module('frozenload',loadpath).load_inputs();helper=module('frozenstates',helperpath);cases=['SHW3X','SHW4X','RH4X'];assert list(data)==cases
md=json.loads(modpath.read_text(encoding='utf-8'));mass=read(masspath);cm=read(cmpath);keys=sorted({(d['Story'],d['Diaphragm']) for d in cm},key=lambda k:(int(k[0][5:]),k[1]));assert len(keys)==18 and len(cm)==5400
cmmap={(int(d['Mode']),d['Story'],d['Diaphragm']):d for d in cm};massmap={(d['Axis'],d['Story'],d['Diaphragm']):float(d['identified_mass_kg']) for d in mass}
def table(n):return {int(d[1][1]):dict(SourceRow=d[0],**dict(zip(md[n][1][1],d[1]))) for d in md[n][3:] if d[1][0]=='Modal'}
period=table('Modal Periods And Frequencies');pf=table('Modal Participation Factors');omega=np.array([float(period[r]['CircFreq']) for r in range(1,301)]);mr=np.array([1000*float(pf[r]['ModalMass']) for r in range(1,301)])
phix=np.array([[float(cmmap[r,*k]['UX_converted_m']) for r in range(1,301)] for k in keys]);phiy=np.array([[float(cmmap[r,*k]['UY_converted_m']) for r in range(1,301)] for k in keys]);mx=np.array([massmap['X',*k] for k in keys]);S=mx@phix;Gamma=S/mr;coefx=phix*Gamma;coefy=phiy*Gamma
B=np.array([(mx*np.array([int(k[0][5:])>=cut for k in keys]))@phix*Gamma for cut in range(1,13)])
cs('actual300-frozen-forward-coefficients-300.csv',[dict(Mode=i+1,omega_rad_s=float(omega[i]),mr_kg_m2=float(mr[i]),Sx_kg_m=float(S[i]),Gamma_per_m=float(Gamma[i]),source_period_row=period[i+1]['SourceRow'],source_ModalMass_row=pf[i+1]['SourceRow'],scope='fixed actual300 linear reference, no output fit') for i in range(300)])
nativeCM={};nativeforce={};sourceRowsCM={};sourceRowsforce={};timechecks=[];failures=[]
for z,manifest in manifests.items():
 for tabname in ['Diaphragm CM Displacements','Story Forces']:
  tab=manifest['tables'][tabname];cols=tab.get('columns',tab.get('value_columns'));units=dict(zip(tab['headers'],tab['units']));path=dirs[z]/tab['cache']
  if tabname.startswith('Diaphragm'):
   assert units['UX']==units['UY']=='mm';groups={(g['keys']['Output Case'],g['keys']['Story'],g['keys']['Diaphragm']):k for k,g in tab['groups'].items()}
  else:
   assert units['VX']=='kN';groups={(g['keys']['Output Case'],g['keys']['Story'],g['keys']['Location']):k for k,g in tab['groups'].items()}
  with np.load(path,allow_pickle=False) as zz:
   for case in cases:
    targets=keys if tabname.startswith('Diaphragm') else [('Story'+str(i),'Bottom') for i in range(1,13)]
    for k in targets:
     g=groups.get((case,*k))
     if g is None:failures.append(dict(stage='native_pair',Case=case,zeta=z,table=tabname,key=str(k),reason='missing exact group'));continue
     a=zz[g];t=a[:,cols.index('Time')];ok=np.array_equal(t,data[case]['t']);timechecks.append(dict(Case=case,zeta=z,table=tabname,Story=k[0],Diaphragm_or_Location=k[1],group=g,native_n=len(t),input_n=len(data[case]['t']),exact_time_match=ok))
     if not ok:failures.append(dict(stage='native_pair',Case=case,zeta=z,table=tabname,key=str(k),reason='time vectors differ; not compared or filled'));continue
     if tabname.startswith('Diaphragm'):
      nativeCM[z,case,*k]=a[:,[cols.index('UX'),cols.index('UY')]]*.001;sourceRowsCM[z,case,*k]=a[:,cols.index('SourceRow')].astype(int)
     else:nativeforce[z,case,k[0]]=a[:,cols.index('VX')].copy();sourceRowsforce[z,case,k[0]]=a[:,cols.index('SourceRow')].astype(int)
cs('native-time-group-pairing-180.csv',timechecks)
def metrics(y,p,t,absolute_curve=False):
 den=float(np.linalg.norm(y));i=int(np.argmax(abs(y)));j=int(np.argmax(abs(p)));A=float(abs(y[i]));Ap=float(abs(p[j]));nrmse=float(np.linalg.norm((abs(p)-abs(y)) if absolute_curve else (p-y))/den) if den else None
 return dict(NRMSE=nrmse,native_absolute_peak=float(A),predicted_absolute_peak=float(Ap),peak_relative_error=Ap/A-1 if A else None,native_peak_time_s=float(t[i]),predicted_peak_time_s=float(t[j]),peak_time_shift_s=float(t[j]-t[i]),native_value_at_native_peak=float(y[i]),prediction_at_native_peak=float(p[i]),native_value_at_prediction_peak=float(y[j]),prediction_at_prediction_peak=float(p[j]))
cmerrors=[];forceerrors=[];arraypaths=[]
for case in cases:
 t=data[case]['t'];ag=data[case]['ag'];assert np.allclose(np.diff(t),.02,atol=1e-9,rtol=0)
 for z in [.05,.08]:
  unit_s,unit_v,_=helper.states(ag,omega,z,.02);assert np.all(unit_s[0]==0) and np.all(unit_v[0]==0)
  ux=unit_s@coefx.T;uy=unit_s@coefy.T;tr=dict(t=t,ag=ag,s_unitGamma=unit_s,sdot_unitGamma=unit_v,omega=omega,Gamma_X=Gamma,phi_X=phix,phi_Y=phiy,B_direct= B,CM_predicted_UX_m=ux,CM_predicted_UY_m=uy)
  for j,k in enumerate(keys):
   if (z,case,*k) not in nativeCM:continue
   yy=nativeCM[z,case,*k];tr[f'CM_native_{k[0]}_{k[1]}_UX_UY_m']=yy
   for ia,(ax,pred) in enumerate([('UX',ux[:,j]),('UY',uy[:,j])]):
    m=metrics(yy[:,ia],pred,t);ni=int(np.argmax(abs(yy[:,ia])));pi=int(np.argmax(abs(pred)));cmerrors.append(dict(Case=case,zeta=z,Story=k[0],Diaphragm=k[1],Axis=ax,unit='m',**m,native_peak_SourceRow=int(sourceRowsCM[z,case,*k][ni]),native_at_predicted_peak_SourceRow=int(sourceRowsCM[z,case,*k][pi]),comparison='signed CM motion direct prediction; actual vs oldD model identity confounded'))
  cs(f'early-CM-{case}-z{z:g}-36.csv',[d for d in cmerrors if d['Case']==case and d['zeta']==z]);print(f'CM_EARLY {case} {z} '+datetime.now(timezone.utc).isoformat(),flush=True)
  E=unit_s*(omega**2);Q=E+unit_v*(2*z*omega)
  for op,kern in [('elastic_inertia',E),('classical_balance',Q)]:
   yp=kern@B.T/1000;tr['shear_'+op+'_predicted_kN']=yp
   for i in range(12):
    story='Story'+str(i+1)
    if (z,case,story) not in nativeforce:continue
    y=nativeforce[z,case,story];tr['shear_native_'+story+'_kN']=y;m=metrics(y,yp[:,i],t,absolute_curve=True);m['absolute_curve_NRMSE']=m.pop('NRMSE');ni=int(np.argmax(abs(y)));pi=int(np.argmax(abs(yp[:,i])));forceerrors.append(dict(Case=case,zeta=z,Story=story,Location='Bottom',Axis='X',operator=op,unit='kN',**m,native_peak_SourceRow=int(sourceRowsforce[z,case,story][ni]),native_at_predicted_peak_SourceRow=int(sourceRowsforce[z,case,story][pi]),eta_mapping='unverified; native sign preserved, no sign trials',comparison='absolute curve/absolute peak diagnostic only; no signed-force acceptance'))
  out=L/f'actual300-{case}-z{z:g}-factorized-reference.npz';np.savez_compressed(out,**tr);arraypaths.append(out)
cs('CM-direct-forward-errors-216.csv',cmerrors);cs('shear-two-operator-absolute-diagnostics-144.csv',forceerrors)
if failures:cs('failed-native-pairings.csv',failures)
summ=[]
for z in [.05,.08]:
 for case in cases:
  for ax in ['UX','UY']:
   rr=[d for d in cmerrors if d['zeta']==z and d['Case']==case and d['Axis']==ax];valid=[d for d in rr if d['NRMSE'] is not None];summ.append(dict(Case=case,zeta=z,quantity=ax,operator='CM_motion',points=len(rr),median_NRMSE=float(np.median([d['NRMSE'] for d in valid])) if valid else None,max_NRMSE=max((d['NRMSE'] for d in valid),default=None),max_abs_peak_relative_error=max((abs(d['peak_relative_error']) for d in valid),default=None)))
  for op in ['elastic_inertia','classical_balance']:
   rr=[d for d in forceerrors if d['zeta']==z and d['Case']==case and d['operator']==op];summ.append(dict(Case=case,zeta=z,quantity='Bottom_VX_absolute_only',operator=op,points=len(rr),median_NRMSE=float(np.median([d['absolute_curve_NRMSE'] for d in rr])) if rr else None,max_NRMSE=max((d['absolute_curve_NRMSE'] for d in rr),default=None),max_abs_peak_relative_error=max((abs(d['peak_relative_error']) for d in rr),default=None)))
cs('direct-forward-summary-24.csv',summ)
js('results.json',dict(completed_utc=datetime.now(timezone.utc).isoformat(),CM_rows=len(cmerrors),shear_rows=len(forceerrors),native_pair_failures=failures,time_checks=len(timechecks),all_time_vectors_exact=all(d['exact_time_match'] for d in timechecks),summary=summ,sources_unchanged=all(sha(p)==b['sha256'] for p,b in zip(sourcepaths,bindings)),arrays_local_only=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in arraypaths],no_fit=True,no_old_output_coefficients=True,states_integrations=6,actual_FNA_q=False))
print(json.dumps(dict(CM_rows=len(cmerrors),shear_rows=len(forceerrors),failures=len(failures),summary=summ),ensure_ascii=False,indent=2))
