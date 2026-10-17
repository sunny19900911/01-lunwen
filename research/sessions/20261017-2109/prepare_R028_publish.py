"""R028 completed-only explicit preflight; raw data and active packages excluded."""
from pathlib import Path
from datetime import datetime
import ast,csv,hashlib,json,re,subprocess
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
GIT='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
ALLOWED={
'novelty/maxwell-session004/R034-final-science-scope',
'experiments/maxwell-session004/R029-final-science-data-scope'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 head=subprocess.check_output([GIT,'rev-parse','HEAD'],cwd=R,text=True).strip()
 assert head=='27fd2916156108a83d37d666abb9c9266fe40bc6'
 assert not subprocess.check_output([GIT,'diff','--cached','--name-only'],cwd=R).strip()
 state=json.loads((S/'status.json').read_text('utf-8'));assert state['checkpoint_open'] and state['current_round']=='R028'
 assert datetime.now().astimezone()>=datetime.fromisoformat(state['next_git_eligible_after'])
 assert datetime.now().astimezone()>=datetime.fromisoformat(state['deadline']) # final closure only after real hard cutoff
 adopted=json.loads((S/'R028-adoption.json').read_text('utf-8'))
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
rounds/R027.md
rounds/R028.md
R027-publish-manifest.json
R027-index-qa.json
R027-push.json
R027-prepublish-snapshot.json
R027-late-handoff.md
final-summary-science-candidate-v001.md
review_R028_science.py
R028-science-review-v001.json
R028-adoption.json
create_R028_cutoff_files.py
R028-closeout-instructions-v001.md
prepare_R028_publish.py
publish_R028.py
final-summary.md
R028-cutoff-snapshot.json
R028-preclose-snapshot.json
topic-cards/T-M001-v023.md
topic-cards/events.md'''.splitlines()
 paths += [S/name for name in names]
 for name in adopted.get('manuscripts',[]):
  assert name=='papers/damping-output-boundaries/manuscript/maxwell-paper-narrative-v003.md'
  paths.append(R/name)
 paths.append(R/'docs/Maxwell六角色协作-20261017.md')
 changed=set(subprocess.check_output([GIT,'diff','--name-only','-z'],cwd=R).decode().split('\0'))
 untracked=set(subprocess.check_output([GIT,'ls-files','--others','--exclude-standard','-z'],cwd=R).decode().split('\0'))
 files=[];tables=0;display=[]
 for p in sorted(set(paths)):
  name=p.relative_to(R).as_posix()
  if name not in changed|untracked:continue
  raw=p.read_bytes();assert len(raw)<1000000
  assert '/local-cache/' not in name and p.suffix in {'.md','.json','.py','.csv','.txt','.patch','.diff'},name
  txt=raw.decode('utf-8-sig')
  assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}',txt)
  if p.suffix not in {'.patch','.diff'}:assert all(line.rstrip(' \t')==line for line in txt.splitlines()),name
  if p.suffix in {'.patch','.diff'}:
   import importlib.util
   spec=importlib.util.spec_from_file_location('diff011',S/'prepare_R011_publish.py');dm=importlib.util.module_from_spec(spec);spec.loader.exec_module(dm)
   oldname,newname=adopted['patch_pairs'][name];dm.check_diff(p,R/oldname,R/newname)
   assert all(line==' ' or line.rstrip(' \t')==line for line in txt.splitlines()),name
  elif p.suffix=='.json':json.loads(txt)
  elif p.suffix=='.py':ast.parse(txt)
  elif p.suffix=='.csv':
   rows=list(csv.reader(txt.splitlines()));assert rows and all(len(row)==len(rows[0]) for row in rows)
  elif p.suffix=='.md':
   for link in re.findall(r'\]\(([^\n)]+)\)',txt):
    if '://' not in link and not link.startswith('#'):assert (p.parent/link.split('#')[0]).resolve().exists(),(name,link)
   table_view=txt
   lines=table_view.splitlines()
   for i,line in enumerate(lines):
    if re.fullmatch(r'\|[ \t:|\-]+\|',line) and i and lines[i-1].startswith('|'):
     count=lines[i-1].count('|');j=i
     while j<len(lines) and lines[j].startswith('|'):
      assert lines[j].count('|')==count,(name,j+1);j+=1
     tables+=1
  files.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md')=='93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
 result={'at':datetime.now().astimezone().isoformat(),'expected_head':head,'checks_passed':True,'files':files,'file_count':len(files),'total_bytes':sum(item['bytes'] for item in files),'markdown_tables_checked':tables,
 'explicit_format_exceptions':[{'path':name,'rule':'Unified context exactly checked against both source files'} for name in adopted['patch_pairs'] if name in [item['path'] for item in files]],'frozen_table_display_views':display,
 'scope':adopted['scope'],'exclusions':'All active packages, source originals/excerpts/page images, raw arrays/engineering data, unknown old dirty files.'}
 (S/'R028-publish-manifest.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
 print(json.dumps({key:result[key] for key in ['checks_passed','file_count','total_bytes','markdown_tables_checked']}))
if __name__=='__main__':main()
