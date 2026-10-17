"""Scalar-only conditional envelope bridge for frozen cut3 harmonic data."""
from pathlib import Path
from decimal import Decimal as D, localcontext, ROUND_CEILING
from datetime import datetime, timezone
import hashlib,json,time,platform

HERE=Path(__file__).resolve().parent
EXP=HERE.parents[2]/'experiments/round002'
PI=D('3.141592653589793238462643383279502884197169399375105820974944592307816406286')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    start=time.perf_counter()
    bs=(EXP/'extended_frequency_check.json').read_bytes(); bf=(EXP/'frequency_refinement.json').read_bytes()
    ext=json.loads(bs.decode('utf-8'),parse_float=D)
    fre=json.loads(bf.decode('utf-8'),parse_float=D)
    rec=next(v for v in ext['decimal_independent_physical_checks'] if v['frequency_rad_s']=='35.22861073659129')
    with localcontext() as ctx:
        ctx.prec=80
        w=list(map(D,rec['omega_rad_s']));r=fre['model']['residues'][2]
        assert r==fre['model']['residues'][5]
        assert all(abs(a-b)<D('1e-12') for a,b in zip(w,fre['model']['omega']))
        z0,z1=D('0.05'),D('0.08');kappa=z1/z0
        h0,h1=D(rec['H0_abs']),D(rec['H1_abs']);delta=h1-kappa*h0
        terms=lambda z:[abs(q)/(a*(1-z*z).sqrt()*(z*a)**2) for a,q in zip(w,r)]
        t0,t1=terms(z0),terms(z1);m0,m1=sum(t0),sum(t1)
        threshold=PI*(m1+kappa*m0)/(2*delta)
        M0=m0.to_integral_value(rounding=ROUND_CEILING);M1=m1.to_integral_value(rounding=ROUND_CEILING)
        T=D('1e16');lip=PI/(2*T)
        p0=h0+lip*M0;p1=h1-lip*M1
        seconds_year=D('31557600')
        out={'kind':'conditional-scalar-envelope-bridge','finished_utc':datetime.now(timezone.utc).isoformat(),
             'elapsed_seconds':time.perf_counter()-start,'python':platform.python_version(),
             'script_sha256':sha(Path(__file__).read_bytes()),'source_extended_sha256':sha(bs),'source_refinement_sha256':sha(bf),
             'frequency_rad_s':rec['frequency_rad_s'],'omega_70digit_source':list(map(str,w)),
             'topcut_residues_from_frozen_float_source':list(map(str,r)),
             'kappa':str(kappa),'H0_abs_from_source':str(h0),'H1_abs_from_source':str(h1),'delta':str(delta),
             'moment0_per_mode_upper':list(map(str,t0)),'moment1_per_mode_upper':list(map(str,t1)),
             'moment0_sum_upper_numeric':str(m0),'moment1_sum_upper_numeric':str(m1),
             'threshold_T_seconds_numeric':str(threshold),'threshold_active_duration_2T_seconds':str(2*threshold),
             'threshold_active_duration_julian_years':str(2*threshold/seconds_year),
             'chosen_T_seconds':str(T),'chosen_active_duration_seconds':str(2*T),'chosen_active_duration_julian_years':str(2*T/seconds_year),
             'rounded_moment0_numeric':str(M0),'rounded_moment1_numeric':str(M1),
             'chosen_P0_upper_numeric':str(p0),'chosen_P1_lower_numeric':str(p1),'chosen_ratio_lower_numeric':str(p1/p0),
             'chosen_strict_excess_numeric':str(p1-kappa*p0),
             'checks':{'source_harmonic_delta_positive':delta>0,'chosen_T_above_threshold':T>threshold,'chosen_P1_lower_positive':p1>0,'chosen_ratio_lower_above_kappa':p1/p0>kappa},
             'limits':['No giant time history simulated.','Frozen H values are high-precision numerical values, not interval certificates.','Residues inherited at float64 reporting precision; rounding moment sums upward is numerical conservatism, not a proof of exact physical moment bounds.','Conditional analytic lemma must be combined with certified positive delta for a strict mathematical instance certificate.']}
    assert all(out['checks'].values())
    (HERE/'bridge-instance-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
