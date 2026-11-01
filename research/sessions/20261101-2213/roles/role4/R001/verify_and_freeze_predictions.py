import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return list(csv.DictReader((O/n).open(encoding='utf-8-sig')))
rule=json.loads((O/'input-prediction-rules-freeze.json').read_text(encoding='utf-8'));r=json.loads((O/'results.json').read_text(encoding='utf-8'));peaks=read('all300-layer-peak-predictions-96.csv');checks=read('local-infinitesimal-derivative-checks-600.csv');assert len(peaks)==96 and len({(d['target_zeta'],d['Taylor_order'],d['Story']) for d in peaks})==96
source=Path(rule['inputs'][0]['path']);local=Path(r['local_only_output']['path']);assert sha(local)==r['local_only_output']['sha256']
maxcurve=maxpeak=maxtime=0.
with np.load(source,allow_pickle=False) as base,np.load(local,allow_pickle=False) as a:
 t=base['t'];s0=base['s_unitGamma'];om=base['omega'];B=base['B_direct'];Z=a['z_unit'];W=a['w_unit'];assert Z.shape==W.shape==s0.shape and np.all(Z[0]==0) and np.all(W[0]==0);p0=np.max(abs((s0*om**2)@B.T/1000),axis=0)
 for z in rule['target_zetas']:
  delta=z-.05
  for order in [1,2]:
   ss=s0+delta*Z+(delta*delta/2*W if order==2 else 0);VV=(ss*om**2)@B.T/1000;saved=a[f'z{z:g}_order{order}_shear_inertia_kN'];maxcurve=max(maxcurve,float(np.max(abs(VV-saved))))
   for i in range(12):
    d=next(d for d in peaks if float(d['target_zeta'])==z and int(d['Taylor_order'])==order and d['Story']=='Story'+str(i+1));ip=int(np.argmax(abs(VV[:,i])));p=float(abs(VV[ip,i]));maxpeak=max(maxpeak,abs(p-float(d['predicted_peak_kN'])),abs(100*(1-p/p0[i])-float(d['predicted_decrease_percent'])));maxtime=max(maxtime,abs(float(t[ip])-float(d['predicted_peak_time_s'])))
assert max(maxcurve,maxpeak,maxtime)<1e-10
comparisons=[]
for z in rule['target_zetas']:
 for st in range(1,13):
  story='Story'+str(st);a=next(d for d in peaks if float(d['target_zeta'])==z and d['Taylor_order']=='1' and d['Story']==story);b=next(d for d in peaks if float(d['target_zeta'])==z and d['Taylor_order']=='2' and d['Story']==story);d1=float(a['predicted_decrease_percent']);d2=float(b['predicted_decrease_percent']);comparisons.append(dict(target_zeta=z,Story=story,order1_predicted_decrease_percent=d1,order2_predicted_decrease_percent=d2,order2_minus_order1_decrease_pp=d2-d1,order1_below10pct_demo=d1<10,order2_below10pct_demo=d2<10,demo10pct_classification_disagrees=(d1<10)!=(d2<10),order1_peak_time_s=float(a['predicted_peak_time_s']),order2_peak_time_s=float(b['predicted_peak_time_s']),two_orders_peak_times_differ=float(a['predicted_peak_time_s'])!=float(b['predicted_peak_time_s']),scope='prediction-only comparison, not truth error estimate or accuracy guarantee'))
with (O/'prediction-order-comparison-and-demo-screen-48.csv').open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(comparisons[0]));w.writeheader();w.writerows(comparisons)
priority=[d for d in comparisons if d['Story'] in ['Story5','Story12']]
with (O/'Story5-Story12-prediction-order-comparison-8.csv').open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(priority[0]));w.writeheader();w.writerows(priority)
deriv=[]
for mode in [2,10,13]:
 lo=next(d for d in checks if int(d['Mode'])==mode and float(d['local_check_h'])==1e-4);hi=next(d for d in checks if int(d['Mode'])==mode and float(d['local_check_h'])==5e-5);deriv.append(dict(Mode=mode,first_error_ratio_h_to_halfh=float(lo['first_derivative_relative_L2_error'])/float(hi['first_derivative_relative_L2_error']),second_error_ratio_h_to_halfh=float(lo['second_derivative_relative_L2_error'])/float(hi['second_derivative_relative_L2_error'])))
assert all(3.5<d['first_error_ratio_h_to_halfh']<4.5 and 3.5<d['second_error_ratio_h_to_halfh']<4.5 for d in deriv)
lines=['# 基于5%基准响应的候选阻尼预测：首轮实数','',
'已用SHW3X的5%基准模态运动和固定物理系数，完成300阶阻尼一、二阶灵敏度，预测6%、7%、8%、10%时的全层剪力峰值。候选目标响应尚未用于计算或验证。先行的2/10/13三阶预测也单独保存，其结果仅表示这三阶合成。','',
'各阶满足`s¨+2ζωs˙+ω²s=−ag`。在ζ₀=0.05处令`z=∂s/∂ζ`、`w=∂²s/∂ζ²`，采用`ŝ₁=s₀+Δζz`和`ŝ₂=s₀+Δζz+½Δζ²w`。楼层剪力按固定B、ω合成，再求整个保存时程中绝对值最大值；没有只在原峰时刻代入。输入、频率、质量及物理输出系数保持不变，采用既有300阶弹性惯性剪力参照。','',
'|候选ζ|Story5 一阶降幅 / %|Story5 二阶降幅 / %|Story12 一阶降幅 / %|Story12 二阶降幅 / %|','|---:|---:|---:|---:|---:|']
for z in rule['target_zetas']:
 s5=next(d for d in priority if d['target_zeta']==z and d['Story']=='Story5');s12=next(d for d in priority if d['target_zeta']==z and d['Story']=='Story12');lines.append(f"|{z:.0%}|{s5['order1_predicted_decrease_percent']:.4f}|{s5['order2_predicted_decrease_percent']:.4f}|{s12['order1_predicted_decrease_percent']:.4f}|{s12['order2_predicted_decrease_percent']:.4f}|")
lines+=['','候选8%时，两种预测均显示Story5改善小于10%的演示要求，Story12则明显较大。候选10%时，Story5的一阶预测为9.35%、二阶为13.71%，对演示要求的判断发生分歧；这类楼层应优先安排完整候选响应复核。10%仅是本轮演示输入，不是规范阈值。两阶预测之间的差别还不是经过证明的误差界，不能据此先认二阶更准确。','',
'控制峰也可能换时：候选8%的Story12一阶预测峰在20.44s，二阶在21.18s。两者均由整个时程求峰得到，现阶段不能用原5%峰时刻固定不动来替代候选峰搜索。','',
'灵敏度递推由精确离散传播式对ζ求导，基准运动直接读缓存；逐步回代基准的最大位移差8.67×10⁻¹⁹m。以ζ₀±10⁻⁴、ζ₀±5×10⁻⁵作微小邻域导数检查，全300阶相对L2差最大为一阶6.78×10⁻⁶、二阶4.50×10⁻⁶，三阶重点模式的误差随扰动减半约缩小至四分之一。该检查验证导数实现，不是6%—10%候选响应的准确度检验。','',
'首批三阶小表于22:25:54落盘，早于首8分钟检查点；全300阶96行楼层峰值、2400行单阶运动预测、288行CM峰值及48行两阶判断对照均已保存。完整灵敏度和预测曲线仅留本地，公式、代码、输入与预测先冻结；下一轮再生成或打开候选目标参考响应，核实误差及低改善楼层判断。']
(O/'one-page-prediction-result.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
notes=['# 算法与预测隔离核验','',
'仅打开旧020的SHW3X、ζ=.05因子数组；访问键为t/ag/s_unitGamma/sdot_unitGamma/omega/B_direct/Gamma_X/phi_X/phi_Y。未打开任何ζ=.08数组，未读取目标峰或目标曲线作为预测输入。旧README和manifest仅作来源说明，历史8%结果已见过，不将未来对照称盲测。','',
'精确步进采用分段线性输入闭式传播矩阵E(ζ)，wd=ω√(1−ζ²)、e=exp(−ζωΔt)。解析求E′和E″，并包括线性输入特解对ζ的一阶导数。令dq=s₀,n−1−qp0、dv=v₀,n−1−vp、dz=z_n−1−∂ζqp0，递推','',
'z_n=E11 dz+E12 zdot_prev+E11′dq+E12′dv+∂ζqp1；w_n=E11 w_prev+E12 wdot_prev+2E11′dz+2E12′zdot_prev+E11″dq+E12″dv。速度导数使用E21/E22对应表达式。qp关于ζ为线性，二阶导数为0。该算法是稳定精确传播式的参数微分，不用显式Euler积分灵敏度。','',
'基准s/v逐步取冻结缓存，不自行重跑旧六套响应。只为微小导数验证调用原exact states四次，ζ值为.0499/.0501/.04995/.05005；未在有限目标.06/.07/.08/.10求新真值。没有SciPy、依赖安装、剪力拟合、频率/增益/符号/时间调整。','',
'导数检查600行保留全部300阶与两种扰动步长；重点2/10/13阶及全300阶预测均列出，不按目标结果删样本。预测阶次对照是描述性的候选比较，不将两阶差称认证区间。主文结果与工程含义见one-page-prediction-result.md；完整曲线和导数为local-cache，禁止上传。']
(O/'algorithm-and-isolation-notes.md').write_text('\n'.join(notes)+'\n',encoding='utf-8')
for d in rule['inputs']:assert sha(Path(d['path']))==d['sha256']
assert sha(O/'predict_from_damping_sensitivity.py')==rule['code_sha256'];now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-11-01T14:21:56+00:00')).total_seconds();assert elapsed<900
first=datetime.fromtimestamp((O/'early-three-mode-target-predictions-96.csv').stat().st_mtime,timezone.utc).isoformat()
v=dict(prediction_frozen_utc=now.isoformat(),started_utc='2026-11-01T14:21:56+00:00',elapsed_seconds=elapsed,first_small_prediction_saved_utc=first,first8min_small_output_met=True,all300_analytic_sensitivities=True,baseline_cache_reused=True,baseline_step_q_max_error_m=r['baseline_primal_step_max_abs_q_error_m'],local_derivative_check_rows=600,selected_mode_FD_step_halving=deriv,all300_prediction_peak_rows_rechecked=96,max_predicted_curve_reconstruction_error_kN=maxcurve,max_peak_or_decrease_recheck_difference=maxpeak,max_predicted_peak_time_recheck_error_s=maxtime,finite_target_truth_generated=False,target8_response_arrays_opened=False,nearby_derivative_check_only_exact_solve_count=4,old_six_ODE_sets_not_regenerated=True,input_and_code_SHA_unchanged=True,no_fit_solver_or_Git=True,complete_arrays_local_only=True)
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='prediction-freeze-manifest.json']
(O/'prediction-freeze-manifest.json').write_text(json.dumps(dict(status='predictions frozen before target evaluation',frozen_utc=now.isoformat(),outputs=files,inputs=rule['inputs'],local_only_prediction_array=r['local_only_output'],array_upload_allowed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(v,ensure_ascii=False,indent=2))
