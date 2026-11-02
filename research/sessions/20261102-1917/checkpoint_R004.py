"""Publish the completed final reviews, not the active Word preparation."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,ast
S=Path(__file__).resolve().parent;R=S.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=S/'status.json';status=json.loads(p.read_text(encoding='utf-8'));assert not status['checkpoint_open']
status['checkpoint_open']=True;status['checkpoint']='R004';status['checkpoint_started_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['status.json','threads.json','runs.md','next-task.md','final-review-adoption-v001.md','check_final_p06_word.py','checkpoint_R004.py','roles/role3/R002/final-reference-and-bilingual-audit.md','roles/role3/R002/checks.json','roles/role3/R002/freeze.json','roles/role6/R002/final-reader-review.md','roles/role6/R002/freeze.json']
paths=[S/n for n in names]
mp=S/'roles/role2/R003/delivery-manifest.json';d=json.loads(mp.read_text(encoding='utf-8'));paths.append(mp)
for q in d['files']:
 x=Path(q['path']);assert x.is_relative_to(S) and sha(x)==q['sha256'];paths.append(x)
items=[]
for x in dict.fromkeys(paths):
 b=x.read_bytes()
 if x.suffix=='.py':ast.parse(b.decode('utf-8'))
 if x.suffix=='.json':json.loads(b.decode('utf-8'))
 items.append({'relative':x.relative_to(R).as_posix(),'sha256':sha(x)})
cfg={'checkpoint':'R004','message':'P06 session022: complete correctness, source and engineering final reviews','files':items,'checks':['Root fully read all three formal reviews','All three reviews zero must changes; adopt only three wording replacements from engineering review','502 displayed numeric fields matched in final content check','Ten references and bilingual scope verified with primary source package','Word identity gate prepared and syntax checked only, not yet run against a Word document','Active sole-author Word-preparation files excluded; no DOCX or QA completion claimed']}
mp=S/'git-R004-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=json.loads((S/'git-R004-receipt.json').read_text(encoding='utf-8'));status['checkpoint_open']=False;status['git']={'last_checkpoint':'R004','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local']};p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
