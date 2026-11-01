from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib,json,csv

O=Path(__file__).resolve().parent; S=O.parents[2]
start=datetime.fromisoformat('2026-11-02T00:28:52.367001+08:00')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readrows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
a=json.loads((O/'independent-results.json').read_text()); b=json.loads((O/'production-comparison.json').read_text())
assert a['floors']==39 and a['modal_own_peak_rows']==10836
assert b['main_numeric_fields_checked']==546 and b['modal_numeric_fields_checked']==285
assert b['must_fix_items']==0 and b['all_unit_and_controller_times_match']
for name,count in [('independent-baseline-U-C-rates-39.csv',39),('independent-SHW3X-priority-2.csv',2),
                   ('selected-own-modal-peak-vs-total-peak-234.csv',234),('independent-modal-own-peak-rates-10836.csv',10836)]:
    assert len(readrows(O/name))==count
R=S/'roles/role1/R007'; rp=R/'manifest.json'
assert sha(rp)=='b5a1fb775af6c7c49c347146d25c83d83add230bb7a509e7b87b1bd1145e07b0'
for d in json.loads(rp.read_text(encoding='utf-8'))['files']:
    p=Path(d['path']); assert sha(p)==d['sha256'] and p.stat().st_size==d['bytes']
for name in ['one-page-independent-baseline-UC-audit.md','author-ready-baseline-UC-wording.md']:
    t=(O/name).read_text(encoding='utf-8'); assert len(t)>500 and '�' not in t
now=datetime.now(timezone(timedelta(hours=8)))
result={'task':'session021-role2-R012','actual_start':start.isoformat(),'actual_freeze':now.isoformat(),
 'elapsed_seconds':(now-start).total_seconds(),'within12min':(now-start).total_seconds()<=720,
 'within15min':(now-start).total_seconds()<=900,'must_fix_items':0,
 'independent_before_new_results_read':True,'comparison_passed':True,
 'new_ODE':0,'new_target_response_arrays':0,'old8pct_response_read':False,
 'role1_manifest_sha256':sha(rp),'role4_manifest_sha256':b['producer_manifest_sha256'],
 'numerical_scope':'fixed saved grid, double precision; local right derivatives only',
 'files':[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']}
with (O/'delivery-manifest.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in result.items() if k!='files'},ensure_ascii=False,indent=2))
print('manifest_sha256',sha(O/'delivery-manifest.json'))
print('manifest_file_count',len(result['files']))
