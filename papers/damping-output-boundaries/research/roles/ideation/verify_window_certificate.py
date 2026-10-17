"""Finite-window comparison kernel for the historical two-story shear example."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from math import sqrt, prod, exp
import hashlib
import json
import platform

OUT = Path(__file__).resolve().parent


def main():
    z0, z1 = .05, .08
    ws = [sqrt((3-sqrt(5))/2), sqrt((3+sqrt(5))/2)]
    # H_z(s)=-(s^2+6*z/sqrt(5)*s+2)/D_z(s), verified historically.
    numerator = lambda s, z: s*s + 6*z/sqrt(5)*s + 2
    denominator = lambda s, z: prod(s*s + 2*z*w*s + w*w for w in ws)
    poles = [-3*z0/sqrt(5)+sign*1j*sqrt(2-9*z0*z0/5) for sign in [-1,1]]
    poles += [-z1*w+sign*1j*w*sqrt(1-z1*z1) for w in ws for sign in [-1,1]]
    residues = [numerator(p,z1)*denominator(p,z0)/prod(p-q for j,q in enumerate(poles) if j != i)
                for i,p in enumerate(poles)]
    errors = []
    for s in [1+2j, 2+3j, 3+0j]:
        q = numerator(s,z1)*denominator(s,z0)/(numerator(s,z0)*denominator(s,z1))
        errors.append(abs(q - 1 - sum(c/(s-p) for c,p in zip(residues,poles))))
    bounds = [{"T": T, "B_modal_triangle_upper": 1+sum(abs(c)*(1-exp(p.real*T))/(-p.real)
               for c,p in zip(residues,poles))} for T in [5,20,60]]
    summary = {"run_time_Asia_Shanghai": datetime.now(timezone(timedelta(hours=8))).isoformat(),
               "python_version": platform.python_version(),
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "input": "Historical equal-unit-mass/equal-unit-story-stiffness two-story model; bottom elastic shear output",
               "zeta": [z0,z1], "omega": ws, "quotient_direct_term": 1,
               "quotient_poles": [{"re": p.real, "im": p.imag} for p in poles],
               "quotient_residues": [{"re": c.real, "im": c.imag} for c in residues],
               "partial_fraction_check_max_abs_error": max(errors),
               "all_poles_strictly_left_half_plane": all(p.real<0 for p in poles),
               "finite_window_upper_bounds": bounds,
               "B_infinity_modal_triangle_upper": 1+sum(abs(c)/(-p.real) for c,p in zip(residues,poles)),
               "scope": "Any same locally bounded input with zero prehistory; theoretical continuous-time window peaks",
               "limitations": ["Bounds use floating-point roots/residues; no interval arithmetic certification.",
                               "This is not a tight extremal peak ratio or an engineering-record prediction.",
                               "No time-domain input search was run."]}
    (OUT / "window-certificate-result.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    assert max(errors) < 1e-12
    assert all(p.real<0 for p in poles)


if __name__ == "__main__":
    main()
