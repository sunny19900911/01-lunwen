"""Independent analytic peak-envelope audit for the frozen synthetic witness."""
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
INPUT = HERE.parents[2]/"experiments/round004/complete_peak_witness.json"


def main():
    source_bytes = INPUT.read_bytes()
    inp = json.loads(source_bytes.decode("utf-8"))
    row = inp["runs"][-1]
    zeta, residue_abs_sum, residue_sum_abs = F(1,20),F(99,10),F(79,10)
    sqrt_lower = F(499,500)
    assert sqrt_lower**2 < 1-zeta*zeta
    # y''=sum r_i Im(p_i^2 x_i)/beta_i + sum r_i f,
    # and |x_i|<=1/(zeta*omega_i), |p_i|=omega_i.
    curvature_rational_upper = residue_abs_sum/(zeta*sqrt_lower)+residue_sum_abs
    assert curvature_rational_upper < 207
    h = F(1,1024)
    p0_sample = F(str(row["complete_P0"]))
    p1_sample = F(str(row["complete_P1"]))
    p0_upper = p0_sample+F(207)*h*h/8
    ratio_lower = p1_sample/p0_upper
    # These reproduce a conservative envelope conditional on the numerical
    # sample values; no unproved outward rounding of the samples is asserted.
    assert ratio_lower > F(8,5)
    beta = [w*math.sqrt(1-0.05**2) for w in (1,3)]
    tail = 600*sum(abs(r)/b*math.exp(-0.05*w*900) for w,r,b in zip((1,3),(1,-8.9),beta))
    out = {
        "run_time_utc":datetime.now(timezone.utc).isoformat(),
        "source_sha256":hashlib.sha256(source_bytes).hexdigest(),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "curvature_rational_upper":str(curvature_rational_upper),
        "curvature_rational_upper_approx":float(curvature_rational_upper),
        "safe_curvature_integer":207,
        "sample_dt_exact":str(h),
        "continuous_baseline_upper_conditional_on_sample":float(p0_upper),
        "continuous_ratio_lower_conditional_on_samples":float(ratio_lower),
        "tail_after_Tplus900":tail,
        "scope":"Analytic M2 upper is exact rational after a proven square-root lower bound. Peak envelope uses previously computed floating samples, so the full result remains independently reviewed numerical evidence, not directed-interval certification. No FFT or witness regeneration."
    }
    (HERE/"EEXP004-bound-audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
