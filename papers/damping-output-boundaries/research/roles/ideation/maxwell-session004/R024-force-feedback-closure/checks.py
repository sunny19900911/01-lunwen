"""Tiny exact algebra only; no time integration or engineering data."""
from fractions import Fraction as Q
from pathlib import Path
import json


def add(a, b):
    return [[x + y for x, y in zip(r, s)] for r, s in zip(a, b)]


def mul(a, b):
    return [[sum(x * y for x, y in zip(r, c)) for c in zip(*b)] for r in a]


def tr(a):
    return [list(c) for c in zip(*a)]


def inv(a):
    x, y = a[0]
    z, w = a[1]
    det = x * w - y * z
    assert det != 0
    return [[w / det, -y / det], [-z / det, x / det]]


def diag(x, y):
    return [[x, Q(0)], [Q(0), y]]


B = [[Q(1), Q(0)], [Q(-1), Q(1)]]
f = [[Q(1)], [Q(2)]]
cases = []
for s in (Q(1, 2), Q(1), Q(3)):
    # M=I, C=I/5, K=[[2,-1],[-1,2]]; zero initial states.
    A = [[s * s + s / 5 + 2, Q(-1)],
         [Q(-1), s * s + s / 5 + 2]]
    S = inv(A)
    H = mul(mul(B, S), tr(B))
    assert H[0][1] != 0 and H[1][0] != 0
    compliance = diag(Q(1, 2) + 1 / (4 * s), Q(1, 3) + 1 / (5 * s))
    Z = inv(compliance)  # alpha=1: F(s)=Z(s) delta(s).
    uU = mul(S, f)
    deltaU = mul(B, uU)
    F = mul(inv(add(compliance, H)), deltaU)
    correction = mul(mul(S, tr(B)), F)
    uD = [[a[0] - b[0]] for a, b in zip(uU, correction)]
    direct = mul(inv(add(A, mul(mul(tr(B), Z), B))), f)
    assert uD == direct
    assert mul(B, uD) == mul(compliance, F)
    cases.append({'s': str(s), 'direct_equals_feedback': True,
                  'cross_port_kernel_nonzero': True})

# Nonzero-state compatibility fixes the affine signs, componentwise.
delta0 = [Q(2), Q(-1)]
F0 = [Q(3), Q(4)]
Ft = [Q(5), Q(-2)]
k = [Q(2), Q(3)]
integral_g = [Q(1, 7), Q(-2, 9)]
HF = [Q(2, 11), Q(-3, 13)]
deltaU = [d + (v - v0) / kk + gg + hh for d, v, v0, kk, gg, hh
          in zip(delta0, Ft, F0, k, integral_g, HF)]
lhs = [v / kk + hh + gg for v, kk, hh, gg in zip(Ft, k, HF, integral_g)]
rhs = [u - d + v0 / kk for u, d, v0, kk in zip(deltaU, delta0, F0, k)]
assert lhs == rhs
assert lhs != [u - d - v0 / kk for u, d, v0, kk in zip(deltaU, delta0, F0, k)]

result = {'all_passed': True, 'arithmetic': 'fractions.Fraction',
          'linear_special_case_only': True, 'cases': cases,
          'nonzero_initial_affine_signs': True,
          'not_proved_by_samples': ['nonlinear equivalence', 'rational function identity',
                                    'existence/uniqueness', 'algorithm convergence',
                                    'engineering model certification']}
Path(__file__).with_name('checks.json').write_bytes(
    (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
print(json.dumps(result, ensure_ascii=False))
