import os
os.environ['OPENBLAS_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np

O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130';SOURCE=S/'roles/role4/R002'
START=datetime.fromisoformat('2026-10-31T11:59:43+08:00');DEADLINE=START+timedelta(minutes=12)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate():
    if now()>=DEADLINE:raise RuntimeError('R003 deadline')
def save(n,x):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def table(n,x):
    with (O/n).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(x[0]),lineterminator='\n');w.writeheader();w.writerows(x)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

gate();manifest=json.loads((SOURCE/'delivery-manifest.json').read_text(encoding='utf-8'))
for e in manifest['outputs']:
    p=SOURCE/e['name'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
# Only two scientific inputs here; deliberately do not open the old mass join.
ce=next(x for x in manifest['inputs'] if x['path'].endswith('controlled_small_tables.json'))
ae=next(x for x in manifest['inputs'] if x['path'].endswith('CM-signed-all300-5400.csv'))
for e in (ce,ae):
    p=Path(e['path']);assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
small=json.loads(Path(ce['path']).read_text(encoding='utf-8'));cm=readcsv(Path(ae['path']))
assert len(cm)==5400
keys=sorted({(int(x['Story'].removeprefix('Story')),x['Diaphragm']) for x in cm})
assert len(keys)==18
key_index={('Story'+str(st),di):j for j,(st,di) in enumerate(keys)}
pf_table=small['Modal Participation Factors'];ph=pf_table[1][1];pu=pf_table[2][1]
mu_table=small['Modal Participating Mass Ratios'];mh=mu_table[1][1]
assert pu[ph.index('ModalMass')]=='kN-m-s²'
assert pu[ph.index('UX')]==pu[ph.index('UY')]=='kN-m'
pf={int(row[ph.index('Mode')]):(source,row) for source,row in pf_table[3:] if row[ph.index('Case')]=='Modal'}
mu={int(row[mh.index('Mode')]):(source,row) for source,row in mu_table[3:] if row[mh.index('Case')]=='Modal'}
assert sorted(pf)==sorted(mu)==list(range(1,301))
A={d:np.full((300,18),np.nan) for d in ('X','Y')};seen=set()
for x in cm:
    i=int(x['Mode'])-1;j=key_index[x['Story'],x['Diaphragm']]
    assert (i,j) not in seen;seen.add((i,j))
    assert x['OutputCase']=='Modal' and x['CaseType']=='LinModRitz' and x['StepType']=='Mode'
    for d in ('X','Y'):
        # Fixed declared mm->m conversion; converted cache columns only checked, not used to choose a scale.
        val=float(x['U'+d+'_native_mm'])*.001
        assert np.isclose(val,float(x['U'+d+'_converted_m']),rtol=2e-15,atol=1e-22)
        A[d][i,j]=val
assert all(np.isfinite(a).all() for a in A.values())
modal_mass=np.array([float(pf[k][1][ph.index('ModalMass')])*1000 for k in range(1,301)])
assert np.all(modal_mass>0)
svrows=[];massrows=[];moderows=[];summaries={};weights={};totals={}
for d in ('X','Y'):
    gate();f=np.array([float(pf[k][1][ph.index('U'+d)]) for k in range(1,301)])
    participation=np.array([float(mu[k][1][mh.index('U'+d)]) for k in range(1,301)])
    assert np.all((participation>=0)&(participation<=1))
    ref=int(np.argmax(abs(f[:100])));assert f[ref]!=0
    H=A[d]-(f/f[ref])[:,None]*A[d][ref]
    _,sv,Vt=np.linalg.svd(H[:100],full_matrices=False)
    tol=np.finfo(float).eps*max(H[:100].shape)*sv[0]
    rank=int(np.sum(sv>tol));rankrel=int(np.sum(sv>1e-10*sv[0]))
    assert rank==rankrel==17
    w=Vt[-1]/sum(Vt[-1]);assert np.all(w>0) and abs(sum(w)-1)<1e-14
    projection=A[d]@w;res=H@w;train_scale=float(np.max(abs(projection[:100])))
    # A predeclared training-only projection scale controls reporting flags, never weights or mode removal.
    stable=(abs(projection)>1e-10*train_scale)&(participation>0)
    estimates=np.full(300,np.nan);estimates[stable]=participation[stable]*modal_mass[stable]/projection[stable]**2
    assert np.all(stable)
    total=float(np.median(estimates[:100]));assert total>0
    weights[d]=w;totals[d]=total
    for i,singular in enumerate(sv):svrows.append({'direction':d,'singular_index':i+1,'singular_value':float(singular),'relative_to_max':float(singular/sv[0]),'rank_tolerance':float(tol)})
    for j,(story,diaphragm) in enumerate(keys):massrows.append({'direction':d,'Story':'Story'+str(story),'Diaphragm':diaphragm,'weight':float(w[j]),'identified_mass_kg':float(total*w[j]),'training_total_mass_kg':total})
    for i in range(300):
        moderows.append({'direction':d,'Mode':i+1,'split':'train' if i<100 else 'holdout','PF_native_signed':float(f[i]),'mu':float(participation[i]),'ModalMass_kg_m2':float(modal_mass[i]),'CM_weighted_projection_m':float(projection[i]),'H_residual_m':float(res[i]),'residual_over_train_max_projection':float(res[i]/train_scale),'stable':bool(stable[i]),'total_mass_estimate_kg':float(estimates[i]),'relative_mass_error_vs_train_median':float(estimates[i]/total-1)})
    summaries[d]={'reference_mode_train':ref+1,'reference_also_global':int(np.argmax(abs(f)))==ref,'rank_train100':rank,'rank_relative1e-10':rankrel,'nullity':18-rank,'sigma17':float(sv[-2]),'sigma18':float(sv[-1]),'nonnull_condition':float(sv[0]/sv[-2]),'minimum_weight':float(min(w)),'positive_weights':int(sum(w>0)),'total_mass_train_median_kg':total,'holdout_max_H_residual_over_train_projection':float(np.max(abs(res[100:]))/train_scale),'holdout_total_mass_min_kg':float(min(estimates[100:])),'holdout_total_mass_max_kg':float(max(estimates[100:])),'holdout_max_relative_mass_error':float(max(abs(estimates[100:]/total-1))),'stable_total_estimates':int(sum(stable))}
# Seal identification before any old masses or role4 identified-mass numeric table is parsed.
table('independent-identification-before-comparison-36.csv',massrows)
table('independent-singular-values-36.csv',svrows)
table('independent-mode-checks-600.csv',moderows)
save('early-independent-results.json',{'completed':now().isoformat(),'directions':summaries,'no_old_mass_file_read':True,'no_role4_scientific_result_table_parsed':True,'method_note':'source README was seen during preflight; solver uses only CM, PF ratios, mu, ModalMass, declared unit factors; no previous mass values enter calculations','ModalMass_conversion':'kN*m*s^2 *1000 = kg*m^2; generalized inertia of exported modal displacement, not effective modal mass','CM_conversion':'raw mm *0.001 = m, applied identically to all modes, no fitted gain','sources_used':[ce,ae]})
gate()
observed=np.sum((A['X']**2)*(totals['X']*weights['X'])[None,:],axis=1)+np.sum((A['Y']**2)*(totals['Y']*weights['Y'])[None,:],axis=1)
fractions=observed/modal_mass
selected=[{'Mode':k,'observed_XY_generalized_mass_kg_m2':float(observed[k-1]),'source_ModalMass_kg_m2':float(modal_mass[k-1]),'observed_fraction':float(fractions[k-1])} for k in (2,10,13)]
table('observed-generalized-mass-selected-3.csv',selected)
save('observed-generalized-mass-summary.json',{'computed_at':now().isoformat(),'min_fraction_all300':float(min(fractions)),'max_fraction_all300':float(max(fractions)),'max_mode':int(np.argmax(fractions))+1,'greater_than_one_count_with_1e-10_tolerance':int(sum(fractions>1+1e-10)),'warning':'XY point-mass observation diagnostic only; not a proof of full FE mass inner product, full modal observability, Eigen cut recovery, or FNA coordinate reconstruction'})
print(json.dumps({'completed':now().isoformat(),'independent_identification_saved':True,'directions':summaries,'selected_Gobs':selected},ensure_ascii=False))
