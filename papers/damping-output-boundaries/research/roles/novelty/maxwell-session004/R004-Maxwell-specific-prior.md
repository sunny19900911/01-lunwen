# R004：Maxwell器件耗散—峰力候选的定点同条件查重

角色：创新性验证子任务。真实开始：2026-10-17 22:07:35 +08:00（Asia/Shanghai）；本轮不超过6分钟，22:13前收束。仅写本报告；不改R001/R002/R003，不读工程数据、不跑ETABS、不访问账户、不发送跨聊消息。

## 有范围结论

**在本轮明确检查的两篇既有Maxwell论文和四条新增定点检索中，未发现可由已读全文定位为候选精确Φ(M)、末段最大速度加载取等、或无统一V时固定真实耗散峰力无界的同条件旧发表。** 这只是有限范围未发现，不能写“首次”“文献没有”或“已建立创新性”。通用比较/最优控制/积分验证方法与本构均为经典，本角色不审证明，也不替代角色2独审或主控裁决。

搜索命中的一篇可公开读取全文的bang-bang Maxwell研究，优化的是**可变阻尼系数C(t)**，目标是增加吸能；与本候选固定k/c/α、在有界总变形速度输入中最小化达到给定峰力所需耗散的决策变量、目标和约束不同。它不能直接排重为same-claim，也不能因为不同而证明候选首次。

## 冻结候选与排重键

只读输入：`../../ideation/maxwell-session004/R003-maxwell-energy-peak-bound.md`。

实际核对SHA256：`0509CE63722190AD5B726088CEB1B1060B3824508B82F41FE96778981AE6FE3F`，与派工指纹一致；不静默采用未来修改版。

本轮只比以下三个精确对象：

1. 单个固定参数k,c,α>0的非线性Maxwell元件，零初力，固定有限窗，**总变形**速度满足统一的本质上界V；D是真实dashpot耗散，不是端部总功；给定可达峰力M时的精确最小耗散Φ(M)，积分分母含`V−(f/c)^(1/α)`。
2. 同条件下先等待、末段取总速度v=±V，恰在窗末达峰，从而取等；本候选没有为该取等结论额外要求末力为零。
3. 去掉跨输入序列统一的速度上界，固定同一k,c,α,T和D0>0，初末力均零，每条输入各自有有限速度但其统一界不存在，峰力可无界。此为器件本构输入类命题，不是地震楼体反例。

没有将一般频率依赖、一般输出非单调、阻尼能量比或Hu论文纳入本轮搜索。

## 既有原文定点复查

原PDF仍只读保留在W5首轮`research/maxwell-20261017/roles/novelty/evidence/`，本轮未重下载；来源链接、指纹及R001视觉核查状态如下。

| 原文与版本 | 本轮核对的原文定位 / 实际可读程度 | 与候选的关系 |
|---|---|---|
| Conde J., Bernabeu A. (2021), *Influence of Maxwell Stiffness in Damage Control and Analysis of Structures with Added Viscous Dampers*, Applied Sciences11:3089，[正式PDF](https://mdpi-res.com/d_attachment/applsci/applsci-11-03089/article_deploy/applsci-11-03089.pdf)，SHA256 `A7DD7754CB9840EEFADA8B698067A956A31CF392645979755CBFDDADD78CADEF` | 印刷/PDF p3 §2.1式(1)–(3)：非线性dashpot及串联Maxwell本构；p4式(4)–(10)、p5 Fig.3：指定幅频谐波、周期耗能及等效；这些页已在R001实际看图，本轮重读文字。另定点读p24 §4.11、Fig.15前文的minimum/bounds语境，p24本轮仅文字层、未像素复查。 | 本构相同，但p4–5采用指定谐波；p24讨论结构/装置刚度比与若干数值响应的关系。已读位置没有给任意有界总速度输入、零初力、有限窗的Φ最小耗散或末段加载取等。此为`related-not-equivalent`，不是全文不存在相关命题的全称断言。 |
| Londoño J.M., Wagg D.J., Neild S.A. (2014), *Supporting brace sizing in structures with added linear viscous fluid dampers: A filter design solution*, EESD43:1999–2013，[机构正式版PDF](https://eprints.whiterose.ac.uk/id/eprint/81371/1/WRRO_81371.pdf)，SHA256 `CF7E469E0897CB095FA45274D5FF98C0269D68EB2084D128BC4C6775817A0A1D` | p2001/PDF4式(1b)–(5)：线性串联本构/一阶滤波；p2002–2003/PDF5–6式(6)–(9)：幅值效率及支撑刚度；p2004–2005/PDF7–8式(10)–(15)：MDOF装配；p2012/PDF15 §5：方法目标与适用模型。本轮重读上述文字；PDF4/7/8沿用R001原页核图，PDF5/6/15本轮未新增像素核查。 | 以结构频率带内效率确定支撑刚度，参数而非任意时间输入路径是其设计对象。没有在已读位置给D受限时最大可达峰、精确Φ或固定D/无统一V反例。`related-not-equivalent`。线性本构及普通一阶动态响应已有，不能因本轮未找到打印成同一界的文献，就把线性可达峰公式本身列新。 |

两份全文同时做了有范围词定位：`bang`、`optimal control`、`dissipation`、`finite`、`bound`、`velocity`、`maximum/maximal/minimum`。搜索词命中只是定位手段；没有用“未命中某个词”证明命题不存在。

## 新增搜索：恰四条

2026-10-17 22:08前后执行以下公开网页检索，未再增加查询：

1. `"Maxwell" "minimum dissipation" "strain rate"`
2. `"Maxwell" "bounded velocity" "force" "energy"`
3. `"Maxwell" "bang-bang" "dissipation"`
4. `"nonlinear Maxwell" "peak force" "bound"`

检索存在电磁Maxwell、分子流体和会议程序等同名噪声，未作为本构命题证据，也未为追噪声扩展搜索。本轮只展开最直接的器件bang-bang命中，见下。

## 新原文：Kurino等2004的bang-bang对象不同

Kurino H., Matsunaga Y., Yamada T., Tagami J. (2004), *High Performance Passive Hydraulic Damper with Semi-Active Characteristics*, 13th World Conference on Earthquake Engineering, Paper33, Vancouver, 1–6 August2004。[会议公开PDF](https://www.iitk.ac.in/nicee/wcee/article/13_33.pdf)。公开PDF共12页；本轮读取全文入口并定点核其PDF2–3的可读文字层。原文印刷页码未确认，下面只报PDF页序；对PDF2–3的截图请求均超时，未新增图像证据或保存本地PDF。

| 位置 | 原文实际条件与目标 | 不同于候选的关键点 |
|---|---|---|
| PDF2，`Control Strategy for Efficient Energy Dissipation` / `Maxwell-type Mechanical Model`，Fig.1 | 串联弹簧刚度取常数；阻尼系数C(t)可在小值与大值间改变且保持正值。 | 候选c固定，控制变量是总变形速度v；这里切换的是器件内部阻尼系数。 |
| PDF2，`Energy Dissipation Capacity of Passive Linear Damper`，式(1) | 对给定谐波运动讨论选择常数阻尼系数后的最大每周期吸能。 | 不是固定c、任意有界速度输入、给定峰M的有限窗最小D；不能把“maximum energy”与本Φ最小值对调。 |
| PDF3，`Switching Control Law for Semi-active Damping Device`，式(2)、Fig.2 | on/off或bang-bang切换C(t)，以力和运动方向等信息调节吸能过程。 | 两项工作都有切换动作，但变量和目标不同；不能按“bang-bang”一词认作同一优化定理。未逐符号复述式(2)，以免超出文字层/未核图范围。 |
| PDF3，`Energy Dissipation Capacity of Semi-active Damping Device`，式(3)、Fig.3 | 理想化谐波回线及每周期吸能比较。 | 没有在所核段落给候选的零初力/有限窗/总速度统一界/精确Φ以及无V固定D峰无界的同条件陈述。 |

此处只据原文所核条件判`related-not-equivalent`，不评价该论文控制律在它全部配置下的数学最优性，也不把它的semi-active元件当成候选的常参数被动元件。

另有两个公开PDF检索命中未展开核读：[IPPT报告m764](https://www.ippt.pan.pl/repository/open/m764.pdf)、[Hansen2024的single-element Maxwell流体研究](https://glass.ruc.dk/pdf/articles/2024_PRE_110_L023101.pdf)。前者检索片段指向切换阻尼机构，后者为流体波矢相关扩展；**这些只是未读线索，不能用片段排除或认定与Φ同条件。** 本轮没有把博士论文/一般流体材料工作替代成已核的器件命题原文。

## 交接建议与不能声称的内容

- 已核的器件论文没有直接给出候选精确优化式；候选仍可交角色2数学审核，再由主控决定是否投入更窄的来源追溯。
- 同条件发表优先权依然未定；尤其一般标量最优控制、可达集、带速率约束的最小耗散等价表述，本轮未覆盖。通用方法框架由父角色另审，本文件不重复搜寻或冒充已经排除。
- 不把线性Maxwell本构、普通一阶阶跃响应、功—储能恒等式、比较法或bang-bang字样本身列为新增理论。
- 不据本轮检索判断候选成立，更不将器件输入类结论迁移为楼层力或地震响应保证。

本轮只贡献有限的Maxwell-specific来源比较；候选全文指纹和R001/R002/R003均保持冻结。保存时间由本文件最后修改时刻给出；截止仍为本轮22:13及总研究2026-10-18 07:09:45 +08:00。
