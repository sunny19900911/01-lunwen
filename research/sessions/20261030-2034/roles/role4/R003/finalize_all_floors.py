from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):
 with (O/n).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def js(n,d):
 with (O/n).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
rules=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));errors=read('all12-prediction-errors-144.csv');summary=read('all12-validation-summary-24.csv');native=read('native-all12-peak-change-36.csv');groups=read('all12-low-high-N24-to-N36-144.csv');anchors=read('all12-same-time-low-high-residual-288.csv');result=json.loads((O/'results.json').read_text(encoding='utf-8'))
assert [len(errors),len(summary),len(native),len(groups),len(anchors)]==[144,24,36,144,288]
max_metric=0.;max_part=0.
with np.load(O/'local-cache/all12-low-high-reference-traces.npz',allow_pickle=False) as z:
 for q in errors:
  tag=f"N{q['N']}__{q['Case']}__{q['Story']}__z{float(q['zeta']):g}";y=z[tag+'__native'];pred=z[tag+'__prediction'];lo=z[tag+'__low1to12'];hi=z[tag+'__represented_high13plus'];res=z[tag+'__residual'];nr=float(np.linalg.norm(pred-y)/np.linalg.norm(y));max_metric=max(max_metric,abs(nr-float(q['NRMSE'])));max_part=max(max_part,float(np.max(abs(y-lo-hi-res))))
  assert abs(nr-float(q['NRMSE']))<1e-12 and math.isclose(np.max(abs(pred))/np.max(abs(y))-1,float(q['peak_relative_error']),rel_tol=1e-9,abs_tol=1e-12)
  assert np.max(abs(pred-lo-hi))<1e-6
for q in anchors:assert abs(float(q['native_kN'])-float(q['low1to12_kN'])-float(q['represented_high13plus_kN'])-float(q['residual_native_minus_prediction_kN']))<1e-6
assert sum(q['fit_origin']=='frozen_Story5_12_reused' for q in errors)==24
lines=['# 全12层固定输出参照与阻尼增量响应','',
'只扩展其余10层，每个N一次10输出lstsq；Story5/12的冻结系数、预测和24条误差直接复用，逐项核对未变。N24/N36、elastic、rcond=1e-10；仍仅原生SHW3X+SHW4X的5%训练，RH4X整波留出，8%三波不重拟合。没有新N、物理模型或布置计算。','',
'为避免重复积分，从旧两层冻结逐模态参照项除以其冻结系数恢复共享单位基，逐列选择两层中绝对系数较大者作数值反归一化。这不是对原生信号拟合增益；恢复后对旧两层预测的最大差7.89×10⁻⁸ kN，旧结果仍直接复用。共享基、原生时间及新10层Bottom VX已逐点对齐。','',
'## 全楼误差','',
'NRMSE为完整曲线L2误差除以原生L2。下表8%列为三波最大值；全部逐波、逐态、峰差及源行在144行表。','',
'| 层 | N24：5%RH4留出 | N36：5%RH4留出 | N24：8%最大 | N36：8%最大 |','|---|---:|---:|---:|---:|']
for i in range(1,13):
 a=next(q for q in summary if q['N']=='24' and q['Story']==f'Story{i}');b=next(q for q in summary if q['N']=='36' and q['Story']==f'Story{i}')
 lines.append(f"| Story{i} | {100*float(a['heldout5_NRMSE']):.3f}% | {100*float(b['heldout5_NRMSE']):.3f}% | {100*float(a['fixed8_NRMSE_max']):.3f}% | {100*float(b['fixed8_NRMSE_max']):.3f}% |")
lines+=['',
'N36多数层继续改善，但不能只展示最好的目标层：Story11的5%留出仍为5.717%，8%最高4.552%；该层是本全楼参照中误差较大的位置。两层成功不等于全楼同等精度。','',
'## 原生5%→8%峰下降：真实高度差异','',
'| 层 | RH4X | SHW3X | SHW4X |','|---|---:|---:|---:|']
for i in range(1,13):
 values=[next(float(q['native_peak_decrease_percent']) for q in native if q['Story']==f'Story{i}' and q['Case']==case) for case in ['RH4X','SHW3X','SHW4X']]
 lines.append(f'| Story{i} | {values[0]:.3f}% | {values[1]:.3f}% | {values[2]:.3f}% |')
lines+=['',
'这些为相同输入的原生整条曲线各自寻峰结果，不是将独立峰相减作同刻受力分担。本轮工况为原生SHW3，不与旧实际装置表的SHW7名称混用。RH4X最小峰下降在Story7（19.128%），SHW3X在Story5（6.851%），SHW4X在Story1（10.751%）；本三波最大值均在Story12。这是需要参照项解释的真实整层差异，不预设安装位置/装置未发挥原因。','',
'## 低组、高组合与残差','',
'低组固定为1—12；高组合是各截断中“已表示的13阶以上”：N24为13—24，N36为13—36，不能称完整真实高阶总量。全楼144条组曲线对照同时保留差/原生L2、差/组自身L2及绝对RMS。N24→36低组相对原生的最大变化0.3124%，在Story11/SHW3X/5%；高组合最大变化5.7138%，在Story11/SHW4X/5%。这与上一项13—24子组大幅再分配不同：高组合允许新增25—36的补偿，不能据此认证每一高阶系数。','',
'288条主要峰同刻表保留native=low+represented_high+residual，含原生峰与预测峰两类时刻、原符号及两组抵消诊断。残差没有被吸收入某个模态，也未把这些有符号剪力项称为能量份额。仅在分母非零时定义两组抵消量；它描述拟合参照的同刻抵消，不是真实单阶坐标的唯一分解。','',
'## 交付接口','',
'- all12-prediction-errors-144.csv：全楼两N、三波、两态误差和原生峰下降。','- native-all12-peak-change-36.csv：36对原生层剪力峰及对方同刻值、源行。','- all12-validation-summary-24.csv：24个N×层的留出/8%范围。','- all12-low-high-N24-to-N36-144.csv：低组及已表示高组合曲线变化。','- all12-same-time-low-high-residual-288.csv：主要峰同刻项与残差。','- all12-models-small.json、all12-fixed-coefficients-720.csv：新10层固定输出映射及旧两层复用标记。','',
'完整数组仅local-cache/all12-low-high-reference-traces.npz，禁止上传；外层只交小表与指纹。实际命令python -X utf8 extend_all_floors.py后执行python -X utf8 finalize_all_floors.py。仅读取旧小缓存，无大Excel、ETABS/API、Git、8%重拟合或旧两层重拟合。以上均为fitted-model参照及真实原生响应对照，待独审后解释稳定组。']
(O/'README-all12.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for q in rules['inputs']:assert sha(Path(q['path']))==q['sha256']
assert sha(O/'extend_all_floors.py')==rules['code_sha256']
now=datetime.now(timezone.utc);start=datetime.fromisoformat(rules['start_observed_utc']);assert now<=datetime.fromisoformat(rules['deadline_utc'])
js('verification.json',{'verified_utc':now.isoformat(),'error_rows':144,'native_pair_rows':36,'new_fits':2,'new_outputs_per_fit':10,'frozen_old_output_error_rows_reused':24,'no_old_Story5_12_refit':True,'no_native8_refit':True,'original_basis_recovery_old_prediction_max_error_kN':result['basis_recovery_max_error_kN'],'all_time_vectors_exact':True,'metrics_recomputed_from_frozen_arrays':True,'max_metric_recheck_difference':max_metric,'max_native_minus_low_high_residual_abs_kN':max_part,'all288_key_time_balances_checked':True,'all_inputs_and_code_unchanged':True,'no_new_N_or_full_SDOF_reintegration':True,'full_arrays_local_only':True,'classification':'fitted-model, not physical unique modal force or energy decomposition'})
files=[{'name':p.name,'bytes':p.stat().st_size,'last_modified_utc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'sha256':sha(p)} for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
js('delivery-manifest.json',{'status':'complete all12 extension; independent audit pending','frozen_utc':now.isoformat(),'frozen_Asia_Shanghai':now.astimezone(timezone(timedelta(hours=8))).isoformat(),'elapsed_seconds':(now-start).total_seconds(),'within10_minutes':True,'files':files,'local_only_array':{'path':'local-cache/all12-low-high-reference-traces.npz','bytes':(O/'local-cache/all12-low-high-reference-traces.npz').stat().st_size,'sha256':sha(O/'local-cache/all12-low-high-reference-traces.npz'),'upload_allowed':False},'primary':'all12-prediction-errors-144.csv','report':'README-all12.md'})
print(json.dumps({'frozen_Asia_Shanghai':now.astimezone(timezone(timedelta(hours=8))).isoformat(),'elapsed_seconds':(now-start).total_seconds(),'files':len(files),'new_fits':2,'error_rows':144,'max_partition_check_kN':max_part}))
