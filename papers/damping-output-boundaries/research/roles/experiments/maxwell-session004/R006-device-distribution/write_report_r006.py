"""Describe frozen group summaries and prespecified within-story rankings only."""
from pathlib import Path
import csv,json
H=Path(__file__).resolve().parent
assert not (H/'report.md').exists()
def read(n):
    with (H/n).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
rows=read('device_record_summary_r006.csv');ranks=read('within_story_rank_extremes_r006.csv')
s=json.loads((H/'summary_r006.json').read_text(encoding='utf-8'));p=json.loads((H/'protocol.json').read_text(encoding='utf-8'))
def selected(case,story,metric,side):
    return '、'.join(x['Link'] for x in ranks if x['Case']==case and x['Story']==story and x['metric']==metric and x['side_with_exact_boundary_ties']==side)
def bounds(group,key):
    vals=[float(x[key]) for x in group];return f'{min(vals):.7g}–{max(vals):.7g}'
lines=['# M-EXP-R006：共同完整32只装置的力与条件能量分布','',
    '状态：candidate，等待独立复核。范围固定为 Story8–11 每层8只、六工况共192组；不同楼层和不同工况不合并成全模型能量。', '',
    '每工况、每层8只装置分别按原生 max|P| 和条件 Dport 给出前2/后2，包含边界精确并列。原生 Wtrap 与采用固定拟合刚度扣除储能后的 Dport 分列。这些排名描述已有模型输出与条件账本，不给出好坏阈值或布置最优结论。', '',
    '## 预定子集、来源及覆盖', '',
    '先核查当前 Maxwell 角色目录与 W5 Maxwell core-cache：全局/楼层缓存七表不含 Link P/U1；现有完整 Link 配对CSV仅六条K2/K5记录，不能覆盖192组。读取数值前冻结 protocol.json，依据R001覆盖清单选全部六工况共同完整的32只。K12/Story7仅RH4X完整，按共同完整子集规则排除，不按响应值挑选。', '',
    '原始有控.xlsx的SHA256实际重新核对为 `'+s['source_sha256']+'`，文件大小与mtime_ns在提取前后相同。仅对 Element Forces - Links 的P、Element Deformations - Links的U1各执行一次有界流式目标提取；未重抽全局七表。', '',
    'P单位kN，U1原单位mm，除以1000为m，时间s。全部192组的P-I/P-J/U1完整、时间一致、源行递增，且P-I/P-J逐点完全相同，端口功只计P-I一次。完整521472个配对时点及全过程三流源行保存在本地NPZ；P源格列I，U1源格列H。六条已有训练/迁移CSV的全部八列、全部点与新提取结果完全相等。', '',
    '## 每工况/楼层内原生峰力分布与排名', '',
    '范围为同组8只的各自记录峰值范围，不是同时刻合力。前2/后2包含精确并列，可能多于2只；不跨楼层或波间作减幅比较。', '',
    r'| 工况 | 层 | 原生max\|P\|范围/kN | 峰力前2含并列 | 峰力后2含并列 |', '|---|---|---:|---|---|']
for case in p['cases']:
    for story in p['stories']:
        g=[x for x in rows if x['Case']==case and x['Story']==story]
        lines.append(f"| {case} | {story} | {bounds(g,'max_abs_native_P_kN')} | {selected(case,story,'max_abs_native_P_kN','top2')} | {selected(case,story,'max_abs_native_P_kN','bottom2')} |")
lines+=['', '## 同组原生端口功与条件Dport分布及排名', '',
    '下表能量单位均为kN·m，范围只比较同工况/楼层8只的各自结果，没有作装置求和。Dport排名依据Dport数值，原生Wtrap保留为独立列，不能把Wtrap直接称为纯黏性耗能。', '',
    '| 工况 | 层 | 原生Wtrap范围 | 条件Dport范围 | Dport前2含并列 | Dport后2含并列 |', '|---|---|---:|---:|---|---|']
for case in p['cases']:
    for story in p['stories']:
        g=[x for x in rows if x['Case']==case and x['Story']==story]
        lines.append(f"| {case} | {story} | {bounds(g,'Wtrap_native_kNm')} | {bounds(g,'Dport_conditional_kNm')} | {selected(case,story,'Dport_conditional_kNm','top2')} | {selected(case,story,'Dport_conditional_kNm','bottom2')} |")
lines+=['', '同一工况、同一层中，两项指标的前2并不总是同一批装置。例如RH4X/Story8的峰力前2为K10、K92，条件Dport前2为K92、K103；SHW4Y/Story11分别为K80、K6与K80、K5。这些差异只描述所列记录，全部24个工况/楼层组的排名均在上表保留。', '',
    '两个排名所对应的输出不同：峰力取单个时刻最大绝对值，Dport是整段端口功扣除条件储能变化的账本量。应分别读取这两张表，不将排名替换成统一装置效能标签。', '',
    '## 固定参数与离散账本', '',
    '固定R002 alpha=0.30、a=2.0006042528243313e−6 m/kN、b=1.1798190016520894e−9，k=1/a。未拟合或另选参数，真实属性仍未认证。', '',
    '```', 'h = sign(F)|F|^(1/alpha)', 'Wtrap = Σ Favg Δd_obs', 'ΔUs = a(F_end² − F_0²)/2',
    'Dport = Wtrap − ΔUs', 'Dforce_trap = b Σ Δt avg(Fh)',
    'Dforce_trap − Dport = (b/4)ΣΔt ΔF Δh + ΣFavg Δr',
    'r = a(F−F0)+b cumulative_trapezoid(h)−(d_obs−d0)', '```', '',
    f"每组CSV同时保留Wtrap、条件ΔUs/Dport、模型Dforce_trap及两项离散差额。最大总恒等式残差为{s['max_abs_total_identity_residual_kNm']:.6g} kN·m；各组单区间恒等式也通过浮点容差检查。此恒等式来自相同固定模型的经典离散储能/乘积关系，不能作为独立物理验证或连续积分误差界。", '',
    f"{s['negative_increment_groups']}组存在负Dport区间增量，全部原样保留；192行摘要给出每组负值数、最小值与区间。未用裁剪或阈值掩盖负值，也不能仅凭条件离散负增量认证真实设备非被动。", '',
    '## 实际运行、产物及解释边界', '',
    f"数值脚本实际运行{s['elapsed_seconds']:.6f}s、exit 0，10项检查全部通过。协议、覆盖清单、R002参数摘要和六条核对CSV的SHA在完成时保持不变。实际有界读取记录如下：", '',
    '| 表 | 扫描至源行 | 目标数值行 | 读取次数 |', '|---|---:|---:|---:|']
for a in s['sheet_audits']:lines.append(f"| {a['sheet']} | {a['last_source_row']} | {a['selected_numeric_rows']} | {a['sheet_passes']} |")
lines+=['',
    f"主交付 `device_record_summary_r006.csv` 192行；`within_story_rank_extremes_r006.csv` {s['rank_rows']}行；其余为协议、脚本、摘要、运行记录和本报告。完整配对时程 `local_paired_histories_r006.npz` 只留本地，不上传；`local_history_manifest_r006.json` 描述数组键、列和形状。所有原始源行均在NPZ中，峰值源格和时刻另在192行CSV中，便于小规模核查。", '',
    '无几何和朝向证据，不把轴向P/U1投影为全局X/Y效果；工况名X/Y不自动代表独立事件。该32只共同完整子集不代表88只完整响应，未累加闭合88只全模型能量，也不作因果减幅或布置优化结论。当前端口版本映射和真实属性的既有限制继续适用。', '',
    '下一检查：由独立角色对本地冻结NPZ及192行摘要复算峰值定位、Wtrap/条件储能与Dport、离散差额、负增量计数及层内前2/后2并列规则；不再重提取原始表或拟合。']
(H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(H/'next-task.md').write_text('独立只读R006本地冻结NPZ、协议、源SHA元数据和192行CSV；复算每组原生max|P|/U1及控制时刻/源格、Wtrap、条件ΔUs/Dport、Dforce与两项离散差额、负增量保留。核查192组三流完整、I/J只计一次、六旧CSV全部八列精确核对、每工况/楼层8只内前2/后2及精确并列。原生W与条件D分开解释。不重读Excel、不拟合、不全88求和或赋予布置好坏。旧R001–R005不动。本角色冻结后停止，待父任务新单项指令。\n',encoding='utf-8')
print(json.dumps({'report_written':True,'report_characters':len('\n'.join(lines))},ensure_ascii=False))
