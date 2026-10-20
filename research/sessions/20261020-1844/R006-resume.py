"""Resume the existing, reviewed R006 index without restaging frozen files."""
from pathlib import Path
import subprocess,json,datetime,hashlib
S=Path(__file__).resolve().parent; R=S.parents[2]
def git(*args,check=True):
    p=subprocess.run(['git','-C',str(R),*args],capture_output=True,timeout=60)
    if check and p.returncode: raise RuntimeError((p.stdout+p.stderr).decode('utf-8','replace'))
    return p
m=json.loads((S/'git-R006-manifest.json').read_text('utf-8'))
assert git('rev-parse','HEAD').stdout.decode().strip()==m['head_before']
paths={x['path'] for x in m['files']}|{(S/'git-R006-manifest.json').relative_to(R).as_posix()}
staged=set(git('diff','--cached','--name-only','-z').stdout.decode().strip('\0').split('\0'))
assert staged<=paths
for x in m['files']:
    assert hashlib.sha256(git('cat-file','blob',':'+x['path']).stdout).hexdigest()==x['sha256']
check=git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check',check=False)
diagnostic=check.stdout.decode('utf-8')
assert diagnostic=='research/sessions/20261020-1844/roles/role5/R009-build_word.py:349: trailing whitespace.\n+        \n',repr(diagnostic)
# Frozen provenance is preserved. This empty line has no Python semantics.
# Exact diagnostic equality above permits only this reviewed provenance exception.
git('-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid','commit','-m','research: modal shear R006')
head=git('rev-parse','HEAD').stdout.decode().strip(); attempts=[]
for i in range(2):
    p=git('-c','http.proxy=http://127.0.0.1:17890','push','origin','main',check=False)
    attempts.append({'attempt':i+1,'success':p.returncode==0,'output':(p.stdout+p.stderr).decode('utf-8','replace')})
    if p.returncode==0: break
remote=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','origin','refs/heads/main',check=False)
sha=remote.stdout.decode().split()[0] if remote.returncode==0 and remote.stdout.strip() else None
out={'finished_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'commit':head,'file_count':len(paths),'attempts':attempts,'remote_commit':sha,'remote_verified':sha==head,'whitespace_exception':{'file':'roles/role5/R009-build_word.py','line':349,'reason':'Frozen empty Python line contains spaces; preserved bytes and source manifest; all other diagnostics absent.'}}
(S/'git-R006-receipt.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
p=S/'status.json';v=json.loads(p.read_text('utf-8'));v.update(last_remote_verified=out,last_git_receipt='git-R006-receipt.json',checkpoint_open=False,last_completed_checkpoint='R006');p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(out,ensure_ascii=False))
