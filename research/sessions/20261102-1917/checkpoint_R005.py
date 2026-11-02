"""Publish reviewed preparation and the explicit submission-requirement correction."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,ast
S=Path(__file__).resolve().parent;R=S.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=S/'status.json';status=json.loads(p.read_text(encoding='utf-8'))
if status['checkpoint_open']:
 assert status['checkpoint']=='R005' and not (S/'git-R005-manifest.json').exists() and not (S/'git-R005-receipt.json').exists()
 assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=R).strip(),'Do not resume unknown staged work'
status['checkpoint_open']=True;status['checkpoint']='R005';status['checkpoint_started_at']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat();p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['status.json','threads.json','runs.md','next-task.md','root-template-visual-review.json','v003-exact-change-contract.json','automation-final-phase-update-receipt.json','automation-final-phase-actual-readback.json','checkpoint_R005.py','R005-prestage-failure-and-recovery.json',
'roles/role3/R003/reference-requirement-correction.md','roles/role3/R003/freeze.json','roles/role5/R003/freeze.json','roles/role5/R003/artifact.md','roles/role5/R003/math_omml.py','roles/role5/R003/render_review.py','roles/role5/R003/inspect_template.ps1','roles/role5/R003/preflight_word.py']
items=[]
for name in names:
 x=S/name;b=x.read_bytes()
 if x.suffix=='.py':ast.parse(b.decode('utf-8'))
 if x.suffix=='.json':json.loads(b.decode('utf-8'))
 items.append({'relative':x.relative_to(R).as_posix(),'sha256':sha(x)})
cfg={'checkpoint':'R005','message':'P06 session022: prepare native Word production and clarify official requirements','files':items,'checks':['Root fully read frozen preparation report, safe rendering and template inspection code','Root actually viewed all four official template pages','Reference count and line-grid discrepancies independently confirmed, no compliance claim','Current ten substantive references retained; no irrelevant additions','Exact v003 change contract precomputed; science manuscript not written by root','No final Word or final-page QA claimed, active role5 R004 artifacts excluded','All official template, source excerpts, PDF and page images in local-cache excluded']}
mp=S/'git-R005-manifest.json';assert not mp.exists();mp.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rc=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(mp)],cwd=R).returncode
if rc:raise SystemExit(rc)
rec=json.loads((S/'git-R005-receipt.json').read_text(encoding='utf-8'));status['checkpoint_open']=False;status['git']={'last_checkpoint':'R005','HEAD':rec['HEAD'],'pending_push':rec['pending_push'],'remote_verified':rec['remote_equals_local']};p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
