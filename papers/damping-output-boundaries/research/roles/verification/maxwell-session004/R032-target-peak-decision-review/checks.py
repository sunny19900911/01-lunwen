"""Independent exact PL/function challenges; no author script, ODE or arrays."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
AUTHOR=ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R023-target-peak-decision'
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for x in read(AUTHOR/'artifact-manifest.json')['artifacts']:
    r=record(AUTHOR/x['name']);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
assert record(AUTHOR/'report.md')['sha256']=='d119ec9239da9c3b376afb3d39e4df89b98e0a415ad8bba1ba56cbffa3d6779d'
inputs=read(AUTHOR/'input-freeze.json')['inputs']
for x in inputs:assert record(Path(x['path']))==x
sources=[record(p) for p in sorted(set(list(AUTHOR.iterdir())+[Path(x['path']) for x in inputs])) if p.is_file()]
def value(pl,t):
    assert pl[0][0]<=t<=pl[-1][0]
    for (a,u),(b,v) in zip(pl,pl[1:]):
        if a<=t<=b:return u+(v-u)*(t-a)/(b-a)
    raise AssertionError('PL interval absent')
def addpl(*curves):
    knots=sorted(set(t for curve in curves for t,_ in curve))
    return [(t,sum((value(curve,t) for curve in curves),F(0))) for t in knots]
def peak(pl):return max(abs(y) for _,y in pl)
def nodes(vals,knots=(F(0),F(1,2),F(1))):return list(zip(knots,map(F,vals)))
def decide(U,Z,etaU=F(0),etaC=F(0),eps=F(0)):
    if eps is None:return {'decision':'unclosed_remainder'}
    assert min(U,Z,etaU,etaC,eps)>=0
    delta=etaU+etaC+eps
    LU,HU=max(F(0),U-etaU),U+etaU
    LD,HD=max(F(0),Z-delta),Z+delta
    return {'decision':'decrease' if HD<LU else 'increase' if LD>HU else 'inconclusive','U':(LU,HU),'D':(LD,HD)}
# All endpoint-sign PL errors satisfy their full-window sup budgets.
u=nodes([0,2,-1]);etaU=F(1,20);etaC=F(1,40);eps=F(1,40)
families=[]
for factor,expected in [(F(-1,2),'decrease'),(F(1,2),'increase')]:
    c=[(t,factor*y) for t,y in u];z=addpl(u,c);d=decide(peak(u),peak(z),etaU,etaC,eps)
    assert d['decision']==expected
    tested=0
    for signs in product([-1,1],repeat=9):
        eu=nodes([etaU*s for s in signs[:3]]);ec=nodes([etaC*s for s in signs[3:6]]);r=nodes([eps*s for s in signs[6:]])
        trueU=addpl(u,eu);trueD=addpl(u,eu,c,ec,r);pu,pd=peak(trueU),peak(trueD)
        assert d['U'][0]<=pu<=d['U'][1] and d['D'][0]<=pd<=d['D'][1]
        assert (pd<pu) if expected=='decrease' else (pd>pu)
        tested+=1
    families.append({'verdict':expected,'exact_PL_error_corners':tested})
# Different knot sets must be merged before evaluating the sum peak.
linear=[(F(0),F(0)),(F(1),F(1,2))]
tent=[(F(0),F(0)),(F(1,3),F(1)),(F(1),F(0))]
assert peak(addpl(linear,tent))==F(7,6)
assert max(abs(value(linear,t)+value(tent,t)) for t,_ in linear)==F(1,2)
# Same shared reference error can reverse either naive verdict if removed from D.
knots=(F(0),F(1,3),F(2,3),F(1));counter=[]
for uh,ch,error,false_order,true_order in [
    ([0,2,2,0],[0,-1,F(3,10),0],[0,F(1,5),F(-1,5),0],'increase','decrease'),
    ([0,F(23,10),F(19,10),0],[0,F(-1,2),F(1,10),0],[0,F(-1,5),F(1,5),0],'decrease','increase')]:
    U=nodes(uh,knots);C=nodes(ch,knots);E=nodes(error,knots);Z=addpl(U,C)
    PU,PD=peak(addpl(U,E)),peak(addpl(U,E,C))
    correct=decide(peak(U),peak(Z),etaU=F(1,5))
    LU,HU=peak(U)-F(1,5),peak(U)+F(1,5)
    wrong='increase' if peak(Z)>HU else 'decrease' if peak(Z)<LU else 'inconclusive'
    assert wrong==false_order and correct['decision']=='inconclusive'
    assert (PD<PU) if true_order=='decrease' else (PD>PU)
    counter.append({'wrong_if_U_error_removed':wrong,'actual_order':true_order,'actual_U_peak':str(PU),'actual_D_peak':str(PD)})
assert decide(F(2),F(7,4),eps=F(1,4))['decision']=='inconclusive'
assert decide(F(2),F(9,4),eps=F(1,4))['decision']=='inconclusive'
assert decide(F(0),F(0))['decision']=='inconclusive'
assert decide(F(0),F(1))['decision']=='increase'
assert decide(F(2),F(1),eps=None)['decision']=='unclosed_remainder'
assert decide(F(1),F(1),eps=F(1,10))['decision']=='inconclusive'
assert F(9,10)<1<F(11,10)  # Identical center/epsilon admits either peak order.
# Lipschitz hidden interior peak attains the hmax/2 bound on a nonuniform grid.
hidden=[(F(0),F(0)),(F(1,3),F(1)),(F(2,3),F(0)),(F(1),F(0))]
grid=[F(0),F(2,3),F(1)];M=max(abs(value(hidden,t)) for t in grid);L=F(3);hmax=F(2,3)
assert M==0 and peak(hidden)==M+L*hmax/2==1
# Omitting a window endpoint invalidates nearest-node hmax/2.
grid_bad=[F(1,2),F(1)];badM=max(1-t for t in grid_bad)
assert badM+F(1)*(grid_bad[1]-grid_bad[0])/2==F(3,4)<1
# Nodal evaluation errors must also reduce the lower bound.
observed=F(11,10);etaN=F(1,10);true_constant_peak=F(1)
assert observed>true_constant_peak and observed-etaN==true_constant_peak
# Different peak times: the peak of a difference is not the difference of peaks.
ua=nodes([0,1,0],(F(0),F(1,3),F(1)));da=nodes([0,1,0],(F(0),F(2,3),F(1)))
assert peak(da)-peak(ua)==0 and peak(addpl(da,[(t,-y) for t,y in ua]))>0
for x in sources:assert record(Path(x['path']))==x
write(HERE/'source-freeze.json',sources)
out={'required_changes':0,'scope':'Exact abstract real PL/function error-contract challenges; no mechanical realization, unknown 56-device residual, ODE or engineering decision claimed.',
 'independent_robust_PL_families':families,'PL_breakpoint_union_peak':'7/6; using only reference knots gives 1/2',
 'shared_reference_error_reverses_both_naive_orders':counter,'strict_equality_zero_peak_and_unclosed_remainder_cases_passed':True,
 'same_center_same_eps_admits_both_orders':True,'Lipschitz_nonuniform_grid_hidden_peak_attains_gap_half':True,
 'omitting_window_endpoint_fails_gap_half_bound':True,'nodal_error_lower_bound_subtraction_necessary':True,
 'different_peak_times_challenge_passed':True,'small_source_count':len(sources),'sources_unchanged':True,
 'author_script_ODE_arrays_or_NPZ_access':False,'unknown56_remainder_assumed_zero':False}
write(HERE/'checks.json',out)
print(json.dumps(out,indent=2))
