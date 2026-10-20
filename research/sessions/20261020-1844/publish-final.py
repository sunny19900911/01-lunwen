"""Publish only the completed, authorized session artifacts, preserving frozen bytes."""
from pathlib import Path
import ast,datetime,hashlib,json,subprocess
S=Path(__file__).resolve().parent; R=S.parents[2]
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def git(*args,check=True):
    p=subprocess.run(['git','-C',str(R),*args],capture_output=True,timeout=60)
    if check and p.returncode:raise RuntimeError((p.stdout+p.stderr).decode('utf-8','replace'))
    return p
assert not git('diff','--cached','--name-only').stdout.strip(),'Existing index must be continued separately'
assert git('branch','--show-current').stdout.strip()==b'main'
names=['close-session.py','publish-final.py','R006-resume.py','git-R006-receipt.json','final-tool-receipts.json','final-automation-readback.json','root-final-word-QA.json','普通中文研究说明.md','final-summary-prepared.md','final-summary.md','rounds/R007-final.md','status.json','threads.json','claims.md','runs.md']
files=[S/n for n in names]
for prefix in ['R010','R011']:
    files.extend(p for p in sorted((S/'roles/role5').glob(prefix+'*')) if p.is_file() and p.suffix in {'.md','.json','.py','.ps1','.txt'})
files.extend(R/'papers/damping-output-boundaries/manuscript'/n for n in ['modal-shear-session009-v010.md','modal-shear-session009-论文审阅稿-v010.docx'])
assert len(files)==len(set(files))
for p in files:
    assert p.is_file() and p.stat().st_size<2500000,p
    assert p.is_relative_to(S) or p.parent==R/'papers/damping-output-boundaries/manuscript'
    assert not any('local-cache' in part or part=='__pycache__' for part in p.parts)
    if p.suffix=='.json':json.loads(p.read_text('utf-8-sig'))
    if p.suffix=='.py':ast.parse(p.read_text('utf-8-sig'))
head_before=git('rev-parse','HEAD').stdout.decode().strip()
prechecks=[];remote_before=None
for i in range(2):
    p=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','origin','refs/heads/main',check=False)
    prechecks.append({'attempt':i+1,'success':p.returncode==0})
    if p.returncode==0:remote_before=p.stdout.decode().split()[0];break
assert remote_before is None or remote_before==head_before,'Remote changed; do not overwrite'
manifest=S/'git-FINAL-manifest.json';receipt=S/'git-FINAL-receipt.json'
assert not manifest.exists() and not receipt.exists(),'Do not duplicate final publication'
data={'prepared_at':now(),'head_before':head_before,'remote_before':remote_before,'prechecks':prechecks,'files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8');files.append(manifest)
paths=[p.relative_to(R).as_posix() for p in files]
git('add','--',*paths)
staged=set(git('diff','--cached','--name-only','-z').stdout.decode().strip('\0').split('\0'))
assert staged<=set(paths)
for p,path in zip(files,paths):assert git('cat-file','blob',':'+path).stdout==p.read_bytes(),path
check=git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check',check=False)
diagnostics=check.stdout.decode('utf-8')
allowed='research/sessions/20261020-1844/roles/role5/R011-build_word.py:352: trailing whitespace.\n+        \n'
assert check.returncode==0 or diagnostics==allowed,diagnostics
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
out={'finished_at':now(),'commit':head,'file_count':len(files),'staged_file_count':len(staged),'attempts':attempts,'remote_commit':remote,'remote_verified':remote==head,'whitespace_exception':diagnostics,'exception_reason':'Preserve frozen Python builder; reviewed whitespace-only line has no semantics. No other whitespace diagnostics.' if diagnostics else None,'local_receipt_follows_commit':True}
receipt.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
v=json.loads((S/'status.json').read_text('utf-8'));v.update(last_completed_checkpoint='FINAL',last_git_receipt=receipt.name,last_remote_verified=out,final_git_status='remote_verified' if remote==head else 'local_commit_pending_push_or_verification',checkpoint_open=False,phase='closed-budget')
(S/'status.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(out,ensure_ascii=False))
