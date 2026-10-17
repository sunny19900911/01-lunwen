# 固定物理输入时长的跨模型边界：刚度—时间缩放候选

2026-10-17，Asia/Shanghai；13:26:58开始读取，单项≤5分钟。纯解析，无实验、搜索、谱/根/网格或子任务，不扩当前v006范围，不改共享或正文。**新缩放及固定时长三分法均为candidate，待不同作者核。** C029等既有来源按主控已接纳状态使用，原candidate文件不改字节。

**候选结论：对每个预先固定的物理半时长Tfix>0、基准z=ζ₀>0及κ>1，跨全部有限正m/k三层真实topcut类、输入支撑[0,2Tfix]的最优完整峰比上确界，恰等于允许任意有限支撑长度时的跨模型上确界。因此它有限当且仅当z>U=√(2/27)。** 在0<z≤U时，固定物理时长不能替代C025的固定模型条件；下述失界通过改变模型完成，不是在一个固定模型里只换固定时长波形。

## 1. 基底加速度输入及允许的模型缩放

固定任一合法原模型p：M=diag(m)>0，标准剪切K=Bᵀdiag(k)B，b=1，输出ℓ=k₃(0,−1,1)，共同经典模态阻尼Cζ。原方程为

\[
M\ddot u+C_\zeta\dot u+Ku=Mb f(t),\qquad f=-a_g,\qquad y=\ell^Tu.
\tag{S1}
\]

任取有限σ>0，将全部层刚度乘σ²，质量不变：

\[
M_\sigma=M,\quad K_\sigma=\sigma^2K,\quad
k_{j,\sigma}=\sigma^2k_j,\quad
\ell_\sigma=\sigma^2\ell.
\tag{S2}
\]

仍是有限正质量/正层刚度真实链，真实输出为新模型的k₃,σ(u₃,σ−u₂,σ)。质量归一振型可保持相同，ωᵢ,σ=σωᵢ、Γᵢ,σ=Γᵢ，因此在两个阻尼状态分别有

\[
C_{\zeta,\sigma}
=M\Phi\operatorname{diag}(2\zeta\sigma\omega_i)\Phi^TM
=\sigma C_\zeta.
\tag{S3}
\]

共同ζ、预定z及κ均不变，正阻尼及增量耗散保持。Sσ=σS、Dσ=σ³D，故ζ*,σ=ζ*，临界/非临界身份不变。这是在相同物理单位下改变刚度与频率，不只是重命名时间单位。

## 2. 传递函数与时域因子核对

以f=−a_g为标量输入，原真实topcut传递为

\[
H_\zeta(s)=\ell^T(s^2M+sC_\zeta+K)^{-1}Mb.
\]

因缩放动力矩阵可提出σ²，新模型严格有

\[
\begin{aligned}
H_{\zeta,\sigma}(s)
&=(\sigma^2\ell)^T[s^2M+s\sigma C_\zeta+\sigma^2K]^{-1}Mb\\
&=H_\zeta(s/\sigma).
\end{aligned}
\tag{S4}
\]

取两个状态共同的新输入fσ(t)=f(σt)。Laplace变换为Fσ(s)=σ⁻¹F(s/σ)，所以

\[
Y_{\zeta,\sigma}(s)=\sigma^{-1}Y_\zeta(s/\sigma),
\quad h_{\zeta,\sigma}(t)=\sigma h_\zeta(\sigma t),
\quad \boxed{y_{\zeta,\sigma}(t)=y_\zeta(\sigma t).}
\tag{S5}
\]

没有遗漏变换中的1/σ；冲激核本身的σ系数在卷积换元中抵消。

也可直接核运动方程：取uσ(t)=σ⁻²u(σt)，则u̇σ=σ⁻¹u̇(σt)、üσ=ü(σt)，代入缩放后的(S1)得到同一右端Mb f(σt)，零初始保持，ℓσᵀuσ=y(σt)。输入仍是相同加速度单位的基底加速度，不是保持位移不变后错误增加惯性输入；若另需表示共同基底位移，可取qg,σ(t)=σ⁻²qg(σt)，其加速度恰为q̈g(σt)。

对实紧支撑L1输入，卷积积分换元亦直接证明(S5)，不需要输入可微。若原输入全轴C1，新输入仍C1。σ>0给全时间半轴的双射，包含输入后全部自由尾段，故

\[
P_{j,p_\sigma}(f_\sigma)=P_{j,p}(f),\qquad
R_{p_\sigma}(f_\sigma)=R_p(f),\qquad
\|f_\sigma\|_1=\sigma^{-1}\|f\|_1.
\tag{S6}
\]

原输入有有限L∞幅值时，该幅值完全保持；若原幅≤1，新输入仍幅≤1。实际a_g输入的传递整体多一个负号，缩放与峰比结论相同。两状态使用相同σ及同一fσ，不另行归一化各自响应。

## 3. 任意固定物理时长与跨模型上确界

固定Tfix>0。任一有限支撑输入可先共同平移，使其支撑于[0,Lf]，Lf>0有限；完整峰值不因平移改变。选择

\[
\sigma\ge\max\{1,L_f/(2T_{\rm fix})\}<\infty.
\tag{S7}
\]

则fσ支撑于[0,Lf/σ]⊂[0,2Tfix]，并由(S6)保留原峰比。每个目标比值选一个输入，再选一个有限σ和缩放模型；原模型类对该刚度缩放封闭。

令Bfree(z,κ)为原C029跨所有模型、非零实紧支撑L1且不限支撑长度的上确界，Bfix(Tfix;z,κ)为同一跨模型类但限支撑[0,2Tfix]的上确界。类包含给Bfix≤Bfree；反向由(S7)把每一个自由时长候选比值原样放进固定时长跨模型集合，得到

\[
\boxed{B_{\rm fix}(T_{\rm fix};z,\kappa)
=B_{\rm free}(z,\kappa),\qquad T_{\rm fix}>0.}
\tag{S8}
\]

等号在扩展实数中成立，允许两边为∞；它不是同一固定模型两种输入类的最优常数相等。

对某个固定原p及某个已固定σ，类似双向输入换元还给

\[
K_{p_\sigma,T_{\rm fix}}(z,\kappa)
=K_{p,\sigma T_{\rm fix}}(z,\kappa).
\tag{S9}
\]

这里右边允许的原模型时长也变了，没有把Kp,Tfix变成同一固定p的无界量。

## 4. 已审C029给出的固定秒数三分法

由(S8)及已审C029，针对z>0、κ>1：

\[
\boxed{B_{\rm fix}(T_{\rm fix};z,\kappa)<\infty
\iff z>U,\qquad U=\sqrt{2/27},\quad T_{\rm fix}>0.}
\tag{S10}
\]

1. **z>U。** C029的39M(z,κ)已覆盖全部模型和任意有限支撑实L1输入，因此也控制固定时长子类；它不依赖Tfix或模型，仍允许依赖预定z、κ。
2. **0<z<U。** C028先选一个ζ*=z的模型，C016给任意大比值的有限支撑C1包络输入。对每条见证按(S7)选σ，得到固定Tfix内、幅不增、同比值的另一个合法模型/共同输入。跨模型上确界为∞；新模型保持临界，但模型会随见证改变。
3. **z=U。** 每个有限正模型都非临界，固定对的全部有限支撑峰比本来就有限，因此其固定时长子类亦有限。C028上端序列和C020给跨模型任意大比值的有限C1输入；逐条压缩后同样塞入预定时长，且ζ*不变，所有缩放模型仍非临界。因此逐模型有限与固定秒数下的跨模型∞同时成立。

两种否定已有实C1、幅≤1的设计见证；必要时还可对原有界C1输入作一次共同正比例缩幅，不改峰比。因此输入幅上限或仅要求C1都不能挽救这里的跨全模型统一界。没有对任意非平滑L1输入凭空强加L∞归一化。

κ=1时另为相同状态、峰比1；z=0不在本正阻尼命题中，不代入阈值估计。

## 5. 固定模型条件为何仍必要

否定部分的量词是：对每个预给Tfix>0及每个要求R，存在一个模型pR和同一对输入fR，使固定支撑下峰比>R。σ可以依原模型、原输入长度及R所需见证选择，符合跨模型上确界。

没有证明存在**同一个**p，使该固定Tfix内峰比可任意大。也没有选一个共同σ压缩全部不断增长的原输入支撑；每条见证都可使用新的σ，所以K与C等模型参数改变。C025对每个固定模型的有限时长界仍成立，其模型相关常数/自然时间尺度不需对这些缩放模型统一。

本缩放一般使输入导数按σ的幂增大、频率尺度提高，并使全部刚度乘σ²。故不外推到有固定带宽/导数界、频率区间、刚度或质量参数盒、装置约束的更窄类。它是无这些附加约束的数学类反例，不是实际地震波或工程阻尼建议，也不声称最优有限常数/工程安全阈值。

特别地，对每个预给0<z≤U，即使允许界依赖(z,κ,Tfix)，仍没有跨全正模型有限保证；因此更不能只保留κ与物理秒数Tfix来替代C025的模型依赖。z>U则维持C029允许依赖(z,κ)的正向界，不把它误写成全正阻尼域的κ-only结论。

## 6. 来源、状态与待审点

本轮待独审：Cζ、ℓ和加速度输入的缩放因子；Laplace的1/σ及位移σ⁻²；全部尾段/同一输入；跨模型量词及(S8)反向包含；z=U逐固定对有限。既有来源及独审只读绑定如下，原字节不改。

| 已审来源或审核 | SHA256 |
|---|---|
| [C029预定阻尼三分法](prescribed-damping-uniform-bound-candidate.md) | 82fb5aa189567e4e4d9caa95ddd0cd787d2c80914b67d4291cfe83ea24e4167b |
| [C029不同作者独审](../../verification/theory-session002/prescribed-damping-uniform-bound-review.md) | 8caa090fc5f02f83aecc2db1f2987431dbab4018deed18b894c823e60f38c9eb |
| [C016一般物理构造独审](../../verification/addendum-V011-general-topcut.md) | 9e411f53f706d2cb5489f7e559a4ba064a0ac8176dd0c57676a50f7865b1b70e |
| [C028值域](critical-damping-range-candidate.md) | 2d2ee32e3ae68a2a45802a8e16b6bf3291e7bda69bc499e4bc84c572dab44674 |
| [C028不同作者独审](../../verification/theory-session002/critical-damping-range-review.md) | dfec30deb7f42a39e26d4c669aaeea42f0bb606cba780005a1476818202dc3f0 |
| [C020下界原件](../../verification/theory-round001/explicit-detuning-bound-candidate.md) | eae981f394ed06dc1bc085dea34fd8bf4343a570128ae38efe483ac03b3b0d79 |
| [C025固定模型上界](../../verification/theory-session002/fixed-duration-upper-feasibility.md) | d0b90a16a80a74d6db6d105e68df48bcbd75fe37489b9ab7d643275cdd44d8ac |
| [C025不同作者审核](fixed-duration-upper-independent-review.md) | b13c0254d92429f789be2c788d5f0513d5a4b6d642f7d9fb1ad703343ca46030 |

本文件只有解析和文档QA，没有实验或新计算脚本。完成冻结回报主控，待不同作者审核，不自行改账本、v006或其他稿件。
