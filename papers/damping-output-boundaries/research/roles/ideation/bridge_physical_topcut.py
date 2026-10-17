"""Finite-envelope certificate scale from frozen E002b; never simulates huge T."""
from datetime import datetime, timezone, timedelta
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import platform
import time

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[2]/"experiments/round002/extended_frequency_check.json"


def main():
    start = time.perf_counter()
    source_bytes = SOURCE.read_bytes()
    source = json.loads(source_bytes.decode("utf-8"))
    frozen = next(row for row in source["decimal_independent_physical_checks"]
                  if row["frequency_rad_s"]=="50")
    with localcontext() as context:
        context.prec = 80
        one,zero = D(1),D(0)
        m = [D(str(v)) for v in source["mass"]]
        k = [D(str(v)) for v in source["stiffness"]]
        omega = sorted(D(v) for v in frozen["omega_rad_s"])
        K = [[k[0]+k[1],-k[1],zero],[-k[1],k[1]+k[2],-k[2]],[zero,-k[2],k[2]]]
        modes=[];residues=[];gammas=[];eigen_residuals=[]
        for w in omega:
            lam=w*w
            v=[one,(k[0]+k[1]-lam*m[0])/k[1]]
            v.append(((k[1]+k[2]-lam*m[1])*v[1]-k[1])/k[2])
            norm=sum(mi*vi*vi for mi,vi in zip(m,v)).sqrt()
            phi=[vi/norm for vi in v]
            gamma=sum(mi*vi for mi,vi in zip(m,phi))
            residue=-k[2]*(phi[2]-phi[1])*gamma
            modes.append(phi);gammas.append(gamma);residues.append(residue)
            eigen_residuals.append(max(abs(sum(K[i][j]*phi[j] for j in range(3))-lam*m[i]*phi[i]) for i in range(3)))
        gram=max(abs(sum(m[j]*modes[i][j]*modes[l][j] for j in range(3))-(one if i==l else zero)) for i in range(3) for l in range(3))
        assert max(eigen_residuals)<D('1e-60') and gram<D('1e-60')
        om=D(50);z0=D('.05');z1=D('.08');kappa=z1/z0
        def transfer(z):
            parts=[]
            for w,r in zip(omega,residues):
                aa=w*w-om*om;bb=2*z*w*om;den=aa*aa+bb*bb
                parts.append((r*aa/den,-r*bb/den))
            return sum(p[0] for p in parts),sum(p[1] for p in parts)
        def amplitude(z):
            re,im=transfer(z)
            return (re*re+im*im).sqrt()
        amps=[amplitude(z) for z in [z0,z1]]
        moments=[sum(abs(r)/(z*z*w**3*(one-z*z).sqrt()) for w,r in zip(omega,residues)) for z in [z0,z1]]
        frozen_amps=[D(frozen['H0_abs']),D(frozen['H1_abs'])]
        amplitude_difference=max(abs(a-b) for a,b in zip(amps,frozen_amps))
        assert amplitude_difference<D('1e-60')
        delta=amps[1]-kappa*amps[0]
        assert delta>D('3e-13') and moments[0]<1400 and moments[1]<550
        # Decimal pi value is for reporting, not outward-rounded certification.
        pi=D('3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628')
        critical=pi*(moments[1]+kappa*moments[0])/(2*delta)
        T=D('2e16');seconds_per_year=D(31557600)
        eps=[pi*v/(2*T) for v in moments]
        lower_ratio=(amps[1]-eps[1])/(amps[0]+eps[0])
        assert lower_ratio>kappa
        threshold_outer=F(22,7)*(F(550)+F(8,5)*1400)/(2*F(3,10**13))
        chosen=F(2*10**16)
        assert chosen>threshold_outer
        exact_margin=F(3,10**13)-F(22,7)*(550+F(8,5)*1400)/(2*chosen)
        assert exact_margin>0
        out={"time_Asia_Shanghai":datetime.now(timezone(timedelta(hours=8))).isoformat(),
             "python_version":platform.python_version(),"decimal_precision":context.prec,
             "source_sha256":hashlib.sha256(source_bytes).hexdigest(),
             "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "omega_from_frozen_70_digit_physical_check":list(map(str,omega)),
             "reconstructed_actual_acceleration_residues":list(map(str,residues)),
             "mass_normalization_max_error":str(gram),"eigen_equation_max_residual":str(max(eigen_residuals)),
             "modal_vs_frozen_physical_amplitude_max_difference":str(amplitude_difference),
             "frequency_rad_s":"50","zeta":[str(z0),str(z1)],"kappa":str(kappa),
             "H0_abs":str(amps[0]),"H1_abs":str(amps[1]),"delta":str(delta),
             "first_absolute_moment_analytic_upper_evaluated":[str(v) for v in moments],
             "T_critical_formula_evaluated_s":str(critical),
             "T_critical_formula_evaluated_years":str(critical/seconds_per_year),
             "chosen_T_s":str(T),"input_support_s":["0",str(2*T)],
             "chosen_support_years":str(2*T/seconds_per_year),
             "full_time_error_bounds_at_chosen_T":[str(v) for v in eps],
             "peak_ratio_lower_formula_evaluated":str(lower_ratio),
             "coarse_numerical_outer_conditions":{"m0_upper":1400,"m1_upper":550,"delta_lower":"3/10000000000000","pi_upper":"22/7"},
             "coarse_T_threshold_exact_if_outer_conditions_hold":str(threshold_outer),
             "coarse_strict_margin_exact_at_chosen_T_if_outer_conditions_hold":str(exact_margin),
             "input_definition":"sin^2(pi*t/(2*T))*cos(50*(t-T)-arg(H1(i*50))) for 0<=t<=2*T; zero outside",
             "elapsed_seconds":time.perf_counter()-start,
             "scope":"Conditional analytic bridge with high-precision numerical model instance; no huge-duration simulation, directed rounding, machine certificate, natural earthquake, or engineering risk estimate."}
    (HERE/"physical-topcut-bridge.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({key:out[key] for key in ['delta','first_absolute_moment_analytic_upper_evaluated','T_critical_formula_evaluated_s','chosen_support_years','peak_ratio_lower_formula_evaluated','elapsed_seconds']},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
