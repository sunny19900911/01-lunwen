"""R018 explicit reviewed frozen package preflight; no index/network mutation."""
from pathlib import Path
from datetime import datetime
import ast,csv,hashlib,importlib.util,json,re,subprocess
S=Path(__file__).resolve().parent;R=S.parents[2]
B=R/'papers/damping-output-boundaries/research/roles'
GIT='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 head=subprocess.check_output([GIT,'rev-parse','HEAD'],cwd=R,text=True).strip()
 assert head=='31d4520fe8463d755d415250518f990983847c45'
 assert not subprocess.check_output([GIT,'diff','--cached','--name-only'],cwd=R).strip()
 state=json.loads((S/'status.json').read_text('utf-8'))
 assert state['checkpoint_open'] and state['current_round']=='R018'
 assert datetime.now().astimezone()>=datetime.fromisoformat(state['next_git_eligible_after'])
 adopted=json.loads((S/'R018-adoption.json').read_text('utf-8'))
 assert sha(S/'R018-root-review.json')==adopted['root_review']['sha256']
 for name,expected in adopted['checked_identities'].items():assert sha(R/name)==expected,name
 spec=importlib.util.spec_from_file_location('review018',S/'review_R018_integrations.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 paths=[p for name in mod.FOLDERS for p in (B/name).iterdir() if p.is_file()]
 paths += [R/'papers/damping-output-boundaries/manuscript/maxwell-engineering-validation-plan-v001.md']
 names='''status.json
plan.md
claims.md
runs.md
rounds/R017.md
rounds/R018.md
topic-cards/T-M001-v015.md
topic-cards/events.md
R017-publish-manifest.json
R017-index-qa.json
R017-push.json
R017-after-push-snapshot.json
R017-late-handoff.md
R018-initial-snapshot.json
R018-root-review.json
R018-adoption.json
review_R018_integrations.py
prepare_R018_publish.py
publish_R018.py
independent-midpoint-fine-replay-protocol-v001.md'''.splitlines()
 names.append('finite-observation-neighbor-protocol-v001.md')
 paths += [S/name for name in names]
 for entry in adopted.get('additional_frozen_files',[]):
  p=R/entry['path'];assert sha(p)==entry['sha256'];paths.append(p)
 files=[];tables=0
 for p in sorted(set(paths)):
  name=p.relative_to(R).as_posix();raw=p.read_bytes()
  assert '/local-cache/' not in name and p.suffix in {'.md','.json','.py','.csv','.txt'},name
  assert len(raw)<1000000
  text=raw.decode('utf-8-sig')
  assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}',text)
  assert all(line.rstrip(' \t')==line for line in text.splitlines()),name
  if p.suffix=='.py':ast.parse(text)
  elif p.suffix=='.json':json.loads(text)
  elif p.suffix=='.csv':
   rows=list(csv.reader(text.splitlines()));assert rows and all(len(row)==len(rows[0]) for row in rows),name
  elif p.suffix=='.md':
   for link in re.findall(r'\]\(([^\n)]+)\)',text):
    if '://' not in link and not link.startswith('#'):
     assert (p.parent/link.split('#')[0]).resolve().exists(),(name,link)
   lines=text.splitlines()
   for i,line in enumerate(lines):
    if re.fullmatch(r'\|[ \t:|\-]+\|',line) and i and lines[i-1].startswith('|'):
     count=lines[i-1].count('|');j=i
     while j<len(lines) and lines[j].startswith('|'):
      assert lines[j].count('|')==count,(name,j+1);j+=1
     tables+=1
  files.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md')=='93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
 result={'at':datetime.now().astimezone().isoformat(),'expected_head':head,'checks_passed':True,'files':files,
 'file_count':len(files),'total_bytes':sum(item['bytes'] for item in files),'markdown_tables_checked':tables,
 'scope':'Reviewed classical midpoint math/finite diagnostic and real engineering paired-validation plan. Additional audits only when frozen and explicitly adopted.',
 'exclusions':'All active packages and arrays/originals/cache/fulltexts,old dirty and unknown files.'}
 (S/'R018-publish-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({key:result[key] for key in ['checks_passed','file_count','total_bytes','markdown_tables_checked']}))
if __name__=='__main__':main()

