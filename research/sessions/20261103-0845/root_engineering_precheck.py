from pathlib import Path
import csv,json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];H=R/'research/handoffs/p06-sh3-sh4-20261103'
rows=list(csv.DictReader((H/'story5-reference-checks-4.csv').open(encoding='utf-8-sig')))
modes=list(csv.DictReader((H/'story5-all300-signed-reference-1200.csv').open(encoding='utf-8-sig')))
assert len(rows)==4 and len(modes)==1200
out=[]
for case in ['SHW3X','SHW4X']:
 pair=sorted([r for r in rows if r['Case']==case],key=lambda x:float(x['zeta']));assert len(pair)==2
 base,ref=pair;pb=float(base['native_peak_abs_kN']);pm=float(ref['native_peak_abs_kN'])
 for r in pair:
  group=[x for x in modes if x['Case']==case and float(x['zeta'])==float(r['zeta'])];assert len(group)==300
  vals=[float(x['reference_signed_shear_kN']) for x in group]
  assert abs(sum(vals)-float(r['reference_at_native_peak_signed_kN']))<1e-8
  assert abs(sum(vals[:3])-float(r['reference_modes1to3_kN']))<1e-8
  assert abs(sum(vals[3:])-float(r['reference_modes4to300_kN']))<1e-8
 out.append({'input':case,'PB_kN':pb,'PM_kN':pm,'paired_reduction_percent':100*(1-pm/pb),'tB_s':float(base['native_peak_time_s']),'tM_s':float(ref['native_peak_time_s']),'scope':'Observed paired software peak; mechanism table is conditional reference.'})
report={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'rows':out,'sum_checks':{'four_states_300_term_sum':True,'no_new_ODE':True},'engineering_reading':'SHW3X has smaller paired reduction but SHW4X greater PM. Do not assign SHW3 reduction to SHW4 PM. Conditional mechanism comparison does not replace this direct output decision.','status':'Root arithmetic precheck; independent audit in progress.'}
(S/'root-R001-engineering-precheck.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
