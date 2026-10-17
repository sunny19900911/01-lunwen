"""Tiny exact matrix substitutions; no time-stepping solver or trajectory."""
from fractions import Fraction as Q
from pathlib import Path
import json


def add(a, b):
    return [[x+y for x, y in zip(r, s)] for r, s in zip(a, b)]


def scale(a, k):
    return [[k*x for x in r] for r in a]


def sub(a, b):
    return add(a, scale(b, -1))


def mul(a, b):
    return [[sum(x*y for x, y in zip(r, c)) for c in zip(*b)] for r in a]


def tr(a):
    return [list(r) for r in zip(*a)]


def inv2(a):
    x, y = a[0]
    z, w = a[1]
    d = x*w-y*z
    assert d != 0
    return [[w/d, -y/d], [-z/d, x/d]]


def dot(a, b):
    return sum(x[0]*y[0] for x, y in zip(a, b))


def quad(a, x):
    return dot(x, mul(a, x))


M = [[Q(2), Q(0)], [Q(0), Q(3)]]
K = [[Q(3), Q(-1)], [Q(-1), Q(2)]]
C = [[Q(1, 5), Q(0)], [Q(0), Q(2, 5)]]
J = [[Q(1, 2), Q(0)], [Q(0), Q(1, 3)]]  # K_s inverse.
h = Q(1, 7)
u0, v0, F0 = [[Q(1)], [Q(-2)]], [[Q(2)], [Q(1)]], [[Q(3)], [Q(-1)]]
vp, Fp = [[Q(-1)], [Q(3)]], [[Q(2)], [Q(-3)]]
gp = [[Q(1)], [Q(-1)]]  # g(Fp), realizable by alpha=1,c=(2,3).
f = [[Q(5)], [Q(-4)]]
up = add(u0, scale(vp, h))
du, dv, dF = sub(up, u0), sub(vp, v0), sub(Fp, F0)
A = add(add(M, scale(C, h)), scale(K, h*h))
assert A[0][0] > 0 and A[0][0]*A[1][1]-A[0][1]*A[1][0] > 0
Ai = inv2(A)
results = []
for B in ([[Q(1), Q(0)], [Q(-1), Q(1)]],
          [[Q(1), Q(0)], [Q(1), Q(0)]]):
    Bt = tr(B)
    # Manufacture one exact compatible algebraic state, not a time solve.
    fc = add(add(add(scale(mul(M, dv), 1/h), mul(C, vp)), mul(K, up)), mul(Bt, Fp))
    Fprevious = sub(Fp, scale(mul(inv2(J), sub(mul(B, vp), gp)), h))
    z = mul(Ai, add(mul(M, v0), scale(sub(fc, mul(K, u0)), h)))
    S = mul(mul(B, Ai), Bt)
    Qh = add(J, scale(S, h*h))
    rhs = add(mul(J, Fprevious), scale(mul(B, z), h))
    assert vp == sub(z, scale(mul(mul(Ai, Bt), Fp), h))
    assert add(mul(Qh, Fp), scale(gp, h)) == rhs
    assert S[0][1] != 0
    detS = S[0][0]*S[1][1]-S[0][1]*S[1][0]
    assert Qh[0][0] > 0 and Qh[0][0]*Qh[1][1]-Qh[0][1]*Qh[1][0] > 0
    def energy(u, v, ff):
        return (quad(K, u)+quad(M, v)+quad(J, ff))/2
    dfc = sub(Fp, Fprevious)
    physical = h*(quad(C, vp)+dot(Fp, gp))
    numeric = (quad(K, du)+quad(M, dv)+quad(J, dfc))/2
    assert energy(up, vp, Fp)-energy(u0, v0, Fprevious)+physical+numeric == h*dot(vp, fc)
    # Arbitrary stored states: all three signed residual-work terms.
    ru = sub(scale(du, 1/h), vp)
    rv = sub(add(add(add(scale(mul(M, dv), 1/h), mul(C, vp)), mul(K, up)), mul(Bt, Fp)), f)
    rf = add(sub(scale(mul(J, dF), 1/h), mul(B, vp)), gp)
    numeric_r = (quad(K, du)+quad(M, dv)+quad(J, dF))/2
    residual_work = h*(dot(up, mul(K, ru))+dot(vp, rv)+dot(Fp, rf))
    balance = energy(up, vp, Fp)-energy(u0, v0, F0)+physical+numeric_r-h*dot(vp, f)
    assert balance == residual_work
    results.append({'S_singular': detS == 0, 'Q_positive_definite': True,
                    'full_cross_port_elimination': True, 'exact_energy_identity': True,
                    'residual_work_signs': True})

# Ensure the kinematic residual term is exercised separately.
ru = [[Q(1, 11)], [Q(-2, 13)]]
dup = add(du, scale(ru, h))
upp = add(u0, dup)
B = [[Q(1), Q(0)], [Q(-1), Q(1)]]
rv = sub(add(add(add(scale(mul(M, dv), 1/h), mul(C, vp)), mul(K, upp)), mul(tr(B), Fp)), f)
rf = add(sub(scale(mul(J, dF), 1/h), mul(B, vp)), gp)
lhs = energy(upp, vp, Fp)-energy(u0, v0, F0)+physical+(quad(K, dup)+quad(M, dv)+quad(J, dF))/2-h*dot(vp, f)
rhs = h*(dot(upp, mul(K, ru))+dot(vp, rv)+dot(Fp, rf))
assert lhs == rhs and dot(upp, mul(K, ru)) != 0

result = {'all_passed': True, 'arithmetic': 'fractions.Fraction',
          'cases': results, 'nonzero_kinematic_residual_work_checked': True,
          'scope': 'Manufactured algebraic substitutions only; existence proof is in report; no trajectory, root iteration, continuous convergence or engineering accuracy tested.'}
Path(__file__).with_name('checks.json').write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result))
