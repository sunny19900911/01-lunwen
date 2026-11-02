"""Resume only this checkpoint's verified index; leave the frozen unified diff local."""
from pathlib import Path
import json,hashlib,subprocess,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];M=S/'git-R006-manifest.json';cfg=json.loads(M.read_text(encoding='utf-8'));out=S/'git-R006-receipt.json'
assert not out.exists()
def sha(b):return hashlib.sha256(b).hexdigest()
def run(args,required=True):
 p=subprocess.run(args,cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace')
 if required and p.returncode:raise RuntimeError(p.stdout+'\n'+p.stderr)
 return p
items=cfg['files']+[{'relative':M.relative_to(R).as_posix(),'sha256':sha(M.read_bytes())}];known={x['relative']:x['sha256'] for x in items}
staged=set(filter(None,run(['git','diff','--cached','--name-only','-z']).stdout.split('\0')))
assert staged and staged<=set(known),'Do not modify unrelated staged work'
for p in staged:assert sha(subprocess.check_output(['git','show',':'+p],cwd=R))==known[p]
excluded=(S/'roles/role5/R004/v002-to-v003.diff').relative_to(R).as_posix();assert excluded in staged
f=R/excluded;original=f.read_bytes();trailing=[x for x in original.decode('utf-8').splitlines() if x.rstrip()!=x];assert trailing and all(x==' ' for x in trailing),'Only standard blank unified-diff context lines expected'
before=run(['git','rev-parse','HEAD']).stdout.strip();remote_before=run(['git','-c','http.proxy=http://127.0.0.1:17890','ls-remote','--exit-code','origin','refs/heads/main']).stdout.split()[0];assert before==remote_before
run(['git','restore','--staged','--',excluded]);assert f.read_bytes()==original,'Frozen diff unchanged'
run(['git','diff','--cached','--check'])
staged=set(filter(None,run(['git','diff','--cached','--name-only','-z']).stdout.split('\0')));assert excluded not in staged and staged<=set(known)
for p in staged:assert sha(subprocess.check_output(['git','show',':'+p],cwd=R))==known[p]
p=run(['git','commit','-m',cfg['message']],False);fallback=False
if p.returncode and ('identity unknown' in p.stderr.lower() or 'unable to auto-detect email' in p.stderr.lower()):
 fallback=True;p=run(['git','-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid','commit','-m',cfg['message']],False)
assert p.returncode==0,p.stderr
head=run(['git','rev-parse','HEAD']).stdout.strip();attempts=[]
for i in range(2):
 p=run(['git','-c','http.proxy=http://127.0.0.1:17890','push','origin','main'],False);attempts.append({'attempt':i+1,'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 if p.returncode==0:break
p=run(['git','-c','http.proxy=http://127.0.0.1:17890','ls-remote','--exit-code','origin','refs/heads/main'],False);remote=p.stdout.split()[0] if p.returncode==0 and p.stdout.strip() else None
receipt={'checkpoint':'R006','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'HEAD':head,'previous_HEAD':before,'remote_HEAD':remote,'remote_equals_local':remote==head,'pending_push':remote!=head,'verified_blob_hashes':len(staged),'staged_files':sorted(staged),'push_attempts':attempts,'identity_fallback':fallback,'excluded_local_file':{'path':excluded,'sha256':sha(original),'reason':'Standard unified-diff empty-context whitespace retained unchanged locally; source and exact-change contract are published'},'only_preexisting_staged_entries':'all verified as belonging to this R006 manifest'}
with out.open('x',encoding='utf-8') as h:json.dump(receipt,h,ensure_ascii=False,indent=2);h.write('\n')
p=S/'status.json';status=json.loads(p.read_text(encoding='utf-8'));assert status['checkpoint_open'] and status['checkpoint']=='R006';status['checkpoint_open']=False;status['git']={'last_checkpoint':'R006','HEAD':head,'pending_push':remote!=head,'remote_verified':remote==head};p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:receipt[k] for k in ['checkpoint','HEAD','remote_equals_local','pending_push']}))
