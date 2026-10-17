"""Exact polynomial checks for the candidate root-structure proof; no eigensolve/root search."""
from fractions import Fraction as F
from math import comb
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime, timezone, timedelta

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]

def add(a, b):
    out = dict(a)
    for power, value in b.items():
        out[power] = out.get(power, F(0)) + value
    return {power: value for power, value in out.items() if value}

def scale(a, value):
    return {power: coefficient * value for power, coefficient in a.items() if coefficient * value}

def mul(a, b):
    out = {}
    for (i, j), x in a.items():
        for (k, l), y in b.items():
            power = (i + k, j + l)
            out[power] = out.get(power, F(0)) + x * y
    return {power: value for power, value in out.items() if value}

one = {(0, 0): F(1)}
r = {(1, 0): F(1)}
z = {(0, 1): F(1)}
r2, z2 = mul(r, r), mul(z, z)
A = add(one, scale(r2, -2))
B = add(add(scale(r2, 8), scale(r, 8)), scale(one, 6))
c = add(scale(one, 3), scale(r, 2))
Bp = add(scale(r, 16), scale(one, 8))
N_from_diff = add(mul(add(scale(r, -4), scale(z, -2)), add(B, scale(z, -10))),
                  mul(c, add(mul(Bp, z), scale(mul(r, A), 8))))
N_expected = add(add(scale(z2, 20), mul(add(add(scale(r2, 16), scale(r, 88)), scale(one, 12)), z)),
                 scale(mul(r2, add(add(scale(r2, 2), scale(r, 5)), one)), -16))
assert N_from_diff == N_expected
N_at_r2 = {}
for (i, j), value in N_expected.items():
    N_at_r2[i + 2*j] = N_at_r2.get(i + 2*j, F(0)) + value
assert {k:v for k,v in N_at_r2.items() if v} == {2:F(-4), 3:F(8), 4:F(4)}
U = [F(41,36), F(22,3), -F(44,3), -F(80), -F(32)]
shift = [sum((U[j] * comb(j,k) * F(1,3)**(j-k) for j in range(k, len(U))), F(0)) for k in range(len(U))]
assert shift == [-F(455,324), -F(914,27), -F(116), -F(368,3), -F(32)]
assert all(x < 0 for x in shift)
endpoint = F(5,144) - F(86,9)/12 + F(49,81)
assert endpoint == -F(203,1296) < 0
assert F(1,9) + F(2,3) - 1 == -F(2,9) < 0
# The transformed quartic from the spectral invariants.
quartic = add(add(scale(z2, 5), scale(mul(B, z), -1)), mul(A, A))
quartic_expected = {(0,0):F(1), (2,0):F(-4), (4,0):F(4),
                     (0,1):F(-6), (1,1):F(-8), (2,1):F(-8), (0,2):F(5)}
assert quartic == quartic_expected
sources = [
    'papers/damping-output-boundaries/research/roles/ideation/round-009.md',
    'papers/damping-output-boundaries/research/roles/verification/appendix-V011-low-damping-IVT.md',
    'papers/damping-output-boundaries/research/roles/experiments/round-012-low-damping-bisection.md',
]
result = {
    'status':'candidate; exact algebra checks only, independent proof review pending',
    'executed_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
    'python':sys.version.split()[0],
    'method':'stdlib Fraction, bivariate polynomial coefficients; no eigenvalue computation, no root search',
    'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'sources':{s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sources},
    'checks':{'transformed_quartic':True,'derivative_numerator_identity':True,
              'substitute_z_r_squared':True,'negative_shift_coefficients':True,
              'quadratic_endpoint':True,'small_r_sign':True},
    'U_of_u_plus_one_third_ascending':[str(x) for x in shift],
    'F_at_r_one_third_z_one_twelfth':str(endpoint),
    'limitations':'Algebra checks do not establish trace ordering/implicit differentiation by themselves; see candidate proof. No directed rounding or E012 endpoint certificate.'
}
out=HERE/'root-structure-algebra.json'
assert not out.exists(), 'refuse to overwrite frozen result'
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
