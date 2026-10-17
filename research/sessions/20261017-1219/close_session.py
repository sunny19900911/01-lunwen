"""Close only after the fixed deadline and official scheduler pause; no research."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
import tomllib

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PAPER = ROOT/'papers/damping-output-boundaries'
now = datetime.now(timezone(timedelta(hours=8)))
assert now >= datetime.fromisoformat('2026-10-17T14:19:08+08:00'), 'Cutoff not reached; no writes'
state = json.loads((HERE/'status.json').read_text('utf-8'))
assert state['phase'] != 'closed', 'Session already closed; do not repeat'
assert all(x['status'] == 'idle' for x in state['role_cursors'])
stamp = now.isoformat()
paused = []
for ident, key in [('git','scheduler'),('automation-3','cutoff')]:
    config = tomllib.loads((Path('C:/Users/mj528/.codex/automations')/ident/'automation.toml').read_text('utf-8'))
    assert config['status'] == 'PAUSED', (ident, 'official pause required')
    assert hashlib.sha256(config['prompt'].encode()).hexdigest() == state[key]['prompt_sha256']
    state[key].update(status='PAUSED', verified_at=stamp, verified_by='official automation_update success and actual TOML read; prompt unchanged')
    paused.append({'id':ident,'status':config['status'],'verified_at':stamp,'prompt_unchanged':True,'method':'official automation_update, then read-only config verification'})
(HERE/'automation-pause-confirmation.json').write_bytes((json.dumps(paused,ensure_ascii=False,indent=2)+'\n').encode())

summary = f'''# 第二轮两小时研究：最终总结

本轮授权时段为2026-10-17 12:19:08—14:19:08（北京时间），实际收束记录于{stamp}。五个角色均已完成在途任务、停止写研究产物；主控和一次性收束两个自动化已通过正式工具暂停。没有追加研究时长。

## 先看什么

- [通俗导读](../../../papers/damping-output-boundaries/research/read-this-first.md)：不必先读公式，先看这篇论文究竟回答什么。
- [理论稿v007](../../../papers/damping-output-boundaries/manuscript/theory-draft-v007.md)：五个主节、两幅原图、八条参考，较长证明放附录。
- [主张账本](../../../papers/damping-output-boundaries/research/claims.md)、[最终选题卡](../../../papers/damping-output-boundaries/research/topic-cards/T001.md)、[待用户决策](../../../papers/damping-output-boundaries/research/decisions-pending.md)。

## 现在道理讲到哪一步

只知道阻尼增加多少倍，未必足以保证某个位置的最大反应最多放大多少。不同振动方式原先可能互相抵消，增加阻尼改变了这种抵消。这个现象已有先例；我们整理并补强的是规定模型下的共同保证、真实反例及适用边界。

1. 至多两个有效模态有保守共同上限；真实正参数三层模型则能打破只依赖阻尼倍数的保证。无界的是两状态的峰值比，不是绝对振动无限大。
2. 固定模型、限制输入时长后，完整峰比仍有有限界，输入结束后的反应全部计入。近抵消条件的最坏量级与输入允许持续多久已经区分，并给出联合边界。
3. 每个模型各有上限，不代表所有模型共用上限。对整个正参数类，单纯限制秒数在所列阻尼范围内仍不够；换模型并配套压缩输入可保留峰比。
4. 再给质量和刚度设置全模型共用的固定正下限、有限上限，并保留输入时长上限，就能恢复范围内的共同有限界。目前证明的是存在，还没有工程可用的数值。

指定一维模型族的精确5%→8%例子保留隐式定义；限定参数域的唯一性和小阻尼目标渐近成本得到补强。全正三层类的临界输出阻尼范围、预给基准阻尼的跨模型分类也已写入正文/附录。这些数学分界不是建议阻尼或工程安全线。

## 做了哪些实际核查

新解析结果按各自前提经过不同作者审核，主控逐项读取并核对关键接口；v007另有数学整合与引用整合两项审阅，通俗导读经过找误读、四处澄清和新SHA增量复核。最终稿SHA为93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323；导读SHA为5633d02ae47176cabb200fb467a96ac067e7e0cfcc5646ea71ea7976daeeb72f。

本轮只做有限谐波对照、理论界图及解析常数独立算术复核；它们不是完整峰值的普遍证明。保守充分时长证书仍很松，不能当实际地震或必要最短时长。没有操作ETABS求解器、付费计算或投稿。原稿、原数据和冻结证据未覆盖。

机器检查覆盖JSON/脚本语法、本地链接、冻结SHA、暂存字节、式号与原图/公式保留；v007映射56个身份、99个有序唯一式号通过。这不等于形式化证明器认证或历史优先权认证。

## 查新得到什么、还缺什么

2025年的近先例已经读到关键模型/零点条件，并定向读至正文文字末尾；它采用两系数Rayleigh阻尼，三异正频共同模态阻尼与其直接范围不同，而两模态可重合。原文已有虚轴边界和阻尼优化，不能把这些概念称为新。复杂原式OCR、学位论文与更广等价推论仍未核完。

最后还核实了一般输出比先例允许增长不停的L2e输入，本题主要使用最终结束的紧支撑L1输入；输入域不简单包含，区别不能只说成L2与L∞不同。非结构解析例解释了为何不能随意交换卷积次序；它不是新的物理阻尼反例，也不能替代创新性核查。

下一步最值得投入的是三项具体原文对照：Rath学位论文及一般零点分类；L034/L035的精确核积分与Sultan其余等价推论；一般输出比理论能否直接推出本题的模型统一界和联合阶。没有找到同式不证明首次。

## 交付与后续决定

当前得到可复核的理论研究稿，尚不能称投稿定稿或已确认创新。用户不需要裁决公式；之后决定期刊、语言、正式署名及是否另写工程案例。继续研究需另行安排预算，本轮不会自动续期。

仓库[research-paper-lab技能](../../../.agents/skills/research-paper-lab/SKILL.md)与[框架](../../../docs/多角色论文研究框架.md)保留五角色、文献复查、选题卡/演变、定时检查点和证据边界，可继续复用；本轮没有把课题参数写回通用技能。

历史检查点R001—R008均有实际提交/远端核对；R004一次TLS失败经唯一一次重试成功。最终收束验证见[R009](R009.md)。大原始文件、论文全文、NPZ、未知文件及角色可变历史问答不加入最终提交；可变历史仅保存本地指纹清单，稳定研究证据和当前交接状态已经版本化。
'''
(HERE/'final-summary.md').write_bytes(summary.encode())

decisions = '''# 现在需要你决定什么

本轮两小时研究已结束，方向仍是你选定的“先把理论道理讲清楚”。不用再选A/C，也不用替团队判断公式。

## 已经拿到的东西

有一版经过数学和引用整合复核的理论稿，还有一份不用先读公式的[通俗导读](read-this-first.md)。证明能说明共同保证在什么条件下成立、失效和恢复；尚未得到可直接用于工程判断的实用数值。

## 后面由你决定的事

1. **下一阶段还投入多少时间。** 建议优先确认“别人是否已经证明过同条件结果”，再做英文润色或投稿格式。当前两项定时任务已暂停，不会自动延长。
2. **期刊、语言和正式署名。** 等贡献定位核清后再定，不需要现在仓促选择。
3. **是否另写工程案例文章。** 原工程数据和观察保留；它与当前理论论文分开推进，后面再给具体资料需求。

## 团队仍要解决的技术问题

- 补核Rath博士论文和一般零点分类，确认已有结果是否覆盖本题。
- 补核两篇二阶核积分论文的精确公式，以及结构峰值增益文献的等价推论。L034仍缺全文；L035已有两页正文文本，但精确公式/分支和原页核对未完。
- 把一般输出比理论与本题的输入范围、完整峰值和跨模型常数逐条对上；不能只凭名字不同就说有创新。

这些是团队的查证工作，不要求你选哪条公式正确。现有结果尚不能承诺首次发现、特定建筑机理或工程安全保证。详情见[第二轮最终总结](../../../research/sessions/20261017-1219/final-summary.md)。
'''
(PAPER/'research/decisions-pending.md').write_bytes(decisions.encode())

card = f'''# T001 先把增阻尼的道理讲清楚

最终快照v020，{stamp}。用户已选A理论主线；第二轮12:19:08—14:19:08结束，两个自动化已暂停，五角色均无在途工作。

## 研究判断

已有可复核理论稿v007：至多双有效模态的保守共同界、真实三层反例、失谐与输入时长联合边界、全类阻尼范围和跨模型分类、固定秒数缩放及正紧参数盒恢复有限性。无界的是峰比而非绝对振动；存在界不等于已有工程实用数值。

## 交付与限制

| 维度 | 当前结论 | 尚未解决 |
|---|---|---|
| 数学 | 各限定结果已独审，v007数学整合0必修 | 非形式化认证，常数未称最优 |
| 可读性 | 通俗导读四处澄清后新SHA复核通过 | 复杂证明仍在附录，不要求用户裁公式 |
| 文献 | 2025关键正文及后半部定向阅读、Rayleigh关系、一般输出比输入域均留有原文定位 | 学位论文/L034、精确核公式/更广等价推论与历史优先权未闭合 |
| 数值 | 有限谐波/理论界/常数复核支持说明，原图证据保持 | 采样不是完整峰证明，充分时长很松，不是实际/必要时长 |
| 工程 | 原生案例与拟合资料完整保留，退出本篇主线 | 未解释唯一机理、未给安全线或实用系数 |
| 决策 | 用户理论方向不变，本轮预算关闭 | 后续预算、期刊/语言/署名及另写工程案例由用户决定 |

建议下一步先补查同条件先例，确认具体贡献，再考虑投稿包装；不再自动派工或扩大范围。

入口：[通俗导读](../read-this-first.md)、[理论稿v007](../../manuscript/theory-draft-v007.md)、[主张账本](../claims.md)、[待决清单](../decisions-pending.md)、[最终总结](../../../../research/sessions/20261017-1219/final-summary.md)。
'''
(PAPER/'research/topic-cards/T001.md').write_bytes(card.encode())
snapshot = re.sub(r'\]\((?!https?:)([^)]+)\)',lambda m:'](../../'+m.group(1)+')',card)
(PAPER/'research/topic-cards/history/T001/v020.md').write_bytes(snapshot.encode())
def append(path,text):
    with path.open('ab') as f:
        f.write(('\n'+text+'\n').encode())
append(PAPER/'research/topic-cards/events.md',stamp+'：v019→v020，两小时预算关闭，v007及通俗导读已审，最后输入域比对完成；新颖性与工程实用性未升级，两个自动化正式暂停，后续待用户新预算。')
append(PAPER/'research/claims.md',stamp+'：会话20261017-1219到期关闭，所有限定数学状态按原独审保留，未将未决文献/工程问题改为完成。v007与导读保持冻结，五角色无在途；停止派工，不自动延长。')

front = ROOT/'README.md'
b = front.read_bytes()
old = '当前执行：[第二轮两小时理论攻坚](research/sessions/20261017-1219/plan.md)，用户已选择集中理论，时段12:19:08—14:19:08。主控定时协调原五角色，状态见[活动会话](research/active-session.json)。第一轮研究及关闭记录保持历史。'
new = '第二轮两小时理论攻坚已结束（12:19:08—14:19:08），两个定时任务已暂停。先看[通俗导读](papers/damping-output-boundaries/research/read-this-first.md)、[已审理论稿v007](papers/damping-output-boundaries/manuscript/theory-draft-v007.md)及[第二轮最终总结](research/sessions/20261017-1219/final-summary.md)。用户已选理论主线，新颖性仍未确认；第一轮记录保持历史。'
assert old.encode() in b
front.write_bytes(b.replace(old.encode(),new.encode()).replace('[两小时最终总结]'.encode(),'[第一轮最终总结]'.encode()))
append(PAPER/'README.md','本轮已于14:19截止收束，两个自动化已暂停；见[第二轮最终总结](../../research/sessions/20261017-1219/final-summary.md)和[普通中文待决清单](research/decisions-pending.md)。')

state.update(phase='closed',recorded_at=stamp,closed_at=stamp,close_reason='user-approved two-hour budget ended; unresolved novelty remains',latest_round='R009.md',checkpoint_open=True,pending_push=None,prepared_publication=None)
state['next_checkpoint']='Closed. No new research or scheduler resume without new user instruction. Frozen v007 and reader guide accepted; unresolved source/engineering limits retained.'
state['latest_increment_receipt']={'recorded_at':stamp,'disposition':'all final increments collected; no in-flight research'}
(HERE/'status.json').write_bytes((json.dumps(state,ensure_ascii=False,indent=2)+'\n').encode())
active=json.loads((ROOT/'research/active-session.json').read_text('utf-8'))
active.update(phase='closed',closed_at=stamp,summary='research/sessions/20261017-1219/final-summary.md')
(ROOT/'research/active-session.json').write_bytes((json.dumps(active,ensure_ascii=False,indent=2)+'\n').encode())
(HERE/'R009.md').write_bytes((f'''# 最终检查点：两小时到期收束

{stamp}执行行政收束；研究授权截止14:19:08，之后未派新研究。五角色已无在途，两个正式自动化已调用暂停并读实际配置核准，原prompt不变。最终总结、普通中文待决、v020选题快照和主入口更新；正式v007、导读及全部冻结证据保持原字节。后续不自动延长，不把未决新颖性/工程值改成完成。

最后一次正常Git提交/推送前检查明确清单、实际内容、JSON/AST/本地链接/冻结身份/暂存字节。未知5E-07、NPZ、原始Excel/EDB、论文全文与可变角色历史问答均排除。本轮常规Git成功均核对远端；最终推送仍按命令级代理、最多一次重试、无强推。
''').encode())
print(stamp)
