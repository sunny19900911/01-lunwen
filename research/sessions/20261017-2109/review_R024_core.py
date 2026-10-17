"""R024 immutable root diff review; supplementary peer binding must use a new file."""
from pathlib import Path
from datetime import datetime
import difflib,hashlib,importlib.util,json,re
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles';M=R/'papers/damping-output-boundaries/manuscript'
OUT=S/'R024-core-review-v001.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists()
 spec=importlib.util.spec_from_file_location('identity020',S/'review_R020_integrations.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 checked={}
 folders=['writing/maxwell-session004/narrative-paper-v002','literature/maxwell-session004/R031-total-voltage-RL-prior-art']
 for name in folders:
  d=B/name
  for p in d.iterdir():
   if p.is_file() and p.suffix=='.json':m.verify(json.loads(p.read_text('utf-8-sig')),d,checked)
   if p.is_file():checked[p.relative_to(R).as_posix()]=sha(p)
 expected={M/'maxwell-paper-narrative-v001.md':'98de2905d9871dffa5a39b9ec61d5d9d84edc6607a7ea25c609dd6c61611b320',M/'maxwell-paper-narrative-v002.md':'af496eafe3996eb73f48be5be5722ebfa895265fd4965af204ab30f9c58d5911',M/'maxwell-fixed-dissipation-peak-appendix-v001.md':'31f1d60317f94fc7b7b60a01e523f415b21c464682a5c6d4f77ebce1c2ea5741',M/'maxwell-fixed-dissipation-peak-appendix-v002.md':'c36bbd54984e119de7ca89b25f3bc651ce92e90bc13e3dcaf1c67d3cf6843f5f',B/folders[1]/'report.md':'ad7f61ca1c6df7694bfce540fb4b6d6fd0699e5c365473c964a66ef2b5164787'}
 for p,h in expected.items():assert sha(p)==h,p;checked[p.relative_to(R).as_posix()]=h
 d=B/folders[0];oldrep=B/'writing/maxwell-session004/narrative-paper-v001/reproduction-appendix.md'
 triples=[(d/'diff-narrative-from-v001.patch',M/'maxwell-paper-narrative-v001.md',M/'maxwell-paper-narrative-v002.md',10),(d/'diff-fixed-D-appendix-from-v001.patch',M/'maxwell-fixed-dissipation-peak-appendix-v001.md',M/'maxwell-fixed-dissipation-peak-appendix-v002.md',7),(d/'diff-reproduction-from-v001.patch',oldrep,d/'reproduction-appendix.md',0)]
 spec=importlib.util.spec_from_file_location('diff011',S/'prepare_R011_publish.py');dm=importlib.util.module_from_spec(spec);spec.loader.exec_module(dm)
 patches={};preservation=[]
 for patch,old,new,n in triples:
  dm.check_diff(patch,old,new)
  a,b=old.read_text('utf-8').splitlines(keepends=True),new.read_text('utf-8').splitlines(keepends=True)
  ops=difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes()
  restore=[]
  for tag,i,j,k,l in ops:
   if tag=='equal':restore+=b[k:l]
   else:restore+=a[i:j]
  assert ''.join(restore).encode('utf-8')==old.read_bytes()
  formula=lambda text:re.findall(r'\$\$.*?\$\$',text,re.S)
  if n:assert len(formula(''.join(a)))==n and formula(''.join(a))==formula(''.join(b))
  assert [z for z in a if z.startswith('|')]==[z for z in b if z.startswith('|')]
  assert re.findall(r'!\[.*?\]\([^\n)]+\)',''.join(a))==re.findall(r'!\[.*?\]\([^\n)]+\)',''.join(b))
  patches[patch.relative_to(R).as_posix()]=[old.relative_to(R).as_posix(),new.relative_to(R).as_posix()]
  preservation.append({'old':old.relative_to(R).as_posix(),'new':new.relative_to(R).as_posix(),'exact_reverse_old_SHA':sha(old),'formula_count':n,'table_and_image_unchanged':True})
 for p in [M/'maxwell-paper-narrative-v002.md',M/'maxwell-fixed-dissipation-peak-appendix-v002.md']:
  text=p.read_text('utf-8');assert '低于U逆的像域' not in text
  assert '不在U_J⁻¹的定义域[D0,D_max]内，因为D_min<D0' in text
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,'patch_pairs':patches,'preservation':preservation,
 'root_actual_read':'New author report and all three real diffs; entire v001 body/reproduction/map and all three original integration reports were read before this repair. New changed prose and direct R017 proof link checked.',
 'semantic_result':'M1 repaired in BOTH narrative and formerly published fixedD appendix. Direct positive-problem proof link no longer suggests inverse appendix contains full fixed-peak proof. Two engineering clarifications correctly distinguish sampled device axial-force peaks from story displacement peaks and old elastic5/8 from real-device pair. All numerical/scientific/machine limits inherited unchanged.',
 'prior_art_result':'R031 entire report read:2queries,0new primary body; weak keyword selection and no selected relevant new source are not access failures or proof of no prior art. Exact publication coverage remains unknown. No new primary conclusions adopted.',
 'review_scope':'Core only; pending R047 limited independent diff review will be bound in a separate final record. Old failed v001 and original reviews preserved, no unchanged endorsement.',
 'immutable_output':True}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'exact_patches':len(patches),'unchanged_formulas':17}))
if __name__=='__main__':main()
