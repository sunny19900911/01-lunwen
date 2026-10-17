
"""Independent root check of the classic dissipation/kernel conditional bound."""
from pathlib import Path
from datetime import datetime
from fractions import Fraction as Q
import hashlib,importlib.util,json
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
FOLDERS=['ideation/maxwell-session004/R030-dissipation-modal-output-bound','verification/maxwell-session004/R042-dissipation-modal-bound-independent','verification/maxwell-session004/R042-dissipation-modal-bound-independent/post-freeze-comparison','literature/maxwell-session004/R028-convolution-holder-source']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 spec=importlib.util.spec_from_file_location('identity020',S/'review_R020_integrations.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 checked={}
 for name in FOLDERS:
  d=B/name;assert d.is_dir(),('await completed comparison',name)
  for p in d.iterdir():
   if p.is_file() and p.suffix=='.json':mod.verify(json.loads(p.read_text('utf-8-sig')),d,checked)
 author=B/FOLDERS[0]/'report.md';review=B/FOLDERS[1]/'report.md'
 assert sha(author)=='78722bbbd78ffd8e3ad725cfec16648997d1548ab7e505754a7997733f45c288'
 assert sha(review)=='c92dc64f6157bd4035961723fdbcd5c0d06cdcbf507ff25ee8b83e1f062ea604'
 for alpha in [Q(3,10),Q(1),Q(5,2)]:
  p=(1+alpha)/alpha;q=1+alpha
  assert 1/p+1/q==1
  assert (1/alpha)/p==1/q
  assert alpha/q==1/p
  # Weighted joint device/time force factor: c^(-p/q)=c^(-1/alpha).
  assert -p/q==-1/alpha
  # Force/length/time exponents after multiplication by kernel norm.
  assert (1/q+1/p-1, -alpha/q+1/p+1, alpha/q+1/q-1)==(0,1,0)
 src=B/'literature/maxwell-session004/R028-convolution-holder-source/local-cache'
 assert sha(src/'MIT18_156_lecture25.pdf')=='996490a8065004dbec4776388fb70730be2597588b4fb5b5e873e0d7e808ae43'
 assert sha(src/'MIT25-3.png')=='aceecb45df3eba157fab39397795ddf64838f9746ad1aa2536ce3bf10404f982'
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,
 'root_actual_read':['R030 frozen full report/checks code','R042 independent full proof/closure','post-freeze comparison fullreport','R028 full source report and source-manifest; actually viewed MIT original PDF page3 image'],
 'root_independent_derivation':[
 'Same physical M,C,K0/f/body IC gives exact full-force convolution; h_j combines fixed ell and B with actual physical Green, complete modal normalization when diagonalizable',
 'D=c^(-1/alpha)*norm(F,p)^p gives c^(1/q)*D^(1/p), exponents and units checked independently',
 'For every t<=H use Holder on [0,t], extend only integral bounds to H; physical displacement solutions continuous so essential and actual supremum agree',
 'Joint device/time weighted Holder uses factors c^(1/q)h and c^(-1/q)F, yielding sum c*norm(h,q)^q times sum D with correct exponents',
 'Common nonzero body IC cancels, different IC adds homogeneous term. FNA reference residual is not fullF and is not controlled by the same force power budget',
 'C PSD gives no infinite-time Lq guarantee; sin(t) counterexample. Missing modes/devices/tail need remainder; no acceleration direct-term extension',
 'Only abs peak difference band, not sign/decrease/layout order; actual dissipation budget and physical geometry/modal/C must be certified separately. No sharp building attainability claim'],
 'primary_source_scope':'MIT lecture25 page3 supplies direct endpoint Holder convolution. Classical tool application, no new theory or exact-priority conclusion.',
 'no_source_scientific_programs_or_data_arrays_executed':True}
 (S/'R021-C039-root-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'candidate':'C039'}))
if __name__=='__main__':main()

