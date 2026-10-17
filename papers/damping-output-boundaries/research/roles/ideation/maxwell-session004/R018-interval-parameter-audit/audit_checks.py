"""Scalar/Fraction audit only; never opens NPZ or executes budget main()."""
from pathlib import Path
from fractions import Fraction as Q
import ast
import hashlib
import json
import math
import runpy
import sys
import numpy as np  # Import before the basic-operation probes, as in target.

HERE = Path(__file__).resolve().parent
freeze = json.loads((HERE/'input-freeze.json').read_text(encoding='utf-8'))
paths = [Path(item['path']) for item in freeze['inputs']]
for path, item in zip(paths,freeze['inputs']):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
summary = json.loads(paths[2].read_text(encoding='utf-8'))
p = summary['parameter_enclosures']
def bounds(name): return tuple(Q(x) for x in p[name])
rlo,rhi=Q('1.7151372034229'),Q('1.7151372034230')
poly=lambda r:r**3-3*r+Q(1,10)
kap=lambda r:3*r*r-1-r**3/10
cfun=lambda r:3/r-1/r**3-Q(1,10)
assert poly(rlo)<0<poly(rhi) and 3*rlo*rlo-3>0 and 1<rlo<rhi<2
rl,rh=bounds('r_interval'); assert rl<=rlo<rhi<=rh
kl,kh=bounds('kappa_interval'); cl,ch=bounds('c_interval')
assert kl<=kap(rlo)<kap(rhi)<=kh and 7<kl<kh<8
assert 0<cl<=cfun(rhi)<cfun(rlo)<=ch
assert bounds('Kdiag_interval')[0]<=Q(1001,1000)<=bounds('Kdiag_interval')[1]
assert bounds('Koff_interval')[0]<=-Q(1,1000)<=bounds('Koff_interval')[1]
wl,wh=bounds('sqrt501over500_interval'); assert 0<wl and wl**2<=Q(501,500)<=wh**2
cdl,cdh=bounds('Cdiag_interval'); col,coh=bounds('Coff_interval')
assert cdl<=(1+wl)/20 and cdh>=(1+wh)/20
assert col<=(1-wh)/20 and coh>=(1-wl)/20
pl,ph=bounds('PI_interval'); hl,hh=bounds('h_interval')
N=16384; assert hl<=Q(20,N)*pl and hh>=Q(20,N)*ph
for n in [0,1,N//2,N-1,N,6*N-1]:
    assert Q(20*n+10,N)==Q(20,N)*(Q(n)+Q(1,2))
assert N*Q(20,N)==20 and 6*N*Q(20,N)==120
ns=runpy.run_path(str(paths[4]),run_name='helper_for_scalar_audit'); I=ns['I']
gchecks=0
for force in [-2.,-1.,0.,1.,2.]:
    out=ns['g_power_10_3'](I.point(force),I(float(cl),float(ch)))
    for cv in [cfun(rlo),cfun(rhi)]:
        target_cube=(1 if force>=0 else -1)*abs(Q(force)/cv)**10
        assert Q(out.lo)**3<=target_cube<=Q(out.hi)**3
        upper=ns['g_derivative_upper'](abs(force),I(float(cl),float(ch)))
        derivative_cube=(Q(10,3)/cv)**3*abs(Q(force)/cv)**7
        assert Q(upper)**3>=derivative_cube
        gchecks+=2
Ehi=Q(summary['candidate_bounds']['terminal_E_interval_candidate'][1])
tl,th=(Q(x) for x in summary['candidate_bounds']['tail_sqrt_interval_candidate'])
assert 0<tl and tl*tl<=2*Ehi<=th*th
tree=ast.parse(paths[0].read_text(encoding='utf-8'))
root_calls=[]
for call in ast.walk(tree):
    if isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute) and call.func.attr=='root':
        root_calls.append(ast.unparse(call))
        assert isinstance(call.args[-1],ast.Constant) and type(call.args[-1].value) is int and call.args[-1].value==2
assert len(root_calls)==2
tiny=math.nextafter(0.,math.inf); one=1.; half_ulp=float.fromhex('0x1p-53')
odd=math.nextafter(one,math.inf); even2=math.nextafter(odd,math.inf)
probes={
 'minimum_subnormal_exact':Q(tiny)==Q(1,2**1074),
 'subnormal_add':Q(tiny+tiny)==2*Q(tiny),
 'subnormal_input_multiply':tiny*one==tiny,
 'subnormal_input_divide':tiny/one==tiny,
 'normal_product_to_subnormal':float.fromhex('0x1p-1022')*float.fromhex('0x1p-52')==tiny,
 'nearest_even_tie_down':one+half_ulp==one,
 'nearest_even_tie_up':odd+half_ulp==even2,
 'negative_nearest_even':-one-half_ulp==-one,
 'nextafter_roundtrip':math.nextafter(tiny,-math.inf)==0.,
}
assert all(probes.values())
result={
 'scope':'Scalar exact-rational and post-NumPy finite runtime probes; no NPZ access, ODE or all-segment budget replay.',
 'r_polynomial_signs':[str(poly(rlo)),str(poly(rhi))],
 'r_derivative_lower':str(3*rlo*rlo-3),
 'kappa_exact_endpoint_range':[str(kap(rlo)),str(kap(rhi))],
 'c_exact_endpoint_range':[str(cfun(rhi)),str(cfun(rlo))],
 'parameters_and_K_C_h_enclosures':'all exact Fraction checks passed',
 'g_and_derivative_exact_cube_checks':gchecks,
 'terminal_sqrt_encloses_2_reported_Ehi':True,
 'terminal_Ehi_itself_audited':False,
 'explicit_main_root_calls':root_calls,
 'post_numpy_runtime':{'python':sys.version,'executable':sys.executable,'numpy':np.__version__,
     'float_info':{'radix':sys.float_info.radix,'mant_dig':sys.float_info.mant_dig,'max_exp':sys.float_info.max_exp,'rounds':sys.float_info.rounds},
     'finite_probes':probes,'limit':'Snapshot in this audit process. Does not prove permanent absence of FTZ/DAZ or historic runtime rounding-mode changes.'},
 'source_and_small_input_sha_unchanged':all(hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'] for path,item in zip(paths,freeze['inputs']))
}
(HERE/'audit-results.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(result,ensure_ascii=False,indent=2))
