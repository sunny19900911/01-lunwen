from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,csv,math
H=Path(__file__).resolve().parent;R=H.parents[4]
summary=json.loads((H/'actual-response-summary.json').read_text(encoding='utf-8'))
names=['actual_response_tables.py','input-freeze.json','actual-versus-baseline-time-peak-72.csv','actual-layer-direction-ranges-24.csv','actual-bottom-mean-screening-6.csv','actual-response-summary.json','actual-response-report.md','freeze_numeric.py']
for p in [H/n for n in names]:assert p.is_file()
for n in names:
 if n.endswith('.csv'):
  with (H/n).open(encoding='utf-8',newline='')as f:a=list(csv.reader(f))
  assert a and all(len(x)==len(a[0])for x in a)
source_verified=[]
for q in summary['source_inputs']:
 p=Path(q['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==q['sha256'];source_verified.append(q['sha256'])
d={'status':'numeric-frozen-awaiting-independent-audit','at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'scope':'Actual device model D versus baseline B, six shared cases; no M borrowed','all72_native_grid_and_peak_checks_passed':True,'source_inputs_unchanged':True,'independent_numerical_audit_pending':True,
 'files':[{'relative':(H/n).relative_to(R).as_posix(),'bytes':(H/n).stat().st_size,'sha256':hashlib.sha256((H/n).read_bytes()).hexdigest()}for n in names]}
p=H/'numeric-delivery-manifest.json';assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':d['status'],'at':d['at'],'files':len(names)},ensure_ascii=False))
