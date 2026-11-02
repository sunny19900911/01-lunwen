"""Freeze the fully read v002 as a final-review candidate, excluding active work."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,ast
S=Path(__file__).resolve().parent;R=S.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=S/'status.json';status=json.loads(p.read_text(encoding='utf-8'));assert not status['checkpoint_open']
status['checkpoint_open']=True;status['checkpoint']='R003';status['checkpoint_started_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['status.json','threads.json','runs.md','next-task.md','rounds/R002.md','root-v002-editorial-review.md','checkpoint_R003.py','roles/role5/R002/freeze.json','roles/role5/R002/changes-and-sources.md','roles/role5/R002/engineering-data-and-full-tables.md','roles/role5/R002/QA.json','roles/role5/R002/build-report.json']
paths=[S/n for n in names]
paper=R/'papers/damping-output-boundaries/manuscript/p06-engineering-session022-v002.md';assert sha(paper)=='b3a86796c990bcb7d80ce74c7e343a6eb24ef2931581f5853652a9f3f3a60cde';paths.append(paper)
items=[]
for x in paths:
 b=x.read_bytes()
 if x.suffix=='.py':ast.parse(b.decode('utf-8'))
 if x.suffix=='.json':json.loads(b.decode('utf-8'))
 items.append({'relative':x.relative_to(R).as_posix(),'sha256':sha(x)})
cfg={'checkpoint':'R003','message':'P06 session022: integrate reviewed engineering records into complete draft','files':items,'checks':['Root full read v002 and supplementary engineering table','New numeric content already independently reviewed in role2 R002','Eight representative records and 24 full groups use same-case paired peaks','Three source-verified neighbours integrated, ten references with actual text use','Final content/source/wording reviews in progress, version is candidate not delivered Word','Active review and Word-preparation files deliberately excluded']}
mp=S/'git-R003-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=json.loads((S/'git-R003-receipt.json').read_text(encoding='utf-8'));status['checkpoint_open']=False;status['git']={'last_checkpoint':'R003','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local']};p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
