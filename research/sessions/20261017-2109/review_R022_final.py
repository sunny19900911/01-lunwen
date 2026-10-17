"""R022 final immutable peer/source check, separate from the frozen core QA."""
from pathlib import Path
from datetime import datetime
from fractions import Fraction as Q
import ast, hashlib, importlib.util, json
S=Path(__file__).resolve().parent; R=S.parents[2]
B=R/'papers/damping-output-boundaries/research/roles'
OUT=S/'R022-final-review-v001.json'
PACKAGES=[
 'writing/maxwell-session004/compact-paper-v004',
 'verification/maxwell-session004/R043-compact-v004-math-integration',
 'literature/maxwell-session004/R029-compact-v004-source-diff-review',
 'novelty/maxwell-session004/R026-Gusev-alternate-source',
 'novelty/maxwell-session004/R027-RL-equivalent-prior-art',
 'ideation/maxwell-session004/R031-RL-mapping-review']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists(), 'Choose a new QA output version'
 spec=importlib.util.spec_from_file_location('identity020',S/'review_R020_integrations.py')
 m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
 checked={}
 for name in PACKAGES:
  d=B/name
  for p in d.iterdir():
   if not p.is_file(): continue
   assert p.stat().st_size<1000000
   if p.suffix=='.json': m.verify(json.loads(p.read_text('utf-8-sig')),d,checked)
   if p.suffix=='.py': ast.parse(p.read_text('utf-8-sig'))
   checked[p.relative_to(R).as_posix()]=sha(p)
 expected={
  B/PACKAGES[1]/'report.md':'c5bb6d9b471756294374a142b5e742dad176962666fe16b168a1dd0fd46d023c',
  B/PACKAGES[2]/'report.md':'4c1c22599a63a9dafbd56be97b46ae7ff64258b9f13ddf567aabc5054dc67839',
  B/PACKAGES[3]/'report.md':'df360a3bf55ae4262f4c59686ef26d7b6cfa118ae613a4a93cd87f1222664323',
  B/PACKAGES[4]/'report.md':'e01a8ac619c33918d01a3919963f9d99651552f5f92cb75181ae47e7f87ff804',
  B/PACKAGES[5]/'report.md':'868419082e6870fa46a2164013c0fd5fcad62aed8f64c85315482e65ae61cf40'}
 for p,digest in expected.items(): assert sha(p)==digest,p
 spec2=importlib.util.spec_from_file_location('diff011',S/'prepare_R011_publish.py')
 dm=importlib.util.module_from_spec(spec2); spec2.loader.exec_module(dm)
 old=R/'papers/damping-output-boundaries/manuscript/maxwell-paper-compact-v003.md'
 new=old.with_name('maxwell-paper-compact-v004.md')
 patches=[]
 for name in PACKAGES:
  for p in (B/name).glob('*.patch'):
   dm.check_diff(p,old,new); patches.append(p.relative_to(R).as_posix())
 core=S/'R022-core-review-v001.json'
 frozen=json.loads(core.read_text('utf-8'))
 for name,digest in frozen['checked_small_file_identities'].items(): assert sha(R/name)==digest,name
 checked[core.relative_to(R).as_posix()]=sha(core)
 # Independent exact polynomial example; no author program or scientific arrays executed.
 def mul(a,b):
  z=[Q(0)]*(len(a)+len(b)-1)
  for i,x in enumerate(a):
   for j,y in enumerate(b): z[i+j]+=x*y
  return z
 def integ(a): return sum((x/Q(i+1) for i,x in enumerate(a)),Q(0))
 a=[Q(0),Q(1)]; b=[Q(0),Q(1,2),Q(3,2),Q(-1)]
 assert sum(a)==sum(b)==1 and integ(a)==integ(b)==Q(1,2)
 assert integ(mul(a,a))==Q(1,3) and integ(mul(b,b))==Q(59,168)
 assert integ(mul(b,b))-integ(mul(a,a))==Q(1,56)
 def deriv(a): return [Q(i)*x for i,x in enumerate(a) if i]
 for z in [a,b]:
  assert integ(mul(z,deriv(z)))==Q(1,2)
  # For alpha=1/2,c=1: Rv=I^2, actual D=int I^3.
  assert integ(mul(z,[Q(0)]))==0
 checks={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,
 'checked_small_file_identities':checked,'publish_packages':PACKAGES,
 'core_record_immutable':{'path':core.relative_to(R).as_posix(),'sha256':sha(core)},
 'exact_patches_checked':patches,'root_full_reports_read':list(expected.keys()),
 'peer_findings':{'R043_math_integration_must_fix':0,'R029_source_diff_must_fix':0,
 'R029_overrun_seconds':182.933527,'R029_last_input_snapshot_to_freeze_not_rechecked_by_role':True,
 'root_current_declared_small_input_identities_rechecked_now':True},
 'RL_mapping':'I=F,U=v,L=1/kappa,Rv=g(F); total delta=int U=L deltaI+int Rv. Only linear Rv=RI with fixed endpoint I makes delta and Q=int I interchangeable. The original protocol is preserved with explicit correction addendum.',
 'exact_counterexample':{'same_endpoints':True,'same_Q':'1/2','integral_Rv_A':'1/3','integral_Rv_B':'59/168','total_delta_difference':'1/56','actual_dissipation':'int I^3, not int I^2','source_power_minus_D':'1/2'},
 'Goetz_primary_scope':'Root actually viewed cached original PDF pages2 and10. True Joule cost; voltage cap excludes resistor, not total Maxwell velocity cap. Endpoint/neural constraints differ; closest classic alpha1 tool, not established full same-condition cost interval. Page8 local-minimum discussion was read by role6 only, not root original page.',
 'Gusev_primary_scope':'Official metadata reported by role6; PDF unavailable, root landing failed. No body/coverage/absence claim.',
 'priority':'Exact prior publication remains unresolved; neither search failure nor differing neighbor conditions establishes novelty.',
 'source_originals_and_arrays_in_publish':False}
 checks['root_full_reports_read']=[str(p.relative_to(R).as_posix()) for p in expected]
 OUT.write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'patches':len(patches)}))
if __name__=='__main__': main()
