from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[4];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((H/'numeric-delivery-manifest.json').read_text(encoding='utf-8'))
for q in old['files']:assert sha(R/q['relative'])==q['sha256']
paths=[H/'numeric-delivery-manifest.json',H/'root-cross-check.json',H/'check_against_root.py',Path(__file__)]
d={'status':'complete-item1-numerics','at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'numeric_manifest_preserved':True,'root_36_fields_exact_match':True,'plot_owner':'root; no duplicate plot produced','item2_or_3_started':False,'files':old['files']+[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in paths]}
p=H/'delivery-manifest.json';assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':d['status'],'files':len(d['files']),'at':d['at']},ensure_ascii=False))
