"""Single prescribed unit three-storey model: passive viscous-network decomposition."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,platform,sys,time
import numpy as np

OUT=Path(__file__).resolve().parent/'round009_viscous_network'
M=np.eye(3)
K=np.array([[2.,-1.,0.],[-1.,2.,-1.],[0.,-1.,1.]])

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    started=time.perf_counter();OUT.mkdir(exist_ok=True)
    lam,Q=np.linalg.eigh(K)
    sqrtK=(Q*np.sqrt(lam))@Q.T
    C=2*sqrtK
    ground=C@np.ones(3)
    reconstruction=np.diag(ground)
    coefficients=[]
    for i in range(3):
        coefficients.append({'kind':'ground','nodes':f'{i+1}-reference','coefficient_per_zeta':float(ground[i]),
                             'formula':f'g{i+1}=(C_unit*1)_{i+1}','strictly_positive':bool(ground[i]>0)})
    for i,j in [(0,1),(0,2),(1,2)]:
        c=-C[i,j]
        edge=np.eye(3)[i]-np.eye(3)[j]
        reconstruction+=c*np.outer(edge,edge)
        coefficients.append({'kind':'inter_node','nodes':f'{i+1}-{j+1}','coefficient_per_zeta':float(c),
                             'formula':f'c{i+1}{j+1}=-C_unit[{i+1},{j+1}]','strictly_positive':bool(c>0)})
    residual=reconstruction-C
    eigenC=np.linalg.eigvalsh(C)
    square_residual=float(np.max(abs(C@C-4*K)))
    reconstruct_residual=float(np.max(abs(residual)))
    checks={'K_positive_definite':bool(lam.min()>0),
            'C_is_symmetric':bool(np.max(abs(C-C.T))<1e-12),
            'principal_square_root_identity':square_residual<1e-12,
            'all_six_network_coefficients_positive':all(r['strictly_positive'] for r in coefficients),
            'network_reconstruction_matches_C':reconstruct_residual<1e-12,
            'C_unit_positive_definite':bool(eigenC.min()>0),
            'same_basis_classical_modal_damping':bool(np.max(abs(Q.T@C@Q-np.diag(2*np.sqrt(lam))))<1e-12),
            'nonadjacent_1_3_edge_retained':bool(-C[0,2]>1e-4),
            'all_three_ground_terms_retained':bool(np.all(ground>0)),
            'runtime_below_300_seconds':time.perf_counter()-started<300}
    with (OUT/'network_coefficients.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(coefficients[0]));writer.writeheader();writer.writerows(coefficients)
    params={'mass':[1.,1.,1.],'story_stiffness':[1.,1.,1.],'zeta_for_coefficients':1.,'M':M.tolist(),'K':K.tolist()}
    result={'evidence_id':'E-EXP-009','finished_utc':datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds':time.perf_counter()-started,'code_sha256':sha(__file__),
            'python':platform.python_version(),'numpy':np.__version__,'params':params,
            'params_sha256':hashlib.sha256(json.dumps(params,sort_keys=True).encode()).hexdigest(),
            'C_unit_zeta':C.tolist(),'sqrtK':sqrtK.tolist(),'eigenvalues_K':lam.tolist(),
            'eigenvalues_C_unit':eigenC.tolist(),'network_coefficients':coefficients,
            'network_reconstruction':reconstruction.tolist(),'reconstruction_residual_max_abs':reconstruct_residual,
            'C_squared_minus_4K_max_abs':square_residual,'symmetry_residual_max_abs':float(np.max(abs(C-C.T))),
            'coefficient_postprocessing':'None; no clipping, absolute-value substitution, or optimization',
            'increment':'For every delta_zeta>0, delta_C=delta_zeta*C_unit is positive definite; all six coefficients scale by delta_zeta.',
            'power_identity':'v^T delta_C v=delta_zeta*(sum_i g_i v_i^2+sum_i<j c_ij (v_i-v_j)^2)>=0',
            'scope':'One prescribed unit synthetic model. Includes nonadjacent 1-3 edge and all three ground/reference links. Not adjacent-story-only dashpots, no engineering unit mapping, no solver or construction claim. No general matrix-square-root/M-matrix theorem is established.',
            'checks':checks}
    (OUT/'network_realization.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'coefficients':coefficients,'eigenvalues_C':eigenC.tolist(),'reconstruction_residual':reconstruct_residual,
                      'square_residual':square_residual,'checks':checks,'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
    assert all(checks.values())

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');main()
