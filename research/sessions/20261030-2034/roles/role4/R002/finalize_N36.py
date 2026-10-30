from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def cs(n,rows):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(n,d):
 with (O/n).open('x',encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
rules=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));metrics=read(O/'prediction-errors-N36-24.csv');groups=read(O/'N24-to-N36-common-group-curves-96.csv');cond=read(O/'models-condition-2.csv');stable=read(O/'rcond-stability-2.csv');assert len(metrics)==24 and len(groups)==96
agg=[]
for story in ['Story5','Story12']:
 for group in ['1to3','4to6','7to12','13to24']:
  rr=[q for q in groups if q['variant']=='N36_elastic_rc1e-10' and q['Story']==story and q['group']==group];assert len(rr)==6
  agg.append({'Story':story,'group':group,'max_curve_difference_L2_over_native_L2':max(float(q['difference_L2_over_native_L2']) for q in rr),'max_curve_difference_L2_over_N24_group_L2':max(float(q['difference_L2_over_N24_group_L2']) for q in rr),'N24_group_RMS_min_kN':min(float(q['N24_group_RMS_kN']) for q in rr),'N24_group_RMS_max_kN':max(float(q['N24_group_RMS_kN']) for q in rr),'max_curve_difference_RMS_kN':max(float(q['difference_RMS_kN']) for q in rr),'summary_scope':'max over3 cases and2 damping states; two rconds separately retained and identical'})
cs('group-stability-summary-8.csv',agg)
high=[];maxerr=0.
with np.load(O/'local-cache/N36-elastic-two-rcond-traces.npz',allow_pickle=False) as z,np.load(P/'local-cache/N24-two-operator-traces.npz',allow_pickle=False) as old:
 for q in metrics:
  tag=f"{q['variant']}__{q['Case']}__{q['Story']}__z{float(q['zeta']):g}";y=z[tag+'__native'];pred=z[tag+'__prediction'];terms=z[tag+'__terms'];err=float(np.linalg.norm(pred-y)/np.linalg.norm(y));maxerr=max(maxerr,abs(err-float(q['NRMSE'])))
  assert abs(err-float(q['NRMSE']))<1e-12 and np.max(abs(terms.sum(1)-pred))<1e-6
  assert math.isclose(np.max(abs(pred))/np.max(abs(y))-1,float(q['peak_relative_error']),rel_tol=1e-10,abs_tol=1e-12)
  if q['variant']=='N36_elastic_rc1e-10':
   a=old[f"elastic__{q['Case']}__{q['Story']}__z{float(q['zeta']):g}__terms"][:,12:24].sum(1);b=terms[:,12:24].sum(1);c=terms[:,24:36].sum(1);joint=b+c;it=int(np.argmax(abs(y)));den=float(np.linalg.norm(y))
   high.append({'Case':q['Case'],'Story':q['Story'],'zeta':q['zeta'],'native_RMS_kN':float(np.sqrt(np.mean(y*y))),'N24_group13to24_RMS_kN':float(np.sqrt(np.mean(a*a))),'N36_group13to24_RMS_kN':float(np.sqrt(np.mean(b*b))),'N36_added25to36_RMS_kN':float(np.sqrt(np.mean(c*c))),'N36_combined13to36_RMS_kN':float(np.sqrt(np.mean(joint*joint))),'combined_high_change_L2_over_native_L2':float(np.linalg.norm(joint-a)/den),'native_peak_time_s':float(z[tag+'__t'][it]),'N24_high_signed_at_native_peak_kN':float(a[it]),'N36_common13to24_signed_at_native_peak_kN':float(b[it]),'N36_added25to36_signed_at_native_peak_kN':float(c[it]),'N36_combined13to36_signed_at_native_peak_kN':float(joint[it]),'scope':'fitted high-block compensation diagnostic, not proof of physical high-mode cancellation'})
cs('high-block-compensation-12.csv',high)
text=['# 一次N36 elastic扩阶检查：低阶组小变，高阶分配未收敛','',
'只新增N36 elastic，rcond=1e-10/1e-8并列。保持SHW3X+SHW4X原生5%训练、RH4X整波留出，8%三波固定同一输出映射，不重新拟合。冻结N24仅从已有系数和时程读取，未重跑6/12/24或任何其他N。','',
'两rcond的系数和预测逐点相同，训练缩放矩阵秩均36；完整/保留条件数均约4.558×10⁷，最小/最大奇异值比约2.194×10⁻⁸。因此本测试两cutoff相同不代表参数具有广泛稳健性，更不能据满秩认证物理逐阶可辨识。','',
'| 层 | 5%留出RH4 NRMSE | 8%三波NRMSE范围 | 8%峰差范围 |','|---|---:|---:|---:|']
for story in ['Story5','Story12']:
 hh=next(q for q in metrics if q['variant']=='N36_elastic_rc1e-10' and q['Story']==story and q['evaluation']=='heldout5');rr=[q for q in metrics if q['variant']=='N36_elastic_rc1e-10' and q['Story']==story and q['evaluation']=='fixed_map8'];nr=[100*float(q['NRMSE']) for q in rr];pe=[100*float(q['peak_relative_error']) for q in rr]
 text.append(f"| {story} | {100*float(hh['NRMSE']):.3f}% | {min(nr):.3f}%—{max(nr):.3f}% | {min(pe):+.3f}%—{max(pe):+.3f}% |")
text+=['',
'Story12较N24继续改善：5%留出4.384%→2.951%，8%范围2.576%—5.033%→1.123%—2.406%。Story5的8%范围1.328%—1.763%→0.861%—1.420%。这些是固定输出参照对原生曲线的误差，不是辨识出的真实单阶误差。','',
'## 共同组N24→N36变化','',
'以下为三波、两ζ六条曲线中的最大相对L2差。前一分母为原生整层曲线，后一分母为N24该组自身曲线；另列绝对RMS变化，防止小组造成相对量夸大。','',
'| 层/共同组 | 差/原生L2最大 | 差/组自身L2最大 | 差RMS最大/kN |','|---|---:|---:|---:|']
for q in agg:text.append(f"| {q['Story']}/{q['group']} | {100*q['max_curve_difference_L2_over_native_L2']:.4f}% | {100*q['max_curve_difference_L2_over_N24_group_L2']:.3f}% | {q['max_curve_difference_RMS_kN']:.4f} |")
text+=['',
'共同1—3、4—6、7—12组相对原生曲线变化均不超过0.166%；但Story5的4—6小组相对自身仍可变化7.68%，不能将整层尺度下小变称作每个系数都稳定。13—24组则明显随扩阶重新分配：Story5变化最高为原生L2的11.524%，Story12为71.830%；相对组自身最高为435.259%、122.445%。','',
'新增25—36阶与原13—24阶之间出现拟合补偿，12条高阶块同刻值及RMS已另存。这说明总曲线更准与高阶组分配收敛是不同问题。当前可优先讨论上述共同低阶组在既定参照内的变化；13—24及新增高阶只能连同补偿/截断残差说明，不单独包装为真实模态控制机制。按任务约定到此停止扩阶，不继续追更大N。','',
'## 文件与复算','',
'prediction-errors-N36-24.csv保留两个rcond全部误差、峰差、原生源行和N24对照；N24-to-N36-common-group-curves-96.csv及group-stability-summary-8.csv给共同组；high-block-compensation-12.csv给高阶补偿；models-condition-2.csv与rcond-stability-2.csv给秩/病态性。两个模型和144条系数为小产物。全部时程只在local-cache/N36-elastic-two-rcond-traces.npz，禁止上传。','',
'实际命令：python -X utf8 run_N36_check.py，然后python -X utf8 finalize_N36.py。同根冻结源/ω/单位/零初值，ag不再倍率；无原件大提取、ETABS/API、Git或旧拟合重跑。结果待独审，仍分类fitted-model。']
(O/'README-N36-stability.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
for b in rules['source']:assert sha(Path(b['path']))==b['sha256']
for b in rules['frozen_N24_inputs']:assert sha(Path(b['path']))==b['sha256']
assert sha(O/'run_N36_check.py')==rules['code_sha256']
now=datetime.now(timezone.utc);start=datetime.fromisoformat(rules['start_observed_utc']);assert now<=datetime.fromisoformat(rules['deadline_utc'])
js('verification.json',{'verified_utc':now.isoformat(),'only_new_N':36,'operator':'elastic','rconds':[1e-10,1e-8],'prediction_rows':24,'common_group_rows':96,'aggregate_rows':8,'high_block_rows':12,'new_models':2,'rank_both':36,'rcond_models_and_predictions_identical':all(float(q['max_abs_prediction_rcond_difference_kN'])==0 and float(q['N36_rcond_raw_coef_relative_L2'])==0 for q in stable),'metrics_recomputed_from_saved_arrays':True,'max_NRMSE_recheck_difference':maxerr,'native8_no_refit':True,'N6_N12_N24_not_refitted':True,'all_frozen_sources_and_code_unchanged':True,'full_arrays_local_only':True,'further_N_extension_not_performed':True,'classification':'fitted-model; stable outputs do not certify true modal decomposition'})
files=[{'name':p.name,'bytes':p.stat().st_size,'last_modified_utc':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),'sha256':sha(p)} for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
js('delivery-manifest.json',{'status':'complete single N36 stability check, independent review pending','frozen_utc':now.isoformat(),'frozen_Asia_Shanghai':now.astimezone(timezone(timedelta(hours=8))).isoformat(),'elapsed_seconds':(now-start).total_seconds(),'within10_minutes':True,'files':files,'local_only_array':{'path':'local-cache/N36-elastic-two-rcond-traces.npz','bytes':(O/'local-cache/N36-elastic-two-rcond-traces.npz').stat().st_size,'sha256':sha(O/'local-cache/N36-elastic-two-rcond-traces.npz'),'upload_allowed':False},'main_errors':'prediction-errors-N36-24.csv','report':'README-N36-stability.md'})
print(json.dumps({'frozen_Asia_Shanghai':now.astimezone(timezone(timedelta(hours=8))).isoformat(),'elapsed_seconds':(now-start).total_seconds(),'files':len(files),'within10_minutes':True}))
