from pathlib import Path
import json,datetime
H=Path(__file__).resolve().parent
a=json.loads((H/'actual-cache-audit.json').read_text(encoding='utf-8'))['statistics']
p=json.loads((H.parent/'response/actual-response-summary.json').read_text(encoding='utf-8'))
mapping={'d_median_pp':'d_median_pp','d_95percentile_pp':'d_95_percentile_pp','d_max_pp':'d_max_pp','minimum_d_pp':'d_min_pp','same_peak_time_count':'same_saved_peak_time_count','zero_d_count':'d_zero_count_exact','max_time_shift_s':'max_abs_peak_time_shift_s'}
checks=[]
for k,v in mapping.items():
 e=abs(a[k]-p[v]);assert e<1e-12
 checks.append({'independent_key':k,'producer_key':v,'independent':a[k],'producer':p[v],'abs_difference':e})
assert a['max_d_record']['Case']==p['d_max_record']['Case'] and a['max_d_record']['Story']==p['d_max_record']['Story']
result={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'checks':checks,'must':0,'array_rereads':0}
(H/'aggregate-summary-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
