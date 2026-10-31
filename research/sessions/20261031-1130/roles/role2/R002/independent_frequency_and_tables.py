import os
os.environ['OPENBLAS_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np

O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130'
D6=S/'roles/role6/R001';ROOT=S/'root-R001-physical-three-floor'
START=datetime.fromisoformat('2026-10-31T11:49:25+08:00');DEADLINE=START+timedelta(minutes=10)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate():
    if now()>=DEADLINE:raise RuntimeError('R002 deadline')
def save(n,obj):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def writecsv(n,rs):
    with (O/n).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def readcsv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
gate();freeze6=json.loads((D6/'freeze.json').read_text(encoding='utf-8'))
for name,e in freeze6['files'].items():
    p=D6/name;assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
rootmanifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
for e in rootmanifest['outputs']:
    p=ROOT/e['name'];assert p.stat().st_size==e['bytes'] and sha(p)==e['sha256']
save('input-freeze.json',{'started':START.isoformat(),'deadline':DEADLINE.isoformat(),'role6_freeze_sha256':sha(D6/'freeze.json'),'root_manifest_sha256':sha(ROOT/'manifest.json'),'source_code_imported':False,'old_arrays_read':False})
# Route A: physical 2x2 dynamic stiffness; square root from the exact Cayley-Hamilton identity.
M=np.eye(2);K=np.array([[2.,-1.],[-1.,1.]]);sqrtK=(K+np.eye(2))/np.sqrt(5.)
assert np.allclose(sqrtK@sqrtK,K,rtol=0,atol=1e-14)
assert min(np.linalg.eigvalsh(M))>0 and min(np.linalg.eigvalsh(K))>0
# Route B: independently projected modal equations, output the actual first spring force k1*u1.
lam,Phi=np.linalg.eigh(K);omega=np.sqrt(lam);r=np.ones(2);Gamma=Phi.T@M@r
B=(Phi[0,:]*Gamma)/lam
assert np.allclose(B,Gamma**2,rtol=1e-13,atol=1e-14)
Omega=np.sqrt(2.);out=[];complex_values={}
target=json.loads((D6/'two-mode-counterexample.json').read_text(encoding='utf-8'))
for zeta in (.05,.08):
    gate();damping=2*zeta*sqrtK
    assert min(np.linalg.eigvalsh(damping))>0
    displacement=np.linalg.solve(K-Omega**2*M+1j*Omega*damping,-M@r)
    modal_terms=-(Phi[0,:]*Gamma)/(lam-Omega**2+1j*2*zeta*omega*Omega)
    amplitudes=abs(modal_terms);U=float(sum(amplitudes));P=float(abs(displacement[0]));C=P/U
    modalerror=float(abs(sum(modal_terms)-displacement[0]))
    formula=(72/5)*zeta**2/(1+56*zeta**2+64*zeta**4)
    assert modalerror<1e-13 and abs(P*P-formula)<1e-13
    assert 0<C<1
    ref=next(x for x in target['rows'] if x['zeta']==zeta)
    for a,b in [(U,ref['U_N']),(P,ref['P_N']),(C,ref['C']),*zip(amplitudes,ref['modal_abs_peak_N'])]:assert abs(a-b)<1e-12
    out.append({'zeta':zeta,'mode1_peak_N':float(amplitudes[0]),'mode2_peak_N':float(amplitudes[1]),'U_N':U,'P_N':P,'combination_C':C,'P_squared_direct':P*P,'P_squared_formula':formula,'direct_vs_modal_abs_error_N':modalerror,'min_damping_eigenvalue':float(min(np.linalg.eigvalsh(damping))),'steady_u1_at_t0':float(displacement[0].imag),'steady_u2_at_t0':float(displacement[1].imag),'steady_v1_at_t0':float(Omega*displacement[0].real),'steady_v2_at_t0':float(Omega*displacement[1].real)})
    complex_values[str(zeta)]={'physical_displacement_amplitude':[[float(v.real),float(v.imag)] for v in displacement],'modal_first_spring_force_amplitudes':[[float(v.real),float(v.imag)] for v in modal_terms]}
writecsv('independent-two-layer-steady-2.csv',out)
assert all(out[1][k]<out[0][k] for k in ('mode1_peak_N','mode2_peak_N','U_N')) and out[1]['P_N']>out[0]['P_N']
ratios={'U8_over_U5':out[1]['U_N']/out[0]['U_N'],'P8_over_P5':out[1]['P_N']/out[0]['P_N'],'C8_over_C5':out[1]['combination_C']/out[0]['combination_C']}
for k,v in ratios.items():assert abs(v-target[k])<1e-12
assert abs(ratios['P8_over_P5']-ratios['U8_over_U5']*ratios['C8_over_C5'])<1e-14
save('two-layer-checks.json',{'completed':now().isoformat(),'M':M.tolist(),'K':K.tolist(),'sqrtK_exact_expression':'(K+I)/sqrt(5)','omega':omega.tolist(),'B_base_kg':B.tolist(),'ratios':ratios,'complex_values':complex_values,'min_added_damping_eigenvalue':float(min(np.linalg.eigvalsh(.06*sqrtK))),'P_squared_derivation':'t=2*zeta*sqrt(2/5); u1_hat=3*i*t/(1+5*t^2+5*i*t); abs(u1_hat)^2=9*t^2/(1+35*t^2+25*t^4)','derivative_sign':'d(P^2)/d(zeta)=(144/5)*zeta*(1-64*zeta^4)/(1+56*zeta^2+64*zeta^4)^2 >0 for 0<zeta<1/sqrt(8)','initial_state':'sin input steady solution u(0)=Im(u_hat), v(0)=Omega*Re(u_hat), generally nonzero; no zero-initial finite-input claim','output':'first story spring force k1*u1, k1=1 N/m','role6_formula_and_values_pass':True})
gate()
# Root physical coefficient audit: read only the old 2273-byte parameter JSON, never its npz or code.
meta=json.loads((ROOT/'results.json').read_text(encoding='utf-8'))
entry=next(e for e in meta['inputs'] if e['path'].endswith('passive_local_counterexample.json'))
p=Path(entry['path']);assert p.stat().st_size==entry['bytes'] and sha(p)==entry['sha256']
old=json.loads(p.read_text(encoding='utf-8'));M3=np.array(old['M']);K3=np.array(old['K'])
assert np.allclose(M3,np.diag(np.diag(M3)))
inv=np.diag(1/np.sqrt(np.diag(M3)));l3,u3=np.linalg.eigh(inv@K3@inv);phi3=inv@u3
assert np.linalg.norm(K3@phi3-M3@phi3@np.diag(l3))<1e-13
lookup={(int(x['floor']),int(x['mode'])):x for x in readcsv(ROOT/'physical-coefficients-9.csv')};coeff=[]
for floor in (1,2,3):
    a=np.array([float(i>=floor-1) for i in range(3)])
    for mode in (1,2,3):
        v=phi3[:,mode-1];mr=float(v@M3@v);st=float(np.ones(3)@M3@v);ss=float(a@M3@v);g=st/mr;meff=st*st/mr
        bi=meff*ss/st;be=float(a@K3@v*g/l3[mode-1]);ref=lookup[floor,mode]
        assert abs(bi-float(ref['direct_B']))<1e-12 and abs(be-float(ref['K_recovery_B']))<1e-12
        coeff.append({'floor':floor,'mode':mode,'independent_omega':float(np.sqrt(l3[mode-1])),'independent_B_ratio':bi,'independent_B_K':be,'root_B_ratio':float(ref['direct_B']),'root_B_K':float(ref['K_recovery_B']),'max_abs_difference':max(abs(bi-float(ref['direct_B'])),abs(be-float(ref['K_recovery_B'])),abs(bi-be))})
writecsv('root-coefficients-independent-9.csv',coeff)
modal=readcsv(ROOT/'modal-output-peaks-18.csv');peaks={(int(x['floor']),float(x['zeta'])):x for x in readcsv(ROOT/'reconstruction-and-peak-6.csv')}
refs={int(x['floor']):x for x in readcsv(ROOT/'amplitude-and-combination-ratios-3.csv')};rr=[]
for floor in (1,2,3):
    vals={}
    for z in (.05,.08):
        pr=peaks[floor,z];U=sum(float(x['actual_modal_output_peak']) for x in modal if int(x['floor'])==floor and float(x['zeta'])==z);P=float(pr['peak']);C=P/U
        assert abs(U-float(pr['independent_modal_peak_sum_U']))<1e-13 and abs(C-float(pr['peak_combination_factor_C']))<1e-13
        vals[z]=(P,U,C)
    rp,ru,rc=[vals[.08][i]/vals[.05][i] for i in range(3)];ref=refs[floor]
    for x,k in [(rp,'P8_over_P5'),(ru,'U8_over_U5'),(rc,'C8_over_C5')]:assert abs(x-float(ref[k]))<1e-13
    assert abs(rp-ru*rc)<1e-13
    rr.append({'floor':floor,'P8_over_P5':rp,'U8_over_U5':ru,'C8_over_C5':rc,'identity_error':rp-ru*rc})
writecsv('root-ratio-identities-3.csv',rr)
save('checks.json',{'completed':now().isoformat(),'two_layer_states':2,'physical_direct_and_modal_routes_pass':True,'passive_M_K_and_damping':True,'role6_method_verdict':'conditional pass; guards for finite truncation, U=0, baseline P=0/C=0, spectral envelopes retained','root_coefficient_rows':9,'root_coefficient_max_abs_difference':max(x['max_abs_difference'] for x in coeff),'root_ratio_rows':3,'root_scalar_U_C_rows':6,'must_count':0,'source_scripts_imported':False,'time_integration_or_fit':False,'old_120001_array_read':False,'raw_extrema_or_full_reconstruction_independently_reverified':False})
print(json.dumps(json.loads((O/'checks.json').read_text(encoding='utf-8')),ensure_ascii=False))
