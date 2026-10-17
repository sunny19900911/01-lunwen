"""Independent analytic forced-response audit; synthetic LTI model, not ETABS.

Uses three exact harmonic solutions within the sin^2 window, followed by
the exact homogeneous response. No original integration script is imported.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SOURCE = REPO.parent / "W5-重燃双塔连体/04-正文/均匀增阻尼的输出放大判据与模态抵消边界-理论稿-20261016.md"
OMEGA = 2.0
W = np.array([1.0, 2.0, 3.0])
RAW_R = np.array([565.0, -14.0, 951.0])
R = RAW_R / np.linalg.norm(RAW_R)


def transfer(zeta):
    return np.sum(R / (W * W - OMEGA**2 + 2j * zeta * W * OMEGA))


def exact_base_zero():
    real, imag = F(0), F(0)
    for w, r in zip((1, 2, 3), (565, -14, 951)):
        d, e = F(w*w - 4), F(w, 5)  # 2*(1/20)*w*2
        real += r * d / (d*d + e*e)
        imag -= r * e / (d*d + e*e)
    return {"real": str(real), "imag": str(imag)}


def harmonic_state(t, w, zeta, nu):
    alpha = zeta*w
    beta = w*math.sqrt(1-zeta*zeta)
    e = np.exp(1j*nu*t)
    decay = np.exp(-alpha*t)
    co, si = np.cos(beta*t), np.sin(beta*t)
    den = w*w - nu*nu + 2j*alpha*nu
    q = (e - decay*(co + (alpha + 1j*nu)*si/beta))/den
    v = (1j*nu*e - decay*(1j*nu*co - (w*w + 1j*alpha*nu)*si/beta))/den
    return q, v


def window_state(t, w, zeta, half_duration, phase):
    q = np.zeros(np.shape(t), dtype=complex)
    v = np.zeros(np.shape(t), dtype=complex)
    for coefficient, nu in ((0.5, OMEGA), (-0.25, OMEGA + math.pi/half_duration), (-0.25, OMEGA - math.pi/half_duration)):
        qn, vn = harmonic_state(t, w, zeta, nu)
        q += coefficient*qn
        v += coefficient*vn
    phase_factor = np.exp(1j*phase)
    return (q*phase_factor).real, (v*phase_factor).real


def signal(zeta, half_duration, dt, tail=400.0):
    duration = 2*half_duration
    phase = -OMEGA*half_duration - np.angle(transfer(0.08))
    t = np.arange(round((duration+tail)/dt)+1)*dt
    active = t <= duration
    y = np.zeros_like(t)
    tail_limit_at_end = 0.0
    for w, r in zip(W, R):
        q, _ = window_state(t[active], w, zeta, half_duration, phase)
        y[active] += r*q
        ql, vl = window_state(np.array([duration]), w, zeta, half_duration, phase)
        ql, vl = float(ql[0]), float(vl[0])
        alpha, beta = zeta*w, w*math.sqrt(1-zeta*zeta)
        s = t[~active]-duration
        amp = (vl+alpha*ql)/beta
        y[~active] += r*np.exp(-alpha*s)*(ql*np.cos(beta*s)+amp*np.sin(beta*s))
        tail_limit_at_end += abs(r)*math.hypot(ql, amp)*math.exp(-alpha*tail)
    idx = int(np.argmax(np.abs(y)))
    return {"peak_sampled": float(abs(y[idx])), "peak_time_sampled": float(t[idx]), "unobserved_tail_upper": tail_limit_at_end}


def moment_upper(zeta):
    # |sum h_i| <= sum |h_i|, |sin| <= 1: simple rigorous upper bound.
    return float(np.sum(np.abs(R)/(W*np.sqrt(1-zeta*zeta)*(zeta*W)**2)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="finite-envelope-audit.json")
    args = parser.parse_args()
    rows = []
    for half_duration in (60.0, 120.0, 240.0, 480.0, 960.0, 1920.0):
        states = [signal(z, half_duration, 0.02) for z in (0.05, 0.08)]
        rows.append({"T": half_duration, "support_duration": 2*half_duration, "dt": 0.02, "states": states, "ratio_sampled": states[1]["peak_sampled"]/states[0]["peak_sampled"]})
    refine = [signal(z, 240.0, 0.01) for z in (0.05, 0.08)]
    coarse = rows[2]["states"]
    fixed_input_horizons = []
    for tail in (100.0, 200.0, 400.0):
        states = [signal(z, 240.0, 0.02, tail=tail) for z in (0.05, 0.08)]
        fixed_input_horizons.append({"T_fixed": 240.0, "support_duration_fixed": 480.0, "tail_seconds": tail, "states": states, "ratio_sampled": states[1]["peak_sampled"]/states[0]["peak_sampled"]})
    h1 = float(abs(transfer(0.08)))
    m0, m1 = moment_upper(0.05), moment_upper(0.08)
    payload = {
        "kind": "synthetic-analytic-response-audit",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version,
        "numpy": np.__version__,
        "parameters": {"omega": W.tolist(), "residues_raw": RAW_R.tolist(), "residue_normalization": "Euclidean norm", "zeta": [0.05, 0.08], "input": "sin(pi*t/(2*T))**2 * cos(2*t+phase), 0<=t<=2*T", "phase": "-2*T-arg(H1(2))", "tail_seconds": 400},
        "base_zero_exact_rational": exact_base_zero(),
        "H1_abs": h1,
        "moment_upper": [m0, m1],
        "rows": rows,
        "fixed_input_observation_extension": fixed_input_horizons,
        "refinement_T240_dt001": refine,
        "peak_relative_changes_under_refinement": [abs(refine[k]["peak_sampled"]-coarse[k]["peak_sampled"])/refine[k]["peak_sampled"] for k in (0, 1)],
        "analytic_ratio_lower_T100000": (2*100000*h1/math.pi-m1)/m0,
        "limitations": ["sampled peaks are not certified continuous-time maxima", "infinite-ratio statement comes from analytic convolution inequality, not finite scan", "fixed system/output, varying input duration and phase", "not a native ETABS model or engineering causal identification"],
    }
    assert payload["base_zero_exact_rational"] == {"real": "0", "imag": "0"}
    assert all(row["states"][k]["unobserved_tail_upper"] < row["states"][k]["peak_sampled"] for row in rows for k in (0, 1))
    (HERE/args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"rows": [{"support_duration": row["support_duration"], "ratio": row["ratio_sampled"]} for row in rows], "exact_zero": payload["base_zero_exact_rational"], "refinement": payload["peak_relative_changes_under_refinement"], "analytic_lower_T100000": payload["analytic_ratio_lower_T100000"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
