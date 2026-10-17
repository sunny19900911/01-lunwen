
"""Explicit R020 preflight; no active packages or primary-source caches."""
from pathlib import Path
from datetime import datetime
import ast,csv,hashlib,json,re,subprocess
S=Path(__file__).resolve().parent;R=S.parents[2]
B=R/'papers/damping-output-boundaries/research/roles'
GIT='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
FOLDERS=[
'ideation/maxwell-session004/R029-fixed-dissipation-peak-inverse',
'verification/maxwell-session004/R040-fixed-D-inverse-independent',
'verification/maxwell-session004/R040-fixed-D-inverse-independent/post-freeze-comparison',
'literature/maxwell-session004/R027-nonzero-terminal-dissipation-prior-art',
'writing/maxwell-session004/finite-observation-appendix-v001',
'novelty/maxwell-session004/R024-finite-observation-appendix-review']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 head=subprocess.check_output([GIT,'rev-parse','HEAD'],cwd=R,text=True).strip()
 assert head=='0fd3cd482e871e08e69677cb7713731eea2389c1'
 assert not subprocess.check_output([GIT,'diff','--cached','--name-only'],cwd=R).strip()
 state=json.loads((S/'status.json').read_text('utf-8'))
 assert state['checkpoint_open'] and state['current_round']=='R020'
 assert datetime.now().astimezone()>=datetime.fromisoformat(state['next_git_eligible_after'])
 adopted=json.loads((S/'R020-adoption.json').read_text('utf-8'))
 for name,digest in adopted['checked_identities'].items():assert sha(R/name)==digest,name
 paths=[p for name in FOLDERS for p in (B/name).iterdir() if p.is_file()]
 names='''status.json
plan.md
claims.md
runs.md
rounds/R019.md
rounds/R020.md
R019-publish-manifest.json
R019-index-qa.json
R019-push.json
R019-after-push-snapshot.json
R019-late-handoff.md
R020-role-snapshot.json
fixed-dissipation-peak-inverse-protocol-v001.md
R020-core-root-review.json
R020-C038-adoption.json
R020-prior-art-root-review.json
R020-adoption.json
review_R020_integrations.py
topic-cards/T-M001-v017.md
topic-cards/events.md
prepare_R020_publish.py
publish_R020.py'''.splitlines()
 paths += [S/name for name in names]
 paths += [R/'papers/damping-output-boundaries/manuscript/maxwell-finite-observation-appendix-v001.md']
 changed=set(subprocess.check_output([GIT,'diff','--name-only','-z'],cwd=R).decode().split('\0'))
 untracked=set(subprocess.check_output([GIT,'ls-files','--others','--exclude-standard','-z'],cwd=R).decode().split('\0'))
 files=[];tables=0
 for p in sorted(set(paths)):
  name=p.relative_to(R).as_posix()
  if name not in changed|untracked:continue
  raw=p.read_bytes();assert len(raw)<1000000
  assert '/local-cache/' not in name and p.suffix in {'.md','.json','.py','.csv','.txt'},name
  txt=raw.decode('utf-8-sig')
  assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}',txt)
  assert all(line.rstrip(' \t')==line for line in txt.splitlines()),name
  if p.suffix=='.json':json.loads(txt)
  elif p.suffix=='.py':ast.parse(txt)
  elif p.suffix=='.csv':
   rows=list(csv.reader(txt.splitlines()));assert rows and all(len(row)==len(rows[0]) for row in rows)
  elif p.suffix=='.md':
   for link in re.findall(r'\]\(([^\n)]+)\)',txt):
    if '://' not in link and not link.startswith('#'):
     assert (p.parent/link.split('#')[0]).resolve().exists(),(name,link)
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
 'scope':'Reviewed fixed-D analytic inverse, C037 appendix integration and bounded prior-art positioning; routine master receipts. Active new fixed-D manuscript excluded.',
 'exclusions':'Primary originals/page images/excerpts, raw engineering/array data, active packages and all old dirty/unknown files.'}
 (S/'R020-publish-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({key:result[key] for key in ['checks_passed','file_count','total_bytes','markdown_tables_checked']}))
if __name__=='__main__':main()

