"""Bind the preserved failed-version reviews and the new limited repair review."""
from pathlib import Path
from datetime import datetime
import hashlib,importlib.util,json
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles';OUT=S/'R024-final-review-v001.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists()
 spec=importlib.util.spec_from_file_location('id020',S/'review_R020_integrations.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 checked={}
 for name in ['R024-core-review-v001.json','R023-narrative-review-binding-v001.json']:
  p=S/name;obj=json.loads(p.read_text('utf-8'))
  for n,d in obj['checked_small_file_identities'].items():assert sha(R/n)==d,n;checked[n]=d
  checked[p.relative_to(R).as_posix()]=sha(p)
 d=B/'verification/maxwell-session004/R047-narrative-v002-diff-review'
 for p in d.iterdir():
  if p.is_file():
   if p.suffix=='.json':m.verify(json.loads(p.read_text('utf-8-sig')),d,checked)
   checked[p.relative_to(R).as_posix()]=sha(p)
 assert sha(d/'report.md')=='6908e28059271be8f7f44fdc99c52d7944819439a2722430020a640af0a0b151'
 spec=importlib.util.spec_from_file_location('diff011',S/'prepare_R011_publish.py');dm=importlib.util.module_from_spec(spec);spec.loader.exec_module(dm)
 core=json.loads((S/'R024-core-review-v001.json').read_text('utf-8'));pairs=dict(core['patch_pairs'])
 wd=B/'writing/maxwell-session004/narrative-paper-v002'
 for p in d.glob('*.patch'):
  author=wd/p.name.removeprefix('independent-')
  names=pairs[author.relative_to(R).as_posix()]
  dm.check_diff(p,R/names[0],R/names[1]);assert p.read_bytes()==author.read_bytes()
  pairs[p.relative_to(R).as_posix()]=names
 assert len(pairs)==6
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,'patch_pairs':pairs,
 'root_full_read':['R047 final report, new author report and three real diffs','Original narrative body/reproduction/map plus R046 math/R028 contribution/R026 engineering reports','R031 search report and prior-art limits'],
 'admission':'v002 only: original full mathematical/source/engineering reviews except their shared M1 + new R047 independent limited repair review0must + root core/final exact diffs and identities. Old v001 remains failed-term historical version; never adopted unchanged.',
 'preservation':'Both manuscripts formulas10+7/table/image/numeric/scientific and machine conditions unchanged; roots reverse old bytes exact, independent R047 separately parsed unified hunks. Root did not execute author or reviewer scientific scripts.',
 'prior_art':'R031 has2new queries and0new primary bodies; no same-condition publication closure or novelty upgrade.',
 'immutable_output':True}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'exact_patches':len(pairs)}))
if __name__=='__main__':main()
