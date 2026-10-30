from pathlib import Path
import subprocess,json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
cfg=json.loads((S/'git-R004-publication.json').read_text(encoding='utf-8'))
receipt=S/'git-R004-receipt.json'
assert not receipt.exists()
def call(a,required=True):
 p=subprocess.run(a,cwd=R,capture_output=True,text=True,encoding='utf-8',errors='replace')
 if required and p.returncode:raise RuntimeError(p.stdout+'\n'+p.stderr)
 return p
def sha(b):return hashlib.sha256(b).hexdigest()
items=cfg['files']+[{'relative':(S/'git-R004-publication.json').relative_to(R).as_posix(),'sha256':sha((S/'git-R004-publication.json').read_bytes())}]
staged=set(call(['git','diff','--cached','--name-only']).stdout.splitlines())
assert staged and staged<=set(q['relative']for q in items)
for q in items:
 if q['relative']in staged:assert sha(subprocess.check_output(['git','show',':'+q['relative']],cwd=R))==q['sha256']
check=call(['git','diff','--cached','--check'],False)
expected='research/sessions/20261030-2034/roles/role1/R003/coefficient-bound-one-page.md:28: trailing whitespace.\n+\\ \\Longrightarrow\\ \n'
assert check.returncode==2 and check.stdout.replace('\r\n','\n')==expected,(check.returncode,check.stdout)
math_path=R/'research/sessions/20261030-2034/roles/role1/R003/coefficient-bound-one-page.md'
assert math_path.read_text(encoding='utf-8').splitlines()[27]=='\\ \\Longrightarrow\\ '
before=call(['git','rev-parse','HEAD']).stdout.strip()
remote=call(['git','-c','http.proxy=http://127.0.0.1:17890','ls-remote','--exit-code','origin','refs/heads/main']).stdout.split()[0]
assert before==remote and call(['git','branch','--show-current']).stdout.strip()=='main'
p=call(['git','commit','-m',cfg['message']],False);fallback=False
if p.returncode and ('identity unknown'in p.stderr.lower()or'unable to auto-detect email'in p.stderr.lower()):
 fallback=True;p=call(['git','-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid','commit','-m',cfg['message']],False)
assert p.returncode==0,p.stderr
head=call(['git','rev-parse','HEAD']).stdout.strip();attempts=[]
for i in range(2):
 p=call(['git','-c','http.proxy=http://127.0.0.1:17890','push','origin','main'],False)
 attempts.append({'attempt':i+1,'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
 if p.returncode==0:break
p=call(['git','-c','http.proxy=http://127.0.0.1:17890','ls-remote','--exit-code','origin','refs/heads/main'],False)
remote=p.stdout.split()[0]if p.returncode==0 and p.stdout.strip()else None
d={'checkpoint':'R004','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'HEAD':head,'previous_HEAD':before,'staged_files':sorted(staged),'verified_blob_hashes':len(staged),'identity_fallback':fallback,'push_attempts':attempts,'remote_HEAD':remote,'remote_equals_local':remote==head,'pending_push':remote!=head,'initial_check_failure':check.stdout,'single_reviewed_whitespace_exception':{'path':str(math_path.relative_to(R)),'line':28,'sha256':sha(math_path.read_bytes()),'reason':'intentional LaTeX escaped spacing after implication; frozen source bytes preserved; all other diff-check output empty'}}
with receipt.open('x',encoding='utf-8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({k:d[k]for k in ['checkpoint','HEAD','remote_equals_local','pending_push']},ensure_ascii=False))
