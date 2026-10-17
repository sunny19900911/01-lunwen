"""Closed-form boundary checks for the refined scalar kernel L1 inequality."""
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent


def alpha_times_tv(z):
    # z=alpha/sqrt(beta); time scaling removes beta.
    if z == 1:
        return 2/math.e
    if z < 1:
        gamma = math.sqrt(1-z*z)
        peak_time = math.atan2(gamma,z)/gamma
        return 2*z*math.exp(-z*peak_time)/(-math.expm1(-math.pi*z/gamma))
    q = z+math.sqrt(z*z-1)
    p = 1/q
    peak_time = math.log(q/p)/(q-p)
    return 2*z*math.exp(-p*peak_time)/q


def main():
    zs = sorted(set([10**(j/4) for j in range(-32,25)]+[0.999999999999,1.0,1.000000000001]))
    rows = []
    for z in zs:
        value = alpha_times_tv(z)
        assert value <= 1+1e-12
        row = {"alpha_over_sqrt_beta":z,"alpha_times_TV_closed":value}
        if z<1:
            proof_upper = z/math.sinh(z)
            assert value <= proof_upper+1e-12 and proof_upper<=1+1e-12
            row["underdamped_proof_upper"] = proof_upper
        rows.append(row)
    kappa = F(8,5)
    refined = (2*kappa-1)*(3-2/kappa)**2
    assert refined == F(539,80)
    out = {
        "run_time_utc":datetime.now(timezone.utc).isoformat(),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_proof_sha256":hashlib.sha256((HERE/"round-002.md").read_bytes()).hexdigest(),
        "scalar_closed_form_checks":rows,
        "critical_alpha_times_TV_exact":"2/e",
        "sharp_limit":"alpha/sqrt(beta)->infinity gives alpha*TV->1; beta stays positive along the sequence",
        "new_B_at_kappa_8_5_exact":str(refined),
        "new_B_at_kappa_8_5":float(refined),
        "old_B_at_kappa_8_5":21.25,
        "limitations":["Finite closed-form checks supplement the analytic proof, not a universal proof.","Sharpness refers only to the scalar 1/alpha coefficient, not the multiplied two-mode peak constant.","No ETABS or input peak optimization."]
    }
    (HERE/"kernel-refinement-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"checks":len(rows),"min_alpha_TV":min(x["alpha_times_TV_closed"] for x in rows),"max_alpha_TV":max(x["alpha_times_TV_closed"] for x in rows),"B_exact":str(refined),"B":float(refined)}))


if __name__ == "__main__":
    main()
