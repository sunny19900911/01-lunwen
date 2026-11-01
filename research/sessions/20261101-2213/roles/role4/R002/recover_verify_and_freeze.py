import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','2');os.environ.setdefault('OMP_NUM_THREADS','2')
from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):(O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def cs(n,rr):
 with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
rule=json.loads((O/'evaluation-rules-freeze.json').read_text(encoding='utf-8'));boundsfreeze=json.loads((O/'bounds-frozen-before-target-open.json').read_text(encoding='utf-8'));index=json.loads((O/'reference-truth-array-index.json').read_text(encoding='utf-8'));long=read(O/'frozen-prediction-vs-exact-reference-96.csv');wide=read(O/'all12-target-reference-comparison-wide-48.csv');intervals=read(O/'coth-interval-coverage-width-decisions-96.csv');oldpeak=read(O/'old-peak-first-order-baseline-comparison-48.csv');summary=read(O/'prediction-and-coth-bound-summary-8.csv');truthrows=read(O/'exact-reference-truth-peaks-48.csv');cost=read(O/'workload-and-measured-cost-ledger-8.csv');targets=rule['target_zetas'];assert [len(long),len(wide),len(intervals),len(oldpeak),len(summary),len(truthrows)]==[96,48,96,48,8,48]
for d in rule['inputs']:assert sha(Path(d['path']))==d['sha256']
assert sha(O/boundsfreeze['file'])==boundsfreeze['sha256']
prior=json.loads((P/'input-prediction-rules-freeze.json').read_text(encoding='utf-8'));presult=json.loads((P/'results.json').read_text(encoding='utf-8'));basepath=Path(prior['inputs'][0]['path']);senspath=Path(presult['local_only_output']['path']);maxP=maxD=maxNR=maxE=maxinterval=0.;checked=0
with np.load(basepath,allow_pickle=False) as base,np.load(senspath,allow_pickle=False) as sens:
 t=base['t'];om=base['omega'];B=base['B_direct'];V0=(base['s_unitGamma']*om**2)@B.T/1000;P0=np.max(abs(V0),axis=0);ZD=sens['zdot_unit'];WD=sens['wdot_unit']
 for truth in index:
  z=truth['zeta'];path=Path(truth['path']);assert sha(path)==truth['sha256']
  with np.load(path,allow_pickle=False) as a:
   assert np.array_equal(t,a['t']) and np.array_equal(om,a['omega']) and np.array_equal(B,a['B_direct']);true=a['shear_elastic_inertia_predicted_kN'] if z==.08 else a['shear_elastic_inertia_kN'];assert np.max(abs((a['s_unitGamma']*om**2)@B.T/1000-true))<1e-8
   for order in [1,2]:
    pred=sens[f'z{z:g}_order{order}_shear_inertia_kN'];delta=z-.05;rs=np.max(abs((2*om*delta**2*ZD) if order==1 else (om*delta**3*WD)),axis=0);coth=1/np.tanh(np.pi*z/(2*np.sqrt(1-z*z)));Eb=abs(B)@rs*coth/1000
    for j in range(12):
     story='Story'+str(j+1);d=next(d for d in long if float(d['target_zeta'])==z and int(d['Taylor_order'])==order and d['Story']==story);it=next(d for d in intervals if float(d['target_zeta'])==z and int(d['Taylor_order'])==order and d['Story']==story);pt=float(np.max(abs(true[:,j])));pp=float(np.max(abs(pred[:,j])));dt=1-pt/P0[j];dp=1-pp/P0[j];maxP=max(maxP,abs(pt-float(d['exact_reference_peak_kN'])),abs(pp-float(d['predicted_peak_kN'])));maxD=max(maxD,abs(100*(dp-dt)-float(d['decrease_error_percentage_points'])));nr=float(np.linalg.norm(pred[:,j]-true[:,j])/np.linalg.norm(true[:,j]));maxNR=max(maxNR,abs(nr-float(d['curve_signed_NRMSE'])));maxE=max(maxE,abs(float(Eb[j])-float(it['sampled_residual_coth_E_kN'])));DL=1-(pp+Eb[j])/P0[j];DU=1-max(0,pp-Eb[j])/P0[j];maxinterval=max(maxinterval,abs(DL-float(it['D_lower'])),abs(DU-float(it['D_upper'])));assert (float(it['D_lower'])-1e-12<=dt<=float(it['D_upper'])+1e-12)==(it['sampled_bound_peak_coverage']=='True');checked+=1
assert checked==96 and max(maxP,maxD,maxNR,maxE,maxinterval)<1e-8
schemes=[]
for z in targets:
 for order in [1,2]:
  rr=[d for d in intervals if float(d['target_zeta'])==z and int(d['Taylor_order'])==order];mathdecision='insufficient' if any(d['interval_decision']=='insufficient' for d in rr) else ('meets' if all(d['interval_decision']=='meets' for d in rr) else 'uncertain');flagged=sum(d['operational_full_recompute']=='True' for d in rr);schemes.append(dict(target_zeta=z,Taylor_order=order,mathematical_whole_building_decision=mathdecision,operational_flagged_layers=flagged,unique_full_building_recompute_count_if_all_flagged_layers_checked=int(flagged>0),scope='one target solve covers all floors; not one solve per flagged floor; early rejection alternative not timed'))
cs('candidate-level-recompute-accounting-8.csv',schemes)
worse=[d for d in wide if abs(float(d['order2_peak_relative_error']))>abs(float(d['order1_peak_relative_error']))];cs('order2-worse-than-order1-peak-cases.csv',worse);mis=[d for d in long if d['point_miss_insufficient']=='True'];cs('point-prediction-insufficient-miss-cases-2.csv',mis)
policy=next(d for d in rule['inputs'] if d['path'].endswith('engineering-policy-freeze-v001.json'));pol=json.loads(Path(policy['path']).read_text(encoding='utf-8'));policytime=datetime.fromisoformat(pol['actual_freeze']);boundtime=datetime.fromisoformat(boundsfreeze['frozen_utc']);newfiles=[d for d in index if d['zeta']!=.08];firstnew=min(datetime.fromtimestamp(Path(d['path']).stat().st_mtime,timezone.utc) for d in newfiles);assert policytime<boundtime<firstnew
truth_adverse=sum(d['truth_adverse_Dlt0']=='True' for d in truthrows);totalpointmiss=sum(d['point_miss_insufficient']=='True' for d in long);coverage=sum(d['sampled_bound_peak_coverage']=='True' for d in intervals)/96;curvecoverage=sum(d['sampled_bound_curve_coverage']=='True' for d in intervals)/96;phaseinfo=dict(policy_frozen_at=pol['actual_freeze'],bounds_frozen_at=boundsfreeze['frozen_utc'],first_new_truth_file_completed_utc=firstnew.isoformat(),priority_file_saved_utc=datetime.fromtimestamp((O/'Story5-Story12-priority-truth-and-predictions-8.csv').stat().st_mtime,timezone.utc).isoformat())
js('results.json',dict(completed_utc=datetime.now(timezone.utc).isoformat(),recovered_from_existing_small_tables_after_serialization_failure=True,no_truth_regenerated_during_recovery=True,targets=targets,new_exact_state_solves=3,reused8_exact_source=True,reference_truth_rows=48,prediction_comparison_rows=96,interval_rows=96,all300_prediction_order2_worse_peak_count=len(worse),truth_adverse_rows=truth_adverse,adverse_miss_rate=None if truth_adverse==0 else sum(d['point_miss_adverse']=='True' for d in long)/truth_adverse,point_insufficient_miss_rows=totalpointmiss,peak_interval_coverage=coverage,curve_interval_coverage=curvecoverage,summary=summary,timing_isolation=phaseinfo,bound_eval_seconds=boundsfreeze['bound_eval_seconds'],prediction_R001_unchanged=True,source_SHA_unchanged=True))
priority=[d for d in wide if d['Story'] in ['Story5','Story12']]
lines=['# SHW3X阻尼灵敏度预测与参考真值：首轮检验','',
'基准5%预测冻结后，生成6%、7%、10%的300阶精确线性参考响应；8%直接复用旧020同一模型的冻结结果。四个目标、12层全部对照，一、二阶预测均未回调。','',
'|候选ζ|Story5真值降幅 / %|一阶 / %|二阶 / %|Story12真值降幅 / %|一阶 / %|二阶 / %|','|---:|---:|---:|---:|---:|---:|---:|']
for z in targets:
 a=next(d for d in priority if float(d['target_zeta'])==z and d['Story']=='Story5');b=next(d for d in priority if float(d['target_zeta'])==z and d['Story']=='Story12');lines.append(f"|{z:.0%}|{float(a['exact_reference_decrease_percent']):.4f}|{float(a['order1_decrease_percent']):.4f}|{float(a['order2_decrease_percent']):.4f}|{float(b['exact_reference_decrease_percent']):.4f}|{float(b['order1_decrease_percent']):.4f}|{float(b['order2_decrease_percent']):.4f}|")
lines+=['','小增量下二阶预测较好；增量扩大后不能保证。候选10%的Story12，一阶峰误差5.07%，二阶达15.76%，二阶仍选21.18s而参考控制峰为'+next(d['exact_reference_peak_time_s'] for d in wide if float(d['target_zeta'])==.10 and d['Story']=='Story12')+'s。全48个层—目标组合中，二阶峰误差大于一阶有'+str(len(worse))+'例，全部单列保留。','',
'点预测在8%时有两项漏判改善不足：一阶将Story8预测为10.4378%，参考为9.9043%；二阶将Story3预测为10.5235%，参考为9.4371%。参考真值均无D<0案例，因此不利漏判率分母不适用，不能据“未漏判”声称能可靠排除不利响应。','',
'残差界仅采用一次预定的低成本计算：r₁=2ωΔζ²ż、r₂=ωΔζ³ẇ，取保存网格上的残差最大值，乘候选阻尼位移冲激核无穷L1范数ω⁻²coth[πζc/(2√(1−ζc²))]，再以|B|ω²/1000累加。该计算不使用候选真值；界与区间已先落盘，才读取或生成目标响应。','',
'|候选ζ|阶数|全层最大峰误差 / %|D区间中位宽 / 百分点|峰区间覆盖|操作复算层比例|','|---:|---:|---:|---:|---:|---:|']
for d in summary:lines.append(f"|{float(d['target_zeta']):.0%}|{d['Taylor_order']}|{100*float(d['max_absolute_peak_relative_error']):.4f}|{100*float(d['median_D_interval_width']):.4f}|{100*float(d['peak_interval_coverage']):.0f}%|{100*float(d['full_recompute_fraction']):.2f}%|")
lines+=['','全部96个峰区间及曲线尺度在本次参考响应上覆盖，但宽界不能当作预测成功。二阶6%时中位宽0.8243个百分点，操作上仅1/12层需复算；二阶7%时中位宽5.6546个百分点、9/12层需复算；8%和10%的两种阶次均要求全部楼层复算，工程筛选能力明显不足。下一轮应检验保留残差时变信息的局部卷积，不能把本次覆盖率直接作方法有效性的结论。','',
'工程政策在22:35由根冻结：Dreq=10%、允许D区间宽度5个百分点，均为演示要求。数学达标/不足/不确定与宽度分别保留；跨目标或过宽触发操作复算，宽但同在目标一侧仍保留数学分类。单个候选一次全楼分析覆盖全部楼层，费用没有按被标记楼层数重复计算。成本表列入一、二阶导数两个受迫系统、4次微扰导数检查、8次预测合成及8次残差界；R001未单独计时导数CPU，因而本轮不报告提速倍数。','',
'这里的真值是同一固定300阶线性模型和原输出网格的精确递推参考，不是实际FNA原生逐阶响应。残差使用采样最大值，未增加采样间极值及基准/导数数值残差的定向认证，区间覆盖只作本轮数值检验。旧峰时一阶基线和全时程一阶均已对同一真值评价，不能只在旧峰时刻代入就保证候选峰。']
(O/'one-page-validation-and-bound-result.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
notes=['# 运行、隔离、失败与费用记录','',
'本次R001预测冻结14:28:46Z在先；根工程政策22:35+08冻结；R002残差界先冻结，随后才读取8%数组及生成新目标响应。具体时间见results.json.timing_isolation。旧8%属于历史已知案例，不称盲测。','',
'首个完整数值运行已生成所有3份新真值、48行参考、96行预测对照、48行旧峰基线、96行区间和成本表，随后写results.json时因NumPy int64不可JSON序列化退出1。科学输出完整保留；本恢复脚本只从已保存表/数组重构汇总并独立复核，没有重跑任何真值或修改R001。原失败程序保留作为实际执行记录。','',
'微扰导数检查属于R001准备成本，不能漏掉；本R002bound_eval_seconds='+str(boundsfreeze['bound_eval_seconds'])+'。参考6/7/10的精确状态求解和输出合成各约0.06s，存储/I/O另算；8%只记录旧数组读取成本。R001导数与预测没有独立数值计时，不能将本轮界的低计时单独宣传成端到端优势。','',
'candidate-level-recompute-accounting-8.csv同时列数学全楼分类和操作标记层数；如所有标记层都检查，一个ζ仍只计一次全楼复算。是否在已知某层不足时提前舍弃整个候选属于后续整体策略，本轮未据此重算有利费用。','',
'r公式均以s为位移单位核，ż/ẇ为其阻尼导数的时间导数；输出乘Bω²/1000，未混用g=ω²s再重复乘ω²。coth取候选ζ，不取基准ζ。所有真值、导数和原预测完整数组只本地，Git排除local-cache。']
(O/'run-isolation-and-cost-notes.md').write_text('\n'.join(notes)+'\n',encoding='utf-8')
for d in rule['inputs']:assert sha(Path(d['path']))==d['sha256']
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-11-01T14:33:19+00:00')).total_seconds();assert elapsed<900
v=dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,within_primary12_minutes=elapsed<720,reference_truth_rows=48,comparison_rows_recomputed=96,new_exact_state_solves=3,reused_old_exact8=True,recovery_added_truth_solves=0,prediction_R001_bytes_unchanged=True,policy_before_current_target_production=True,timing_isolation=phaseinfo,max_peak_recheck_difference_kN=maxP,max_D_error_recheck_difference_pp=maxD,max_NRMSE_recheck_difference=maxNR,max_coth_E_equivalent_formula_difference_kN=maxE,max_D_interval_formula_difference=maxinterval,peak_coverage=coverage,curve_coverage=curvecoverage,order2_worse_peak_cases=len(worse),truth_adverse_count=truth_adverse,adverse_miss_denominator_not_applicable=truth_adverse==0,no_local_convolution_or_bound_retuning=True,no_Git=True,sampled_residual_not_continuous_certificate=True)
js('verification.json',v);files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json'];js('delivery-manifest.json',dict(frozen_utc=now.isoformat(),outputs=files,inputs=rule['inputs'],target_reference_arrays=index,complete_arrays_local_only=True,array_upload_allowed=False));print(json.dumps(v,ensure_ascii=False,indent=2))
