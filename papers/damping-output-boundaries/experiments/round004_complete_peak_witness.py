"""Small synthetic finite-input witness search; FFT inverse followed by causal forward runs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,time,sys,csv,math
import numpy as np

OUT=Path(__file__).resolve().parent/'round004'
W=np.array([1.,3.]);R=np.array([1.,-8.9]);Z0=.05;Z1=.08
PERIOD=1024.;SUPPORT=100.;CUT=300.;RAMP=20.;TAIL=900.;SIGMA=.1

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def H(s,z):return sum(R[j]/(s*s+2*z*W[j]*s+W[j]**2) for j in range(2))
def N(z):return np.array([sum(R),2*z*(R[0]*3+R[1]),R[0]*9+R[1]])
def D(z,j):return np.array([1.,2*z*W[j],W[j]**2])
NUM=np.polymul(N(Z1),np.polymul(D(Z0,0),D(Z0,1)))
DEN=np.polymul(N(Z0),np.polymul(D(Z1,0),D(Z1,1)))
POLES=np.roots(DEN);RES=np.polyval(np.polysub(NUM,DEN),POLES)/np.polyval(np.polyder(DEN),POLES)

def q(t):
    t=np.asarray(t);y=np.zeros(t.shape,complex)
    for p,c in zip(POLES,RES):
        mask=t>=0 if p.real<0 else t<0
        y[mask]+=(1 if p.real<0 else -1)*c*np.exp(p*t[mask])
    return y.real

def target(t):
    base=np.tanh(q(-t)/.002)
    # Both branches are negative near zero; flatten there before adding a smooth spike.
    a=np.clip((abs(t)-.3)/.1,0,1);blend=a*a*a*(10-15*a+6*a*a)
    base=-1+blend*(base+1)
    frequency=2*np.pi*np.fft.rfftfreq(len(t),t[1]-t[0])
    base=np.fft.irfft(np.fft.rfft(base)*np.exp(-.5*(.05*frequency)**2),len(t))
    base=np.clip(base,-1,1)
    spike=np.exp(-(t/SIGMA)**2)
    y=base+(1-base)*spike
    taper=np.sin(np.pi/2*np.clip((SUPPORT-abs(t))/10,0,1))**4
    return y*taper

def forward(f,step,z):
    tt=np.arange(int(round(TAIL/step))+1)*step
    beta=W*np.sqrt(1-z*z)
    h=np.zeros(len(tt))
    for j in range(2):
        pole=-z*W[j]+1j*beta[j]
        x=pole*step/2
        weight=step*(np.sinh(x)/x)**2
        term=R[j]*np.imag(np.exp(pole*tt)*weight)/beta[j]
        half=step*sum((pole*step)**n/math.factorial(n+2) for n in range(18))
        term[0]=R[j]*half.imag/beta[j]
        h+=term
    length=len(f)+len(h)-1;size=1<<(length-1).bit_length()
    y=np.fft.irfft(np.fft.rfft(f,size)*np.fft.rfft(h,size),size)[:length]
    i=int(np.argmax(abs(y)))
    # f is interpreted by linear interpolation and is bounded by one.
    tailbound=2*CUT*sum(abs(R[j])/beta[j]*np.exp(-z*W[j]*TAIL) for j in range(2))
    return y,float(abs(y[i])),float(i*step),float(tailbound)

def main():
    started=time.perf_counter();OUT.mkdir(exist_ok=True)
    tpos=np.arange(0,400.0001,.002)
    qpos=sum(c*np.exp(p*tpos) for p,c in zip(POLES,RES) if p.real<0).real
    anti=sum(abs(c)/p.real for p,c in zip(POLES,RES) if p.real>0)
    tv=1+float(np.trapezoid(abs(qpos),tpos))+float(anti)
    invpoly,invrem=np.polydiv(np.polymul(D(Z0,0),D(Z0,1)),N(Z0))
    invp=np.roots(N(Z0));invr=np.polyval(invrem,invp)/np.polyval(np.polyder(N(Z0)),invp)
    rows=[];saved=None
    for power in [18,19,20]:
        count=2**power;step=PERIOD/count
        t=(np.arange(count)-count//2)*step
        desired=target(t)
        freq=2*np.pi*np.fft.rfftfreq(count,step)
        inverse=np.fft.irfft(np.fft.rfft(desired)/H(1j*freq,Z0),count)
        keep=abs(t)<=CUT
        tf=t[keep];f=inverse[keep]
        window=np.sin(np.pi/2*np.clip((CUT-abs(tf))/RAMP,0,1))**4
        cutf=f*window
        scale=float(max(abs(cutf)));cutf=cutf/scale
        y0,p0,at0,b0=forward(cutf,step,Z0);y1,p1,at1,b1=forward(cutf,step,Z1)
        omission=sum(abs(c)/abs(p)**2*np.exp(-abs(p)*(CUT-RAMP-SUPPORT)) for p,c in zip(invp,invr))
        actual_taper_error=float(np.sum(abs(f-f*window))*step/scale)
        outside=float(np.sum(abs(inverse[abs(t)>CUT]))*step/scale)
        input_l1=float(np.trapezoid(abs(cutf),dx=step))
        row={'power':power,'dt_s':step,'input_samples':len(cutf),'input_duration_s':2*CUT,
             'normalizing_scale':scale,'max_abs_input':float(max(abs(cutf))),'input_l1':input_l1,
             'complete_P0':p0,'complete_P1':p1,'complete_ratio':p1/p0,
             'baseline_peak_time_s':at0,'new_peak_time_s':at1,
             'baseline_peak_after_input_ends':bool(at0>2*CUT),'new_peak_after_input_ends':bool(at1>2*CUT),
             'tail0_bound_after_input_plus_900':b0,'tail1_bound_after_input_plus_900':b1,
             'inverse_taper_and_omission_numeric_l1':actual_taper_error+outside,
             'ideal_inverse_truncation_l1_bound_unnormalized':float(omission),
             'generation_outer_edge_input_abs':float(max(abs(inverse[:100]).max(),abs(inverse[-100:]).max())/scale)}
        rows.append(row);print(json.dumps(row),flush=True)
        if power==20:
            saved=(tf+CUT,cutf,y0,y1,step)
    with (OUT/'complete_peak_comparison.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    ti,f,y0,y1,step=saved
    # The actual normalized finite input is the saved witness; no output-based rescaling.
    np.savez_compressed(OUT/'finite_input_witness.npz',t=ti,input=f)
    with (OUT/'witness_trace_decimated.csv').open('w',encoding='utf-8-sig',newline='') as file:
        writer=csv.writer(file);writer.writerow(['t_s','input','baseline_y','new_y'])
        for i in range(0,len(y0),256):
            writer.writerow([i*step,float(f[i]) if i<len(f) else 0.,float(y0[i]),float(y1[i])])
    convergence=max(row['complete_ratio'] for row in rows)-min(row['complete_ratio'] for row in rows)
    checks={'Q_TV_above_kappa_only_used_as_guide':tv>1.6,
            'same_unit_amplitude_compact_input_for_both_states':all(abs(row['max_abs_input']-1)<1e-14 for row in rows),
            'all_forward_complete_ratios_above_1p6':all(row['complete_ratio']>1.6 for row in rows),
            'all_forward_complete_ratios_below_B21p25':all(row['complete_ratio']<21.25 for row in rows),
            'ratio_grid_range_below_1e-3':convergence<1e-3,
            'analytic_remaining_tails_below_1e-10_of_baseline_peak':all(max(row['tail0_bound_after_input_plus_900'],row['tail1_bound_after_input_plus_900'])<1e-10*row['complete_P0'] for row in rows),
            'input_endpoints_zero':float(f[0])==0 and float(f[-1])==0,
            'elapsed_below_300_seconds':time.perf_counter()-started<300}
    result={'evidence_id':'E-EXP-004','finished_utc':datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds':time.perf_counter()-started,'code_sha256':sha(__file__),
            'params':{'omega':W.tolist(),'residues':R.tolist(),'zeta0':Z0,'zeta1':Z1,
                      'target_support':[-SUPPORT,SUPPORT],'target_positive_spike_sigma':SIGMA,
                      'input_support':[0,2*CUT],'input_taper_width':RAMP,'zero_initial':True,
                      'same_input_both_states':True,'tail_after_input':TAIL,'generation_period':PERIOD,
                      'target_sign_tanh_scale':.002,'target_base_gaussian_sigma':.05,
                      'forward_method':'Exact modal convolution weights for piecewise linear saved input; FFT only performs linear discrete convolution'},
            'Q_TV_numeric':tv,'inverse_polynomial':invpoly.tolist(),
            'inverse_poles':invp.tolist(),'inverse_residues':invr.tolist(),'runs':rows,
            'ratio_absolute_grid_range':convergence,'checks':checks,
            'witness_sha256':sha(OUT/'finite_input_witness.npz'),
            'limits':'Finite saved input, causal zero-initial forward convolution and complete free-tail checks. FFT quadrature is numerical, not a certified continuous-time extremum proof; ratio convergence and tail bounds supplied. Synthetic fixed real-residue output, not engineering shear.'}
    (OUT/'complete_peak_witness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'checks':checks,'elapsed_seconds':result['elapsed_seconds'],'grid_range':convergence},ensure_ascii=False,indent=2))
    assert all(checks.values())

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
