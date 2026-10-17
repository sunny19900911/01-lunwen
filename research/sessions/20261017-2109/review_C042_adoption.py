"""Immutable final C042 admission after the independent proof and comparison."""
from pathlib import Path
from datetime import datetime
import hashlib,importlib.util,json
S=Path(__file__).resolve().parent;R=S.parents[2];B=R/'papers/damping-output-boundaries/research/roles';OUT=S/'C042-adoption-v001.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not OUT.exists()
 spec=importlib.util.spec_from_file_location('id020',S/'review_R020_integrations.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 core=S/'continuous-velocity-root-core-v001.json';q=json.loads(core.read_text('utf-8'));checked=dict(q['checked_small_file_identities'])
 for n,d in checked.items():assert sha(R/n)==d,n
 checked[core.relative_to(R).as_posix()]=sha(core)
 folders=['verification/maxwell-session004/R048-continuous-velocity-independent','verification/maxwell-session004/R048-continuous-velocity-independent/post-freeze-comparison']
 for name in folders:
  d=B/name
  for p in d.iterdir():
   if p.is_file():
    if p.suffix=='.json':m.verify(json.loads(p.read_text('utf-8-sig')),d,checked)
    checked[p.relative_to(R).as_posix()]=sha(p)
 assert sha(B/folders[0]/'report.md')=='fb2868540d569662bf991a1147ff26f98b8022aae2c6d0730c66f4bf68287312'
 assert sha(B/folders[1]/'report.md')=='da6306bca306e9bbf2ea69ef1d1353c601418b2d033068396cc975064fd4e268'
 result={'at':datetime.now().astimezone().isoformat(),'claim':'M-C042','status':'supported','evidence':'analytic-derivation','review':'reviewed','checked_identities':checked,
 'conditions':'0<alpha<=1; positive kappa,c,V;0<h<B=cV^alpha;F0=0,FT=h;v continuous on[0,T],abs(v)<=V; terminal totaldelta free. No endpointvelocity/acceleration or building feedback constraints.',
 'conclusion':'For T>tmin every continuous admissible trajectory has Dmin<D<Dmax; inf=Dmin and sup=Dmax, neither attained. Exact terminal h holds for EVERY approximating ramp trajectory, not only its limit. T=tmin constant v=V is an attainable singleton exception.',
 'proof_chain':'Root prior independent candidate notes; author R034 signed-Psi/equality and ramp-parameter bracketing; R048 independently frozen radial/Phi-up equality plus fixed-bracket root calibration; new separate90second postcomparison0must. Root full author/independent/post proofs read and assumptions/strict comparison/control convergence checked.',
 'root_assessment':'Both smoothing proofs valid; author tighter contraction and3Vepsilon upper bound do not conflict with independent exponential estimate or root loose8Vepsilon. Upper time equality and lower zero-set/negative-sign alternatives explicitly excluded.',
 'scope_exclusions':'No full continuousD interval attainability or fixedD peakset, alpha>1, endpoint v0/vT, bounded acceleration, zero extension, terminaldelta closure, engineering/actualFNA realization or publication novelty.',
 'novelty':'Classic comparison/AC chain rule/smoothing/IVT/continuous dependence consequence; not a new tool or actual structural design guarantee.',
 'publication':'Local post-R024 admission, not included in bdb7828. Eligible for next reviewed checkpoint only.',
 'source_scientific_programs_arrays_or_ODE_executed':False,'immutable_output':True}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'adopted':'C042','identities':len(checked),'engineering_or_priority':False}))
if __name__=='__main__':main()
