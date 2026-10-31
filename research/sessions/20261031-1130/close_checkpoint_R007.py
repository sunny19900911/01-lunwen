from pathlib import Path
from datetime import datetime,timezone,timedelta
import json
S=Path(__file__).resolve().parent
p=S/'status.json';d=json.loads(p.read_text());r=json.loads((S/'git-R007-receipt.json').read_text())
assert r['remote_equals_local'] and d['checkpoint']=='R007-writing'
d.update(checkpoint='R007-complete',checkpoint_open=False,last_actual=datetime.now(timezone(timedelta(hours=8))).isoformat())
d['git'].update(current_HEAD_and_remote=r['HEAD'],last_success_HEAD=r['HEAD'],last_success_receipt='git-R007-receipt.json',publication='R007 normalpush remoteSHAequal; postpublication state')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checkpoint':d['checkpoint'],'HEAD':r['HEAD'],'time':d['last_actual']}))
