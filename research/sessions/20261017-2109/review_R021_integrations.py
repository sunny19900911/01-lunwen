
"""R021 root source checks and independent exact checks for two fixed explanatory profiles."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime
import ast,hashlib,importlib.util,json,math,re
S=Path(__file__).resolve().parent;R=S.parents[2]
B=R/'papers/damping-output-boundaries/research/roles'
FOLDERS=['writing/maxwell-session004/fixed-dissipation-peak-appendix-v001','verification/maxwell-session004/R041-fixed-D-appendix-integration','experiments/maxwell-session004/R025-fixed-D-two-peak-example','novelty/maxwell-session004/R025-fixed-D-example-review','literature/maxwell-session004/R028-convolution-holder-source']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 spec=importlib.util.spec_from_file_location('identity020',S/'review_R020_integrations.py')
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 checked={}
 for name in FOLDERS:
  d=B/name;assert ((d/'validation.json').exists() or (d/'validation-R028.json').exists()),('await frozen validation',name)
  for p in d.iterdir():
   if p.is_file() and p.suffix=='.json':mod.verify(json.loads(p.read_text('utf-8-sig')),d,checked)
   if p.is_file() and p.suffix=='.py':ast.parse(p.read_text('utf-8-sig'))
 manuscript=R/'papers/damping-output-boundaries/manuscript/maxwell-fixed-dissipation-peak-appendix-v001.md'
 assert sha(manuscript)=='31f1d60317f94fc7b7b60a01e523f415b21c464682a5c6d4f77ebce1c2ea5741'
 txt=manuscript.read_text('utf-8');assert len(re.findall(r'\$\$.*?\$\$',txt,re.S))==7
 assert set(re.findall(r'\\tag\{([1-7])\}',txt))==set('1234567')
 lines=txt.splitlines();i=lines.index('| 前置条件 | 固定D的完整结论 |')
 assert all(line.count('|')==3 for line in lines[i:i+8]) and not lines[i+8].startswith('|')
 checked[manuscript.relative_to(R).as_posix()]=sha(manuscript)
 # Exact old alpha=1 integrals, independent rational endpoint identities and analytic log bounds.
 h,D,T=Q(1,2),Q(1,4),Q(4)
 log_bounds=[(Q(2,3),Q(3,4)),(Q(10,11),Q(1))]
 out=[]
 for M,(lo,hi) in zip([Q(1,2),Q(3,5)],log_bounds):
  A=1/(1-M);Bdown=(1+M)/(1+h)
  assert 1-1/A==M and (1+M)/Bdown-1==h
  const=-2*M+h-h*h/2
  assert lo+const>0 and D-(hi+const)>0
  # tau < 1, ell upper via lower log bound, so waiting has a strict rational lower bound.
  ell_upper=(D-(lo+const))/(M*M)
  assert T-hi-ell_upper>0
  tu=math.log(float(A));td=math.log(float(Bdown));tau=tu+td
  ell=(float(D)-tau-float(const))/float(M*M);wait=float(T)-tau-ell
  # These are only display comparisons; analytic exact identities precede the floats.
  Dcheck=tu-float(M+M*M/2)+td-float(M-M*M/2-h+h*h/2)+float(M*M)*ell
  Wcheck=tu-float(M)+td+float(h-M)+float(M*M)*ell
  assert abs(Dcheck-float(D))<1e-13 and abs(Wcheck-3/8)<1e-13
  delta=tu+float(M)*ell-td
  assert wait>0 and ell>0 and td>=0
  out.append({'M':str(M),'rise':tu,'hold':ell,'fall':td,'wait':wait,'delta':delta,'D_display':Dcheck,'W_display':Wcheck})
 assert abs(out[0]['delta']-(7/4-math.log(2)))<1e-13
 assert abs(out[1]['delta']-(43/24+math.log(75/32)-(5/3)*math.log(8/3)))<1e-13
 assert out[0]['delta']>out[1]['delta']>0
 result={'at':datetime.now().astimezone().isoformat(),'checks_passed':True,'checked_small_file_identities':checked,
 'root_full_read':['C038 appendix full text plusR041 report/checks','R025 example full report andchecks.py','R025 independent example review report/validation'],
 'exact_reasoning':'Each linear phase solution and exact end argument verified; old integrals give exact D=L+M²ell=1/4, W=D+1/8. Rational log bounds give positive waits/holds. Terminal delta differs by derivative -(D-L)/M²<0 on fixed interval, not by float inequality alone.',
 'ordinary_scalar_displays_not_continuous_certificate':out,
 'appendix_equations':7,'appendix_condition_rows':6,
 'scope':'Integration of admitted C038; exact dimensionless illustrative profiles. No new ODE/data theorem/engineering or priority claim. New energy-modal candidate excluded until independent review.',
 'source_programs_executed':False,'arrays_originals_or_CSV_opened':False}
 (S/'R021-root-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'passed':True,'identities':len(checked),'profiles':2,'appendix_equations':7}))
if __name__=='__main__':main()

