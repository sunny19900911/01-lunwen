"""Exact rational outer bounds for the five-mode window-center estimate."""
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
INPUT = HERE/"double-zero-independent.json"


def main():
    source_bytes = INPUT.read_bytes()
    inp = json.loads(source_bytes.decode("utf-8"))
    raw = inp["input_raw_residues"]
    residues = [F(abs(r),max(map(abs,raw))) for r in raw]
    def rational_moment(zeta, sqrt_lower):
        assert sqrt_lower**2 < 1-zeta*zeta
        return sum(2*r/(w*sqrt_lower*(zeta*w)**3) for w,r in zip(range(1,6),residues))
    m02 = rational_moment(F(1,20),F(499,500))
    m12 = rational_moment(F(2,25),F(249,250))
    him = F(inp["independent_H1"]["imag_exact"])
    assert m02 < 162 and m12 < 40 and him > F(113,1000000)
    # pi^2<10 and |H1|>=Im H1>113e-6. a'_T(T)=0 eliminates
    # the first moment term at the selected center time for the new state.
    rows = []
    for t in (1920,3000,4800,10000):
        p0 = F(810,t*t)
        p1 = F(113,1000000)-F(200,t*t)
        rows.append({"T":t,"support_duration":2*t,"P0_upper_exact":str(p0),"P1_lower_exact":str(p1),"ratio_lower_exact":str(p1/p0),"ratio_lower_approx":float(p1/p0)})
    out = {
        "run_time_utc":datetime.now(timezone.utc).isoformat(),
        "input_sha256":hashlib.sha256(source_bytes).hexdigest(),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "m02_rational_upper":str(m02),"m12_rational_upper":str(m12),
        "m02_upper_approx":float(m02),"m12_upper_approx":float(m12),
        "safe_outer_bounds":{"m02":162,"m12":40,"pi_squared_upper":10,"H1_abs_lower":"113/1000000"},
        "rows":rows,
        "scope":"Analytic lower bounds for a varying-duration sin^4 input family; no time-history integration, no matching upper growth rate, no ETABS result."
    }
    (HERE/"center-bound-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
