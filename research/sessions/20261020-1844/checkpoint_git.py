"""Explicit-path publication for the user's authorized fifteen-minute checkpoints."""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,subprocess
S=Path(__file__).resolve().parent;R=S.parents[2]
def now():return datetime.datetime.now(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def git(*a,check=True):
 p=subprocess.run(['git','-C',str(R),*a],capture_output=True,timeout=60)
 if check and p.returncode:raise RuntimeError(p.stderr.decode('utf-8','replace')[-1800:])
 return p.stdout
ap=argparse.ArgumentParser();ap.add_argument('--label',required=True);ap.add_argument('--files',nargs='+',required=True);args=ap.parse_args()
assert not git('diff','--cached','--name-only').strip(),'Existing index is outside this checkpoint'
assert git('branch','--show-current').strip()==b'main'
files=[]
for f in args.files:
 p=(R/f).resolve();rel=p.relative_to(R)
 assert p.is_relative_to(S) or (p.parent==R/'papers/damping-output-boundaries/manuscript' and p.name.startswith('modal-shear-session009-')),str(p)
 assert not any('local-cache' in v or v=='__pycache__' for v in rel.parts)
 assert p.suffix.lower() in {'.md','.json','.csv','.py','.svg','.png','.docx'} or p.name=='.gitignore'
 assert p.is_file() and p.stat().st_size<2500000
 if p.suffix=='.py':ast.parse(p.read_text('utf-8-sig'))
 if p.suffix=='.json':json.loads(p.read_text('utf-8-sig'))
 files.append(p)
assert len(files)==len(set(files))
manifest=S/('git-'+args.label+'-manifest.json');receipt=S/('git-'+args.label+'-receipt.json')
assert not manifest.exists() and not receipt.exists(),'Use a fresh checkpoint label'
head_before=git('rev-parse','HEAD').decode().strip()
remote_before=None;read_errors=[]
for i in range(2):
 try:remote_before=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','origin','refs/heads/main').split()[0].decode();break
 except Exception as e:read_errors.append(str(e))
assert remote_before is None or remote_before==head_before,'Remote changed; inspect without overwriting local work'
data={'prepared_at':now(),'label':args.label,'remote_before':remote_before,'head_before':head_before,'files':[{'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],'scope':'Only explicit completed checkpoint paths; raw data, third-party full papers, caches and old changes excluded'}
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8');files.append(manifest)
paths=[p.relative_to(R).as_posix() for p in files]
git('add','--',*paths)
staged=set(filter(None,git('diff','--cached','--name-only','-z').decode('utf-8').split('\0')))
assert staged<=set(paths),'Unexpected staged path'
for p,path in zip(files,paths):assert git('cat-file','blob',':'+path)==p.read_bytes(),path
git('-c','core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol','diff','--cached','--check')
git('-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid','commit','-m','research: modal shear '+args.label)
head=git('rev-parse','HEAD').decode().strip();attempts=[];pushed=False
for i in range(2):
 try:git('-c','http.proxy=http://127.0.0.1:17890','push','origin','main');attempts.append({'attempt':i+1,'success':True});pushed=True;break
 except Exception as e:attempts.append({'attempt':i+1,'success':False,'error':str(e)})
remote=None
if pushed:
 try:remote=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','origin','refs/heads/main').split()[0].decode()
 except Exception as e:read_errors.append(str(e))
out={'finished_at':now(),'commit':head,'file_count':len(files),'attempts':attempts,'remote_commit':remote,'remote_verified':remote==head,'read_errors':read_errors}
receipt.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
p=S/'status.json';v=json.loads(p.read_text('utf-8'));v['last_remote_verified']=out;v['last_git_receipt']=receipt.name;v['checkpoint_open']=False;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(out,ensure_ascii=False))
