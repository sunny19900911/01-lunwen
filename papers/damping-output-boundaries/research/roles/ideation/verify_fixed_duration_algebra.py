"""Exact polynomial and initial-kernel-derivative audit for fixed-window carrier family."""
from fractions import Fraction as F
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import platform
from verify_double_zero import pmul, numerator

HERE = Path(__file__).resolve().parent


def modal_derivatives(w, zeta, order):
    vals = [F(0), F(1)]
    for k in range(order-1):
        vals.append(-2*zeta*w*vals[k+1]-w*w*vals[k])
    return vals[:order+1]


def main():
    ws = list(map(F,[1,2,3]))
    rs = list(map(F,[1,-2,1]))
    rows = []
    for z in [F(1,2), F(4,5)]:
        n = numerator(ws,rs,z)
        while len(n)>1 and n[-1]==0:
            n.pop()
        d = [F(1)]
        for w in ws:
            d = pmul(d,[w*w,2*z*w,F(1)])
        individual = [modal_derivatives(w,z,7) for w in ws]
        hd = [sum(r*values[k] for r,values in zip(rs,individual)) for k in range(8)]
        rows.append({"zeta":str(z),"numerator_ascending":list(map(str,n)),
                     "denominator_ascending":list(map(str,d)),
                     "kernel_right_derivatives_0_to_7":list(map(str,hd)),
                     "relative_degree":len(d)-len(n)})
    assert rows[0]["numerator_ascending"]==["22","12"]
    assert rows[1]["numerator_ascending"]==["22","96/5","78/25"]
    assert rows[0]["kernel_right_derivatives_0_to_7"][:6]==["0","0","0","0","12","-50"]
    assert rows[1]["kernel_right_derivatives_0_to_7"][:5]==["0","0","0","78/25","-1344/125"]
    ratio = F(rows[1]["numerator_ascending"][-1])/F(rows[0]["numerator_ascending"][-1])
    assert ratio == F(13,50)
    out = {"time_Asia_Shanghai":datetime.now(timezone(timedelta(hours=8))).isoformat(),
           "python_version":platform.python_version(),
           "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "polynomial_helper_sha256":hashlib.sha256((HERE/"verify_double_zero.py").read_bytes()).hexdigest(),
           "omega":list(map(str,ws)),"residues":list(map(str,rs)),
           "checks":rows,"asymptotic_peak_ratio_coefficient_exact":str(ratio),
           "scope":"Exact algebra only; uniform integration-by-parts argument is in round-003.md. No finite-pulse integration or fixed-record prediction."}
    (HERE/"fixed-duration-algebra.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
