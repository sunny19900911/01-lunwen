"""Rational endpoint checks for an IVT-defined physical model; no eigensweep/root search."""
from fractions import Fraction as F
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import platform

HERE=Path(__file__).resolve().parent


def determinant(a):
    return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])


def model(L):
    return [[F(2),F(-1),F(0)],[F(-1),1+L,-L],[F(0),-L,L]]


def main():
    cap=F(20000)
    K1=model(F(1));KB=model(cap)
    assert determinant(K1)==1 and sum(K1[i][i] for i in range(3))==5
    assert determinant(KB)==cap
    # Lower q(1): D>=8, S^3<=15sqrt(15)<60 because sqrt(15)<4.
    assert F(15)<F(4)**2
    lower=F(8)/(4*60)
    target=F(1,400)
    assert lower==F(1,30) and lower>target
    # Ritz (sqrt(mu-)+sqrt(mu+))^2=5/2+sqrt(2)<4.
    assert F(2)<F(3,2)**2 and F(5,2)+F(3,2)==4
    # High eigenvalue >= Rayleigh(v), v=(0,1,-1).
    v=[F(0),F(1),F(-1)]
    rayleigh=sum(v[i]*KB[i][j]*v[j] for i in range(3) for j in range(3))/sum(x*x for x in v)
    assert rayleigh==2*cap+F(1,2) and rayleigh>200**2
    upper=F(2)/(4*200)
    assert upper==target  # actual inequalities are strict on both numerator and denominator.
    # kappa mapping and the nonzero exact numerator multiplier.
    z0,z1=F(1,20),F(2,25)
    assert z0*z0==target and z1/z0==F(8,5)
    numerator_factor=1-(z1/z0)**2
    assert numerator_factor==F(-39,25)
    out={"time_Asia_Shanghai":datetime.now(timezone(timedelta(hours=8))).isoformat(),
         "python_version":platform.python_version(),
         "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "model_family":"M=I3; k=(1,1,L); ell=(0,-L,L); f=-base_acceleration",
         "only_endpoint_matrix_values_checked":[1,20000],
         "characteristic_polynomial":"lambda^3-(3+2L)*lambda^2+(1+5L)*lambda-L",
         "Ritz_generalized_characteristic_polynomial":"2*mu^2-5*mu+1",
         "q_definition":"q(L)=zeta_crit(L)^2=D(L)/(4*S(L)^3)",
         "lower_endpoint_q_strict_lower":str(lower),"target_q":str(target),
         "upper_endpoint_rayleigh_exact":str(rayleigh),
         "upper_endpoint_q_strict_upper":str(upper),
         "IVT_root_open_bracket":[1,20000],
         "L_star_definition":"smallest L in [1,20000] with q(L)=1/400; existence/continuity proved in round-009.md",
         "zeta0_exact":str(z0),"zeta1_exact":str(z1),
         "new_numerator_factor_exact":str(numerator_factor),
         "scope":"Exact rational supporting checks only. No numerical L*, root search, model scan, eigenvalue approximation, time simulation, or engineering-instance claim."}
    (HERE/"low-damping-bracket.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
