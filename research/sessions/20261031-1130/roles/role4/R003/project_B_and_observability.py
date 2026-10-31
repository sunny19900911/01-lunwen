from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R002';R=O.parents[5];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def cs(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def js(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prior=json.loads((P/'input-rules-freeze.json').read_text(encoding='utf-8'));src=[P/'identified-masses-before-old-comparison-36.csv',Path(prior['inputs'][1]['path']),Path(prior['inputs'][0]['path'])];manifest=json.loads((P/'delivery-manifest.json').read_text(encoding='utf-8'));assert sha(src[0])==next(d['sha256'] for d in manifest['outputs'] if d['name']==src[0].name)
bindings=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in src]
js('input-rules-freeze.json',dict(start_observed_utc='2026-10-31T04:01:49+00:00',deadline_utc='2026-10-31T04:13:49+00:00',frozen_utc=datetime.now(timezone.utc).isoformat(),inputs=bindings,masses='reuse frozen R002 only; no re-identification',cut='Storys Bottom includes Story>=s, all diaphragms',B='m_eff*S_above/S_all; signed inertia projection, not full-FE elastic shear',m_eff='actual modal mass ratio times R002 identified directional mass total',checks='base B=m_eff; local Cauchy and full-modal-mass Cauchy; signed sum B vs actual identified mass above, finite300 Ritz no forced completeness',observability='C=[diag(sqrt(mx))*PhiX;diag(sqrt(my))*PhiY], 36x300 actual q coordinates; SVD rowspace and selected e2/e10/e13 distances only',rank='eps*max(C.shape)*sigma1; also relative1e-10',no_new_ODE_q_or_shear_fit=True))
mass=read(src[0]);cm=read(src[1]);keys=sorted({(d['Story'],d['Diaphragm']) for d in mass},key=lambda k:(int(k[0][5:]),k[1]));assert len(keys)==18 and len(cm)==5400
massmap={(d['Axis'],d['Story'],d['Diaphragm']):d for d in mass};cmmap={(int(d['Mode']),d['Story'],d['Diaphragm']):d for d in cm}
data=json.loads(src[2].read_text(encoding='utf-8'))
def table(n):return {int(d[1][1]):dict(SourceRow=d[0],**dict(zip(data[n][1][1],d[1]))) for d in data[n][3:] if d[1][0]=='Modal'}
rat=table('Modal Participating Mass Ratios');pf=table('Modal Participation Factors');mr=np.array([1000*float(pf[r]['ModalMass']) for r in range(1,301)])
As={};ms={};Bfull=[];modebase=[];sums=[];main=[];maxbase=0.;maxlocal=maxglobal=0.;sumBaxes={}
for ax in ['X','Y']:
 A=np.array([[float(cmmap[r,*k]['U'+ax+'_converted_m']) for r in range(1,301)] for k in keys]);m=np.array([float(massmap[ax,*k]['identified_mass_kg']) for k in keys]);M=float(m.sum());mu=np.array([float(rat[r]['U'+ax]) for r in range(1,301)])*M;S=m@A;assert np.all(S!=0)
 As[ax]=A;ms[ax]=m
 for ir in range(300):modebase.append(dict(Axis=ax,Mode=ir+1,S_all_identified_mass_CM_kg_m=float(S[ir]),m_eff_actual_ratio_times_identified_M_kg=float(mu[ir]),m_eff_from_S2_over_native_mr_kg=float(S[ir]**2/mr[ir]),relative_consistency_error=float(S[ir]**2/mr[ir]/mu[ir]-1),native_mr_kg_m2=float(mr[ir]),scope='inertia projection only, not fullFE elastic shear'))
 for cut in range(1,13):
  selected=np.array([int(k[0][5:])>=cut for k in keys]);Mup=float(m[selected].sum());Ss=m[selected]@A[selected];Gup=(m[selected,None]*A[selected]**2).sum(axis=0);B=mu*Ss/S;local=np.divide(Ss**2,Mup*Gup,out=np.zeros(300),where=Gup!=0);glob=np.divide(B**2,mu*Mup,out=np.zeros(300),where=mu!=0)
  maxlocal=max(maxlocal,float(local.max()));maxglobal=max(maxglobal,float(glob.max()));assert local.max()<=1+1e-10 and glob.max()<=1+1e-10
  if cut==1:maxbase=max(maxbase,float(np.max(abs(B-mu))))
  for ir in range(300):
   d=dict(cut_story='Story'+str(cut),Axis=ax,Mode=ir+1,B_inertia_projection_kg_not_fullFE_elastic=float(B[ir]),Cauchy_B2_over_meff_Mabove=float(glob[ir]),Cauchy_Sabove2_over_Mabove_Gabove=float(local[ir]));Bfull.append(d)
   if ir+1 in [2,10,13]:main.append({**d,'CMs_above':int(selected.sum()),'identified_Mabove_kg':Mup,'S_above_kg_m':float(Ss[ir]),'m_eff_kg':float(mu[ir]),'base_S_kg_m':float(S[ir])})
  sums.append(dict(cut_story='Story'+str(cut),Axis=ax,CMs_above=int(selected.sum()),identified_mass_above_kg=Mup,sum_signed_300_B_inertia_projection_kg_not_fullFE_elastic=float(B.sum()),sum_B_minus_mass_above_kg=float(B.sum()-Mup),relative_sum_B_minus_mass=float(B.sum()/Mup-1),sum_abs_300_B_kg=float(abs(B).sum()),negative_B_modes_count=int(sum(B<0)),scope='finite300 Ritz inertia projection, no forced completeness'))
cs('all12-300-XY-signed-B-inertia-not-elastic-7200.csv',Bfull);cs('modes2-10-13-all12-XY-B-inertia-not-elastic-72.csv',main);cs('mode-direction-normalization-checks-600.csv',modebase);cs('finite300-signed-sumB-versus-mass-above-24.csv',sums)
C=np.vstack([np.sqrt(ms['X'])[:,None]*As['X'],np.sqrt(ms['Y'])[:,None]*As['Y']]);assert C.shape==(36,300)
U,sv,Vh=np.linalg.svd(C,full_matrices=False);tol=np.finfo(float).eps*max(C.shape)*sv[0];rank=int(sum(sv>tol));rank10=int(sum(sv>1e-10*sv[0]));Vr=Vh[:rank];lever=(Vr**2).sum(axis=0);dist=np.sqrt(np.maximum(0,1-lever))
cs('CM-observation-singular-values-36.csv',[dict(index=i+1,singular_value=float(v),relative_to_largest=float(v/sv[0]),rank_primary_threshold=float(tol),above_threshold=bool(v>tol),scope='36x300 massweighted CM translation observation, not force') for i,v in enumerate(sv)])
cs('coordinate-rowspace-distances-all300.csv',[dict(Mode=i+1,rowspace_projection_squared_norm=float(lever[i]),distance_e_to_rowspace=float(dist[i]),unique_if_distance_below_1e10=bool(dist[i]<1e-10),scope='CM translation actual-q coordinate identifiability only; no q fitted') for i in range(300)])
selectedobs=[]
for mode in [2,10,13]:
 i=mode-1;e=np.zeros(300);e[i]=1.;proj=Vr.T@Vr[:,i];n=e-proj;nn=float(np.linalg.norm(n));res=float(np.linalg.norm(C@n)/(np.linalg.norm(C)*nn))
 selectedobs.append(dict(Mode=mode,distance_e_to_rowspace=nn,rowspace_leverage=float(lever[i]),nullspace_vector_mode_component=float(n[i]),nullspace_vector_norm=nn,relative_observation_null_residual=res,actual_q_mode_uniquely_identifiable=bool(nn<1e-10),scope='nonzero null coordinate proves no unique actual q from instantaneous CM translations'))
cs('modes2-10-13-coordinate-identifiability-3.csv',selectedobs)
summary=dict(completed_utc=datetime.now(timezone.utc).isoformat(),B_rows=len(Bfull),main_mode_rows=len(main),sum_mass_checks=len(sums),base_B_minus_meff_max_abs_kg=maxbase,max_local_Cauchy_ratio=maxlocal,max_global_Cauchy_ratio=maxglobal,max_mode_normalization_relative_error=max(abs(d['relative_consistency_error']) for d in modebase),sumB_max_abs_relative_mass_deviation=max(abs(d['relative_sum_B_minus_mass']) for d in sums),worst_sumB=sorted(sums,key=lambda d:abs(d['relative_sum_B_minus_mass']),reverse=True)[:5],C_shape=list(C.shape),C_rank=rank,C_rank_relative1e10=rank10,C_nullspace_dimension=300-rank,C_singular_max=float(sv[0]),C_singular_min=float(sv[-1]),selected_coordinate_checks=selectedobs,sources_unchanged=all(sha(p)==b['sha256'] for p,b in zip(src,bindings)),no_new_mass_identification_q_fit_or_ODE=True)
js('results.json',summary);print(json.dumps(summary,ensure_ascii=False,indent=2))
