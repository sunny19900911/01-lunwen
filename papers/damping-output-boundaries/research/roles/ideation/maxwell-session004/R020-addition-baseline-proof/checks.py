"""Exact rational coefficient checks; no dynamics or experiment output reads."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json

HERE=Path(__file__).resolve().parent
freeze=json.loads((HERE/'input-freeze.json').read_text(encoding='utf-8'))
for item in freeze['inputs']:
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256']
A=-Q(50,51); B_over_sqrt2=-Q(5,51); C_over_sqrt2=Q(5,51)
nuD_over_sqrt2=Q(67,68); a=Q(1,20); nu2=Q(399,400); omega2=Q(2)
assert (1-omega2)*A-Q(1,10)*omega2*B_over_sqrt2==1
assert (1-omega2)*B_over_sqrt2+Q(1,10)*A==0
assert B_over_sqrt2+C_over_sqrt2==0
assert A-a*C_over_sqrt2+nuD_over_sqrt2==0
Ap2=A*A+2*B_over_sqrt2**2
R2=2*C_over_sqrt2**2+2*nuD_over_sqrt2**2/nu2
assert Ap2==Q(50,51)<1
assert R2==Q(40000,20349)<Q(141,100)**2
assert A==-(-a*C_over_sqrt2+nuD_over_sqrt2)
assert Q(2)<Q(3,2)**2
assert Q(141,100)*Q(5,4)==Q(141,80)==Q('1.7625')<Q('2.41')
assert Q(1)+Q(141,100)==Q('2.41')
result={'scope':'Exact Fraction coefficient/initial state/amplitude algebra only; no ODE or D experiment reads.',
        'particular_sine_cosine_equations':True,'zero_initial_u_v':True,
        'particular_amplitude_squared':str(Ap2),'homogeneous_radius_squared':str(R2),
        'R_squared_gap_to_1.41_squared':str(Q(141,100)**2-R2),
        'cutoff_particular_state_is_negative_homogeneous_initial_state':True,
        'tail_exact_identity':'x(T+tau)=-xh(tau)+xh(T+tau)',
        'tail_safe_upper':'1.7625 strict','U_fulltime_safe_upper':'2.41 strict',
        'D_node_for_conditional_example':'T, already-frozen N=16384 grid node N',
        'D_certified_lower_available':False,'D_strict_increase_proved':False,
        'output_compliance_new_K':str(Q(2,3)),
        'source_sha_unchanged':True}
(HERE/'checks.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(result,ensure_ascii=False,indent=2))
