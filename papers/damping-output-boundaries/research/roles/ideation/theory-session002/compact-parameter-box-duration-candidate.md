# 正参数紧盒与固定输入时长：统一完整峰比有限性的候选

2026-10-17，Asia/Shanghai；13:38:46开始读取，单项≤5分钟。纯解析可行性/证明候选，无新实验、搜索、谱/根/网格、子任务或Git调用，不扩v006，不改共享账本或正文。**新盒内统一命题保持candidate，待不同作者审核。**

**候选结论：固定正参数紧盒、z=ζ₀>0、κ>1及物理半时长Tfix>0后，对全盒真实topcut、支撑[0,2Tfix]的全部非零实L1共同输入，存在统一有限完整峰比界。** 对0<z≤U=√(2/27)，可重新建立盒上统一的C025两步估计；无需所有模型的r=z/ζ*都在[1/2,3/2]。z>U直接用已审C029，无需扩展过阻尼机械可观测性论证。下述只定义存在性常数，不提供数值、认证下界、最优系数或工程值。

## 1. 参数紧盒与连续物理表示

固定

\[
\mathcal P_\Box=[m_-,m_+]^3\times[k_-,k_+]^3,
\quad0<m_-\le m_+<\infty,\quad0<k_-\le k_+<\infty.
\tag{B1}
\]

每个p对应M=diag(m)、标准固定基剪切K、b=1、ℓ=k₃(0,−1,1)，两状态各阶共同阻尼为z、κz。Pj均包括全部自由尾段，非零实L1输入支撑于[0,2Tfix]，零初始，不加幅值/Lip/导数限制。

令J=M⁻¹ᐟ²KM⁻¹ᐟ²，物理经典阻尼可写

\[
C_z(p)=2zM^{1/2}J(p)^{1/2}M^{1/2}.
\tag{B2}
\]

正对角逆平方根、正定平方根均连续，故固定物理状态X=(u,u̇)中的

\[
\mathcal A_p=\begin{pmatrix}0&I\\-M^{-1}K&-M^{-1}C_z\end{pmatrix},
\qquad L_p=(\ell^T,0)
\tag{B3}
\]

随p连续。不需先选择一个全局振型符号，避免把符号跳变误当模型不连续。

## 2. 盒上正频率、频隙和真实留数不退化

每个J正定、不可约实对称三对角，因两个非对角均非零而谱简单。按大小排序的λᵢ(p)及ωᵢ(p)=√λᵢ(p)连续，因此在紧盒上

\[
\inf_p\omega_1(p)>0,\quad\sup_p\omega_3(p)<\infty,
\quad\inf_p\min\{\lambda_2-\lambda_1,\lambda_3-\lambda_2\}>0.
\tag{B4}
\]

理由不是给频隙虚填一个数字：若这些连续正函数的最小值为0，紧性使其在某个盒内点达到0，与该点正定/简单谱矛盾。

真实topcut的既有完整物理矩给

\[
\rho_i(p)=\frac{c(p)}{\prod_{j\ne i}(\lambda_i-\lambda_j)},
\qquad c(p)=\frac{k_1k_2k_3}{m_1m_2}>0.
\tag{B5}
\]

故ρᵢ在盒上连续，有限且从不为0，特别min_p|ρᵢ|>0；不是自由拟合留数。由ρᵢ=(ℓᵀφᵢ)Γᵢ≠0，逐点输出投影ℓᵀφᵢ亦非零。S=Σωᵢ及q*=ζ*²=D/(4S³)连续、正，盒上具有正最小值和有限最大值。这里只使用这些存在性事实，不声称已数值计算任何极值。

## 3. z≤U时重建分子核统一有界：不硬套r区间

现在固定0<z≤U<1。令a=2ζ*、r=z/ζ*、x=s/S，则ar=2z。C025的原假设r∈[1/2,3/2]未必覆盖本盒；仅由每个模型固定时长有限，也不能直接取一个未证连续的Cmodel的最大值。

但代数分母及分子比可直接改写为

\[
p_p(x)=x^3+2zx^2+x+\frac{2q_*(p)}z,
\qquad
V_p(x)=\kappa+
\frac{2(\kappa-1)[\kappa z x^2-q_*(p)/z]}{p_p(x)}.
\tag{B6}
\]

实轴导数满足与p无关的严格界

\[
p_p'(x)=3(x+2z/3)^2+1-4z^2/3
\ge1-\frac{8}{81}=\frac{73}{81}>0.
\tag{B7}
\]

常数项2q*/z>0，所以每个p_p恰有一个负实根和一对非实共轭根；全部简单（非实重根连同共轭至少需四次）。以负实根及正/负虚部连续标记，系数在盒上连续，根和简单留数也连续。紧盒使留数之和及S有有限上界，根的相互距离亦有正最小值。

离轴根按稳定半轴取核；z=ζ*(p)时的±i归一化根取因果有界振荡核。每项幅值不超过S(p)|Rλ(p)|，故存在

\[
v_p=\kappa\delta_0+g_{v,p}(t)dt,\qquad
\sup_{p\in\mathcal P_\Box}\|g_{v,p}\|_\infty
\le\max_p\left[S(p)\sum_\lambda|R_\lambda(p)|\right]
=:M_{v,\Box}<\infty.
\tag{B8}
\]

这不要求在临界面上L1连续，也不称临界核TV有限。盒上q*正下界排除常数项趋0的边界；简单根及紧性排除留数极点碰撞。

三个机械分母比仍有因果乘积核μp，TV≤Aκ=(3−2/κ)³，覆盖新状态的机械临界和过阻尼。沿C025合法接口，非临界用稳定双边Fourier，临界对实际zout=μp*y₀∈L1用Re s>0的Laplace身份；有界核与L1的绝对卷积、结合律均保留。因此对全部盒内模型

\[
P_1\le A_\kappa\{\kappa P_0+M_{v,\Box}\|y_0\|_1\}.
\tag{B9}
\]

重用的是同一卷积证明；(B6)—(B8)重新提供它需要的统一核界，而非省掉原r假设。

## 4. 盒上可观测Gramian及一致自由尾

基准z≤U<1固定，六机械极点为ωᵢ(−z±i√(1−z²))。频率互异且正，六极点不同，真实输出投影均非零，PBH条件给每个物理对(Lp,Ap)可观测。

固定物理观测窗tobs>0，不随p或输入改变，定义

\[
W_p=\int_0^{t_{\rm obs}}e^{\mathcal A_p^Ts}L_p^TL_pe^{\mathcal A_ps}ds,
\qquad w_\Box=\min_p\lambda_{\min}W_p>0.
\tag{B10}
\]

Wp逐点正定且连续，盒紧，故严格正下界成立。使用固定物理状态坐标，使Gramian连续性不依赖模态向量符号。

全部Ap也构成紧Hurwitz族。可通过唯一解ApᵀPp+PpAp=−I的正定Lyapunov矩阵核一致指数稳定：有限维Lyapunov算子可逆、系数连续，故Pp连续；紧性给其最小特征值正下界和最大特征值有限上界，再由d(XᵀPpX)/dt=−||X||²获得统一指数包络。此论证不先假设无限积分一致收敛，因而无循环。可选有限常数Mtail,□、γ□>0，使

\[
\|L_pe^{\mathcal A_ps}\|\le M_{{\rm tail},\Box}e^{-\gamma_\Box s},
\qquad p\in\mathcal P_\Box,\ s\ge0.
\tag{B11}
\]

这些常数只是存在性量；没有计算Pp、Gramian或认证其极值。

输入在b=2Tfix停止后，L1受迫状态连续，齐次自由尾为Lp exp(Ap s)Xp(b)。完整P₀控制未来观测窗，故

\[
\|X_p(b)\|\le\sqrt{t_{\rm obs}/w_\Box}\,P_0,
\qquad
\int_b^\infty|y_0(t)|dt\le C_{{\rm tail},\Box}P_0,
\quad
C_{{\rm tail},\Box}=
\frac{M_{{\rm tail},\Box}}{\gamma_\Box}
\sqrt{t_{\rm obs}/w_\Box}<\infty.
\tag{B12}
\]

加上输入段长度直接估计，||y₀||1≤(2Tfix+Ctail,□)P₀。没有把输出在b处截断，也没有由输入L1大小反推P₀；输入本身可无界。每个非零输入P₀>0由原非零有理传递注入性保证。

## 5. 全盒固定时长有限界及其边界

(B9)与(B12)给存在性上界

\[
\boxed{\sup_{p\in\mathcal P_\Box}
\sup_{0\ne f\in L^1,\ \operatorname{supp}f\subset[0,2T_{\rm fix}]}
\frac{P_1(f)}{P_0(f)}
\le A_\kappa\big[\kappa+M_{v,\Box}
(2T_{\rm fix}+C_{{\rm tail},\Box})\big]<\infty,
\quad 0<z\le U.}
\tag{B13}
\]

Mv,□具有时间倒数单位、Ctail,□与Tfix为时间，右端无量纲。常数允许依赖盒边界、z、κ及固定状态/时间规范，不依赖具体模型或输入。本轮未给数值或可执行认证算法，故不宣称已有可计算证书、工程可用系数或最优值。

z>U时直接用已审C029的39M(z,κ)模型无关界即可，甚至不需要紧盒或固定Tfix；本项不重新处理过阻尼机械可观测性。两段合起来，题设任意固定z>0、κ>1、Tfix>0的正紧盒均可恢复统一完整峰比有限性。

此前刚度无界缩放会把k乘σ²，不能保持同一给定有限k+盒；这里的频率、频隙和Gramian正下界正是未加盒时可能失控的接口。存在性不表示任何实际工程盒都有小常数，也不表示模型不确定时有自然波预测保证。

不能把(B13)去掉固定支撑：若盒内含ζ*(p)=z的临界模型，已审无限输入时长族仍可失界。也不能只因某些模型逐点有限，就声称任意参数集合统一；正下界/上界及紧性均被实际使用。

## 6. 待审接口与来源

待异作者检查：正紧盒上的简单谱/留数连续性；固定z的(B6)—(B7)替代r区间是否正确；临界核统一L∞及像空间身份；物理状态Gramian严格正和Lyapunov紧族包络；完整尾段/全部原L1输入。未发现必须保留为未证的接口，仍需独立审核后由主控裁决。

| 已审来源或审核 | SHA256 |
|---|---|
| [C025原固定模型证明](../../verification/theory-session002/fixed-duration-upper-feasibility.md) | d0b90a16a80a74d6db6d105e68df48bcbd75fe37489b9ab7d643275cdd44d8ac |
| [C025不同作者审核](fixed-duration-upper-independent-review.md) | b13c0254d92429f789be2c788d5f0513d5a4b6d642f7d9fb1ad703343ca46030 |
| [真实三层谱/留数独审](../../verification/addendum-V011-general-topcut.md) | 9e411f53f706d2cb5489f7e559a4ba064a0ac8176dd0c57676a50f7865b1b70e |
| [根分类/稳定性独审](../../verification/detuning-boundary-review.md) | d8b3077827b8ba0c8e0670ec3a6bcde80c7ff7c8769f47917e0c98cce2759866 |
| [C029预定阻尼界](prescribed-damping-uniform-bound-candidate.md) | 82fb5aa189567e4e4d9caa95ddd0cd787d2c80914b67d4291cfe83ea24e4167b |
| [C029不同作者独审](../../verification/theory-session002/prescribed-damping-uniform-bound-review.md) | 8caa090fc5f02f83aecc2db1f2987431dbab4018deed18b894c823e60f38c9eb |

本轮只有解析与文档QA，无Git调用、实验、搜索、计算谱/根/矩阵或子任务，不改旧证据。完成后冻结回主控等待独审，不扩v006或共享结论。
