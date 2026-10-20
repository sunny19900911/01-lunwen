from pathlib import Path
import csv,json,math
S=Path(__file__).resolve().parent
def rows(f):
 with (S/'roles/role4'/f).open(encoding='utf-8-sig',newline='') as a:return list(csv.DictReader(a))
sf=rows('R001-story-forces-72.csv');dr=rows('R001-story-drifts-144.csv');ct=rows('R001-main-axis-controls-6.csv');mo=rows('R001-first-three-modal-summary.csv')
assert (len(sf),len(dr),len(ct),len(mo))==(72,144,6,9)
for c in ct:
 case=c['Case'];axis=c['Axis'];a=max((x for x in sf if x['Case']==case),key=lambda x:float(x['V'+axis+'_peak_abs']));b=max((x for x in dr if x['Case']==case and x['Axis']==axis),key=lambda x:float(x['Drift_peak_abs']))
 assert a['Story']==c['QT_control_Story'] and math.isclose(float(a['V'+axis+'_peak_abs']),float(c['QT_peak_kN']),rel_tol=1e-12)
 assert b['Story']==c['Drift_control_Story'] and math.isclose(float(b['Drift_peak_abs']),float(c['Drift_peak_ratio']),rel_tol=1e-12)
assert all(x['exact_base_grid']=='True' for x in sf)
assert all(x['all_times_in_base_grid']=='True' and 0<float(x['coverage_fraction'])<=1 for x in dr)
base={x['mode']:x for x in mo if x['model']=='baseline_label0'};diffs=[]
for x in mo:
 b=base[x['mode']];diffs.append({'model':x['model'],'mode':x['mode'],'relative_period_difference':abs(float(x['period_s'])/float(b['period_s'])-1),'max_abs_participation_ratio_difference':max(abs(float(x[k])-float(b[k])) for k in ['mass_ratio_UX','mass_ratio_UY','mass_ratio_RZ'])})
out={'pass':True,'scope':'Independent cross-table aggregation and first3 native-summary comparison, not raw-array recomputation or node-mode proof','counts':{'shear':72,'drift':144,'controls':6,'modal':9},'controls_consistent':True,'period_and_mass_comparisons':diffs,'exact_native_modal_decomposition_claimed':False}
(S/'R001-root-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps({'pass':True,'max_relative_period_difference':max(x['relative_period_difference'] for x in diffs),'max_abs_mass_ratio_difference':max(x['max_abs_participation_ratio_difference'] for x in diffs)},ensure_ascii=False))
