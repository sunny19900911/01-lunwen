"""Small independent FOH challenges only: never open/hash an NPZ or execute source."""
from pathlib import Path
from fractions import Fraction as F
from math import factorial
import cmath,csv,hashlib,json,math
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
BASE=ROOT/'papers/damping-output-boundaries/research/roles'
SRC=BASE/'experiments/maxwell-session004/R019-force-output-replay-prototype'
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def rows(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
s=read(SRC/'summary_r019.json');p=read(SRC/'protocol.json');manifest=read(SRC/'delivery_manifest_r019.json')
for x in manifest['files']:
    r=record(SRC/x['name']);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
assert record(SRC/'replay_given_force_foh.py')['sha256']==s['code_sha256']
assert record(SRC/'protocol.json')['sha256']==s['protocol_sha256']
assert read(SRC/'run_record_r019.json')['summary_sha256']==record(SRC/'summary_r019.json')['sha256']
assert read(SRC/'foh_weight_algebra_checks.json')['checks']==s['FOH_algebra_checks']
coeffrows=rows(SRC/'synthetic_modal_port_target_coefficients.csv')
assert len(coeffrows)==2
for row,mode in zip(coeffrows,s['modal_coefficients']):
    assert row['source_type']==mode['source_type'] and row['mode']==mode['mode']
    assert all(float(row[k])==mode[k] for k in ['omega','zeta','modal_mass','beta','gamma_u1','gamma_u2'])
smallrefs=[Path(x['path']) for key,x in p['refs'].items() if key!='local_cache']
for key,x in p['refs'].items():
    if key!='local_cache':assert record(Path(x['path']))==x
files=list(SRC.iterdir())+smallrefs+[BASE/'ideation/maxwell-session004/R022-force-target-interface/report.md']
files += list((BASE/'verification/maxwell-session004/R030-force-target-interface-review').iterdir())
sources=[record(x) for x in sorted(set(files)) if x.is_file()]
def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def mv(A,x):return [dot(r,x) for r in A]
def mm(A,B):return [[dot(r,c) for c in zip(*B)] for r in A]
I=[[F(1),F(0)],[F(0),F(1)]];b=[F(0),F(1)];h=F(s['dt']);terms=40
def series(A):
    power=I;E=[[F(0),F(0)],[F(0),F(0)]];J0=[F(0),F(0)];J1=[F(0),F(0)]
    for n in range(terms):
        for i in range(2):
            for j in range(2):E[i][j]+=power[i][j]*h**n/factorial(n)
        ab=mv(power,b)
        for i in range(2):
            J0[i]+=ab[i]*h**(n+1)/factorial(n+1)
            J1[i]+=ab[i]*h**(n+1)/factorial(n+2)
        power=mm(power,A)
    r=max(sum(abs(x) for x in row) for row in A)*h
    assert r<1
    e_tail=r**terms/F(factorial(terms))/(1-r/F(terms+1))
    j0_tail=h*r**terms/F(factorial(terms+1))/(1-r/F(terms+2))
    j1_tail=h*r**terms/F(factorial(terms+2))/(1-r/F(terms+3))
    return E,J0,J1,e_tail,j0_tail,j1_tail
results=[]
for check in s['FOH_algebra_checks']:
    assert all(x<=check['arithmetic_tolerance'] for x in check['residuals'].values())
    A=[[F(x) for x in row] for row in check['A']]
    E,J0,J1,et,j0t,j1t=series(A)
    diffE=max(abs(F(check['E'][i][j])-E[i][j])+et for i in range(2) for j in range(2))
    diff0=max(abs(F(x)-y)+j0t for x,y in zip(check['J0'],J0))
    diff1=max(abs(F(x)-y)+j1t for x,y in zip(check['J1'],J1))
    left=[x-y for x,y in zip(J0,J1)]
    pulseleft=max(abs(F(x)-y)+j0t+j1t for x,y in zip(check['W_left'],left))
    pulseright=max(abs(F(x)-y)+j1t for x,y in zip(check['W_right'],J1))
    assert max(diffE,diff0,diff1,pulseleft,pulseright)<F(1,10**11)
    results.append({'mode':check['mode'],'E_difference_upper_float_display':float(diffE),'J0_difference_upper_float_display':float(diff0),'J1_difference_upper_float_display':float(diff1),
       'left_endpoint_pulse_difference_upper_float_display':float(pulseleft),'right_endpoint_pulse_difference_upper_float_display':float(pulseright),'all_exact_differences_below_1e_minus11':True})
# Exact nilpotent state transition: left acceleration pulse has h²/3, right h²/6.
E,J0,J1,*_=series([[F(0),F(1)],[F(0),F(0)]])
assert J0==[h*h/2,h] and J1==[h*h/6,h/2]
assert [J0[i]-J1[i] for i in range(2)]==[h*h/3,h/2]
# Baseline independently via complex harmonic transfer and propagation from (x(T),v(T)).
w=math.sqrt(2);nu=math.sqrt(399/400);a=1/20;T=s['T'];H=1/complex(1-w*w,.1*w)
C=-H.imag;D=(-w*H.real+a*C)/nu
def loading(t):
    z=H*cmath.exp(1j*w*t);xhp=math.exp(-a*t)*((-a*C+nu*D)*math.cos(nu*t)+(-a*D-nu*C)*math.sin(nu*t))
    return z.imag+math.exp(-a*t)*(C*math.cos(nu*t)+D*math.sin(nu*t)),(1j*w*z).imag+xhp
xT,vT=loading(T);snapshots=rows(SRC/'four_fixed_point_replay.csv')
assert [int(x['node_index']) for x in snapshots]==[0,16384,16529,98304]
baseline=[]
for row in snapshots:
    n=int(row['node_index']);t=float(row['time_original_label'])
    if n<=16384:value=loading(t)[0]
    else:
        tau=t-T;value=math.exp(-a*tau)*(xT*math.cos(nu*tau)+(vT+a*xT)/nu*math.sin(nu*tau))
    error=abs(value-float(row['analytic_U_scalar']));assert error<1e-12
    baseline.append({'node':n,'independent_U_difference':error})
    for target in [1,2]:
        pred=F(float(row['analytic_U_scalar']))+F(float(row[f'u{target}_device_delta_plus']))+F(float(row[f'u{target}_device_delta_minus']))
        assert abs(pred-F(float(row[f'u{target}_D_replay'])))<F(1,10**13)
        err=F(float(row[f'u{target}_D_replay']))-F(float(row[f'u{target}_D_cache']))
        assert abs(err-F(float(row[f'u{target}_error_pred_minus_cache'])))<F(1,10**13)
for x in s['whole_window_error_metrics'].values():
    assert 0<=x['RMS_error']<=x['maximum_abs_error']<.01
    assert x['max_error_below_point01'] and x['fixed_diagnostic_threshold']==.01
    witness=x['maximum_error_witness']
    assert abs(witness['signed_error'])==x['maximum_abs_error']
    assert abs((witness['prediction']-witness['cached_D'])-witness['signed_error'])<1e-13
assert s['N']==16384 and s['window_end']==float(snapshots[-1]['time_original_label'])
assert s['force_window_scope']['last_recorded_F']==float(snapshots[-1]['F_given_signed'])!=0
for x in sources:assert record(Path(x['path']))==x
write(HERE/'source-freeze.json',{'verified_small_sources':sources,'explicitly_not_opened_or_hashed':p['refs']['local_cache']})
out={'required_changes':0,'scope':'Two rounded 2x2 FOH operators, exact nilpotent endpoint pulses, four scalar baseline/snapshot consistency checks, and small-file identities only.',
 'independent_method':'Exact Fraction 40-term matrix/integrated-power series with rational infinity-norm tail majorants for frozen rounded A/h; no source-code execution or numpy import.',
 'rounded_operator_weight_challenges':results,'exact_left_right_pulse_orientation_passed':True,'baseline_complex_transfer_and_cutoff_state_propagation':baseline,
 'four_fixed_snapshot_scalar_assembly_passed':True,'recorded_summary_error_gate_consistency_passed':True,'recomputed_whole_window_max_or_RMS':False,
 'NPZ_read_decode_or_rehash':False,'nonlinear_ODE_or_author_replay_executed':False,'full98305_data_certified':False,
 'matrix_series_scope':'Rational tail checks concern these two frozen rounded low-dimensional operators only; they do not certify exact-model parameter rounding, input interpolation, recursive whole-window error, or original D accuracy.',
 'small_source_count':len(sources),'small_sources_unchanged':True,'unknown_force_tail_not_extended':True}
write(HERE/'checks.json',out)
print(json.dumps(out,indent=2))
