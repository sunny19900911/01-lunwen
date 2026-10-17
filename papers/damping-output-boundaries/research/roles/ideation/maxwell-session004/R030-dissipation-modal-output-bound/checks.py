"""Tiny exact exponent/unit/inequality algebra; no trajectories or data."""
from fractions import Fraction as Q
from pathlib import Path
import json

exponent_checks = []
for alpha in (Q(3, 10), Q(2)):
    p, q = (1+alpha)/alpha, 1+alpha
    assert p > 1 and q > 1 and 1/p+1/q == 1
    c_exp, D_exp = 1/(1+alpha), alpha/(1+alpha)
    assert (1/alpha)/p == c_exp and 1/p == D_exp
    # c: force*time^alpha/length^alpha; D: force*length.
    force_exp = c_exp+D_exp
    time_exp = alpha*c_exp
    length_exp = -alpha*c_exp+D_exp
    assert force_exp == 1 and time_exp == 1/p and length_exp == 0
    assert (1/q-1)+time_exp == 0  # kernel norm time unit cancels.
    exponent_checks.append({'alpha': str(alpha), 'p': str(p), 'q': str(q),
                            'c_exponent': str(c_exp), 'D_exponent': str(D_exp)})

# Abstract alpha=1, H=1 constant functions: Holder algebra only.
# These constants are not claimed to be mechanical Green/Maxwell trajectories.
c1, c2, h1, h2, F1, F2 = Q(1), Q(4), Q(1), Q(2), Q(1), Q(8)
D1, D2 = F1*F1/c1, F2*F2/c2
sum_pairing = h1*F1+h2*F2
weighted_kernel_power = c1*h1*h1+c2*h2*h2
assert sum_pairing**2 == weighted_kernel_power*(D1+D2)
assert D1 == 1 and D2 == 16 and sum_pairing == 17
target_scale = Q(-3)
scaled_pairing = target_scale*sum_pairing
scaled_kernel_power = target_scale**2*weighted_kernel_power
assert scaled_pairing**2 == scaled_kernel_power*(D1+D2)
assert abs(scaled_pairing) == abs(target_scale)*abs(sum_pairing)

# Exact stationary physical bare-model counterexample to residual-force reuse.
u, velocity, force, external, K0, ke, B = [Q(1), Q(0), Q(0), Q(1), Q(1), Q(1), Q(1)]
assert K0*u+B*force == external
assert B*velocity == 0  # Fdot/kappa and g(0) both zero.
true_dissipation = Q(0)
residual = force-ke*B*u
assert true_dissipation == 0 and residual == -1
assert residual**2 > true_dissipation

result = {'all_passed': True, 'arithmetic': 'fractions.Fraction',
          'exponent_and_unit_checks': exponent_checks,
          'abstract_cross_device_Holder_equality_algebra': True,
          'target_scaling_check': True,
          'physical_full_force_not_FNA_residual_counterexample': True,
          'scope': 'Isolated algebra only; no actual Green/Maxwell equality trajectory, time integration, arrays, new data or parameter sweep.'}
Path(__file__).with_name('checks.json').write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result))
