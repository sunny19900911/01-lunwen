from pathlib import Path
from datetime import datetime,timezone,timedelta
from time import perf_counter,process_time
import json,csv,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def cs(n,rows):
    with (O/n).open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
w0=perf_counter();c0=process_time();rules=json.loads((O/'input-method-envelope-rules-freeze-v002.json').read_text(encoding='utf-8'));freeze=json.loads((O/'prediction-and-envelope-freeze.json').read_text(encoding='utf-8'));res=json.loads((O/'results.json').read_text(encoding='utf-8'));idx=json.loads((O/'reference-array-index-4.json').read_text(encoding='utf-8'));assert all(sha(Path(d['path']))==d['sha256'] for d in rules['inputs']);assert all(sha(Path(d['path']))==d['sha256'] for d in freeze['files']);assert all(sha(Path(d['path']))==d['sha256'] for d in freeze['new_local_arrays']);assert all(sha(Path(d['path']))==d['sha256'] for d in idx)
ind=rd(O/'all-individual-frozen-intervals-288.csv');truth=rd(O/'all-individual-reference-peaks-144.csv');env=rd(O/'input-envelope-frozen-intervals-96.csv');et=rd(O/'input-envelope-reference-peaks-and-strong-objective-48.csv');ev=rd(O/'input-envelope-interval-and-objective-validation-96.csv');base=rd(O/'baseline-input-envelope-S-12.csv');candidate=rd(O/'input-envelope-candidate-validation-8.csv');cases=['SHW3X','SHW4X','RH4X'];zs=[.06,.07,.08,.10];il=[];ic=[];changes=[];maxendpoint=0.;maxtruth=0.
for d in ind:
    rr=next(t for t in truth if t['Case']==d['Case'] and t['target_zeta']==d['target_zeta'] and t['Story']==d['Story']);p0=float(d['P0_kN']);ph=float(d['Phat_kN']);pt=float(rr['reference_peak_kN']);D=float(rr['reference_D']);Dp=1-ph/p0;il.append({**d,'reference_peak_kN':pt,'reference_D':D,'peak_relative_error':ph/pt-1,'peak_covered':float(d['L_kN'])<=pt<=float(d['U_kN']),'point_insufficient_miss':D<.1 and Dp>=.1,'point_false_insufficient':D>=.1 and Dp<.1,'point_false_adverse':D>=0 and Dp<0,'true_adverse':D<0,'interval_insufficient_miss':D<.1 and d['decision_status']=='meets','interval_false_insufficient':D>=.1 and d['decision_status']=='insufficient'})
for case in cases:
    for z in zs:
        tr=[d for d in truth if d['Case']==case and float(d['target_zeta'])==z];tp=all(float(d['reference_D'])>=.1 for d in tr)
        for order in [1,2]:
            rr=[d for d in ind if d['Case']==case and float(d['target_zeta'])==z and int(d['Taylor_order'])==order];action='reject' if any(float(d['D_upper'])<.1 for d in rr) else ('pass' if all(float(d['D_lower'])>=.1 and float(d['D_width'])<=.05 for d in rr) else 'recompute');ic.append(dict(Case=case,target_zeta=z,Taylor_order=order,action=action,v001_flagged_floors=sum(d['v001_recompute']=='True' for d in rr),true_all12_meet=tp,false_pass=bool(not tp and action=='pass'),false_reject=bool(tp and action=='reject'),minimum_true_D=min(float(d['reference_D']) for d in tr)))
for b in base:
    rr=[d for d in ind if d['Story']==b['Story'] and float(d['target_zeta'])==.06 and int(d['Taylor_order'])==1];pk=max(float(d['P0_kN']) for d in rr);active=[d['Case'] for d in rr if float(d['P0_kN'])==pk];assert pk==float(b['P0env_kN']) and ';'.join(active)==b['baseline_controlling_inputs'];pairs=dict(x.split(':') for x in b['source_S'].split(';'));Spr=max(-float(pairs[c])*pk for c in active);assert abs(-Spr/pk-float(b['S_env_percent_per_damping_pp']))<1e-9
for e in env:
    z=float(e['target_zeta']);order=int(e['Taylor_order']);story=e['Story'];rr=[d for d in ind if float(d['target_zeta'])==z and int(d['Taylor_order'])==order and d['Story']==story];lo=max(float(d['L_kN']) for d in rr);up=max(float(d['U_kN']) for d in rr);p0=float(e['P0env_kN']);maxendpoint=max(maxendpoint,abs(lo-float(e['L_env_kN'])),abs(up-float(e['U_env_kN'])));DL=1-up/p0;DU=1-lo/p0;assert abs(DL-float(e['D_env_lower']))<1e-12 and abs(DU-float(e['D_env_upper']))<1e-12;possible=[d['Case'] for d in rr if float(d['U_kN'])>=lo];assert ';'.join(possible)==e['potential_controlling_inputs'];tr=[d for d in truth if float(d['target_zeta'])==z and d['Story']==story];pk=max(float(d['reference_peak_kN']) for d in tr);etr=next(d for d in et if float(d['target_zeta'])==z and d['Story']==story);maxtruth=max(maxtruth,abs(pk-float(etr['reference_envelope_peak_kN'])));assert lo<=pk<=up
for tr in et:
    b=next(d for d in base if d['Story']==tr['Story']);changes.append(dict(target_zeta=float(tr['target_zeta']),Story=tr['Story'],baseline_controlling_input=b['baseline_controlling_inputs'],candidate_true_controlling_input=tr['reference_controlling_inputs'],control_changed=b['baseline_controlling_inputs']!=tr['reference_controlling_inputs'],reference_envelope_D=float(tr['reference_envelope_D']),min_individual_reference_D=float(tr['min_individual_reference_D'])))
assert maxendpoint==0 and maxtruth==0
# Independently repeat the new 96 curve/peak checks from already saved arrays, no state solve.
newcurvemiss=0;newpeakdiff=0.
for entry in idx:
    case=entry['Case'];z=entry['target_zeta'];predfile=next(Path(d['path']) for d in freeze['new_local_arrays'] if case in Path(d['path']).name)
    with np.load(predfile,allow_pickle=False) as a:PV={o:a[f'z{z:g}_order{o}_V'].copy() for o in [1,2]};EE={o:a[f'z{z:g}_order{o}_E'].copy() for o in [1,2]};tt=a['t'].copy()
    with np.load(entry['path'],allow_pickle=False) as a:assert np.array_equal(tt,a['t']);V=a['shear_elastic_inertia_predicted_kN' if z==.08 else 'V'].copy()
    for o in [1,2]:newcurvemiss+=int(np.count_nonzero(abs(PV[o]-V)>EE[o]))
    pk=np.max(abs(V),axis=0)
    for j in range(12):r=next(d for d in truth if d['Case']==case and float(d['target_zeta'])==z and d['Story']==f'Story{j+1}');newpeakdiff=max(newpeakdiff,abs(pk[j]-float(r['reference_peak_kN'])))
assert newcurvemiss==0 and newpeakdiff==0
for c in candidate:
    z=float(c['target_zeta']);o=int(c['Taylor_order']);rr=[d for d in env if float(d['target_zeta'])==z and int(d['Taylor_order'])==o];action='reject' if any(float(d['D_env_upper'])<.1 for d in rr) else ('pass' if all(float(d['D_env_lower'])>=.1 and float(d['D_env_width'])<=.05 for d in rr) else 'recompute');assert action==c['envelope_candidate_action']
cs('all-individual-scalar-validation-288.csv',il);cs('per-input-candidate-validation-preserved-24.csv',ic);cs('baseline-to-target-controlling-inputs-48.csv',changes)
metrics=[]
for z in zs:
    tr=[d for d in et if float(d['target_zeta'])==z];minimum=min(float(d['reference_envelope_D']) for d in tr);strong=min(float(d['min_individual_reference_D']) for d in tr);lim=';'.join(d['Story'] for d in tr if float(d['reference_envelope_D'])==minimum)
    for o in [1,2]:
        rr=[d for d in env if float(d['target_zeta'])==z and int(d['Taylor_order'])==o];cc=next(d for d in candidate if float(d['target_zeta'])==z and int(d['Taylor_order'])==o);metrics.append(dict(target_zeta=z,Taylor_order=o,reference_min_envelope_D=minimum,reference_limiting_floors=lim,reference_min_strong_D=strong,median_envelope_D_width_pp=100*float(np.median([float(d['D_env_width']) for d in rr])),max_envelope_D_width_pp=100*max(float(d['D_env_width']) for d in rr),envelope_action=cc['envelope_candidate_action'],strong_action=cc['strong_each_input_candidate_action'],true_envelope_meets=cc['true_envelope_all12_meet']))
cs('engineering-envelope-decision-summary-8.csv',metrics)
verification=dict(completed_utc=datetime.now(timezone.utc).isoformat(),all_individual_rows_rebuilt=288,all_truth_rows=144,baseline_S_rows_checked=12,envelope_intervals_rebuilt=96,envelope_reference_rows_rebuilt=48,candidate_actions_checked=8,per_input_candidate_actions_preserved=24,max_envelope_endpoint_difference_kN=maxendpoint,max_envelope_reference_difference_kN=maxtruth,new96_curve_checks_strict_uncovered_samples=newcurvemiss,new_reference_peak_max_difference_kN=float(newpeakdiff),source_prediction_reference_hashes_unchanged=True,new_target_state_solves=0,wall_seconds=perf_counter()-w0,process_CPU_seconds=process_time()-c0,independent_role2_review_pending=True)
js('verification.json',verification)
table=['# 三输入绝对峰包络工程主表','', '固定SHW3X、SHW4X、RH4X，X向、全部12层。Senv取基准包络控制输入的峰导数；各候选Denv是真实参照后验值，不是由S外推。','', '|层|基准控制输入|P0env/kN|Senv|6%参照Denv/%|7%/%|8%/%|10%/%|','|---|---|---|---|---|---|---|---|']
for b in base:
    vals=[next(float(d['reference_envelope_D'])*100 for d in et if float(d['target_zeta'])==z and d['Story']==b['Story']) for z in zs];table.append(f"|{b['Story']}|{b['baseline_controlling_inputs']}|{float(b['P0env_kN']):.3f}|{float(b['S_env_percent_per_damping_pp']):.6f}|"+'|'.join(f'{x:.3f}' for x in vals)+'|')
table+=['','候选决策及全部预测区间见engineering-envelope-decision-summary-8.csv与input-envelope-frozen-intervals-96.csv；逐输入原目标单独保存在all-individual-scalar-validation-288.csv、per-input-candidate-validation-preserved-24.csv。']
(O/'engineering-main-table-three-input-envelope12.md').open('x',encoding='utf-8').write('\n'.join(table)+'\n')
newcomp=rd(O/'new-individual-prediction-validation-96.csv');pointmiss=[d for d in ev if d['point_insufficient_miss']=='True'];cs('envelope-point-insufficient-miss-cases-2.csv',pointmiss)
change7=[d for d in changes if d['Story']=='Story7'];adverse=sum(float(d['reference_D'])<0 for d in truth);passed=sum(d['envelope_candidate_action']=='pass' for d in candidate)
text=['# 三输入绝对峰包络：新增预测与工程候选判断','',
'在固定SHW3X、SHW4X、RH4X三条X输入下，另按“各层输入绝对剪力峰包络降低10%”评价候选。两阶区间均拒绝6%、7%，8%、10%仍要求完整复算；10%完整参照实际满足全12层目标，但预测区间较宽，未能直接通过。原逐输入均降低10%的更强目标、原误差和失败全部保留。','',
'## 目标及先预测后参照','',
'各层P0env=max_e P0e，Penv=max_e Pe；区间为[max_e Le,max_e Ue]，再以同一P0env归一化。它是不同输入各自绝对峰的包络，不是输入平均、不同输入同一时刻相加或逐输入相对降幅取最小值。三条X输入集合与10%/5个百分点条件均来自根预先冻结的附加政策，不泛化至Y或任意事件。','',
'只从已有SHW4X/RH4X的5%与z/w缓存补8%/10%两阶预测及离散区间，没有新导数求解。全部新逐输入预测与合并包络区间、候选动作于'+freeze['frozen_utc']+'冻结，之后核对旧8%各自SHA及t/ag/ω/B完全一致后读取，且仅新增两套10%状态。旧8%是已知参照，整项不称未见地震盲测。旧6%/7%及SHW3X8%/10%仅读已有小表。','',
'## 包络基准S与控制输入','',
'12层基准包络均由唯一输入控制：第3—7层为SHW4X，其余为SHW3X。因此Senv取该控制输入的S；若将来精确并列，须先取最大力峰导数再归一。第5层Senv=4.676272，而三输入中最小S=2.132064，二者不能混用。包络基准改善最慢是Story8，Senv=3.559472。','',
'Story7基准控制输入是SHW4X，候选完整参照控制输入在四个目标均变为SHW3X；每个目标的真实及潜在控制输入均另列。预测的控制输入不唯一时，只要各输入区间有效，maxL/maxU包络仍有效，不因身份不确定就自动否定目标判断。','',
'## 候选结果与两个目标的区别','',
'|ζ|阶次|包络真实最小降幅/%|限制层|逐输入真实最小降幅/%|包络区间宽度中位数/百分点|包络动作|逐输入强目标动作|','|---|---|---|---|---|---|---|---|']
for d in metrics:text.append(f"|{d['target_zeta']:.2f}|{d['Taylor_order']}|{100*d['reference_min_envelope_D']:.3f}|{d['reference_limiting_floors']}|{100*d['reference_min_strong_D']:.3f}|{d['median_envelope_D_width_pp']:.3f}|{d['envelope_action']}|{d['strong_action']}|")
text+=['','8%包络最小真实降幅9.228%，仍不足10%，而逐输入最小降幅仅6.851%；10%相应为14.635%与11.584%，两种目标均真实达到，但区间方法仍要求复算。样本中的最终真假没有出现两个目标一成一败，不能虚构这种差异；其数值定义和预测决策确有区别，例如8%二阶包络尚不确定、逐输入强目标可拒绝。','',
'共有2个包络点预测改善不足漏判，分别如下，区间均未误放行：','', '|ζ|阶次|层|包络点预测降幅/%|真实包络降幅/%|','|---|---|---|---|---|']
for d in pointmiss:text.append(f"|{float(d['target_zeta']):.2f}|{d['Taylor_order']}|{d['Story']}|{100*float(d['D_env_point']):.6f}|{100*float(d['reference_envelope_D']):.6f}|")
text+=['','96组新增逐输入峰/完整曲线及96组合并包络峰全部被计算区间覆盖，包络实际控制输入也均在预测的潜在输入集合内；未回调任何界或阈值。无包络候选通过，条件误放行率N/A；全部144个逐输入参照峰中没有D<0，不利漏判率仍N/A。区间仅针对保存网格、采用既定工程浮点保护，不声称严格浮点或连续极值保证。','',
'## 成本、执行及限制','',
f"本轮主脚本实际总墙钟{res['wall_total_seconds']:.6f}s、进程CPU{res['process_CPU_total_seconds']:.6f}s，包含新读取、预测/包络、直接FFT核查、参照与归档。SHW4X/RH4X预测与界的墙钟核心合计{sum(float(d['core_wall_seconds']) for d in rd(O/'new-prediction-bound-work-2.csv')):.6f}s；各输入含核查的CPU、两份旧8%读取、两套新10%状态+投影的墙钟/CPU分别列于原计时CSV。新导数工作量0，但不能把先前的导数成本视为整个方法免费；既有R005已测完整流程较慢的失败结论保留，不据本轮复用缓存声称端到端提速。",'',
'一次包络候选复算需覆盖固定三输入，最多是3条状态历程；不是每标记楼层一次，也不是不论输入数多少只算一条历程。首次复用块因未传入V0变量在任何预测/目标产生前退出1；以新v002输入冻结和缓存子目录补齐已知V0/Vζ/P0后成功退出0，原失败文件未改。没有重复目标求解。','',
f"全部288行逐输入区间、144行参照、12层包络S、96行包络区间、8项候选动作及新增96条曲线只读核查通过；最大端点/峰值差均为0，额外状态求解0。核查阶段另耗墙钟{verification['wall_seconds']:.6f}s、CPU{verification['process_CPU_seconds']:.6f}s。②独审仍待完成。",'',
'本轮未扩展输入、模型、布局或ζ集合，旧稿和旧冻结文件保持。完整预测时程与新10%数组仅local-cache；旧8%原数组只读。']
(O/'one-page-three-input-envelope-engineering-result.md').open('x',encoding='utf-8').write('\n'.join(text)+'\n')
notes=['# 执行、隔离与计时','',
'真实开始2026-11-01T16:00:47UTC（2026-11-02 00:00:47+08）；8分钟16:08:47UTC，15分钟硬限16:15:47UTC。首次脚本在执行冻结预测算术块的首行缺V0退出1，未产生预测/目标。prepare_recovery_v002.py创建新v002脚本，仅补齐既有基准V0/VZ/P0，变更输入冻结文件名与local-cache/v002目录；原失败字节未覆盖。','',
'实际v002主命令python.exe -X utf8 extend_two_inputs_then_form_input_envelope_v002.py成功exit0，所有预测及合并区间先于参照冻结；之后读取2个旧8%源、只求2个新10%。verify_report_and_freeze.py读取保存表/数组核对及成稿，不含ODE。旧每输入政策与原失败均保留，附加包络目标来自根本轮冻结文件。','',
'perf_counter为墙钟，process_time为进程CPU，均在本轮主过程前开始。CPU含各线程CPU，计量分辨率可能使短段数值粗；主阶段含I/O/验证，预测核心wall字段另列。与此前未记CPU的任务分开，不将本轮CPU补填进旧记录。预测复用旧导数是本轮增量成本，非完整方法准备成本消失。','',
'包络S与控制输入规则先于新真值固定。所有峰包络是不同输入各自峰，不声称跨输入峰同时发生。旧8%已历史见，新的10%也只验证固定同一模型/输入，不计作新地震事件。所有全数组及原件不入Git，最多3输入状态分析覆盖全楼。']
(O/'run-isolation-cost-and-recovery-notes.md').open('x',encoding='utf-8').write('\n'.join(notes)+'\n')
stamp=datetime.now(timezone.utc);elapsed=(stamp-datetime.fromisoformat('2026-11-01T16:00:47+00:00')).total_seconds();js('delivery-manifest.json',dict(actual_freeze_utc=stamp.isoformat(),actual_freeze_plus08=stamp.astimezone(timezone(timedelta(hours=8))).isoformat(),elapsed_seconds=elapsed,within8min=elapsed<=480,within15min=elapsed<=900,files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(O.iterdir()) if p.is_file()],local_only_new_arrays=freeze['new_local_arrays']+[d for d in idx if d['new_state_solve']],readonly_reused8_arrays=[d for d in idx if not d['new_state_solve']],new_target_solves=2,new_derivative_solves=0,first_attempt_exit=1,recovery_exit=0,old_outputs_unchanged=True,independent_role2_review_pending=True))
print(json.dumps(dict(frozen_utc=stamp.isoformat(),elapsed_seconds=elapsed,verification=verification,changed_controlling_inputs=sum(d['control_changed'] for d in changes),min_summary=metrics),ensure_ascii=False,indent=2))
