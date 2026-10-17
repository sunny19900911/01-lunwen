
"""Explicit R025 preflight, only completed reviewed packages named in adoption."""
from pathlib import Path
from datetime import datetime
import ast,csv,hashlib,json,re,subprocess
S=Path(__file__).resolve().parent;R=S.parents[2]
B=R/'papers/damping-output-boundaries/research/roles'
GIT='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
ALLOWED={'novelty/maxwell-session004/R030-handoff-plain-and-priorart-review','ideation/maxwell-session004/R034-continuous-velocity-endpoints', 'verification/maxwell-session004/R048-continuous-velocity-independent', 'experiments/maxwell-session004/R027-plain-summary-engineering-review', 'verification/maxwell-session004/R049-continuous-velocity-appendix-integration', 'novelty/maxwell-session004/R029-plain-summary-contribution-review', 'writing/maxwell-session004/continuous-velocity-endpoints-v001', 'literature/maxwell-session004/R032-public-candidate-original'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 head=subprocess.check_output([GIT,'rev-parse','HEAD'],cwd=R,text=True).strip()
 assert head=='bdb7828fc43cef94fba05fea1c683de099201931'
 assert not subprocess.check_output([GIT,'diff','--cached','--name-only'],cwd=R).strip()
 state=json.loads((S/'status.json').read_text('utf-8'))
 assert state['checkpoint_open'] and state['current_round']=='R025'
 assert datetime.now().astimezone()>=datetime.fromisoformat(state['next_git_eligible_after'])
 adopted=json.loads((S/'R025-adoption.json').read_text('utf-8'))
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
rounds/R024.md
rounds/R025.md
R024-publish-manifest.json
R024-index-qa.json
R024-push.json
R024-after-push-snapshot.json
R024-late-handoff.md
C042-adoption-v001.json
review_C042_adoption.py
continuous-velocity-endpoint-protocol-v001.md
continuous-velocity-root-candidate-v001.md
continuous-velocity-root-core-v001.json
R025-initial-snapshot.json
R025-root-review-v001.json
R025-adoption.json
review_R025_root.py
prepare_R025_publish.py
publish_R025.py
阶段结论-白话-v001.md
阶段结论-白话-v002.md
阶段结论-白话-v002.diff
R025-plain-summary-v002-repair.json
R025-preflight-math-token-correction.json
R025-frozen-table-display-addendum.md
同条件排重-结论表-v001.md
topic-cards/T-M001-v021.md
topic-cards/events.md'''.splitlines()
 paths += [S/name for name in names]
 for name in adopted.get('additional_session_files',[]):
  assert name.startswith('R025-') or name.startswith('topic-cards/'),name
  paths.append(S/name)
 for name in adopted.get('manuscripts',[]):
  assert name=='papers/damping-output-boundaries/manuscript/maxwell-continuous-velocity-endpoints-v001.md'
  paths.append(R/name)
 paths.append(R/'docs/Maxwell六角色协作-20261017.md')
 changed=set(subprocess.check_output([GIT,'diff','--name-only','-z'],cwd=R).decode().split('\0'))
 untracked=set(subprocess.check_output([GIT,'ls-files','--others','--exclude-standard','-z'],cwd=R).decode().split('\0'))
 files=[];tables=0
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
   oldname,newname=adopted['patch_pairs'][name]
   dm.check_diff(p,R/oldname,R/newname)
   assert all(line==' ' or line.rstrip(' \t')==line for line in txt.splitlines()),name
  elif p.suffix=='.json':json.loads(txt)
  elif p.suffix=='.py':ast.parse(txt)
  elif p.suffix=='.csv':
   rows=list(csv.reader(txt.splitlines()));assert rows and all(len(row)==len(rows[0]) for row in rows)
  elif p.suffix=='.md':
   link_view=txt
   if name=='papers/damping-output-boundaries/research/roles/verification/maxwell-session004/R048-continuous-velocity-independent/report.md':
    assert sha(p)=='fb2868540d569662bf991a1147ff26f98b8022aae2c6d0730c66f4bf68287312'
    formula='    z(T)=κ∫₀ᵀexp[−κ∫ₛᵀa(u)du](v₁−v₂)(s)ds>0.'
    assert txt.count(formula)==1
    link_view=txt.replace(formula,'') # frozen indented formula, not a Markdown link
   for link in re.findall(r'\]\(([^\n)]+)\)',link_view):
    if '://' not in link and not link.startswith('#'):assert (p.parent/link.split('#')[0]).resolve().exists(),(name,link)
   table_view=txt
   if name=='papers/damping-output-boundaries/research/roles/verification/maxwell-session004/R049-continuous-velocity-appendix-integration/report.md':
    assert sha(p)=='ac1a7f080880de0a1b04f1d40f972d6e8b40df008e9927a6cad48bd75f1a2888'
    assert txt.count('κ||Δv||₁')==1
    table_view=txt.replace('κ||Δv||₁','κ‖Δv‖₁') # display-only supplement linked in session
   lines=table_view.splitlines()
   for i,line in enumerate(lines):
    if re.fullmatch(r'\|[ \t:|\-]+\|',line) and i and lines[i-1].startswith('|'):
     count=lines[i-1].count('|');j=i
     while j<len(lines) and lines[j].startswith('|'):
      assert lines[j].count('|')==count,(name,j+1);j+=1
     tables+=1
  files.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md')=='93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
 result={'at':datetime.now().astimezone().isoformat(),'expected_head':head,'checks_passed':True,'files':files,'file_count':len(files),'total_bytes':sum(item['bytes'] for item in files),'markdown_tables_checked':tables,'explicit_format_exceptions':[{'path':name,'rule':'one-space unified context verified against both original files'} for name in adopted['patch_pairs'] if name in [item['path'] for item in files]],
 'scope':adopted['scope'],'exclusions':'All active packages, source originals/excerpts/page images, raw arrays/engineering data, unknown old dirty files.'}
 (S/'R025-publish-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({key:result[key] for key in ['checks_passed','file_count','total_bytes','markdown_tables_checked']}))
if __name__=='__main__':main()

