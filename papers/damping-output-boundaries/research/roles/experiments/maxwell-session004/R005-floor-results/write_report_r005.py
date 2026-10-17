"""Render compact tables from frozen R005 derived CSVs; no cache reread."""
from pathlib import Path
import csv,json
H=Path(__file__).resolve().parent
assert not (H/'report.md').exists()
read=lambda n:list(csv.DictReader((H/n).open(encoding='utf-8',newline='')))
floors=read('floor_record_peaks_r005.csv');ranks=read('top3_floor_ranks_r005.csv');coverage=read('mapped_group_coverage_r005.csv')
s=json.loads((H/'summary_r005.json').read_text(encoding='utf-8'));p=json.loads((H/'protocol.json').read_text(encoding='utf-8'))
small=[]
for r in floors:
    small.append({'Case':r['Case'],'Story':r['Story'],'Bottom_shear_abs_record_peak_kN':r['shear_abs_record_peak'],
        'CM_abs_record_peak_mm':r['cm_abs_record_peak'],'Drift_exported_abs_record_peak_unit_blank':r['drift_abs_record_peak'],
        'shear_and_CM_complete':r['shear_all_groups_complete']=='True' and r['cm_all_groups_complete']=='True',
        'Drift_scope':'exported_records_only; Label/coordinates unavailable'})
with (H/'floor_three_metric_table_r005.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(small[0]));w.writeheader();w.writerows(small)
lines=['# M-EXP-R005：六工况楼层工程输出记录峰值','',
    '状态：candidate，等待独立复核。只复用既有三张 core-cache 和覆盖清单；未拟合、求解、读取原始 Excel 或外搜。',
    '', '六工况中，Bottom 层剪绝对记录峰值前三均为 Story1、Story2、Story3；CM 位移前三均为 Story12、Story11、Story10。主比较的两个指标前三集合没有交集，最大控制层分别为 Story1 和 Story12，层号差为 11。这描述当前单一模型状态中不同指标的控制楼层，不能据此推断减震率或装置布置最优。',
    '', '## 冻结口径与覆盖', '',
    '先检查 manifest 字段、分组键及 NPZ 数组头，再于读取数值前冻结 protocol.json。按工况名后缀作分析约定：X→VX/UX/Drift X，Y→VY/UY/Drift Y；该约定不认证真实输入方向。层力只取 Bottom。CM 每个同层隔板分别保留，再以同层隔板记录绝对峰的最大值汇总；峰值带符号值、时刻、源行和控制隔板保存在 CSV 的 controllers_json 中。',
    '', '六工况×12层共72组 Bottom 层剪、108组独立 CM 隔板记录均覆盖完整预期网格：RH4X/Y 2501点、0–50s；SHW4X/Y 2951点、0–59s；SHW7X/Y 2696点、0–53.9s；输出间隔0.02s。只对这些完整指标作主比较。实际存在的隔板组逐一保留，没有补造某层未导出的隔板。',
    '', '72组对应方向 Drift 均未覆盖全部预期网格，每组缺1–21个时刻；未补零、插值或删除记录。其数值仅称“已导出记录的绝对最大值”。缓存的 Drift 列单位为空，本次保留原值，不转换或擅自认证单位。Label及X/Y/Z坐标未进入既有缓存，故无法在不重新提取原始表的条件下保留；输出明确标为空及 not_preserved_in_cache，控制时刻和 SourceRow 完整保留。此限制不代表原始工作簿没有这些列。',
    '', '前三按12层峰值从大到小取第三个层值为阈值，包含所有与阈值完全相等的并列层；所有绝对峰同值控制记录也保留。此次各指标没有第三名边界并列，排名表共54行。时刻不作为独立样本，不进行显著性分析。',
    '', '## 六工况控制楼层', '', '| 工况 | Bottom层剪前三 | CM位移前三 | 前三交集 | 漂移记录前三（覆盖不全） |', '|---|---|---|---|---|']
for c in s['comparisons']:
    show=lambda key:'、'.join(x.replace('Story','') for x in json.loads(c[key])) or '无'
    lines.append(f"| {c['Case']} | {show('shear_top3_including_ties_json')} | {show('cm_top3_including_ties_json')} | {show('intersection_json')} | {show('drift_top3_separate_sparse_json')} |")
lines+=['', '层剪、CM 位移和漂移记录对应不同的输出指标，其各自峰值也可能出现在不同时刻。因此这些排名不能合成为同一时刻楼层受力剖面，也不能将不同指标的控制层当作可互换的设计结论。漂移排名单列，既有缺失使其不能认证真实全时程峰值或 RMS。',
    '', '## 各工况12层三指标小表', '', '数值按原导出单位展示：Bottom 层剪 kN，CM 位移 mm；Drift 列单位空，保留原值。表中均为绝对记录峰，带符号值及控制定位请见完整峰值 CSV。', '']
for case in p['cases']:
    lines += [f'### {case}', '', '| 层 | Bottom层剪/kN | CM位移/mm | Drift导出记录最大值（单位空） |', '|---|---:|---:|---:|']
    for r in small:
        if r['Case']==case:
            lines.append('| '+r['Story']+' | '+' | '.join(format(float(r[k]),'.8g') for k in ['Bottom_shear_abs_record_peak_kN','CM_abs_record_peak_mm','Drift_exported_abs_record_peak_unit_blank'])+' |')
    lines.append('')
lines += ['## 各指标最大控制记录定位', '', '| 工况 | 指标 | 控制层 | 控制隔板 | 时刻/s | 带符号值 | SourceRow |', '|---|---|---|---|---:|---:|---:|']
for r in ranks:
    if r['rank_competition']=='1':
        for c in json.loads(r['controllers_json']):
            lines.append(f"| {r['Case']} | {r['metric']} | {r['Story']} | {c['diaphragm'] or '—'} | {c['t_s']:.8g} | {c['signed_value']:.9g} | {c['source_row']} |")
lines += ['', '漂移控制记录的 Label/坐标在缓存中不可用；上表 SourceRow 指向原 Story Drifts 表行号。若未来另行授权原表定位，可仅补核这些行，不能将当前未知信息写成已确认。',
    '', '## 来源、执行与交付', '',
    '源工作簿身份继承自已审缓存 manifest：`'+p['source_xlsx_identity_inherited_only']['sha256']+'`；本次未重读或重新哈希原工作簿。缓存与覆盖记录实际 SHA256 如下：', '']
for name,ref in p['inputs'].items():lines.append('- '+name+': `'+ref['sha256']+'`')
lines += ['- manifest.json: `'+p['coverage_manifest']['sha256']+'`', '',
    f"实际数值脚本运行 {s['elapsed_seconds']:.6f}s，exit 0，9项检查全部通过。包括72层表行、108独立CM组、72个Bottom层剪组、72个映射漂移组、有限性、层剪及CM完整网格、输入SHA不变、协议不变和运行时间上限。协议冻结时间与实际完成UTC见 JSON；未覆盖或重跑冻结结果。", '',
    '交付：`floor_three_metric_table_r005.csv` 是72行小表；`floor_record_peaks_r005.csv` 保留三指标控制记录；`diaphragm_record_peaks_r005.csv` 保留108个独立隔板组；`mapped_group_coverage_r005.csv` 保留252组覆盖；`top3_floor_ranks_r005.csv` 含54行排名；`main_metric_comparison_r005.csv` 含6工况主比较。协议、来源SHA、脚本、summary和run_record一并保留，无大数组或图片。', '',
    '没有无控公平配对，不报告减幅；没有几何与装置朝向，不投影装置力。当前模型状态、命名方向约定及漂移覆盖限制绑定所有描述。全部结果维持 candidate，待角色2独核。']
(H/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(H/'next-task.md').write_text('只读已冻结三张core-cache与manifest，独立复算六工况12层VX/UX/Drift X或VY/UY/Drift Y的记录绝对峰、Top3及并列；层剪只Bottom，CM隔板先分别再同层汇总。核对控制隔板/带符号值/时刻/SourceRow及漂移缺1–21个网格点，确认Label/坐标不在缓存而未伪造。主比较只用完整层剪与CM，漂移只已导出记录。不得读取Excel、改方向判据、拟合、求解、补值或声称减幅/最优布置。独立检查后由父任务决定状态；本角色完成即停止。\n',encoding='utf-8')
print(json.dumps({'report_written':True,'compact_rows':len(small),'report_characters':len('\n'.join(lines))},ensure_ascii=False))
