# 低临界阻尼的谱极限、首阶渐近及参数成本

2026-10-17，Asia/Shanghai；12:32:09开始读取。单项≤5分钟，固定族M=I、k=(1,1,L)，不求新根、不扫参、不拟合、不算时程。C021已由主控接纳；本文件所有新增渐近与推广推论仍为 **candidate / analytic-derivation，待独立审核**，不裁定首创性。

**候选结论：L→∞时，两个低阶λ趋于μ±=(5±√17)/4，高阶λ₃~2L；q(L)~[√(5+2√2)/8]L⁻¹ᐟ²，ζ*(L)~[(5+2√2)¹ᐟ⁴/(2√2)]L⁻¹ᐟ⁴。结合已接纳的严格单调性，任意目标0<ε≤ζ*(1)在L≥1有唯一参数Lε；当ε↓0，Lε~[(5+2√2)/64]ε⁻⁴。** 这表示本固定一参数族追求很小临界阻尼的刚度比代价，不是工程最优设计或有限L误差保证。

## 1. 低两阶有界与特征不变量

固定

\[
K(L)=\begin{pmatrix}2&-1&0\\-1&1+L&-L\\0&-L&L\end{pmatrix},\quad L>0,
\]

记有序特征值0<λ₁≤λ₂≤λ₃，ωᵢ=√λᵢ。矩阵特征多项式为

\[
p_L(\lambda)=\lambda^3-(3+2L)\lambda^2+(1+5L)\lambda-L.
\tag{A1}
\]

除以L后，在每个有界λ集合上系数极限为−2λ²+5λ−1，但不能仅凭此就默认实际有两个有界根。所需有界性由[既有IVT谱压缩证明](../../verification/appendix-V011-low-damping-IVT.md)提供：固定二维子空间u₂=u₃的Ritz值为

\[
\mu_\pm=\frac{5\pm\sqrt{17}}4,
\qquad 0<\lambda_1\le\mu_-,\quad0<\lambda_2\le\mu_+.
\tag{A2}
\]

设τ=λ₁+λ₂、π=λ₁λ₂，则τ有界。由迹先得

\[
\lambda_3=2L+3-\tau\sim2L.
\tag{A3}
\]

由行列式及二阶主不变量依次得到

\[
\pi=\frac L{\lambda_3}\longrightarrow\frac12,
\qquad
\tau=\frac{1+5L-\pi}{\lambda_3}\longrightarrow\frac52.
\tag{A4}
\]

所以λ₁、λ₂是t²−τt+π的两个有序正根，根式连续且极限判别式17/4>0，严格有

\[
\lambda_1\longrightarrow\mu_-,\qquad
\lambda_2\longrightarrow\mu_+,\qquad
\lambda_3=2L+\frac12+o(1).
\tag{A5}
\]

这给出实际谱的极限，不使用E012小数外推，也不需要额外假定逐阶根支路的解析性。频率相应满足ω₁→√μ−、ω₂→√μ+、ω₃~√(2L)。

## 2. q和临界阻尼的明确首阶系数

记a=ω₁、b=ω₂、d=ω₃，则由(A5)

\[
a+b\longrightarrow A_0:=\sqrt{\mu_-}+\sqrt{\mu_+}
=\sqrt{\frac52+\sqrt2}>0,
\qquad d\sim\sqrt{2L}\longrightarrow\infty.
\tag{A6}
\]

因为a、b有界，按精确定义

\[
q(L)=\frac{(a+b)(a+d)(b+d)}{4(a+b+d)^3}
=\frac{a+b}{4d}
\frac{(1+a/d)(1+b/d)}{[1+(a+b)/d]^3}.
\tag{A7}
\]

最后的乘因子趋1，故

\[
\boxed{\lim_{L\to\infty}\sqrt L\,q(L)
=Q_0:=\frac{A_0}{4\sqrt2}
=\frac{\sqrt{5+2\sqrt2}}8.}
\tag{A8}
\]

q>0，ζ*(L)=√q(L)，连续平方根直接给

\[
\boxed{\lim_{L\to\infty}L^{1/4}\zeta_*(L)
=Z_0:=\sqrt{Q_0}
=\frac{(5+2\sqrt2)^{1/4}}{2\sqrt2}.}
\tag{A9}
\]

等价地q=Q₀L⁻¹ᐟ²(1+o(1))、ζ*=Z₀L⁻¹ᐟ⁴(1+o(1))。这里o(1)只声明参数趋极限，不给任何有限L的严格余项常数、起效阈值或相对误差。

## 3. 任意目标临界阻尼的唯一参数及成本

[原根结构证明](low-damping-root-structure.md)已由[不同作者独审](../../verification/theory-round001/root-monotonicity-review.md)通过且主控记为C021：q在L≥1连续严格下降。由(A8)，q→0；因此ζ*也连续严格下降，并把[1,∞)一一映到(0,ζ*(1)]。从而

\[
\forall\varepsilon\in(0,\zeta_*(1)]\quad
\exists!\ L_\varepsilon\in[1,\infty):
\zeta_*(L_\varepsilon)=\varepsilon.
\tag{A10}
\]

ε=ζ*(1)时Lε=1；ε更小时Lε>1，ε↓0时Lε→∞。将(A9)沿唯一逆函数代入，得到

\[
\varepsilon^4L_\varepsilon\longrightarrow Z_0^4=Q_0^2
=\frac{5+2\sqrt2}{64},
\]

即

\[
\boxed{L_\varepsilon=
\frac{5+2\sqrt2}{64}\,\varepsilon^{-4}(1+o(1)),
\qquad \varepsilon\downarrow0.}
\tag{A11}
\]

例如严格的渐近比值表述为L_{ε/2}/Lε→16，而不是对任意有限ε宣称恰为16。当前k₁=k₂=1，因此L也是k₃/k₁的刚度比；上述成本只属于这一指定族，不能据此断言所有三层体系都至少需要同样刚度比，更不是最小材料/装置/经济成本。

## 4. 与固定κ物理反例的有边界推论

对每个先给定目标ε∈(0,ζ*(1)]，先固定(A10)唯一选定的Lε，再任取一个固定κ>1，令两状态的各阶共同经典阻尼比分别为ε、κε，并固定M、K、b、真实弹性topcut输出ℓ=Lε(0,−1,1)。两阻尼矩阵为Cζ=2ζ√K，均稳定，增量正定。

由已接纳的一般三层topcut精确零点及有限支撑包络证明（C016 v2），有

\[
N_\varepsilon(iS)=0,
\quad N_{\kappa\varepsilon}(iS)=L_\varepsilon(1-\kappa^2)\ne0.
\tag{A12}
\]

因此对该一个已固定模型、输出和阻尼对，存在共同的、幅有界、每次有限支撑而支撑时长可增长的输入族，使含全部自由尾段的峰比无界。没有要求κε<1；共同经典系统在任意正ζ下稳定，若新态部分模态过阻尼也不改变该存在性。

该推论不表示任意已给定三层模型都能指定任意ε而保持零点，也不表示固定天然记录、固定最大时长、绝对需求发散、短时显著风险或仅相邻层dashpot。一般理想被动网络的现有证明仍按其原限定范围适用，不能由本渐近式推出施工方案。

## 5. 本轮验证与交接

本轮推导仅使用(A1)不变量、已审Ritz界、根式连续性、首阶极限及已接纳C021/C016 v2。标准库Fraction在内存独立检查低根判别式(5/2)²−4(1/2)=17/4，以及Q₀²=(5/2+√2)/32=(5+2√2)/64的有理系数；没有创建新数值脚本、计算谱/根、扫参、拟合或重跑E012。

实际读取的C021候选SHA256为5d9b7ef7e9209f0343a6bca5ffd05fb194b3a6573022aae17de4d317a798b9ac；独审路径见第3节。旧IVT、E012及上午冻结证据不改。此项产物交主控安排独审后再由作者使用；新渐近、唯一逆映射及成本推论均保留candidate，不直接改共享主张或正文。
