import os
os.environ['OPENBLAS_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,csv,hashlib
import numpy as np

O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130';SRC=S/'roles/role4/R003'
START=datetime.fromisoformat('2026-10-31T12:10:27+08:00');DEADLINE=START+timedelta(minutes=10)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate():
    if now()>=DEADLINE:raise RuntimeError('R004 deadline')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(n,x):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def table(n,x):
    with (O/n).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(x[0]),lineterminator='\n');w.writeheader();w.writerows(x)
gate();mf=json.loads((SRC/'delivery-manifest.json').read_text(encoding='utf-8'))
for e in mf['outputs']:
    p=SRC/e['name'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
cm_entry=next(e for e in mf['inputs'] if e['path'].endswith('CM-signed-all300-5400.csv'))
meta_entry=next(e for e in mf['inputs'] if e['path'].endswith('controlled_small_tables.json'))
for e in (cm_entry,meta_entry):
    p=Path(e['path']);assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
ownmass=S/'roles/role2/R003/independent-identification-before-comparison-36.csv'
ownmf=json.loads((ownmass.parent/'manifest.json').read_text(encoding='utf-8'))
e=next(e for e in ownmf['files'] if e['name']==ownmass.name)
assert ownmass.stat().st_size==e['bytes'] and sha(ownmass)==e['sha256']
mr=rows(ownmass);keys=sorted({(int(x['Story'].removeprefix('Story')),x['Diaphragm']) for x in mr});index={('Story'+str(a),b):i for i,(a,b) in enumerate(keys)}
assert len(keys)==18
mass={d:np.zeros(18) for d in ('X','Y')}
for x in mr:mass[x['direction']][index[x['Story'],x['Diaphragm']]]=float(x['identified_mass_kg'])
assert all(np.all(m>0) for m in mass.values())
cm=rows(Path(cm_entry['path']));F={d:np.full((300,18),np.nan) for d in ('X','Y')};seen=set()
for x in cm:
    i=int(x['Mode'])-1;j=index[x['Story'],x['Diaphragm']];assert (i,j) not in seen;seen.add((i,j))
    assert x['OutputCase']=='Modal' and x['CaseType']=='LinModRitz'
    for d in ('X','Y'):F[d][i,j]=float(x['U'+d+'_native_mm'])*.001
assert len(seen)==5400 and all(np.isfinite(a).all() for a in F.values())
small=json.loads(Path(meta_entry['path']).read_text(encoding='utf-8'));t=small['Modal Participating Mass Ratios'];h=t[1][1]
ratio={int(x[h.index('Mode')]):x for _,x in t[3:] if x[h.index('Case')]=='Modal'}
assert sorted(ratio)==list(range(1,301))
B={};selected=[];sums=[];globS={};meffdir={}
for d in ('X','Y'):
    gate();total=float(sum(mass[d]));globS[d]=F[d]@mass[d]
    mu=np.array([float(ratio[k][h.index('U'+d)]) for k in range(1,301)]);meffdir[d]=total*mu
    assert np.all(abs(globS[d])>1e-10*max(abs(globS[d])))
    for story in range(1,13):
        mask=np.array([st>=story for st,_ in keys]);mabove=float(sum(mass[d][mask]));sab=F[d][:,mask]@mass[d][mask]
        b=meffdir[d]*sab/globS[d];B[d,story]=b
        for mode in (2,10,13):
            i=mode-1
            selected.append({'Axis':d,'cut_story':'Story'+str(story),'Mode':mode,'B_inertia_projection_kg':float(b[i]),'S_above_kg_m':float(sab[i]),'S_all_kg_m':float(globS[d][i]),'m_eff_kg':float(meffdir[d][i]),'identified_mass_above_kg':mabove})
        sb=float(sum(b));sums.append({'Axis':d,'cut_story':'Story'+str(story),'mass_above_kg':mabove,'sum_signed_300_B_kg':sb,'difference_kg':sb-mabove,'relative_difference':sb/mabove-1,'sum_abs_300_B_kg':float(sum(abs(b))),'negative_modes':int(sum(b<0))})
table('independent-inertia-B-selected-72.csv',selected)
table('independent-finite300-sumB-24.csv',sums)
gate()
# Modal columns retain their native coordinates; no Gamma or column normalization is applied.
C=np.vstack([np.sqrt(mass['X'])[:,None]*F['X'].T,np.sqrt(mass['Y'])[:,None]*F['Y'].T])
_,sv,Vt=np.linalg.svd(C,full_matrices=False);tol=np.finfo(float).eps*max(C.shape)*sv[0]
rank=int(sum(sv>tol));rank2=int(sum(sv>sv[0]*1e-10));assert rank==rank2==36
V=Vt[:rank];coord=[]
for mode in (2,10,13):
    e=np.zeros(300);e[mode-1]=1
    n=e-V.T@V[:,mode-1];dist=float(np.linalg.norm(n));component=float(n[mode-1]);nullerr=float(np.linalg.norm(C@n)/(sv[0]*dist));leverage=float(sum(V[:,mode-1]**2))
    assert dist>.05 and nullerr<1e-12 and abs(component-dist**2)<1e-13
    coord.append({'Mode':mode,'distance_to_rowspace':dist,'rowspace_leverage':leverage,'null_direction_mode_component':component,'relative_Cn_null_residual':nullerr,'uniquely_identifiable_from_instantaneous_observations':False})
table('independent-coordinate-distances-3.csv',coord)
table('independent-observation-singular-values-36.csv',[{'index':i+1,'sigma':float(s),'relative_sigma':float(s/sv[0]),'rank_tolerance':float(tol)} for i,s in enumerate(sv)])
save('independent-early.json',{'completed':now().isoformat(),'rank':rank,'rank_relative1e-10':rank2,'shape':list(C.shape),'nullity':300-rank,'sigma_max':float(sv[0]),'sigma_min':float(sv[-1]),'conditional_nonzero_singular_condition':float(sv[0]/sv[-1]),'no_target_result_table_used_before_saved_outputs':True,'mass_source':'role2 R003 already frozen independent identification, no re-identification','CM_coordinates':'XY translations all300 columns in native modal normalization, row weighted only','sources':[{'path':str(ownmass),'sha256':sha(ownmass)},cm_entry,meta_entry]})
gate()
target={(x['Axis'],x['cut_story'],int(x['Mode'])):x for x in rows(SRC/'modes2-10-13-all12-XY-B-inertia-not-elastic-72.csv')}
errB=[]
for x in selected:
    y=target[x['Axis'],x['cut_story'],x['Mode']];a=x['B_inertia_projection_kg'];b=float(y['B_inertia_projection_kg_not_fullFE_elastic']);er=abs(a-b)
    assert er<1e-10*max(1,abs(b));errB.append(er)
targetsum={(x['Axis'],x['cut_story']):x for x in rows(SRC/'finite300-signed-sumB-versus-mass-above-24.csv')};errsum=[]
for x in sums:
    y=targetsum[x['Axis'],x['cut_story']]
    for a,b in [('mass_above_kg','identified_mass_above_kg'),('sum_signed_300_B_kg','sum_signed_300_B_inertia_projection_kg_not_fullFE_elastic'),('difference_kg','sum_B_minus_mass_above_kg'),('sum_abs_300_B_kg','sum_abs_300_B_kg')]:
        er=abs(x[a]-float(y[b]));assert er<1e-5;errsum.append(er)
    assert x['negative_modes']==int(y['negative_B_modes_count'])
targetq={int(x['Mode']):x for x in rows(SRC/'modes2-10-13-coordinate-identifiability-3.csv')};errq=[]
for x in coord:
    y=targetq[x['Mode']]
    for a,b in [('distance_to_rowspace','distance_e_to_rowspace'),('rowspace_leverage','rowspace_leverage'),('null_direction_mode_component','nullspace_vector_mode_component')]:
        er=abs(x[a]-float(y[b]));assert er<1e-12;errq.append(er)
v2=S/'roles/role6/R003/wording-v002-manifest.json';mathmanifest=json.loads(v2.read_text(encoding='utf-8'))
assert sha(v2.parent/mathmanifest['primary_report'])==mathmanifest['sha256']
save('checks.json',{'completed':now().isoformat(),'B_rows':72,'max_abs_B_error_kg':max(errB),'sumB_rows':24,'sumB_scalar_comparisons':len(errsum),'max_abs_sumB_related_scalar_error_kg':max(errsum),'coordinate_modes':3,'coordinate_scalar_comparisons':len(errq),'max_coordinate_scalar_difference':max(errq),'rank':rank,'nullity':300-rank,'worst_finite_mass_closure':max(sums,key=lambda x:abs(x['relative_difference'])),'numeric_must_count':0,'theory_report_sha256':mathmanifest['sha256'],'no_role4_code_imported':True,'no_new_ODE_or_mass_identification':True,'not_certified':'Ritz full-space eigen equation; target elastic force recovery; actual FNA q; dynamics-informed time observability'})
print(json.dumps(json.loads((O/'checks.json').read_text(encoding='utf-8')),ensure_ascii=False))
