from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def csvout(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
def js(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
prior=json.loads((P/'results.json').read_text(encoding='utf-8'));src=[Path(prior['source_bindings'][i]['path']) for i in [0,1,2]];bindings=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in src]
for p in src:assert sha(p)==next(d['sha256'] for d in prior['source_bindings'] if d['path']==str(p))
js('input-rules-freeze.json',dict(start_observed_utc='2026-10-31T03:55:46+00:00',deadline_utc='2026-10-31T04:07:46+00:00',frozen_utc=datetime.now(timezone.utc).isoformat(),inputs=bindings,train_modes=[1,100],holdout_modes=[101,300],reference='largest absolute native f among first100; report whether also global largest',rank_threshold='eps*max(H.shape)*smax (primary), plus descriptive 1e-10 relative singular threshold',stable_projection_threshold='abs(Aw)>1e-10*max(abs(Aw)), mu>0; retain all600 estimates and flags',total_mass_scalar='median of stable estimates in first100 only; validate last200, never tune a multiplier',old_mass='read only after identified masses have been saved',CM_model='18 concentrated directional translational masses, not complete FE mass coverage',native_f='signed UX/UY raw values used only in f_r/f_ref; no SI multiplier or Gamma relabeling',ModalMass_conversion='native kN-m-s2 times1000 gives kg*m2',no_shear_fit_ODE_or_new_data=True))
cm=read(src[1]);assert len(cm)==5400
keys=sorted({(d['Story'],d['Diaphragm']) for d in cm},key=lambda k:(int(k[0][5:]),k[1]));assert len(keys)==18
by={(int(d['Mode']),d['Story'],d['Diaphragm']):d for d in cm};assert len(by)==5400
data=json.loads(src[0].read_text(encoding='utf-8'))
def tab(n):return {int(v[1][1]):dict(SourceRow=v[0],**dict(zip(data[n][1][1],v[1]))) for v in data[n][3:] if v[1][0]=='Modal'}
pf=tab('Modal Participation Factors');mu=tab('Modal Participating Mass Ratios');mr=np.array([1000*float(pf[r]['ModalMass']) for r in range(1,301)])
models={};massrows=[];spectrum=[];constraints=[];estimates=[];early=[]
for ax in ['X','Y']:
 A=np.array([[float(by[r,*k]['U'+ax+'_converted_m']) for k in keys] for r in range(1,301)])
 f=np.array([float(pf[r]['U'+ax]) for r in range(1,301)]);ref=int(np.argmax(abs(f[:100])));assert f[ref]!=0
 H=A-(f/f[ref])[:,None]*A[ref];Ht=H[:100]
 _,sv,Vh=np.linalg.svd(Ht,full_matrices=False);tol=np.finfo(float).eps*max(Ht.shape)*sv[0];rank=int(sum(sv>tol));rank10=int(sum(sv>sv[0]*1e-10));assert rank==17,'first100 nullspace not unique; stop before mass interpretation'
 raw=Vh[-1];assert abs(float(raw.sum()))>1e-12;w=raw/raw.sum();assert np.min(w)>=-1e-12
 assert np.min(w)>0,'do not silently clamp negative masses'
 aw=A@w;expected=(f/f[ref])*aw[ref];resid=aw-expected;denmax=float(np.max(abs(aw[:100])));stable=(abs(aw)>1e-10*float(np.max(abs(aw)))) & np.array([float(mu[r]['U'+ax])>0 for r in range(1,301)])
 muc=np.array([float(mu[r]['U'+ax]) for r in range(1,301)]);M=np.divide(muc*mr,aw*aw,out=np.full(300,np.nan),where=aw!=0)
 train_mask=stable & (np.arange(300)<100);assert train_mask.any();Mhat=float(np.median(M[train_mask]));mass=Mhat*w
 for i,k in enumerate(keys):massrows.append(dict(Axis=ax,Story=k[0],Diaphragm=k[1],identified_relative_mass=float(w[i]),identified_mass_kg=float(mass[i]),identified_total_mass_train_median_kg=Mhat,identification='first100 signed projection constraints and first100 mass-ratio/ModalMass estimates only'))
 for i,s in enumerate(sv):spectrum.append(dict(Axis=ax,Singular_index=i+1,singular_value=float(s),relative_to_max=float(s/sv[0]),primary_rank_tolerance=float(tol),above_primary_threshold=bool(s>tol)))
 for r in range(300):
  constraints.append(dict(Axis=ax,Mode=r+1,split='first100_train' if r<100 else 'last200_holdout',reference_Mode=ref+1,native_signed_f=float(f[r]),native_f_over_reference=float(f[r]/f[ref]),Aw_m=float(aw[r]),predicted_Aw_from_f_ratio_m=float(expected[r]),constraint_residual_m=float(resid[r]),residual_over_train_max_Aw=float(resid[r]/denmax),relative_row_residual=abs(float(resid[r]/aw[r])) if aw[r]!=0 else None))
  estimates.append(dict(Axis=ax,Mode=r+1,split='first100_train' if r<100 else 'last200_holdout',mass_ratio_mu=float(muc[r]),ModalMass_times1000_kg_m2=float(mr[r]),Aw_m=float(aw[r]),projection_stable=bool(stable[r]),Mtotal_mode_estimate_kg=float(M[r]) if np.isfinite(M[r]) else None,first100_median_Mtotal_kg=Mhat,relative_difference_vs_train_median=float(M[r]/Mhat-1) if np.isfinite(M[r]) else None,PF_SourceRow=pf[r+1]['SourceRow'],mu_SourceRow=mu[r+1]['SourceRow']))
 def spread(mask):
  vv=M[mask];return dict(count=int(mask.sum()),minimum_kg=float(vv.min()) if len(vv) else None,median_kg=float(np.median(vv)) if len(vv) else None,maximum_kg=float(vv.max()) if len(vv) else None,max_relative_deviation_vs_train_median=float(np.max(abs(vv/Mhat-1))) if len(vv) else None)
 _,svall,_=np.linalg.svd(H,full_matrices=False)
 info=dict(Axis=ax,reference_Mode=ref+1,reference_is_also_global_max=ref==int(np.argmax(abs(f))),train_rank=rank,train_rank_relative1e10=rank10,all300_rank=int(sum(svall>np.finfo(float).eps*max(H.shape)*svall[0])),train_singular_values=sv.tolist(),nullspace_dimension=18-rank,min_identified_weight=float(w.min()),sum_identified_weights=float(w.sum()),relative_H_train_null_residual=float(np.linalg.norm(Ht@w)/(np.linalg.norm(Ht)*np.linalg.norm(w))),train_max_abs_projection_constraint_residual_m=float(np.max(abs(resid[:100]))),holdout_max_abs_projection_constraint_residual_m=float(np.max(abs(resid[100:]))),holdout_max_residual_over_train_max_Aw=float(np.max(abs(resid[100:]))/denmax),train_mass_spread=spread(train_mask),holdout_mass_spread=spread(stable & (np.arange(300)>=100)),unstable_mode_numbers=[int(r+1) for r in np.flatnonzero(~stable)],identified_total_mass_kg=Mhat)
 early.append(info);models[ax]=dict(A=A,w=w,mass=mass,Mhat=Mhat,H=H,ref=ref,info=info)
csvout('identified-masses-before-old-comparison-36.csv',massrows)
csvout('constraint-singular-values-36.csv',spectrum)
csvout('projection-constraint-train100-holdout200-600.csv',constraints)
csvout('independent-mode-total-mass-estimates-600.csv',estimates)
js('early-rank-and-identification.json',dict(saved_before_old_mass_read_utc=datetime.now(timezone.utc).isoformat(),axis_results=early))
# Only here are old mass values read; no weight, sign or scale is subsequently changed.
old=read(src[2]);oldmap={(d['Story'],d['Diaphragm']):d for d in old};assert set(oldmap)==set(keys)
comparisons=[]
for d in massrows:
 k=(d['Story'],d['Diaphragm']);oldv=float(oldmap[k]['old_Mass'+d['Axis']+'_kg']);oldtot=sum(float(v['old_Mass'+d['Axis']+'_kg']) for v in old)
 comparisons.append({**d,'old_mass_kg':oldv,'old_relative_mass':oldv/oldtot,'identified_minus_old_kg':d['identified_mass_kg']-oldv,'identified_vs_old_relative_difference':d['identified_mass_kg']/oldv-1,'old_SourceRow':oldmap[k]['old_mass_SourceRow']})
csvout('identified-versus-old-directional-masses-36.csv',comparisons)
obs=[]
for r in range(300):
 tx=float(np.sum(models['X']['mass']*models['X']['A'][r]**2));ty=float(np.sum(models['Y']['mass']*models['Y']['A'][r]**2));rat=(tx+ty)/mr[r]
 obs.append(dict(Mode=r+1,split='first100_train' if r<100 else 'last200_holdout',observed_X_generalized_mass_kg_m2=tx,observed_Y_generalized_mass_kg_m2=ty,observed_XY_generalized_mass_kg_m2=tx+ty,native_ModalMass_times1000_kg_m2=float(mr[r]),observed_XY_over_native_mr=rat,native_minus_observed_kg_m2=float(mr[r]-tx-ty),exceeds_one_beyond_1e10=bool(rat>1+1e-10),scope='18-CM concentrated translation observation; no actual q recovery'))
csvout('observed-XY-generalized-mass-check-300.csv',obs)
result=dict(completed_utc=datetime.now(timezone.utc).isoformat(),axis_results=early,max_identified_old_mass_relative_difference=max(abs(d['identified_vs_old_relative_difference']) for d in comparisons),max_identified_old_mass_abs_difference_kg=max(abs(d['identified_minus_old_kg']) for d in comparisons),observed_XY_ratio_min=min(d['observed_XY_over_native_mr'] for d in obs),observed_XY_ratio_max=max(d['observed_XY_over_native_mr'] for d in obs),observed_ratio_violations=[d for d in obs if d['exceeds_one_beyond_1e10']],top5_observed_ratios=sorted(obs,key=lambda d:d['observed_XY_over_native_mr'],reverse=True)[:5],sources_unchanged=all(sha(p)==b['sha256'] for p,b in zip(src,bindings)),old_mass_read_only_after_identified_mass_file_saved=True,no_total_shear_fit_ODE_or_new_table=True)
assert result['sources_unchanged'];js('results.json',result)
print(json.dumps(result,ensure_ascii=False,indent=2))
