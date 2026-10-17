"""Isolated exact algebra only; no trajectories or new model numerics."""
from fractions import Fraction as Q
from pathlib import Path
import json

dot = lambda x, y: sum(a*b for a, b in zip(x, y))
mv = lambda A, x: [dot(row, x) for row in A]
C = [[Q(2), Q(0)], [Q(0), Q(0)]]
Cd = [[Q(1, 2), Q(0)], [Q(0), Q(0)]]
f, v = [Q(4), Q(0)], [Q(3), Q(5)]
center = [x/2 for x in mv(Cd, f)]
shift = [x-y for x, y in zip(v, center)]
power = dot(v, f)-dot(v, mv(C, v))
square_formula = dot(f, mv(Cd, f))/4-dot(shift, mv(C, shift))
assert power == square_formula
assert power <= dot(f, mv(Cd, f))/4
# Missing Range(C): exact point-power counterexample, not a time solution.
fn, vn = [Q(0), Q(1)], [Q(0), Q(2)]
assert dot(vn, fn)-dot(vn, mv(C, vn)) > dot(fn, mv(Cd, fn))/4

# B1 = (sqrt(2 E0) + integral beta)^2 / 2, exact radius form.
R0, input_integral = Q(2), Q(3)
E0 = R0*R0/2
B1 = (R0+input_integral)**2/2
assert B1 == Q(25, 2) and R0*R0/2 == E0
assert (R0+Q(0))**2/2 == E0
J, eps = Q(0), Q(1, 7)
assert J/(J+eps) <= 1  # zero-point regularized factor is harmless.

# Abstract order/units-free certificate comparisons, not predicted responses.
A, R = Q(5), Q(2)
assert min(A, A+R) == A
assert min(A, Q(1)+R) == Q(3) < A
assert min(A, Q(4)+R) == A
alpha = Q(3, 10)
p, q = (1+alpha)/alpha, 1+alpha
assert 1/p+1/q == 1 and 1/p > 0

result = {'all_passed': True, 'arithmetic': 'fractions.Fraction',
          'PSD_range_complete_square_identity': True,
          'no_range_pseudoinverse_counterexample': True,
          'L1_radius_factor_and_zero_point': True,
          'same_direct_reference_bound_is_redundant': True,
          'smaller_reference_alone_does_not_ensure_improvement': True,
          'scope': 'Exact algebra/branch examples only; no input data, trajectories, ODE, arrays, parameter scan, opposite candidate or performance claim.'}
Path(__file__).with_name('checks.json').write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result))
