# R005：并联漏电RC的最小焦耳热同条件来源审查

角色：创新性验证子任务。真实开始：2026-10-17 22:29:18 +08:00（Asia/Shanghai）；22:36前收束。本轮实际只执行**2条web search query**，其后只有命中来源的open/find/screenshot，没有第三条检索。旧R001–R004冻结；不读工程数组、不访问账户、不下载附件、不修改共享账本、不执行Git、不发跨聊消息；仅写本报告。

## 结果与强度

**这两条查询未取得可定位为全部同条件的RC最小焦耳热定理或精确Φ及等号构造的一手正文。** 不能写“RC方面不存在此结论”，也不能据此宣称线性或非线性Maxwell的发表优先权。

实际读到的一篇公开原文有相同的并联RC支路状态方程，但其优化对象是有温升/SOC约束的多阶段充电时间，且属于多状态电池模型；与本次固定T、固定支路终端电压、最小单个漏电电阻焦耳热不相同。此差别有正文定位，足以避免按“含并联RC”误记成same-claim；不足以排除该文未读位置或其它一般控制结果可经特例/等价改写覆盖目标。

## 精确比较对象

本轮只核α=1的形式映射：`Ccap=1/k`，`R=c`，电容电压`x`对应Maxwell力`F`，端口电流`I`对应总变形速度`v`，满足

`Ccap*x' = I − x/R`。

固定常数`Ccap,R,Imax,T>0`；`x(0)=0`、`x(T)=M`，`|I(t)|≤Imax`几乎处处；目标成本是`J=∫[0,T]x(t)^2/R dt`。允许先等待再取饱和电流。终端必须可达；目标不是无泄漏串联RC从固定电压源的常规充电，也不是仅约束SOC的电池优化。

候选线性Φ的来源对象沿用角色1冻结文件`../../ideation/maxwell-session004/R003-maxwell-energy-peak-bound.md`的α=1段及第5节，不改变它的证明状态。本轮派工要求的**固定终端x(T)=M**与更一般的**规定轨迹峰值M**须分别记录，不能只因候选晚期加载同时实现两者就把任意旧文的两种可行类混同。

**成本等价边界：** 同一并联RC端口、固定电容且始末电压固定时，端口净供能`∫xI dt`与`J`只差固定储能增量`Ccap*(x(T)^2−x(0)^2)/2`。因此不能把“最小供能”一概排除为不同成本。是否还含串联电源损耗、固定电源电压乘总电荷、输入平方项、热/化学能项或终端惩罚，须读正文逐项核对。本报告没有因标题中的energy或charging一词直接裁决等价。

## 两条实际查询

于2026-10-17 22:29前后一次批量执行：

1. `"leakage" "capacitor" "minimum energy" "charging"`
2. `"parallel RC" "optimal" "charging"`

没有追加同义词查询、作者查询或别学科查询。父角色另有两条预算，本子任务没有占用或重复其检索。

## 一手正文已读：Jarid–Das2021

Saad Jarid, Manohar Das, *An Electro-Thermal Model based fast optimal charging strategy for Li-ion batteries*, **AIMS Energy9(5):915–933**，2021，DOI [10.3934/energy.2021043](https://doi.org/10.3934/energy.2021043)。[出版社公开PDF](https://www.aimspress.com/aimspress-data/aimse/2021/5/PDF/energy-09-05-043.pdf)。共19 PDF页；本轮通过公开PDF文本定点核§3、§4正文。未下载本地；screenshot请求返回PDF引用，但当前工具输出未提供可供本角色确认的原页像素，故**不登记为已亲看图像**。

| 印刷页 / PDF页 / 定位 | 实际正文条件 | 对目标的比较 |
|---|---|---|
| p920 / PDF6，§3.1、Fig.2、式(1)–(3) | 电池模型包含SOC依赖OCV、串联R0及两个并联RC支路；SOC是额外状态，端电压由多个分量合成。 | 含目标的一阶RC构件，但整个系统不是单个固定参数漏电电容。支路电压不能直接当电池SOC或总端电压。 |
| p921 / PDF7，式(4)、(5) | 每支路满足`Vj' = −Vj/(Rj*Cj) + I/Cj`；正文同时说明等效电路参数随温度及SOC变化。 | 常参数单支路在方程层与α=1映射同形；不能据方程同形推定目标函数、端点条件、限流或精确最优解同形。 |
| p921 / PDF7，§3.2式(8) | 热源包括电池过电势相关项及熵热；配合核/壳热状态方程。 | 不是单独规定`∫Vj²/Rj`的目标；不能直接把热源、总热或焦耳热的不同对象合并。 |
| p923 / PDF9，§4.1 `Optimization problem1`，约束(11a)、(11b)；§4.1.1 `problem2` | 最小化充电总时间，以温升及目标SOC增量约束多段电流/持续时长；不是固定T的该成本最小化。 | 不满足目标的时间/成本/终端状态三项关键排重条件。 |
| p924 / PDF10，§4.1.2 `problem3`，约束(12a)、(12b)；§4.2 | 给定各段电流，优化各段终止时刻，并继续保留温升/SOC约束；采用逐变量搜索。 | 不等于任意可测`|I|≤Imax`中的精确全局Φ及等待后饱和构造。 |

关系标签：`related-not-equivalent`。本轮未在上述已读段落见目标精确Φ、全部同条件的全局最小值定理或其等号条件。这里的不同条件来自正文，不来自摘要；也不把此判断升级为“该文任何特例都不能覆盖目标”的证明。

## 仅线索 / 未得正文：不用于覆盖裁决

| 来源URL与身份 | 本轮访问等级及实际结果 | 允许结论 |
|---|---|---|
| [2017 Journal of Energy Storage题名记录](https://www.sciencedirect.com/science/article/pii/S2352152X16302419)，*Optimal charging for general equivalent electrical battery model, and battery life management*，DOI10.1016/j.est.2016.11.002 | 搜索返回元数据/摘要及少量section片段；直接open为403。未读其模型、成本、端点/控制约束的完整定义。 | 只作书目线索；不依据片段把其“general model”判为覆盖或排除目标，亦不追URL变体。 |
| [Rauh–Lahme–Benzinane2022](https://www.mdpi.com/2571-8797/4/4/78)，*A Comparison of the Use of Pontryagin’s Maximum Principle and Reinforcement Learning Techniques for the Optimal Charging of Lithium-Ion Batteries*，DOI10.3390/cleantechnol4040078 | 搜索返回书目/摘要；官网HTML open为429。另试标准出版社PDF地址`https://mdpi-res.com/d_attachment/cleantechnol/cleantechnol-04-00078/article_deploy/cleantechnol-04-00078.pdf`，工具返回not accessible，未取得正文；未重试。 | 不以摘要中的PMP或parallel RC判断同条件最优结果；本轮原文未得。 |
| [2018 RF energy harvesting论文的PMC入口](https://pmc.ncbi.nlm.nih.gov/articles/PMC6263956/)，*On the Impact of Mobility on Battery-Less RF Energy Harvesting System Performance* | 搜索返回泄漏/能量收支片段；open实际为reCAPTCHA检查页。未通过验证、未读取其正文。 | 只作未读线索，不按片段裁决泄漏最优控制问题。 |

搜索还返回文档、学位论文和其它电池/电路条目；未为它们增加query或展开引用链。本轮没有用它们替代目标一手正文，也没有将未展开条目计为已查无同结论。

## 交接

1. α=1与常参数单并联RC的模型映射可直接沿用；其来源排重仍不能只搜Maxwell名称。本文没有给该经典映射加原创性标签。
2. 精确Φ/等号及全条件覆盖仍未核得一手旧发表。本轮两条检索范围有限；R004/R005未发现不构成首次证明，保持发表优先权未定。
3. 即使未来找到本线性RC同条件原文，也只能先覆盖α=1。α≠1对应非欧姆支路，本报告不作一般α的自动覆盖或排除判断。
4. 正文已读的Jarid–Das2021可作为区分“同一RC动力学构件”与“同一最优控制命题”的明确记录；无需据它扩大一般电池充电研究。下一步由唯一主控按已有预算决定，本子任务到此收束。

保存时间以本文件最后修改时刻为准；本轮限时22:36，总研究截止仍为2026-10-18 07:09:45 +08:00。
