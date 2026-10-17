"""Fixed physical unit topcut: six predefined sin-squared envelopes, exact modal formulas."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,platform,sys,time
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/'round010_unit_topcut_envelopes'
TOPIC=HERE.parent
TS=[20.,40.,80.,160.,320.,640.]
DT=.01;TAIL=300.
K=np.array([[2.,-1.,0.],[-1.,2.,-1.],[0.,-1.,1.]])
b=np.ones(3);ell=np.array([0.,-1.,1.])

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def savecsv(name,rows):
    with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def main():
    start=time.perf_counter();OUT.mkdir(exist_ok=True)
    lam,phi=np.linalg.eigh(K)
    gamma=phi.T@b;phi=phi*np.where(gamma<0,-1.,1.);gamma=phi.T@b
    omega=np.sqrt(lam);rho=(ell@phi)*gamma
    S=float(sum(omega));D=float(np.prod([omega[0]+omega[1],omega[0]+omega[2],omega[1]+omega[2]]))
    z0=np.sqrt(D/(4*S**3));z1=1.6*z0
    H=lambda z:sum(rho/(lam-S*S+2j*z*omega*S))
    h0,h1=H(z0),H(z1);argument=float(np.angle(h1))
    Cunit=2*(phi*omega)@phi.T
    network=[]
    for i in range(3):network.append({'kind':'ground','nodes':f'{i+1}-reference','unit_zeta_coefficient':float(sum(Cunit[i]))})
    for i,j in [(0,1),(0,2),(1,2)]:network.append({'kind':'inter_node','nodes':f'{i+1}-{j+1}','unit_zeta_coefficient':float(-Cunit[i,j])})
    def calculate(T,step,keep=False):
        t=np.arange(int(round(2*T/step))+1)*step
        frequencies=np.array([S,S+np.pi/T,S-np.pi/T]);weights=np.array([.5,-.25,-.25])
        E=np.exp(1j*t[:,None]*frequencies[None,:]);phase=np.exp(-1j*(S*T+argument))
        f=np.sin(np.pi*t/(2*T))**2*np.cos(S*(t-T)-argument);f[0]=f[-1]=0.
        decomposition_error=float(np.max(abs(f-(E@weights*phase).real)))
        tau=np.arange(int(round(TAIL/step))+1)*step
        states=[];ys=[]
        for zeta in [z0,z1]:
            alpha=zeta*omega;beta=omega*np.sqrt(1-zeta*zeta)
            q=np.empty((len(t),3));v=np.empty_like(q)
            for i in range(3):
                den=lam[i]-frequencies**2+2j*alpha[i]*frequencies
                aa=sum(weights/den);bb=sum(weights*(alpha[i]+1j*frequencies)/(beta[i]*den))
                decay=np.exp(-alpha[i]*t);cos=np.cos(beta[i]*t);sin=np.sin(beta[i]*t)
                q[:,i]=(phase*(E@(weights/den)-decay*(aa*cos+bb*sin))).real
                v[:,i]=(phase*(E@(weights*1j*frequencies/den)-decay*((-alpha[i]*aa+beta[i]*bb)*cos+(-beta[i]*aa-alpha[i]*bb)*sin))).real
            q[0]=0.;v[0]=0.
            ypre=q@rho
            qt,vt=q[-1].copy(),v[-1].copy()
            tail_modes=np.exp(-tau[:,None]*alpha)*(qt*np.cos(tau[:,None]*beta)+(vt+alpha*qt)/beta*np.sin(tau[:,None]*beta))
            ytail=tail_modes@rho
            y=np.r_[ypre,ytail[1:]];tt=np.r_[t,2*T+tau[1:]]
            index=int(np.argmax(abs(y)));amp=abs(rho)*np.sqrt(qt*qt+((vt+alpha*qt)/beta)**2)
            remainder=float(sum(amp*np.exp(-alpha*TAIL)))
            states.append({'zeta':float(zeta),'sampled_peak':float(abs(y[index])),'signed_peak':float(y[index]),
                           'peak_time_s':float(tt[index]),'peak_region':'input' if tt[index]<=2*T else 'free_tail',
                           'tail_sampled_peak':float(max(abs(ytail))),'remaining_tail_bound':remainder,
                           'end_scalar_modal_q':qt.tolist(),'end_scalar_modal_v':vt.tolist()})
            ys.append(y)
        row={'T_s':T,'input_support_s':2*T,'dt_s':step,'sampled_P0':states[0]['sampled_peak'],
             't_P0_s':states[0]['peak_time_s'],'signed_P0':states[0]['signed_peak'],
             'sampled_P1':states[1]['sampled_peak'],'t_P1_s':states[1]['peak_time_s'],'signed_P1':states[1]['signed_peak'],
             'sampled_peak_ratio':states[1]['sampled_peak']/states[0]['sampled_peak'],
             'sampled_max_abs_input':float(max(abs(f))),'remaining_tail0_bound':states[0]['remaining_tail_bound'],
             'remaining_tail1_bound':states[1]['remaining_tail_bound'],'three_frequency_decomposition_max_error':decomposition_error}
        if keep:
            force=np.r_[f,np.zeros(len(tau)-1)]
            savecsv('T640_display_trace.csv',[{'t_s':float(tt[i]),'input_f_minus_a':float(force[i]),
                    'baseline_topcut':float(ys[0][i]),'new_topcut':float(ys[1][i]),'in_input_support':bool(tt[i]<=2*T)}
                    for i in range(0,len(tt),20)])
        return row,states
    rows=[];allstates=[]
    for T in TS:
        row,states=calculate(T,DT,keep=T==640.)
        rows.append(row);allstates.append({'T_s':T,'states':states});print(json.dumps(row),flush=True)
    fine,finestates=calculate(640.,.005)
    coarse=rows[-1]
    sensitivity={key:abs(fine[key]/coarse[key]-1) for key in ['sampled_P0','sampled_P1','sampled_peak_ratio']}
    savecsv('six_envelope_sampled_peaks.csv',rows)
    checks={'physical_rho_from_fixed_ell_phi_gamma':bool(np.max(abs(phi.T@phi-np.eye(3)))<1e-12 and abs(sum(rho))<1e-12 and abs(sum(lam*rho))<1e-12 and abs(sum(lam*lam*rho)-1)<1e-12),
            'baseline_frequency_zero_numerically_consistent_only':abs(h0)<1e-14,
            'new_frequency_response_nonzero':abs(h1)>1e-4,
            'specified_damping_levels_and_underdamped':bool(.26<z0<.261 and .417<z1<.418 and z1<1),
            'network_has_six_positive_coefficients_including_13_and_ground':all(x['unit_zeta_coefficient']>0 for x in network),
            'added_classical_C_positive_definite':bool(np.linalg.eigvalsh((z1-z0)*Cunit).min()>0),
            'input_max_abs_at_most_one_no_rescaling':all(row['sampled_max_abs_input']<=1+1e-13 for row in rows+[fine]),
            'three_frequency_identity_below_1e-10':all(row['three_frequency_decomposition_max_error']<1e-10 for row in rows+[fine]),
            'remaining_tail_below_1e-10_of_sampled_P0':all(max(row['remaining_tail0_bound'],row['remaining_tail1_bound'])<1e-10*row['sampled_P0'] for row in rows+[fine]),
            'fixed_T640_sampling_change_below_1e-3':max(sensitivity.values())<1e-3,
            'runtime_below_300_seconds':time.perf_counter()-start<300}
    sources=[TOPIC/'research/roles/ideation/round-008.md',TOPIC/'research/roles/verification/round-011.md',HERE/'round009_viscous_network/network_realization.json']
    result={'evidence_id':'E-EXP-010','finished_utc':datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds':time.perf_counter()-start,'code_sha256':sha(__file__),'python':platform.python_version(),'numpy':np.__version__,
            'sources':[{'path':str(p),'sha256':sha(p)} for p in sources],
            'params':{'M':np.eye(3).tolist(),'K':K.tolist(),'b':b.tolist(),'ell':ell.tolist(),'omega':omega.tolist(),
                      'Gamma':gamma.tolist(),'rho_for_f_minus_a':rho.tolist(),'S_Omega_star':S,'D_pair_sum_product':D,
                      'zeta0':float(z0),'zeta1':float(z1),'kappa':1.6,'T_values':TS,'dt':DT,'tail_after_input':TAIL,
                      'H1_phase':argument,'input':'sin^2(pi*t/(2T))*cos(S*(t-T)-arg H1(iS)) on [0,2T]; f=-a, same input in both states, zero initial; no normalization',
                      'units':'Consistent synthetic unit model; no engineering unit mapping'},
            'raw_double_H0_at_iS':[h0.real,h0.imag],'H1_at_iS':[h1.real,h1.imag],
            'baseline_zero_basis':'Exact algebraic definitions and I009/V011; small numerical residual is only a consistency check. No rho or response term was manually altered to force a zero.',
            'network_per_unit_zeta':network,'C0':(z0*Cunit).tolist(),'C1':(z1*Cunit).tolist(),
            'six_sampled_peak_rows':rows,'end_state_and_tail_checks':allstates,'T640_finer_row':fine,'T640_finer_states':finestates,
            'T640_relative_sampling_changes':sensitivity,'display_trace_dt':.2,'checks':{k:bool(v) for k,v in checks.items()},
            'limits':'Sampled peaks over full input plus 300s tail, with remaining analytic tail envelopes; not certified continuous-time extrema. Six values do not prove unboundedness; I009/V011 supplies the separate analytic argument. zeta is about .2607 to .4171, not .05 to .08.'}
    (OUT/'unit_topcut_envelope_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'checks':result['checks'],'T640_relative_sampling_changes':sensitivity,'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
    assert all(checks.values())

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
