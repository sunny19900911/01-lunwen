from pathlib import Path
from datetime import datetime,timezone,timedelta
from time import perf_counter
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R004'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def cs(n,rows):
    with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
rules=json.loads((O/'evaluation-inputs-rules-freeze.json').read_text(encoding='utf-8'));res=json.loads((O/'results.json').read_text(encoding='utf-8'));cost=json.loads((O/'pipeline-cost-results.json').read_text(encoding='utf-8'));idx=json.loads((O/'target-array-index.json').read_text(encoding='utf-8'));assert all(sha(Path(d['path']))==d['sha256'] for d in rules['inputs']);assert all(sha(Path(d['path']))==d['sha256'] for d in idx)
with np.load(P/'local-cache/baseline-sensitivities-and-frozen-predictions.npz',allow_pickle=False) as a:
    t=a['t'].copy();ag=a['ag_in_s2'].copy();B=a['B'].copy();om=a['omega'].copy();s0=a['s_unit'].copy();PV={(z,o):a[f'z{z:g}_order{o}_shear_kip'].copy() for z in [.06,.07,.08,.10] for o in [1,2]}
# Explicitly add baseline output/peak preparation, absent from prior replay timer.
clock=perf_counter();V0=(s0*om**2)@B.T;P0=np.max(abs(V0),axis=0);baselineoutput=perf_counter()-clock
adjusted=[]
for d in cost['summary']:
    new=dict(d);new['baseline_output_and_peak_seconds']=baselineoutput;new['total_measured_component_seconds']=d['total_measured_component_seconds']+baselineoutput;new['method_to_direct_cost_ratio']=new['total_measured_component_seconds']/d['direct4_complete_core_plus_commonprep_seconds'];adjusted.append(new)
cs('fair-pipeline-cost-including-baseline-output-4.csv',adjusted)
with np.load(P/'local-cache/frozen-discrete-envelopes.npz',allow_pickle=False) as a:ENV={(z,o):a[f'z{z:g}_order{o}_E_kip'].copy() for z in [.06,.07,.08,.10] for o in [1,2]}
refs=rd(O/'exact-reference-floor-peaks-12.csv');predrows=rd(O/'frozen-prediction-vs-reference-24.csv');intervals=rd(O/'interval-coverage-width-decisions-24.csv');maxpeak=maxD=maxmetric=0.;strictuncovered=0;trueadverse=0
for entry in idx:
    z=entry['target_zeta']
    with np.load(entry['path'],allow_pickle=False) as a:
        assert np.array_equal(t,a['t']) and np.array_equal(ag,a['ag_in_s2']) and np.array_equal(om,a['omega']) and np.array_equal(B,a['B']);Q=a['s_unit'].copy();V=a['shear_kip'].copy()
    assert np.max(abs(V-(Q*om**2)@B.T))<1e-10
    for j in range(3):
        story=f'Story{j+1}';ip=int(np.argmax(abs(V[:,j])));pt=float(abs(V[ip,j]));dd=1-pt/P0[j];r=next(d for d in refs if float(d['target_zeta'])==z and d['Story']==story);maxpeak=max(maxpeak,abs(pt-float(r['reference_abs_peak_kip'])));maxD=max(maxD,abs(dd-float(r['reference_D'])));assert float(r['reference_signed_value_at_abs_peak_kip'])==float(V[ip,j]);assert float(r['reference_peak_time_s'])==float(t[ip]);trueadverse+=int(dd<0)
        for order in [1,2]:
            ph=float(np.max(abs(PV[z,order][:,j])));ir=next(d for d in intervals if float(d['target_zeta'])==z and int(d['Taylor_order'])==order and d['Story']==story);pr=next(d for d in predrows if float(d['target_zeta'])==z and int(d['Taylor_order'])==order and d['Story']==story);maxmetric=max(maxmetric,abs(float(pr['peak_relative_error'])-(ph/pt-1)),abs(float(pr['signed_curve_NRMSE'])-np.linalg.norm(PV[z,order][:,j]-V[:,j])/np.linalg.norm(V[:,j])));strictuncovered+=int(np.count_nonzero(abs(PV[z,order][:,j]-V[:,j])>ENV[z,order][:,j]));lo=float(np.max(np.maximum(0,abs(PV[z,order][:,j])-ENV[z,order][:,j])));up=float(np.max(abs(PV[z,order][:,j])+ENV[z,order][:,j]));assert abs(lo-float(ir['P_lower_kip']))<1e-10 and abs(up-float(ir['P_upper_kip']))<1e-10;assert (ir['peak_covered']=='True')==(lo<=pt<=up)
assert maxpeak==0 and maxD==0 and maxmetric<1e-12
candidate=rd(O/'candidate-v001-v002-decision-validation-8.csv')
for r in candidate:
    z=float(r['target_zeta']);o=int(r['Taylor_order']);ir=[d for d in intervals if float(d['target_zeta'])==z and int(d['Taylor_order'])==o];reject=any(d['decision_status']=='insufficient' for d in ir);passed=all(d['decision_status']=='meets' and d['width_status']=='acceptable' for d in ir);action='reject' if reject else ('pass' if passed else 'recompute');assert action==r['v002_candidate_action'];assert int(r['v001_building_recompute'])==int(any(d['v001_operational_recompute']=='True' for d in ir))
verification=dict(completed_utc=datetime.now(timezone.utc).isoformat(),truth_rows_recomputed=12,prediction_rows_recomputed=24,interval_rows_recomputed=24,candidate_actions_recomputed=8,max_truth_peak_difference_kip=maxpeak,max_truth_D_difference=maxD,max_prediction_metric_difference=maxmetric,strict_uncovered_curve_samples=strictuncovered,true_adverse_cases=trueadverse,source_prediction_policy_hashes_unchanged=True,target_array_hashes_unchanged=True,extra_finite_target_state_solves=0,cost_replay_baseline_and_derivatives_only=True,static_audit_passed=True,independent_dynamic_auditor_review_pending=True)
js('verification.json',verification)
miss=[d for d in predrows if d['point_miss_insufficient']=='True'];falsead=[d for d in predrows if d['point_false_adverse']=='True'];wider=[d for d in rd(P/'discrete-and-coth-prediction-intervals-24.csv') if d['discrete_wider_than_coth']=='True'];wide=rd(O/'all3-reference-and-prediction-wide-12.csv');worse=[d for d in wide if abs(float(d['order2_peak_relative_error']))>abs(float(d['order1_peak_relative_error']))];cs('point-insufficient-miss-cases-1.csv',miss);cs('point-false-adverse-cases-4.csv',falsead);cs('second-order-worse-peak-cases-2.csv',worse)
old=rd(O/'old-time-first-order-comparison-12.csv');oldwins=newwins=ties=0
for d in old:
    p=next(e for e in predrows if e['target_zeta']==d['target_zeta'] and e['Story']==d['Story'] and e['Taylor_order']=='1');diff=abs(float(p['peak_relative_error']))-abs(float(d['peak_relative_error']))
    if abs(diff)<1e-12:ties+=1
    elif diff<0:newwins+=1
    else:oldwins+=1
summary=res['summary'];text=['# 公开框架候选验证与完整成本比较','',
'四个冻结候选参照已完成。离散包络覆盖24组峰值及全部采样曲线，但较大阻尼增量的区间仍宽。二阶点预测在ζ=.08屋面漏判一次改善不足；ζ=.10时二阶两层的峰值误差反而更大。事先冻结的区间策略没有错误放行或错误拒绝，不过完整预测流程在本实现中仍比四候选直接全解慢。','',
'## 计算对象与隔离','',
'采用经②静态独审通过的公开Example5三层三跨框架参数，保留12独立水平质量自由度和全部12阶，柱脚转动自由；输入为H-E12140真实地震记录。该对象是公开教学框架的自写线性重构，不是实测建筑或OpenSees运行结果。输入、时间轴、5%基准、候选6/7/8/10%、两阶预测及工程阈值全部沿用R004，未回调。单位为in/kip/s，ag=原g×386.4，dt=.005s、全7802点至39.005s。','',
'本轮仅生成4组候选参照状态。弹性剪力分别由Bω²s和C(PhiΓs)计算，未除1000或重复乘Γ；后者作为独立物理输出核查，计时另列。双输出相对L2差最大'+f"{res['max_dual_output_relative_L2']:.3e}"+'。完整数组仅保存在local-cache。','',
'## 真实减震率与预测误差','',
'|ζ|Story1参照减震率/%|Story2/%|Story3/%|','|---|---|---|---|']
for z in [.06,.07,.08,.10]:
    rr=[next(d for d in refs if float(d['target_zeta'])==z and d['Story']==f'Story{j}') for j in [1,2,3]];text.append(f'|{z:.2f}|'+ '|'.join(f"{float(d['reference_decrease_percent']):.3f}" for d in rr)+'|')
text+=['','|ζ|阶次|最大峰值相对误差/%|区间宽度中位数/百分点|v001全楼复算|v002动作|','|---|---|---|---|---|---|']
for d in summary:text.append(f"|{d['target_zeta']:.2f}|{d['Taylor_order']}|{100*d['max_absolute_peak_relative_error']:.3f}|{d['median_D_width_pp']:.3f}|{d['v001_building_recompute']}|{d['v002_action']}|")
text+=['','ζ=.08二阶屋面点预测减震11.195%，参照为7.337%，超过10%的点判断造成一次改善不足漏判；区间仍为不确定并触发复算。ζ=.10时一阶把实际均达到10%的三层全部误判为不足。二阶虽给出超过10%的点值，Story1/Story2的峰值误差达到16.665%/14.538%，且Story2预测控制峰为10.530s的正剪力，参照控制峰为16.525s的负剪力，时间相差5.995s。二阶更差的2个峰值样本全部保留。','',
'四个候选的12个楼层参照均没有D<0；一阶Story1的4个负降幅点预测均为误报。所有参照绝对峰对应有符号负剪力，这与D<0是不同概念；CSV同时保存正最大值、负最小值、控制峰符号和时刻。不利响应漏判率分母为N/A，不能把零真实不利样本写成安全通过。','',
f'旧峰一阶与完整时程一阶比较，完整时程峰值误差更小{newwins}项、更大{oldwins}项、相同{ties}项；完整输出保留，未宣称逐项支配。','',
'## 区间与候选决策','',
'24/24峰值、24/24完整采样曲线均严格覆盖，逐样本未覆盖数为0；coth对照也全部覆盖。未更改保护量、阈值或两阶预测，未以真值选择界。区间仍只覆盖保存时刻，未获得连续极值或严格浮点证明。','',
'v002一阶拒绝前三个候选、只复算ζ=.10；二阶拒绝ζ=.06/.07、复算.08/.10。前三候选确实不能满足全三层10%要求，最后候选确实全部达到；候选错误放行、错误拒绝均为0。对拒绝的候选不要求所有楼层给出精确数值，宽度超限记录仍保留。v001原策略分别需3次和2次全楼分析；一次分析覆盖所有楼层，层数不是求解次数。','',
'## 公平计算成本','',
'采用同一runtime的一次计时，以原始记录解析、基准状态、导数、4候选预测、缺陷核/FFT、区间分类和触发的完整分析组成总工作量。成本重放只计算基准与灵敏度，预测和包络与R004逐字数值一致；没有为计时新增候选状态。条件复算成本取本轮4次实际完整求解的相应计时。因此下表为实际测得组件之和，并非一次不间断端到端秒表；不伪称额外完整流程运行。','',
'|阶次|策略|触发全楼求解|流程组件合计/s|4候选直接全解/s|成本比（大于1更慢）|','|---|---|---|---|---|---|']
for d in adjusted:text.append(f"|{d['Taylor_order']}|{d['policy']}|{d['triggered_building_solves']}|{d['total_measured_component_seconds']:.6f}|{d['direct4_complete_core_plus_commonprep_seconds']:.6f}|{d['method_to_direct_cost_ratio']:.3f}|")
text+=['','各候选的完整状态、弹性输出和峰值指标合计实测'+f"{res['new_target_compute_core_seconds']:.6f}s"+'；共同原始输入准备'+f"{adjusted[0]['common_input_preparation_seconds']:.6f}s"+'，直接比较总计'+f"{adjusted[0]['direct4_complete_core_plus_commonprep_seconds']:.6f}s"+'。重放基准状态'+f"{adjusted[0]['baseline_state_seconds']:.6f}s"+'，一阶导数'+f"{adjusted[0]['first_derivative_seconds']:.6f}s"+'，另二阶导数'+f"{adjusted[2]['second_derivative_seconds']:.6f}s"+'，另补基准输出及寻峰'+f'{baselineoutput:.6f}s'+'。每种独立方法均计入全部核设置，未把二阶共享核误记为免费。','',
'验证开销与可选归档不混入算法比较：本轮双物理输出核查'+f"{res['dual_output_check_seconds']:.6f}s"+'，4份完整参照数组压缩写入'+f"{res['target_local_write_seconds']:.6f}s"+'；源散列、预测缓存恢复、独立复核与脚本启动另列。内核与归档开销均保留。一次运行的绝对秒数受系统负载影响，不作硬件普遍结论。当前组件比较已显示没有提速，减少完整求解次数不能替代总成本下降。','',
'核查：12组真值峰、24组误差、24组区间和8组候选动作由保存数组复核，未新增目标求解；R004预测/区间/政策散列及本轮4个参照数组散列一致。②后续动态独审仍待完成，④核查不替代独审。']
(O/'one-page-public-validation-and-cost-result.md').open('x',encoding='utf-8').write('\n'.join(text)+'\n')
notes=['# 运行、计时与隔离记录','',
'实际开始2026-11-01T15:15:48UTC（23:15:48+08）；8分钟15:23:48UTC，主要12分钟15:27:48UTC，15分钟硬限15:30:48UTC。小表于15:17:42.477079UTC保存，约114.48s。四个参照仅生成一次，后续目标数组只读。','',
'实际命令依次为python.exe -X utf8加evaluate_public_frozen_predictions.py、measure_frozen_prediction_pipeline_cost.py、verify_report_and_freeze.py，全部在R005执行；退出状态以工具结果为准。完整数组只进local-cache，未运行OpenSees/ETABS/YJK，未开新参数/记录/模型或读取外部账户。','',
'代价定义：complete_candidate_core_seconds是输入已在内存时的候选完整状态求解+一个物理输出+峰值/决策指标。公共源输入解析另加到两边；第二物理输出为验证，归档写盘另记。条件流水线以真实测得组件加总，不声称single-wall端到端实跑。原fair-complete-pipeline-vs-direct-cost-4.csv未含基准输出/寻峰，新的fair-pipeline-cost-including-baseline-output-4.csv显式补齐，旧文件保持不动。','',
'重放的基准、Z/ZD、W/WD和候选预测、包络与R004最大差均为0；不含目标响应重放。first/second导数独立计时，二阶准备包含一阶；每个单独方法每候选都计核设置。输入/导数实现与对照直接求解同为NumPy/既有exact helper。未按计时挑选最好重复值。','',
'小表冻结后只进行有限验证及成本报告。R004全部字节保持；本轮冻结后如有修正应以新文件/新manifest交付。']
(O/'run-isolation-and-cost-notes.md').open('x',encoding='utf-8').write('\n'.join(notes)+'\n')
stamp=datetime.now(timezone.utc);elapsed=(stamp-datetime.fromisoformat('2026-11-01T15:15:48+00:00')).total_seconds();js('delivery-manifest.json',dict(actual_freeze_utc=stamp.isoformat(),actual_freeze_plus08=stamp.astimezone(timezone(timedelta(hours=8))).isoformat(),elapsed_seconds=elapsed,within8min=elapsed<=480,within12min=elapsed<=720,within15min=elapsed<=900,files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file()],local_only_arrays=idx,new_target_reference_solves=4,extra_target_solves_after_small_freeze=0,R004_hashes_unchanged=True,independent_dynamic_audit_pending=True))
print(json.dumps(dict(frozen_utc=stamp.isoformat(),elapsed_seconds=elapsed,verification=verification,cost=adjusted),ensure_ascii=False,indent=2))
