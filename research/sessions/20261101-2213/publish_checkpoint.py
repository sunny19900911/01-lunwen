from pathlib import Path
import argparse,subprocess,json,hashlib,datetime,ast,csv
ap=argparse.ArgumentParser();ap.add_argument('--manifest',required=True);args=ap.parse_args()
M=Path(args.manifest).resolve();S=Path(__file__).resolve().parent;R=S.parents[2]
cfg=json.loads(M.read_text(encoding='utf-8'));out=S/('git-'+cfg['checkpoint']+'-receipt.json')
assert not out.exists(),'Existing receipt: inspect it instead of repeating'
def call(a,required=True):
 p=subprocess.run(a,cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace')
 if required and p.returncode:raise RuntimeError(p.stdout+'\n'+p.stderr)
 return p
def sha(b):return hashlib.sha256(b).hexdigest()
assert not call(['git','diff','--cached','--name-only']).stdout.strip(),'Unknown staged work'
assert call(['git','branch','--show-current']).stdout.strip()=='main'
before=call(['git','rev-parse','HEAD']).stdout.strip()
remote=call(['git','-c','http.proxy=http://127.0.0.1:17890','ls-remote','--exit-code','origin','refs/heads/main']).stdout.split()[0]
resumed_pending=None
if before!=remote:
 pending_path=(R/cfg.get('resume_pending_receipt','')).resolve()
 assert pending_path.is_relative_to(S) and pending_path.is_file(),'Remote changed: inspect; no force'
 pending=json.loads(pending_path.read_text(encoding='utf-8'))
 assert pending.get('pending_push') and pending['HEAD']==before and pending['remote_HEAD']==remote,'Only the exact recorded pending commit can be resumed'
 call(['git','merge-base','--is-ancestor',remote,before])
 resumed_pending=pending_path.relative_to(R).as_posix()
items=cfg['files']+[{'relative':M.relative_to(R).as_posix(),'sha256':sha(M.read_bytes())}]
paths=[]
for q in items:
 p=(R/q['relative']).resolve()
 assert p.is_relative_to(S) or (p.parent==R/'papers/damping-output-boundaries/manuscript' and p.name.startswith('damping-prediction-session021-'))
 assert 'local-cache'not in p.parts and p.suffix in ['.md','.json','.csv','.py','.cjs','.ps1','.svg','.png','.docx']
 b=p.read_bytes();assert len(b)<1048576 and sha(b)==q['sha256']
 if p.suffix=='.json':json.loads(b.decode('utf-8'))
 if p.suffix=='.py':ast.parse(b.decode('utf-8'))
 if p.suffix=='.csv':
  a=list(csv.reader(b.decode('utf-8-sig').splitlines()));assert len(a)>1 and all(len(r)==len(a[0])for r in a)
 paths.append(q['relative'])
assert len(paths)==len(set(paths))
call(['git','add','--']+paths);call(['git','diff','--cached','--check'])
staged={p for p in call(['git','diff','--cached','--name-only','-z']).stdout.split('\0')if p};assert staged and staged<=set(paths)
for q in items:
 if q['relative']in staged:assert sha(subprocess.check_output(['git','show',':'+q['relative']],cwd=R))==q['sha256']
p=call(['git','commit','-m',cfg['message']],False);fallback=False
if p.returncode and ('identity unknown'in p.stderr.lower()or'unable to auto-detect email'in p.stderr.lower()):
 fallback=True;p=call(['git','-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid','commit','-m',cfg['message']],False)
assert p.returncode==0,p.stderr
head=call(['git','rev-parse','HEAD']).stdout.strip();attempts=[]
for i in range(2):
 p=call(['git','-c','http.proxy=http://127.0.0.1:17890','push','origin','main'],False);attempts.append({'attempt':i+1,'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 if p.returncode==0:break
p=call(['git','-c','http.proxy=http://127.0.0.1:17890','ls-remote','--exit-code','origin','refs/heads/main'],False)
remote=p.stdout.split()[0]if p.returncode==0 and p.stdout.strip()else None
d={'checkpoint':cfg['checkpoint'],'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'HEAD':head,'previous_HEAD':before,'staged_files':sorted(staged),'verified_blob_hashes':len(staged),'identity_fallback':fallback,'push_attempts':attempts,'remote_HEAD':remote,'remote_equals_local':remote==head,'pending_push':remote!=head,'resumed_pending_receipt':resumed_pending}
with out.open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:d[k]for k in ['checkpoint','HEAD','remote_equals_local','pending_push']},ensure_ascii=False))

