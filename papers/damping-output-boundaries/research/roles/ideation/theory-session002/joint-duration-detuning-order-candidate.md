# 时长—失谐联合双侧阶：三项已接纳结果的组合候选

2026-10-17，Asia/Shanghai；12:58:47开始读取，本项≤5分钟。仅组合主控已接纳C023、C025和C020，不作新求根、扫参、时程、实验或检索，不派子任务。**本联合命题仍为candidate，交主控安排不同作者审核；不自行改claims或正文。** 三源及独审字节绑定见末表，旧candidate字样按冻结时点保留。

## 1. 同一固定模型、输入类及参数域

先固定任一正m/k完整三自由度剪切链、真实顶层弹性剪力输出、共同基底标量输入、零初始和一个κ>1。模型、输入分布与输出在全命题内不变；两状态各阶共同阻尼为ζ₀=rζ*、ζ₁=κrζ*。

令

\[
\eta_\kappa=\min\{1/2,(\kappa-1)/(2\kappa)\},\quad
I_\kappa=[1-\eta_\kappa,1+\eta_\kappa],\quad
\delta=|r-1|,\quad r\in I_\kappa.
\tag{J1}
\]

闭域包含r=1，且Iκ⊂[1/2,3/2]；κr=1不在该域。对T>0，定义

\[
\mathcal F_{1,T}=\{0\ne f\in L^1(\mathbb R;\mathbb R):
\operatorname{supp}f\subset[0,2T]\},\qquad
\mathcal F_{C^1,T}=\mathcal F_{1,T}\cap C_c^1(\mathbb R;\mathbb R).
\tag{J2}
\]

支撑按L1意义理解；C1子类为全轴函数，端点零延拓亦为C1。无额外幅值、Lipschitz或导数上限。对两类分别定义

\[
K_{C^1,T}(r)=\sup_{f\in\mathcal F_{C^1,T}}\frac{P_1(f)}{P_0(f)},
\qquad K_{1,T}(r)=\sup_{f\in\mathcal F_{1,T}}\frac{P_1(f)}{P_0(f)},
\tag{J3}
\]

其中Pj取同一个输入下的完整输出峰，包含输入前后的全部自由尾段。非零有理H₀对非零紧支撑标量L1输入的注入性保证P₀>0；稳定严格真核使输出连续、有界。每次取上确界，模型、r和κ均已固定。类包含立即给K_C¹,T≤K₁,T，不宣称它们相等。

## 2. 统一时长尺度及下界

采用已接纳C023原常数A,B,E>0：在Iκ内|H₀(iS)|≤Aδ、|H₁(iS)|≥B，两态一阶矩误差统一为E/T。令

\[
T_0=\frac{2E}B>0,\quad T_{\rm env}=\frac EA>0,\quad
\tau=\frac T{T_{\rm env}},\quad
\tau_0=\frac{T_0}{T_{\rm env}}=\frac{2A}B>0,\quad
C_{\rm env}=\frac B{2A}>0.
\tag{J4}
\]

T、T₀、Tenv有时间单位，τ、τ₀、δ及Cenv无量纲。特别τ₀Cenv=1；Tenv及T₀依赖该固定模型与κ，不能当所有模型通用的秒数。

对全部r∈Iκ和全部T≥T₀，C023给同一实sin²包络fT,r，支撑[0,2T]、全轴C1且非零，因此属于这里相同支撑的F_C¹,T。两阻尼状态使用同一个f；不同r/T允许换相位。于是

\[
K_{C^1,T}(r)\ge\frac{C_{\rm env}}{\delta+1/\tau}
\ge c_-\min\{\tau,\delta^{-1}\},\qquad
c_-:=\frac{C_{\rm env}}2>0.
\tag{J5}
\]

δ>0时为普通不等式；δ=0时直接用C023原式K_C¹,T≥Cenvτ，再以min{τ,∞}=τ解释较弱的(J5)。不是把C020的除δ公式用于临界点。

## 3. 同一时长变量的上界

C025的有量纲D4式对更大的r域[1/2,3/2]及全部非零实L1输入成立，因此也覆盖(J1)—(J3)。记其固定模型常数Mv、Ctail和Aκ=(3−2/κ)³，则

\[
K_{1,T}(r)\le A_\kappa[\kappa+M_v(2T+C_{\rm tail})]
=\alpha+\beta\tau,
\tag{J6}
\]

\[
\alpha=A_\kappa(\kappa+M_vC_{\rm tail})>0,\qquad
\beta=2A_\kappa M_vT_{\rm env}\ge0.
\]

Mv具有时间倒数单位，Ctail与Tenv为时间，所以α、β均无量纲，且不依赖r、T或输入。因τ≥τ₀>0，

\[
K_{1,T}(r)\le D_+\tau,\qquad
D_+:=\beta+\frac\alpha{\tau_0}>0.
\tag{J7}
\]

这一步必须保留正时长门槛，不能令T任意趋0后仍省掉α。

对δ>0，Iκ又恰在C020的局部域内；原实L1类的已审上界及类包含给K₁,T≤Uκ/δ，常数

\[
U_\kappa=(3-2/\kappa)^3
\left[\frac{\kappa+C_{0,\kappa}}2+C_{1,\kappa}\right],\quad
C_{0,\kappa}=\frac{36}7(\kappa-1)(1+3\kappa/2),\quad
C_{1,\kappa}=\frac{236}{35}(\kappa-1)(1+9\kappa/4).
\tag{J8}
\]

因此δ>0时

\[
K_{1,T}(r)\le\min\{D_+\tau,U_\kappa/\delta\}
\le c_+\min\{\tau,\delta^{-1}\},\qquad
c_+:=\max\{D_+,U_\kappa\}>0.
\tag{J9}
\]

δ=0时只由(J7)得到K₁,T≤D+τ≤c+τ，故以扩展实数min约定写(J9)仍成立，而无需定义临界Uκ/0的有限值。

## 4. 联合命题、量词和边界

综上候选组合为

\[
\boxed{
c_-\min\{\tau,\delta^{-1}\}
\le K_{C^1,T}(r)\le K_{1,T}(r)
\le c_+\min\{\tau,\delta^{-1}\},
\quad r\in I_\kappa,\quad T\ge T_0.}
\tag{J10}
\]

δ0时min项定义为τ。两个正有限常数c±、正时间T₀/Tenv先由固定模型与κ决定，再对整个r/T域同时成立。因此两输入类的最优峰比具有相同的模型相关联合阶；允许r随T变化而留在Iκ，不需先固定失谐再令时长趋大。这里的“同阶”是双侧常数夹逼，不是渐近等价系数，也不是两K相同。

- 下界来自每个r/T的一条设计输入，是上确界的下界；没有宣称所有允许输入都达到它。上界才覆盖该支持长度内全部实L1输入，无额外Lip限制。
- 输入支撑固定为[0,2T]，输出峰仍取完整尾段；不能把Pj换成只在[0,2T]内寻峰。
- 域取三源共同有效部分：Iκ用C023的正新态幅值域，包含于C025的[1/2,3/2]；C020仅在δ>0时调用。若扩大到新态零点κr=1或删去T≥T₀，当前组合不成立为所列同一证书。
- c+含C025的机械频谱/可观测Gramian及C023的时长尺度，c−也依赖固定模型；没有κ-only通用时长界、认证物理秒数、最优系数或工程优化。C020上界系数虽仅依赖κ，也不会抹去另两项的模型依赖。
- min型联合阶不把Tenv/δ或T₀认证为某一要求增幅的必要最短时长。本文件不做时长优化、参数认证或天然记录预测。
- 三个已接纳证明的核心接口不在本轮重推；C025临界身份及全部自由尾上界不依赖本角色的下界。组合没有发现输入类、参数域或量纲漏洞，仍待不同作者检查后由主控裁决。

人话说明：对于一个已经固定的模型，最坏放大同时受到“输入能持续多久”和“离精确抵消有多远”两种尺度限制。在所列时长门槛以上，最坏峰比被常数夹在这两个尺度较小者附近。它讨论的是可选择波形的最坏情况，不保证每条地震波，也不把上下界系数称为实际放大倍数。

## 5. 三源及独审字节绑定

下列实际SHA256在本轮只读核对；原文件保持不变。C020桥接另列，确保上界确实属于原紧支撑实L1输入类。

| 已接纳来源或审核 | SHA256 |
|---|---|
| [C020原命题](../../verification/theory-round001/explicit-detuning-bound-candidate.md) | eae981f394ed06dc1bc085dea34fd8bf4343a570128ae38efe483ac03b3b0d79 |
| [C020不同作者独审](../../verification/theory-session002/explicit-detuning-bound-review.md) | 3ee1f68b91e22448f3e127a86207de52d7e3aba2eca5926377f3ccf10dace838 |
| [C020原L1类桥接](../../verification/theory-session002/C020-input-class-addendum.md) | 462eca175cbc2de92c7cb82f946464c256c511edb8bb78d4050dbf7b4b851a55 |
| [C023原命题](finite-envelope-detuning-candidate.md) | ea99a02b167720490242edc396adc6da154dd617a55dfc8df26c28c2daf3b3db |
| [C023不同作者独审](../../verification/theory-round001/finite-envelope-detuning-review.md) | 216b63ac6a84d37fceb770cd1c42a77824b6e3618395fbbc0cfc05d53010977c |
| [C025原命题](../../verification/theory-session002/fixed-duration-upper-feasibility.md) | d0b90a16a80a74d6db6d105e68df48bcbd75fe37489b9ab7d643275cdd44d8ac |
| [C025不同作者独审](fixed-duration-upper-independent-review.md) | b13c0254d92429f789be2c788d5f0513d5a4b6d642f7d9fb1ad703343ca46030 |

本轮仅解析组合和文档QA，没有新增实验、计算脚本或搜索。完成后冻结此候选，向主控回报并等待不同作者审核；不自行改共享状态或正文。
