"""Publish only this completed session's small artifacts; no solver/research run."""
from pathlib import Path
import ast,hashlib,json,subprocess,datetime,tomllib,re

S=Path(__file__).resolve().parent
R=S.parents[2]
NOW=lambda:datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def git(*args,check=True,binary=False):
 p=subprocess.run(['git','-C',str(R),*args],capture_output=True,timeout=60)
 if check and p.returncode:raise RuntimeError(p.stderr.decode('utf-8','replace')[-2000:])
 return p.stdout if binary else p.stdout.decode('utf-8','replace').strip()
assert not git('diff','--cached','--name-only'),'Existing index must be preserved'
assert git('branch','--show-current')=='main'
remote=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','--exit-code','origin','refs/heads/main').split()[0]
assert remote==git('rev-parse','HEAD'),'Remote changed; read divergence before any integration'
before=git('status','--porcelain','--untracked-files=no')
files=[]
for p in sorted(S.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(S)
 if any('local-cache' in x or x=='__pycache__' for x in rel.parts):continue
 if p.suffix.lower() not in {'.md','.json','.csv','.py','.gitignore'} and p.name!='.gitignore':continue
 if p.name in {'closeout-push-receipt.json','closeout-publish-manifest.json'}:continue
 assert p.stat().st_size<250000,str(p)
 b=p.read_bytes();t=b.decode('utf-8-sig')
 if p.suffix=='.py':ast.parse(t)
 if p.suffix=='.json':json.loads(t)
 files.append(p)
paper=R/'papers/damping-output-boundaries/manuscript/placement-session007-v001.md'
freeze=json.loads((S/'roles/role5/R003-freeze.json').read_text('utf-8'))
expected=next(x for x in freeze['files'] if x['path'].replace('\\','/').endswith('/placement-session007-v001.md'))
assert hashlib.sha256(paper.read_bytes()).hexdigest()==expected['sha256']
files.append(paper)
v=json.loads((S/'status.json').read_text('utf-8'))
v.update(phase='closed-budget',checkpoint_open=False,no_new_scientific_dispatch=True,closed_at=NOW(),canonical_manuscript=str(paper.relative_to(R)),closeout_push_status='pending actual result; see closeout-push-receipt.json')
v['automation_actual_config']={}
for aid in ['automation-5','automation-4','git','automation-3']:
 a=tomllib.loads((Path('C:/Users/mj528/.codex/automations')/aid/'automation.toml').read_text('utf-8-sig'))
 assert a['status']=='PAUSED',aid
 v['automation_actual_config'][aid]={k:a.get(k) for k in ['id','kind','name','status','rrule','target_thread_id']}
(S/'status.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
manifest={'prepared_at':NOW(),'files':[{'path':str(p.relative_to(R)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'excluded':'raw workbooks, entire nodes, trajectory arrays, local-cache, PDFs, old dirty files','old_tracked_status':before,'checks':'JSON decoding, Python AST, writer frozen manuscript SHA, explicit paths and staged blob byte identity'}
mp=S/'closeout-publish-manifest.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8');files.append(mp)
paths=[str(p.relative_to(R)).replace('\\','/') for p in files]
git('add','--',*paths)
staged=git('diff','--cached','--name-only','-z',binary=True).decode('utf-8').split('\0');staged=[x for x in staged if x]
assert set(staged)==set(paths),(set(staged)-set(paths))
for p,path in zip(files,paths):assert git('cat-file','blob',':'+path,binary=True)==p.read_bytes(),path
git('diff','--cached','--check')
git('-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid','commit','-m','research: record real-building placement study and six-role closeout')
commit=git('rev-parse','HEAD');attempts=[];pushed=False
for i in range(2):
 try:
  out=git('-c','http.proxy=http://127.0.0.1:17890','push','origin','main');attempts.append({'attempt':i+1,'success':True,'output':out});pushed=True;break
 except Exception as e:attempts.append({'attempt':i+1,'success':False,'error':str(e)})
actual_remote=None
if pushed:actual_remote=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','--exit-code','origin','refs/heads/main').split()[0]
receipt={'completed_at':NOW(),'commit':commit,'file_count':len(files),'push_attempts':attempts,'remote_commit':actual_remote,'remote_verified':pushed and actual_remote==commit,'no_prior_ten_minute_pushes_claimed':True,'original_tracked_status_before':before,'original_tracked_status_after':git('status','--porcelain','--untracked-files=no')}
(S/'closeout-push-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'commit':commit,'file_count':len(files),'remote_verified':receipt['remote_verified'],'receipt':str(S/'closeout-push-receipt.json')},ensure_ascii=False))
