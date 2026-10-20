"""H2 full saved-state projection, one position per call, no ODE or source imports."""
from pathlib import Path
import csv,hashlib,json,sys
import numpy as np
P=Path(__file__).resolve().parent
freeze=json.loads((P/'R003-input-freeze.json').read_text(encoding='utf-8'));B=Path(freeze['source_root']);pos=int(sys.argv[1]);assert pos in freeze['positions']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=B/'H021-delivery-manifest.json';assert sha(m)==freeze['H021_manifest_sha256'];manifest=json.loads(m.read_text(encoding='utf-8'))
entries=manifest['files']+manifest['local_only_states']
def checked(path):
 e=next(x for x in entries if Path(x['path']).resolve()==path.resolve());assert path.stat().st_size==e['bytes'] and sha(path)==e['sha256'];return e
prepath=B/'H021-three-floor-prospective/pre-run-freeze.json';preentry=checked(prepath);pre=json.loads(prepath.read_text(encoding='utf-8'))
source=B/'H021-three-floor-prospective/local-only'/f'H2_envelope__position{pos}__h0.005.npz';entry=checked(source)
M=np.array(pre['M']);K=np.array(pre['K']);D=np.array(pre['D']);stiff=np.array(pre['story_stiffness']);mass=np.diag(M)
assert np.max(abs(M-np.diag(mass)))==0
lam,V=np.linalg.eigh(K/np.sqrt(mass[:,None]*mass[None,:]));phi=V/np.sqrt(mass[:,None])
for j in range(3):
 if phi[0,j]<0:phi[:,j]*=-1
orth=float(np.max(abs(phi.T@M@phi-np.eye(3))));eig=float(np.max(abs(K@phi-(M@phi)*lam)));assert max(orth,eig)<1e-12
with np.load(source) as f:a=f['trajectory']
t=a[:,0];u=a[:,1:4];assert len(t)==40001 and t[0]==0 and t[-1]==200 and np.all(np.diff(t)>0) and np.isfinite(u).all()
q=u@M@phi;ustate=float(np.max(abs(q@phi.T-u)));assert ustate<1e-12
rows=[];summ=[]
for label,ell in [('QS2',stiff[1]*D[1]),('roof',np.array([0.,0.,1.]))]:
 terms=q*(ell@phi);direct=u@ell;three=terms.sum(axis=1);two=terms[:,:2].sum(axis=1)
 err=float(np.max(abs(three-direct)));res=float(np.max(abs((direct-two)-terms[:,2])));assert max(err,res)<1e-12
 i=int(np.argmax(abs(direct)));j=int(np.argmax(abs(two)));Pfull=float(abs(direct[i]));Ptwo=float(abs(two[j]));assert Pfull>0
 summ.append({'quantity':label,'full_peak':Pfull,'full_peak_t':float(t[i]),'two_mode_posthoc_peak':Ptwo,'two_mode_peak_t':float(t[j]),'signed_peak_change_relative':Ptwo/Pfull-1,'absolute_peak_error_relative':abs(Ptwo/Pfull-1),'three_mode_reconstruction_max_abs_error':err,'tail_residual_identity_max_abs_error':res})
 for anchor,idx in [('full_output_own_peak',i),('two_mode_posthoc_own_peak',j)]:
  v=terms[idx];den=float(np.sum(abs(v)))
  rows.append({'case':'H2_envelope','position':pos,'scheme':'none' if pos==0 else 'device_story1','quantity':label,'anchor':anchor,'index':idx,'time_nondimensional':float(t[idx]),'mode1_signed':float(v[0]),'mode2_signed':float(v[1]),'mode3_signed':float(v[2]),'two_mode_signed_sum':float(two[idx]),'three_mode_signed_sum':float(three[idx]),'direct_full_signed':float(direct[idx]),'sum_abs_modal_terms':den,'absolute_sum_over_sum_absolute':abs(float(three[idx]))/den if den else None,'full_peak':Pfull,'two_mode_posthoc_peak':Ptwo,'signed_peak_change_relative':Ptwo/Pfull-1,'three_mode_reconstruction_max_abs_error':err})
tag='none' if pos==0 else 'story1'
fp=P/f'R003-{tag}-anchors.csv';assert not fp.exists()
with fp.open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
out={'case':'H2_envelope','position':pos,'time_and_outputs':'nondimensional; same40001 saved nodes, h=.005, t0..200','source_state':entry,'source_model_freeze':preentry,'mass':M.tolist(),'stiffness':K.tolist(),'phi_columns_mass_normalized':phi.tolist(),'omega':np.sqrt(lam).tolist(),'phi_sign_convention':'first component positive','mass_orthogonality_error':orth,'eigen_equation_error':eig,'u_reconstruction_error':ustate,'summaries':summ,'new_ODE_runs':0,'not_a_reduced_feedback_solve':True}
fj=P/f'R003-{tag}-summary.json';assert not fj.exists();fj.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'table':str(fp),'summaries':summ,'rows':rows},ensure_ascii=False))
