"""Independent exact polynomial audit of five-mode witness and Q properness."""
from fractions import Fraction as F
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
IDEA = HERE.parent / "ideation/double-zero-result.json"


def multiply(a, b):
    out = [F(0)]*(len(a)+len(b)-1)
    for j, x in enumerate(a):
        for k, y in enumerate(b):
            out[j+k] += x*y
    return out


def numerator(ws, rs, zeta):
    out = [F(0)]*(2*len(ws)-1)
    for i, r in enumerate(rs):
        term = [F(r)]
        for j, w in enumerate(ws):
            if j != i:
                term = multiply(term, [F(w*w), 2*zeta*w, F(1)])
        out = [x+y for x,y in zip(out, term)]
    while len(out)>1 and out[-1] == 0:
        out.pop()
    return out


def divide(a, b):
    rem = a[:]
    q = [F(0)]*(max(0,len(a)-len(b))+1)
    for k in range(len(a)-len(b),-1,-1):
        q[k] = rem[k+len(b)-1]/b[-1]
        for j,v in enumerate(b):
            rem[k+j] -= q[k]*v
    return q, rem[:len(b)-1]


def remainder_at_2i(p):
    _, rem = divide(p, [F(4),F(0),F(1)])
    return [str(rem[0]), str(2*rem[1])]


def main():
    source_bytes = IDEA.read_bytes()
    inp = json.loads(source_bytes.decode("utf-8-sig"))
    ws, raw = [1,2,3,4,5], inp["raw_integer_residues"]
    n0 = numerator(ws, raw, F(1,20))
    n1 = numerator(ws, raw, F(2,25))
    quotient, rem = divide(n0, [F(16),F(0),F(8),F(0),F(1)])
    assert all(v == 0 for v in rem)
    assert remainder_at_2i(quotient) != ["0","0"]
    assert remainder_at_2i(n1) != ["0","0"]
    # Independent Fourier derivative check comes from an exact double factor,
    # not the originating script's numerical differentiation kernels.
    # Read only the raw witness from the source result. Recompute transfer
    # values and moment bounds here; do not inherit derived source fields.
    normalized = [F(r, max(map(abs, raw))) for r in raw]
    h1_re, h1_im = F(0), F(0)
    for w, r in zip(ws, normalized):
        d, c = F(w*w-4), 2*F(2,25)*w*2
        h1_re += r*d/(d*d+c*c)
        h1_im -= r*c/(d*d+c*c)
    h1 = complex(float(h1_re), float(h1_im))
    # h_i(t)=r_i exp(-zeta*w_i*t) sin(w_d*t)/w_d.
    # Triangle inequality and |sin|<=1 give integral t^p |h| dt
    # <= sum |r_i| p! / [w_d (zeta*w_i)^(p+1)].
    def independent_moment_upper(zeta, p):
        return sum(float(abs(r))*math.factorial(p) /
                   (w*math.sqrt(1-zeta*zeta)*(zeta*w)**(p+1))
                   for w, r in zip(ws, normalized))
    m02 = independent_moment_upper(0.05, 2)
    m11 = independent_moment_upper(0.08, 1)
    lower = []
    for t in (10000,100000,1000000):
        p0 = math.pi**2*m02/(2*t*t)
        p1 = abs(h1)-3*math.pi*m11/(4*t)
        lower.append({"T": t,"P0_upper":p0,"P1_lower":p1,"ratio_lower_when_positive":max(0,p1)/p0})
    improper0 = numerator([1,2,3],[1,-2,1],F(1,2))
    improper1 = numerator([1,2,3],[1,-2,1],F(4,5))
    assert improper0 == [F(22),F(12)]
    assert improper1 == [F(22),F(96,5),F(78,25)]
    out = {
        "kind":"independent-exact-polynomial-audit",
        "run_time_utc":datetime.now(timezone.utc).isoformat(),
        "source_result_sha256":hashlib.sha256(source_bytes).hexdigest(),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "frozen_parameters":{"omega":ws,"Omega":2,"zeta0":"1/20","zeta1":"2/25","normalization":"divide raw residues by their maximum absolute value"},
        "input_raw_residues":raw,
        "base_numerator_coefficients_ascending":[str(v) for v in n0],
        "quotient_after_s2plus4_squared":[str(v) for v in quotient],
        "factor_remainder":[str(v) for v in rem],
        "quotient_at_2i":remainder_at_2i(quotient),
        "new_numerator_at_2i":remainder_at_2i(n1),
        "independent_H1":{"real_exact":str(h1_re),"imag_exact":str(h1_im),"abs":abs(h1)},
        "independent_moment_upper_bounds":{"m0_order2":m02,"m1_order1":m11},
        "sin4_global_derivative_upper":{"a_prime":3*math.pi/4,"a_second":math.pi**2},
        "improved_analytic_lower_bounds":lower,
        "improper_Q_witness":{"omega":[1,2,3],"residues":[1,-2,1],"zeta":["1/2","4/5"],"N0_coefficients_ascending":[str(v) for v in improper0],"N1_coefficients_ascending":[str(v) for v in improper1],"Q_asymptotic":"13*s/50", "scope":"Shows Q properness must be checked; no pulse peak experiment executed for this witness."},
        "limitations":["Exact algebra confirms this witness, not minimum modal dimension.","No ETABS identification or finite-pulse time integration.","Only raw integer residues inherited; H1 and moment upper bounds independently recomputed.","Peak lower bounds describe an input family with active duration 2T; no matching O(T^2) upper bound is proved."]
    }
    (HERE/"double-zero-independent.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
