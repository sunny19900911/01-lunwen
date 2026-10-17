
"""R022 immutable root core check; never overwrite an adopted QA record."""
from pathlib import Path
from datetime import datetime
import difflib,hashlib,importlib.util,json,re
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
OUT=S/'R022-core-review-v001.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists(),'Use a new output version for additional checks'
 spec=importlib.util.spec_from_file_location('identity020',S/'review_R020_integrations.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 checked={}
 folders=['writing/maxwell-session004/compact-paper-v004','novelty/maxwell-session004/R026-Gusev-alternate-source']
 for name in folders:
  d=B/name
  for p in d.iterdir():
   if p.is_file() and p.suffix=='.json':mod.verify(json.loads(p.read_text('utf-8-sig')),d,checked)
 old=R/'papers/damping-output-boundaries/manuscript/maxwell-paper-compact-v003.md'
 new=old.with_name('maxwell-paper-compact-v004.md')
 assert sha(old)=='8c92fc07944df70491931733530902b7bd4e2d577b508fe5004741dcade06095'
 assert sha(new)=='1c68afccee269708ac857adb74b98b94433deccbae6d972da4e239ac4191643b'
 for p in [old,new]:checked[p.relative_to(R).as_posix()]=sha(p)
 a,b=old.read_text('utf-8').splitlines(keepends=True),new.read_text('utf-8').splitlines(keepends=True)
 ops=difflib.SequenceMatcher(a=a,b=b,autojunk=False).get_opcodes()
 changed=[o for o in ops if o[0]!='equal']
 assert [o[0] for o in changed]==['replace','replace','insert','insert'],changed
 assert [(o[1],o[2]) for o in changed[:2]]==[(2,3),(6,7)]
 recovered=[]
 for tag,i,j,k,l in ops:
  if tag=='equal':recovered+=b[k:l]
  elif tag=='replace':recovered+=a[i:j]
  else:assert tag=='insert'
 assert ''.join(recovered).encode('utf-8')==old.read_bytes()
 ta,tb=''.join(a),''.join(b);formulas=lambda t:re.findall(r'\$\$.*?\$\$',t,re.S)
 assert len(formulas(ta))==3 and len(formulas(tb))==4 and formulas(tb)[:3]==formulas(ta)
 def tables(t):
  lines=t.splitlines();result=[]
  for i,line in enumerate(lines):
   if re.fullmatch(r'\|[ \t:|\-]+\|',line) and i and lines[i-1].startswith('|'):
    start=i-1;j=i+1
    while j<len(lines) and lines[j].startswith('|'):j+=1
    result.append('\n'.join(lines[start:j]))
  return result
 assert len(tables(ta))==2 and tables(ta)==tables(tb)
 assert len(re.findall(r'^## [1-5] ',tb,re.M))==5
 assert re.findall(r'!\[.*?\]\([^\n)]+\)',ta)==re.findall(r'!\[.*?\]\([^\n)]+\)',tb)
 spec2=importlib.util.spec_from_file_location('diff011',S/'prepare_R011_publish.py')
 dm=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(dm)
 patch=dm.check_diff(B/'writing/maxwell-session004/compact-paper-v004/diff-from-v003.patch',old,new)
 assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md')=='93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,
 'root_entire_content_read':['compact-v004 and real patch','Gusev R026 report plus metadata/validation/attempt (no PDF body)'],
 'manuscript_checks':{'four_authorized_changes_only':True,'reverse_recovers_v003_exact_bytes':True,'old_three_formulas_two_tables_and_image_unchanged':True,'new_classic_C039_fourth_equation':True,'five_sections':True,'patch':patch},
 'root_semantic_review':'C039 complete physical K0/fullF and actualC/target/port kernel, true total dissipative D not ratio/subset, finiteH/commonalpha and proper c weight, continuous displacement; no decrease/layout-order/actual engineering claim. C038/free terminaldelta/classical example separate.',
 'Gusev_scope':'Role6 official metadata retrieval only; full PDF still unavailable. Root independent landing open400timeout did not verify original metadata itself. Neither exactcondition absence nor coverage decided, no retrieval repeated.',
 'source_scientific_programs_or_arrays_executed':False,
 'immutable_output':'This v001 record will not be updated to add peer reviews; final review uses a new file name.'}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'scientific_identities':len(checked),'diff_changes':len(changed),'equations':4,'tables':2}))
if __name__=='__main__':main()

