"""Explicit R019 scientific-figure/source/manuscript publication preflight."""
from pathlib import Path
from datetime import datetime
import ast,csv,hashlib,importlib.util,json,re,struct,subprocess,xml.etree.ElementTree as ET
S=Path(__file__).resolve().parent;R=S.parents[2]
B=R/'papers/damping-output-boundaries/research/roles'
GIT='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'
NODE='C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
CORE_FOLDERS=['writing/maxwell-session004/C025-layout-explanation-figure-v001','experiments/maxwell-session004/R024-C025-figure-review','novelty/maxwell-session004/R022-Correia-Maxwell-prior-art-review']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 head=subprocess.check_output([GIT,'rev-parse','HEAD'],cwd=R,text=True).strip()
 assert head=='b80475bc6255c97b43d106e276a8efbe74b8ade1'
 assert not subprocess.check_output([GIT,'diff','--cached','--name-only'],cwd=R).strip()
 state=json.loads((S/'status.json').read_text('utf-8'))
 assert state['checkpoint_open'] and state['current_round']=='R019'
 assert datetime.now().astimezone()>=datetime.fromisoformat(state['next_git_eligible_after'])
 adopted=json.loads((S/'R019-adoption.json').read_text('utf-8'))
 for item in adopted['review_records']:
  assert sha(S/item['path'])==item['sha256'],item['path']
 for name,expected in adopted['checked_identities'].items():assert sha(R/name)==expected,name
 paths=[p for name in CORE_FOLDERS for p in (B/name).iterdir() if p.is_file()]
 names='''status.json
plan.md
claims.md
runs.md
rounds/R018.md
rounds/R019.md
R018-publish-manifest.json
R018-index-qa.json
R018-push.json
R018-after-push-snapshot.json
R018-late-handoff.md
R019-initial-snapshot.json
R019-core-root-review.json
R019-core-adoption.json
R019-adoption.json
R019-root-review.json
review_R019_integrations.py
R019-C037-readable-table.md
R019-source-snapshots/claims-read-before-R019.md
R019-source-snapshots/mapping.json
topic-cards/T-M001-v016.md
topic-cards/events.md
prepare_R019_publish.py
publish_R019.py'''.splitlines()
 paths += [S/name for name in names]
 for item in adopted.get('additional_frozen_files',[]):
  p=R/item['path'];assert sha(p)==item['sha256'];paths.append(p)
 spec=importlib.util.spec_from_file_location('diff011',S/'prepare_R011_publish.py')
 diffmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(diffmod)
 files=[];tables=0;exceptions=[]
 for p in sorted(set(paths)):
  name=p.relative_to(R).as_posix();raw=p.read_bytes()
  assert '/local-cache/' not in name and p.suffix in {'.md','.json','.py','.csv','.txt','.diff','.png','.svg','.cjs'},name
  assert len(raw)<1000000,name
  if p.suffix=='.png':
   assert raw[:8]==b'\x89PNG\r\n\x1a\n';assert struct.unpack('>II',raw[16:24])==(2400,1680)
   assert sha(p)=='34bfaf854d8d5415a0fa7ccdce907a81a6687da5584fd9c0e0aed3616f90f7a6'
  else:
   text=raw.decode('utf-8-sig')
   assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}',text)
   if p.suffix=='.diff':
    assert p.name=='v002-to-v003.diff',name
    result=diffmod.check_diff(p,R/'papers/damping-output-boundaries/manuscript/maxwell-paper-compact-v002.md',R/'papers/damping-output-boundaries/manuscript/maxwell-paper-compact-v003.md')
    exceptions.append(result)
    assert all(line==' ' or line.rstrip(' \t')==line for line in text.splitlines())
   else:assert all(line.rstrip(' \t')==line for line in text.splitlines()),name
   if p.suffix=='.py':ast.parse(text)
   elif p.suffix=='.cjs':subprocess.run([NODE,'--check',str(p)],check=True,capture_output=True)
   elif p.suffix=='.json':json.loads(text)
   elif p.suffix=='.csv':
    rows=list(csv.reader(text.splitlines()));assert rows and all(len(row)==len(rows[0]) for row in rows),name
   elif p.suffix=='.svg':
    tree=ET.fromstring(raw);assert not any(el.tag.split('}')[-1].lower() in ['script','foreignobject'] for el in tree.iter())
    assert sha(p)=='f770ccb7ef4af2baeecbb89c03b7421d128d585780c7603d14a5e93b7fe3bf6d'
    exceptions.append({'path':name,'originalCRLF_preserved':True,'SVGactual_pixels_root_and_independent_reviewed':True})
   elif p.suffix=='.md':
    for link in re.findall(r'\]\(([^\n)]+)\)',text):
     if '://' not in link and not link.startswith('#'):
      linkparent=p.parent
      if name.endswith('/R019-source-snapshots/claims-read-before-R019.md'):
       assert sha(p)=='8140c0690e9195809cb3b1e2d718e48149bff92e5a0d824d66a99063517c3a30'
       linkparent=S
      assert (linkparent/link.split('#')[0]).resolve().exists(),(name,link)
    lines=text.splitlines()
    if name.endswith('/R039-finite-observation-neighbor-review/report.md'):
     assert sha(p)=='9284538b25e4253908846f34fccaa11ac6ac0dabe4cccf72afda5224cb32031b'
     assert sum('sup_[0,H]差/|a|的上界Li(H)' in line for line in lines)==1
     lines=[line.replace('sup_[0,H]差/|a|的上界Li(H)','sup_[0,H]差/a绝对值的上界Li(H)') for line in lines]
     exceptions.append({'path':name,'frozen_math_pipe_header_retained':True,'readable_addendum':'R019-C037-readable-table.md','no_source_byte_mutation':True})
    for i,line in enumerate(lines):
     if re.fullmatch(r'\|[ \t:|\-]+\|',line) and i and lines[i-1].startswith('|'):
      count=lines[i-1].count('|');j=i
      while j<len(lines) and lines[j].startswith('|'):
       assert lines[j].count('|')==count,(name,j+1);j+=1
      tables+=1
  files.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
 assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md')=='93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
 result={'at':datetime.now().astimezone().isoformat(),'expected_head':head,'checks_passed':True,'files':files,'file_count':len(files),'total_bytes':sum(item['bytes'] for item in files),'markdown_tables_checked':tables,'explicit_format_exceptions':exceptions,
 'scope':adopted['publish_scope'],'exclusions':'All active unreviewed packages,source PDF/pagecache,rawarrays/Excel,old dirty/unknown files.'}
 (S/'R019-publish-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({key:result[key] for key in ['checks_passed','file_count','total_bytes','markdown_tables_checked']}))
if __name__=='__main__':main()

