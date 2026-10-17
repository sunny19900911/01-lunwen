"""R026 completed-only explicit preflight; raw data and active packages excluded."""
from pathlib import Path
from datetime import datetime
import ast,csv,hashlib,json,re,subprocess
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
GIT='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
ALLOWED={
'ideation/maxwell-session004/R035-continuous-cost-image',
'verification/maxwell-session004/R050-continuous-cost-image-independent',
'verification/maxwell-session004/R051-continuous-cost-image-integration',
'experiments/maxwell-session004/R028-session-receipt-audit',
'novelty/maxwell-session004/R031-final-handoff-scope',
'novelty/maxwell-session004/R032-final-handoff-v002',
'writing/maxwell-session004/continuous-cost-image-v001'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 head=subprocess.check_output([GIT,'rev-parse','HEAD'],cwd=R,text=True).strip()
 assert head=='80d4bfab066a8399c0ffd2f4051495a7469c3632'
 assert not subprocess.check_output([GIT,'diff','--cached','--name-only'],cwd=R).strip()
 state=json.loads((S/'status.json').read_text('utf-8'));assert state['checkpoint_open'] and state['current_round']=='R026'
 assert datetime.now().astimezone()>=datetime.fromisoformat(state['next_git_eligible_after'])
 adopted=json.loads((S/'R026-adoption.json').read_text('utf-8'))
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
rounds/R025.md
rounds/R026.md
R025-publish-manifest.json
R025-index-qa.json
R025-push.json
R025-after-push-snapshot.json
R025-late-handoff.md
continuous-velocity-cost-image-protocol-v001.md
continuous-cost-image-root-candidate-v001.md
continuous-cost-image-root-core-v001.json
C043-root-review-v001.json
C043-adoption-v001.json
review_C043_adoption.py
R026-receipt-root-audit-v001.json
R026-receipt-csv-comparison-v001.json
R026-R025-preflight-completion-addendum.json
R026-frozen-table-display-addendum.md
最终交付说明-候选-v001.md
最终交付说明-候选-v002.md
最终交付说明-候选-v002.diff
R026-handoff-v002-repair.json
R026-scheduler-preclose-audit.json
待用户决定-本轮收束-v001.md
review_R026_root.py
R026-root-review-v001.json
R026-adoption.json
prepare_R026_publish.py
publish_R026.py
R026-prepublish-snapshot.json
topic-cards/T-M001-v022.md
topic-cards/events.md'''.splitlines()
 paths += [S/name for name in names]
 for name in adopted.get('manuscripts',[]):
  assert name=='papers/damping-output-boundaries/manuscript/maxwell-continuous-cost-image-v001.md'
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
   if name=='papers/damping-output-boundaries/research/roles/verification/maxwell-session004/R050-continuous-cost-image-independent/post-freeze-comparison/report.md':
    assert sha(p)=='f64e2a9c0d83c16530603f9bd75b3812f74e7c1c9c991a930bb3f91ee620c283'
    assert txt.count('||Δv||₁')==2
    table_view=txt.replace('||Δv||₁','‖Δv‖₁')
    display.append({'path':name,'sha256':sha(p),'view_only':'Two ASCII norm tokens in one frozen table row; readable session addendum; original unchanged'})
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
 (S/'R026-publish-manifest.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
 print(json.dumps({key:result[key] for key in ['checks_passed','file_count','total_bytes','markdown_tables_checked']}))
if __name__=='__main__':main()
