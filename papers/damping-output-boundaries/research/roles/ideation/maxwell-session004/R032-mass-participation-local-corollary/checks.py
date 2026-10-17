"""Exact modal algebra only; the true q-minus inequality is inherited."""
from fractions import Fraction as Q
from pathlib import Path
import json

K = [[Q(2), Q(-1)], [Q(-1), Q(2)]]
plus, minus, r = [Q(1), Q(1)], [Q(1), Q(-1)], [Q(1), Q(1)]
dot = lambda x, y: sum(a*b for a, b in zip(x, y))
mv = lambda A, x: [dot(row, x) for row in A]
assert mv(K, plus) == plus
assert mv(K, minus) == [3*x for x in minus]
assert dot(plus, minus) == 0 and dot(plus, plus) == dot(minus, minus) == 2
rho_plus = dot(plus, r)**2/(dot(plus, plus)*dot(r, r))
rho_minus = dot(minus, r)**2/(dot(minus, minus)*dot(r, r))
assert rho_plus == 1 and rho_minus == 0
assert plus[1] == 1 and minus[1] == -1
assert minus[1]**2/dot(minus, minus) == Q(1, 2)  # beta-minus squared.
assert dot(plus, r)**2/dot(plus, plus) == 2  # Gamma-plus squared.
relative_sq = Q(11, 4)**2*2
node_sq = Q(11, 4)**2/2
assert relative_sq == Q(121, 8) > Q('3.88')**2
assert node_sq == Q(121, 32) > Q('1.94')**2
assert relative_sq-Q('3.88')**2 == Q(353, 5000)
assert node_sq-Q('1.94')**2 == Q(353, 20000)
# Purely algebraic same-subspace counterexample, not the true witness data.
u = [Q(-4), Q(0)]
u_tilde = [u[0], u[0]]
e = [x-y for x, y in zip(u, u_tilde)]
assert e[0] == 0 and dot(minus, u_tilde) == 0
assert e[0]-e[1] == u[0]-u[1]
assert max(abs(x) for x in e) >= abs(e[0]-e[1])/2
result = {'all_passed': True, 'arithmetic': 'fractions.Fraction',
          'eigenvalues': [1, 3], 'frequencies_symbolic': ['1', 'sqrt(3)'],
          'direction_effective_masses': [2, 0], 'direction_total_mass': 2,
          'direction_fractions': [1, 0], 'port_beta_minus_squared': '1/2',
          'relative_threshold_squared_margin': '353/5000',
          'max_node_threshold_squared_margin': '353/20000',
          'fixed_u1_for_all_reconstructions_counterexample': True,
          'scope': 'Exact conditional corollary only; no new q-minus estimate, interval/IEEE certification, original pages, NPZ, ODE, parameter scan or software experiment.'}
Path(__file__).with_name('checks.json').write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result))
