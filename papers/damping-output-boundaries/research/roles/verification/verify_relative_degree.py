"""Exact right-derivative audit for the fixed-duration high-frequency witness."""
from fractions import Fraction as F
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent


def derivatives(zeta, max_order=7):
    out = [F(0)]*(max_order+1)
    for w,r in zip((1,2,3),(1,-2,1)):
        modal = [F(0),F(r)]
        for j in range(max_order-1):
            modal.append(-2*zeta*w*modal[j+1]-w*w*modal[j])
        out = [x+y for x,y in zip(out,modal)]
    return out


def l1_derivative_upper(zeta, sqrt_lower, order):
    assert sqrt_lower**2 <= 1-zeta*zeta
    # |h_i^(l)(t)| <= |r_i|*w_i^l*exp(-zeta*w_i*t)/(w_i*sqrt(1-zeta^2)).
    return sum(F(abs(r))*F(w)**(order-2)/(zeta*sqrt_lower) for w,r in zip((1,2,3),(1,-2,1)))


def main():
    base,new = derivatives(F(1,2)),derivatives(F(4,5))
    assert base[:4] == [0]*4 and base[4] == 12
    assert new[:3] == [0]*3 and new[3] == F(78,25)
    out = {
        "run_time_utc":datetime.now(timezone.utc).isoformat(),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "parameters":{"omega":[1,2,3],"residues":[1,-2,1],"zeta":["1/2","4/5"]},
        "base_right_derivatives_orders_0_to_7":[str(v) for v in base],
        "new_right_derivatives_orders_0_to_7":[str(v) for v in new],
        "base_derivative_L1_upper_orders_0_to_5":[str(l1_derivative_upper(F(1,2),F(4,5),j)) for j in range(6)],
        "new_derivative_L1_upper_orders_0_to_5":[str(l1_derivative_upper(F(4,5),F(3,5),j)) for j in range(6)],
        "scope":"Verifies the right-derivative inputs and integrable derivative bounds of the analytic integration-by-parts proof; no high-frequency pulse time integration."
    }
    (HERE/"relative-degree-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
