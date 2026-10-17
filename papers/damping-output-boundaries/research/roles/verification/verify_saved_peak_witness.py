"""Audit a frozen piecewise-linear input using non-FFT complex recurrence."""
from pathlib import Path
from datetime import datetime, timezone
import cmath, hashlib, json, math, platform, time
import numpy as np

HERE=Path(__file__).resolve().parent
EXP=HERE.parents[2]/'experiments/round004'
EXPECTED='e1bacdc2938750250eb829c54357eba17e4d3bee8694cc33a18f65c7647d859e'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def coefficients(p,h):
    z=p*h; term=z; em1=z; rem=0j
    for j in range(2,19):
        term*=z/j; em1+=term; rem+=term
    return cmath.exp(z),em1/p,rem/(h*p*p)

def state_run(values,h,zeta,tail_duration):
    ws=(1.,3.); rs=(1.,-8.9)
    bs=[w*math.sqrt(1-zeta*zeta) for w in ws]
    ps=[complex(-zeta*w,b) for w,b in zip(ws,bs)]
    (e0,a0,b0),(e1,a1,b1)=[coefficients(p,h) for p in ps]
    x0=x1=0j; peak=0.; peak_index=0
    for j in range(len(values)-1):
        v=values[j]; delta=values[j+1]-v
        x0=e0*x0+a0*v+b0*delta
        x1=e1*x1+a1*v+b1*delta
        y=rs[0]*x0.imag/bs[0]+rs[1]*x1.imag/bs[1]
        if abs(y)>peak: peak=abs(y); peak_index=j+1
    tau=np.arange(int(round(tail_duration/h))+1)*h
    tail=rs[0]/bs[0]*np.imag(x0*np.exp(ps[0]*tau))+rs[1]/bs[1]*np.imag(x1*np.exp(ps[1]*tau))
    ti=int(np.argmax(np.abs(tail))); tp=float(abs(tail[ti]))
    duration=(len(values)-1)*h
    bound=sum(abs(r)*abs(x)/b*math.exp(-zeta*w*tail_duration) for r,x,b,w in zip(rs,[x0,x1],bs,ws))
    universal=duration*sum(abs(r)/b*math.exp(-zeta*w*tail_duration) for r,b,w in zip(rs,bs,ws))
    return {'zeta':zeta,'zero_initial_complex_states':[[0.,0.],[0.,0.]],
            'active_sample_peak':peak,'active_sample_peak_time':peak_index*h,
            'tail_sample_peak':tp,'tail_sample_peak_time':duration+ti*h,
            'complete_sample_peak':max(peak,tp),'complete_sample_peak_time':peak_index*h if peak>=tp else duration+ti*h,
            'tail_duration':tail_duration,'tail_samples':len(tau),
            'remaining_tail_bound_from_final_states':bound,'remaining_tail_bound_from_input_duration':universal,
            'final_complex_states':[[x0.real,x0.imag],[x1.real,x1.imag]]}

def main():
    start=time.perf_counter(); inp=EXP/'finite_input_witness.npz'
    assert sha(inp)==EXPECTED
    with np.load(inp,allow_pickle=False) as data:
        t=data['t'].copy(); f=data['input'].copy()
    h=float(t[1]-t[0]); f.flags.writeable=False
    assert len(t)==len(f) and np.all(np.isfinite(f))
    assert t[0]==0. and t[-1]==600. and np.max(abs(np.diff(t)-h))==0.
    assert f[0]==0. and f[-1]==0. and float(np.max(abs(f)))==1.
    values=f.tolist()
    states=[state_run(values,h,z,900.) for z in [.05,.08]]
    reference=json.loads((EXP/'complete_peak_witness.json').read_text(encoding='utf-8'))['runs'][-1]
    ratio=states[1]['complete_sample_peak']/states[0]['complete_sample_peak']
    out={'evidence_id':'E-EXP-004-independent-saved-input-audit',
         'finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-start,
         'python':platform.python_version(),'numpy':np.__version__,'script_sha256':sha(__file__),
         'input_sha256':sha(inp),'input_samples':len(f),'input_dt':h,'support':[float(t[0]),float(t[-1])],
         'endpoint_values':[float(f[0]),float(f[-1])],'max_abs_input':float(np.max(abs(f))),
         'same_readonly_saved_input_both_states':True,'method':'Zero-initial piecewise-linear exact exponential recurrence; no FFT and no construction script import.',
         'states':states,'complete_sample_ratio':ratio,'reference_ratio':reference['complete_ratio'],
         'ratio_absolute_difference':abs(ratio-reference['complete_ratio']),
         'checks':{'input_sha_matches':sha(inp)==EXPECTED,'ratio_above_1p6':ratio>1.6,
                   'ratio_below_6p7375':ratio<6.7375,'reference_ratio_difference_below_1e-8':abs(ratio-reference['complete_ratio'])<1e-8,
                   'remaining_tail_smaller_than_peaks':all(s['remaining_tail_bound_from_input_duration']<1e-12*s['complete_sample_peak'] for s in states)},
         'limits':['Sample peaks are not continuous-time extrema certification.','Exact recurrence means exact piecewise-linear formula evaluated in float64, not exact arithmetic.','One frozen synthetic input and output; no engineering interpretation or search.']}
    assert all(out['checks'].values())
    (HERE/'saved-peak-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
