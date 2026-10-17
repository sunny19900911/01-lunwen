"""C043 finite metadata checks after manual full proof review; never execute author code."""
from pathlib import Path
from datetime import datetime
import hashlib,json,ast
S=Path(__file__).resolve().parent;R=S.parents[2]
A=R/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R035-continuous-cost-image'
V=R/'papers/damping-output-boundaries/research/roles/verification/maxwell-session004/R050-continuous-cost-image-independent'
OUT=S/'C043-root-review-v001.json'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists()
 checked={}
 def add(p):
  p=p.resolve();name=p.relative_to(R).as_posix()
  assert p.suffix in {'.md','.json','.py'} and p.stat().st_size<1000000
  assert 'local-cache' not in name and name!='5E-07'
  raw=p.read_bytes();txt=raw.decode('utf-8-sig')
  if p.suffix=='.json':json.loads(txt)
  if p.suffix=='.py':ast.parse(txt)
  checked[name]=hashlib.sha256(raw).hexdigest()
  return p
 def check_records(obj,parent):
  if isinstance(obj,dict):
   if isinstance(obj.get('path'),str) and isinstance(obj.get('sha256'),str):
    name=obj['path'];p=R/name
    if not p.exists():p=parent/name
    add(p);assert digest(p)==obj['sha256'],name
    if 'bytes' in obj:assert p.stat().st_size==obj['bytes'],name
   for value in obj.values():check_records(value,parent)
  elif isinstance(obj,list):
   for value in obj:check_records(value,parent)
 for base in [A,V,V/'post-freeze-comparison']:
  for p in base.iterdir():
   if p.is_file():add(p)
 for p in [A/'source-freeze.json',A/'artifact-manifest.json',V/'source-freeze.json',V/'validation.json',V/'post-freeze-comparison/validation.json']:
  check_records(json.loads(p.read_text('utf-8')),p.parent)
 for name in ['continuous-velocity-cost-image-protocol-v001.md','continuous-cost-image-root-candidate-v001.md','continuous-cost-image-root-core-v001.json','C042-adoption-v001.json']:
  add(S/name)
 assert digest(A/'report.md')=='55d19dc282c64b4c68df43fe72cb94b126d6ca53479c96d84ce08aad9207a249'
 assert digest(V/'report.md')=='0098f1650e5ccdb7c6ac7670caa28795debada72c144918080f9fbd92860ef80'
 post=json.loads((V/'post-freeze-comparison/validation.json').read_text('utf-8'))
 assert post['must_fix_count']==0 and post['original_R050_unchanged']
 for p in [A/'validation.json',V/'validation.json',V/'post-freeze-comparison/validation.json']:
  j=json.loads(p.read_text('utf-8'));assert j['within_limit']
 result={'at':datetime.now().astimezone().isoformat(),'checked_identities':checked,'finite_count':len(checked),
 'manual_full_text_review':['R035 report and author crosscheck','R050 full independent report and closure checks','R050 frozen post-comparison report','Root candidate written before reading both new role reports'],
 'mathematical_obligations_reviewed':[
 'State stays in (-B,B), g C1 and nonnegative secants; ordered distinct continuous controls give strict terminal comparison',
 'Joint continuity of clipped convex-mix control and terminal state; fixed [-2V,2V] bracket gives constant caps',
 'Target-level bias root exists and unique; no false global strict monotonicity across saturated platforms',
 'Two equal clipped controls for distinct biases take only two cap values, continuity forces constant cap, excluded by strict terminal bracket',
 'Compact bias interval plus joint continuity and unique target root gives continuous bias selection',
 'Zero bias at original path endpoints and uniqueness recover both original controls exactly',
 'Every path point satisfies exact terminal force, continuous amplitude cap; end-total-deformation remains free',
 'Cost continuous on exact-terminal path; no monotonicity needed',
 'C042 sharp exact-terminal families supply opposite sides of arbitrary interior cost; IVT fills each exact d',
 'T=tmin unique constant V and singleton; T<tmin empty, not passed through interior root argument'],
 'result':'supported analytic-derivation reviewed within explicit continuous-speed class; complete D image only',
 'inherited_lemma':'C042 adopted endpoint exclusion and sharp families, not re-proved this round; metadata checks do not prove mathematics',
 'limits':['No continuous fixed-D peak set','No imposed end velocities, uniform acceleration bound, end-total-deformation closure, structural feedback','No alpha>1, h=0, real building realization, layout ranking or novelty conclusion'],
 'frozen_markdown_display_issue':{'path':(V/'post-freeze-comparison/report.md').relative_to(R).as_posix(),'sha256':digest(V/'post-freeze-comparison/report.md'),'issue':'ASCII double norm bars inside one table cell; preserve original and provide display-only supplement, no mathematical change'},
 'no_new_ODE_arrays_or_search':True,'no_author_program_execution':True}
 OUT.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
 print(json.dumps({'finite_count':len(checked),'pass':True}))
if __name__=='__main__':main()
