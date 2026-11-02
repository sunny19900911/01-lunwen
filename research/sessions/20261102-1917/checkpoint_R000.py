"""Initial reviewed root-only checkpoint; active role files are excluded."""
from pathlib import Path
import json,hashlib,datetime,subprocess,ast
S=Path(__file__).resolve().parent
R=S.parents[2]
status=json.loads((S/'status.json').read_text(encoding='utf-8'))
assert not status['checkpoint_open']
status['checkpoint_open']=True
status['checkpoint']='R000'
status['checkpoint_started_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
(S/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['initialize.py','plan.md','authorization-evidence.json','claims.md','runs.md','threads.json','status.json','root-R001-method-contract.md','initial-thread-snapshot.json','R001-dispatch-tool-receipts.json','automation-create-tool-receipt.json','automation-actual-readback.json','publish_checkpoint.py','checkpoint_R000.py','rounds/R001-start.md']
files=[]
for name in names:
 p=S/name;b=p.read_bytes()
 if p.suffix=='.py':ast.parse(b.decode('utf-8'))
 if p.suffix=='.json':json.loads(b.decode('utf-8'))
 files.append({'relative':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(b).hexdigest()})
manifest={'checkpoint':'R000','message':'P06 session022: freeze engineering scope and launch six-role review','files':files,'checks':['Root fully read original P06 and final summary','Original MD and adopted DOCX SHA verified','Human new authorization read in original review thread','Root new method contract reviewed; no new science claim','Only root frozen files; no active role outputs','Formal heartbeat create/view and actual configuration verified']}
mp=S/'git-R000-manifest.json'
assert not mp.exists()
mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=subprocess.run([__import__('sys').executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R)
if p.returncode:raise SystemExit(p.returncode)
receipt=json.loads((S/'git-R000-receipt.json').read_text(encoding='utf-8'))
status['checkpoint_open']=False
status['git']={'last_checkpoint':'R000','HEAD':receipt['HEAD'],'pending_push':receipt['pending_push'],'remote_verified':receipt['remote_equals_local']}
(S/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
