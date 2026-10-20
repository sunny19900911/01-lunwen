"""Explicit completed-file checkpoints for the authorized journal revision window."""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,subprocess
S=Path(__file__).resolve().parent;R=S.parents[2]
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def git(*args,check=True):
 p=subprocess.run(['git','-C',str(R),*args],capture_output=True,timeout=60)
 if check and p.returncode:raise RuntimeError((p.stdout+p.stderr).decode('utf-8','replace'))
 return p.stdout
a=argparse.ArgumentParser();a.add_argument('--label',required=True);a.add_argument('--list',required=True);v=a.parse_args()
assert not git('diff','--cached','--name-only').strip(),'Continue existing checkpoint; do not create a second index'
assert git('branch','--show-current').strip()==b'main'
files=[]
for rel in json.loads(Path(v.list).read_text('utf-8-sig')):
 p=(R/rel).resolve();assert p.is_relative_to(S) or (p.parent==R/'papers/damping-output-boundaries/manuscript' and p.name.startswith('jgjg-session010-'))
 assert not any('local-cache' in x or x=='__pycache__' for x in p.relative_to(R).parts)
 assert p.is_file() and p.stat().st_size<2500000
 assert p.suffix in {'.md','.json','.csv','.py','.ps1','.cjs','.svg','.png','.docx'}
 if p.suffix=='.json':json.loads(p.read_text('utf-8-sig'))
 if p.suffix=='.py':ast.parse(p.read_text('utf-8-sig'))
 files.append(p)
assert len(files)==len(set(files))
manifest=S/f'git-{v.label}-manifest.json';receipt=S/f'git-{v.label}-receipt.json'
assert not manifest.exists() and not receipt.exists(),'Use a new label only for a new checkpoint; resume existing staged index instead'
head_before=git('rev-parse','HEAD').decode().strip();remote_before=None;pre_errors=[]
for i in range(2):
 try:remote_before=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','origin','refs/heads/main').decode().split()[0];break
 except Exception as e:pre_errors.append(str(e))
assert remote_before is None or remote_before==head_before,'Remote changed; inspect safely without force or reset'
data={'prepared_at':now(),'label':v.label,'head_before':head_before,'remote_before':remote_before,'pre_errors':pre_errors,'files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8');files.append(manifest)
paths=[p.relative_to(R).as_posix() for p in files];git('add','--',*paths)
staged=set(git('diff','--cached','--name-only','-z').decode().strip('\0').split('\0'));assert staged<=set(paths)
for p,rel in zip(files,paths):assert git('cat-file','blob',':'+rel)==p.read_bytes(),rel
git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check')
git('-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid','commit','-m','research: journal engineering evaluation '+v.label)
head=git('rev-parse','HEAD').decode().strip();attempts=[];pushed=False
for i in range(2):
 try:
  output=git('-c','http.proxy=http://127.0.0.1:17890','push','origin','main');attempts.append({'attempt':i+1,'success':True});pushed=True;break
 except Exception as e:attempts.append({'attempt':i+1,'success':False,'error':str(e)})
remote=None;verify_error=None
if pushed:
 try:remote=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','origin','refs/heads/main').decode().split()[0]
 except Exception as e:verify_error=str(e)
out={'finished_at':now(),'commit':head,'file_count':len(files),'staged_file_count':len(staged),'attempts':attempts,'remote_commit':remote,'remote_verified':remote==head,'verify_error':verify_error}
receipt.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
p=S/'status.json';st=json.loads(p.read_text('utf-8'));st.update(checkpoint_open=False,last_git_checkpoint=v.label,last_git_receipt=receipt.name,last_git_result=out);p.write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(out,ensure_ascii=False))
