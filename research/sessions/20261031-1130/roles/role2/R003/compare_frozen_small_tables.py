from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np
O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130';SRC=S/'roles/role4/R002'
now=lambda:datetime.now(timezone(timedelta(hours=8)))
assert now()<datetime.fromisoformat('2026-10-31T12:11:43+08:00')
def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(n,x):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
early=json.loads((O/'early-independent-results.json').read_text(encoding='utf-8'))
assert early['no_old_mass_file_read'] and early['no_role4_scientific_result_table_parsed']
own=readcsv(O/'independent-identification-before-comparison-36.csv')
delivered={(x['Axis'],x['Story'],x['Diaphragm']):x for x in readcsv(SRC/'identified-masses-before-old-comparison-36.csv')}
manifest=json.loads((SRC/'delivery-manifest.json').read_text(encoding='utf-8'))
oldentry=next(e for e in manifest['inputs'] if e['path'].endswith('old-CM-mass-coordinate-new-mode-key-join-18.csv'))
p=Path(oldentry['path']);assert p.stat().st_size==oldentry['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==oldentry['sha256']
legacy={(x['Story'],x['Diaphragm']):x for x in readcsv(p)}
comparison=[];massdiff=[];weightdiff=[];olddiff=[]
for x in own:
    d=x['direction'];y=delivered[d,x['Story'],x['Diaphragm']];old=legacy[x['Story'],x['Diaphragm']]
    m=float(x['identified_mass_kg']);w=float(x['weight']);my=float(y['identified_mass_kg']);wy=float(y['identified_relative_mass']);mo=float(old['old_Mass'+d+'_kg'])
    assert abs(m-my)<1e-10*max(1,abs(my)) and abs(w-wy)<1e-13
    massdiff.append(abs(m-my));weightdiff.append(abs(w-wy));olddiff.append(abs(m/mo-1))
    comparison.append({'direction':d,'Story':x['Story'],'Diaphragm':x['Diaphragm'],'independent_mass_kg':m,'delivered_mass_kg':my,'old_mass_kg_comparison_only':mo,'abs_independent_vs_delivered_kg':abs(m-my),'relative_vs_old':m/mo-1})
with (O/'post-identification-comparison-36.csv').open('x',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(comparison[0]),lineterminator='\n');w.writeheader();w.writerows(comparison)
obs={int(x['Mode']):x for x in readcsv(SRC/'observed-XY-generalized-mass-check-300.csv')}
observed_diff=[]
for x in readcsv(O/'observed-generalized-mass-selected-3.csv'):
    ref=obs[int(x['Mode'])];e=abs(float(x['observed_fraction'])-float(ref['observed_XY_over_native_mr']))
    assert e<1e-12;observed_diff.append(e)
mode=readcsv(O/'independent-mode-checks-600.csv');diag={}
for d in ('X','Y'):
    rr=[x for x in mode if x['direction']==d];total=early['directions'][d]['total_mass_train_median_kg']
    native_over_projection=np.array([float(x['PF_native_signed'])/float(x['CM_weighted_projection_m']) for x in rr])
    c=float(np.median(native_over_projection[:100]))
    # Diagnostic only. Neither this constant nor its sign was used to form H, weights or total mass.
    f_over_S=native_over_projection/total
    diag[d]={'PF_native_over_CM_projection_train_median':c,'holdout_max_relative_deviation_from_train_constant':float(max(abs(native_over_projection[100:]/c-1))),'PF_native_over_identified_S_SI_min':float(min(f_over_S)),'PF_native_over_identified_S_SI_max':float(max(f_over_S)),'diagnostic_only_not_a_fitted_SI_gain':True,'raw_PF_not_relabelled_Gamma':True}
smallentry=next(e for e in manifest['inputs'] if e['path'].endswith('controlled_small_tables.json'))
small=json.loads(Path(smallentry['path']).read_text(encoding='utf-8'))
pf=small['Modal Participation Factors'];mu=small['Modal Participating Mass Ratios'];ph=pf[1][1];mh=mu[1][1]
period_pf={int(x[ph.index('Mode')]):float(x[ph.index('Period')]) for _,x in pf[3:]}
period_mu={int(x[mh.index('Mode')]):float(x[mh.index('Period')]) for _,x in mu[3:]}
assert period_pf==period_mu
save('unit-and-scale-diagnostics.json',{'completed':now().isoformat(),'source_period_matches_all300':True,'PF_native_units':pf[2][1][ph.index('UX')],'ModalMass_native_units':pf[2][1][ph.index('ModalMass')],'ModalMass_SI_unit':'kg*m^2, not kg','ModalMass_fixed_conversion':1000,'CM_native_unit':'mm','CM_fixed_conversion_to_m':.001,'directions':diag,'interpretation':'CM/PF/modal mass same-mode relative normalization is strongly consistent. Absolute signed load convention behind native PF is not certified as Gamma. Derived PF/S diagnostics are never used as adjustable conversion factors.'})
save('comparison-checks.json',{'completed':now().isoformat(),'implementation_must_count':0,'identified_mass_comparisons':36,'max_abs_mass_difference_vs_role4_kg':max(massdiff),'max_weight_difference_vs_role4':max(weightdiff),'max_relative_difference_vs_old_posthoc':max(olddiff),'selected_observed_generalized_mass_comparisons':3,'max_observed_fraction_difference':max(observed_diff),'old_mass_first_read_after_own_saved_identification':True,'old_mass_used_to_estimate_weights_or_totals':False,'role4_scientific_code_imported':False,'no_ODE_or_large_response_arrays':True})
print(json.dumps(json.loads((O/'comparison-checks.json').read_text(encoding='utf-8')),ensure_ascii=False))
print(json.dumps(diag,ensure_ascii=False))
