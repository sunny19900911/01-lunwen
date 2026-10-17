"""Isolated rational algebra and inverse-domain logic; no trajectory or scan."""
from fractions import Fraction as Q
from pathlib import Path
import json

# Sum of up/down derivative kernels, at one exact admissible algebraic point.
kappa, V, g = Q(2), Q(3), Q(1)
tau_prime = 1/(kappa*(V-g))+1/(kappa*(V+g))
assert tau_prime == 2*V/(kappa*(V*V-g*g)) > 0
P, Pprime, slack = Q(5), Q(7), Q(2)
Lprime = P*tau_prime
assert Lprime > 0
Uprime = Lprime+Pprime*slack-P*tau_prime
assert Uprime == Pprime*slack > 0
assert Lprime+Pprime*Q(0)-P*tau_prime == 0

# Generic order-cell labels, NOT redefinitions or samples of Maxwell L/U.
dmin, d0, dmax = Q(1), Q(3), Q(7)
inverse_calls = []


def inverse_argument_contract(D):
    if not dmin <= D <= dmax:
        return None
    assert dmin <= D <= dmax  # L inverse image interval.
    u_arg = max(D, d0)
    assert d0 <= u_arg <= dmax  # U inverse image interval.
    inverse_calls.append({'D': str(D), 'L_argument': str(D),
                          'U_argument_after_clipping': str(u_arg),
                          'lower_is_h': D <= d0})
    return D, u_arg


assert inverse_argument_contract(Q(0)) is None
assert inverse_argument_contract(Q(8)) is None
assert inverse_argument_contract(dmin) == (dmin, d0)
assert inverse_argument_contract(d0) == (d0, d0)
assert inverse_argument_contract(Q(5)) == (Q(5), Q(5))
assert inverse_argument_contract(dmax) == (dmax, dmax)
assert not d0 <= dmin <= dmax  # Naive U inverse at Dmin is undefined.

# Algebra of the existing attainable-dissipation construction, not integration.
L, power, duration = Q(2), Q(3), Q(5)
D = Q(8)
ell = (D-L)/power
assert 0 <= ell <= duration
assert L+power*ell == D
assert (duration-ell)+ell == duration
assert (L-L)/power == 0
assert (L+power*duration-L)/power == duration
assert L+power*Q(0) == L  # zero-slack endpoint.

# Separate shortest-time singleton and correct work-to-dissipation shift.
h, terminal_cost = Q(2), Q(5)
singleton = lambda D: [h] if D == terminal_cost else []
assert singleton(terminal_cost) == [h] and singleton(terminal_cost+1) == []
shift = h*h/(2*kappa)
W = D+shift
assert W-shift == D

result = {'all_passed': True, 'arithmetic': 'fractions.Fraction',
          'derivative_sum_and_U_cancellation': True,
          'positive_interior_zero_terminal_U_derivative': True,
          'inverse_domain_branches': inverse_calls,
          'outside_D_domain_never_calls_inverse': True,
          'naive_lower_U_inverse_counterexample': True,
          'dwell_time_fill_and_endpoints': True,
          'shortest_time_singleton_and_work_shift': True,
          'scope': 'Logical order labels and isolated algebra only. No Maxwell function values approximated, inverse numerically solved, trajectory/array read, time integration or model parameter sweep.'}
Path(__file__).with_name('checks.json').write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result))
