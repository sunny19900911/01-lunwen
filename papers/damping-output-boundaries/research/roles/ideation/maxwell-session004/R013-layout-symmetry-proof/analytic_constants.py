"""Frozen R013 scalar checks; no ODE integration or sampled peak search."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
protocol = HERE / "protocol-copy.json"
assert hashlib.sha256(protocol.read_bytes()).hexdigest() == "5fbd02e556ec24a7b4431cef5a09e749596b47466b8a32a2990f47a76c2ce41e"
eps = Q(1, 1000)
q = Q(21, 10) * eps
delta = 13 * q * 22 / (1 - 22 * q)
assert delta == Q(3003, 4769) < Q(16, 25)
assert 1 + delta < Q(17, 10)
assert Q(19, 2) - delta > Q(44, 5)
exp_lower = sum((Q(31, 10) ** n / math.factorial(n) for n in range(9)), Q(0))
assert exp_lower > 22
assert 1 + Q(157, 1000) + Q(157, 1000)**2 / 2 > Q(7, 6)
assert 3 * Q(17, 10)**2 - 1 - Q(1, 10) * Q(173, 100)**3 > 7
lo, hi = 1.7, 1.73
for _ in range(60):
    mid = (lo + hi) / 2
    if mid**3 - 3 * mid + 0.1 < 0:
        lo = mid
    else:
        hi = mid
r = (lo + hi) / 2
lam = r**3
kappa = 3 * r**2 - 1 - 0.1 * lam
omega = math.sqrt(399/400)
w = math.sqrt(1 + 2 * float(eps))
z = math.exp(-math.pi / (20 * omega))
l1u = (1 + z) / (1 - z)
baseline_lower = 10 - math.exp(-math.pi) * math.sqrt(100 + (0.5 / omega)**2)
u_T = -10 + math.exp(-math.pi) * (10 * math.cos(20 * math.pi * omega) + 0.5 / omega * math.sin(20 * math.pi * omega))
assert l1u < 13 and 20 + 0.05 * l1u < 22 and baseline_lower > 9.5 and u_T < -9.5
result = {
    "scope": "Analytic constants only; floating values illustrative; exact rational gates asserted separately. No ODE, time arrays or sampled extrema.",
    "protocol_sha256": hashlib.sha256(protocol.read_bytes()).hexdigest(),
    "exact_gates": {"q": str(q), "22q": str(22*q), "position_error_upper": str(delta), "position_error_lt_0.64": True, "A_bound_lt_1.7": True, "B_lower_gt_8.8": True, "exp_3.1_partial_sum_gt_22": True, "exp_0.157_partial_sum_gt_7_over_6": True, "kappa_lower_gt_7": True},
    "illustrative_scalar_values": {"r": r, "lambda": lam, "kappa": kappa, "c": kappa/lam, "w": w, "deltaC_inf": 0.1*(w-1), "hU_L1": l1u, "hU_velocity_L1_upper": 20+0.05*l1u, "hD_velocity_L1_upper_r": r, "state_bound": float(22/(1-22*q)), "position_error_upper": float(delta), "baseline_abs_T_lower": baseline_lower, "baseline_signed_T": u_T}
}
(HERE / "analytic-checks.json").write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
print(json.dumps(result, ensure_ascii=False, indent=2))
