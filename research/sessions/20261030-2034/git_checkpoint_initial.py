from pathlib import Path
import subprocess,json,hashlib,datetime,ast,csv
S=Path(__file__).resolve().parent;R=S.parents[2]
def run(args,check=True):
 p=subprocess.run(args,cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace')
 if check and p.returncode:raise RuntimeError(p.stdout+'\n'+p.stderr)
 return p
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def js(path,d):
 with path.open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
names=['plan.md','status.json','authorization.md','claims.md','runs.md','threads.json','initial-thread-snapshots.json','automation-start-tool-receipts.json','rounds/R001-start.md','run_low_order_fit.py','git_checkpoint_initial.py']
names+=['root-R001-low-order/'+n for n in ['README.md','input-rules-freeze.json','prediction-errors-96.csv','fixed-output-coefficients.csv','primary-modal-reference-peaks.csv','primary-critical-time-terms.csv','primary-critical-time-groups.csv','models-small.json','coefficient-stability.csv','results.json','manifest.json']]
assert not run(['git','diff','--cached','--name-only']).stdout.strip(),'Index not empty; do not mix unknown staged work'
assert run(['git','branch','--show-current']).stdout.strip()=='main'
starthead=run(['git','rev-parse','HEAD']).stdout.strip()
remote=run(['git','-c','http.proxy=http://127.0.0.1:17890','ls-remote','--exit-code','origin','refs/heads/main']).stdout.split()[0]
assert starthead==remote,'Remote/base changed; inspect before publishing'
intent=[]
for name in names:
 p=S/name;assert p.is_file() and 'local-cache' not in p.parts
 assert p.stat().st_size<262144
 b=p.read_bytes()
 if p.suffix=='.json':json.loads(b.decode('utf-8'))
 if p.suffix=='.py':ast.parse(b.decode('utf-8'))
 if p.suffix=='.csv':
  rows=list(csv.reader(b.decode('utf-8-sig').splitlines()));assert len(rows)>1 and all(len(q)==len(rows[0])for q in rows)
 intent.append({'relative':p.relative_to(R).as_posix(),'bytes':len(b),'sha256':sha_bytes(b)})
js(S/'git-R001-intent.json',{'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorization':'human20261030 explicit15min Git upload','initial_HEAD_remote':starthead,'all_role_files_excluded_until_frozen':True,'source_files':intent,'exclude':'local-cache,raw arrays,prior dirty work'})
p=S/'git-R001-intent.json';intent.append({'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha_bytes(p.read_bytes())})
run(['git','add','--']+[q['relative']for q in intent])
run(['git','diff','--cached','--check'])
staged=set(run(['git','diff','--cached','--name-only']).stdout.splitlines())
assert staged=={q['relative']for q in intent}
for q in intent:
 b=subprocess.check_output(['git','show',':'+q['relative']],cwd=R)
 assert sha_bytes(b)==q['sha256'],'Staged blob differs from actual frozen file'
stat=run(['git','diff','--cached','--stat']).stdout
msg='research: session019 real damping-superposition low-order results'
p=run(['git','commit','-m',msg],check=False)
identity_fallback=False
if p.returncode and ('identity unknown'in p.stderr.lower() or 'unable to auto-detect email'in p.stderr.lower()):
 identity_fallback=True;p=run(['git','-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid','commit','-m',msg],check=False)
if p.returncode:raise RuntimeError('Commit failed: '+p.stderr)
head=run(['git','rev-parse','HEAD']).stdout.strip();attempts=[]
for i in range(2):
 p=run(['git','-c','http.proxy=http://127.0.0.1:17890','push','origin','main'],check=False)
 attempts.append({'attempt':i+1,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 if p.returncode==0:break
verify=run(['git','-c','http.proxy=http://127.0.0.1:17890','ls-remote','--exit-code','origin','refs/heads/main'],check=False)
remote_after=verify.stdout.split()[0] if verify.returncode==0 and verify.stdout.strip() else None
receipt={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':head,'previous_head':starthead,'files':len(intent),'identity_fallback':identity_fallback,'commit_success':True,'push_attempts':attempts,'remote_after':remote_after,'remote_equal_HEAD':remote_after==head,'stat':stat,'staged_blobs_sha_verified':len(intent),'pending_push':remote_after!=head,'no_raw_or_old_dirty_staged':True}
js(S/'git-R001-receipt.json',receipt)
print(json.dumps({k:receipt[k]for k in ['head','files','commit_success','remote_after','remote_equal_HEAD','pending_push']},ensure_ascii=False))

