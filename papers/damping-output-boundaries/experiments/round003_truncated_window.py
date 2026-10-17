"""Synthetic two-mode output: frozen-window versus complete-tail peak.

The baseline positive-real-zero exponential term is cancelled analytically.
Closed forms, sampling refinement, curvature bounds and 70-digit checks are used.
"""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import csv
import hashlib
import json
import math
import platform
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent/'round003'
W=np.array([1.,3.]);R=np.array([1.,-2.])
Z0,Z1=.05,.08
Z=Z0+np.sqrt(Z0*Z0+7)
TS=[.25,.5,1.,2.,3.,4.,6.,8.]
STEPS=[.01,.005,.0025]
TAIL=600.
KAPPA=Z1/Z0
COARSE_BOUND=(4*KAPPA-3)*(5-4/KAPPA)**2


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def coefficients(damping):
    alpha=damping*W;beta=W*np.sqrt(1-damping*damping)
    denominator=Z*Z+2*damping*W*Z+W*W
    a=R/denominator
    amplitude=np.sqrt(1+((Z+alpha)/beta)**2)
    return alpha,beta,a,amplitude


def G(t,damping):
    t=np.asarray(t)
    alpha,beta,a,_=coefficients(damping)
    f=np.exp(-t[...,None]*alpha)*(np.cos(t[...,None]*beta)+(Z+alpha)/beta*np.sin(t[...,None]*beta))
    if damping==Z0:
        # D2(z0)=2 D1(z0), so A1=-A2 exactly; never sum noisy exponentials.
        value=(f[...,0]-f[...,1])/(Z*Z+2*Z0*Z+1)
    else:
        value=f@a
    return value


def h_at_zero(damping):
    if damping==Z0:return 0.
    d=Z*Z+2*damping*W*Z+W*W
    # Numerator N1(z0)=2(zeta1-zeta0)z0, not a subtractive residual.
    return float(2*(damping-Z0)*Z/(d[0]*d[1]))


def before(t,T,damping):
    t=np.asarray(t)
    if damping==Z0:return -np.exp(-Z*T)*G(t,damping)
    y=h_at_zero(damping)*np.exp(Z*(t-T))-np.exp(-Z*T)*G(t,damping)
    return np.where(t==0,0.,y)


def after(tau,T,damping):
    tau=np.asarray(tau)
    return G(tau,damping)-np.exp(-Z*T)*G(T+tau,damping)


def golden_peak(fun,left,right):
    g=(np.sqrt(5)-1)/2;a,b=left,right
    c,d=b-g*(b-a),a+g*(b-a);fc,fd=abs(fun(c)),abs(fun(d))
    for _ in range(65):
        if fc<fd:
            a,c,fc=c,d,fd;d=a+g*(b-a);fd=abs(fun(d))
        else:
            b,d,fd=d,c,fc;c=b-g*(b-a);fc=abs(fun(c))
    return max([(left,abs(fun(left))),(right,abs(fun(right))),(c,fc),(d,fd)],key=lambda x:x[1])


def sampled_peak(t,y,fun):
    index=int(np.argmax(abs(y)));refined=(float(t[index]),float(abs(y[index])))
    if index>0 and index<len(t)-1:
        refined=golden_peak(fun,float(t[index-1]),float(t[index+1]))
    return {'sample_peak':float(abs(y[index])),'sample_time':float(t[index]),
            'refined_peak':float(refined[1]),'refined_time':float(refined[0])}


def derivative_and_tail_bounds(T,damping,L):
    alpha,_,a,amplitude=coefficients(damping)
    if damping==Z0:
        a=np.array([1.,-1.])/(Z*Z+2*Z0*Z+1)
    curvature_before=Z*Z*abs(h_at_zero(damping))+np.exp(-Z*T)*np.sum(abs(a)*W*W*amplitude)
    curvature_after=np.sum(abs(a)*W*W*amplitude*(1+np.exp(-(Z+alpha)*T)))
    tail=np.sum(abs(a)*amplitude*(1+np.exp(-(Z+alpha)*T))*np.exp(-alpha*L))
    return float(curvature_before),float(curvature_after),float(tail)


def decimal_baseline(t,T):
    """Independent high precision modal convolution, without enforcing cancellation."""
    D=Decimal
    with localcontext() as context:
        context.prec=70
        zeta=D('.05');z=zeta+(zeta*zeta+D(7)).sqrt();tt=D(str(t));duration=D(str(T))
        def sincos(x):
            sinterm=x;costerm=D(1);s=x;c=D(1)
            for j in range(1,200):
                sinterm*=-x*x/D((2*j)*(2*j+1));costerm*=-x*x/D((2*j-1)*(2*j))
                s+=sinterm;c+=costerm
                if max(abs(sinterm),abs(costerm))<D('1e-77'):break
            return s,c
        response=D(0)
        h=D(0)
        for w,r in [(D(1),D(1)),(D(3),D(-2))]:
            alpha=zeta*w;beta=w*(D(1)-zeta*zeta).sqrt();den=z*z+2*alpha*z+w*w
            s,c=sincos(beta*tt)
            f=(-alpha*tt).exp()*(c+(z+alpha)/beta*s)
            response+=r*(-z*duration).exp()*((z*tt).exp()-f)/den
            h+=r/den
        return {'t':str(tt),'T':str(duration),'baseline_response_70digits':str(response),
                'baseline_H_at_zero_residual':str(h),'precision_digits':context.prec}


def main():
    started=time.perf_counter();OUT.mkdir(exist_ok=True)
    rows=[];summary=[];precise=[]
    for T in TS:
        details=[]
        for step in STEPS:
            npre=math.ceil(T/step)
            t=np.linspace(0,T,npre+1)
            tau=np.linspace(0,TAIL,int(round(TAIL/step))+1)
            states=[]
            for damping in [Z0,Z1]:
                pre=before(t,T,damping);tail=after(tau,T,damping)
                p=sampled_peak(t,pre,lambda x:before(x,T,damping))
                a=sampled_peak(tau,tail,lambda x:after(x,T,damping))
                mpre,mpost,tailbound=derivative_and_tail_bounds(T,damping,TAIL)
                p_upper=p['sample_peak']+mpre*(T/npre)**2/8
                a_upper=a['sample_peak']+mpost*step*step/8
                lower=max(p['refined_peak'],a['refined_peak'])
                upper=max(p_upper,a_upper,tailbound)
                states.append({'damping':damping,'pre':p,'tail':a,
                               'truncated_peak_numerical_upper':p_upper,
                               'full_peak_numerical_lower':lower,'full_peak_numerical_upper':upper,
                               'tail_bound_beyond_600':tailbound,
                               'full_refined_peak':lower,
                               'full_peak_time':p['refined_time'] if p['refined_peak']>=a['refined_peak'] else T+a['refined_time'],
                               'pre_curvature_bound':mpre,'post_curvature_bound':mpost})
            a,b=states
            row={'T_s':T,'dt_s':step,'truncated_P0':a['pre']['refined_peak'],
                 'truncated_P1':b['pre']['refined_peak'],'truncated_ratio':b['pre']['refined_peak']/a['pre']['refined_peak'],
                 'truncated_sample_P0':a['pre']['sample_peak'],'truncated_sample_P1':b['pre']['sample_peak'],
                 'truncated_sample_ratio':b['pre']['sample_peak']/a['pre']['sample_peak'],
                 'truncated_ratio_numerical_lower':b['pre']['sample_peak']/a['truncated_peak_numerical_upper'],
                 'full_P0':a['full_refined_peak'],'full_P1':b['full_refined_peak'],
                 'full_sample_P0':max(a['pre']['sample_peak'],a['tail']['sample_peak']),
                 'full_sample_P1':max(b['pre']['sample_peak'],b['tail']['sample_peak']),
                 'full_ratio':b['full_refined_peak']/a['full_refined_peak'],
                 'full_ratio_numerical_lower':b['full_peak_numerical_lower']/a['full_peak_numerical_upper'],
                 'full_ratio_numerical_upper':b['full_peak_numerical_upper']/a['full_peak_numerical_lower'],
                 'baseline_full_peak_time_s':a['full_peak_time'],'new_full_peak_time_s':b['full_peak_time'],
                 'max_bound_beyond_600':max(a['tail_bound_beyond_600'],b['tail_bound_beyond_600'])}
            rows.append(row);details.append({'grid':row,'states':states})
        final=details[-1]
        summary.append(final)
        old=final['states'][0]
        for point in [old['pre']['refined_time'],T]:
            check=decimal_baseline(point,T)
            high=float(check['baseline_response_70digits']);low=float(before(point,T,Z0))
            check['double_closed_form_value']=low
            check['relative_difference']=abs(low-high)/max(abs(high),1e-300)
            precise.append(check)
        print(f'T={T:g}: truncated={rows[-1]["truncated_ratio"]:.9g}, complete={rows[-1]["full_ratio"]:.9g}',flush=True)

    with (OUT/'window_peak_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    trace_t=np.linspace(0,24,1201);T=4.
    with (OUT/'T4_response_trace.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['t_s','input','baseline_y','new_y','inside_frozen_window'])
        for t in trace_t:
            if t<=T:
                u=np.exp(Z*(t-T));y0=before(t,T,Z0);y1=before(t,T,Z1)
            else:u=0.;y0=after(t-T,T,Z0);y1=after(t-T,T,Z1)
            writer.writerow([float(t),float(u),float(y0),float(y1),bool(t<=T)])

    convergence=[]
    for T in TS:
        subset=[row for row in rows if row['T_s']==T]
        convergence.append({'T':T,
                            'truncated_ratio_rel_range':max(r['truncated_ratio'] for r in subset)/min(r['truncated_ratio'] for r in subset)-1,
                            'full_ratio_rel_range':max(r['full_ratio'] for r in subset)/min(r['full_ratio'] for r in subset)-1,
                            'truncated_raw_sample_ratio_rel_range':max(r['truncated_sample_ratio'] for r in subset)/min(r['truncated_sample_ratio'] for r in subset)-1,
                            'full_raw_sample_ratio_rel_range':max(r['full_sample_P1']/r['full_sample_P0'] for r in subset)/min(r['full_sample_P1']/r['full_sample_P0'] for r in subset)-1})
    checks={'nonzero_finite_input':all((1-math.exp(-2*Z*T))/(2*Z)>0 for T in TS),
            'baseline_exp_term_cancelled_analytically':h_at_zero(Z0)==0.,
            'zero_initial_responses':all(float(before(0,T,zeta))==0 for T in TS for zeta in [Z0,Z1]),
            'decimal_baseline_relative_checks_below_1e-10':all(row['relative_difference']<1e-10 for row in precise),
            'T4_truncated_ratio_above_complete_coarse_bound':next(r for r in rows if r['T_s']==4 and r['dt_s']==.0025)['truncated_ratio_numerical_lower']>COARSE_BOUND,
            'all_complete_ratio_upper_below_complete_coarse_bound':all(r['full_ratio_numerical_upper']<COARSE_BOUND for r in rows),
            'tail_beyond_600_below_1e-12_of_full_baseline':all(r['max_bound_beyond_600']<1e-12*r['full_P0'] for r in rows),
            'refined_peak_ratios_converge_below_1e-8':all(max(r['truncated_ratio_rel_range'],r['full_ratio_rel_range'])<1e-8 for r in convergence),
            'elapsed_below_300_seconds':time.perf_counter()-started<300}
    params={'omega':W.tolist(),'residues':R.tolist(),'zeta0':Z0,'zeta1':Z1,'T_values':TS,'input':'exp(z0*(t-T)) on [0,T], zero elsewhere','zero_initial':True}
    result={'evidence_id':'E-EXP-003','finished_utc':datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds':time.perf_counter()-started,'code_sha256':sha(__file__),
            'python':platform.python_version(),'numpy':np.__version__,'python_executable':sys.executable,
            'params':params,'params_sha256':hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest(),
            'z0':float(Z),'H0_at_z0_exact':0,'H1_at_z0':h_at_zero(Z1),
            'complete_peak_coarse_bound':COARSE_BOUND,'steps':STEPS,'tail_duration_after_T':TAIL,
            'summaries':summary,'decimal_checks':precise,'convergence':convergence,'checks':checks,
            'numerical_enclosure_note':'Curvature interpolation bounds are analytic formulas evaluated in float64, without directed interval rounding. Tail amplitudes bounded by modal sinusoid envelopes. Refined maxima remain numerical evidence.',
            'boundary':'Synthetic fixed real-residue output. Frozen [0,T] ratio is a different observable from the full response peak including its free tail; no engineering floor-shear interpretation.'}
    (OUT/'truncated_window_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'checks':checks,'elapsed_seconds':result['elapsed_seconds'],'max_convergence_variation':max(max(r['truncated_ratio_rel_range'],r['full_ratio_rel_range']) for r in convergence)},ensure_ascii=False,indent=2))
    assert all(checks.values())


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
