"""Small exact identity checks and closed-kernel examples; no universal numerical proof."""
from datetime import datetime, timezone, timedelta
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import math
import platform

HERE = Path(__file__).resolve().parent


def closed_tv(alpha, beta):
    if beta == alpha*alpha:
        return 2/(math.e*alpha)
    if beta > alpha*alpha:
        gamma = math.sqrt(beta-alpha*alpha)
        t0 = math.atan2(gamma,alpha)/gamma
        return 2*math.exp(-alpha*t0)/(math.sqrt(beta)*(-math.expm1(-math.pi*alpha/gamma)))
    q = alpha+math.sqrt(alpha*alpha-beta)
    p = beta/q
    t0 = math.log(q/p)/(q-p)
    return 2*math.exp(-p*t0)/q


def main():
    identities = []
    for alpha in [F(1,10),F(1),F(10)]:
        for gamma in [F(1,100),F(1),F(100)]:
            den = alpha*alpha+4*gamma*gamma
            c2 = F(1)/(2*alpha)+alpha/(2*den)
            s2 = F(1)/(2*alpha)-alpha/(2*den)
            cs = gamma/den
            direct = c2-2*alpha/gamma*cs+alpha*alpha/(gamma*gamma)*s2
            compact = F(1)/(2*alpha)+alpha/(2*den)
            assert direct == compact and compact < 1/alpha
            identities.append({"alpha":str(alpha),"gamma":str(gamma),"weighted_square_integral":str(compact)})
    cases = []
    for beta in [1.000001,1.01,2.,101.,10001.,1.,.99,.5,.1,.01,1e-4,1e-8]:
        tv = closed_tv(1.,beta)
        assert 0<tv<1
        cases.append({"alpha":1,"beta":beta,"TV_closed":tv,
                      "branch":"under" if beta>1 else "critical" if beta==1 else "over"})
    kappa = F(8,5)
    new = (2*kappa-1)*(3-2/kappa)**2
    old = (4*kappa-3)*(5-4/kappa)**2
    assert new == F(539,80) and old == F(85,4)
    out = {"time_Asia_Shanghai":datetime.now(timezone(timedelta(hours=8))).isoformat(),
           "python_version":platform.python_version(),
           "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "exact_weighted_square_identity_cases":identities,
           "closed_kernel_examples":cases,
           "kappa_exact":str(kappa),"new_bound_exact":str(new),"new_bound":float(new),
           "old_bound_exact":str(old),"old_bound":float(old),
           "scope":"Finite examples supplement the analytic proof in round-005.md; no numerical proof, peak search, or ETABS result."}
    (HERE/"sharper-kernel-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"exact_cases":len(identities),"closed_kernel_cases":len(cases),"old_bound":float(old),"new_bound":float(new)},ensure_ascii=False))


if __name__ == "__main__":
    main()
