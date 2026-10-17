> Canonical交接副本：2026-10-17T21:32:36+08:00。W5原文件保留；本副本仅调整相对链接并整合已核纠正，详见R001总包。论文全文与页图不进入本目录。

# R001 CSI与局部传力一手原文复核

角色：创新性验证；作者称呼：小香金猪。读取开始2026-10-17 21:17:19 +08:00；关键原页复核至21:23:41 +08:00。所有时间为Asia/Shanghai。本报告只核下列版本及所列页，不假定与新工作簿软件版本完全相同。

## 结论与来源身份

Maxwell串联本构、有效阻尼的交叉耦合限制、弹性剪力与含阻尼总剪力的区分均为可直接引用的已有理论/软件定义，不能列为本轮新理论。CSI官方FAQ没有给出`ζ0 E_link/E_global`能量比式；不能将该比值错误归引到FAQ。

| N-LID | 一手原文与版本 | 本地证据/可得程度 | 本轮实际核查 |
|---|---|---|---|
| N-L001 | Computers & Structures, Inc., *CSI Analysis Reference Manual*, ISO GEN062708M1 Rev.15, July 2016；[官方全文](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf) | [PDF](../../../../../../../W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence/CSI-Analysis-Reference-Rev15-2016.pdf)，556页，7811196 B；SHA256 `7f6f6890afee2e1890d33f5d34d53d8e23f60850890bd230848642b50a6291ac` | 正文定位印pp277—281、357—361；亲看印p279/PDF301、印p280/PDF302、印p359/PDF381原页。其余所列页为原文文本复核。 |
| N-L002 | Song J., Chu Y.-L., Liang Z., Lee G.C., *Modal Analysis of Generally Damped Linear Structures Subjected to Seismic Excitations*, MCEER-08-0005, 4 March 2008；[NIST托管原报告](https://nehrpsearch.nist.gov/static/files/NSF/PB2009102311.pdf) | [PDF](../../../../../../../W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence/MCEER-08-0005.pdf)，228页，1798029 B；SHA256 `941a58f7a8e88975405ccfdfeea412a42d9f982ca7ff3c6a055a93c8c25fda48` | 亲看印p38/PDF56 Eq3.58—3.59、印p40/PDF58 Eq3.62—3.63；印p39/PDF57文字定位。 |
| N-L003 | CSI, *Damping FAQ*, 8 October 2022；[官方HTML](https://web.wiki.csiamerica.com/wiki/spaces/kb/pages/2006597/Damping%2BFAQ) | 公开HTML全文；无PDF页码。访问2026-10-17 | 核“Can the software calculate the percentage of critical damping achieved by dampers added to a model?”完整两种估计方法及相邻节。 |

## 命题—原文—前提—复用范围

| 命题 | 原页/式定位 | 一手原文实际支持及前提 | 关系与可复用结论 | 仍未解决 |
|---|---|---|---|---|
| M-C001/M-C004：Maxwell不是单一纯黏滞常数 | N-L001印pp279—280，Fig67及无编号本构式；[亲看页](../../../../../../../W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence/CSI-Rev15-PDFpage-302.png) | 线性弹簧与速度幂黏滞段串联，内变形为两段之和。速度指数正值。 | `same-claim`于本构与拓扑；总端部变形速度不能直接作为黏滞段速度。 | 新装置实际k、c、α、局部DOF、线性有效参数与真实非线性参数、分析类型尚由主控核。 |
| M-C002：Global Damping分母身份 | N-L001印pp358—359，Global Energy Response Components；[亲看页](../../../../../../../W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence/CSI-Rev15-PDFpage-381.png) | Global项对应工况/材料背景阻尼；装置黏滞耗散另列。模态与直接积分的背景阻尼定义不同。 | `related-not-equivalent`；可按分项检查能量口径，不能由列名推出统一ζ0。 | 当前导出`Link Damper Energy`与该版“Nonlinear Viscous Damping”的字段映射仍需当前软件/导出设置佐证。手册没有给ζ0能量比公式。 |
| M-C004：有效模态阻尼替代全耦合 | N-L001印pp278—279，Linear Effective Damping；[亲看页](../../../../../../../W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence/CSI-Rev15-PDFpage-301.png) | 反应谱/线性模态时程将有效阻尼转成模态比时忽略交叉耦合；原文明确其重要性。 | `related-not-equivalent`；“忽略耦合可失准”已有，不是本轮创新。 | 没有给本工程误差大小，也没有证明本工程每个输出必失准。 |
| M-C003：弹性剪力、总剪力、装置力分开 | N-L002印p38 Eq3.58/3.59、印p40 Eq3.62/3.63；[p38](../../../../../../../W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence/MCEER-PDFpage-56.png)、[p40](../../../../../../../W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence/MCEER-PDFpage-58.png) | 一般阻尼线性结构、给定剪切楼层/布置映射；装置力节忽略较小固有阻尼，将C全部归附加装置。 | `same-claim`于输出身份/布置映射；可直接复用区分，不重新宣称发现“阻尼力进入剪力”。 | p40公式不能把背景C归成每只装置；任意Maxwell需内部状态，不能无条件代入固定C速度式。真实空间切口仍须映射。 |
| M-C002：软件是否直接报告临界阻尼百分比 | N-L003上述HTML节，条目1—2 | FAQ提供有效模态信息估计与单自由度释放衰减近似，后者引Wilson书p228。 | `related-not-equivalent`；它不认证记录能量比等于模态阻尼。 | Wilson原书p228本轮未读，不将FAQ的间接引用升级为原书复核。 |

以上是浓缩转述；不复制大段原文。全文来源、页码和图页保留供后续复查。

## 可复用的局部力公式接口

采用N-L002符号，弹性层剪与含阻尼一般层剪分别为

\[
\mathbf F_{IS}(t)=T_S Kx(t),\qquad
\mathbf F_{GS}(t)=T_S\{C\dot x(t)+Kx(t)\}.
\]

来源：印p38 Eq3.58/3.59。必须同刻相加；峰值之和不等于合力峰值。其装置力式为`F_DR=T_DC T_S C xdot`（印p40 Eq3.62），只在原文该节把C全部归于装置的假设下使用。本文工程有明确背景阻尼时须分离，真实Maxwell优先采用已核局部端力与几何映射。

这是线性剪切模型的既有接口，不自动等于ETABS任意三维切口的输出定义；需另核切口边界、方向、是否计入装置及两端连接件。

## 失败路径、版本边界与后续接口

- 公共网页读取全文成功；PowerShell `Invoke-WebRequest`首次取CSI PDF遇TLS EOF，随后Python标准库从同一官方URL取得有效PDF并核文件头/散列。无需改软件或访问账户。
- bundled Python无`fitz`，改用已有Poppler渲染，退出码0；已用图像工具亲看上述关键页。未安装依赖。
- 本轮未读新Excel数据、未求解、不创建调度/聊天、不修改主账本或其他角色文件。下载与原页PNG只在本角色`evidence/`。
- 新工作簿实际软件版本未核；2016手册中的产品能力限制不能直接当2026版本限制。此处复用的是明确模型/输出定义和方法前提。
- 后续以[可复用公式与定义](R001-reusable-formulas.md)固定能量比口径，再由主控提供背景阻尼及完整同刻数据检验。本文件不代替其数据验证。
