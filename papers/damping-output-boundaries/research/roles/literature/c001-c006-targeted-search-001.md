# C001/C006 定向查重 001

- 复查者：literature/history_methods；实际检索：2026-10-17 09:12–09:18 +08:00。
- 输入：主控本轮提供的C001公式及C006/V002审核状态；已读round-002.md与linfty-background-001.md，避免重复经典Young不等式、稳定反演与L015/L016零点分类。
- 范围：36条有限关键词查询，追踪5条候选L025–L029；仅以论文、作者大学和出版社来源支持技术比较。搜索结果中的ResearchGate、Scribd及其他镜像未用于核论文定理。未访问外部账户、未绕过限制。
- 写入：只有本文件。公开PDF在内存读取/渲染，没有落地全文或页图；不改索引或共享账本。

## 1. 先固定待比较的精确命题

**C001（任务提供，本文不重新审核推导）：**

\[
H_\zeta(s)=\sum_{j=1}^{2}\frac{r_j}{s^2+2\zeta\omega_j s+\omega_j^2},
\quad x=\zeta^2,\qquad
|H|^2=\frac{A+Bx}{C+Dx+Ex^2}.
\]

固定输入/输出的实留数、固定异频模态、两状态共同阻尼比分别为ζ0、ζ1。任务给出的有限状态放大条件为

\[
BC-AD-AE(x_0+x_1)-BE x_0x_1>0.
\]

必须区分：模态和的模平方展开、对ζ的局部导数、两个有限ζ端点的比较、以及给定记录峰值的变化。文中A、B、C、D、E是当前课题定义，不与引用论文同名字母直接等同。

**C006（主控称已获V002完整审核，本角色未替代证明审核）：**

固定κ=ζ1/ζ0，比较同一输入产生的完整响应峰值；候选
B(κ)=(4κ−3)(5−4/κ)²
对双模态族的ω、r、ζ0统一。三模态候选反例族可破坏任何只依赖κ的有限界。输入/初始条件、完整尾段、允许双边核等沿用已冻结证明；本轮不把它改成任意有限观察窗命题。

本轮最重要的量词是：

- 具体模型p的峰值增益K(p)有限；
- 对所有p的sup K(p)是否有限；
- 该sup是否可由仅含κ的B(κ)控制。

前一句即使已有文献，也不自动覆盖后两句。

## 2. 文献登记与原文定位

### L025：Papagiannopoulos与Beskos，2008，原作者会议全文

**G.A. Papagiannopoulos, D.E. Beskos. Seismic Inelastic Design of Steel Structures by Spectrum Analysis and Equivalent Damping. 14th World Conference on Earthquake Engineering, Beijing, 12–17 October 2008.**

[会议全文（IIT Kanpur/NICEE存档）](https://www.iitk.ac.in/nicee/wcee/article/14_05-05-0038.PDF)。全文8页，无印刷页码；本文不制造页码。SHA256：85b72983a5ea9ea2cffab1c261bcd043f801d16f9f423fef3b165b629ef0ea19。DOI未核实。

- 实际阅读：PDF第1–5页相关文字；完整页图核第3、4页。
- PDF第3页§2式(2.1)给屋顶绝对加速度/输入比R=1+Σzk；式(2.2)明确写模平方的自项与2Re(zk zj*)交叉项，式(2.3)定义复模态项。第4页讨论“monotonicity criteria”，对象是频率曲线各峰之间的平滑/增减分支。
- 比较：同属频域模态组合，但输出有直通项1，等效阻尼按模态迭代，并非共同ζ两端点。这里的monotonicity不是“随ζ增大响应单调”。
- 与C001为related-not-equivalent：证明模平方交叉项是既有工具，尚不能由所读段落裁定当前有限端点判据已被覆盖。未发现相同式形不构成创新结论。

补充检索路径：先遇到Muho、Kalapodis、Papagiannopoulos、Beskos的2024综述，再回溯本原作者来源；没有把综述当最早先例。综述的[正式公开全文](https://journal.hep.com.cn/rcs/EN/PDF/10.1016/j.rcns.2024.11.003)，Resilient Cities and Structures 3:107–125，19页，印刷108/PDF2式(1)也展开交叉项；本轮仅文字阅读此页，没有核原页，未另分配L-ID。公开PDF SHA256：50cd57cc4c2c61151507addd203ce7ddfbcc90ac9d0aea590a30dbe2790d7d55。

### L026：Sultan，2013，只有一手书目确认

**Cornel Sultan. Decoupling Approximation Design Using the Peak to Peak Gain. Mechanical Systems and Signal Processing 36(2):582–603, 2013.**

[作者Virginia Tech履历](https://www.aoe.vt.edu/content/aoe_vt_edu/en/people/faculty/sultan/personal-page/resume/_jcr_content/content/download/file.res/Short%20Resume_CornelSultan_2021.pdf)，PDF第4页，Journals第28项，确认题名、作者、卷期、页码和年份。

- 原论文全文：未从本轮允许的一手站点取得。出版社DOI解析失败；搜索引擎给出ResearchGate作者上传文本，但本轮没有据该文本核定理。
- DOI候选线索10.1016/j.ymssp.2012.10.007尚未由可读的一手原文独立确认。
- 状态：insufficient-text。题名直接涉及peak-to-peak与结构解耦，适合作为后续全文优先项；不能凭题名、CV或摘要判断它是否已有共同阻尼模型族的统一常数。

### L027：Tomljanović、Beattie、Gugercin，2017预印本

**Zoran Tomljanović, Christopher Beattie, Serkan Gugercin. Damping Optimization of Parameter Dependent Mechanical Systems by Rational Interpolation. arXiv:1707.01789v1, 6 July 2017.**

[作者大学仓储全文](https://vtechworks.lib.vt.edu/server/api/core/bitstreams/f2f89fa1-d571-46cc-b97f-3db584535cee/content)。25页；SHA256：7df1cbda2759b9ef7cfa5160771a3b0bb35e7dc0c0ca25ba2f82f900b40d661b。此处只登记已读v1，不冒充正式版DOI。

- 实际阅读：首页、页2–4引言；页3完整页图核。
- 页2式(2)以critical damping倍数表示内部阻尼；页3式(3)给外部阻尼参数化传递函数，式(6)/(7)定义H2目标。页3底部的“uniform bound”明确要求单位L2能量输入，右端是具体模型的H2范数。
- 与C006为related-not-equivalent：这是输入能量到输出峰值控制，既不是两个输出的峰值比，也不是对所有模型仅依赖κ的常数。“uniform”在该段不能单独搬成当前模型族统一性。
- 本轮未审其优化算法或全25页证明，不以该段认定C006重复。

### L028：Abedor、Nagpal、Poolla，1996，出版社摘要

**J. Abedor, K. Nagpal, K. Poolla. A Linear Matrix Inequality Approach to Peak-to-Peak Gain Minimization. International Journal of Robust and Nonlinear Control 6(9–10):899–927, 1996.**

[出版社一手页面](https://onlinelibrary.wiley.com/doi/abs/10.1002/%28SICI%291099-1239%28199611%296%3A9/10%3C899%3A%3AAID-RNC259%3E3.0.CO%3B2-G)，DOI：10.1002/(SICI)1099-1239(199611)6:9/10<899::AID-RNC259>3.0.CO;2-G。

- 实际读取：出版社Abstract及How to cite，HTML无页码。摘要称以可达集的inescapable ellipsoids建立star-norm上界，并进行控制器/滤波器设计。
- 全文未取得；没有给出虚构定理、式号或论文内页码。
- 状态：insufficient-text；仅支持“L∞诱导峰值增益的上界与最小化已有专门研究”这一背景。不能据摘要判断其是否推出C006结构约束下的B(κ)。

### L029：Schuler与Allgöwer，2009，会议全文

**Simone Schuler, Frank Allgöwer. ℓ∞-Gain Model Reduction for Discrete-Time Systems via LMIs. 2009 American Control Conference, pp.5701–5706.**

[会议全文（NTNU存档）](https://skoge.folk.ntnu.no/prost/proceedings/acc09/data/papers/0884.pdf)。6页；SHA256：ca5a6791099a1b7271bde582a2734c41c585f59cf03440ee5295c538d7469a22；DOI未核实。

- 实际读取：PDF第1–3页；印刷5702/PDF2完整页图核。
- 印刷5702的§III-A、Theorem1式(4a,b)、Remark1与式(5)，提供具体离散系统及误差系统的star-norm/LMI增益界。Remark1明确γ是上界。
- 与C006为related-not-equivalent：时间域是离散右侧序列；关注给定系统/降阶误差的矩阵相关界。没有从该段得到连续共同ζ两模态全族统一常数或三模态无界分类。
- 本轮未审核Theorem1全部等价表述；引用重点只取该页明确的上界定位，不能把星范数自动当精确诱导范数。

## 3. 对C001/C006的实质反馈

| 需要核查的内容 | 新材料实际覆盖 | 剩余缺口 |
|---|---|---|
| 多模态模平方、自项与带符号交叉项 | L025式(2.1)–(2.3)有直接原文 | C001固定实留数/共同ζ化为x的线性分子与二次分母后的有限端点诊断 |
| “monotonicity”一词 | L025第4页为随频率的曲线分支平滑 | 不能解释为随共同ζ或有限增量单调 |
| 峰值增益的模型相关上界 | L029完整页；L028只有摘要 | 可计算单模型γ不能代替对ω/r/ζ0全族的sup |
| “uniform time response bound” | L027页3明确为单位L2输入、模型H2范数 | 不是κ-only输出/输出L∞比 |
| 连续时间结构解耦误差的peak-to-peak原理 | L026只确认真实书目 | 仍需合法全文，不能提前裁定相同或不同 |
| 至少三模态才能破所有κ-only有限界 | 本轮无新原文直接给出相同量词的维数分类 | L015/L016按已有round-002保留；不重复下载，也不能把零点分类当该峰值分类 |

**贡献表述建议（解释，不是文献原句）：** C001的交叉相乘属于直接代数，模平方展开也已有明确先例；候选价值应放在针对指定输出/共同ζ族给出可检查的有限变化系数条件及其适用边界。C006则必须显式保留“只依赖κ、全族统一、完整响应”的量词。仅报告某一Q的核可积或LMI界不能完成该层贡献。

本轮没有找到精确等价结果，也没有建立“不存在等价结果”的结论。当前检索未穷尽，尤其L026/L028全文不足。不能据此写“首个”“首次”或“已有文献均未研究”。

## 4. 完整关键词记录与筛选失败

以下为实际36条查询；引号保留搜索约束。未对每条命中逐篇读全文，也不按搜索结果数衡量查重覆盖。

1. "damping" "two modes" "amplification" "antiresonance"
2. "damping" "peak response" "bound" "modal" uniform
3. "Effect of damping on the seismic response of long-period structures considering crossover phenomena" pdf
4. "damping" "L infinity" "two" "modes"
5. rational transfer function "L1 norm" "H infinity" degree bound
6. "peak-to-peak" gain "damping" bounds
7. "damping" "two-mode" "criterion" response amplification
8. "damping" "response" "monotonicity" transfer function theorem
9. "rational" "impulse response" "norm" "McMillan" bound
10. "L1 norm" "H-infinity norm" bounds transfer function
11. "Decoupling approximation design using the peak to peak gain" pdf
12. "damping" "uniform bound" "response" modes
13. "Decoupling" "peak to peak gain" site:vt.edu
14. "star norm" "peak" Boyd
15. "impulse response" "L1" "H∞" "bound" rational
16. "APPLICATIONS OF EQUIVALENT DAMPING IN SEISMIC DESIGN"
17. "Nagpal" "Abedor" "Poolla" "peak" gain
18. "rational functions" "L1-norm" "bounds"
19. "damping" "finite" "two modes" "transfer function" amplification
20. "star norm" "peak-to-peak" pdf
21. "10.1016/j.ymssp.2012.10.007"
22. "L1" "norm" "rational" "degree" "upper bound" control systems
23. "two modal" "damping" "amplification" criterion
24. "uniform" "peak" "damping ratio" "bound"
25. "damping" "modal cancellation" "bound"
26. "damping" "two-mode" "amplification" -quantum -Gaussian -optical
27. "damping ratio" "peak ratio" bound
28. "rational transfer" "L1" norm bound degree；限定ieeexplore.ieee.org、epubs.siam.org、arxiv.org、stanford.edu
29. "relative error" "peak-to-peak" model reduction
30. "multiplicative" "L1 norm" model reduction
31. "damping" "Wiener" norm
32. "damping" "response amplification" "analytical" "modal"
33. "finite damping" "amplification"
34. "common damping ratio" "amplification"
35. "uniform" "peak amplification" "damping"
36. "damping sensitivity" "receptance" amplification

失败/排除路径：

- “two-mode amplification/damping”大量命中量子光学，“peak ratio”大量命中阻尼识别；没有把这些系统当机械模态和的同一命题。
- “L1”与“multiplicative”命中NMF、回归或几何近似；均排除。
- 已有L011出版社摘要/引言本轮可读，但未得全文；保留旧insufficient-text，不重复编号、不据crossover摘要判断C001。
- L026 DOI解析及一次出版社PII访问返回工具Internal Error；未借账号或版权镜像补取。
- L025的2024后续综述，web重定向失败；按已知合法公开URL在内存取得全文，随后回溯原作者2008会议论文。
- L029一次web打开失败，但公开PDF经内存获取成功，关键页已核。上述“工具失败”不等于来源不存在。
- 未重新下载L015/L016，也未重新罗列Young工具作为本轮新证据。

## 5. 输入指纹、可重做方式与下一步

入口SHA256：

- round-002.md：022912B3538035A2D322B49C30814F906327E889E23E9C57E0B4C2BBBF2F4CD3。
- linfty-background-001.md：1BCF5DBC03CF6397AEA373E59430F99BD900D1A3F210E8C91137C4DDBF0A6EE8。

实际读取方法：从上列公开URL请求字节，SHA256冻结；pypdf从BytesIO提取；Poppler以stdin的PDF和stdout的PNG进行只读渲染。没有落盘原文，因此复做者需从公开URL重新获取并核哈希，不能假定本地缓存已共享。

最高价值下一步：优先补L026连续时间peak-to-peak结构误差原论文的合法全文，检查它的误差算子是否为输出比Q、常数依赖哪些模型参数、是否有模型族统一结论；再沿L028原文追踪范数上界。对C001，则应把当前系数条件与L025的有直通项频响分开，查有限参数灵敏度/端点不等式，而非继续堆积“阻尼有时有害”的例子。

本轮仅提供查重与条件比较；未改任何主张状态，未执行Git写操作或结构求解。
