from pathlib import Path
from datetime import datetime,timezone,timedelta
from decimal import Decimal,localcontext
import csv,json,hashlib,statistics
O=Path(__file__).resolve().parent;R=O.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def js(n,v):
    with (O/n).open('x',encoding='utf-8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
rules=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'));stats=json.loads((O/'small-results-summary.json').read_text(encoding='utf-8'));assert all(sha(Path(d['path']))==d['sha256'] for d in rules['inputs']);source=Path(rules['inputs'][0]['path']);raw=rd(source);table=rd(O/'engineering-review-by-story-direction-24.csv');case_stats=rd(O/'bottom-and-mean-screening-by-case-14.csv');maxerr=0.;rechecks=0
with localcontext() as ctx:
    ctx.prec=45
    for t in table:
        rr=[d for d in raw if d['Axis']==t['Axis'] and d['Story']==t['Story']];assert len(rr)==7;decR={d['Case']:Decimal(100)*(1-Decimal(d['P_M_kN'])/Decimal(d['P_B_kN'])) for d in rr};mincase=min(decR,key=decR.get);demand=max(rr,key=lambda d:Decimal(d['P_M_kN']));assert t['minimum_r_case']==mincase and t['reference_demand_case']==demand['Case']
        for prefix,case in [('minimum_r_',mincase),('reference_demand_',demand['Case'])]:
            d=next(d for d in rr if d['Case']==case);pb=Decimal(d['P_B_kN']);pm=Decimal(d['P_M_kN']);A=abs(Decimal(d['V_M_at_tB_signed_kN']));rp=Decimal(100)*(1-pm/pb);dd=Decimal(100)*(pm-A)/pb;ra=Decimal(100)*(1-A/pb)
            for key,value in [('PB_kN',pb),('PM_kN',pm),('r_percent',rp),('d_pp',dd),('r_at_percent',ra)]:maxerr=max(maxerr,abs(float(value)-float(t[prefix+key])));rechecks+=1
            for key,original in [('tB_s','t_B_s'),('tM_s','t_M_s')]:assert float(t[prefix+key])==float(d[original])
            assert t[prefix+'original_peak_source_row_B']==d['source_row_B_peak'] and t[prefix+'original_peak_source_row_M']==d['source_row_M_peak']
        assert float(t['reference_envelope_PMmax_kN'])==max(float(d['P_M_kN']) for d in rr);assert float(t['baseline_envelope_PBmax_kN'])==max(float(d['P_B_kN']) for d in rr)
assert maxerr<1e-9
for c in case_stats:
    rr=[d for d in raw if d['Case']==c['Case']];rr.sort(key=lambda d:int(d['Story'][5:]));values=[float(d['r_peak_percent']) for d in rr];assert abs(min(values)-float(c['minimum_r_percent']))<1e-12;assert abs(sum(values)/12-float(c['mean12_r_percent']))<1e-12;assert float(rr[0]['r_peak_percent'])==float(c['bottom_r_percent'])
oldstats=rd(R/'research/sessions/20261021-0737/roles/role4/R002-story-axis-summary-24.csv');oldmaxdiff=0.
for t in table:
    d=next(e for e in oldstats if e['Story']==t['Story'] and e['Axis']==t['Axis']);assert d['minimum_Case']==t['minimum_r_case'];oldmaxdiff=max(oldmaxdiff,abs(float(t['minimum_r_r_percent'])-float(d['minimum_reduction_percent'])),abs(float(t['median_r_percent'])-float(d['median_reduction_percent'])),abs(float(t['maximum_r_percent'])-float(d['maximum_reduction_percent'])))
assert oldmaxdiff<1e-10
# Reuse only safe Story Forces header/unit metadata, not Program Control or arrays.
ofreeze=json.loads((R/'research/sessions/20261020-1844/roles/role4/R002-input-freeze.json').read_text(encoding='utf-8'));units=[]
for d in ofreeze['inputs'][:2]:
    p=Path(d['path']);assert sha(p)==d['sha256'];m=json.loads(p.read_text(encoding='utf-8'));a=m['tables']['Story Forces'];header=a['headers'];u=a['units'];assert len(header)==len(u);mapping=dict(zip(header,u));assert mapping['VX']=='kN' and mapping['VY']=='kN';units.append(dict(manifest_path=str(p),sha256=sha(p),only_table='Story Forces',VX_unit=mapping['VX'],VY_unit=mapping['VY'],native_Time_unit_cell=mapping.get('Time'),time_note='native Time unit cell blank; seconds interpretation retained from established cache/old peak-table contract, not invented unit-row text'))
js('safe-native-force-unit-metadata-check.json',dict(checked_utc=datetime.now(timezone.utc).isoformat(),sources=units,no_Program_Control_read_or_export=True,no_response_arrays_read=True))
verification=dict(completed_utc=datetime.now(timezone.utc).isoformat(),engineering_rows_checked=24,paired_control_field_checks=rechecks,max_high_precision_rebuild_difference=maxerr,source_rows_and_peak_times_match=True,case_mean_bottom_rows_checked=14,old_24_min_median_max_max_difference=oldmaxdiff,all_source_hashes_unchanged=True,force_units_from_both_native_manifests='VX/VY kN',Time_native_unit_cell='blank, established prior time contract seconds',large_workbook_reads=0,response_array_reads=0,new_ODE=0,independent_role2_audit_pending=True)
js('verification.json',verification)
first=stats['SHW7X'];x5=stats['XStory5'];dsource=next(d for d in raw if d['Case']=='SHW7X' and d['Story']=='Story7');keys_diff=[d for d in table if d['same_minimum_r_and_reference_demand_case']=='False'];env_diff=[d for d in table if d['envelope_pair_is_same_case']=='False']
examples=[dict(example='SHW7X_bottom_mean_vs_local_min',Case='SHW7X',Story='Story7',PB_kN=float(dsource['P_B_kN']),PM_kN=float(dsource['P_M_kN']),r_percent=float(dsource['r_peak_percent']),d_pp=float(dsource['d_pp']),tB_s=float(dsource['t_B_s']),tM_s=float(dsource['t_M_s']),bottom_r_percent=first['bottom_r_percent'],mean_r_percent=first['mean12_r_percent']),dict(example='X_Story5_two_distinct_control_keys',Axis='X',Story='Story5',minimum_reduction=dict(Case=x5['minimum_r_case'],PB_kN=x5['minimum_r_PB_kN'],PM_kN=x5['minimum_r_PM_kN'],r_percent=x5['minimum_r_r_percent'],d_pp=x5['minimum_r_d_pp'],tB_s=x5['minimum_r_tB_s'],tM_s=x5['minimum_r_tM_s']),reference_demand=dict(Case=x5['reference_demand_case'],PB_kN=x5['reference_demand_PB_kN'],PM_kN=x5['reference_demand_PM_kN'],r_percent=x5['reference_demand_r_percent'],d_pp=x5['reference_demand_d_pp'],tB_s=x5['reference_demand_tB_s'],tM_s=x5['reference_demand_tM_s']))];js('two-engineering-examples.json',examples)
compact=['# 分层工程复核表（两组控制键分列）','', '力单位kN。左组是同方向七输入中的最小减幅及其成对峰；右组是参考模型最大绝对需求及该输入自身成对峰。r均为同输入独立峰比较，不交叉配对。完整d、两模型峰时、原始行号及输入元信息保留在CSV。','', '|方向/层|最小减幅输入|最小r/%|其PB / PM|最大参考需求输入|该输入PB / PM|该输入r/%|','|---|---|---|---|---|---|---|']
for t in table:compact.append(f"|{t['Axis']}/{t['Story']}|{t['minimum_r_case']}|{float(t['minimum_r_r_percent']):.4f}|{float(t['minimum_r_PB_kN']):.2f} / {float(t['minimum_r_PM_kN']):.2f}|{t['reference_demand_case']}|{float(t['reference_demand_PB_kN']):.2f} / {float(t['reference_demand_PM_kN']):.2f}|{float(t['reference_demand_r_percent']):.4f}|")
(O/'engineering-review-table-24.md').open('x',encoding='utf-8').write('\n'.join(compact)+'\n')
text=['# 24行分层复核：改善不足与最大需求分别定位','',
'在同一方向的七个输入中，最小减幅输入与参考模型最大绝对需求输入在19/24个楼层—方向组中不同。因此，改善较少的记录与需求最大的记录应分别列示、分别查看，不能把一条记录的减幅配给另一条记录的峰值。新表保留了两组输入键及各自成对PB、PM、r、d、基准/参考峰时和源行号。','',
'数据为旧已审168条同输入B/M原生Story Forces Bottom主方向记录，只由冻结小CSV重组，未重提原大表、读取响应数组或运行求解器。X、Y各七方向工况，共七个波族标签的14方向工况；不能称14条独立地震事件。r=100(1−PM/PB)，d=100(PM−|VM(tB)|)/PB，d单位百分点。所列旧tB按已选第一保存峰使用，未补做所有并列峰审查。','',
'## 两个可直接复核的例子','',
f"SHW7X中Story7减幅{first['minimum_r_percent']:.6f}%，PB/PM={float(dsource['P_B_kN']):.4f}/{float(dsource['P_M_kN']):.4f}kN；同工况底层为{first['bottom_r_percent']:.6f}%，十二层r的等权算术平均为{first['mean12_r_percent']:.6f}%。底层及平均值分别比局部最小值高{first['bottom_minus_min_pp']:.6f}、{first['mean_minus_min_pp']:.6f}个百分点。均值是十二个比例的平均，不是总剪力减幅或一个真实楼层。",'',
f"X向Story5的最小减幅来自SHW3X：PB/PM={x5['minimum_r_PB_kN']:.4f}/{x5['minimum_r_PM_kN']:.4f}kN、r={x5['minimum_r_r_percent']:.6f}%、d={x5['minimum_r_d_pp']:.6f}个百分点、tB→tM={x5['minimum_r_tB_s']:.2f}→{x5['minimum_r_tM_s']:.2f}s。最大参考需求却由SHW4X控制：PB/PM={x5['reference_demand_PB_kN']:.4f}/{x5['reference_demand_PM_kN']:.4f}kN、r={x5['reference_demand_r_percent']:.6f}%、d={x5['reference_demand_d_pp']:.6f}个百分点、峰时{x5['reference_demand_tB_s']:.2f}→{x5['reference_demand_tM_s']:.2f}s。6.851%的减幅不能标在9027.7451kN需求上，后者须与自身PB配对。",'',
'## 底层、均值与包络各表示什么','',
'底层恰为最小减幅层的工况只有3/14，其余11/14可被只看底层的简化读数遗漏。全部14工况的十二层算术平均都高于各自最小值；这只说明均值不能定位最小楼层，不是引入新的合格阈值或“失效概率”。逐工况底层—最小值、平均—最小值差及低于两简化读数的楼层数见14行附表。','',
'参考需求包络是max_c PM,s,c，基准需求包络是max_c PB,s,c；两个最大值在3/24组中也由不同输入控制。CSV另列的1−maxPM/maxPB只是两模型各自需求包络之比，不能替代min_c(1−PM,c/PB,c)，也不能冒充一个同输入成对记录。正文主表优先保留最大PM控制输入自己的PB、PM、r，两个输入集合及方向保持一致。','',
'## 输入与模型身份：已知事实和缺项','',
'既有native_paired_validation.json记录14工况输入逐样本一致、PGA均350mm/s²（.35m/s²），168组保存时间逐点一致；每组点数和时窗列入新14行元信息表。由保存点数与时窗得到名义保存间隔.02s，但本轮没有重读全时间轴，也不能把该值当内部积分步。原生两份Story Forces单位行均确认VX/VY为kN；Time单位单元格本身为空，秒的解释沿用既有缓存/峰表契约，未编造单位行内容。','',
'旧核查还记录荷载工况设置除GUID/备注相同、质心质量刚度表相同。它们以及周期近等都不能证明完整M/K一致。参考模型按提供资料描述为附加3个百分点模态阻尼，标签0不等于零阻尼；完整逐阶阻尼表、全M/K和初始状态、每工况数值倍率及时间缩放、独立原始事件/台站/分量来源仍未由本轮小表补齐。逐输入比较与已知缺项应同时保留，不能用同周期消除这些条件。','',
'输出仍称软件Bottom楼层剪力。截面侧别/正方向、是否包含所列阻尼器作用尚不完整，因此不另扣装置力、不改称剔除阻尼后的主体弹性剪力。本表定位应查看的楼层、输入和时段，不代替承载力、变形或装置验算。','',
f"核查由原168小表和45位Decimal算术重新选择两组控制输入，24行{rechecks}个配对字段最大差{maxerr:.3e}；与旧已审24行最小/中位/最大统计最大差{oldmaxdiff:.3e}。原源散列保持，新增数字待②独审后纳入稿件。"]
(O/'one-page-engineering-review-findings.md').open('x',encoding='utf-8').write('\n'.join(text)+'\n')
notes=['# 执行与边界记录','',
'实际开始2026-11-02T11:26:57UTC（19:26:57+08）；主要12分钟11:38:57UTC，硬15分钟11:41:57UTC。工程24行CSV、14行简化筛查和元信息JSON在11:31:55.463538UTC先保存，然后才写报告。窗口仍为本session固定19:17:23—21:47:23，不延长。','',
'实际运行build_engineering_review_table.py退出0；随后verify_report_and_freeze.py只读小CSV/JSON、核数及报告，退出由工具记录。只写本session角色4/R001。原168、d表及审查/旧稿/旧session全部只读，无Git/自动化/新ODE/预测/CM或求解器。','',
'另读取两个443/510KB既有响应缓存manifest的Story Forces字段和单位，不读其中Program Control，不读任何NPZ或Excel。原生Time单位行为空，如实保留。native_paired_validation.json仅读已有比较元信息，不重新认证原始输入或完整模型身份。','',
'最小r与最大PM两组键各自保留同输入配对PB/PM/d/峰时，未混组。严格相等控制值的全部并列键保留，展示首个字典序键；简化读数的数值差计数容差1e−10个百分点，不是工程目标。未设置是否满足规范或承载力的判据。']
(O/'run-isolation-and-source-notes.md').open('x',encoding='utf-8').write('\n'.join(notes)+'\n')
stamp=datetime.now(timezone.utc);elapsed=(stamp-datetime.fromisoformat('2026-11-02T11:26:57+00:00')).total_seconds();manifest=dict(actual_freeze_utc=stamp.isoformat(),actual_freeze_plus08=stamp.astimezone(timezone(timedelta(hours=8))).isoformat(),elapsed_seconds=elapsed,within12min=elapsed<=720,within15min=elapsed<=900,files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file()],new_large_workbook_reads=0,response_array_reads=0,new_ODE=0,old_outputs_unchanged=True,independent_role2_review_pending=True)
js('delivery-manifest.json',manifest);print(json.dumps(dict(frozen_utc=stamp.isoformat(),elapsed_seconds=elapsed,manifest_sha256=sha(O/'delivery-manifest.json'),table_sha256=sha(O/'engineering-review-by-story-direction-24.csv'),verification=verification),ensure_ascii=False,indent=2))
