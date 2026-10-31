from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return list(csv.DictReader((O/n).open(encoding='utf-8-sig')))
r=json.loads((O/'results.json').read_text(encoding='utf-8'));rule=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'))
for d in rule['inputs']:assert sha(Path(d['path']))==d['sha256']
mass=read('identified-masses-before-old-comparison-36.csv');est=read('independent-mode-total-mass-estimates-600.csv');obs=read('observed-XY-generalized-mass-check-300.csv');cons=read('projection-constraint-train100-holdout200-600.csv')
assert len(mass)==36 and len(est)==600 and len(obs)==300 and len(cons)==600
maxM=maxobs=0.
for d in est:
 val=float(d['mass_ratio_mu'])*float(d['ModalMass_times1000_kg_m2'])/float(d['Aw_m'])**2;maxM=max(maxM,abs(val/float(d['Mtotal_mode_estimate_kg'])-1));assert d['projection_stable']=='True'
for d in obs:
 val=(float(d['observed_X_generalized_mass_kg_m2'])+float(d['observed_Y_generalized_mass_kg_m2']))/float(d['native_ModalMass_times1000_kg_m2']);maxobs=max(maxobs,abs(val-float(d['observed_XY_over_native_mr'])));assert val<=1+1e-10
worst=[]
for ax in ['X','Y']:
 worst += sorted([d for d in est if d['Axis']==ax],key=lambda d:abs(float(d['relative_difference_vs_train_median'])),reverse=True)[:5]
with (O/'largest-total-mass-estimate-deviations-10.csv').open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(worst[0]));w.writeheader();w.writerows(worst)
masskeys=sorted({(d['Story'],d['Diaphragm']) for d in mass},key=lambda k:(int(k[0][5:]),k[1]));mm={(d['Axis'],d['Story'],d['Diaphragm']):d for d in mass}
lines=['# R002：18质心集中模型内的方向质量识别','',
'**X/Y分别只用前100阶，投影约束矩阵均为rank17、一维零空间，18项质量权重全部正；后200阶独立检查通过。用同源质量参与比例和ModalMass估得X/Y总质量均为47,440,864.269713 kg。识别结果先保存，再读取旧18行质量作事后比较，最大相对差3.60×10⁻¹⁴。**','',
'## 无需原生f的SI倍率的识别','',
'令A_rj为同模型Modal第r阶第j个CM的X或Y带符号平动（原生mm固定转m），f_r为对应原生UX/UY参与列。原生f不改称Γ，不假定其SI倍率；只使用同表同方向的f_r/f_ref。X选第2阶、Y选第1阶为最大|f|参考，二者也恰是全部300阶的最大|f|。','',
'建立`H_r=A_r−(f_r/f_ref)A_ref`，前100行H的零空间给出w，固定Σw=1。w不使用旧质量、不拟合总剪力。主秩阈值为`eps×max(shape)×σ1`；另报σ/σ1>1e−10所得秩，均为17。全部300行另算秩仍为17，但不用于决定w。后200行按已冻结w检查Aw与f比值关系。','',
'|方向|σ17 / σ18|最小权重|后200阶最大残差/前100阶最大\|Aw\||','|---|---:|---:|']
for d in r['axis_results']:lines.append(f"|{d['Axis']}|{d['train_singular_values'][-2]:.6g} / {d['train_singular_values'][-1]:.6g}|{d['min_identified_weight']:.10f}|{d['holdout_max_residual_over_train_max_Aw']:.6g}|")
lines+=['','## 总质量与18组质量','',
'按每阶`M_r=µ_r(1000×native ModalMass_r)/(A_rw)²`直接计算kg；µ为原生无量纲质量参与比例，kN-m-s²×1000为kg·m²。预先规定µ>0且\|Aw\|大于该方向最大值的1e−10为稳定估计。本次600项均满足；全部估计均保留。总质量标量只取前100阶估计中位数，后200阶不反调。','',
'|方向|前100中位数 / kg|后200最小—最大 / kg|后200最大相对偏差|','|---|---:|---:|---:|']
for d in r['axis_results']:
 h=d['holdout_mass_spread'];lines.append(f"|{d['Axis']}|{d['identified_total_mass_kg']:.9f}|{h['minimum_kg']:.6f}—{h['maximum_kg']:.6f}|{h['max_relative_deviation_vs_train_median']:.6g}|")
lines+=['','|Story / Diaphragm|识别X质量 / kg|识别Y质量 / kg|','|---|---:|---:|']
for k in masskeys:lines.append(f"|{k[0]} / {k[1]}|{float(mm['X',*k]['identified_mass_kg']):.6f}|{float(mm['Y',*k]['identified_mass_kg']):.6f}|")
lines+=['','事后旧18行质量逐组对照最大绝对差'+f"{r['max_identified_old_mass_abs_difference_kg']:.6g}"+' kg，最大相对差'+f"{r['max_identified_old_mass_relative_difference']:.6g}"+'。该对照未参与H、w、M的确定或任何倍率调整。最大偏差模式保留10行诊断表，不把数值误差较大者删除。','',
'## 观测广义质量的最小前置检查','',
'用已识别方向质量，对全部300阶计算`Gobs=ΣmX φX²+ΣmY φY²`并除以源表ModalMass×1000。结果范围为'+f"{r['observed_XY_ratio_min']:.9g}—{r['observed_XY_ratio_max']:.9g}"+'，无大于1（容差1e−10）的记录。最高为第10阶0.9926992，第13阶0.9920534；第2阶0.9627481。该检查支持在18个集中平动观测的假设下继续研究，但没有恢复实际q，也不证明观测矩阵全秩、模态正交或完整质量内积已取得。转角、竖向及非隔板自由度的遗漏仍须单独处理。','',
'## 本轮结论的范围','',
'本次识别对象是**18个CM集中方向质量模型内部**满足实际CM形状与原生有符号投影比例的非负质量；通过留出的后200阶检验，并与旧质量逐组重合，证据强于仅比较质量总和。它不是从总剪力逆拟合质量，也不等于全有限元质量覆盖、约束、真实质量矩阵交叉项已经认证。实际Modal为LinModRitz；本轮没有认证B可直接恢复精确弹性楼层剪力。Γ=0在非经典/FNA耦合下仍可能有实际q，本轮未恢复实际q。','',
'无负权、无前100秩不足、无不稳定投影估计或Gobs/mr>1样本；全部600估计和300观测检查均保留，没有剔除失败记录。唯一的总质量选取规则是前100中位数。未提新表、未读大响应、无新ODE、无剪力拟合或Git操作。输入SHA、阈值、实际起止及脚本见冻结记录。']
(O/'README-CM-mass-identification.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T03:55:46+00:00')).total_seconds();assert elapsed<720
v=dict(frozen_utc=now.isoformat(),started_utc='2026-10-31T03:55:46+00:00',elapsed_seconds=elapsed,train_modes=[1,100],holdout_modes=[101,300],train_rank_XY=[d['train_rank'] for d in r['axis_results']],nullspace_dimension_XY=[d['nullspace_dimension'] for d in r['axis_results']],all_36_directional_masses_positive=all(float(d['identified_mass_kg'])>0 for d in mass),identified_mass_saved_before_old_read=True,mass_estimates_retained=600,observed_mass_checks_retained=300,max_scalar_M_formula_recheck_relative_error=maxM,max_observed_fraction_formula_recheck_error=maxobs,source_hashes_unchanged=True,no_output_shear_fit=True,no_f_SI_multiplier_tuning=True,no_actual_q_recovery=True,complete_FE_mass_coverage_certified=False,no_ODE_or_solver_or_Git=True)
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=rule['inputs'],complete_arrays_local_only=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False,indent=2))
