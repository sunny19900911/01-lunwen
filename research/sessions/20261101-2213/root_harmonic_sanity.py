from pathlib import Path
from datetime import datetime,timezone,timedelta
import numpy as np,csv,json,hashlib
S=Path(__file__).resolve().parent;O=S/'root-R001-harmonic-sanity'
assert not O.exists(),'Do not overwrite frozen output'
O.mkdir()
K=np.array([[2.,-1.],[-1.,1.]])
lam,phi=np.linalg.eigh(K);om=np.sqrt(lam);G=phi.T@np.ones(2);out=phi[0]*G
z0=.05;predictions=[]
for freq in [.4,float(om[0]),1.,float(np.sqrt(2)),float(om[1]),2.4]:
 D0=lam-freq**2+2j*z0*om*freq;Dp=2j*om*freq
 s0=-1/D0;z=Dp/D0**2;w=-2*Dp**2/D0**3
 for delta in [-.01,.01,.02,.03,.05,.07]:
  # Prediction coefficients depend on baseline only; target transfer not used here.
  p1=s0+delta*z;p2=p1+delta**2*w/2
  predictions.append((freq,delta,s0,z,w,p1,p2))
rows=[];maxres=0.
for freq,delta,s0,z,w,p1,p2 in predictions:
 Dt=lam-freq**2+2j*(z0+delta)*om*freq;truth=-1/Dt
 r1=Dt*p1+1;r2=Dt*p2+1
 e1=2*delta**2*1j*om*freq*z;e2=delta**3*1j*om*freq*w
 maxres=max(maxres,float(np.max(np.abs(r1-e1))),float(np.max(np.abs(r2-e2))))
 assert np.allclose(r1,e1,atol=1e-11,rtol=1e-10) and np.allclose(r2,e2,atol=1e-11,rtol=1e-10)
 P0=abs(out@s0);P1=abs(out@p1);P2=abs(out@p2);Pt=abs(out@truth)
 rows.append(dict(frequency_rad_s=freq,zeta0=z0,target_zeta=z0+delta,delta=delta,baseline_peak_N=P0,linear_pred_peak_N=P1,quadratic_pred_peak_N=P2,target_peak_N=Pt,linear_rel_peak_error=abs(P1-Pt)/Pt,quadratic_rel_peak_error=abs(P2-Pt)/Pt,pred_linear_reduction=1-P1/P0,pred_quadratic_reduction=1-P2/P0,target_reduction=1-Pt/P0))
with(O/'steady-two-floor-prediction-sanity-36.csv').open('w',encoding='utf-8',newline='')as f:
 wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
key=next(r for r in rows if abs(r['frequency_rad_s']-np.sqrt(2))<1e-12 and abs(r['target_zeta']-.08)<1e-12)
result=dict(actual=datetime.now(timezone(timedelta(hours=8))).isoformat(),rows=len(rows),scope='known2floor exact harmonicsteady transfer sanity, not zeroIC earthquake validation or engineeringforecast',baseline_only_coefficients=True,prediction_frozen_in_memory_before_truth=True,independent_blind_test=False,modes_omega=om.tolist(),residual_max_abs=maxres,key_sqrt2_target8=key,new_ODE=False,original_data=False)
(O/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'one-page.md').write_text('# 基准灵敏度的稳态小核验\n\n已在已知两层模型、6个频率和6个阻尼增量共36个组合中核对一/二阶灵敏度残差。两层M=I、K=[[2,-1],[-1,1]]，输出第一层弹性力。先由5%复数传递函数求预测，再读取目标阻尼传递函数。它是解析实现核验，不是实际地震盲测；每个阻尼状态的相应稳态初值不同。\n\n'+json.dumps(key,ensure_ascii=False,indent=2)+'\n\n有限增量误差及全部较差组合保留CSV。没有新工程结果或实际装置结论。\n',encoding='utf-8')
(O/'manifest.json').write_text(json.dumps(dict(frozen=result['actual'],files=[dict(name=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(O.iterdir())]),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
