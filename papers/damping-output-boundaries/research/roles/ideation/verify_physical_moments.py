"""Exact shear-chain matrix moments and candidate exclusion checks; no solver run."""
from fractions import Fraction as F
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import platform

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[2]/"experiments/round002/extended_frequency_check.json"


def dot(x,y):
    return sum(a*b for a,b in zip(x,y))


def mv(a,x):
    return [dot(row,x) for row in a]


def solve(a,b):
    q = [row[:]+[v] for row,v in zip(a,b)]
    n = len(a)
    for i in range(n):
        p = next(j for j in range(i,n) if q[j][i])
        q[i],q[p] = q[p],q[i]
        div = q[i][i]
        q[i] = [v/div for v in q[i]]
        for j in range(n):
            if j != i:
                c = q[j][i]
                q[j] = [v-c*w for v,w in zip(q[j],q[i])]
    return [row[-1] for row in q]


def check_model(m,k,label):
    m1,m2,m3 = m
    k1,k2,k3 = k
    K = [[k1+k2,-k2,F(0)],[-k2,k2+k3,-k3],[F(0),-k3,k3]]
    A = [[v/m[i] for v in row] for i,row in enumerate(K)]
    b = [F(1)]*3
    assert mv(K,b)==[k1,0,0]
    cuts = [[k1,0,0],[-k2,k2,0],[0,-k3,k3]]
    nets = [[K[j][i] for j in range(3)] for i in range(3)]
    static = solve(K,m)
    vectors = [b,mv(A,b),mv(A,mv(A,b))]
    rows = []
    for kind,ells in [("cut",cuts),("net",nets)]:
        for j,ell in enumerate(ells):
            vals = [dot(ell,v) for v in vectors]
            inverse = dot(ell,static)
            assert inverse==(sum(m[j:]) if kind=="cut" else m[j])
            assert vals[0]==(k1 if j==0 else 0)
            if j==1:
                assert vals[1]==-k1*k2/m1
            if j==2:
                assert vals[1]==0 and vals[2]==k1*k2*k3/(m1*m2)
            if kind=="cut" and j==0:
                assert vals[1]==k1*k1/m1
            if kind=="net" and j==0:
                assert vals[1]==k1*(k1+k2)/m1
            rows.append({"output":kind+str(j+1),"mu_minus1":str(inverse),
                         "mu0":str(vals[0]),"mu1":str(vals[1]),"mu2":str(vals[2])})
    return {"label":label,"mass":list(map(str,m)),"stiffness":list(map(str,k)),"rows":rows}


def main():
    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes.decode("utf-8"))
    cases = [check_model(list(map(F,[1,1,1])),list(map(F,[1,1,1])),"unit_chain"),
             check_model([F(2),F(3,2),F(5)],[F(7,3),F(11),F(13,2)],"asymmetric_rational_chain"),
             check_model(list(map(lambda v:F(str(v)),source["mass"])),
                         list(map(lambda v:F(str(v)),source["stiffness"])),"E-EXP-002b_frozen_decimal_parameters")]
    def candidate(ws,rs):
        return {"mu_minus1":sum(r/(w*w) for r,w in zip(rs,ws)),
                "mu0":sum(rs),"mu1":sum(r*w*w for r,w in zip(rs,ws)),
                "mu2":sum(r*w**4 for r,w in zip(rs,ws))}
    c3 = candidate(list(map(F,[1,2,3])),list(map(F,[1,-2,1])))
    c2 = candidate(list(map(F,[1,3])),[F(1),F(-89,10)])
    assert c3=={"mu_minus1":F(11,18),"mu0":0,"mu1":2,"mu2":50}
    assert c2["mu_minus1"]==F(1,90) and c2["mu0"]==F(-79,10)
    # These products are invariant under a nonzero common signed scale.
    assert c3["mu_minus1"]*c3["mu1"]>0  # middle output requires negative.
    assert c2["mu_minus1"]*c2["mu0"]<0  # base output requires positive.
    out = {"time_Asia_Shanghai":datetime.now(timezone(timedelta(hours=8))).isoformat(),
           "python_version":platform.python_version(),
           "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "source":str(SOURCE.relative_to(HERE.parents[4])),
           "source_sha256":hashlib.sha256(source_bytes).hexdigest(),
           "input_sign":"f=-base_acceleration; rho=(ell^T phi)*Gamma; acceleration-transfer residues are -rho",
           "models":cases,"candidate_three_mode":{k:str(v) for k,v in c3.items()},
           "candidate_E004":{k:str(v) for k,v in c2.items()},
           "scope":"Exact physical-side matrix/static moments and candidate exclusions; no new eigensolve, peak computation, ETABS run or inverse-realization sufficiency theorem."}
    (HERE/"physical-moment-result.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"models":len(cases),"outputs_each":6,"candidate_three":out["candidate_three_mode"],"candidate_E004":out["candidate_E004"]},ensure_ascii=False))


if __name__ == "__main__":
    main()
