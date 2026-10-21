from pathlib import Path
import subprocess,json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
def git(*a,check=True):
 p=subprocess.run(['git','-C',str(R),*a],capture_output=True,timeout=60)
 if check and p.returncode:raise RuntimeError((p.stdout+p.stderr).decode('utf-8','replace'))
 return p
m=json.loads((S/'git-R000-manifest.json').read_text('utf-8'));assert git('rev-parse','HEAD').stdout.decode().strip()==m['head_before']
paths={v['path'] for v in m['files']}|{(S/'git-R000-manifest.json').relative_to(R).as_posix()}
staged=set(git('diff','--cached','--name-only','-z').stdout.decode().strip('\0').split('\0'));assert staged<=paths
for v in m['files']:assert hashlib.sha256(git('cat-file','blob',':'+v['path']).stdout).hexdigest()==v['sha256']
p=git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check',check=False)
assert p.stdout.decode()=='research/sessions/20261021-0737/roles/role5/R002-build_word.py:397: trailing whitespace.\n+        \n'
git('-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid','commit','-m','research: engineering journal revision and verified continuation')
head=git('rev-parse','HEAD').stdout.decode().strip();attempts=[];ok=False
for i in range(2):
 p=git('-c','http.proxy=http://127.0.0.1:17890','push','origin','main',check=False);attempts.append({'attempt':i+1,'success':p.returncode==0})
 if p.returncode==0:ok=True;break
remote=None
if ok:
 p=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','origin','refs/heads/main',check=False)
 if p.returncode==0:remote=p.stdout.decode().split()[0]
out={'finished_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'commit':head,'file_count':len(staged),'attempts':attempts,'remote_commit':remote,'remote_verified':remote==head,'frozen_whitespace_exception':'role5 R002 builder whitespace-only line397 retained to preserve source SHA'}
(S/'git-R000-receipt.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8');v=json.loads((S/'status.json').read_text('utf-8'));v.update(checkpoint_open=False,last_git_checkpoint='R000',last_git_receipt='git-R000-receipt.json',last_git_result=out);(S/'status.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(out,ensure_ascii=False))
