"""Continue the exact final index; unified diff context spaces are retained."""
from pathlib import Path
import json,hashlib,subprocess,datetime,re
S=Path(__file__).resolve().parent;R=S.parents[2]
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def git(*a,check=True):
 p=subprocess.run(['git','-C',str(R),*a],capture_output=True,timeout=60)
 if check and p.returncode:raise RuntimeError((p.stdout+p.stderr).decode('utf-8','replace'))
 return p
m=json.loads((S/'git-FINAL-manifest.json').read_text('utf-8'))
assert git('rev-parse','HEAD').stdout.decode().strip()==m['head_before']
paths={v['path'] for v in m['files']}|{(S/'git-FINAL-manifest.json').relative_to(R).as_posix()}
staged=set(git('diff','--cached','--name-only','-z').stdout.decode().strip('\0').split('\0'))
assert staged<=paths
for v in m['files']:assert hashlib.sha256(git('cat-file','blob',':'+v['path']).stdout).hexdigest()==v['sha256']
p=git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check',check=False)
diagnostics=p.stdout.decode('utf-8');exceptions=[]
allowed={'research/sessions/20261020-1844/roles/role5/R010-diff.txt','research/sessions/20261020-1844/roles/role5/R010-final-diff.txt','research/sessions/20261020-1844/roles/role5/R011-build_word.py'}
for line in diagnostics.splitlines():
 if not line.strip():continue
 match=re.fullmatch(r'(.+):(\d+): trailing whitespace\.',line)
 if match:
  path,num=match.group(1),int(match.group(2));assert path in allowed
  raw=git('cat-file','blob',':'+path).stdout.splitlines()[num-1]
  assert not raw.strip(),(path,num,raw)
  if path.endswith('.py'):assert num==352
  exceptions.append({'path':path,'line':num,'reason':'Whitespace-only frozen line; unified diff context prefix or empty Python line.'})
 else:assert line.strip()=='+',repr(line)
assert exceptions
selfpath=Path(__file__).relative_to(R).as_posix();git('add','--',selfpath)
assert git('cat-file','blob',':'+selfpath).stdout==Path(__file__).read_bytes()
git('-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid','commit','-m','research: deliver modal shear manuscript and editable Word')
head=git('rev-parse','HEAD').stdout.decode().strip();attempts=[];pushed=False
for i in range(2):
 p=git('-c','http.proxy=http://127.0.0.1:17890','push','origin','main',check=False)
 attempts.append({'attempt':i+1,'success':p.returncode==0,'output':(p.stdout+p.stderr).decode('utf-8','replace')})
 if p.returncode==0:pushed=True;break
remote=None
if pushed:
 p=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','origin','refs/heads/main',check=False)
 if p.returncode==0:remote=p.stdout.decode().split()[0]
out={'finished_at':now(),'commit':head,'manifest':'git-FINAL-manifest.json','additional_explicit_path':selfpath,'additional_path_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'file_count':len(staged)+1,'attempts':attempts,'remote_commit':remote,'remote_verified':head==remote,'reviewed_frozen_whitespace_exceptions':exceptions,'initial_check_failed_before_commit':True,'local_receipt_follows_commit':True}
(S/'git-FINAL-receipt.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
v=json.loads((S/'status.json').read_text('utf-8'));v.update(last_completed_checkpoint='FINAL',last_git_receipt='git-FINAL-receipt.json',last_remote_verified=out,final_git_status='remote_verified' if remote==head else 'local_commit_pending_push_or_verification',checkpoint_open=False,phase='closed-budget')
(S/'status.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:out[k] for k in ['finished_at','commit','file_count','attempts','remote_commit','remote_verified']},ensure_ascii=False))
