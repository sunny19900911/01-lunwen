"""Exact rational five-mode double-zero construction; Python standard library only."""
from fractions import Fraction as F
from functools import reduce
from math import gcd, lcm, factorial, sqrt, pi
from pathlib import Path
import hashlib
import json
import platform
from datetime import datetime, timezone, timedelta

OUT = Path(__file__).resolve().parent


def add(z, q):
    return z[0] + q[0], z[1] + q[1]


def mul(z, q):
    return z[0] * q[0] - z[1] * q[1], z[0] * q[1] + z[1] * q[0]


def scale(c, z):
    return c * z[0], c * z[1]


def inv(z):
    d = z[0] ** 2 + z[1] ** 2
    return z[0] / d, -z[1] / d


def summed(zs):
    return reduce(add, zs, (F(0), F(0)))


def kernels(w, om, zeta):
    d = (w * w - om * om, 2 * zeta * w * om)
    dp = (-2 * om, 2 * zeta * w)
    g = inv(d)
    g2 = mul(g, g)
    gp = scale(-1, mul(dp, g2))
    gpp = add(scale(2, g2), scale(2, mul(mul(dp, dp), mul(g2, g))))
    return g, gp, gpp


def null_vector(matrix):
    a = [row[:] for row in matrix]
    nr, nc = len(a), len(a[0])
    pivots = []
    row = 0
    for col in range(nc):
        pick = next((j for j in range(row, nr) if a[j][col]), None)
        if pick is None:
            continue
        a[row], a[pick] = a[pick], a[row]
        div = a[row][col]
        a[row] = [v / div for v in a[row]]
        for j in range(nr):
            if j != row and a[j][col]:
                c = a[j][col]
                a[j] = [v - c * q for v, q in zip(a[j], a[row])]
        pivots.append(col)
        row += 1
        if row == nr:
            break
    free = next(j for j in range(nc) if j not in pivots)
    x = [F(0)] * nc
    x[free] = F(1)
    for j, p in reversed(list(enumerate(pivots))):
        x[p] = -sum(a[j][k] * x[k] for k in range(p + 1, nc))
    common = lcm(*(q.denominator for q in x))
    ints = [int(q * common) for q in x]
    divisor = reduce(gcd, (abs(q) for q in ints))
    return [q // divisor for q in ints], len(pivots)


def pmul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for j, x in enumerate(a):
        for k, y in enumerate(b):
            out[j + k] += x * y
    return out


def numerator(ws, residues, zeta):
    out = [F(0)] * (2 * len(ws) - 1)
    for i, r in enumerate(residues):
        p = [F(r)]
        for j, w in enumerate(ws):
            if i != j:
                p = pmul(p, [w * w, 2 * zeta * w, F(1)])
        out = [v + p[k] for k, v in enumerate(out)]
    return out


def pdivide(a, b):
    rem = a[:]
    q = [F(0)] * (len(a) - len(b) + 1)
    for k in range(len(q) - 1, -1, -1):
        q[k] = rem[k + len(b) - 1] / b[-1]
        for j, v in enumerate(b):
            rem[k + j] -= q[k] * v
    return q, rem[:len(b) - 1]


def jscomplex(z):
    return {"real_exact": str(z[0]), "imag_exact": str(z[1]),
            "real": float(z[0]), "imag": float(z[1])}


def moment_bound(ws, rs, zeta, p):
    return sum(abs(r) * factorial(p) /
               (w * sqrt(1 - zeta * zeta) * (zeta * w) ** (p + 1))
               for w, r in zip(ws, rs))


def main():
    ws = list(map(F, [1, 2, 3, 4, 5]))
    om, z0, z1 = F(2), F(1, 20), F(2, 25)
    ks0 = [kernels(w, om, z0) for w in ws]
    matrix = [[k[order][part] for k in ks0]
              for order in [0, 1] for part in [0, 1]]
    raw, rank = null_vector(matrix)
    residues = [F(r, max(map(abs, raw))) for r in raw]
    h0 = summed(scale(r, k[0]) for r, k in zip(residues, ks0))
    hp0 = summed(scale(r, k[1]) for r, k in zip(residues, ks0))
    hpp0 = summed(scale(r, k[2]) for r, k in zip(residues, ks0))
    h1 = summed(scale(r, kernels(w, om, z1)[0]) for r, w in zip(residues, ws))
    quotient, remainder = pdivide(numerator(ws, raw, z0), [F(16), F(0), F(8), F(0), F(1)])
    a0, a1, a2, a3, a4 = quotient
    hurwitz2 = a3*a2-a4*a1
    hurwitz3 = a3*a2*a1-a4*a1*a1-a3*a3*a0
    checks = {"rank_is_four": rank == 4, "H0_is_exactly_zero": h0 == (0, 0),
              "H0_prime_is_exactly_zero": hp0 == (0, 0),
              "H0_second_derivative_is_nonzero": hpp0 != (0, 0),
              "H1_is_nonzero": h1 != (0, 0),
              "numerator_divisible_by_s2_plus_4_squared": all(v == 0 for v in remainder)}
    m02 = moment_bound(list(map(float, ws)), list(map(float, residues)), float(z0), 2)
    m11 = moment_bound(list(map(float, ws)), list(map(float, residues)), float(z1), 1)
    # a(x)=sin^4(pi*x/2), x in [0,2], zero outside; ||a'||<=2pi,
    # ||a''||<=4pi^2. These simple constants are deliberately conservative.
    h1abs = abs(complex(float(h1[0]), float(h1[1])))
    lower_bounds = []
    for T in [10000, 100000, 1000000]:
        p0_upper = 2 * pi * pi * m02 / T ** 2
        p1_lower = h1abs - 2 * pi * m11 / T
        lower_bounds.append({"T": T, "active_duration": 2*T,
                             "P0_upper": p0_upper, "P1_lower": p1_lower,
                             "ratio_lower_if_positive": max(0, p1_lower) / p0_upper})
    output = {"run_time_Asia_Shanghai": datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "python_version": platform.python_version(),
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "parameters": {"omega": [str(w) for w in ws], "Omega": str(om),
                             "zeta0": str(z0), "zeta1": str(z1)},
              "raw_integer_residues": raw,
              "max_abs_normalized_residues": [str(r) for r in residues],
              "checks": checks, "H0": jscomplex(h0), "H0_prime": jscomplex(hp0),
              "H0_second_derivative": jscomplex(hpp0), "H1": jscomplex(h1),
              "H1_abs": h1abs,
              "baseline_numerator_quotient_after_dividing_by_s2_plus_4_squared": [str(v) for v in quotient],
              "remaining_quartic_checks": {"all_coefficients_positive": all(v>0 for v in quotient),
                                            "hurwitz2_positive": hurwitz2>0,
                                            "hurwitz3_positive": hurwitz3>0,
                                            "hurwitz3_exact": str(hurwitz3),
                                            "interpretation": "The remaining quartic is not Hurwitz; do not claim a matching O(T^2) causal-window upper bound from this witness."},
              "moment_upper_bounds": {"m0_order2": m02, "m1_order1": m11},
              "conservative_peak_ratio_lower_bounds": lower_bounds,
              "limitations": ["Exact algebra supports this witness only; no minimum-mode claim.",
                              "No finite-pulse time integration was run.",
                              "Peak estimates depend on the analytic envelope argument; independent review pending."]}
    (OUT / "double-zero-result.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    assert all(checks.values())


if __name__ == "__main__":
    main()
