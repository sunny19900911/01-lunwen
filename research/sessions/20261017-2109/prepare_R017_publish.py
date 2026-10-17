"""R017 explicit completed package preflight. No Git mutation."""
from pathlib import Path
from datetime import datetime
import ast,csv,hashlib,importlib.util,json,re,subprocess
S=Path(__file__).resolve().parent
R=S.parents[2]
B=R/'papers/damping-output-boundaries/research/roles'
GIT='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 head=subprocess.check_output([GIT,'rev-parse','HEAD'],cwd=R,text=True).strip()
 assert head=='b62314a4c519160ed43ce1f439552b7b4d501a42'
 assert not subprocess.check_output([GIT,'diff','--cached','--name-only'],cwd=R).strip()
 state=json.loads((S/'status.json').read_text('utf-8'))
 assert state['checkpoint_open'] and state['current_round']=='R017'
 assert datetime.now().astimezone()>=datetime.fromisoformat(state['next_git_eligible_after'])
 adopted=json.loads((S/'R017-adoption.json').read_text('utf-8'))
 assert sha(S/'R017-root-review.json')==adopted['root_review']['sha256']
 for name,expected in adopted['checked_identities'].items():assert sha(R/name)==expected,name
 spec=importlib.util.spec_from_file_location('review017',S/'review_R017_integrations.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 paths=[p for name in mod.FOLDERS for p in (B/name).iterdir() if p.is_file()]
 paths += [R/'papers/damping-output-boundaries/manuscript'/f'maxwell-paper-compact-{v}.md' for v in ['v001','v002']]
 names='''status.json
plan.md
claims.md
runs.md
rounds/R016.md
rounds/R017.md
R016-index-qa.json
R016-push.json
R016-after-push-snapshot.json
R016-late-handoff.md
R017-initial-snapshot.json
R017-midpoint-handoff-snapshot.json
R017-root-review.json
R017-adoption.json
review_R017_integrations.py
prepare_R017_publish.py
publish_R017.py
forward-midpoint-synthetic-protocol-v001.md'''.splitlines()
 paths += [S/name for name in names]
 files=[];tables=0
 diff=S.parents[2]/'papers/damping-output-boundaries/research/roles/writing/maxwell-session004/compact-paper-v002/v001-to-v002.diff'
 for p in sorted(set(paths)):
  name=p.relative_to(R).as_posix();raw=p.read_bytes()
  assert '/local-cache/' not in name and p.suffix in {'.md','.json','.py','.csv','.txt','.diff'},name
  assert len(raw)<1000000
  text=raw.decode('utf-8-sig')
  assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}',text)
  if p==diff:
   assert sha(p)=='d805e850f0fdd387ce91b14a4e2d48e604ce24db7991863fdefff803de0c6eeb'
   assert all(line==' ' or line.rstrip(' \t')==line for line in text.splitlines())
  else:assert all(line.rstrip(' \t')==line for line in text.splitlines()),name
  if p.suffix=='.py':ast.parse(text)
  elif p.suffix=='.json':json.loads(text)
  elif p.suffix=='.csv':
   rows=list(csv.reader(text.splitlines()));assert rows and all(len(row)==len(rows[0]) for row in rows),name
  elif p.suffix=='.md':
   for link in re.findall(r'\]\(([^\n)]+)\)',text):
    if '://' not in link and not link.startswith('#'):
     # Frozen R035 inline mathematical indicator is not a Markdown reference.
     if name.endswith('R035-compact-math-review/report.md') and link=='t':
      assert sha(p)=='cf171cdee88e63a50a7457a18846d21517e127762a62c35fce5b834fa30b4840'
      assert '1_[0,20π](t)' in text
      continue
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
 'scope':'Reviewed classical BE math and limited implementation with explicit failed fine-u1 gate;compact-v001 hold history plus independently repaired v002. Separate midpoint protocol candidate only.',
 'exclusions':'Active midpoint work;all arrays/originals/cache/fulltexts,all old dirty and unknown files.'}
 (S/'R017-publish-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({key:result[key] for key in ['checks_passed','file_count','total_bytes','markdown_tables_checked']}))
if __name__=='__main__':main()

