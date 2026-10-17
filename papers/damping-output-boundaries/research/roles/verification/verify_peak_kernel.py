"""Boundary checks accompanying the independent L-infinity proof review.

Closed scalar kernel total variations, exact two-mode coefficient identity,
and exact opposite-sign-pole partial fractions. These are not peak searches.
"""
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
INPUT = HERE.parent/"ideation/round-001.md"


def positive_beta_tv(alpha, beta):
    omega = math.sqrt(beta)
    if alpha == omega:
        return 2/(math.e*alpha)
    if alpha < omega:
        gamma = math.sqrt(beta-alpha*alpha)
        first_extremum = math.atan2(gamma,alpha)/gamma
        return 2*math.exp(-alpha*first_extremum)/(omega*(-math.expm1(-math.pi*alpha/gamma)))
    q = alpha+math.sqrt(alpha*alpha-beta)
    p = beta/q
    first_extremum = math.log(q/p)/(q-p)
    return 2*math.exp(-p*first_extremum)/q


def main():
    kernel_checks = []
    for beta in (0.01,1.0,100.0):
        for ratio in (1e-6,0.001,0.05,0.5,0.999999,1.0,1.000001,2,10,1000):
            alpha = ratio*math.sqrt(beta)
            tv = positive_beta_tv(alpha,beta)
            assert tv <= 2/alpha*(1+1e-12)
            kernel_checks.append({"alpha":alpha,"beta":beta,"TV_closed":tv,"alpha_times_TV":alpha*tv})
    identity_count, opposite_poles_count = 0,0
    branches = set()
    for w1,w2 in ((F(1),F(2)),(F(1),F(3)),(F(2),F(3))):
        for r1 in range(-4,5):
            for r2 in range(-4,5):
                if r1 == r2 == 0:
                    continue
                a,b,c = r1+r2,r1*w2+r2*w1,r1*w2*w2+r2*w1*w1
                assert c == (w1+w2)*b-w1*w2*a
                if a == 0:
                    assert b != 0 and c/b == w1+w2
                    branches.add("a=0")
                else:
                    if c/a > 0:
                        assert b/a > 0
                        branches.add("ac>0")
                    elif c == 0:
                        assert b/a == w1*w2/(w1+w2)
                        branches.add("c=0")
                    else:
                        branches.add("ac<0")
                    if b == 0:
                        assert c == -w1*w2*a
                        branches.add("b=0")
                identity_count += 1
    for p,q in ((F(1),F(1)),(F(1),F(3)),(F(3),F(1)),(F(1,1000),F(1)),(F(1),F(1,1000))):
        alpha,beta = (q-p)/2,-p*q
        for s in (F(2,7),F(11,7),F(50,7)):
            if s in (p,-q):
                continue
            actual = s/(s*s+2*alpha*s+beta)
            parts = (p/(p+q))/(s-p)+(q/(p+q))/(s+q)
            assert actual == parts
            opposite_poles_count += 1
    kappa = 1.6
    out = {
        "run_time_utc":datetime.now(timezone.utc).isoformat(),
        "input_sha256":hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "positive_beta_kernel_checks":kernel_checks,
        "two_mode_exact_identity_checks":identity_count,
        "branches_covered":sorted(branches),
        "opposite_pole_exact_partial_fraction_checks":opposite_poles_count,
        "B_at_kappa_1_6":(4*kappa-3)*(5-4/kappa)**2,
        "scope":"Boundary checks supplement the analytic proof in round-002.md; no numerical scan is a universal proof; no ETABS data."
    }
    (HERE/"peak-kernel-audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"kernel_checks":len(kernel_checks),"identity_checks":identity_count,"branches":sorted(branches),"opposite_pole_checks":opposite_poles_count,"B":out["B_at_kappa_1_6"]}))


if __name__ == "__main__":
    main()
