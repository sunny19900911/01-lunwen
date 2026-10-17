"""R018 review exact index bytes and normal authorized push; one retry maximum."""
from pathlib import Path
from datetime import datetime
import hashlib,json,os,subprocess
S=Path(__file__).resolve().parent
R=S.parents[2]
GIT='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
def git(*args,check=True):
 return subprocess.run([GIT,*args],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=check)
def main():
 manifest=json.loads((S/'R018-publish-manifest.json').read_text('utf-8'))
 assert manifest['checks_passed']
 assert git('rev-parse','HEAD').stdout.decode().strip()==manifest['expected_head']
 assert not git('diff','--cached','--name-only').stdout.strip()
 # Read status metadata only; do not open/hash unknown untracked files.
 before=git('status','--short','--untracked-files=normal').stdout.decode('utf-8',errors='replace')
 names=[item['path'] for item in manifest['files']]
 for item in manifest['files']:
  p=R/item['path'];raw=p.read_bytes()
  assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],item['path']
 git('add','--',*names)
 staged=git('diff','--cached','--name-only','-z').stdout.decode('utf-8').split('\0')
 staged=[name for name in staged if name]
 assert set(staged)==set(names),(len(staged),len(names),set(names)-set(staged))
 for item in manifest['files']:
  raw=git('show',':'+item['path']).stdout
  assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],item['path']
 # Frozen unified diff contains legitimate one-space context; checked against both originals.
 normal=[name for name in names if not name.endswith('/v001-to-v002.diff')]
 git('diff','--cached','--check','--',*normal)
 qa={'at':datetime.now().astimezone().isoformat(),'file_count':len(names),'all_reviewed_working_and_staged_blobs_equal':True,
     'normal_cached_diff_check_passed':True,'frozen_diff_checked_against_both_sources':True,
     'before_status_entry_count':len(before.splitlines()),'explicit_paths':names,'protected_unknown_files_opened':False}
 (S/'R018-index-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
 identity=['-c','user.name=Codex Paper Lab','-c','user.email=codex-paper-lab@localhost.invalid']
 git(*identity,'commit','-m','research: review midpoint forward diagnostics and paired engineering validation plan')
 commit=git('rev-parse','HEAD').stdout.decode().strip()
 os.environ['GIT_TERMINAL_PROMPT']='0';os.environ['GCM_INTERACTIVE']='Never'
 attempts=[]
 for attempt in range(2):
  opts=['-c','http.proxy=http://127.0.0.1:17890']
  if attempt:opts+=['-c','http.version=HTTP/1.1']
  result=git(*opts,'push','origin','main',check=False)
  attempts.append({'attempt':attempt+1,'exit_code':result.returncode,'stdout':result.stdout.decode('utf-8',errors='replace'),'stderr':result.stderr.decode('utf-8',errors='replace')})
  if result.returncode==0:break
 remote=None;verified=False
 if attempts[-1]['exit_code']==0:
  result=git('-c','http.proxy=http://127.0.0.1:17890','ls-remote','origin','refs/heads/main',check=False)
  if result.returncode==0 and result.stdout.strip():
   remote=result.stdout.decode().split()[0];verified=remote==commit
 receipt={'at':datetime.now().astimezone().isoformat(),'commit':commit,'remote_commit':remote,'verified':verified,
 'attempts':attempts,'file_count':len(names),'protected_originals_arrays_and_unknowns_excluded':True}
 (S/'R018-push.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'commit':commit,'remote':remote,'verified':verified,'files':len(names),'attempts':len(attempts)}))
if __name__=='__main__':main()

