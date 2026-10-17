"""Independent exact scalar/determinant checks; no source execution or state array."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
AUTHOR=ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R025-asymmetric-neighborhood'
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for x in read(AUTHOR/'artifact-manifest.json')['artifacts']:
    r=record(AUTHOR/x['file']);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
assert record(AUTHOR/'report.md')['sha256']=='002da4c102b207a9f50fa9e8882142b231a27ef99e69c6dbab20db0e18944046'
refs=read(AUTHOR/'source-freeze.json')['sources']
for x in refs:
    r=record(ROOT/x['path']);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
sources=[record(p) for p in sorted(set(list(AUTHOR.iterdir())+[ROOT/x['path'] for x in refs])) if p.is_file()]
adopt=read(ROOT/'research/sessions/20261017-2109/R011-nonlinear-certificate-adoption.json')
assert adopt['claim']=='M-C025'
for x in refs:
    if x['path'] in adopt['checked_sources']:assert x['sha256']==adopt['checked_sources'][x['path']]
summarypath=next(ROOT/x['path'] for x in refs if x['path'].endswith('/summary_r015.json'))
summary=read(summarypath);bounds=summary['candidate_bounds']
E=F(bounds['terminal_E_interval_candidate'][1]);radius=F(bounds['tail_sqrt_interval_candidate'][1]);IH=F(bounds['I_total_6T_upper_candidate'])
components=summary['terminal_energy_component_intervals']
assert F(components['total'][1])==E
assert E>=sum((F(components[k][1]) for k in ['kinetic','physical_elastic','device_spring']),F(0))
assert all(F(components[k][0])>=0 for k in ['kinetic','physical_elastic','device_spring'])
square_margin=radius*radius-2*E;assert square_margin>0
nominal=radius+IH;assert nominal<F('1.098')
assert F(bounds['early_upper_candidate'])<F('1.325') and F(bounds['tail_upper_candidate'])<F('1.325')
assert F(bounds['fixed_T_lower_candidate'])>F('8.809')
for key,hexbits in adopt['bound_binary64_hex'].items():assert F(float.fromhex(hexbits))==F(bounds[key])
assert adopt['safe_decimal_statements']['A_fulltime_peak_upper']=='1.325'
assert adopt['safe_decimal_statements']['B_at_T_lower']=='8.809'
# Independent rational pi enclosure (Machin identity, alternating arctan tails).
def atan_bounds(q,n=24):
    x=sum((F((-1)**j,(2*j+1)*q**(2*j+1)) for j in range(n)),F(0))
    y=x+F((-1)**n,(2*n+1)*q**(2*n+1));return min(x,y),max(x,y)
v=atan_bounds(5);w=atan_bounds(239);pi=(16*v[0]-4*w[1],16*v[1]-4*w[0])
assert pi[1]<F(22,7)
sqrt2_hi=F(99,70);assert sqrt2_hi*sqrt2_hi>2
mu=F(1,10**6);epsilon=F(1,1000);q=F('1.000001')
assert q*q*(1-mu)>1 and q*q>1+mu
rhoH=40*sqrt2_hi*mu*120*F(22,7);rhoT=40*sqrt2_hi*mu*20*F(22,7)
assert rhoH<F('.02134') and rhoT<F('.003556')
early=F('1.325')+q*F('.02134');tail=q*(q*F('1.098')+F('.02134'))
lower=F('8.809')-q*F('.003556');gap=lower-max(early,tail)
assert tail<early<F('1.35') and lower>F('8.80') and gap>F('7.45')
assert early==F('1.34634002134') and tail==F('1.119342217341098')
assert lower==F('8.805443996444') and gap==F('7.459103975104')
# Symbolic determinant coefficient identities; lower bounds apply to every |a|<=mu.
def pm(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out
def detpoly(center,off):
    p=pm([center,F(1)],[center,F(-1)]);p[0]-=off*off;return p
assert detpoly(1+epsilon,epsilon)==[1+2*epsilon,F(0),F(-1)]
assert 1+epsilon-mu>0 and 1+2*epsilon-mu*mu>0
assert detpoly(epsilon+mu,epsilon)==[2*epsilon*mu+mu*mu,F(0),F(-1)]
assert epsilon>0 and 2*epsilon*mu>0  # Ka-(1-mu)I positive for all |a|<=mu.
assert detpoly(mu*(1+epsilon),mu*epsilon)==[mu*mu*(1+2*epsilon),F(0),F(-1)]
assert mu*epsilon>0 and 2*epsilon*mu*mu>0  # (1+mu)K0-Ka positive.
K0=[[1+epsilon,-epsilon],[-epsilon,1+epsilon]];D=[[F(1),F(0)],[F(0),F(-1)]];P=[[F(0),F(1)],[F(1),F(0)]]
def mm(A,B):return [[sum((x*y for x,y in zip(r,c)),F(0)) for c in zip(*B)] for r in A]
assert mm(mm(P,K0),P)==K0 and mm(mm(P,D),P)==[[-x for x in r] for r in D]
assert mm(K0,D)!=mm(D,K0)  # Fixed C0=aI+bK0 generally nonclassical for nonzero perturbation.
for x in sources:assert record(Path(x['path']))==x
write(HERE/'source-freeze.json',sources)
out={'required_changes':0,'scope':'Exact frozen scalar/binary64 endpoint and symbolic 2x2 determinant identities only; no ODE, spectral scan or source script execution.',
 'complete_terminal_energy_three_components_and_total_checked':True,'sqrt_upper_square_margin_exact':str(square_margin),
 'nominal_true_full_state_radius_bound_exact':str(nominal),'nominal_radius_lt_1_098':True,'not_inferred_from_output_tail':True,
 'root_C025_hex_and_source_identities_match':True,'pi_upper_independently_enclosed_by_Machin_Fraction':True,
 'mu_exact':str(mu),'q_bounds_both_square_verified':True,'rho_H_rational_upper':str(rhoH),'rho_T_rational_upper':str(rhoT),
 'uniform_constants_exact_decimal':{'early':'1.34634002134','tail':'1.119342217341098','B_fixed_T_lower':'8.805443996444','gap_lower':'7.459103975104'},
 'fixed_thresholds_passed':True,'all_parameter_SPD_and_norm_comparisons_by_symbolic_determinants':True,
 'exchange_maps_a_to_minus_a_not_same_a_history':True,'fixed_C0_not_reset_to_modal5percent':True,
 'source_count':len(sources),'sources_unchanged':True,'NPZ_arrays_ODE_helper_source_execution_or_spectral_scan':False,
 'inherited_contract':'All adopted C025 mathematical/model/parameter/helper/decoding/machine/runtime conditions remain required; no engineering tolerance or priority claim.'}
write(HERE/'checks.json',out)
print(json.dumps(out,indent=2))
