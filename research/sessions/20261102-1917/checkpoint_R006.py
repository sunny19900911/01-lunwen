"""Publish accepted scientific v003 and user-readable notes; Word remains active."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,ast
S=Path(__file__).resolve().parent;R=S.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=S/'status.json';status=json.loads(p.read_text(encoding='utf-8'));assert not status['checkpoint_open']
status['checkpoint_open']=True;status['checkpoint']='R006';status['checkpoint_started_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['status.json','threads.json','runs.md','next-task.md','root-v003-final-source-acceptance.json','check_final_p06_word.py','普通中文研究说明.md','投稿前待办.md','final-summary-prepared-v001.md','checkpoint_R006.py','roles/role5/R004/v002-to-v003.diff','roles/role5/R004/v003-identity.json']
paths=[S/n for n in names];paper=R/'papers/damping-output-boundaries/manuscript/p06-engineering-session022-v003.md';assert sha(paper)=='b546eb7e9afe6dfde8f8bc57f705ee6e283b60141000a408965d39921fffdac3';paths.append(paper)
items=[]
for x in paths:
 b=x.read_bytes()
 if x.suffix=='.py':ast.parse(b.decode('utf-8'))
 if x.suffix=='.json':json.loads(b.decode('utf-8'))
 items.append({'relative':x.relative_to(R).as_posix(),'sha256':sha(x)})
cfg={'checkpoint':'R006','message':'P06 session022: freeze final scientific manuscript and engineering guidance','files':items,'checks':['Final v003 matches root preapproved three-paragraph contract and exact SHA','Root exact diff read; figures, tables, formulas, references and appendix unchanged','Readable engineering summary and real submission pending items reviewed','Summary remains explicitly prepared, not a completion assertion','Word candidate and active authoring files excluded until freeze and actual QA','Root Word gate geometry checks prepared, no final Word check claimed']}
mp=S/'git-R006-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=json.loads((S/'git-R006-receipt.json').read_text(encoding='utf-8'));status['checkpoint_open']=False;status['git']={'last_checkpoint':'R006','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local']};p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
