# R008：力回零Maxwell候选的一维控制近邻来源核查

角色：创新性验证子任务。真实开始：2026-10-17 23:36:06 +08:00（Asia/Shanghai）；23:42前交接。仅本文件可写，其他文件只读；无工程数组/Excel、ETABS、账户、上传、Git或跨聊操作。候选正确性归角色2 R014，本角色没有重复证明。

## 冻结候选

首次动作实际读取并核SHA256：

- 路径：`W5-重燃双塔连体/research/maxwell-20261017/roles/verification/force-return-candidate/力回零Maxwell耗散峰力可行区间-作者候选.md`。
- 文件大小：6014 B；SHA256：`1B4D4888B5181EAFB9ACCF2F7A19330BD88B8D0427C4FD2FFD846A2C42A1B446`。
- 原文件mtime：2026-10-17 22:21:24（宿主显示，Asia/Shanghai）；本轮只读，未改写。

本轮排重键：固定正参数k,a,q,V,T；`F'=k[v−a*sgn(F)|F|^q]`；`|v|≤V`几乎处处；`F(0)=F(T)=0`，不要求总变形回零；指定峰值`M=max|F|`；真实状态耗散`D=a∫|F|^(q+1)dt`。候选给出可达时间、精确可行耗散区间`[L(M), U_T(M)]`、等待/饱和/驻留/饱和的取等族以及固定D的双侧反峰界。以上为候选身份记录，不是独立认证。

## 结论

**本轮取得一份可读的一维控制作者原文，足以确认“有界控制、状态积分代价、固定端点、快速过渡加驻留”的基本结构已有；未取得全部同条件的Maxwell精确区间旧发表。** 不能把时段结构或经典充分性验证方法列为新方法，也不能把本轮有限未发现写成候选首次。

已读近邻是无漂移积分器的最小状态平方积分问题，不是固定峰值的非线性Maxwell回零可达代价集合。关系只定为`related-not-equivalent`。精确L/U、所有中间耗散可达、反峰区间的发表覆盖仍未解决；方法来源不替代角色2的正确性审核。

## 实际检索：恰2条

2026-10-17 23:36前后执行：

1. `scalar optimal control state constraints integral cost bang singular bang`
2. `"scalar" "reachable set" "cost" "integral" control`

随后只打开下述一个最直接的一维作者正文；于23:36:52工具时钟已确认可读，此后不再新增检索或追引文。没有重复2003、RC、旧失败下载或一般阻尼非单调搜索。

## 主源：Cots2021的一维bang-singular-bang计算示例

Olivier Cots，*Bang-Singular-Bang problem and turnpike*，ct gallery，作者页明确日期**November2021**。[作者/研究团队公开正文](https://ct.gitlabpages.inria.fr/gallery/turnpike/1d/bsb_turnpike.html)。HTML全文入口可读，有作者署名和原始notebook链接；本轮读§I及§II开头的模型、控制结构和正则化条件，没有运行其代码或另取notebook。

**版本/证据等级：** 这是作者公开教学/计算示例的一手说明，不是本轮核实的同行评审定理论文。HTML无印刷页码或式号，以下用原节标题及明确公式位置定位；不伪造页码、定理号或DOI。没有将网页的数值计算升级为普遍充分性证明。

| 原文定位 | 原文实际对象 | 与冻结候选的对应及差别 |
|---|---|---|
| §I `Description of the optimal control problem` 首个显示公式 | 最小化`J=∫[0,tf]x(t)^2dt`，`x'=u`，`|u|≤1`几乎处处，`x(0)=1`、`x(tf)=1/2`。 | 同为一维、输入有界、固定端点及状态积分代价；但原文无非线性恢复漂移，端点非零、没有固定绝对峰值M和峰值状态约束。 |
| §I 第二个显示公式及随后静态解段 | 静态问题在`u=0`约束下最小化`x²`，静态最优对为`(x,u)=(0,0)`。 | 说明围绕低成本静态状态驻留是现有思路；不是候选在固定峰M处提高耗散上端点的最大化问题。 |
| §I `Hence, if the final time…` 段及随后分段控制公式 | 时间足够长时，先以`u=−1`快速到静态状态，再`u=0`驻留，最后`u=+1`到目标端点；原文称Bang-Singular-Bang。 | 给出清楚的经典过渡—驻留—过渡结构近邻；原文不提供候选的加载/卸载非线性时间积分、L/U或固定D反函数。 |
| §II `Regularization and simple shooting` 首个显示公式 | 代价加入`−ε ln(1−u²)`，并对ε、tf及端点作数值延拓。 | 正则化目标与候选原目标不同；其平滑数值轨迹不构成候选可测速度开关下精确等号的来源。 |
| §II 开头关于`x(0)=x(tf)=0`的段落 | 零端点被用于正则化求解的静态初始化。 | 不能把该零端点初始化挪称为原文已经处理“零端点但强制达到指定非零峰M”的耗散区间；固定峰条件仍需单独核。 |

### 对边界与术语的具体影响

- 候选恢复项`a*sgn(F)|F|^q`不为零。不能只把Cots的`u`改名`v`便宣称同条件；若通过反馈消漂移，有效控制约束会随F改变，必须重新保留该约束。
- 原文只讨论一个最小化问题及其时段结构，没有在已读部分陈述同一峰值约束下的最大耗散、精确可达代价区间和区间内每个值均可达。
- Cots的零状态驻留是其状态成本最小的内部静态段。候选最大耗散在`|F|=M`驻留，与固定峰约束的边界段有关；不能仅因都有“hold”便把两者的PMP术语或充分性条件视为相同。此处不替角色2判断候选证明。
- 原文没有总变形δ，也没有`δ(T)=δ(0)`约束；“没有这个变量”不能当作已经证明候选非零残余变形下的全部边界。
- 即使一份一般最优控制原文可经严格特例化得到候选，也应分别登记“经典框架直接推论”与“原文打印了同一Maxwell公式”；本轮只建立前一层的结构相关性，未完成这种特例化证明或优先权认证。

## Liberzon既有核查只按原强度复用

只读复用`../R004.md`已经登记的Daniel Liberzon作者公开preliminary copy：[*Calculus of Variations and Optimal Control Theory*](https://liberzon.csl.illinois.edu/teaching/cvoc.pdf)，2011-08-09版本，§5.1.4印pp132–134 / PDF142–144，式(5.20)–(5.24)。R004已核沿轨迹积分验证候选代价与任意可行代价关系的经典充分性框架。

本轮未重新打开该PDF，不增加原页核验强度。该框架没有在R004已读位置打印本候选L/U公式；它也不自动认证零点正则性、固定峰约束、非线性回程或“可达代价集合为整闭区间”等细节。不能把R004方法归属追认为本候选同公式的既有发表。

## 未展开命中与覆盖缺口

两条检索还返回以下线索，但按“能读1份就停”没有打开，**不用于判断其是否覆盖候选**：

- [Gusev2017，*An Algorithm for Computing Boundary Points of Reachable Sets of Control Systems under Integral Constraints*](https://www.researchgate.net/publication/318486864_AN_ALGORITHM_FOR_COMPUTING_BOUNDARY_POINTS_OF_REACHABLE_SETS_OF_CONTROL_SYSTEMS_UNDER_INTEGRAL_CONSTRAINTS)，检索书目给DOI10.15826/umj.2017.1.003；只见检索层，未读原文，不能据摘要中的quadratic/control等措辞排除状态代价的等价表述。
- [*Quadratic order conditions for bang-singular extremals*，arXiv1107.0161](https://arxiv.org/abs/1107.0161)，仅检索命中，未读正文；不作同条件分类。
- [*Time optimal control of triple integrator with input saturation and full state constraints*](https://doi.org/10.1016/j.automatica.2020.109240)，仅检索命中，未读正文；不以题名或摘要代替条件核查。

不扩搜、不请求全文、不处理验证码或失败入口。一般可达集、状态约束和最优控制同义表述覆盖仍有限；一份教学近邻加已有经典方法足以提示结构不是新方法，**不足以解决具体双侧可行区间的发表优先权**。

## 交接状态

建议当前仅登记：方法/时段结构`经典`；同条件精确发表覆盖`unresolved`；候选数学正确性`待角色2 R014`；工程输入与连续速度界`未认证`。不认定“新定理”，也不认定“已读作者原文已逐式覆盖”。

实际保存时间以本文件修改时刻为准；本子任务23:42前结束，不延长根任务23:45:35限时或总研究窗口。
