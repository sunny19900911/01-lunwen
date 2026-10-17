"""Independent exact-rational selected challenges; no helper import or ODE."""
from pathlib import Path
from fractions import Fraction as F
from math import factorial
import ast,hashlib,json,time
import numpy as np
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R017-addition-witness-certificate'
# Reuse only this role's frozen pure Fraction function definitions, never its executable run.
old=HERE.parent/'R025/fraction_challenges.py'
tree=ast.parse(old.read_text(encoding='utf-8'))
defs=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[])
exec(compile(defs,str(old),'exec'))
started=time.perf_counter()
s=json.loads((SOURCE/'summary_r017.json').read_text(encoding='utf-8'))
cache=Path(s['source_refs']['local_cache']['path'])
assert hashlib.sha256(cache.read_bytes()).hexdigest()==s['source_refs']['local_cache']['sha256']
with np.load(cache,allow_pickle=False) as z:
    a=z['D_N16384'];assert a.dtype==np.float64 and a.shape==(98305,9)
    assert int(np.argmax(abs(a[:,1])))==16529
    states=a[:16530,1:6].copy()
assert np.isfinite(states).all() and np.all(states[0]==0)
pi=decgrid(sub(scale(atan_bounds(5),16),scale(atan_bounds(239),4)))
sqrt2=decgrid(root_bracket(F(2),2));sqrt3=decgrid(root_bracket(F(3),2))
N=16384;J=16529;h=div(scale(pi,F(20,N)),sqrt2);invh=div(point(1),h)
cd=scale(add(point(1),sqrt3),F(1,20));co=scale(sub(point(1),sqrt3),F(1,20))
par=s['model_and_time_intervals']
for key,v in [('PI_interval',pi),('sqrt2_input_omega_interval',sqrt2),('sqrt3_interval',sqrt3),('true_h_interval',h),('true_T_interval',scale(h,N)),('true_witness_time_interval',scale(h,J)),('Cdiag',cd),('Coff',co)]:
    assert contains(par[key],v),key
checks=[]
for name,info in s['residual_upper_diagnostics'].items():
    n=info['segment'];left=[F(float(x)) for x in states[n]];right=[F(float(x)) for x in states[n+1]]
    d=[y-x for x,y in zip(left,right)];m=[(x+y)/2 for x,y in zip(left,right)]
    f=sin_phase(20*n+10,N,pi) if n<N else point(0)
    ru1=sub(scale(invh,d[0]),point(m[2]));ru2=sub(scale(invh,d[1]),point(m[3]))
    rv1=sub(add(add(add(scale(invh,d[2]),scale(cd,m[2])),scale(co,m[3])),point(2*m[0]-m[1])),f)
    rv2=sub(add(add(add(scale(invh,d[3]),scale(cd,m[3])),scale(co,m[2])),point(2*m[1]-m[0]+m[4])),f)
    rf=add(sub(scale(invh,d[4]/8),point(m[3])),signed_g(m[4],point(10)))
    target=dict(zip(['r_u1','r_u2','r_v1','r_v2','r_F'],[ru1,ru2,rv1,rv2,rf]))[name]
    assert contains(info['interval'],target),(name,n)
    checks.append({'residual':name,'segment':n,'independent_exact_rational_interval_contained':True})
# Independent derivative maximum on the whole frozen PL prefix (endpoint extrema suffice).
force_max=max(abs(F(float(x))) for x in states[:,4])
target=(force_max/10)**7
derivative_upper=root_bracket(target,3)[1]/3
assert F(s['maximum_Lg_upper'])>=derivative_upper
b=s['candidate_witness_bounds'];absstored=abs(F(float(states[J,0])));ih=F(b['I_J_upper_candidate'])
assert F(b['exact_stored_abs_u1_J'])==absstored
assert F(b['D_fixed_witness_lower_candidate'])<=absstored-ih
th=b['U_threshold_outward_interval'];assert F(th[0])<=F(241,100)<=F(th[1])
assert F(b['gap_lower_candidate_against_U_threshold_hi'])<=F(b['D_fixed_witness_lower_candidate'])-F(th[1])
assert F(b['gap_lower_candidate_against_U_threshold_hi'])>0
assert F(b['D_fixed_witness_lower_candidate'])>F('4.34911558')
assert F(b['gap_lower_candidate_against_U_threshold_hi'])>F('1.93911558')
assert ih<F('0.715880662')
# U: exact coefficient equations and squared amplitudes, without rounded radical evaluation.
A=F(-50,51);Bcoef=F(-5,51);Ccoef=-Bcoef;Dcoef=F(67,68);nu2=F(399,400)
assert -A-F(1,10)*2*Bcoef==1
assert -Bcoef+F(1,10)*A==0
assert A*A+2*Bcoef*Bcoef==F(50,51)<1
assert Bcoef+Ccoef==0
assert A+(-F(1,20)*Ccoef+Dcoef)==0
R2=2*Ccoef*Ccoef+2*Dcoef*Dcoef/nu2
assert R2==F(40000,20349)<F(141,100)**2
assert F(141,100)*F(5,4)==F(141,80)<F(241,100)
r=json.loads((HERE/'isolated-run/summary_r017.json').read_text(encoding='utf-8'))
keys=['code_sha256','protocol_sha256','source_refs','actual_loaded_helper_sha256','identity_gate','model_and_time_intervals','candidate_witness_bounds','residual_upper_diagnostics','maximum_Lg_upper','maximum_step_budget_upper','blocks','checks','contracts','outputs']
assert all(r[k]==s[k] for k in keys)
assert (HERE/'isolated-run/prefix_outward_blocks.csv').read_bytes()==(SOURCE/'prefix_outward_blocks.csv').read_bytes()
assert [(x['first_segment'],x['last_segment'],x['n_segments']) for x in r['blocks']]==[(0,16383,16384),(16384,16528,145)]
out={'passed':True,'elapsed_seconds':time.perf_counter()-started,'independent_method':'Exact Fraction interval arithmetic with independently bounded Machin pi, Taylor sine, and rational root bisection; frozen R025 pure arithmetic definitions reused, no outward helper imported.',
 'selected_residual_challenges':checks,'eight_parameter_time_intervals_contained':True,'prefix_Lg_global_upper_challenged':True,'exact_final_direction_checks_passed':True,'U_exact_coefficients_amplitudes_passed':True,
 'full_16529_segment_replay_equal':True,'prefix_csv_byte_identical':True,'replay_is_independent_algorithm':False,'decoded_array':'D_N16384 entire 98305x9 member; only first J+1 five-state columns used in budget',
 'exact_initial_states_zero':True,'candidate_witness_bounds':b,'scope':'Selected exact challenges complement whole-code and theorem review; neither replay nor finite challenges replace the helper and machine contract.'}
(HERE/'fraction-challenges-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'passed':True,'seconds':out['elapsed_seconds'],'selected':len(checks),'full_replay_equal':True}))
