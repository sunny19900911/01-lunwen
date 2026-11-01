from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
O=Path(__file__).resolve().parent;S=O.parents[2];A=S/'roles/role2/R004';P=S/'roles/role6/R002'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((A/'manifest.json').read_text(encoding='utf-8'));producer=json.loads((P/'freeze.json').read_text(encoding='utf-8'));own=json.loads((O/'input-method-rules-freeze.json').read_text(encoding='utf-8'))
assert audit['status']=='frozen' and audit['must_fix']==0 and sha(P/'freeze.json')==audit['producer_freeze_sha256']
assert all(sha(A/d['name'])==d['sha256'] for d in audit['artifacts'])
interface=P/'assembled-v001/static-interface.json';actual=sha(interface);assert actual==producer['files']['assembled-v001/static-interface.json']['sha256']==own['inputs'][0]['sha256']
paths=[A/'manifest.json',A/'one-page.md',P/'freeze.json',interface,O/'delivery-manifest.json',O/'prediction-and-envelope-freeze.json']
output=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),static_audit_conclusion='passed, 0 must-fix; full report read by producer',audit_frozen_at=audit['frozen_at'],audited_interface_matches_used_interface=True,interface_sha256=actual,new_target_state_solves=0,target_response_reads=0,scope='static M/K/eigen/cut only; no dynamic accuracy or OpenSees equivalence claim',prediction_bytes_unchanged=True,bindings=[dict(path=str(p),sha256=sha(p)) for p in paths])
with (O/'static-audit-clearance-addendum-v001.json').open('x',encoding='utf-8') as f:json.dump(output,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(output,ensure_ascii=False,indent=2))
