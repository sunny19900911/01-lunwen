from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
O=Path(__file__).resolve().parent
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
res=json.loads((O/'results.json').read_text(encoding='utf-8'));fr=json.loads((O/'prediction-S-envelope-freeze.json').read_text(encoding='utf-8'));ver=json.loads((O/'verification.json').read_text(encoding='utf-8'));sr=rd(O/'baseline-S-ranked-floors-12.csv');ref=rd(O/'exact-reference-floor-peaks-24.csv');iv=rd(O/'interval-coverage-and-decision-validation-48.csv');cands=rd(O/'candidate-decision-validation-4.csv');miss=rd(O/'point-insufficient-miss-cases-1.csv');pairs=rd(O/'posterior-rank-inversion-pairs-4.csv');ranks=rd(O/'posterior-S-vs-reference-ranks-24.csv')
assert len(miss)==1 and len(pairs)==4
truthpass={z:all(float(d['reference_D'])>=.1 for d in ref if float(d['target_zeta'])==z) for z in [.06,.07]}
for r in cands:assert (r['true_all12_meet']=='True')==truthpass[float(r['target_zeta'])]
passed=[d for d in cands if d['v002_action']=='pass'];falsepassed=[d for d in passed if d['false_pass']=='True'];adverse=sum(float(d['reference_D'])<0 for d in ref)
passiv=[d for d in iv if float(d['target_zeta'])==.07 and d['Taylor_order']=='2'];minimum_lower=min(float(d['D_lower']) for d in passiv);maxwidth=max(float(d['D_width']) for d in passiv);minimumtruth=min(float(d['reference_D']) for d in ref if float(d['target_zeta'])==.07)
assert len(passed)==1 and not falsepassed and minimum_lower>=.1 and maxwidth<=.05 and minimumtruth>=.1
table=['# RH4X基准敏感度工程主表','', '全部300阶、5%基准，同一控制峰的c有符号和闭合S。S与c单位均为剪力降幅百分数/阻尼百分点。','', '|排序|楼层|控制峰时/s|S|主5项：阶号:c|其余295阶之和|','|---|---|---|---|---|---|']
for r in sr:table.append(f"|{r['slow_improvement_rank']}|{r['Story']}|{r['controller_times_s']}|{float(r['S_percent_per_damping_pp']):.6f}|{r['top5_signed_c']}|{float(r['remaining_signed_c_sum']):+.6f}|")
(O/'engineering-main-table-RH4X12.md').open('x',encoding='utf-8').write('\n'.join(table)+'\n')
text=['# RH4X第三个原有输入：预测、排序与通过候选','',
'RH4X的最慢改善层为Story7，5%基准S与6%/7%完整参照均定位到该层；但其余层间排序仍各有2对倒置。第5层基准排第4、有限目标排第3；屋顶基准也不是最快层。7%二阶区间按预定10%目标、5个百分点宽度要求判全楼通过，完整参照确认12层均达标。本轮保留该通过案例及6%一阶点预测的一次改善不足漏判。','',
'## 输入、算法及冻结顺序','',
'只读旧020/R004中actual300-RH4X-z0.05-factorized-reference.npz，SHA256为2354441c71c1bf4e714c26d43af7b103c443419be8578bf775c47466a604cae5，与旧清单一致。2501点、名义dt=.02s、0—50s；原ag已是m/s²，PGA=.35，不加SF/g。5%单位核初位移、初速度为零，所有300阶ω/B与SHW3X完全一致，不重生截断Ritz。剪力Bω²s/1000为kN，不重复Γ。','',
'复用R007已冻结数值算法，只替换输入路径、散列、点数、时窗和本轮时间；近峰计数显式转Python int仅修正上一轮末尾控制台摘要错误，不改变任何数值方法。仍用同一解析阻尼导数、完整时程预测、绝对离散状态缺陷FFT包络和工程浮点保护。','',
'预测、S、主模态、两目标逐时区间及候选动作于'+fr['frozen_utc']+'冻结，之后恰生成6%/7%两套完整线性参照。未读取旧8%数组或以目标选择模态、改阈值；RH4历史响应曾见，这只是第三个原有输入的预定前瞻计算顺序，不称全新地震盲测。','',
'## 最慢层与模态来源','',
'|楼层|S|基准慢改善排名|主要有符号贡献|','|---|---|---|---|']
for st in ['Story7','Story6','Story4','Story5','Story12','Story11']:
    r=next(d for d in sr if d['Story']==st);text.append(f"|{st}|{float(r['S_percent_per_damping_pp']):.6f}|{r['slow_improvement_rank']}|{r['top5_signed_c']}|")
text+=['','Story7主要由2阶+7.820557与3阶+.556410促进，4阶−.461815、10阶−.087495抵消，全部正项+8.850028与负项−.618759相加得到S=8.231270。第5层S=8.554316，2阶+7.020151为主促进；本轮不能沿用SHW3X“第5层最慢”的结论。屋顶S=10.928792，慢改善排名10，而Story11为12.495508、排名12，故屋顶也不是所有输入下一贯最快层。所有c仍是基准控制峰导数来源，不是有限候选的真实剪力分配。','',
'|ζ|S最慢层|参照最慢层|第5层参照排名|倒置对数/66|Spearman|','|---|---|---|---|---|---|']
for d in res['rank_validation']:text.append(f"|{d['target_zeta']:.2f}|{d['baseline_slowest']}|{d['reference_slowest']}|{d['Story5_reference_rank']}|{d['strict_inversions']}|{d['Spearman_no_ties_rho']:.6f}|")
text+=['','四对后验倒置逐项保留，不因最慢层定位正确就宣称全部层序保持。精确活动峰和容差近峰分开；所有楼层精确控制峰均只有1个，旧1%诊断保留Story2的一个独立竞争峰，同时每层前5个局部峰无论是否进入1%均保留。','',
'## 两目标预测与区间','',
'|ζ|阶次|最大峰值相对误差/%|最大降幅误差/百分点|区间宽度中位数/百分点|v001复算层数|v002动作|','|---|---|---|---|---|---|---|']
for d in res['summary']:text.append(f"|{d['target_zeta']:.2f}|{d['Taylor_order']}|{100*d['max_abs_peak_relative_error']:.3f}|{d['max_abs_D_error_pp']:.3f}|{d['median_D_width_pp']:.3f}|{d['v001_recompute_floors']}/12|{d['v002_action']}|")
text+=['','48/48峰值及48/48完整保存曲线均严格覆盖，未覆盖采样点数为0。两阶均拒绝6%；7%一阶要求完整复算、二阶直接通过。完整参照核对上述拒绝/通过均正确，没有候选误放行或错误拒绝。','',
f"7%二阶的全楼区间下限最小为{100*minimum_lower:.6f}%，最大宽度{100*maxwidth:.6f}个百分点；完整参照全楼减震率最小{100*minimumtruth:.6f}%（Story7），高于10%演示目标。宽度与目标判断分别满足要求，故通过来自原规则，并非看真值后放宽标准。",'',
'本轮有1个通过的方法/目标组合，错误放行数0/1；这是同一输入的一个通过案例，不能解释为可靠性概率估计。没有真实D<0样本，不利漏判率仍为N/A。6%一阶点预测漏判如下，区间没有误放行：','', '|楼层|点预测减震/%|完整参照减震/%|','|---|---|---|']
for d in miss:text.append(f"|{d['Story']}|{100*float(d['predicted_D']):.6f}|{100*float(d['reference_D']):.6f}|")
text+=['','## 核查与实际工作量','',
f"12层S、3600条模态来源和60个主项保留；有符号闭合最大误差{ver['max_modal_closure_error']:.3e}。24组参照峰、48组误差/区间、4组候选动作、4对排序倒置由保存文件复核；源、预测和参照散列一致，额外目标求解0。16组固定模态直接正卷积核对全部通过。",'',
f"实际记录的perf_counter墙钟核心时间：两阶灵敏度递推{res['baseline_sensitivity_seconds']:.6f}s，4组预测与离散缺陷包络{res['prediction_bound_core_seconds']:.6f}s，2组完整参照状态及输出峰值{res['new_target_complete_core_seconds']:.6f}s。完整主脚本含归档与核查耗时{res['total_script_seconds']:.6f}s。未单独记录process_time进程CPU时间，不能把这些墙钟秒数标成CPU时间，也不虚构总CPU值。当前包络较高的计算开销仍保留，未声称减少完整求解就实现提速。",'',
'主生产、保存结果核查均实际退出0。R007原文件不改，本轮只写R008；未重提Excel、未重跑旧六套响应、未调用结构求解器或模型API。完整数组只在local-cache，未上传。当前包络针对保存时刻并使用工程浮点保护，仍不等同于连续极值或严格浮点证明；②后续独审待完成。至此停止，不再扩展输入。']
(O/'one-page-RH4X-prediction-rank-and-pass-validation.md').open('x',encoding='utf-8').write('\n'.join(text)+'\n')
notes=['# 运行与隔离记录','',
'真实开始2026-11-01T15:43:56UTC（23:43:56+08），8分钟15:51:56UTC，主要12分钟15:55:56UTC，15分钟硬限15:58:56UTC。预测先冻结15:44:35前；新目标仅6/7两个，在预测冻结后生成。','',
'实际运行依次为prepare_frozen_algorithm_reuse.py、rh4_baseline_prediction_then_two_targets.py、prepare_saved_output_verification.py、verify_rh4_saved_outputs.py、report_and_freeze.py，均由Python UTF8模式执行。前四项实际exit0；本报告脚本退出见工具。算法复制来源、散列及限量变更记录在algorithm-reuse-provenance.json。旧R007的失败记录和旧冻结字节未改。','',
'所有source数组只读；未读取旧RH4X8%、未开新模型/布局/CM或额外输入。单位、zeroIC和名义.02s步长直接按冻结缓存与旧构造固定。S及主项完全在有限目标生成前保存。1%容差和top5局部峰沿用；后验排序不用于选择模态或回调阈值。','',
'所记性能时间为perf_counter wall-clock；没有process_time全CPU计量。核心时间不包含全部I/O、散列与验证，主脚本总时间包含大部分归档/验证。不把这些数字称作公平端到端提速证明。','',
'核查脚本复用上一轮只读核查逻辑，改为本轮实际成功退出状态与4对倒置/1次点漏判文件名。动态目标未重算，额外目标状态求解0；当前通过组合为7%二阶，分母1个，非多个独立结构或事件。']
(O/'run-isolation-and-cost-notes.md').open('x',encoding='utf-8').write('\n'.join(notes)+'\n')
stamp=datetime.now(timezone.utc);elapsed=(stamp-datetime.fromisoformat('2026-11-01T15:43:56+00:00')).total_seconds();idx=json.loads((O/'target-array-index.json').read_text(encoding='utf-8'));js('delivery-manifest.json',dict(actual_freeze_utc=stamp.isoformat(),actual_freeze_plus08=stamp.astimezone(timezone(timedelta(hours=8))).isoformat(),elapsed_seconds=elapsed,within8min=elapsed<=480,within12min=elapsed<=720,within15min=elapsed<=900,files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(O.iterdir()) if p.is_file()],local_only_arrays=[fr['local_array']]+idx,new_target_reference_solves=2,verification_extra_target_solves=0,producer_exit=0,old8_response_read=False,old_outputs_unchanged=True,correct_pass_method_target_combinations=1,conditional_false_pass_count=0,conditional_false_pass_denominator=1,true_adverse_denominator=0,adverse_miss_rate='N/A',CPU_process_time_recorded=False,stopped_no_more_waves=True))
print(json.dumps(dict(frozen_utc=stamp.isoformat(),elapsed_seconds=elapsed,min_pass_interval_D=minimum_lower,max_pass_interval_width=maxwidth,min_pass_truth_D=minimumtruth,passed_combinations=len(passed),false_passes=len(falsepassed),true_adverse=adverse),ensure_ascii=False,indent=2))
