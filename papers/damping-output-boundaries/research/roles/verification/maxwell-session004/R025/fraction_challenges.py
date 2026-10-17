"""Independent exact-Fraction checks; no helper import and no ODE solve."""
from pathlib import Path
from fractions import Fraction as F
from math import factorial
import hashlib, json, time
import numpy as np

ROOT=Path.cwd()
HERE=Path(__file__).resolve().parent
SOURCE=ROOT/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R015-outward-residual-certificate/v002-run'

def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[1],-a[0])
def sub(a,b):return add(a,neg(b))
def mul(a,b):
    c=[x*y for x in a for y in b];return min(c),max(c)
def div(a,b):
    assert not b[0]<=0<=b[1]
    return mul(a,(1/b[1],1/b[0]))
def point(x):q=F(x);return q,q
def scale(a,q):return mul(a,point(q))
def power(a,n):
    out=point(1)
    for _ in range(n):out=mul(out,a)
    return out
def contains(outer,inner):return F(outer[0])<=inner[0]<=inner[1]<=F(outer[1])
def decgrid(a,places=50):
    d=10**places
    return F(a[0]*d//1,d),F(-((-a[1]*d)//1),d)
def atan_bounds(d,n=40):
    s=sum((F((-1)**j,(2*j+1)*d**(2*j+1)) for j in range(n)),F(0))
    t=s+F((-1)**n,(2*n+1)*d**(2*n+1))
    return min(s,t),max(s,t)
def root_bracket(q,degree,iterations=190):
    assert q>=0
    if q==0:return point(0)
    lo=F(0);hi=max(F(1),q)
    for _ in range(iterations):
        m=(lo+hi)/2
        if m**degree<=q:lo=m
        else:hi=m
    return lo,hi
def sin_phase(n,d,pi):
    n%=2*d
    if n>d:n-=2*d
    if 2*n>d:n=d-n
    elif 2*n < -d:n=-d-n
    x=scale(pi,F(n,d));m=(x[0]+x[1])/2
    assert abs(m)<2
    term=m;s=m
    for j in range(1,40):
        term*= -m*m/F(2*j*(2*j+1));s+=term
    err=F(2**81,factorial(81))+(x[1]-x[0])/2
    return s-err,s+err
def signed_g(mid,c):
    if mid==0:return point(0)
    ratio=div(point(abs(mid)),c)
    target=power(ratio,10)
    out=(root_bracket(target[0],3)[0],root_bracket(target[1],3)[1])
    return out if mid>0 else neg(out)

started=time.perf_counter()
summary=json.loads((SOURCE/'summary_r015.json').read_text(encoding='utf-8'))
refs=summary['source_refs']
cache=Path(refs['endpoint_cache']['path'])
assert hashlib.sha256(cache.read_bytes()).hexdigest()==refs['endpoint_cache']['sha256']
with np.load(cache,allow_pickle=False) as z:
    a=z['endpoints'];assert a.dtype==np.float64 and a.shape==(98305,6)
    states=a[:,1:6].copy()
assert np.isfinite(states).all() and np.all(states[0]==0)
a5=atan_bounds(5);a239=atan_bounds(239)
pi=decgrid(sub(scale(a5,16),scale(a239,4)))
N=16384;h=scale(pi,F(20,N));invh=div(point(1),h)
poly=lambda x:x**3-3*x+F(1,10)
lo=F('1.7151372034229');hi=F('1.7151372034230')
assert poly(lo)<0<poly(hi)
for _ in range(160):
    m=(lo+hi)/2
    if poly(m)<0:lo=m
    else:hi=m
r=decgrid((lo,hi));kap=sub(sub(scale(power(r,2),3),point(1)),scale(power(r,3),F(1,10)))
c=div(kap,power(r,3));w=decgrid(root_bracket(F(501,500),2))
cd=scale(add(point(1),w),F(1,20));co=scale(sub(point(1),w),F(1,20))
kd=point(F(1001,1000));ko=point(F(-1,1000))
checks=[]
for name,info in summary['residual_enclosure_diagnostics'].items():
    n=info['segment'];left=list(map(lambda x:F(float(x)),states[n]));right=list(map(lambda x:F(float(x)),states[n+1]))
    delta=[y-x for x,y in zip(left,right)];mid=[(x+y)/2 for x,y in zip(left,right)]
    forcing=sin_phase(20*n+10,N,pi) if n<N else point(0)
    ru1=sub(scale(invh,delta[0]),point(mid[2]));ru2=sub(scale(invh,delta[1]),point(mid[3]))
    rv1=sub(add(add(add(add(scale(invh,delta[2]),scale(cd,mid[2])),scale(co,mid[3])),add(scale(kd,mid[0]),scale(ko,mid[1]))),point(mid[4])),forcing)
    rv2=sub(add(add(add(scale(invh,delta[3]),scale(cd,mid[3])),scale(co,mid[2])),add(scale(kd,mid[1]),scale(ko,mid[0]))),forcing)
    rf=add(sub(div(point(delta[4]),mul(kap,h)),point(mid[2])),signed_g(mid[4],c))
    target=dict(zip(['r_u1','r_u2','r_v1','r_v2','r_F'],[ru1,ru2,rv1,rv2,rf]))[name]
    assert contains(info['enclosure'],target),(name,n)
    checks.append({'residual':name,'segment':n,'independent_exact_rational_interval_contained':True})

u1,u2,v1,v2,force=list(map(lambda x:F(float(x)),states[-1]))
kin=point((v1*v1+v2*v2)/2)
elastic=point(F(1001,2000)*(u1*u1+u2*u2)-F(1,1000)*u1*u2)
spring=div(point(force*force),scale(kap,2));energy=add(add(kin,elastic),spring)
for key,value in [('kinetic',kin),('physical_elastic',elastic),('device_spring',spring),('total',energy)]:
    assert contains(summary['terminal_energy_component_intervals'][key],value)
b=summary['candidate_bounds'];p=F(b['I_prefix_T_upper_candidate']);total=F(b['I_total_6T_upper_candidate'])
maxnode=F(float(np.max(np.abs(states[:,0]))));atT=abs(F(float(states[N,1])))
assert F(b['exact_stored_maxnode_abs_uh1'])==maxnode
assert F(b['exact_stored_abs_uh2_N'])==atT
assert F(b['tail_sqrt_interval_candidate'][1])**2>=2*F(b['terminal_E_interval_candidate'][1])
assert F(b['early_upper_candidate'])>=maxnode+total
assert F(b['tail_upper_candidate'])>=F(b['tail_sqrt_interval_candidate'][1])+total
assert F(b['fixed_T_lower_candidate'])<=atT-p
assert F(b['gap_lower_candidate'])<=F(b['fixed_T_lower_candidate'])-max(F(b['early_upper_candidate']),F(b['tail_upper_candidate']))
assert F(b['gap_lower_candidate'])>0 and p<=total
isolated=json.loads((HERE/'isolated-run/summary_r015.json').read_text(encoding='utf-8'))
for key in ['candidate_bounds','parameter_enclosures','residual_enclosure_diagnostics','terminal_energy_component_intervals']:
    assert isolated[key]==summary[key],key
assert (HERE/'isolated-run/six_block_outward_budget.csv').read_bytes()==(SOURCE/'six_block_outward_budget.csv').read_bytes()
out={'passed':True,'elapsed_seconds':time.perf_counter()-started,
    'method':'Independent Fraction interval arithmetic, independent Machin/Taylor rational bounds and verified rational root bisections; no outward helper import and no ODE.',
    'selected_residual_challenges':checks,'terminal_component_enclosures_passed':4,
    'exact_final_direction_checks_passed':True,'isolated_full_98304_segment_results_equal':True,
    'six_block_csv_byte_identical':True,'NPZ_only_endpoints_decoded':True,
    'exact_initial_states_zero':True,'final_bounds':b,
    'scope':'Selected exact challenges plus independent review; finite challenges are not a substitute for the general interval/helper proof.'}
(HERE/'fraction-challenges-result.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'passed':True,'seconds':out['elapsed_seconds'],'selected':len(checks),'terminal':4,'replay_equal':True}))
