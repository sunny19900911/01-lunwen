import os
os.environ['OPENBLAS_NUM_THREADS']='2'
from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,platform
import numpy as np

O=Path(__file__).parent;R=O.parents[5];S=R/'research/sessions/20261031-1130'
START=datetime.fromisoformat('2026-10-31T11:39:14+08:00');DEADLINE=START+timedelta(minutes=12)
now=lambda:datetime.now(timezone(timedelta(hours=8)))
def gate(stage):
    if now()>=DEADLINE:raise RuntimeError('R001 deadline: '+stage)
def save(n,x):
    with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def table(n,rs):
    with (O/n).open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)

gate('start')
M=np.diag([2.,3.,4.]);D=np.array([[1.,0.,0.],[-1.,1.,0.],[0.,-1.,1.]])
K=D.T@np.diag([10.,7.,5.])@D;r=np.ones(3);invhalf=np.diag(1/np.sqrt(np.diag(M)))
lam,U=np.linalg.eigh(invhalf@K@invhalf);Phi=invhalf@U
cuts=np.array([[1.,1.,1.],[0.,1.,1.],[0.,0.,1.]])
assert np.all(lam>0)
assert np.allclose(Phi.T@M@Phi,np.eye(3),rtol=0,atol=2e-14)
modalres=K@Phi-M@Phi@np.diag(lam)
assert np.linalg.norm(modalres)<2e-13
def calc(phi,lambda_value,cut):
    mr=float(phi@M@phi);St=float(r@M@phi);Ss=float(cut@M@phi)
    gamma=St/mr;meff=St*St/mr
    return mr,St,Ss,gamma,meff,meff*Ss/St,gamma*Ss,float(cut@K@phi*gamma/lambda_value)
out=[]
for j in range(3):
    for i,cut in enumerate(cuts):
        mr,st,ss,gamma,meff,ratio,inertial,elastic=calc(Phi[:,j],lam[j],cut)
        bound=float(np.sqrt((cut@M@cut)*meff))
        assert np.isclose(ratio,elastic,rtol=1e-12,atol=1e-13)
        assert abs(inertial)<=bound+1e-13
        out.append({'Story_cut':i+1,'Mode':j+1,'lambda_s_minus2':float(lam[j]),'omega_rad_s':float(np.sqrt(lam[j])),'modal_mass':mr,'S_total':st,'S_above':ss,'Gamma':gamma,'m_eff_tonnes':meff,'B_ratio_tonnes':ratio,'B_inertial_tonnes':inertial,'B_elastic_tonnes':elastic,'abs_ratio_elastic_error':abs(ratio-elastic),'conditional_Cauchy_bound_tonnes':bound})
table('eigen-coefficients-9.csv',out)
save('model.json',{'created_at':now().isoformat(),'M_tonnes':M.tolist(),'story_k_kN_per_m':[10,7,5],'K_kN_per_m':K.tolist(),'uniform_input_vector':r.tolist(),'cut_selectors':cuts.tolist(),'lambda':lam.tolist(),'Phi_columns':Phi.tolist(),'modal_equation_residual_Frobenius':float(np.linalg.norm(modalres)),'coordinate_and_output_convention':'floor displacements ascending; positive elastic story shear = k_s*(u_s-u_(s-1)) = a_s^T K u; base u0=0'})
gate('normalization')
invariance=[]
for factor in (-7.,.125,3.,-.5):
    for x in out:
        j=x['Mode']-1;i=x['Story_cut']-1
        *_,br,bi,be=calc(Phi[:,j]*factor,lam[j],cuts[i])
        err=max(abs(br-x['B_ratio_tonnes']),abs(bi-x['B_inertial_tonnes']),abs(be-x['B_elastic_tonnes']))
        assert err<2e-12
        invariance.append({'Story_cut':i+1,'Mode':j+1,'phi_scale':factor,'B_ratio_tonnes':br,'B_inertial_tonnes':bi,'B_elastic_tonnes':be,'max_abs_coefficient_change':err})
table('normalization-invariance-36.csv',invariance)
massidentities=[]
for i,cut in enumerate(cuts):
    bsum=sum(x['B_inertial_tonnes'] for x in out if x['Story_cut']==i+1)
    expected=float(cut@M@r);assert abs(bsum-expected)<1e-12
    massidentities.append({'Story_cut':i+1,'sum_all_modes_B_tonnes':bsum,'mass_above_tonnes':expected,'abs_error':abs(bsum-expected)})
assert all(abs(x['B_ratio_tonnes']-x['m_eff_tonnes'])<1e-13 for x in out if x['Story_cut']==1)
table('complete-mass-identities-3.csv',massidentities)
gate('zero participation')
deg=[]
for label,delta in [('antisymmetric_exact',0.),('antisymmetric_near',1e-10)]:
    # Two equal tower masses; construct an exact full-space mode even for near cancellation.
    v=np.array([1.,-1.+delta]);orth=np.array([1.-delta,1.]);M2=np.eye(2);r2=np.ones(2);cut=np.array([1.,0.])
    vhat=v/np.linalg.norm(v);ohat=orth/np.linalg.norm(orth);K2=4*np.outer(vhat,vhat)+2*np.outer(ohat,ohat)
    mr=float(v@v);st=float(r2@v);ss=float(cut@v);gamma=st/mr;meff=st*st/mr
    cancel=abs(st)/float(np.sum(abs(v)));inertial=gamma*ss;elastic=float(cut@K2@v*gamma/4)
    assert np.linalg.norm(K2@v-4*v)<1e-13 and abs(inertial-elastic)<1e-13
    assert cancel<1e-8
    # Never divide by a zero/near-zero S in the candidate reconstruction.
    deg.append({'case':label,'delta_requested':delta,'S_total':st,'S_local_tower':ss,'modal_mass':mr,'Gamma':gamma,'m_eff':meff,'S_cancellation_ratio':cancel,'ratio_formula_executed':False,'B_safe_Gamma_Slocal':inertial,'B_elastic':elastic,'interpretation':'uniform input excites no antisymmetric mode' if delta==0 else 'small actual excitation; ratio expression deliberately guarded'})
table('zero-near-zero-participation-2.csv',deg)
gate('Ritz counterexample')
Mr=np.eye(2);Kr=np.array([[2.,-1.],[-1.,1.]]);rr=np.ones(2)
v=np.linalg.solve(Kr,Mr@rr) # First static-load Ritz vector, not an arbitrary alleged eigenvector.
lr=float(v@Kr@v/(v@Mr@v));er=Kr@v-lr*Mr@v;sr=float(rr@Mr@v);mr=float(v@Mr@v);gr=sr/mr;meff=sr*sr/mr
assert np.linalg.norm(er)>0.1 and abs(float(v@er))<1e-13
ritz=[]
for i,cut in enumerate((np.ones(2),np.array([0.,1.]))):
    ss=float(cut@Mr@v);bi=meff*ss/sr;be=float(cut@Kr@v*gr/lr);cor=float(cut@er*gr/lr)
    assert abs(be-bi-cor)<1e-13 and abs(be-bi)>0.07
    ritz.append({'Story_cut':i+1,'Ritz_lambda':lr,'S_total':sr,'S_cut':ss,'Gamma':gr,'m_eff':meff,'B_ratio_equals_inertia':bi,'B_elastic_cut':be,'elastic_minus_inertia':be-bi,'residual_correction_a_e_Gamma_over_lambda':cor})
table('ritz-counterexample-2.csv',ritz)
save('ritz-model.json',{'M':Mr.tolist(),'K':Kr.tolist(),'input':rr.tolist(),'static_Ritz_vector_KinvMr':v.tolist(),'projected_lambda':lr,'full_eigenvalues':np.linalg.eigvalsh(Kr).tolist(),'full_eigen_residual':er.tolist(),'Galerkin_vT_residual':float(v@er),'inertia_and_elastic_coefficients_not_equal':True})
source=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [S/'plan.md',S/'plan-theory-addendum-v001.md',Path(__file__)]]
save('checks.json',{'completed':now().isoformat(),'model':'new 3-story physical shear model only','eigen_coefficient_checks':9,'normalization_cases':36,'complete_mass_checks':3,'base_B_equals_meff_checks':3,'Cauchy_checks':9,'zero_and_near_zero_cases':2,'Ritz_cut_counterexamples':2,'max_Eigen_ratio_vs_elastic_error':max(x['abs_ratio_elastic_error'] for x in out),'max_normalization_change':max(x['max_abs_coefficient_change'] for x in invariance),'Ritz_full_residual_norm':float(np.linalg.norm(er)),'must_count':0,'new_fits':0,'time_integration':False,'role1_code_imported':False,'engineering_data_read':False,'python':platform.python_version(),'numpy':np.__version__,'sources':source})
print(json.dumps(json.loads((O/'checks.json').read_text(encoding='utf-8')),ensure_ascii=False))
