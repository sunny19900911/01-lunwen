# Rath2025最近先例：来源核查与正文缺口

2026-10-17，Asia/Shanghai；本项开始13:17:11，预算≤6分钟、最多3条新查询。临时标识 **Rath2025（L-ID待主控登记）**；状态 **insufficient-text / candidate定位**。不改正文、claims或正式参考，不联系作者/登录/付费，不派子任务，不重试主控已失败DOI短链。

## 已确认与未确认的书目

[作者大学实验室正式出版物页](https://psdl.engin.umich.edu/publications.php)Journal Papers第2项列：Rath S.、Radgolchin M.、Maheshwari A.、Awtar S.；*Non-minimum Phase Zeros of Multi-DoF Damped Flexible Systems*；2025，Journal of Vibration and Acoustics；DOI **10.1115/1.4067639**。该项给1—27，并只链接DOI，没有公开作者PDF附件。1—27保留为该列表原始记录，不据此断定正式期刊页段或原件页数。

[ResearchGate元数据页](https://www.researchgate.net/publication/387993513_Nonminimum_Phase_Zeros_of_Multi-Degrees-of-Freedom_Damped_Flexible_Systems)显示扩写题名*Nonminimum Phase Zeros of Multi-Degrees-of-Freedom Damped Flexible Systems*及相同DOI；页面明确无全文、只能请求全文。本次不请求、不将其登记为作者上传稿；作者归属未认领，不能借平台的其他被引论文正文替代本篇。该页卷期/月份及1—27未由可读出版社记录另核，不升级为正式书目信息。

三个查询同时出现第三方声称PDF的页面，但未确认原作者上传/许可，故未打开或下载其正文。没有取得本篇正式版或作者稿字节，没有PDF SHA、目录、页式或版本一致性证据。

## 新请求结果与停止边界

| 入口 | 实际结果 |
|---|---|
| Crossref指定DOI的公开work记录 | 一次web工具Internal Error，无HTTP码/可读登记内容；未重试或换壳重发。 |
| ResearchGate指定文章页 | HTML可读，明确No full-text available。只作获取状态定位，不作为定理/模型一手证据。 |
| OpenAlex指定已知DOI记录 | 一次工具不可访问；仅尝试定位合法来源，未得元数据，未据它作研究结论。 |
| ASME该期刊article-lookup/doi入口 | 一次工具不可访问，无可核HTTP码；未得正式长URL或正文，未重试。 |
| 主控已试的doi.org短链 | 仅保留主控转交的Internal Error记录，本角色没有重新打开。 |

3条查询已用完，未新取全文。上述传输/工具错误不等于HTTP403、付费墙、论文不开放或作者稿不存在；不据此推断访问政策。精确URL与查询见[源清单](Rath2025-source-manifest-001.json)。

## 为什么摘要不足以做同条件排重

已见平台摘要谈一般多自由度、proportional viscous damping、无阻尼/有阻尼零点的变量代换及NMP消除条件；这些只能说明优先级高，**不能核定原文前提、精确公式或创新性**。尤其不能凭“proportional”自行判定其为Rayleigh的αM+βK、各阶共同ζ、仅质量比例，或一般Caughey经典阻尼。不同文献对该词用法须由原式核实。

本篇也不能继续笼统归到旧L016的一刚体+两柔性专门分类；新题名/摘要更一般，但没有正文仍不能断言它已经包含三正频率、全部输入/测量映射或本稿物理类。一般B/D若允许任意选择，真实topcut可能是其特例，不能因作者未在摘要写“剪切楼”就宣布不覆盖。

## 取得合法原文后的最小核查契约

1. 只读模型和核心定理页：M/K正定还是含刚体模态；n与频率假设；阻尼矩阵的**实际公式**及模态ζ路径；输入B与位移测量D是否任意实向量，能否代入B=Mb、D=ℓᵀ。
2. 核零点变量代换及跨虚轴充要条件的原式/定理号；将真实三层投影的留数矩代入后，是否直接化成ζ*²=D/(4S³)或等价式。不能以公式外观或记号不同排除等价。
3. 若前项能映射，再查其是否给跨全部正m/k的阈值范围、等频上端的合法链逼近与逐目标实现。未明写范围也可能由一般定理及经典AM–GM/连续性容易推出，需分别评价“已有覆盖”“经典推论”“具体物理实现”。
4. 本稿完整L∞输出比还涉及共同紧支撑输入与全尾段桥接；即便旧文只讲零点，也可能覆盖本稿机制的一部分。没有峰比字样不意味着不影响贡献定位；反过来，零点条件相同也不自动等于全部峰比量词相同。

**给主控的结论：** 该2025一般多模态来源仍值得最高优先级补全文；本轮只确认大学作者书目与正文未得，没有任何同条件覆盖/不覆盖裁决。不能用标题、摘要或有限搜索缺口为现稿排重。新猜想的预给ζ₀跨模型阈值仍由其数学任务处理，本项未读取或抢算。冻结后停止，不自行扩预算/重试/登记L-ID。
