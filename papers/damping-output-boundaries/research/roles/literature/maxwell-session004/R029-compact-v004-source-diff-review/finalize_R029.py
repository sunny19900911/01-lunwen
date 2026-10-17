from pathlib import Path
import json, hashlib
from datetime import datetime, timezone, timedelta

base = Path(__file__).resolve().parent
def sha(p):
    b=p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}
def put(name,obj):
    (base/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
inputs=json.loads((base/'input-rules-R029.json').read_text(encoding='utf-8'))
checks=json.loads((base/'checks-R029.json').read_text(encoding='utf-8'))
assert len(checks['checks'])==133 and all(x['pass'] for x in checks['checks'])
now=datetime.now(timezone(timedelta(hours=8)))
deadline=datetime.fromisoformat(inputs['deadline'])
report=(base/'report.md').read_bytes()
assert report.decode('utf-8') and b'\r' not in report and not report.startswith(b'\xef\xbb\xbf')
validation={'scope':'source attribution, provenance and text/diff integration; mathematical correctness separately reviewed by role2','must_fix':0,'independent_checks':133,'passed':133,'failed':0,'input_count':len(inputs['inputs']),'last_input_identity_check_at':inputs['snapshot_at'],'finalization_input_rescan':False,'external_urls_opened':0,'binary_media_or_arrays_read':0,'old_underlying_manifest_entries_rehashed':0,'finished_at':now.isoformat(),'deadline':inputs['deadline'],'within_deadline':now < deadline,'late_seconds':max(0,(now-deadline).total_seconds()),'delay_reason':'Report/freeze preparation after context compaction and one path lookup error; no new substantive checks after deadline, no time backdating. Finalization uses already completed checks and input snapshot only.','old_QA_bytes_recovered':False}
put('validation.json',validation)
names=['report.md','validation.json','checks-R029.json','input-rules-R029.json','review_R029.py','finalize_R029.py']
put('freeze.json',{'task':'R029-compact-v004-source-diff-review','status':'frozen; source/diff scope has zero must-fix; awaiting main integration decision','started_at':inputs['started_at'],'frozen_at':now.isoformat(),'deadline':inputs['deadline'],'elapsed_seconds':(now-datetime.fromisoformat(inputs['started_at'])).total_seconds(),'global_deadline':'2026-10-18T07:09:45+08:00','artifacts':[sha(base/n) for n in names]})
print(json.dumps({'frozen_at':now.isoformat(),'elapsed_seconds':(now-datetime.fromisoformat(inputs['started_at'])).total_seconds(),'artifacts':[sha(base/n) for n in names+['freeze.json']]},ensure_ascii=False,indent=2))
