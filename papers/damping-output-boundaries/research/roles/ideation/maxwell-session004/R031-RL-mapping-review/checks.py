"""Exact polynomial identities/antiderivatives, no quadrature or ODE."""
from fractions import Fraction as Q
from pathlib import Path
import json


def add(a, b):
    return [(a[i] if i < len(a) else Q(0))+(b[i] if i < len(b) else Q(0))
            for i in range(max(len(a), len(b)))]


def mul(a, b):
    r = [Q(0)]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i+j] += x*y
    return r


def derivative(a):
    return [i*x for i, x in enumerate(a)][1:]


def integral_0_1(a):
    return sum(x/Q(i+1) for i, x in enumerate(a))


IA, IB = [Q(0), Q(1)], [Q(0), Q(1, 2), Q(3, 2), Q(-1)]
assert IA[0] == IB[0] == 0 and sum(IA) == sum(IB) == 1
assert derivative(IB) == [Q(1, 2), Q(3), Q(-3)]
assert integral_0_1(IA) == integral_0_1(IB) == Q(1, 2)
drop_A, drop_B = integral_0_1(mul(IA, IA)), integral_0_1(mul(IB, IB))
assert drop_A == Q(1, 3) and drop_B == Q(59, 168)
assert drop_B-drop_A == Q(1, 56)
for I in (IA, IB):
    drop = mul(I, I)  # nonnegative I, Rv(I)=I^2.
    U = add(derivative(I), drop)
    power = integral_0_1(mul(I, U))
    dissipation = integral_0_1(mul(I, drop))
    stored_change = (sum(I)**2-I[0]**2)/2
    assert power == dissipation+stored_change
    assert integral_0_1(U) == sum(I)-I[0]+integral_0_1(drop)
result = {'all_passed': True, 'arithmetic': 'fractions.Fraction',
          'same_current_endpoints_and_charge': True,
          'charge_exact': '1/2', 'resistor_drop_integrals': ['1/3', '59/168'],
          'total_deformation_increment_difference': '1/56',
          'power_dissipation_storage_identity_both_polynomials': True,
          'scope': 'Exact symbolic polynomial antiderivatives only; no quadrature, ODE, extrema, source search, trajectories/arrays or data.'}
Path(__file__).with_name('checks.json').write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result))
