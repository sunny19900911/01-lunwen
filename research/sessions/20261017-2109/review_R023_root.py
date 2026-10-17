"""Immutable R023 joint-energy/input-budget review. No scientific author code run."""
from pathlib import Path
from datetime import datetime
from fractions import Fraction as Q
import hashlib,importlib.util,json
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
OUT=S/'R023-root-review-v001.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists()
 spec=importlib.util.spec_from_file_location('identity020',S/'review_R020_integrations.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);checked={}
 folders=['ideation/maxwell-session004/R033-input-budget-dissipation-corollary','verification/maxwell-session004/R045-input-budget-dissipation-independent','verification/maxwell-session004/R045-input-budget-dissipation-independent/post-freeze-comparison']
 for name in folders:
  d=B/name
  for p in d.iterdir():
   if p.is_file():
    assert p.stat().st_size<1000000
    if p.suffix=='.json':m.verify(json.loads(p.read_text('utf-8-sig')),d,checked)
    checked[p.relative_to(R).as_posix()]=sha(p)
 expected={
  B/folders[0]/'report.md':'d2cc1282f84395d8087d534fc19f6322f02d65800b5410c3344b152f171eec27',
  B/folders[1]/'report.md':'0754eb8b7a055f185a01b389264418413b14af14c1e797ac4371b334b58e5f5c',
  B/folders[2]/'report.md':'6141bd1a65b7264386500bbbaf814ef1a8b928268b3e0db617c244e2d38e41ec'}
 for p,h in expected.items():assert sha(p)==h,p
 # Separate exact point check of scalar completed square and order, not a general proof.
 c,v,f=Q(7,3),Q(-2,5),Q(13,2)
 assert v*f-c*v*v==f*f/(4*c)-c*(v-f/(2*c))**2
 A,r=Q(5),Q(2)
 assert min(A,A+r)==A and min(A,Q(4)+r)==A and min(A,Q(1)+r)<A
 alpha=Q(3,10);p=(1+alpha)/alpha;q=1+alpha
 assert 1/p+1/q==1
 for name in ['C040-root-review-v001.json','C040-adoption-v001.json']:
  z=S/name;checked[z.relative_to(R).as_posix()]=sha(z)
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,
 'root_full_reports_and_sources_read':['R033 author and checks source, no execution','R045 independent and post comparison','old R010 full report','old R018 full proof','accepted C039 full proofs previously reviewed'],
 'math_review':[
 'J=E+Dtot is AC nonnegative, >=E and >=Dtot; J0=completeE0 and Jprime=vf-vCv. Monotonicity of J is unnecessary.',
 'C positive definite square completion gives J<=B2; PSD needs f in Range(C) a.e. and finite weighted integral. A pseudoinverse alone cannot erase undamped input power.',
 'C PSD and beta L1: Jprime<=sqrt(2E)beta<=sqrt(2J)beta. Apply AC chain rule to sqrt(J+epsilon), integrate and take epsilon down to zero; gives B1 and avoids zero division.',
 'Use min only over finite legal budgets; E-only bound never implies cumulative D bound without J identity. Nonnegative energy and all true viscous dissipations retained.',
 'Common alpha plus complete physical K0/full force and target kernel permits C039 substitution Dtot<=B. Different alpha needs different bound.',
 'PeakD <= min(A,certifiedPeakU+Kspace*B^(1/p)); if PeakUbound>=A branch is redundant. Even smaller PeakUbound only tightens if its sum with R is below A.',
 'U same body IC has initial energy <=complete D initial energy; possible nonzero device initial force is retained in full F and E0. Missing external support work invalidates budget.',
 'Fixed target displacement only; direct energy extends through passive free tail if ALL inputs cease, finiteH kernel bound is not automatically an infiniteH estimate. Layout-only B changes do not change coarse common budget/elastic compliance.'],
 'grade':'Classical immediate energy bookkeeping plus Holder application. No new theory, engineering number, peak reduction, layout ranking or exact priority.',
 'independent_small_checks':'Completed square and three order branches as exact Fraction points; root mathematical proof review above is separate, not established by these finite examples.',
 'author_scientific_programs_arrays_or_ODE_executed':False,'immutable_output':True}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked)}))
if __name__=='__main__':main()
