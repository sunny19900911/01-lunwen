> Canonical交接副本：2026-10-17T21:32:36+08:00。W5原文件保留；本副本仅调整相对链接并整合已核纠正，详见R001总包。论文全文与页图不进入本目录。

# R001：Maxwell 频变、储能与多输出原文核查

作者称呼：小香金猪。独立创新性审查子任务；冻结命题 M-C003 v1、M-C004 v1，兼查 M-C002 的周期能量等效边界。

真实开始：2026-10-17 21:20:13 Asia/Shanghai。原页核读完成：2026-10-17 21:26 左右；落盘时间见文末。约 9 分钟有范围任务。主控账本与原始工程资料均未修改；无 ETABS、账户访问或数据上传。

## 裁决建议

1. **以下是成熟结果，直接引用复用：** Maxwell 串联柔度引入频率相关的有效阻尼与储能刚度；装置力有幅值衰减和相移；装置在结构中的位置与模态投影影响各阶响应；不同输出须分别评价。重新推导这些关系不构成本项目创新。
2. **M-C004 作为普遍的精确替代命题过强。** 已核原文提供的频变算子、储能项和多输出实例足以说明单个能量标量并不自动保证其它输出相同。本轮未找到一篇原文逐字证明当前 M-C004 的全部量词；“不能自动保证”与“对任一具体模型都不能近似匹配”必须区别。特定窄频、近刚支撑和低耦合条件下仍可能近似有效。
3. **M-C003 的宽泛现象也不是创新。** 真实工程模型的同刻局部力预算、输出误差与适用域可以是工程证据候选；是否有新增结论，取决于具体、可复算的空间边界及对已有方法的增量。本轮不宣称首次。

## 原文清单与定位

### N-L01：Londoño、Wagg、Neild（2014），研究论文，正式开放版

*Supporting brace sizing in structures with added linear viscous fluid dampers: A filter design solution.* Earthquake Engineering & Structural Dynamics **43:1999–2013**，DOI [10.1002/eqe.2433](https://doi.org/10.1002/eqe.2433)。[机构库原 PDF](https://eprints.whiterose.ac.uk/id/eprint/81371/1/WRRO_81371.pdf)。机构库封面/元数据有“1993”笔误，以原文首页 1999–2013 为准。

本地 `evidence/Londono2014-WRRO_81371.pdf`，16 PDF 页（含机构库封面）；SHA256 `CF7E469E0897CB095FA45274D5FF98C0269D68EB2084D128BC4C6775817A0A1D`。全文文字可读；关键 PDF4、7、8、13、14 页已实际渲染并看图核式，不止摘要。

| 印刷页 / PDF页 | 原文位置 | 可复用结论及前提 | 对当前命题的关系 |
|---|---|---|---|
| p2001 / PDF4 | Fig.1，式(1b)、(2)、(5) | 线性黏滞元件 $c_d$ 与线性弹簧 $k_b$ 串联；$f_d+(c_d/k_b)\dot f_d=c_d\dot x$，$\rho=c_d/k_b$，$H(s)=\beta/(1+\rho s)$，其中 $\beta=c_d/m$。$H$ 是结构方程归一后的算子，不能把其量纲当作原始力/速度系数。 | 频变滤波为 same-claim；不必从头建立新理论。 |
| p2002 / PDF5 | §2.1，式(6)，Fig.2；文字已读，PDF5尚未本地像素复看 | 效率定义是**幅值比** $\mathcal E(\omega)=\lvert H(j\omega)\rvert/\beta$，不是耗能比例；同一一阶滤波器同时有增益与相位变化。 | 可解释频变/相位；不能把 $\mathcal E$ 直接称附加阻尼比。 |
| p2004 / PDF7 | 式(10)及位置矩阵例子 | $M\ddot x+C\dot x+Kx+\Lambda f_d=-Me\ddot x_g$，$f_d+\Gamma\dot f_d=\Pi\Lambda^T\dot x$。局部装置通过有符号位置矩阵进入结构平衡。 | M-C003 related-not-equivalent：已有空间装配理论；尚未给本项目截面预算。 |
| p2005 / PDF8 | 式(11)–(15) | 背景 $C$ 取经典阻尼；质量归一模态。装置算子 $H(s)=\operatorname{diag}[c_{di}/(1+\rho_i s)]$，经 $\Phi^T\Lambda H(s)\Lambda^T\Phi$ 进入模态方程，一般含交叉项。 | M-C004 的一般单标量替代没有依据；装置局部对角不等于模态中对角。 |
| p2010–2011 / PDF13–14 | Table III、Table IV、Table V，Fig.9–11 | 十层线性框架、两个指定地震输入；分别报告频率/模态阻尼、加速度、顶点位移、层间位移及装置力。Table V 的 Northridge、目标0.4 Hz 行为 $J_1=1.54$、$J_3=0.28$、$J_4=0.65$。 | 同一研究已有“位移改善而某加速度指标增大”的数值先例；不是截面力定理，也不是能量等效标量的同条件反证。 |

Table IV 中 $J_1$ 是跨楼层峰值归一的加速度指标，$J_3$ 是顶层位移指标；不能改写为“同一顶层的峰加速度增加54%”。原文算例的 $J_5$ 是装置力除以100 kN，不能读成有控/无控力比。

### N-L02：Conde、Bernabeu（2021），研究论文，正式开放版

*Influence of Maxwell Stiffness in Damage Control and Analysis of Structures with Added Viscous Dampers.* Applied Sciences **11, 3089**，DOI [10.3390/app11073089](https://doi.org/10.3390/app11073089)。[出版社 PDF](https://mdpi-res.com/d_attachment/applsci/applsci-11-03089/article_deploy/applsci-11-03089.pdf)。

本地 `evidence/Conde2021-applsci-11-03089.pdf`，36页；SHA256 `A7DD7754CB9840EEFADA8B698067A956A31CF392645979755CBFDDADD78CADEF`。PDF3–5 关键原页已渲染亲看；其余仅定向文字定位，不冒充全篇像素核查。

| 印刷页=PDF页 | 定位 | 前提、原文结论 | 重复范围 / 剩余问题 |
|---|---|---|---|
| p3 | §2.1，式(1)–(3)，Fig.1 | 非线性 dashpot 指数 $a$，串联线性刚度 $k_d$；式(2)：$\dot u=\dot f/k_d+(\lvert f\rvert/c)^{1/a}\operatorname{sgn}f$。线性时 $\lambda=c/k_d$。 | 本构及刚/柔极限均为既有；工程输入须先核指数，不能自动用线性滤波器。 |
| p4 | 式(4)–(6)，Fig.2 | 线性 Maxwell、稳态谐波；储能系数 $\beta_s=\omega^2\lambda^2/(1+\omega^2\lambda^2)$，耗散系数 $\beta_d=1/(1+\omega^2\lambda^2)$。不同频率的弹簧/黏滞贡献不同。 | M-C004 的频变机制已有；不能以基本机制作为创新。 |
| p4–5 | 式(7)–(10)，及 p5 式(11)上方 | 纯 dashpot 的谐波每周期耗能 $W_d=\pi bc\omega^a u_0^{1+a}$，能量等效 $c_{1,eq}=bc\omega^{a-1}u_0^{a-1}$；Jacobsen $\xi=W_d/(4\pi W_s)$，$W_s=k_su_0^2/2$。 | 每周期/指定幅频下的能量等效成熟；不是非平稳全记录的 $\zeta_0 E_{link}/E_{global}$ 原文依据。 |
| p5 | Fig.3及其上段，式(11)附近 | 线性与 $a=0.5$ 算例；同谐波输入、相应能量等效系数；柔度改变回线、峰位移时力及耗能。作者同时明确式(11)的 SDOF 前提。 | “能量等效不保持同一力—位移回线”已有直观先例；不能据此声称已经证明本项目多输出误差界。 |

**可直接复用、但归属需说清的表达：** 对 $a=1$，由上述原文式(3)–(6)作代数重写，$K^*(\omega)=i\omega c/(1+i\omega\lambda)$，储能刚度 $k'=k_d\beta_s$，损耗刚度 $k''=\omega c\beta_d$。这是本组符号统一后的成熟公式，不是原文逐字打印的同式号，也不是新增推导贡献。量纲 $k',k''$ 均为力/位移。

**功率—串联储能接口：** 用 N-L02 式(2)乘以 $f$，得到 $f\dot u=d[f^2/(2k_d)]/dt+c^{-1/a}\lvert f\rvert^{1+1/a}$；线性时末项为 $f^2/c$。这是本构与弹簧储能的直接恒等式，交独立验证者审查符号/单位；不冒称 N-L02 原文打印了该功率式，不列创新。有限记录的端部总功与 dashpot 耗散相差终初储能，只有起止储能相等时才可直接相等（回零只是充分特例；整合时更正这一必要条件措辞）。

### N-L03：Symans、Constantinou（1998），作者原文中的试验/模型复述

*Passive Fluid Viscous Damping Systems for Seismic Energy Dissipation.* ISET Journal of Earthquake Technology，Paper382，**35(4):185–206**。[公开原 PDF](https://home.iitk.ac.in/~vinaykg/Iset382.pdf)。本地 `evidence/SymansConstantinou1998-ISET382.pdf`，22页；SHA256 `FF590762497C6C3E2CDB314655119BC6BBE06809B949B952717C546F3E67EA88`。扫描 PDF，pdftotext 无正文；实际查看 PDF1、4–6 原页图。

- 印p188 / PDF4：作者说明其所述受试装置在不同频率下出现储能刚度；这是特定装置试验，不是所有液黏阻尼器的固定截止频率。
- 印p189 / PDF5：式(2)为 $P+\lambda\dot P=C_0\dot u$，式(3)指向 Makris–Constantinou1991 分数阶推广。
- 印p190 / PDF6：式(4)为所述低频条件下的 dashpot 简化；Fig.5比较频变阻尼系数与储能刚度。原文约4 Hz、6 ms仅属其受试装置，不可移植给本项目。

这篇是作者对其试验与模型研究的原文汇述，不把它替代成1991论文的原始推导。Makris、Constantinou（1991）*Fractional-derivative Maxwell model for viscous dampers*，J.Struct.Eng.117(9):2708–2724，DOI [10.1061/(ASCE)0733-9445(1991)117:9(2708)](https://doi.org/10.1061/%28ASCE%290733-9445%281991%29117%3A9%282708%29) 已由[作者机构记录](https://researchconnect.buffalo.edu/en/publications/fractional-derivative-maxwell-model-for-viscous-dampers/)核书目；本轮未取得该1991全文，不为它补造页式或“全输出等效”结论。

## 尚未核全文的高相关线索

- Zhang W.S.、Xu Y.L.（2000），*Vibration analysis of two buildings linked by Maxwell model-defined fluid dampers*，JSV233(5):775–796，[DOI10.1006/jsvi.1999.2735](https://doi.org/10.1006/jsvi.1999.2735)。出版社页面只有摘要/记录可用；双塔 Maxwell 连接本身已有直接主题先例，仍需原文核参数、输出及等效前提，不能仅凭摘要裁决本工程创新。
- Singh、Verma、Moreschi（2003），*Seismic Analysis and Design with Maxwell Dampers*，J.Eng.Mech.129(3):273–282，[DOI10.1061/(ASCE)0733-9399(2003)129:3(273)](https://doi.org/10.1061/%28ASCE%290733-9399%282003%29129%3A3%28273%29)。N-L01参考18与出版社记录一致，未取得全文；不转述其定理。
- Chen、Chai（2011），*Effects of brace stiffness on performance of structures with supplemental Maxwell model-based brace–damper systems*，EESD40(1):75–92，[DOI10.1002/eqe.1023](https://doi.org/10.1002/eqe.1023)。仅由 N-L01 参考19和出版社检索核书目，不能将二手概述写成已读原文结论。

## 只推荐两项后续检验

1. **先用已有本构做分频可替代性检查。** 核新装置 $a,c,k_d$，计算线性适用时的 $\omega c/k_d$ 及模态投影；若非线性则不伪造一个幅频无关 $\lambda$。把能量等效标量在同模型、同输入、同背景阻尼条件下对位移/加速度/层剪的误差分开报告。目标是本工程的可用域与误差，而不是再次发现“频率依赖”。旧0/3模型只有公平配对成立后才可进入替代误差比较。
2. **同刻有符号局部平衡加储能校正。** 对装置两端所在区段建立 $\Lambda f_d$ 的方向和截面边界，验证端部功、dashpot耗散和串联储能闭合，再定位净力峰值时刻的结构力/装置力分量。该核查不以独立峰相加、不以整段耗能代替局部传力。若得到稳定的预测条件或误差界才升格为贡献候选；单例“耗能大而某力不改善”仅是既有现象的工程复现。

## 可接续范围

CSI及 MCEER 周期能量公式由父角色独立审查，本文件不重复采集。没有启动新数值实验。下一次文献增量优先获取上述双塔2000/Maxwell2003原文，或仅对已形成的具体误差/局部预算命题做同条件排重；不返回既有一般阻尼输出非单调路线。

落盘：2026-10-17T21:29:16+08:00 Asia/Shanghai（真实工具时钟核对见同目录 `R001-maxwell-source-manifest.json`）。本轮完成，等待主控同一调度接续；研究总截止仍为2026-10-18 07:09:45 Asia/Shanghai。
