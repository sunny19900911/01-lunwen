"""Tiny exact scalar identities, with no time integration or candidate read."""
from fractions import Fraction as Q
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
ROLE=ROOT/'papers/damping-output-boundaries/research/roles/verification/maxwell-session004'
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
freeze=json.loads((HERE/'protocol-freeze.json').read_text(encoding='utf-8'))
assert record(Path(freeze['protocol']['path']))==freeze['protocol']
paths=[Path(freeze['protocol']['path']),ROLE/'非零末力耗散峰力区间独审-R017.md',ROLE/'R017-proof-evidence.json',ROLE/'R017-review-validation.json',ROLE/'R039-finite-observation-neighbor-review/validation.json']
assert record(paths[1])['sha256']=='5a3596a03e9508861ccfda513ee170addf62c29a35ef97e4ed9e33a3db4c5c6d'
assert not (HERE/'source-freeze.json').exists()
write('source-freeze.json',{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'sources':[record(p) for p in paths],'new_role1_candidate_read':False,'only_mathematical_premise':'Old audited M-C018 in own R017 nonzero-terminal-force review, not literature/FNA R017.'})

# q=1 derivative values at one interior scalar point, not a trajectory.
k,V,gamma,M=Q(2),Q(2),Q(1,3),Q(2)
power=gamma*M*M;powerprime=2*gamma*M
tauprime=1/(k*(V-gamma*M))+1/(k*(V+gamma*M))
assert tauprime==2*V/(k*(V*V-gamma*gamma*M*M))==Q(9,16)
Lprime=power*tauprime;Delta=Q(5,7)
Uprime=Lprime+powerprime*Delta-power*tauprime
assert Lprime==Q(3,4)>0 and Uprime==powerprime*Delta==Q(20,21)>0
assert Lprime+powerprime*0-power*tauprime==0

# A scalar monotone example has a zero right-end slope yet is strictly increasing.
x,y=Q(3,2),Q(2)
U=lambda m:Q(2)-(m-2)**2/2
assert U(y)-U(x)==(y-x)*(4-x-y)/2==Q(1,8)>0
# D below U(h) is outside the restricted inverse image; clipping is necessary.
h,d=Q(1),Q(5,4)
assert d<U(h) and max(d,U(h))==U(h)
# Actual alpha=k=c=V=1 boundary family: h=1/2, T=log(2)+1.
# D0=log(2)-5/8 and U(h)=D0+1/4, so U^{-1}(D0) is outside its image.
h_actual=Q(1,2);waiting=Q(1)
assert h_actual*h_actual*waiting==Q(1,4)>0

# Exact hold-time sufficiency, also covering Delta=0 without dividing by Delta.
base=Q(5,11);P=Q(7,3);available=Q(4,5);hold=Q(2,5)
D=base+P*hold
assert base<=D<=base+P*available and (D-base)/P==hold
assert (base-base)/P==0
assert base+P*0==base
storage=Q(3,2)**2/(2*Q(5,4));dissipation=Q(8,7)
work=dissipation+storage
assert work-storage==dissipation
out={'all_passed':True,'arithmetic':'fractions.Fraction','tau_derivative_identity':True,'L_prime_positive_and_U_prime_cancellation':True,'U_prime_zero_at_time_endpoint':True,'zero_endpoint_slope_compatible_with_strict_increase':True,'restricted_inverse_clipping_boundary':True,'actual_Maxwell_boundary_counterexample_Uh_minus_D0':'1/4','holding_time_exact_interval_attainment':True,'zero_available_hold_time_no_Delta_division':True,'work_storage_shift':True,'new_role1_candidate_read':False,'scope':'Tiny exact scalars only. General monotonicity and inverse proof in independent report. No trajectories, arrays, ODE, parameter sweep or external search.'}
write('checks.json',out);print(json.dumps(out))
