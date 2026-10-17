
"""Explicit R023 preflight, only completed reviewed packages named in adoption."""
from pathlib import Path
from datetime import datetime
import ast,csv,hashlib,json,re,subprocess
S=Path(__file__).resolve().parent;R=S.parents[2]
B=R/'papers/damping-output-boundaries/research/roles'
GIT='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
ALLOWED={'novelty/maxwell-session004/R028-narrative-paper-contribution-review', 'verification/maxwell-session004/R045-input-budget-dissipation-independent', 'verification/maxwell-session004/R044-mass-participation-independent', 'verification/maxwell-session004/R046-narrative-paper-math-integration', 'ideation/maxwell-session004/R032-mass-participation-local-corollary', 'ideation/maxwell-session004/R033-input-budget-dissipation-corollary', 'writing/maxwell-session004/narrative-paper-v001', 'literature/maxwell-session004/R030-FNA-nonlinear-mode-coverage-source'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 head=subprocess.check_output([GIT,'rev-parse','HEAD'],cwd=R,text=True).strip()
 assert head=='fa302ee040925391a04c8a3f7b895f5d3f2a8e0e'
 assert not subprocess.check_output([GIT,'diff','--cached','--name-only'],cwd=R).strip()
 state=json.loads((S/'status.json').read_text('utf-8'))
 assert state['checkpoint_open'] and state['current_round']=='R023'
 assert datetime.now().astimezone()>=datetime.fromisoformat(state['next_git_eligible_after'])
 adopted=json.loads((S/'R023-adoption.json').read_text('utf-8'))
 for name,digest in adopted['checked_identities'].items():assert sha(R/name)==digest,name
 packages=adopted['publish_packages'];assert len(set(packages))==len(packages) and set(packages)<=ALLOWED
 paths=[p for name in packages for p in (B/name).iterdir() if p.is_file()]
 for name in adopted.get('comparison_subfolders',[]):
  assert name.endswith('/post-freeze-comparison') and name.rsplit('/',1)[0] in ALLOWED
  paths += [p for p in (B/name).iterdir() if p.is_file()]
 names='''status.json
plan.md
claims.md
runs.md
rounds/R022.md
rounds/R023.md
R022-publish-manifest.json
R022-index-qa.json
R022-push.json
R022-after-push-snapshot.json
R022-late-handoff.md
C040-root-review-v001.json
C040-adoption-v001.json
review_C040_root_v001.py
input-budget-dissipation-corollary-protocol-v001.md
R023-initial-snapshot.json
R023-root-review-v001.json
R023-adoption.json
review_R023_root.py
prepare_R023_publish.py
publish_R023.py
topic-cards/T-M001-v019.md
topic-cards/events.md
R023-现在能提前算什么上限.md
R023-C038-terminology-erratum-v001.md'''.splitlines()
 paths += [S/name for name in names]
 for name in adopted.get('additional_session_files',[]):
  assert name.startswith('R023-') or name.startswith('topic-cards/'),name
  paths.append(S/name)
 for name in adopted.get('manuscripts',[]):
  assert name=='papers/damping-output-boundaries/manuscript/maxwell-paper-narrative-v001.md'
  paths.append(R/name)
 changed=set(subprocess.check_output([GIT,'diff','--name-only','-z'],cwd=R).decode().split('\0'))
 untracked=set(subprocess.check_output([GIT,'ls-files','--others','--exclude-standard','-z'],cwd=R).decode().split('\0'))
 files=[];tables=0
 for p in sorted(set(paths)):
  name=p.relative_to(R).as_posix()
  if name not in changed|untracked:continue
  raw=p.read_bytes();assert len(raw)<1000000
  assert '/local-cache/' not in name and p.suffix in {'.md','.json','.py','.csv','.txt','.patch'},name
  txt=raw.decode('utf-8-sig')
  assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}',txt)
  if p.suffix!='.patch':assert all(line.rstrip(' \t')==line for line in txt.splitlines()),name
  if p.suffix=='.patch':
   import importlib.util
   spec=importlib.util.spec_from_file_location('diff011',S/'prepare_R011_publish.py');dm=importlib.util.module_from_spec(spec);spec.loader.exec_module(dm)
   dm.check_diff(p,R/'papers/damping-output-boundaries/manuscript/maxwell-paper-compact-v003.md',R/'papers/damping-output-boundaries/manuscript/maxwell-paper-compact-v004.md')
   assert all(line==' ' or line.rstrip(' \t')==line for line in txt.splitlines()),name
  elif p.suffix=='.json':json.loads(txt)
  elif p.suffix=='.py':ast.parse(txt)
  elif p.suffix=='.csv':
   rows=list(csv.reader(txt.splitlines()));assert rows and all(len(row)==len(rows[0]) for row in rows)
  elif p.suffix=='.md':
   for link in re.findall(r'\]\(([^\n)]+)\)',txt):
    if '://' not in link and not link.startswith('#'):assert (p.parent/link.split('#')[0]).resolve().exists(),(name,link)
   lines=txt.splitlines()
   for i,line in enumerate(lines):
    if re.fullmatch(r'\|[ \t:|\-]+\|',line) and i and lines[i-1].startswith('|'):
     count=lines[i-1].count('|');j=i
     while j<len(lines) and lines[j].startswith('|'):
      assert lines[j].count('|')==count,(name,j+1);j+=1
     tables+=1
  files.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md')=='93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
 result={'at':datetime.now().astimezone().isoformat(),'expected_head':head,'checks_passed':True,'files':files,'file_count':len(files),'total_bytes':sum(item['bytes'] for item in files),'markdown_tables_checked':tables,'explicit_format_exceptions':[],
 'scope':adopted['scope'],'exclusions':'All active packages, source originals/excerpts/page images, raw arrays/engineering data, unknown old dirty files.'}
 (S/'R023-publish-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({key:result[key] for key in ['checks_passed','file_count','total_bytes','markdown_tables_checked']}))
if __name__=='__main__':main()

