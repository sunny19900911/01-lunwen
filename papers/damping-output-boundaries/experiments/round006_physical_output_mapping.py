"""One frozen three-storey model: signed modal output map and moment identities.

Only small matrices; no frequency scan, response run, parameter search or ETABS.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv,hashlib,json,platform,sys,time
import numpy as np

HERE=Path(__file__).resolve().parent
OUT=HERE/'round006_model_mapping'
TOPIC=HERE.parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    start=time.perf_counter();OUT.mkdir(exist_ok=True)
    sources=[HERE/'round002/frequency_refinement.json',HERE/'round002/extended_frequency_check.json',
             TOPIC/'research/roles/ideation/round-006.md']
    frozen=json.loads(sources[0].read_text(encoding='utf-8'))['model']
    M=np.array(frozen['M']);K=np.array(frozen['K']);k=np.array(frozen['stiffness'])
    b=np.ones(3);ell=k[2]*np.array([0.,-1.,1.])
    mass_scale=np.diag(1/np.sqrt(np.diag(M)))
    lam,Q=np.linalg.eigh(mass_scale@K@mass_scale)
    phi=mass_scale@Q
    gamma=phi.T@M@b
    phase=np.where(gamma<0,-1.,1.)
    phi=phi*phase
    gamma=phi.T@M@b
    projection=ell@phi
    rho=projection*gamma
    actual_a_residue=-rho
    rows=[{'mode':i+1,'lambda_omega_squared':float(lam[i]),'omega_rad_s':float(np.sqrt(lam[i])),
           'Gamma_f_minus_a':float(gamma[i]),'ell_T_phi':float(projection[i]),
           'rho_for_f_minus_a':float(rho[i]),'r_for_actual_a':float(-rho[i])} for i in range(3)]
    with (OUT/'signed_modal_map.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    moments=[]
    for name,power,rhs,expected in [
        ('mu0',0,float(ell@b),0.),
        ('mu1',1,float(ell@np.linalg.solve(M,K@b)),0.),
        ('mu_minus1',-1,float(ell@np.linalg.solve(K,M@b)),float(np.diag(M)[2]))]:
        terms=lam**power*rho
        lhs=float(sum(terms))
        moments.append({'name':name,'lambda_power':power,'modal_terms':terms.tolist(),'spectral_sum':lhs,
                        'direct_matrix_rhs':rhs,'physical_expected':expected,'abs_difference':abs(lhs-rhs),
                        'scaled_error':abs(lhs-rhs)/max(float(sum(abs(terms))),abs(rhs),1e-30)})
    # Independent residue reconstruction using the three physical moments only.
    moment_matrix=np.vstack([np.ones(3),lam,1/lam])
    rho_from_moments=np.linalg.solve(moment_matrix,np.array([0.,0.,np.diag(M)[2]]))
    phase_checks=[]
    for signs in [[-1,-1,-1],[-1,1,-1],[1,-1,1]]:
        flipped=phi*np.array(signs)
        rr=(ell@flipped)*(flipped.T@M@b)
        phase_checks.append({'column_signs':signs,'max_rho_change':float(max(abs(rr-rho)))})
    C0=np.array(frozen['C0']);C1=np.array(frozen['C1'])
    classical=[];sign_checks=[]
    for zeta,C in [(.05,C0),(.08,C1)]:
        target=np.diag(2*zeta*np.sqrt(lam))
        classical.append({'zeta':zeta,'phi_T_C_phi_diagonal_error':float(np.max(abs(phi.T@C@phi-target))),
                          'C_min_eigenvalue':float(np.linalg.eigvalsh(C).min()),'C13':float(C[0,2])})
        s=complex(1.,.5)
        hf_direct=ell@np.linalg.solve(s*s*M+s*C+K,M@b)
        hf_modal=sum(rho/(s*s+2*zeta*np.sqrt(lam)*s+lam))
        ha_direct=ell@np.linalg.solve(s*s*M+s*C+K,-M@b)
        sign_checks.append({'zeta':zeta,'test_s':[s.real,s.imag],
                            'Hf_direct':[hf_direct.real,hf_direct.imag],
                            'Hf_modal':[hf_modal.real,hf_modal.imag],
                            'Ha_direct':[ha_direct.real,ha_direct.imag],
                            'modal_direct_absolute_error':float(abs(hf_modal-hf_direct)),
                            'Ha_plus_Hf_absolute_error':float(abs(ha_direct+hf_direct))})
    checks={'complete_mass_orthonormality':bool(np.max(abs(phi.T@M@phi-np.eye(3)))<1e-12),
            'complete_eigen_equations':bool(np.max(abs(K@phi-M@phi@np.diag(lam)))<1e-12),
            'input_reconstructed_from_modes':bool(np.max(abs(phi@gamma-b))<1e-12),
            'physical_moments_match_below_1e-11':all(r['abs_difference']<1e-11 for r in moments),
            'independent_moment_residues_match_below_1e-10':bool(np.max(abs(rho_from_moments-rho))<1e-10),
            'frozen_actual_a_residues_equal_negative_rho':bool(np.max(abs(actual_a_residue-np.array(frozen['residues'])[2]))<1e-12),
            'all_column_sign_flips_leave_rho_unchanged':all(r['max_rho_change']==0 for r in phase_checks),
            'both_C_classical_in_same_mass_basis':all(r['phi_T_C_phi_diagonal_error']<1e-11 for r in classical),
            'C1_is_1p6_times_C0':bool(np.max(abs(C1-1.6*C0))<1e-12),
            'C13_nonzero_excludes_adjacent_story_dashpot_topology':abs(C0[0,2])>1e-4,
            'f_minus_a_sign_independent_matrix_check':all(r['modal_direct_absolute_error']<1e-12 and r['Ha_plus_Hf_absolute_error']==0 for r in sign_checks),
            'runtime_below_600s':time.perf_counter()-start<600}
    checks={key:bool(value) for key,value in checks.items()}
    result={'evidence_id':'E-EXP-006','finished_utc':datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds':time.perf_counter()-start,'python':platform.python_version(),'numpy':np.__version__,
            'code_sha256':sha(__file__),'sources':[{ 'path':str(p),'sha256':sha(p)} for p in sources],
            'model':{'M':M.tolist(),'K':K.tolist(),'b':b.tolist(),'ell_cut3':ell.tolist(),'phi':phi.tolist(),
                     'phase_convention':'Each Gamma positive; rho unchanged by any modal column sign reversal'},
            'equations':{'actual_a':'M u_dd + C u_d + K u = -M b a',
                         'chosen_f':'f=-a, M u_dd + C u_d + K u = M b f',
                         'output':'y=ell^T u=k3*(u3-u2)=(Ku)_3, elastic output only',
                         'rho':'rho_i=(ell^T phi_i)*Gamma_i, Gamma_i=phi_i^T M b',
                         'actual_acceleration_residues':'r_i=-rho_i'},
            'signed_modal_map':rows,'moments':moments,'rho_reconstructed_from_moments':rho_from_moments.tolist(),
            'column_sign_checks':phase_checks,'classical_C_checks':classical,'independent_input_sign_checks':sign_checks,
            'checks':checks,'boundary':'One specified synthetic physical cut and complete three-mode basis. C is classical SPD, but C13 != 0 excludes the same-chain adjacent-story dashpot topology. No mapping from arbitrary residues to engineering sections is asserted.'}
    (OUT/'physical_output_mapping.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'checks':checks,'signed_modal_map':rows,'moments':moments,'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
    assert all(checks.values())

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
