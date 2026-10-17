from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
p=ROOT/'research/sessions/20261017-2109/fixed-dissipation-peak-inverse-protocol-v001.md'
b=p.read_bytes()
out={'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'started_at':'2026-10-18T04:26:58+08:00','deadline':'2026-10-18T04:36:58+08:00','global_deadline':'2026-10-18T07:09:45+08:00','protocol':{'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()},'independence':'Before reading role1 R029 candidate; no role1 in-progress files will be read before independent freeze.'}
target=HERE/'protocol-freeze.json';assert not target.exists()
target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(out,ensure_ascii=False))
