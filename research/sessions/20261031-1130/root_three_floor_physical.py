"""Check direct modal coefficients against an existing, fully known 3-floor model.
No input search, refit, time integration, or modification of historical evidence.
"""
from pathlib import Path
import numpy as np,json,hashlib,csv,datetime
S=Path(__file__).resolve().parent
D=S.parents[3]/'W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016'
O=S/'root-R001-physical-three-floor'
O.mkdir(exist_ok=False)
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
paths=[D/('passive_local_counterexample'+ext)for ext in ['.json','.npz','.py']]
src=[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in paths]
cfg=json.loads(paths[0].read_text(encoding='utf-8'));a=np.load(paths[1],allow_pickle=False)
M=np.array(cfg['M']);K=np.array(cfg['K']);k=np.array(cfg['story_stiffness']);assert np.allclose(M,np.eye(3))
lam,phi=np.linalg.eigh(K);omega=np.sqrt(lam);r=np.ones(3);mr=np.einsum('ir,ij,jr->r',phi,M,phi)
St=phi.T@M@r;Gamma=St/mr;meff=St**2/mr
assert np.min(np.abs(St))>1e-8
T=np.triu(np.ones((3,3)));Ss=T@M@phi
B=Ss/St[None,:]*meff[None,:]
Bk=(T@K@phi)*Gamma[None,:]/lam[None,:]
scale=np.array([-2.,.3,5.]);psi=phi*scale
ms=np.einsum('ir,ij,jr->r',psi,M,psi);sp=psi.T@M@r;ep=sp**2/ms
Bscaled=(T@M@psi)/sp[None,:]*ep[None,:]
assert np.max(np.abs(B-Bk))<1e-12
assert np.max(np.abs(B-Bscaled))<1e-12
assert np.max(np.abs(B[0]-meff))<1e-12
assert abs(meff.sum()-3)<1e-12
cut_mass=T@M@r;bound=np.sqrt(cut_mass[:,None]*meff[None,:])
assert np.all(np.abs(B)<=bound+1e-12)
coef=[]
for f in range(3):
 for j in range(3):coef.append({'floor':f+1,'mode':j+1,'omega':float(omega[j]),'mass_projection_all':float(St[j]),'mass_projection_above':float(Ss[f,j]),'effective_modal_mass':float(meff[j]),'direct_B':float(B[f,j]),'K_recovery_B':float(Bk[f,j]),'Cauchy_bound':float(bound[f,j])})
recon=[];modal=[];state={};anchors=[]
t=a['t']
for z in [.05,.08]:
 u=a[f'{z}_u'];V=a[f'{z}_V'];q=u@phi;s=q/Gamma[None,:];g=s*lam[None,:]
 terms=g[:,None,:]*B[None,:,:];pred=terms.sum(axis=2)
 assert u.shape==V.shape==(len(t),3)
 assert np.max(np.abs(pred-V))<1e-11
 P=np.max(np.abs(V),axis=0);amp=np.max(np.abs(terms),axis=0);U=amp.sum(axis=1);C=P/U
 state[z]={'P':P,'U':U,'C':C,'amp':amp,'terms':terms,'native':V}
 for f in range(3):
  ii=int(np.argmax(np.abs(V[:,f])))
  recon.append({'zeta':z,'floor':f+1,'peak':float(P[f]),'peak_time':float(t[ii]),'independent_modal_peak_sum_U':float(U[f]),'peak_combination_factor_C':float(C[f]),'max_abs_reconstruction_error':float(np.max(np.abs(pred[:,f]-V[:,f])))})
  for j in range(3):modal.append({'zeta':z,'floor':f+1,'mode':j+1,'actual_modal_output_peak':float(amp[f,j])})
ratios=[]
for f in range(3):
 p5=state[.05]['P'][f];p8=state[.08]['P'][f];u5=state[.05]['U'][f];u8=state[.08]['U'][f];c5=state[.05]['C'][f];c8=state[.08]['C'][f]
 rr=p8/p5;ur=u8/u5;cr=c8/c5
 assert abs(rr-ur*cr)<1e-12
 ratios.append({'floor':f+1,'P8_over_P5':float(rr),'U8_over_U5':float(ur),'C8_over_C5':float(cr),'product_error':float(rr-ur*cr),'all_independent_modal_peaks_decrease':bool(np.all(state[.08]['amp'][f]<state[.05]['amp'][f])),'identity':'P8/P5=(U8/U5)*(C8/C5); C includes timing and signed cancellation, not pure phase'})
 for anchor_z in [.05,.08]:
  ii=int(np.argmax(np.abs(state[anchor_z]['native'][:,f])))
  for z in [.05,.08]:
   v=state[z]['terms'][ii,f];den=np.abs(v).sum()
   anchors.append({'floor':f+1,'anchor_zeta':anchor_z,'time':float(t[ii]),'evaluated_zeta':z,'modal1':float(v[0]),'modal2':float(v[1]),'modal3':float(v[2]),'signed_total':float(v.sum()),'native_total':float(state[z]['native'][ii,f]),'same_time_cancellation':float(1-abs(v.sum())/den)if den else None})
def write(name,rows):
 with (O/name).open('x',encoding='utf-8',newline='')as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
write('physical-coefficients-9.csv',coef);write('reconstruction-and-peak-6.csv',recon);write('modal-output-peaks-18.csv',modal);write('amplitude-and-combination-ratios-3.csv',ratios);write('same-time-physical-anchors-12.csv',anchors)
out={'start_utc':start,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':'known physical three-floor model; reuse historical displacement/shear arrays, no new integration or fitting','inputs':src,'max_direct_vs_K_B_error':float(np.max(abs(B-Bk))),'max_normalization_invariance_error':float(np.max(abs(B-Bscaled))),'max_output_reconstruction_error':max(v['max_abs_reconstruction_error']for v in recon),'ratios':ratios,'not_engineering_data':True,'no_new_ODE_or_fit':True}
(O/'results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'README.md').write_text('''# 旧三层机制模型的物理分担接入
用已知M/K与旧冻结位移/剪力数组，不重新扫频、积分或拟合。质量加权振型比值直接给各层真实B，逐项与K恢复算子一致，反号/尺度不变、基底B=m_eff、质量与Cauchy检查通过。
各态的真实模态剪力相加复原旧整体剪力。U为各阶独立峰的绝对和，是整体峰的上界，不是实际合成峰；C=P/U，同时包含峰不同时和符号抵消。两态P比精确等于U比与C比之积，不叫纯相位因果项，也不称新定理。
该例用于验证直接系数和解析机制的可执行性，不是实际ETABS工程的逐阶分担认证。所有旧文件只读，完整数组未复制到新目录或Git。
''',encoding='utf-8')
manifest=[]
for p in O.iterdir():
 if p.is_file():manifest.append({'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(O/'manifest.json').write_text(json.dumps({'frozen':True,'outputs':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:out[k]for k in ['max_direct_vs_K_B_error','max_output_reconstruction_error','ratios']},ensure_ascii=False))
