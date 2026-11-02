"""Publish explicit, already read frozen method/review artifacts, not pending data."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,ast
S=Path(__file__).resolve().parent;R=S.parents[2]
p=S/'status.json';status=json.loads(p.read_text(encoding='utf-8'))
assert not status['checkpoint_open']
status['checkpoint_open']=True;status['checkpoint']='R001'
status['checkpoint_started_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['status.json','threads.json','runs.md','next-task.md','topic-card-v001.md','root-R001-method-contract.md','root-R001-old-number-adoption.md','root-R001-method-and-source-adoption.md','publish_checkpoint.py','checkpoint_R001.py',
'roles/role1/R001/two-control-engineering-review-one-page.md','roles/role1/R001/engineering-review-contract.json','roles/role1/R001/review-table-header.csv','roles/role1/R001/manifest.json','roles/role1/R001/audit-clarification-v001/selector-scope.md',
'roles/role2/R001/one-page-independent-review.md','roles/role2/R001/engineering-contract-and-audit-checklist.md','roles/role2/R001/delivery-manifest.json','roles/role2/R001/independent-old-scalar-checks.json',
'roles/role3/R001/journal-and-literature-audit.md','roles/role3/R001/introduction-revision-note.md','roles/role3/R001/freeze.json',
'roles/role6/R001/one-page-software-review-workflow.md','roles/role6/R001/p06-engineering-review-notes.md','roles/role6/R001/freeze.json']
items=[]
for name in names:
 f=S/name;b=f.read_bytes()
 if f.suffix=='.py':ast.parse(b.decode('utf-8'))
 if f.suffix=='.json':json.loads(b.decode('utf-8'))
 items.append({'relative':f.relative_to(R).as_posix(),'sha256':hashlib.sha256(b).hexdigest()})
cfg={'checkpoint':'R001','message':'P06 session022: adopt dual-control engineering review and verified sources','files':items,'checks':['Root fully read role1/2/3/6 frozen reports and contracts','Old 168 scalar checks independently reviewed by role2','New 24-row science still pending role2 R002, deliberately excluded','Official full template in local-cache excluded','Header-only CSV deliberately represents a schema, not numeric evidence','Publisher adjustment allows valid schema CSV; no Git semantics changed']}
mp=S/'git-R001-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=json.loads((S/'git-R001-receipt.json').read_text(encoding='utf-8'))
status['checkpoint_open']=False;status['git']={'last_checkpoint':'R001','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local']}
p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
