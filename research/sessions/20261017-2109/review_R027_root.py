"""R027 finite source and minimal-diff review; no scientific rerun."""
from pathlib import Path
from datetime import datetime
import ast,csv,difflib,hashlib,json,re
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
PACKAGES=['literature/maxwell-session004/R033-Goetz-unread-pages','novelty/maxwell-session004/R033-Goetz-page-scope-review','writing/maxwell-session004/narrative-v003','verification/maxwell-session004/R052-narrative-v003-integration']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=S/'R027-root-review-v001.json';assert not out.exists()
 ids={};local={}
 def add(p):
  p=p.resolve();name=p.relative_to(R).as_posix();raw=p.read_bytes()
  if '/local-cache/' in name:
   assert 'Goetz2013' in name and p.suffix in {'.pdf','.txt','.png'} and len(raw)<2000000
   local[name]=hashlib.sha256(raw).hexdigest();return
  assert p.suffix in {'.md','.json','.py','.patch'} and len(raw)<1000000
  txt=raw.decode('utf-8-sig')
  if p.suffix=='.json':json.loads(txt)
  if p.suffix=='.py':ast.parse(txt)
  ids[name]=hashlib.sha256(raw).hexdigest()
 def records(obj,parent):
  if isinstance(obj,dict):
   name=obj.get('path',obj.get('file'))
   if isinstance(name,str) and isinstance(obj.get('sha256'),str):
    p=Path(name)
    if not p.is_absolute():p=R/name if (R/name).exists() else parent/name
    add(p);assert sha(p)==obj['sha256'],name
    if 'bytes' in obj:assert p.stat().st_size==obj['bytes'],name
   for value in obj.values():records(value,parent)
  elif isinstance(obj,list):
   for value in obj:records(value,parent)
 for pkg in PACKAGES:
  for p in (B/pkg).iterdir():
   if p.is_file():
    add(p)
    if p.suffix=='.json':records(json.loads(p.read_text('utf-8-sig')),p.parent)
 for n in ['Goetz2013-unread-pages-review-protocol-v001.md','Goetz-unread-pages-root-note-v001.md','Goetz-unread-pages-root-read-v001.json','R027-narrative-diff-root-v001.json']:
  add(S/n)
 oldpath=R/'papers/damping-output-boundaries/manuscript/maxwell-paper-narrative-v002.md';newpath=R/'papers/damping-output-boundaries/manuscript/maxwell-paper-narrative-v003.md'
 old=oldpath.read_text('utf-8');new=newpath.read_text('utf-8');add(oldpath);add(newpath)
 expected=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=oldpath.name,tofile=newpath.name))
 for p in [B/PACKAGES[2]/'diff-from-v002.patch',B/PACKAGES[3]/'independent-diff-from-v002.patch']:assert p.read_text('utf-8')==expected
 paragraph=next(x for x in new.splitlines() if x.startswith('对同一器件，若'))
 assert new.replace(paragraph+'\n\n','',1).replace('叙述稿候选 v003','叙述稿候选 v002',1).encode()==oldpath.read_bytes()
 assert re.findall(r'\$\$(.*?)\$\$',old,re.S)==re.findall(r'\$\$(.*?)\$\$',new,re.S)
 assert sha(newpath)=='12d9df37e5b281599b8f84e76853aa7413e951aad378f53a95b4706e968279a9'
 assert json.loads((B/PACKAGES[3]/'validation.json').read_text('utf-8'))['must_fix_count']==0
 assert json.loads((B/PACKAGES[1]/'validation.json').read_text('utf-8'))['result']=='0 mustfix'
 primary=R/'papers/damping-output-boundaries/research/roles/novelty/maxwell-session004/R027-RL-equivalent-prior-art/local-cache/Goetz2013.pdf'
 assert sha(primary)=='6e7449324392802c8351138e3643fae8e966e89c34352a32cb2824d5b118e63f'
 result={'at':datetime.now().astimezone().isoformat(),'checked_identities':ids,'finite_authored_identity_count':len(ids),'local_original_asset_identities_verified':local,'local_assets_not_published':True,
 'primary_source_read_levels':{'master':'Independently text-read3-6/12 and visually reviewed3-6 before role3 report; page12 text only','role3':'New original text/images3-6/12, old pages inherited only','role6':'Independently original text/images4-6/12; page3 report/root-note comparison only','cited_refs28_29':'Bibliography only, no bodies or new search'},
 'source_scope_review':'Root full new report/read-scope metadata and own original pages agree with role6 bounded0must; LI-prime cap/numerical/neuron/bibliography scope preserved. No exact same-condition publication coverage established, no priority claim.',
 'manuscript_review':'Root full new paragraph/exactdiff and section2 definitions plus R052 limited integration0must; all remaining core content inherited earlier reviewed v002, not re-proved',
 'exact_diff_and_reverse':True,'formula_blocks_unchanged':10,'actual_main_table_blocks_unchanged':1,'actual_main_table_data_rows':[4],'image_unchanged':1,
 'positive_terminal':'F(T)=h plus existing h>0, with inherited V and h<B, restricts positive branch; later optional explicit wording arrived after author freeze, original preserved',
 'not_claimed':['continuous fixed-D peak image','new engineering validation','new theorem or publication priority','new source reference-body review','current-window final closure'],
 'metadata_does_not_substitute_math_or_source_reading':True,'new_scientific_code_ODE_arrays_network_or_solver':False}
 out.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'pass':True,'authored_identities':len(ids),'local_asset_identities_only':len(local)}))
if __name__=='__main__':main()
