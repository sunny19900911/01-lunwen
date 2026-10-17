# 论文研究与写作

使用 Codex 协调猜想提出、独立证明与反例、文献原文复查、ETABS实验拟合、论文写作，并把研究依据和技能放在同一版本库中。主控每十分钟汇总检查点，记录选题演变，定期提交选题卡供用户最终决策。

当前执行：[2026年10月17日两小时自主协作](research/sessions/20261017-0847/plan.md)，角色聊天见[线程登记](research/sessions/20261017-0847/threads.json)，待决事项见[独立清单](papers/damping-output-boundaries/research/decisions-pending.md)。本次常规提交/推送已由用户明确授权，截止后不自动续期。

本次课题的[论文、核心图与证据审阅入口](papers/damping-output-boundaries/README.md)集中连接冻结稿、主张账本、两版选题方案及文献补件；[当前选题卡](papers/damping-output-boundaries/research/topic-cards/T001.md)保留实际演变与尚未解决的判断。

- [论文研究框架](docs/多角色论文研究框架.md)：角色、研究循环、论文目录与启动方式。
- [research-paper-lab 技能](.agents/skills/research-paper-lab/SKILL.md)：可执行的研究工作流。
- [角色提示词与交接协议](.agents/skills/research-paper-lab/references/collaboration-protocol.md)：检查点、运行去重、角色提示词和后台模板。
- [ETABS 拟合契约](.agents/skills/research-paper-lab/references/etabs-fitting.md)：数据配对、验证划分、参数可识别性和推论边界。
- [文献复查协议](.agents/skills/research-paper-lab/references/literature-review.md)：将新猜想、证明和反例与已收集论文原文逐条比对。
- [选题卡与演变记录](.agents/skills/research-paper-lab/references/topic-cards.md)：记录各维度判断、版本变化和用户待决事项。
- [选题卡模板](.agents/skills/research-paper-lab/assets/topic-card.template.md)：文献差异、贡献、证据、数据、可行性与备选路线。
- [论文蓝图](.agents/skills/research-paper-lab/references/paper-blueprint.md)：从主张、证据到章节与图表。
- [研究计划模板](.agents/skills/research-paper-lab/assets/research-plan.template.md)：首次启动课题时按需采用。
- [仓库约定](AGENTS.md)：文件所有权、数据、Git和验证规则。

## 启动一项研究

在本仓库目录打开 Codex，提供具体论文问题和已授权的资料路径：

```text
使用本仓库 .agents/skills/research-paper-lab/SKILL.md 中的 $research-paper-lab。
课题为【研究问题】，资料与ETABS导出位于【路径】。
按仓库AGENTS.md组织主控、猜想、验证、文献复查、实验拟合与作者。
先完成一轮：建立证据账本、论文结构、原文对照、选题卡和资料缺口。
每十分钟汇总检查点；实验范围和超时为【实际预算】。
已有论文位于【原文或索引路径】；每30分钟或重大变化更新决策版选题卡。
```

围绕实际候选问题创建 `papers/<topic>/`，无需等最终定题；不要先建空项目。角色交接读取该课题的 `research/` 计划、主张、轮次和选题卡，脚本与结果放 `experiments/`，稿件放 `manuscript/`；既有论文用 `literature/index.md` 索引并记录原文定位。最终选题由用户决定。

本仓库中的技能是共享来源；不同机器从仓库读取。若另有个人安装副本，同名技能不会自动合并或同步，维护时以仓库为准并显式更新副本。Codex可从仓库 `.agents/skills/` 发现技能，见[官方技能说明](https://developers.openai.com/codex/skills)。

## 十分钟汇总与持续工作

技能定义协作方法；长期定时研究需要正式调度器。先验证一轮手动运行，再明确总预算、停止条件、数据和账户权限，按用户指示建立同一聊天的定时唤醒。每轮内部存档，有重要发现、失败或需要决定时再通知。

默认每个检查点复核选题卡，每30分钟或重大变化形成决策版，短任务结束交首版；用户可改间隔。保留旧判断、触发证据和新判断，交付可选路线与资源需求；用户要求固定周期报告时按其偏好执行。未配置调度时不会离线定时更新。

GitHub保存获准的文本、脚本与结果版本。首次提交、后续推送、数据上传和发布分别按明确授权执行。远端版本与本地未提交改动有区别，跨机器交接前应确认使用的是同一版本。

原始ETABS模型和大导出默认留在受控本地目录；仓库中的数据清单提供指纹及获取条件。本框架不预设某个工程结论成立；本次实际运行的分析及其限制以课题证据记录为准。
