"""Exact small-algebra corollary review; never recompute the inherited ODE witness."""
from pathlib import Path
from datetime import datetime
from fractions import Fraction as Q
import hashlib,importlib.util,json
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles'
OUT=S/'C040-root-review-v001.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists()
 spec=importlib.util.spec_from_file_location('identity020',S/'review_R020_integrations.py')
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);checked={}
 folders=['ideation/maxwell-session004/R032-mass-participation-local-corollary','verification/maxwell-session004/R044-mass-participation-independent','verification/maxwell-session004/R044-mass-participation-independent/post-freeze-comparison','literature/maxwell-session004/R030-FNA-nonlinear-mode-coverage-source']
 for name in folders:
  d=B/name
  for p in d.iterdir():
   if p.is_file():
    assert p.stat().st_size<1000000
    if p.suffix=='.json':m.verify(json.loads(p.read_text('utf-8-sig')),d,checked)
    checked[p.relative_to(R).as_posix()]=sha(p)
 expected={
  B/folders[0]/'report.md':'b9bc2371ed2600ff0faece2f1280d8f201362bf2b20e99158ba5b9a52c127d6a',
  B/folders[1]/'report.md':'4f38a134194e7867bf037c63a3c097ae8f861c3c47dc6930079d71b76bfe4ce1',
  B/folders[2]/'report.md':'9141ec5a0a169cebd824897220ce8972208b2dcaf464010e24d122d57b8f6bf3',
  B/folders[3]/'report.md':'5a15e1124af416484d0a5d9e01bd45431eda8e23c562221cc3413a39ecea1418'}
 for p,d in expected.items():assert sha(p)==d,p
 K=((Q(2),Q(-1)),(Q(-1),Q(2)));r=(Q(1),Q(1));ps=((Q(1),Q(1)),(Q(1),Q(-1)))
 dot=lambda a,b:sum(x*y for x,y in zip(a,b))
 for v,lam,rho in zip(ps,[Q(1),Q(3)],[Q(1),Q(0)]):
  assert tuple(dot(row,v) for row in K)==tuple(lam*x for x in v)
  assert dot(v,r)**2/(dot(v,v)*dot(r,r))==rho
 assert Q(121,8)-Q(97,25)**2==Q(353,5000)>0
 assert Q(121,32)-Q(97,50)**2==Q(353,20000)>0
 # Current image identities are checked locally, originals will not be published.
 imgs={}
 for n,digest in [('475','dd3630ca2373b3d1086c1d9658b19c134e3342593fce1aa642fc717b3d267603'),('476','00a353b076fb8ac14694f0da6b1cc9aa97bea84da847006109b9844fee6dd37b')]:
  p=B/('literature/maxwell-session004/local-cache/R004-CSI2016-PDFpage-'+n+'.png')
  assert sha(p)==digest;imgs[p.relative_to(R).as_posix()]=digest
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,
 'full_reports_read':[p.relative_to(R).as_posix() for p in expected],
 'root_actual_primary_images_viewed_and_hashed':imgs,
 'source_scope':'CSI2016 printed453-454/PDF475-476: nonlinear modal coupling, adequate nonlinear-force representation not automatic; masses/inertias on nonlinear DOFs, Ritz suggestion with complete-eigen exception, independent nonlinear-DOF starting deformation loads and enough vectors. Not a direct printed100percent theorem or actual300mode failure.',
 'exact_algebra':'Bare eigenvalues1,3; omega1,sqrt3; directional mass fractions1,0; nonlinear port projection on antisymmetric mode nonzero. Two strict squared decimal margins353/5000,353/20000.',
 'root_proof_review':'For every symmetric reconstruction(a,a), antisymmetric error is true qminus; inherited true witness qminus<-11/4 yields relative displacement error>3.88 and max of two node errors>1.94. Choosing a=true u1 refutes a fixed-u1 bound for all reconstructions. Not a difference of two scalar response peaks.',
 'witness_scope':'Only inherited C027/C028 fixed true tstar16529T/16384 under ALL original model/residual/helper/IEEE nearest gradual-underflow noFTZDAZ nextafter Fraction float64 decode and stable-mode conditions. No ODE/cache/array or old certificate recomputation.',
 'grade':'Classical modal projection corollary, not new mechanism/priority or real ETABS/Ritz accuracy finding.',
 'output_immutable':True}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'primary_images':2}))
if __name__=='__main__':main()
