"""Targeted Fraction/scalar probes only; target main and NPZ are never opened."""
from pathlib import Path
from fractions import Fraction as Q
from datetime import datetime,timezone,timedelta
import ast,hashlib,json,math,runpy,sys
import numpy as np

HERE=Path(__file__).resolve().parent
freeze=json.loads((HERE/'input-freeze.json').read_text(encoding='utf-8'))
paths=[Path(x['path']) for x in freeze['inputs']]
for p,item in zip(paths,freeze['inputs']):
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
summary=json.loads(paths[3].read_text(encoding='utf-8'))
p=summary['model_and_time_intervals']
def bound(name):return tuple(Q(x) for x in p[name])
assert p['N']==16384 and p['J']==16529 and p['J']-p['N']==145
assert bound('Kdiag')==(Q(2),Q(2)) and bound('Koff')==(-Q(1),-Q(1))
assert bound('kappa')==(Q(8),Q(8)) and bound('c')==(Q(10),Q(10))
def add(x,y):return (x[0]+y[0],x[1]+y[1])
def mul(x,y):return (x[0]*y[0]+3*x[1]*y[1],x[0]*y[1]+x[1]*y[0])
cd=(Q(1,20),Q(1,20));co=(Q(1,20),-Q(1,20))
assert add(mul(cd,cd),mul(co,co))==(Q(1,50),Q(0))
assert add(mul(cd,co),mul(cd,co))==(-Q(1,100),Q(0))
wlo,whi=bound('sqrt3_interval'); olo,ohi=bound('sqrt2_input_omega_interval')
assert 0<wlo and wlo*wlo<=3<=whi*whi
assert 0<olo and olo*olo<=2<=ohi*ohi
cdlo,cdhi=bound('Cdiag');colo,cohi=bound('Coff')
assert cdlo<=(1+wlo)/20 and cdhi>=(1+whi)/20
assert colo<=(1-whi)/20 and cohi>=(1-wlo)/20
pl,ph=bound('PI_interval');hl,hh=bound('true_h_interval');N=p['N'];J=p['J']
assert hl<=20*pl/(ohi*N) and hh>=20*ph/(olo*N)
tl,th=bound('true_T_interval');jl,jh=bound('true_witness_time_interval')
assert tl<=N*hl and th>=N*hh and jl<=J*hl and jh>=J*hh and jl>th
for n in [0,N-1,N,J-1]:assert Q(20*n+10,N)==20*(Q(n)+Q(1,2))/N
assert 3<2**2 and 8<3**2 and Q(2,3)<1
threshold=tuple(Q(x) for x in summary['candidate_witness_bounds']['U_threshold_outward_interval'])
assert threshold[0]<=Q(241,100)<=threshold[1]
tree=ast.parse(paths[1].read_text(encoding='utf-8'));rootcalls=[]
for call in ast.walk(tree):
    if isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute) and call.func.attr=='root':
        assert isinstance(call.args[-1],ast.Constant) and type(call.args[-1].value) is int and call.args[-1].value==2
        rootcalls.append(ast.unparse(call))
assert len(rootcalls)==2
ns=runpy.run_path(str(paths[7]),run_name='helper_scalar_review');I=ns['I']
for force in [-10.,-1.,0.,1.,10.]:
    out=ns['g_power_10_3'](I.point(force),I.point(10))
    cube=(1 if force>=0 else -1)*abs(Q(force)/10)**10
    assert Q(out.lo)**3<=cube<=Q(out.hi)**3
    L=ns['g_derivative_upper'](abs(force),I.point(10))
    assert Q(L)**3>=Q(1,3)**3*(abs(Q(force))/10)**7
out=ns['g_power_10_3'](I(-2.,3.),I.point(10))
assert Q(out.lo)**3<=-Q(2,10)**10 and Q(out.hi)**3>=Q(3,10)**10
L=ns['g_derivative_upper'](3.,I.point(10));assert Q(L)**3>=Q(1,3)**3*Q(3,10)**7
tiny=math.nextafter(0.,math.inf);one=1.;half=float.fromhex('0x1p-53');odd=math.nextafter(one,math.inf)
probes={'minsub_exact':Q(tiny)==Q(1,2**1074),'sub_add':Q(tiny+tiny)==2*Q(tiny),
 'sub_mul':tiny*one==tiny,'sub_div':tiny/one==tiny,
 'normal_to_subnormal':float.fromhex('0x1p-1022')*float.fromhex('0x1p-52')==tiny,
 'tie_even_down':one+half==one,'tie_even_up':odd+half==math.nextafter(odd,math.inf),
 'negative_tie_even':-one-half==-one,'nextafter_zero':math.nextafter(tiny,-math.inf)==0.}
assert all(probes.values())
result={'scope':'Only parameter/time/helper and comparison-direction audit. No NPZ, ODE, cumulative residual or U proof replay.',
 'C_square_exact':{'diag':'1/50','off':'-1/100','equals':'K/100'},
 'K_spectrum':[1,3],'safe_norm_weights':[2,1,3],'output_compliance':'2/3',
 'rational_interval_checks':'sqrt2/sqrt3/C/h/T/tJ passed',
 'J_minus_N':J-N,'phase_identity':'omega*(n+1/2)*h=pi*(20n+10)/N',
 'threshold_encloses_exact_241_over_100':True,'explicit_root_calls':rootcalls,
 'g_scalar_cases':5,'g_crosszero_interval_case':True,'g_derivative_upper_cases':6,
 'post_numpy_runtime':{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'python':sys.version,'numpy':np.__version__,
  'executable':sys.executable,'float_info':[sys.float_info.radix,sys.float_info.mant_dig,sys.float_info.max_exp,sys.float_info.rounds],
  'probes':probes,'limit':'Finite process-time snapshot, not permanent or historical hardware mode proof.'},
 'all_small_source_sha_unchanged':True,'I_J_or_final_claim_certified':False}
(HERE/'checks.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(result,ensure_ascii=False,indent=2))
