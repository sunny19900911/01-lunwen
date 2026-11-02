"""Release frozen, independently reviewed engineering scalars and the read v001."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,ast
S=Path(__file__).resolve().parent;R=S.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=S/'status.json';status=json.loads(p.read_text(encoding='utf-8'));assert not status['checkpoint_open']
status['checkpoint_open']=True;status['checkpoint']='R002';status['checkpoint_started_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['status.json','threads.json','runs.md','claims.md','next-task.md','root-v001-editorial-review.md','root-R002-new-table-adoption.md','root-R002-reviewed-small-source-check.json','verify_reviewed_sources.py','checkpoint_R002.py','roles/role5/R001/freeze.json','roles/role5/R001/one-page.md','roles/role5/R001/descriptive-three-model-comparison.md']
paths=[S/n for n in names]
for name in ['roles/role4/R001/delivery-manifest.json','roles/role4/R001/delivery-manifest-v002.json','roles/role2/R002/delivery-manifest.json']:
 mp=S/name;d=json.loads(mp.read_text(encoding='utf-8'));paths.append(mp)
 for q in d.get('files',[])+d.get('additive_files',[]):
  x=Path(q['path']);assert x.is_relative_to(S) and sha(x)==q['sha256'];paths.append(x)
paper=R/'papers/damping-output-boundaries/manuscript/p06-engineering-session022-v001.md';assert sha(paper)=='70c831f0a01b19476bc090d85f874468ecffcef5d612379e2c56d0a22bf96e24';paths.append(paper)
paths=list(dict.fromkeys(paths));items=[]
for x in paths:
 b=x.read_bytes()
 if x.suffix=='.py':ast.parse(b.decode('utf-8'))
 if x.suffix=='.json':json.loads(b.decode('utf-8'))
 items.append({'relative':x.relative_to(R).as_posix(),'sha256':sha(x)})
cfg={'checkpoint':'R002','message':'P06 session022: independently verify dual-control engineering table and draft','files':items,'checks':['Role2 R002 independent selections saved before reading producer table','6415 field checks including 3625 numeric/display checks, zero must corrections','Root full read producer report, 24-row Markdown, method, metadata and independent report','Root hash/AST/CSV gate verified 25 frozen small files; original P06 unchanged','v001 root full read, clearly initial draft; active v002 excluded','Only scalar processed tables; no trajectories, raw model, template, external fulltext, local-cache or comparison directory']}
mp=S/'git-R002-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=json.loads((S/'git-R002-receipt.json').read_text(encoding='utf-8'));status['checkpoint_open']=False;status['git']={'last_checkpoint':'R002','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local']};p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
