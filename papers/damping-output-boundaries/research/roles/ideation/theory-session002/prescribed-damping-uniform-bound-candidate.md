# 预先给定基准阻尼：跨正三层模型统一完整峰界的阈值候选

2026-10-17，Asia/Shanghai；13:10:07开始读取，预算≤8分钟。纯解析，无实验、搜索、谱/根/网格/时程或子任务，不扩作者当前v005，不改共享账本。**本新三分法及正向显式界均为candidate，待不同作者独审。**

依赖明确：0<ζ₀<U的否定使用C028完整值域；ζ₀=U的否定使用其上端逼近序列；正向只需既有AM–GM严格上界及已审C024范数工具。按派工先把C028列为条件，本轮13:11只读账本已记录主控接纳C028，但不据此自行升级本新命题。

## 1. 对象与精确三分法候选

固定预先给定的z=ζ₀>0和κ>1，令ζ₁=κz。跨全部有限正m/k标准三层链、共同基底输入及真实顶层弹性剪力模型p∈P，定义

\[
\mathcal K_p(z,\kappa)=\sup_{0\ne f\in L^1(\mathbb R;\mathbb R),\ \operatorname{supp}f\ \text{紧}}
\frac{P_1(f)}{P_0(f)},\qquad
\mathcal B(z,\kappa)=\sup_{p\in\mathcal P}\mathcal K_p(z,\kappa).
\tag{P1}
\]

每次比较均固定同一模型、输入分布、真实输出，两个状态零初始；峰Pj包含全部自由尾段，不限制最大输入时长，基准非恒零保证非零输入P₀>0。统一界允许依赖预定(z,κ)，不允许依赖模型/谱或输入。

令U=√(2/27)。新候选为

\[
\boxed{\quad\mathcal B(z,\kappa)<\infty
\quad\Longleftrightarrow\quad z>U,\qquad \kappa>1.\quad}
\tag{P2}
\]

- 0<z<U：由C028可选ζ*(p)=z的一个固定模型，其输入族已令Kp=∞。
- z=U：每个模型均非临界、各自Kp有限，但跨模型B=∞。
- z>U：下文给显式模型无关上界39M(z,κ)。

κ=1另为两状态相同、B=1，不属于(P2)的阈值命题。此“阈值”只属于所列数学类和完整峰值保证，不是工程阻尼建议或安全阈值。

## 2. z>U：轴上分子比的三段显式控制

对任一模型令a=2ζ*>0、b=a²∈(0,8/27)、S=Σωᵢ。以x=Ω/S≥0归一频率，并将已审分子Nζ/cp乘b，其中cp>0为真实topcut物理系数，得

\[
d_0=b-4z^2x^2+i2zx(1-x^2),\qquad
d_1=\kappa d_0-(\kappa-1)(b+4\kappa z^2x^2).
\tag{P3}
\]

所以分子比V=Nκz/Nz=d₁/d₀满足

\[
|V|\le\kappa+(\kappa-1)R(x,u),\qquad
R=\frac{b+4\kappa z^2x^2}{|d_0|},\quad
u=\frac b{4z^2},\quad c=\frac{U^2}{z^2}<1,\quad0<u<c.
\tag{P4}
\]

以下不令b远离0；这正是跨模型统一必须处理的边界。

### 2.1 0≤x≤1/2

若x²≤u/2，由实部|d₀|≥4z²(u−x²)≥2z²u，得到

\[
R\le2+\kappa.
\]

若x²>u/2，则u<2x²且x>0。虚部给|d₀|≥2zx(1−x²)≥(3/2)zx，因此

\[
R\le\frac{4z^2(2+\kappa)x^2}{(3/2)zx}
\le\frac43z(2+\kappa).
\tag{P5}
\]

x=0总属于前一情形，d₀=b>0，未除以0。故本段可用

\[
C_{\rm lo}=(2+\kappa)\max\{1,4z/3\}.
\]

### 2.2 1/2≤x≤2

写y=x²∈[1/4,4]。由y≥1/4及加权平方和最小值，

\[
|d_0|^2=16z^4(u-y)^2+4z^2y(1-y)^2
\ge16z^4(u-y)^2+z^2(1-y)^2
\ge\frac{16z^4}{1+16z^2}(1-u)^2.
\tag{P6}
\]

最后一步可由加权Cauchy直接核对；它对全部实y成立。因u≤c<1且u+κy≤c+4κ，得到

\[
R\le C_{\rm mid}:=
\frac{(c+4\kappa)\sqrt{1+16z^2}}{1-c}<\infty.
\tag{P7}
\]

### 2.3 x≥2

y=x²≥4，实部控制|d₀|≥4z²(y−u)，所以

\[
R\le\frac{u+\kappa y}{y-u}
\le\frac{c+\kappa y}{y-c}
=\kappa+\frac{(\kappa+1)c}{y-c}
\le C_{\rm hi}:=\frac{c+4\kappa}{4-c}.
\tag{P8}
\]

定义仅依赖(z,κ)的显式常数

\[
C_*(z,\kappa)=\max\{C_{\rm lo},C_{\rm mid},C_{\rm hi}\},\qquad
M(z,\kappa)=\kappa+(\kappa-1)C_*(z,\kappa).
\tag{P9}
\]

三段覆盖全部x≥0，实系数共轭性又覆盖Ω<0。每个机械分母比的频轴模为

\[
\frac{\sqrt{A_i^2+B_i^2}}{\sqrt{A_i^2+\kappa^2B_i^2}}\le1,
\quad A_i=\omega_i^2-\Omega^2,\quad B_i=2z\omega_i\Omega.
\]

因此完整商Q=Hκz/Hz满足

\[
M_{\rm ax}(Q):=\sup_{\Omega\in\mathbb R}|Q(i\Omega)|
\le M(z,\kappa),
\tag{P10}
\]

没有残留S、频率间距、物理留数或模型阻尼裕度。仅看轴上界本身仍不够证明峰界，下一步单独处理。

## 3. 稳定商、零直通比较及原L1输入桥接

z>U>ζ*(p)对所有模型成立。由已审Routh分类，基准三次分子全部根在严格左半平面；新状态机械分母亦稳定。因此约分后的Q是稳定、实、因果biproper有理函数，Q(∞)=κ，实际有限极点总数按代数重数至多3+6=9。不需全通反射或反因果项。

置G=Q−κ，则G严格真、稳定、实、因果，有限极点不超过9。只对这个G使用已审C024中的Boyd5.33端点步骤，得到普通冲激核g的

\[
\|g\|_1\le19\|G\|_{H^\infty}.
\]

有限重根按C024已经独立核过的逐固定系统稳定微扰/L1连续性处理；该19系数不要求所有模型有统一极点实部裕度。没有把原书未明示的含直通、复系数或双边版本直接套到Q。

此处Q稳定，故其标准H∞范数确为M_ax(Q)。又Q(∞)=κ给κ≤M_ax(Q)，所以因果有限测度q=κδ₀+gdt满足

\[
\begin{aligned}
\|q\|_{\rm TV}
&=\kappa+\|g\|_1\\
&\le\kappa+19(\|Q\|_{H^\infty}+\kappa)\\
&\le39M_{\rm ax}(Q)\le39M(z,\kappa).
\end{aligned}
\tag{P11}
\]

G恒零时取g=0即可，亦不破坏该保守界。39由补回κ直通项而来；本题没有反射因子的额外9倍。

对每个原实紧支撑L1输入，两稳定严格真物理核h₀/h₁属于L1∩C₀；Fourier唯一性给q*h₀=h₁，结合有限测度/L1卷积结合律，得到实际输出y₁=q*y₀及

\[
\boxed{P_1(f)\le39M(z,\kappa)P_0(f),
\qquad \mathcal B(z,\kappa)\le39M(z,\kappa)<\infty.}
\tag{P12}
\]

原L1输入不必有界；h₀∈C₀与f∈L1保证y₀有界，h₀*f亦属L1，因此桥接适用。这里只用Kp≤TV(q)，没有将输出像空间扩大后宣称Kp=TV(q)。全部尾段保留，输入时长没有统一上限。

## 4. z≤U：两种不同的统一界失败

### 4.1 0<z<U，依赖C028的精确模型存在

C028值域命题给一个有限正参数模型p，恰有ζ*(p)=z。先固定该模型和κ>1，已审真实topcut分子在iS满足N_z=0、Nκz=cp(1−κ²)≠0；共同有限支撑输入族的完整峰比无界。故该一个Kp已经为∞，更无跨模型有限界。不是说每个模型在预定z下都失界。

### 4.2 z=U，逐对有限但不统一

C028上端构造给每个t有限正模型p_t，满足ζ*(p_t)<U且ζ*(p_t)→U。于是

\[
r_t=U/\zeta_*(p_t)>1,\qquad\delta_t=r_t-1>0,\qquad\delta_t\to0\quad(t\to\infty).
\]

对充分大的t有0<δt≤ηκ。已审C020的模型统一下常数Lκ>0给

\[
\mathcal K_{p_t}(U,\kappa)
\ge\mathcal K_{C^1,p_t}(U,\kappa)
\ge\frac{L_\kappa}{\delta_t}\longrightarrow\infty,
\quad L_\kappa=\frac{(\kappa-1)(\kappa+3)}{10\kappa^3}.
\tag{P13}
\]

每个p_t自身非临界，故固定对的Kp_t仍有限；无界的是跨模型上确界。输入可以随模型选择，两个状态对同一模型仍使用同一输入；没有固定天然记录或统一输入时长要求。

(P13)才是否定边界统一界的理由。不能仅因(P7)在c→1时发散，就宣布不存在另一有限界；本证明没有作该逻辑跳跃。

## 5. 失效尝试与适用边界

- b→0且x→0最可能使分母小，不能直接在含b的式子中取正下界。本证明用(P5)的实/虚部分支，分子随之缩小，消掉该退化。
- x≈1且u≈1是另一风险。z>U时u≤c<1提供统一间隔；边界c=1不能沿用正向常数，由独立序列下界处理。
- 稳定性必须对Q核实，不能把一般不稳定商的轴上sup当H∞。这里z>U强制z>每个ζ*，所以没有RHP商极点；没有误用不稳定Q的因果范数。
- Boyd只用于实稳定严格真G、保守9阶；κ直通项另补。机械临界或重极点不改变实际有限极点上限，重根处理来自已审C024连续性，不归称原书完整语法。
- (P2)允许界依赖预定ζ₀和κ，不能缩成κ-only。其边界是所列数学类的输出抵消位置，不是工程安全阈值、建议阻尼值、最优系数或短时需求预测。
- 本题固定的是全类共用的两阻尼比；m/k和频率可以变。每个模型内的输出/输入映射仍固定。没有推广到其他输出、含黏滞总截面力、任意阻尼矩阵或同一截断观察窗。

## 6. 来源及待审接口

待不同作者重点核对(P3)分子恒等式、低/中/高三段界尤其(P6)权重、Q稳定与9阶/19→39直通处理、原L1桥接、z=U的逐对有限/跨模型无界，以及C028依赖。候选不使用数值证据，不进入当前v005。

| 既有来源或独审 | SHA256 |
|---|---|
| [C028值域候选](critical-damping-range-candidate.md) | 2d2ee32e3ae68a2a45802a8e16b6bf3291e7bda69bc499e4bc84c572dab44674 |
| [C028异作者审核](../../verification/theory-session002/critical-damping-range-review.md) | dfec30deb7f42a39e26d4c669aaeea42f0bb606cba780005a1476818202dc3f0 |
| [C020原命题](../../verification/theory-round001/explicit-detuning-bound-candidate.md) | eae981f394ed06dc1bc085dea34fd8bf4343a570128ae38efe483ac03b3b0d79 |
| [C020独审](../../verification/theory-session002/explicit-detuning-bound-review.md) | 3ee1f68b91e22448f3e127a86207de52d7e3aba2eca5926377f3ccf10dace838 |
| [C020原L1桥接](../../verification/theory-session002/C020-input-class-addendum.md) | 462eca175cbc2de92c7cb82f946464c256c511edb8bb78d4050dbf7b4b851a55 |
| [C024范数路线](../../verification/theory-session002/classical-norm-route-candidate.md) | a7ebeb92c03d59af08332560e178c68629e33c501a120e997e5cf2fbc49666be |
| [C024不同作者独审](../../verification/theory-round001/classical-norm-route-review.md) | afb8993b77364c6c3865ecb7748473f5ef4ba817d757c063a4e74e4c995bafd2 |
| [Boyd5.33原页条件](../../literature/theory-session002/Boyd-5.33-conditions-001.md) | a5dafe8fb68b0d6c4d4bfb734c44caa47d1eb460cd65b30d27ddba92b5c31bf4 |
| [固定非临界对/稳定性独审](../../verification/detuning-boundary-review.md) | d8b3077827b8ba0c8e0670ec3a6bcde80c7ff7c8769f47917e0c98cce2759866 |

本轮只解析推导及文档身份/链接/编码检查，未做实验、计算脚本或搜索。完成后冻结回主控，等不同作者审核后再裁决共享状态或是否入稿。
