from pathlib import Path
from datetime import datetime, timezone, timedelta
import csv, hashlib, json

O=Path(__file__).resolve().parent; S=O.parents[2]; R=S/'roles/role4/R011'
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=R/'delivery-manifest.json'; m=json.loads(manifest.read_text(encoding='utf-8'))
for d in m['files']:
    p=Path(d['path']); assert p.stat().st_size==d['bytes'] and digest(p)==d['sha256']
ind=rows(O/'independent-baseline-U-C-rates-39.csv'); prod=rows(R/'baseline-U-C-local-sensitivity-main-39.csv')
index={(r['Case'],r['Story']):r for r in ind}
aliases={'P0':'P_total_peak','U0':'U_sum_modal_own_peaks','C0':'C_PoverU',
 'Pprime_right':'Pprime_right_force_per_zeta','Uprime_right':'Uprime_right_force_per_zeta',
 'Cprime_right':'Cprime_right_per_zeta','S':'S_percent_per_damping_pp','SU':'SU_percent_per_damping_pp',
 'SC':'SC_percent_per_damping_pp','total_peak_active_count':'total_exact_active_count',
 'total_right_controller_count':'total_right_controller_count','modal_pprime_positive_count':'positive_pprime_modes',
 'modal_pprime_negative_count':'negative_pprime_modes','zero_modal_peak_count':'zero_p_modes'}
diffs={k:0. for k in aliases}; n=0
for r in prod:
    a=index[(r['Case'],r['Story'])]
    assert a['force_unit']==r['force_unit']
    assert a['total_controller_times_s']==r['total_right_controller_times_s']
    for k,v in aliases.items():
        d=abs(float(a[k])-float(r[v])); diffs[k]=max(diffs[k],d); n+=1
        assert d<=1e-9+2e-12*abs(float(a[k])), (r['Case'],r['Story'],k,d)
assert len(prod)==len(ind)==39
modalindex={(r['Case'],r['Story'],r['Mode']):r for r in rows(O/'independent-modal-own-peak-rates-10836.csv')}
modal=rows(R/'selected-mode-own-peak-vs-total-peak-57.csv')
ma={'modal_peak':'p_mode_own_peak','modal_peak_right_derivative':'pprime_mode_own_peak_force_per_zeta',
 'SU_mode_piece':'own_pprime_contribution_to_SU','own_modal_peak_controller_count':'own_right_controller_count',
 'total_peak_c_piece':'c_at_total_peak_percent_per_damping_pp'}
md={k:0. for k in ma}; mn=0
for r in modal:
    a=modalindex[(r['Case'],r['Story'],r['Mode'])]
    assert a['own_modal_peak_controller_times_s']==r['own_right_controller_times_s']
    assert a['total_peak_time_s']==r['total_peak_controller_time_s']
    for k,v in ma.items():
        d=abs(float(a[k])-float(r[v])); md[k]=max(md[k],d); mn+=1
        assert d<=1e-9+2e-12*abs(float(a[k])), (r['Case'],r['Story'],r['Mode'],k,d)
out={'checked_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
 'independent_result_completed_at':json.loads((O/'independent-results.json').read_text())['completed_at'],
 'producer_freeze_at':m['actual_freeze_plus08'],'producer_manifest_sha256':digest(manifest),
 'producer_files_hash_verified':len(m['files']),'main_rows':39,'main_numeric_fields_checked':n,
 'main_max_difference_by_own_field':diffs,'selected_modal_rows':len(modal),'modal_numeric_fields_checked':mn,
 'modal_max_difference_by_own_field':md,'all_unit_and_controller_times_match':True,
 'role1_R007_contract_sha256':digest(S/'roles/role1/R007/baseline-S-UPC-contract.json'),
 'role1_contract_agreement':'own active modal peaks; zero modal p uses max absolute derivative; quotient and product log derivatives; no extra 100; local only',
 'must_fix_items':0,'production_comparison':'pass; algebra on independently frozen baseline inputs only',
 'new_ODE_or_target_response':False}
with (O/'production-comparison.json').open('x',encoding='utf-8') as f: json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps(out,ensure_ascii=False,indent=2))
print('public Story1:',index[('publicExample5_H-E12140','Story1')])
print('private Story5 mode13:',modalindex[('SHW3X','Story5','13')])
