"""Exact isolated algebra; no time integration, nonlinear solve or trajectory."""
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


def inv(a):
    x, y = a[0]
    z, w = a[1]
    d = x*w-y*z
    assert d != 0
    return [[w/d, -y/d], [-z/d, x/d]]


def dot(a, b):
    return sum(x[0]*y[0] for x, y in zip(a, b))


def quad(a, x):
    return dot(x, mul(a, x))


def mid(a, b):
    return scale(add(a, b), Q(1, 2))


M = [[Q(2), Q(1, 2)], [Q(1, 2), Q(3)]]
K = [[Q(3), Q(-1)], [Q(-1), Q(2)]]
C = [[Q(1, 5), Q(-1, 5)], [Q(-1, 5), Q(1, 5)]]
J = [[Q(1, 2), Q(0)], [Q(0), Q(1, 3)]]
h, a = Q(2, 7), Q(1, 7)
un, vn = [[Q(1)], [Q(-2)]], [[Q(2)], [Q(1)]]
vm, fm_force = [[Q(-1)], [Q(3)]], [[Q(2)], [Q(-3)]]
g = [[Q(1)], [Q(-1)]]  # alpha=1, c=(2,3), evaluated at fm_force.
up, vp = add(un, scale(vm, h)), sub(scale(vm, 2), vn)
um = mid(un, up)
du, dv = sub(up, un), sub(vp, vn)
A = add(add(M, scale(C, a)), scale(K, a*a))
Ai = inv(A)
cases = []


def E(u, v, F):
    return (quad(K, u)+quad(M, v)+quad(J, F))/2


for B in ([[Q(1), Q(0)], [Q(-1), Q(1)]],
          [[Q(1), Q(0)], [Q(1), Q(0)]]):
    Bt = tr(B)
    # Prescribe an isolated compatible algebraic state; do not solve in time.
    Fn = sub(fm_force, scale(mul(inv(J), sub(mul(B, vm), g)), a))
    Fp = sub(scale(fm_force, 2), Fn)
    f = add(add(add(scale(mul(M, dv), 1/h), mul(C, vm)), mul(K, um)), mul(Bt, fm_force))
    z = mul(Ai, add(mul(M, vn), scale(sub(f, mul(K, un)), a)))
    S = mul(mul(B, Ai), Bt)
    Qh = add(J, scale(S, a*a))
    assert S[0][1] != 0
    assert vm == sub(z, scale(mul(mul(Ai, Bt), fm_force), a))
    assert add(mul(Qh, fm_force), scale(g, a)) == add(mul(J, Fn), scale(mul(B, z), a))
    assert Qh[0][0] > 0 and Qh[0][0]*Qh[1][1]-Qh[0][1]*Qh[1][0] > 0
    physical = h*(quad(C, vm)+dot(fm_force, g))
    assert E(up, vp, Fp)-E(un, vn, Fn)+physical == h*dot(vm, f)
    cases.append({'S_singular': S[0][0]*S[1][1]-S[0][1]*S[1][0] == 0,
                  'Q_SPD': True, 'mass_and_cross_port_elimination': True,
                  'nonzero_initial_energy_midpoint_balance': True})

# Perturb all stored endpoints; evaluate actual midpoint and all residuals.
Fn = [[Q(3)], [Q(-1)]]
Fp = [[Q(1)], [Q(-5)]]  # midpoint (2,-3), retains the stated g.
up = add(up, [[Q(1, 11)], [Q(-2, 13)]])
vp = add(vp, [[Q(1, 17)], [Q(2, 19)]])
um, vm, Fm = mid(un, up), mid(vn, vp), mid(Fn, Fp)
du, dv, dF = sub(up, un), sub(vp, vn), sub(Fp, Fn)
f = [[Q(5)], [Q(-4)]]
B = [[Q(1), Q(0)], [Q(-1), Q(1)]]
Ru = sub(du, scale(vm, h))
Rv = sub(mul(M, dv), scale(sub(sub(sub(f, mul(C, vm)), mul(K, um)), mul(tr(B), Fm)), h))
RF = sub(mul(J, dF), scale(sub(mul(B, vm), g), h))
terms = [dot(um, mul(K, Ru)), dot(vm, Rv), dot(Fm, RF)]
assert all(x != 0 for x in terms)
balance = E(up, vp, Fp)-E(un, vn, Fn)+h*(quad(C, vm)+dot(Fm, g)-dot(vm, f))
assert balance == sum(terms)

# Internal work-midpoint mismatch adds the stated pairing correction.
ut = add(um, [[Q(1, 23)], [Q(-1, 29)]])
vt = add(vm, [[Q(-1, 31)], [Q(1, 37)]])
Ft = Fm  # keep nonlinear force evaluation exactly unchanged here.
Rut = sub(du, scale(vt, h))
Rvt = sub(mul(M, dv), scale(sub(sub(sub(f, mul(C, vt)), mul(K, ut)), mul(tr(B), Ft)), h))
RFt = sub(mul(J, dF), scale(sub(mul(B, vt), g), h))
correction = dot(sub(um, ut), mul(K, du))+dot(sub(vm, vt), mul(M, dv))+dot(sub(Fm, Ft), mul(J, dF))
lhs = E(up, vp, Fp)-E(un, vn, Fn)+h*(quad(C, vt)+dot(Ft, g)-dot(vt, f))
assert lhs == dot(ut, mul(K, Rut))+dot(vt, Rvt)+dot(Ft, RFt)+correction
assert correction != 0
assert Q(2)**2 != (Q(1)**2+Q(3)**2)/2  # alpha=1/2,c=1: g(mean)!=mean(g).

result = {'all_passed': True, 'arithmetic': 'fractions.Fraction', 'cases': cases,
          'all_three_nonzero_increment_residual_work_signs': True,
          'internal_midpoint_mismatch_correction': True,
          'nonlinear_g_of_midpoint_not_average_of_g': True,
          'scope': 'Isolated exact substitutions only; no temporal loop, integration, nonlinear solve, arrays, accuracy result or convergence claim.'}
Path(__file__).with_name('checks.json').write_bytes((json.dumps(result, indent=2)+'\n').encode('utf-8'))
print(json.dumps(result))
