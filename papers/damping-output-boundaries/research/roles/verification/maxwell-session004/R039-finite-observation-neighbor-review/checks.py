"""Independent tiny exact checks; no trajectories, arrays, or author execution."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone,timedelta
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
BASE=ROOT/'papers/damping-output-boundaries/research/roles'
AUTHOR=BASE/'ideation/maxwell-session004/R028-finite-observation-neighbor'
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
sources=[ROOT/'research/sessions/20261017-2109/finite-observation-neighbor-protocol-v001.md']+sorted(AUTHOR.iterdir())+[
 BASE/'ideation/maxwell-session004/R025-asymmetric-neighborhood/report.md',
 BASE/'verification/maxwell-session004/R034-asymmetric-neighborhood-review/report.md',
 BASE/'novelty/maxwell-session004/R018-asymmetry-contribution/report.md',
 BASE/'verification/maxwell-session004/R038-midpoint-independent-fine-replay/validation.json']
assert not (HERE/'checks.json').exists()
assert rec(AUTHOR/'report.md')['sha256']=='5b351b23bdc604a35ff3fbe102a394c18c1d83f79d40f1da4ce255dd6cb1629a'
assert rec(sources[0])['sha256']=='cbab6d483e835f05abe08d8468a7c89a9566dd5faa7eef8db5762b4ef472e0b4'
manifest=json.loads((AUTHOR/'artifact-manifest.json').read_text(encoding='utf-8'))
for item in manifest['artifacts']:
    actual=rec(AUTHOR/item['file']);assert actual['bytes']==item['bytes'] and actual['sha256']==item['sha256']
write('source-freeze.json',{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'sources':[rec(p) for p in sources],'scope':'Small source files only. No NPZ opened or hashed.'})

# Deliberately distinct exact scalars test the indispensable change of metric.
epsilon=Q(1,1000);a=Q(-1,2000000);kappa=Q(5,2)
def n2(u,w,v,y,F,A):return u*u+w*w+epsilon*(u-w)**2+A*(u*u-w*w)+v*v+y*y+F*F/kappa
u0,w0,v0,y0,F0=Q(2,3),Q(-5,4),Q(7,6),Q(1,8),Q(-3,2)
ua,wa,va,ya,Fa=Q(4,5),Q(-6,7),Q(8,9),Q(-2,11),Q(-7,5)
explicit=a*(u0*u0-w0*w0)/2
assert explicit!=0
energy_difference=(n2(ua,wa,va,ya,Fa,a)-n2(u0,w0,v0,y0,F0,0))/2
same_metric=(n2(ua,wa,va,ya,Fa,a)-n2(u0,w0,v0,y0,F0,a))/2
assert energy_difference==same_metric+explicit
def quadratic(x,y):return Q(3,10)*x*x+Q(1,5)*x*y+Q(2,5)*y*y
ev,ey=va-v0,ya-y0;sv,sy=va+v0,ya+y0
polar=Q(3,10)*ev*sv+Q(1,10)*(ev*sy+ey*sv)+Q(2,5)*ey*sy
assert quadratic(va,ya)-quadratic(v0,y0)==polar
assert Q(13,3)-1==Q(10,3) and Q(10,3)-1==Q(7,3)
# Integration of r*s gives r*H²/2, then the two layout budgets sum.
H=Q(13,2);r=Q(17,3)
assert 2*(r*H*H/2)==r*H*H
mu=Q(1,10**6);C=Q(7,3)
eta_small=Q(1,10**12);eta_large=Q(2,3)
as_=min(mu/2,eta_small/C);al=min(mu/2,eta_large/C)
assert as_==eta_small/C and al==mu/2
assert 0<as_<=mu/2 and 0<al<=mu/2
assert C*as_<=eta_small and C*al<=eta_large
assert C*as_/2<eta_small and C*al/2<eta_large
upper=Q('1.34634002134');lower=Q('8.805443996444')
gap=lower-upper
assert gap==Q('7.459103975104') and gap>Q('7.45') and gap/2>Q('3.725')
# The boundary can split arbitrarily close inputs; this is not a model sweep.
eps=Q(1,10**15)
quantize=lambda x:(x//1)
assert quantize(1-eps)==0 and quantize(1+eps)==1 and 2*eps<Q(1,10**12)
# For one fixed nonidentical scalar record pair, small error balls are disjoint.
d=Q(1,9);eta_fixed=Q(1,100)
assert 2*eta_fixed<d
out={'all_passed':True,'arithmetic':'fractions.Fraction','energy_explicit_metric_change_nonzero':True,'background_power_polarization_identity':True,'power_derivative_exponents':True,'cumulative_integral_factor':True,'both_min_branches_nonzero_and_common_midpoint_in_ball':True,'same_finite_window_gap':str(gap),'same_finite_window_half_gap':str(gap/2),'quantization_boundary_counterexample':True,'fixed_pair_small_radius_disjoint_counterexample':True,'scope':'Tiny exact algebra only; general proof is in report. No trajectories, arrays, ODE, parameter sweep, author code execution, external search or NPZ.'}
write('checks.json',out);print(json.dumps(out))
