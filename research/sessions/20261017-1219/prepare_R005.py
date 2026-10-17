"""Prepare master-owned R005 checkpoint; never reads local raw or unknown files."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import re

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PAPER = ROOT/'papers/damping-output-boundaries'
now = datetime.now(timezone(timedelta(hours=8))).isoformat()

def append(p, text):
    with p.open('ab') as f:
        f.write(('\n'+text+'\n').encode('utf-8'))

append(PAPER/'research/claims.md', f'''{now}（R005）：最近文献L038已取得公开原件正文文本，不再只有摘要。主控实际open正文首页及原印021007-2–4，核式(2)两系数Rayleigh C=2c_M M+2c_K K、式(4)模态分母、式(6)代换和式(12)含虚轴等号条件。网页OCR/未取得PDF及图像、后续未逐页核完的限制保留；三异频共同正模态阻尼与该族的区别交不同作者独核，不据适用范围不同宣称新颖性。详见roles/literature/theory-session002/Rath2025-public-preview-check-001.md。

| C030 v1 | 固定任意物理输入半时长Tfix>0后，全正m/k三层真实topcut类的最优完整峰比上确界与不限有限支撑时长的跨模型上确界相等；因而z>0、κ>1时有限 iff z>sqrt(2/27) | testing | ideation/theory-session002/fixed-physical-duration-scaling-candidate.md SHA2c1f5db9eb62646b20485b35986d9670415965d5df2cec8df9bb34dfb213167a；analytic-derivation candidate，主控全文读并另核时域因子，已派异作者独审 | K→σ²K、C→σC、真实ell→σ²ell，fσ=f(σt)、uσ=σ^-2u(σt)，全尾峰不变；每条见证可选不同有限模型，不称同一固定模型固定T无界，不外推带宽/导数/参数盒；未入v006 |
''')

card = f'''# T001 先把增阻尼的道理讲清楚

版本v017，{now}。用户已选理论主线，第二轮14:19:08结束，不再重复选方向。

## 我们要回答什么

只知道阻尼增加了多少，能不能保证同一个输出的最大反应不会放大得太多？一栋固定的模型有保证，是否就意味着所有模型共用一个保证？

## 已经站得住的结论

- 一两种有效振动成分有保守的共同上限；三层真实模型在特定条件下可以打破只依赖阻尼倍数的保证。无界的是两状态的峰值比，不能解释成绝对振动无限大。
- 固定一栋模型，输入持续时间也有限时，完整峰值比有上限，包括输入停下后的全部反应。接近精确抵消条件时，最坏放大量同时受持续时间和偏离程度限制。
- 预先给定基准阻尼后，再把所有正质量、正刚度三层模型放在一起比较，存在一个明确分界。分界下可找到某个模型失去统一保证；正好在分界上，每个模型各自有限，但所有模型没有共同有限上限；严格超过分界才有允许依赖基准阻尼的共同保证。这不是工程建议阻尼值。
- 能实现精确抵消的阻尼范围已经给出合法模型构造。质量固定的一维模型族另有唯一选择及小目标成本结论，不能把这个唯一性扩到所有结构。

## 本检查点的变化与限制

| 工作 | 真实状态 | 仍须保留的边界 |
|---|---|---|
| 正文 | v005已独审接纳并推送，作者获准另存v006纳入C028/C029 | v006尚在写，未接纳或发布；C030不在本次升稿范围 |
| 跨模型分类 | C029独审及主控复核通过；R004冻结后回报，本检查点才提交 | 正阻尼、共同各阶阻尼比、真实弹性topcut及完整尾段；经典范数工具不是新原理 |
| 固定秒数 | 新C030缩放候选已全文读，正独审 | 改变模型刚度可压缩时间并保留峰比；未声称同一模型固定时长可任意放大，也未约束带宽/刚度盒 |
| 最近先例 | 已正常公开读取2025原件正文p1–4关键公式，L038登记 | 两系数Rayleigh与共同模态阻尼差别正独核；其后半篇/一般经典阻尼先例仍待核，不宣布首创 |
| 数据和图 | 原冻结结果、两原稿图与保守时间证书保持 | 无新时程/求解器/拟合；原充分时间很松，不是实际或必要时长 |

## 你之后需要决定什么

现在没有卡住研究、必须由你裁决的公式。先继续核证明和先例，最后再由你决定期刊、语言、正式署名，以及是否另写工程案例。数学结论成立与值得按何种贡献投稿，需要分别判断。

依据：[主张账本](../claims.md)、[通俗待决清单](../decisions-pending.md)、[当前会话计划](../../../../research/sessions/20261017-1219/plan.md)。
'''
(PAPER/'research/topic-cards/T001.md').write_bytes(card.encode('utf-8'))
snapshot = re.sub(r'\]\((?!https?:)([^)]+)\)', lambda m: '](../../'+m.group(1)+')', card)
(PAPER/'research/topic-cards/history/T001/v017.md').write_bytes(snapshot.encode('utf-8'))
append(PAPER/'research/topic-cards/events.md', f'{now}：v016→v017，C029独审接纳正式进入本检查点；最近2025原件关键正文可公开读，旧无正文状态保留历史。C030固定物理时长跨模型缩放仍testing，v006在途不提前称成稿。用户A方向不变。')

append(HERE/'R005.md', f'''{now}补充：主控全文读v006范围并准入≤10分钟实际新稿，仅C028/C029，五主节两原图，详证附G；未纳C027/C030。文献正常公开阅读取得原件身份与核心两系数Rayleigh条件，主控也open核原文相关行。先前把公开阅读误加上传许可门槛的路径已纠正；不删除旧失败记录。文献继续同一页后半篇的有限范围核查，猜想独核三频/两频差别。C030缩放候选已冻结、异作者独审在途。没有新数据实验或用户技术选择；R005仍不将活动稿件stage。

反对与失败路径：零点移动/增阻尼不利机制已有Rath先例；模型范围差异不能证明新颖性。即使C030成立，改变模型并压缩输入频率不等于同一建筑里的短地震结论。来源网页复杂根式OCR损坏，尚未逐页审全篇，不能假装完整排重。
''')

status = json.loads((HERE/'status.json').read_text('utf-8'))
status['recorded_at'] = now
status['role_work']['writing'] = 'Actual v006 authorized <=10min, C028/C029 only; not yet frozen or accepted'
status['role_work']['ideation'] = 'C030 frozen and under independent review; now <=5min Rayleigh/common-zeta scope comparison only'
status['role_work']['verification'] = 'C030 exact fixed-time cross-model scaling independent review <=5min'
status['role_work']['literature'] = 'L038 public original body model/zeros read; <=5min same-page remaining-scope followup, no search'
status['next_checkpoint'] = 'R005 OPEN: C029 accepted, public2025 primary text/status updated, C030 testing. v006 actual in progress and excluded pending freeze/review; cutoff14:19:08.'
for item, suffix, activity in zip(status['role_cursors'], [27,26,23,17,22], ['active','active','active','idle','active']):
    item['cursor'] = item['cursor'].rsplit(':',1)[0]+':'+str(suffix)
    item['status'] = activity
(HERE/'status.json').write_bytes((json.dumps(status, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
print(now)
