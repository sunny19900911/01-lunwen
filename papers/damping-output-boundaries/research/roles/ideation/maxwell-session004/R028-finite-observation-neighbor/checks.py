"""Tiny exact identities and observation-set branches, never a model sweep."""
from fractions import Fraction as Q
from pathlib import Path
import json


def bilinear(x, A, y):
    return sum(x[i]*A[i][j]*y[j] for i in range(2) for j in range(2))


K0 = [[Q(1001, 1000), Q(-1, 1000)], [Q(-1, 1000), Q(1001, 1000)]]
D = [[Q(1), Q(0)], [Q(0), Q(-1)]]
a = Q(1, 10**7)
Ka = [[K0[i][j]+a*D[i][j] for j in range(2)] for i in range(2)]
u0, ua = [Q(1), Q(-2)], [Q(3, 2), Q(-7, 4)]
v0, va = [Q(2), Q(-1)], [Q(5, 3), Q(-4, 3)]
F0, Fa, kappa = Q(2), Q(7, 3), Q(3)


def N2(K, u, v, F):
    return bilinear(u, K, u)+sum(x*x for x in v)+F*F/kappa


lhs = (N2(Ka, ua, va, Fa)-N2(K0, u0, v0, F0))/2
same_metric = (N2(Ka, ua, va, Fa)-N2(Ka, u0, v0, F0))/2
explicit_change = a*bilinear(u0, D, u0)/2
assert explicit_change != 0 and lhs == same_metric+explicit_change
C = [[Q(1, 5), Q(1, 10)], [Q(1, 10), Q(2, 5)]]
ev, vsum = [x-y for x, y in zip(va, v0)], [x+y for x, y in zip(va, v0)]
assert bilinear(va, C, va)-bilinear(v0, C, v0) == bilinear(ev, C, vsum)
assert Q(10, 3)-1 == Q(7, 3)
assert Q(13, 3)-1 == Q(10, 3)
# Exact integral coefficient identities underlying the cumulative bounds.
t, c0, radius, lp, sqrt_k = Q(7), Q(2), Q(3), Q(5), Q(2)
integral_s = t*t/2
assert 2*c0*radius**2*integral_s == c0*radius**2*t*t
assert 2*lp*sqrt_k*radius*integral_s == lp*sqrt_k*radius*t*t

# Exercise the two analytic min branches; these are not physical model runs.
mu, Cobs = Q(1, 10**6), Q(3, 2)
branches = []
for eta in (Q(1, 10**12), Q(1, 10)):
    a_selected = min(mu/2, eta/Cobs)
    dist = Cobs*a_selected
    assert 0 < a_selected <= mu/2 and dist <= eta < 2*eta
    obsA, obsB = -dist/2, dist/2
    common = (obsA+obsB)/2
    assert abs(common-obsA) <= eta/2 < eta
    assert abs(common-obsB) <= eta/2 < eta
    branches.append({'active': 'mu/2' if a_selected == mu/2 else 'eta/Cobs',
                     'nonzero_a_and_common_error_ball': True})

# Exact triangle inequality example, not actual certified model peaks.
PA, PB, estimate = Q(1), Q(9), Q(13, 3)
assert PB-PA <= abs(estimate-PA)+abs(estimate-PB)
assert max(abs(estimate-PA), abs(estimate-PB)) >= (PB-PA)/2
eps = Q(1, 10**12)
quantize = lambda x: 2*((x+1)//2)
assert quantize(1-eps) == 0 and quantize(1+eps) == 2
assert (1+eps)-(1-eps) == 2*eps

result = {'all_passed': True, 'arithmetic': 'fractions.Fraction',
          'energy_metric_change_term_nonzero_and_correct': True,
          'background_power_difference_identity': True,
          'nonlinear_derivative_exponents_and_integral_factors': True,
          'observation_min_branches': branches,
          'two_point_triangle_example': True,
          'quantization_boundary_counterexample': True,
          'scope': 'Isolated synthetic identities only. General inequalities and quantifiers are proved in report. No temporal integration, trajectory, NPZ/array read or model-parameter sweep.'}
Path(__file__).with_name('checks.json').write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result))
