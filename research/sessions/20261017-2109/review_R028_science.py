"""Finite scientific-summary review, separate from real scheduler/Git closure."""
from pathlib import Path
from datetime import datetime
import hashlib,json,re
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
PACKAGES=['novelty/maxwell-session004/R034-final-science-scope','experiments/maxwell-session004/R029-final-science-data-scope']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=S/'R028-science-review-v001.json';assert not out.exists()
 ids={}
 def add(p):
  p=p.resolve();name=p.relative_to(R).as_posix();raw=p.read_bytes()
  assert p.suffix in {'.md','.json'} and len(raw)<1000000 and '/local-cache/' not in name
  txt=raw.decode('utf-8-sig')
  if p.suffix=='.json':json.loads(txt)
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
 candidate=S/'final-summary-science-candidate-v001.md';add(candidate)
 assert sha(candidate)=='1771dfc28f6a419a27f0599e016c3a12132153c44707b0fe172e3570d2fbf4bc'
 t=candidate.read_text('utf-8');body=t.split('\n\n',2)[2]
 assert body.startswith('**这轮形成了')
 assert json.loads((B/PACKAGES[0]/'validation.json').read_text('utf-8'))['result']=='0 mustfix'
 assert json.loads((B/PACKAGES[1]/'validation.json').read_text('utf-8'))['must_fix_count']==0
 assert '并非试验实测' in body and '最多176个端点编号' in body
 for link in re.findall(r'\]\(([^\n)]+)\)',body):assert (S/link).resolve().exists()
 result={'at':datetime.now().astimezone().isoformat(),'checked_identities':ids,'finite_identity_count':len(ids),
 'candidate_sha256':sha(candidate),'science_body_sha256':hashlib.sha256(body.encode()).hexdigest(),
 'manual_full_read':'Root authored/read full scientific summary and both complete bounded reviews; prior proof/data/adoption states reused, not new independent proof or data recomputation.',
 'review_result':'Science/contribution and engineering-data scope both0must; root agrees',
 'retained_limits':['Exact publication novelty unresolved','Actual building layout benefit unresolved','Modal/geometry/input/true damping and initial state required for bounds','Continuous fixed-D peak set not solved','193 complete observed simulation groups not raw physical measurements or forward validation'],
 'node_count':'Conditional cardinality: 88 two-end units imply at most176 endpoint IDs, deduplicated; target additional, not actual geometry certification',
 'new_research_or_runtime_closure_claim':False,
 'cutoff_generation_contract':'After real deadline only, final-summary.md prepends actual window/generation metadata and copies exact science_body from after first two paragraphs of this frozen candidate. Operational receipt generated after actual tools, separately.',
 'scheduler_and_final_Git_not_yet_closed':True}
 out.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'pass':True,'identities':len(ids),'science_body_sha256':result['science_body_sha256']}))
if __name__=='__main__':main()
