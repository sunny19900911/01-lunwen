# Boyd式(5.33)：原页条件与符号核定

2026-10-17 12:40 +08:00；文献核定candidate，交主控/验证者。任务开始12:38:06，预算3分钟；**无新搜索、无新数学推广**。只读既有作者公开书稿及本地页图，旧原件不修改。

## 原页逐项结果

主来源：Stephen Boyd、Craig Barratt，*Linear Controller Design: Limits of Performance*，1991；[作者书稿入口](https://web.stanford.edu/~boyd/lcdbook/)。缓存`../local-cache/kernel-boyd-barratt-1991.pdf`，SHA256 **7287e1ee59e6155976bd1afc19e9be799f7b5be359e497b15ce121b3c054dd18**。印刷p118=PDF第127页，§5.5.1中部式(5.33)，已视觉核：

`||H||∞ ≤ ||H||pk_gn ≤ (2n+1)||H||hankel ≤ (2n+1)||H||∞`。

| 所问字段 | 原页可确认的精确范围 |
|---|---|
| 常数 | **2n+1**；不是2n、n+1或此常数的平方。整链含Hankel中间项，不应只转述末端而掩盖适用疑点。 |
| SISO/MIMO | p118 §5.5.1首句明确本节为SISO系统/传递函数。未在此页陈述MIMO同常数推广。 |
| n | 式前仅写“if H has n poles”。明确指H的极点，不是任意给定非最小实现的状态数；本页没有明示是否按代数重数计、共轭对计一个还是两个，也未写McMillan degree。常规约定不能冒充本页逐字定义，交验证者另核。 |
| peak定义 | p97=PDF106，式(5.4)是`sup ||Hw||∞/||w||∞`；式(5.5)等于`∫₀∞|h(t)|dt`；式(5.6)用有限时长实sign输入论证。是时域L∞输入→输出增益。 |
| H∞定义 | p99=PDF108，式(5.9)为L2诱导增益；稳定时式(5.10)为`supω|H(jω)|`；式(5.11)将`supRe(s)>0|H(s)|`定义为系统H∞范数。不稳定系统的该增益记∞，不能只看其虚轴幅值便称有限H∞。 |
| 稳定/因果 | 已读定义采用正时间响应及0到∞核积分，属于书中连续时间因果LTI框架，有限范数对应稳定。没有把式(5.33)写成一般双边稳定/反因果有理商定理。 |
| strictly proper与D | **p118式前后没有明确写strictly proper或列D条件。** p97核公式写普通函数h的绝对积分、没有Dirac项；p103=PDF112的Hankel定义为输入停止后的输出能量。p119—120的§5.6计算部分另外明确用`H=C(sI−A)⁻¹B`无D，并把含D的H∞计算指向参考文献；该后节假设不能自动倒推为p118的完整假设声明。仅凭这些页，不能认证整条(5.33)原样覆盖biproper含D商。含D怎样拆分/改界留给验证者，不在本次补写。 |
| 实/复标量 | 本段SISO明确，但没有逐字声明任意复系数标量系统也适用；p103能量写z(t)²、w(t)²，p97用实sign信号。可核的是实信号控制系统语境，复扩张未在本次原页得到明文保证。 |

## 文献线索与视觉定位

- p118=PDF127中部：完整不等式、SISO及n poles句，旧页图`kernel-boyd-p118.png`本次重看。
- p97=PDF106：§5.2.5及式(5.4)—(5.6)，旧页图`kernel-boyd-p97.png`本次重看。
- p99=PDF108、p103=PDF112、p120=PDF129：本次新渲染并视觉核，分别为旧local-cache内`Boyd-conditions-p99.png`、`Boyd-conditions-p103.png`、`Boyd-conditions-p120.png`；不修改原PDF。
- p124=PDF133的Notes and References下Comparing Gains将式(5.33)归于[BD87]；书末印刷p392=PDF401给S. Boyd、J. Doyle，*Comparison of peak and RMS gains for discrete-time systems*，Systems & Control Letters 9:1—6，June 1987。这里只核书中参考记录，未取1987原论文，不能把其题名的离散时间条件与本书连续时间公式直接等同。

## 给验证者的边界

可以核验如何使用本书的定阶比较，但**本次不能把n的重数约定、D处理、复系数推广或双边版本标为已由p118原文完整解决**。尤其C020的Q含κ直通项且一侧失谐需要反因果核，这些应在短证明中逐项处理。该限制不表示经典工具不能覆盖，也不支持新颖性判断。

保留此前对照：Teixeira的L2e输出比及离散ℓ2停止输入指标，与本题实紧支撑输入/完整尾段L∞分别有独立定义，不用同名gain掩盖差别。
