"""One fixed physical 3-DOF model; no scan or time history.

Decimal values are consistency checks, not interval certificates.
The exact zero is defined by the algebraic coefficients in round-011.md.
"""
from decimal import Decimal as D, getcontext
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import time

getcontext().prec = 80
started = time.perf_counter()


def matvec(a, b):
    return [sum(x * y for x, y in zip(row, b)) for row in a]


K = [[F(2), F(-1), F(0)], [F(-1), F(2), F(-1)], [F(0), F(-1), F(1)]]
b = [F(1)] * 3
ell = [F(0), F(-1), F(1)]
v = b
moments = []
for _ in range(3):
    moments.append(sum(x * y for x, y in zip(ell, v)))
    v = matvec(K, v)
assert moments == [0, 0, 1]


def root(seed):
    x = D(seed)
    for _ in range(30):
        x -= (x**3 - 5 * x**2 + 6 * x - 1) / (3 * x**2 - 10 * x + 6)
    return x


lam = [root(x) for x in ('.2', '1.55', '3.25')]
assert 0 < lam[0] < lam[1] < lam[2]
omega = [x.sqrt() for x in lam]
rho = []
for i in range(3):
    den = D(1)
    for j in range(3):
        if i != j:
            den *= lam[i] - lam[j]
    rho.append(1 / den)
S = sum(omega)
W = omega[0] * omega[1] * omega[2]
pair_product = (omega[0] + omega[1]) * (omega[0] + omega[2]) * (omega[1] + omega[2])
A3 = -2 * sum(w * r for w, r in zip(omega, rho))
A2 = 4 * W * sum(r / w for w, r in zip(omega, rho))
A1 = S * A2 / 2
A0 = D(1)
assert min(A3, A2, A1) > 0
assert abs(A3 - 2 / pair_product) < D('1e-75')
assert abs(A2 - 4 * S / pair_product) < D('1e-75')
Omega = (A1 / A3).sqrt()
zeta = (A0 * A3 / (A2 * A1)).sqrt()
kappa = D(8) / 5


def mul(z, w):
    return (z[0] * w[0] - z[1] * w[1], z[0] * w[1] + z[1] * w[0])


def transfer(z):
    numerator = (1 - A2 * z**2 * Omega**2, z * Omega * (A1 - A3 * Omega**2))
    den = (D(1), D(0))
    for l, w in zip(lam, omega):
        den = mul(den, (l - Omega**2, 2 * z * w * Omega))
    den2 = den[0]**2 + den[1]**2
    h = ((numerator[0] * den[0] + numerator[1] * den[1]) / den2,
         (numerator[1] * den[0] - numerator[0] * den[1]) / den2)
    return {"numerator_re_im": [str(x) for x in numerator],
            "denominator_abs": str(den2.sqrt()),
            "H_re_im": [str(x) for x in h],
            "H_abs": str((h[0]**2 + h[1]**2).sqrt())}


baseline, increased = transfer(zeta), transfer(kappa * zeta)
assert abs(D(baseline['numerator_re_im'][0])) < D('1e-75')
assert abs(D(baseline['numerator_re_im'][1])) < D('1e-75')
assert abs(D(increased['numerator_re_im'][0]) + D(39) / 25) < D('1e-75')
assert D(increased['H_abs']) > 0
assert abs(Omega - S) < D('1e-75')

result = {
    "model": {"M": "I_3", "K": [[int(x) for x in row] for row in K],
              "b": [1, 1, 1], "ell": [0, -1, 1], "input": "f=-ground_acceleration",
              "damping": "C_zeta=2*zeta*sqrt(K), full classical modal damping"},
    "exact_moments_0_1_2": [str(x) for x in moments],
    "precision_digits": 80,
    "lambda": [str(x) for x in lam], "omega": [str(x) for x in omega],
    "rho_from_exact_resolvent_partial_fractions": [str(x) for x in rho],
    "A3_A2_A1_A0": [str(x) for x in (A3, A2, A1, A0)],
    "S": str(S), "pair_product": str(pair_product),
    "Omega_star": str(Omega), "zeta_star": str(zeta),
    "zeta_increased": str(kappa * zeta), "kappa": "8/5",
    "baseline": baseline, "increased": increased,
    "limits": "80-digit non-directed Decimal arithmetic; exact proof is separate; no scan or time history",
    "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "elapsed_seconds": time.perf_counter() - started,
}
out = Path(__file__).with_name('unit-topcut-zero-audit.json')
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({"status": "passed", "output": str(out), "zeta_star": str(zeta),
                  "Omega_star": str(Omega), "H1_abs": increased['H_abs']}, ensure_ascii=False))
