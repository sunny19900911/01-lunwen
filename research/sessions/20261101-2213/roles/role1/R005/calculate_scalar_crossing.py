"""Recompute only the supplied frozen scalar example; no response arrays/ODE."""
from pathlib import Path
from decimal import Decimal, getcontext
import json, hashlib

O=Path(__file__).resolve().parent
F=json.loads((O/'input-freeze.json').read_text(encoding='utf-8'))
for source in F['sources']:
    assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256']
getcontext().prec=40
x={k:Decimal(v) for k,v in F['scalar_inputs'].items()}
p0,pj,g0,gj=[x[k] for k in ['p0','pj','g0','gj']]
assert p0>pj>0 and gj>g0
d=(p0-pj)/(gj-g0)
S0,Sj=-g0/p0,-gj/p0
b=100*d
b2=100*(1-pj/p0)/(S0-Sj)
h0,hj=p0+g0*d,pj+gj*d
assert abs(b-b2)<Decimal('1e-36')
assert abs(h0-hj)<Decimal('1e-36') and h0>0
result={'force_unit':F['force_unit'],'peak_gap_percent':str(100*(1-pj/p0)),
        'S0_percent_per_damping_pp':str(S0),'Sj_percent_per_damping_pp':str(Sj),
        'delta_cross_fraction':str(d),'b_cross_damping_pp':str(b),
        'zeta_at_linear_cross_fraction':str(x['zeta0']+d),
        'linear_cross_height_force':str(h0),'height_closure_error_force':str(h0-hj),
        'b_formula_equivalence_error_pp':str(b-b2),
        'meaning':'linear fixed-baseline-time warning only; not a verified target peak switch',
        'candidate_truth_read':False,'ODE_or_response_array':False}
with (O/'scalar-example-results.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(result,ensure_ascii=False))
