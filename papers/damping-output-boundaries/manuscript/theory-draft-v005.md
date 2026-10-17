# 增阻尼下完整峰值的双模态界与三层剪切链的时长—失谐边界

理论主线稿v005，2026年10月17日。以上为工作标题，最终题名、期刊与署名未定。依据用户选择A及主控准入，从已审冻结v004另存；本版整合固定输入时长上界与时长—失谐联合双侧阶，重组第4节，详证另附F。新增结论已由不同作者独审并经主控接纳，先例同条件覆盖仍待核。

**先用日常语言说明问题。** 给结构增加阻尼，像给振动增加缓冲，但不同振动方式在同一位置会互相叠加、抵消。增加缓冲也可能打破原有抵消，使某个位置的反应比以前大。本文研究的不是某栋楼会不会危险，而是：如果只知道“阻尼增加了多少倍”，能否保证同一位置的最大反应至多增加多少倍？我们已在明确模型下证明：只有一、两种有效振动方式时，存在一个保守的共同上限；三层简单结构就能构造出打破任何这种共同上限的例子。例子中主要是原来的反应越来越接近零，新的反应保持有限，所以比值很大；它不表示实际响应无限变大。精确抵消、输入持续时间及阻尼器连接方式是必须保留的条件，不能直接把例子当作真实建筑风险预测。

## 摘要

针对质量、刚度、输入分布和实线性位移/弹性恢复力输出固定、各阶阻尼比共同变化的线性经典阻尼系统，比较同一紧支撑实L1输入、零初始状态下包含全部自由尾段的输出峰值。对至多两个有效模态，构造传递比的稳定双边有限测度核，证明仅依赖阻尼倍率κ的保守界 $B(\kappa)=(2\kappa-1)(3-2/\kappa)^2$。对任意固定正质量、正层刚度的标准三层剪切楼，以真实顶层弹性剪力为输出，在模型谱定义的基准阻尼ζ*与每个固定κ>1的κζ*之间，构造共同有限支撑有界基底输入族，使完整峰值比无界，而两个绝对响应一致有界。由谱连续性进一步证明，存在以隐式刚度 $L_*$ 精确定义的固定模型，在精确5%→8%阻尼对下具有同样性质；对应谱函数在 $L\ge1$ 严格下降；任意足够小的目标临界阻尼ε在该族内有唯一参数，其刚度比随ε⁻⁴渐近增长。由低阶统一界与物理三层构造，确定破坏这类κ-only有限保证的最少有效模态数为3；该逐层单自由度完整剪切链内最少层数亦为3。每个固定非临界阻尼对仍有模型相关有限界；在明确的临界邻域，最优完整峰比被两个仅依赖κ的显式常数乘以相对失谐距离的倒数双侧夹住；固定模型的输入时长有上限时，包括精确临界在内的完整峰比仍有限；在共同临界邻域和充分时长以上，最坏峰比被固定模型常数乘以时长尺度与失谐倒数的较小者双侧夹住。单位三层模型的六时长采样结果仅展示解析机制，其阻尼为约26.1%→41.7%，与5%→8%存在模型分开。相关零点分类和范数工具已有先例；本稿保留同条件文献覆盖与最优常数的未决状态。

关键词：经典阻尼；完整峰值；双模态；剪切链；反共振；双边卷积

## 1 问题、模型与完整峰值

不同结构输出由模态贡献以不同权重叠加而成。阻尼改变这些贡献的幅值和相位，单一稳态频率上的比较与完整时程峰值的比较因而需要分开。本文问：在同一模型、输入和输出下，增阻尼后的完整峰值，能否由增阻尼前的完整峰值乘一个仅依赖阻尼倍率的有限常数控制？本文的“统一”同时跨固有频率、实留数和允许的输入；每个具体模型的有限界是较弱的命题。

反共振与输出零点的已有研究为这一问题提供背景[1–3]，经典peak gain和卷积估计提供分析工具[4–6]。三质点非最小相位例子已有直接先例[7]。本文按模型、输出、阻尼路径与完整时间域给出正反两端结论，候选贡献的先例覆盖尚需继续核查。

### 1.1 固定对象与有效模态


考虑 $M,K$ 实对称正定、质量归一化实振型及固定输入分布，模态坐标满足

$$\ddot q_i+2\zeta\omega_i\dot q_i+\omega_i^2q_i=\Gamma_i f(t),\qquad \omega_i>0.$$

固定输出为 $Y=\ell^Tu$，留数 $r_i=(\ell^T\phi_i)\Gamma_i$ 为实数。取 $\ell=Kv$ 时，$Y=v^TKu$ 是固定广义恢复力。其Laplace传递函数为

$$G_\zeta(s)=\sum_{i=1}^n\frac{r_i}{s^2+2\zeta\omega_i s+\omega_i^2}.\tag{1}$$

两个状态满足 $0<\zeta_0\le\zeta_1$，质量、刚度、输入分布及输出均保持不变，各阶阻尼比在同一状态中共同取 $\zeta_k$。合并同频项后，去除合并留数为0的项，剩余项数定义为有效模态数。以下排除恒零传递函数；零输入按范数不等式处理，比值仅对非零基准峰值定义。

理论输入采用相同的实紧支撑 $f\in L^1(\mathbb R)$，零初始状态。完整峰值定义为

$$P_k(f)=\|h_k*f\|_{L^\infty(\mathbb R)},\qquad R_P(f)=P_1(f)/P_0(f),\tag{2}$$

其中 $h_k$ 为因果冲激响应，输出包含全部自由衰减尾段。该位移/恢复力表达的输出系数不随阻尼变化；含阻尼力系数或绝对加速度直接项的输出按各自完整方程处理。

后文限制输入支撑包含于 $[0,2T]$ 时，T为半支撑时长，输出峰仍按式（2）取完整时间轴，包含输入停止后的全部自由尾段。

### 1.2 不同指标与时间域

指定频率的 $|G_\zeta(\mathrm i\Omega)|$ 比较稳态幅值；L2范数比较全时程平方积分；式（2）比较全时程最大绝对值。频域幅值比不能未经论证直接作为完整峰比上界。信号平方积分也不等于结构机械耗能。本文所有定理均含输入停止后的全部自由衰减，有限观察窗不直接继承双边核的完整峰值界，详见附录A.6。


## 2 至多双模态的统一有限界

对两个不同正固有频率、固定实留数不全为零及第1.1节条件，记 $\kappa=\zeta_1/\zeta_0$。同一紧支撑实L1输入的完整输出满足

$$P_1(f)\le B(\kappa)P_0(f),\qquad B(\kappa)=(2\kappa-1)(3-2/\kappa)^2.\tag{3}$$

证明将 $\mathcal Q=G_1/G_0$ 写成分子比与两个模态分母比。双模态的系数关系保证约分后的商proper、无未消去虚轴极点；分子比具有总变差不超过 $2\kappa-1$ 的稳定双边有限测度核，每个模态比的核总变差不超过 $3-2/\kappa$。由核卷积、傅里叶唯一性及有限测度的L∞估计得到式（3），完整分支证明见附录A。

非最小相位基准输出允许在双边核中出现反因果分量。证明采用完整输出，包含窗外未来及全部尾段信息。对于截断观察窗，需另计窗口外项或采用具体有理商的因果有限窗估计。

一个有效模态时，单个模态分母比给 $P_1\le(3-2/\kappa)P_0$；因此式（3）的保守界也覆盖该情形。对5%→8%的阻尼倍率 $\kappa=1.6$，式（3）为6.7375。该常数给出统一有限保证，最优性及具体记录的实际增幅分别评价。


![图1　双模态完整峰值界与合成见证比较](<E:/11-工作/001-workbuddy spaceV1/001-workbuddy space/109-论文写作/01-lunwen/papers/damping-output-boundaries/experiments/figures/fig04_peak_bound_comparison.png>)

图1　双模态完整峰值界的精化及合成见证。新界为 $(2\kappa-1)(3-2/\kappa)^2$，旧粗界为 $(4\kappa-3)(5-4/\kappa)^2$；在κ=8/5处分别为6.7375和21.25，整体常数均未证明最优。κ虚线为双模态谐波及完整L2比较界；橙点是本节广义输出的完整采样峰比约1.81183；其连续峰比保守数值下界约1.80872。完整峰值条件包含全部自由尾段。[SVG矢量源](../experiments/figures/fig04_peak_bound_comparison.svg)。



**广义输出的数值边界。** 已冻结双模态见证取 $\omega=(1,3)$、$r=(1,-8.9)$、阻尼0.05→0.08。同一保存的分段线性输入支撑600 s，独立非FFT解析步进加900 s自由尾段，得到采样峰0.0143602364445540与0.0260183021231126，采样峰比1.81182964665。基准曲率界 $|y_0''|<207$、步长 $h=1/1024$ s与指数余尾界给连续峰比保守数值下界约1.80872158>1.6；浮点样本未作定向舍入认证，故保留经独立审核的数值证据身份。该见证说明κ本身不能直接充当完整峰值界，未推翻6.7375的统一粗界。

该输出为固定实线性组合，不是本稿第三节的标准剪切链顶层弹性剪力；完整投影矩排除把其留数直接移作相应标准两层弹性截面。原三网格各自重建过候选，不作为同一输入的纯积分收敛。此处只引用冻结最细输入的独立前向审核及连续外包，见[独立递推记录](../research/roles/verification/saved-peak-audit.json)与[连续外包记录](../research/roles/verification/EEXP004-bound-audit.json)。


## 3 真实三层剪切链的失界与最小性

### 3.1 精确输出零点与共同输入族

取任意固定 $m_1,m_2,m_3,k_1,k_2,k_3>0$ 的标准固定基剪切楼，

$$M=\operatorname{diag}(m_1,m_2,m_3),\quad
K=\begin{pmatrix}k_1+k_2&-k_2&0\\-k_2&k_2+k_3&-k_3\\0&-k_3&k_3\end{pmatrix},\quad b=(1,1,1)^T,\quad\ell=k_3(0,-1,1)^T.\tag{4}$$

相对坐标方程为 $M\ddot u+C_\zeta\dot u+Ku=Mbf$，$f=-a_g$；输出 $y=\ell^Tu=k_3(u_3-u_2)$ 是真实顶层弹性层剪力。$K$ 为层间差能量的正定二次型，$M^{-1/2}KM^{-1/2}$ 是不可约实对称三对角阵，谱正且简单。令完整质量归一振型为 $\Phi$、$\lambda_i=\omega_i^2$、$\Gamma_i=\phi_i^TMb$，取共同模态阻尼路径 $C_\zeta=M\Phi\operatorname{diag}(2\zeta\omega_i)\Phi^TM$。各正阻尼状态及增量矩阵均正定。

完整投影矩给 $\sum\rho_i=\ell^Tb=0$、$\sum\lambda_i\rho_i=\ell^TM^{-1}Kb=0$、$\sum\lambda_i^2\rho_i=k_1k_2k_3/(m_1m_2)$。记 $c=k_1k_2k_3/(m_1m_2)>0$，Vandermonde唯一解为

$$\rho_i=(\ell^T\phi_i)\Gamma_i=\frac{c}{\prod_{j\ne i}(\lambda_i-\lambda_j)},\quad
\sum_i\rho_i=\sum_i\lambda_i\rho_i=0,\quad\sum_i\lambda_i^2\rho_i=c.\tag{5}$$

三个真实留数均非零、按频率递增符号为正、负、正，不能自由选取。令 $S=\sum_i\omega_i$、$W=\prod_i\omega_i$、$D=\prod_{i<j}(\omega_i+\omega_j)$。二阶差商给 $\sum_i\omega_i\rho_i=-c/D$、$\sum_i\rho_i/\omega_i=cS/(WD)$；静态矩 $\sum_i\rho_i/\lambda_i=m_3$ 及 $W^2=\det K/\det M$ 给通分常数项 $c$。完整传递 $H_\zeta(s)=\sum_i\rho_i/(s^2+2\zeta\omega_i s+\lambda_i)$ 的分子为

$$N_\zeta(s)=c\left(\frac{2\zeta}{D}s^3+\frac{4S\zeta^2}{D}s^2+\frac{2S^2\zeta}{D}s+1\right).\tag{6}$$

精确定义 $\Omega_*=S$、$\zeta_0=\zeta_*=\sqrt{D/(4S^3)}$。对每个固定 $\kappa>1$，固定 $\zeta_1=\kappa\zeta_*$，并令 $H_0=H_{\zeta_*}$、$H_1=H_{\kappa\zeta_*}$，则

$$N_{\zeta_*}(s)=\frac{2c\zeta_*}{D}(s+2S\zeta_*)(s^2+S^2),\qquad
N_{\kappa\zeta_*}(\mathrm iS)=c(1-\kappa^2)\ne0.\tag{7}$$

每个模态分母在 $\mathrm iS$ 处有正虚部 $2\zeta\omega_iS$，因此 $H_0(\mathrm iS)=0$、$H_1(\mathrm iS)\ne0$。零点来自式（6）—（7）的精确代数定义，基准传递非恒零，因为分子常数项 $c>0$。

固定上述模型、输出和两个阻尼状态。令 $a_T(t)=\sin^2(\pi t/(2T))$ 于 $[0,2T]$ 内，其余为0，取共同实输入

$$f_T(t)=a_T(t)\cos[S(t-T)-\arg H_1(\mathrm iS)],\qquad |f_T|\le1.\tag{8}$$

任意有限正ζ下各模态均严格稳定，包括临界和过阻尼状态；两个实因果冲激核 $h_k$ 指数衰减，有限重根至多附多项式，因此 $h_k\in L^1$ 且 $\mathfrak m_k=\int_0^\infty s|h_k(s)|ds<\infty$，不需将κ限制在欠阻尼范围。由零延拓包络的全局Lipschitz常数 $\pi/(2T)$，在卷积中加减 $a_T(t)$，对全部实 $t$（包括输入后的全部尾段）得到复响应误差不超过 $\pi\mathfrak m_k/(2T)$。在 $t=T$ 新状态实主项为 $|H_1(\mathrm iS)|$，故完整峰值满足

$$0<P_0(T)\le\frac{\pi\mathfrak m_0}{2T},\qquad P_1(T)\ge|H_1(\mathrm iS)|-\frac{\pi\mathfrak m_1}{2T},\qquad
\frac{P_1(T)}{P_0(T)}\ge\frac{2T|H_1(\mathrm iS)|/\pi-\mathfrak m_1}{\mathfrak m_0}\longrightarrow\infty.\tag{9}$$

比值下界取充分大的 $T$；$P_0>0$ 来自非恒零有理 $H_0$ 对非零紧支撑输入的注入性。对每组固定正m/k模型和每个固定κ>1，模型、真实截面、基准ζ*及新状态κζ*均固定，变化的是输入时长；每个 $T$ 下两状态使用同一输入、初始均为零。又因 $P_k(T)\le\|h_k\|_1$，两个绝对响应一致有界，无界的是基准输出趋零时的比值。ζ*由模型决定，结论不将它替换为任意预定基准ζ。

本节无界输入族允许支撑跨度不断增长；对同一模型设共同有限时长上限时，完整峰比仍有有限界，见第4.2节。

### 3.2 低阻尼目标的唯一存在模型

**5%→8%的存在性推论。** 存在有限 $L_*\in(1,20000)$，固定 $M=I_3$、$k=(1,1,L_*)$、真实输出 $y=L_*(u_3-u_2)$，在 $\zeta_0=1/20$、$\zeta_1=2/25$ 的统一模态阻尼状态间，仍有式（9）的完整峰值比无界输入族。这里 $q(L)=D(L)/(4S(L)^3)$，$L_*$ 精确定义为区间 $[1,20000]$ 内方程 $q(L)=1/400$ 的根集最小元；模型选定后不再随输入时长变化。附录B先以连续性和两个严格谱端点证明存在性，再证明固定族的 $q(L)$ 在 $L\ge1$ 严格下降，因此该半轴恰有一个根，与原区间最小元定义相同；不需要其小数值。20000只是保守存在区间上界，不是实际刚度比；这一推论的模型与第4.3节单位数值展示不同。

**任意低临界阻尼目标。** 对同一指定族 $M=I$、$k=(1,1,L)$，严格单调性和谱极限进一步给出

$$\forall\,0<\varepsilon\le\zeta_*(1),\quad
\exists!\ L_\varepsilon\in[1,\infty):\zeta_*(L_\varepsilon)=\varepsilon,\qquad
L_\varepsilon\sim\frac{5+2\sqrt2}{64}\varepsilon^{-4}
\quad(\varepsilon\downarrow0).\tag{10}$$

先给定ε并固定模型 $L_\varepsilon$ 后，对每个固定κ>1，ε→κε仍有第3.1节的共同有限输入无界比族；5%→8%是其中一个精确特例。这里L为本族 $k_3/k_1$，渐近式没有有限L的误差或起效阈值，也不是跨模型必要刚度或工程最优成本。详证见附录B.2。无需κε<1；即使κε=1或κε>1，各模态仍严格稳定。

### 3.3 最少有效模态数的准确含义

| 有效模态数 | 完整峰值的已得结论 | 输入与输出范围 |
|---:|---|---|
| 1 | 有限κ-only界 $3-2/\kappa$ | 同一紧支撑实L1输入、固定实输出、零初始 |
| 2 | 有限κ-only界 $B(\kappa)$ | 异频非恒零模态和，完整尾段 |
| 3 | 每个固定κ>1均有无界比值输入族 | 每组正m/k三层真实弹性topcut，在其ζ*→κζ*路径、变化时长输入族 |

在每层一个自由度的完整正m/k剪切链、共同基底输入和真实顶层弹性剪力这一物理类中，至多两个有效模态受式（3）约束；每组三层链的真实留数则全部非零，在同一输入、零初始和完整时间域条件下达到失界。因此，对每个固定κ>1，使所有有限κ-only统一保证失效的最少有效模态数为3；在这个完整单自由度逐层剪切链内，最少层数也为3。这里各状态内每阶共用同一ζ，未涉及任意两个逐阶阻尼不同的经典矩阵；一般三维建筑的层数不等于有效模态数。

分类针对“任何有限κ-only界是否存在”。第2节双模态见证已给峰值超过κ的数值例；第3.1节基准ζ*由各模型谱确定，未证明对每个预先给定的模型和任意预定ζ0都有相同结论；第3.2节则是给定小ε后另选模型。κ=1时两状态相同。普通峰值增大、指定阻尼域、固定天然记录、固定最大支撑时长和只相邻层dashpot的更窄系统类仍按各自条件评价。

## 4 失谐、输入时长与完整峰比边界

### 4.1 固定失谐界与局部倒数阶

固定一组正m/k三层链、真实topcut及κ>1。若基准 $\zeta_0\ne\zeta_*$，每个固定阻尼对均有依赖模型、$\zeta_0$ 和κ的有限完整峰比界；精确 $\zeta_0=\zeta_*$ 才有该固定对的无界输入族。接近临界时，改变参数后再选足够长的共同输入，可以得到任意大但逐对有限的峰比，不能把逐点有限升级为临界邻域内统一有界。右半平面输出零点不表示机械失稳，各机械极点始终在左半平面。附录C给分子根分类、稳定双边核和近临界同频比的推导；该同频渐近不等于最优完整峰界的渐近公式。

进一步可定量控制临界附近的最坏完整峰比。固定κ>1及一组第3.1节物理模型，令 $\mathcal F_1$ 为非零实紧支撑L1输入，$\mathcal F_{C^1}$ 为其中全轴零延拓后属C1的子类；可共同平移至非负时间轴，均取零初始和完整尾段。分别定义最优常数 $\mathcal K_1(r)$、$\mathcal K_{C^1}(r)$ 为对应输入类上 $P_1/P_0$ 的上确界，模型和两个阻尼状态在每次取上确界时固定。记

$$r=\frac{\zeta_0}{\zeta_*},\quad \delta=|r-1|,\quad
\eta_\kappa=\min\left\{\frac12,\frac{\kappa-1}{2\kappa}\right\}.\tag{11}$$

对全部正质量/正刚度三层链，在 $0<\delta\le\eta_\kappa$ 内有

$$\frac{L_\kappa}{\delta}\le\mathcal K_{C^1}(r)\le\mathcal K_1(r)
\le\|q_r\|_{\rm TV}\le\frac{U_\kappa}{\delta},\qquad
L_\kappa=\frac{(\kappa-1)(\kappa+3)}{10\kappa^3}>0.\tag{12}$$

这里 $q_r$ 是传递商的稳定双边有限测度核，$U_\kappa$ 的显式展开及证明见附录E.2。常数仅依赖κ，对全部正三层物理谱形状统一；局部双侧界限于所列邻域，两个最优常数无须相等或等于核TV。下一小节固定输入支撑后同时控制时长与失谐。

### 4.2 固定输入时长与联合峰比界

固定第3.1节一个模型及κ。令 $\mathcal F_{1,T}$ 为全部非零实L1、支撑包含于 $[0,2T]$ 的输入，$\mathcal F_{C^1,T}$ 为其中全轴C1子类；无额外幅值或导数上限。记 $\mathcal K_{1,T}(r)$、$\mathcal K_{C^1,T}(r)$ 为两类输入的完整峰比上确界。每次取上确界均先固定模型、r和κ，两状态共用每一条输入。

**任何固定时长均有限，含精确临界。** 对每个T>0，在 $r\in[1/2,3/2]$ 上，全部允许输入的完整峰比均受一个固定模型相关的时长上界控制。附录F用基准输出的完整自由尾控制证明这一点，不要求输入平滑。因此，第3节同一模型的任意大峰比必须允许支撑跨度无共同有限上限，不能只在固定时长内改变波形来实现。

**充分时长以上的联合双侧阶。** 用附录E.4的原模型常数，定义 $T_{\rm env}=E_{\rm env}/A_{\rm env}>0$、$T_0=2E_{\rm env}/B_{\rm env}>0$、$\tau=T/T_{\rm env}$。存在只依赖这个固定模型及κ的正有限常数 $c_-,c_+$，使

$$c_-\,\Psi(\tau,\delta)
\le\mathcal K_{C^1,T}(r)\le\mathcal K_{1,T}(r)
\le c_+\,\Psi(\tau,\delta),\qquad
r\in[1-\eta_\kappa,1+\eta_\kappa],\quad T\ge T_0,\qquad
\Psi(\tau,\delta)=
\begin{cases}
\min\{\tau,\delta^{-1}\},&\delta>0,\\
\tau,&\delta=0.
\end{cases}\tag{13}$$

对这个已固定的模型，最坏峰比同时受“输入能持续多久”和“离精确抵消有多远”两个尺度限制，其量级由两者较小的一个控制。精确抵消时可随允许时长增长而无界；固定一个非零偏差后，延长输入仍受失谐上限约束。

下界来自每个r/T的一条设计输入，上界覆盖全类；两输入类只作双侧常数夹逼，不要求其最优值相同。常数和时长尺度保留模型依赖，式（13）不外推到T<T₀，也不提供必要最短时长或每条实际波形的放大倍数。详证见附录F。

### 4.3 单位三层的六时长采样展示

本节沿用既有六时长采样，未测得最优峰比或认证联合界的最优系数。

单位模型提供一个数值展示：取 $m_j=k_j=1$，则 $M=I_3$、$C_\zeta=2\zeta K^{1/2}$，$\lambda_i$ 为 $\lambda^3-5\lambda^2+6\lambda-1$ 的三个有序正根，分别位于 $(0,1/2)$、$(1,2)$、$(3,4)$。其 $\Omega_*\approx3.4939592074$ rad/s、$\zeta_*\approx0.2606565149$；取κ=8/5时 $\zeta_1\approx0.4170504238$、$N_{\zeta_1}(\mathrm iS)=-39/25$、$|H_1(\mathrm iS)|\approx0.0011047149466$。小数及高精度残差只作一致性核对，不代替精确参数定义。

对上述单位模型，预定六个半时长 $T=20,40,80,160,320,640$ s，两个状态在每个 $T$ 下采用式（8）的同一连续输入、零初始且不归一化。输入精确分解为三个谐波，模态响应由三频解析项及满足零初始的齐次项求出；关断后按解析自由衰减计算。表1及图2展示0.01 s网格上覆盖输入段和关断后300 s的采样峰。

表1　单位三层真实顶层弹性剪力的有限包络展示（合成模型一致单位）

| 半时长T/s | 输入支撑2T/s | 基准采样峰 | 新态采样峰 | 采样峰比 |
|---:|---:|---:|---:|---:|
| 20 | 40 | 2.085558e−4 | 1.124393e−3 | 5.39133 |
| 40 | 80 | 4.256295e−5 | 1.108226e−3 | 26.03734 |
| 80 | 160 | 1.955777e−5 | 1.105584e−3 | 56.52911 |
| 160 | 320 | 9.722021e−6 | 1.104928e−3 | 113.65210 |
| 320 | 640 | 4.858602e−6 | 1.104765e−3 | 227.38323 |
| 640 | 1280 | 2.429118e−6 | 1.104725e−3 | 454.78436 |

六组峰均在输入段内，关断后300 s以外的余尾上界在两状态分别不超过约 $5.162\times10^{-20}$ 和 $4.143\times10^{-29}$。仅T640另在同一连续输入上以0.005 s网格评价，所报两峰及比值在记录精度下不变；网格间连续极值未作区间认证，解析响应公式也不等于解析求得连续峰。六点只作数值展示，式（9）承担无界证明。数据与方法见[六时长报告](../research/roles/experiments/round-010-unit-topcut-envelopes.md)及[冻结六行数表](../experiments/round010_unit_topcut_envelopes/six_envelope_sampled_peaks.csv)。

![图2　单位三层真实弹性顶层剪力的六时长包络展示](<E:/11-工作/001-workbuddy spaceV1/001-workbuddy space/109-论文写作/01-lunwen/papers/damping-output-boundaries/experiments/figures-physical-topcut/fig08_physical_topcut_envelope_peaks.png>)

图2　固定单位三层模型的真实顶层弹性剪力。阻尼比为0.2606565→0.4170504，每个半时长T下两状态输入相同、支撑为2T，峰值按表1的完整采样及余尾口径评价。左图为两状态采样绝对峰，右图为比值；比值增长主要来自基准峰减小，新态峰保持约 $1.10\times10^{-3}$。连线仅引导视线，六点不代替解析证明。本图不是附录B的5%→8%模型，纵轴为合成模型一致单位。[SVG矢量源](../experiments/figures-physical-topcut/fig08_physical_topcut_envelope_peaks.svg)。

## 5 先例、实现范围与结论

### 5.1 已有结果与候选贡献

Richiedei等讨论模态常数的符号和输入、测量点对反共振的影响[1]。Rath与Awtar的两自由度分类含本文共同阻尼所对应的参数特例[2]；其三自由度正式论文在相应分类中采用一个刚体模态和两个柔性模态[3]，与本文三正频率剪切链按各自前提对照。Hoagg等在三质点非共点力到位移传递中已有三次分子及复非最小相位零点例子；其正参数相邻弹簧/阻尼串联拓扑下，点力到单坐标位移的无闭右半平面零点定理，也须按输入、输出和拓扑原条件使用[7]。本文的分布基底输入、截面位移差输出及通常稠密的经典阻尼不等于上述专门拓扑。

卷积估计、peak gain、冲激核L1范数与稳定双边算子均为已有工具[4–6]。本文要比较的是同一结构两个阻尼状态的输出商，并进一步跨模型求仅依赖κ的保证；单模型输入/输出增益不自动完成该比较。这里给出所列物理模型类的显式统一估计；一般逆滤波与零点趋近虚轴的灵敏性机制不作为新原理，同条件覆盖仍待核查。三质点非最小相位或三次分子本身不能作为本稿的新颖性。本轮文献记录已补得L035作者公开两页正文解析及L026作者上传全文网页的关键段定位，不能继续笼统写成三篇均未见正文。L035精确积分常数/分支及L026精确公式版面、版本和其余等价推论仍待核；L034仍缺可核全文。单系统BIBO积分、外力到解耦误差的峰值增益与本文两阻尼输出峰比须按定义和常数依赖分别比较，当前不据相关定位裁定等价覆盖或首创。历史缺口见[全文核对清单](../research/roles/literature/fulltext-request-list.md)，新增获取状态见[L035定位](../research/roles/literature/theory-round001/prior-art-note.md)与[L026定位](../research/roles/literature/theory-session002/L026-comparison-001.md)；本文不从上述尚未完成视觉复核的文献段落转录精确公式，不使用“首次”或“最优”作为已核实结论。

### 5.2 理想黏滞网络及工程边界

对附录B的 $M=I$、$k=(1,1,L)$ 模型族，任意有限L>0的 $C_\zeta=2\zeta\sqrt K$ 可由六条严格正的理想黏滞支路实现：三个楼层两两连接，以及三个楼层各连到同一个共同移动基底。系数由矩阵平方根精确定义，适用于未知小数的 $L_*$，不用移借单位模型的数值系数。附录D给解析证明。

网络含非相邻1↔3连接；本结论不保证只用相邻层器件实现，不推广任意质量矩阵，也不包含实际装置路由、行程和施工设计。报告输出仍为弹性剪力，未将新网络跨截面的黏滞力加到同一个输出中。模型可实现性、固定天然记录的响应和实际建筑危险程度是不同问题。

### 5.3 结论

1. 对固定实输出、共同模态阻尼、同一紧支撑实L1输入及零初始，至多两个有效模态存在仅依赖阻尼倍率的有限完整峰值界；本文给出的 $B(\kappa)$ 保守，未证明最优。基准输出允许非最小相位，稳定双边实现要求使用完整时程。
2. 对每组正m/k三层剪切链的真实顶层弹性剪力，在其谱定义的ζ*→κζ*路径上，每个固定κ>1均有无界完整峰比的共同有限输入族。这确定了破坏所有有限κ-only保证的最少有效模态数为3；在本文逐层单自由度完整链内最少层数亦为3。另有隐式定义的固定模型在精确5%→8%之间达到该结论，其谱函数在固定族 $L\ge1$ 严格下降，根在该半轴唯一；这不认证任何有限小数为精确模型。该指定族对每个 $0<\varepsilon\le\zeta_*(1)$ 有唯一目标模型，刚度比满足式（10）的渐近成本，未给有限误差或跨模型最优设计。
3. 无界比值不等于绝对输出无界，也不意味着每个失谐模型失界。每个固定非临界阻尼对仍有限；在式（11）的局部域内，两输入类的最优峰比均被显式κ-only常数乘以 $1/\delta$ 双侧控制，靠近临界的参数族可出现任意大但逐对有限的比值。固定模型的输入支撑有共同有限上限时，即使精确临界也有有限峰比界；在充分时长以上，两个同支撑输入类的最坏峰比满足式（13）的时长—失谐联合双侧阶，常数依赖模型。单位模型六时长数值仅展示该机制，不替代全时刻证明，更不代表5%→8%的数值工程案例。

本文优先闭合上述理论问题。真实双塔工程观察、探索拟合、高频消阶、输入缩幅与紧性支线保留在[原工作稿v009](working-draft-v009.md)及其冻结证据中；它们不承担本稿核心定理的证明。剩余重点是同条件先例核对与保守常数的学术定位，之后再选择投稿格式。


## 附录 A 双模态完整峰值界的证明

以下给出式（3）的核范数证明，分别处理固定系统、输入空间与完整时间域。核引理的标量锐性与整个乘积界的最优性分别评价。

### A.1 对象、输入空间与完整时间域

取两个不同正固有频率 $\omega_1,\omega_2$，实留数 $r_1,r_2$ 不全为零，固定质量、刚度、输入分布及实线性位移或恢复力输出。两状态各模态阻尼比共同取 $0<\zeta_0\le\zeta_1$，记 $\kappa=\zeta_1/\zeta_0$。同一实输入 $f\in L^1(\mathbb R)$ 具有紧支撑，平移时间后令其支撑起于0；两状态初始条件均为零。比较包括全部自由衰减尾段的完整输出。

设两状态因果冲激响应为 $h_0,h_1$。稳定有限维系统给出 $h_k\in L^1\cap L^\infty$，故 $y_k=h_k*f$ 有界且连续，完整时间轴上的上确界与其L∞范数一致。所用命题为

$$\|y_1\|_\infty\le B(\kappa)\|y_0\|_\infty,\qquad B(\kappa)=(2\kappa-1)(3-2/\kappa)^2.\tag{A1}$$

$f=0$时按不等式表述。对非零紧支撑输入及非恒零基准传递函数，$\|y_0\|_\infty>0$，可进一步报告比值。输出的系数保持不变；随阻尼状态变化的阻尼力项与绝对加速度直接项需要各自的完整传递表达。

### A.2 双模态分子的特殊系数关系

令

$$D_{j,k}(s)=s^2+2\zeta_k\omega_js+\omega_j^2,\qquad G_k(s)=\frac{r_1}{D_{1,k}}+\frac{r_2}{D_{2,k}},$$

并定义

$$a=r_1+r_2,\quad b=r_1\omega_2+r_2\omega_1,\quad c=r_1\omega_2^2+r_2\omega_1^2.$$

通分后 $N_k(s)=as^2+2\zeta_kbs+c$，且

$$c=(\omega_1+\omega_2)b-\omega_1\omega_2a.\tag{A2}$$

因此，$a=0$时必有 $b\ne0$ 且 $c/b=\omega_1+\omega_2>0$；$a\ne0$时，若 $c/a>0$，则 $b/a>0$。这些系数关系使两状态分子具有相同次数；若有原点零因子，它在两状态之间共同出现，可先约去。非零虚轴零点在本双模态共同阻尼参数路径中被排除。

取约去公共因子后的有理商

$$\mathcal Q(s)=\frac{G_1(s)}{G_0(s)}=\frac{N_1(s)}{N_0(s)}\prod_{j=1}^2\frac{D_{j,0}(s)}{D_{j,1}(s)}.\tag{A3}$$

该商proper，允许存在右半平面极点，但没有未约去的虚轴极点。后续构造使用稳定双边核；右半平面极点对应反因果分量。

### A.3 二阶标量核的总变差估计

采用经典peak gain/冲激核L1及阶跃响应总变差框架[6]，考虑 $R_{\alpha,\beta}(s)=s/(s^2+2\alpha s+\beta)$。当 $\beta>0,\alpha>0$，记位移因果核为 $g$，则 $R$的普通核为 $g'$。欠阻尼时，令 $\omega=\sqrt\beta$、$\gamma=\sqrt{\beta-\alpha^2}$、$\theta=\arctan(\gamma/\alpha)$、$z=\alpha/\omega=\cos\theta$，有 $g=e^{-\alpha t}\sin(\gamma t)/\gamma$。第一个极值在 $t_* =\theta/\gamma$，其幅值为 $e^{-\alpha t_*}/\omega$；后续极值绝对值以 $\rho=e^{-\pi\alpha/\gamma}$ 递减。计入全部单调段得

$$\|g'\|_1=\frac{2e^{-\alpha t_*}}{\omega(1-\rho)}.$$

由 $\theta\ge\sin\theta$ 及 $\pi\ge2\sin\theta$，分别得到 $\alpha t_*\ge z$、$\rho\le e^{-2z}$，因此

$$\alpha\|g'\|_1\le\frac{2ze^{-z}}{1-e^{-2z}}=\frac{z}{\sinh z}<1.$$

临界阻尼时 $g=t e^{-\alpha t}$，核绝对积分为 $2/(e\alpha)<1/\alpha$。过阻尼时 $g=(e^{-pt}-e^{-qt})/(q-p)$ 非负单峰。将 $g''+2\alpha g'+\beta g=0$ 从0积分到其峰时，利用 $g(0)=0$、$g'(0)=1$ 和峰时 $g'=0$，得到 $2\alpha g_{max}=1-\beta\int_0^{t_*}g<1$。于是三个分支统一满足

$$\|R_{\alpha,\beta}\|_{\mathrm{kernel},1}<\frac1\alpha,\qquad \alpha>0,\ \beta>0.\tag{A4}$$

固定 $\alpha>0$、令 $\beta\downarrow0$但每次仍严格为正时，过阻尼的 $\alpha\|g'\|_1$ 可趋于1。因此标量系数1不能统一再缩小。该锐性属于单核类，三个因子相乘得到的整体峰值常数仍未证明最优。

当 $\beta<0$，令 $d=\sqrt{\alpha^2-\beta}$、$p=d-\alpha>0$、$q=d+\alpha>0$，则

$$R_{\alpha,\beta}=\frac{p}{p+q}\frac1{s-p}+\frac{q}{p+q}\frac1{s+q}.$$

分别选择 $1/(s-p)$ 的反因果核 $-e^{pt}\mathbf1_{t<0}$ 和 $1/(s+q)$ 的因果核 $e^{-qt}\mathbf1_{t\ge0}$。两半轴支撑分开，核绝对积分为

$$\|R_{\alpha,\beta}\|_{\mathrm{kernel},1}=\frac{2}{p+q}=\frac1{\sqrt{\alpha^2-\beta}}.\tag{A5}$$

当 $\beta=0$ 时先约去 $s$，成为 $1/(s+2\alpha)$；本模型的相应分支有 $\alpha>0$，其核范数为 $1/(2\alpha)$。该值与 $\beta\downarrow0$ 时整条慢尾段的L1范数极限不同。若修正系数本身为0，则直接处理恒等因子，避免写成零乘未定义核。

### A.4 分子比与两个模态比的统一常数

$a\ne0$时，令 $\alpha=\zeta_0b/a$、$\beta=c/a$，有

$$\frac{N_1}{N_0}=1+2(\kappa-1)\alpha R_{\alpha,\beta}.\tag{A6}$$

$\beta>0$时，由式（A2）知 $\alpha>0$，式（A4）给该因子的有限测度核总变差不超过 $1+2(\kappa-1)=2\kappa-1$。$\beta<0$时，式（A5）及 $|\alpha|/\sqrt{\alpha^2-\beta}\le1$ 给不超过 $2\kappa-1$；$\beta=0$时共同原点因子约去，得到不超过 $\kappa$；$b=0$时直接为恒等因子。

$a=0$时单独令 $p=(\omega_1+\omega_2)/(2\zeta_0)>0$，得到

$$\frac{N_1}{N_0}=\kappa-(\kappa-1)\frac{p}{s+p}.$$

其核含 $\kappa\delta_0$ 直通原子和连续指数核，总变差为 $2\kappa-1\le2\kappa-1$。该分支的直通系数为 $\kappa$。

每一个模态分母比可写为

$$\frac{D_{j,0}}{D_{j,1}}=1-2\zeta_1\omega_j(1-1/\kappa)R_{\zeta_1\omega_j,\omega_j^2}.$$

式（A4）给其有限测度核总变差不超过 $1+2(1-1/\kappa)=3-2/\kappa$。按式（A3）卷积三个因子，利用总变差次乘性得到

$$\|q\|_{\mathrm{TV}}\le(2\kappa-1)(3-2/\kappa)^2=B(\kappa),\tag{A7}$$

其中 $q$ 是 $\mathcal Q$ 的稳定双边有限测度核，直通Dirac原子计入总变差。

### A.5 双边卷积恒等式与完整峰值

由于 $q$ 为有限测度且 $h_0\in L^1$，有 $q*h_0\in L^1$。式（A3）的傅里叶恒等式与L1傅里叶唯一性给出 $q*h_0=h_1$。结合卷积结合律和Fubini定理，得到 $y_1=q*y_0$。对 $q=d\delta_0+g(t)\,dt$，$g\in L^1(\mathbb R)$，直接逐点取绝对值有

$$\|q*y_0\|_\infty\le(|d|+\|g\|_1)\|y_0\|_\infty=\|q\|_{\mathrm{TV}}\|y_0\|_\infty.\tag{A8}$$

此处使用经典卷积估计[4]，直通原子另计。与式（A7）合并得到式（A1）。稳定双边实现及其未来信息的作用可与文献[5]的算子框架对照；本证明的具体系数关系及统一常数由式（A2）—（A7）给出。

当 $\kappa=8/5$ 时，$B=539/80=6.7375$。该常数是本推导给出的保守上界，尚未建立最优性，亦不作为某条记录或工程输出的预测值。它控制完整峰值，与谐波幅值或完整L2上界分别报告。

### A.6 完整时间轴与截断同窗

设 $W=[0,T]$，$P_W$ 为零延拓截断算子。双边卷积满足

$$P_W(q*y_0)=P_W\{q*(P_Wy_0)\}+P_W\{q*((I-P_W)y_0)\}.\tag{A9}$$

反因果分量可使第二项含窗口之后的 $y_0$。因此式（A8）的右端使用完整 $\|y_0\|_\infty$，不能仅由该推导将其替换为窗口内峰值。若另取 $\mathcal Q$ 的因果实现，其严格proper部分核为 $g_c$，则因果零初始输出可在有限窗建立

$$\|y_1\|_{\infty,W}\le\left(|d|+\int_0^T|g_c(t)|\,dt\right)\|y_0\|_{\infty,W}.\tag{A10}$$

该常数依赖具体有理商和窗口长度。含右半平面极点时，因果核可以随时间增长；它与式（A7）的稳定双边核采用不同的支撑方向。实际工程导出窗的比较采用其真实时间范围，完整尾段是否受控另行核查。

### A.7 退化、先例与结果强度

| 情形 | 本草案的处理 |
|---|---|
| 两状态阻尼相同 | $\mathcal Q=1$，$B(1)=1$ |
| 单留数为零 | 约为单模态，保守界仍覆盖 |
| 同频 | 合并留数后为单模态；合并为0时按恒零输出处理 |
| 原点公共零因子 | 两状态共同约去，再核查有理商 |
| 非零虚轴未消极点 | 不在本双模态商的结论内；一般多模态另审 |
| 非最小相位基准 | 允许稳定反因果分量，使用完整输出 |
| 非零初始状态 | 增加初始响应项，不能只用输入传递比恒等式 |
| 固定观察窗 | 按式（A9）—（A10）另行计算，不直接移用 $B(\kappa)$ |

Rath与Awtar的两自由度研究[2]已给同号留数和零点位置的分类，并在其Result3式（11）给模态阻尼比区间条件。本文各阶共同阻尼对应该文 $\chi=1$ 的特例。其三自由度正式论文[3]在§3式（6）进入一个刚体模态与两个柔性模态的分类模型；第3.1节三正频率见证采用不同系统前提。两篇原文的输入/输出与刚体模态假设在引用处保留；本文的完整峰值比估计按式（A1）—（A8）给出。

历史同条件粗界为 $(4\kappa-3)(5-4/\kappa)^2$，在 $\kappa=8/5$ 时为21.25；本版采用式（A1）的精化界。代数与核验证包含30个历史核参数、240个有理数系数关系、15个部分分式关系及59个精化标量闭式参数。有限检查支持实现与分支核对，普遍结论由本附录的解析步骤承担。当前最强限制是常数宽松、输入输出类特定、依赖完整时程。

## 附录 B 精确5%→8%阻尼对的物理模型存在性

固定 $M=I_3$、$k_1=k_2=1$、$k_3=L>0$。对应刚度及临界谱函数为

$$K(L)=\begin{pmatrix}2&-1&0\\-1&1+L&-L\\0&-L&L\end{pmatrix},\qquad
q(L)=\frac{D(L)}{4S(L)^3},\quad S(L)=\sum_i\sqrt{\lambda_i(L)},\quad
D(L)=\prod_{i<j}(\sqrt{\lambda_i(L)}+\sqrt{\lambda_j(L)}).\tag{B1}$$

顺序主子式为2、$1+2L$、$L$，故每个有限 $L>0$ 都给正定模型。输入 $f=-a_g$、$b=\mathbf1$，输出为真实顶层弹性剪力 $y=L(u_3-u_2)$。连续对称矩阵族的有序特征值 $\lambda_i(L)>0$ 连续，因而 $q$ 连续。亦可由 $K(L_2)-K(L_1)=(L_2-L_1)vv^T$、$v=(0,1,-1)^T$ 及Weyl界 $|\Delta\lambda_i|\le2|\Delta L|$ 直接得到连续性。

在 $L=1$，$\det K=1$、$\operatorname{tr}K=5$，所以 $\prod_i\omega_i=1$、$\sum_i\omega_i^2=5$。逐对AM–GM给 $D\ge8$，Cauchy给 $S^2\le15$，故 $S^3\le15\sqrt{15}<60$，从而

$$q(1)>\frac8{4\cdot60}=\frac1{30}>\frac1{400}.\tag{B2}$$

在固定二维子空间 $\mathcal W=\{u_2=u_3\}$ 上，取正交基 $e_1,(e_2+e_3)/\sqrt2$，压缩矩阵为
$\begin{pmatrix}2&-1/\sqrt2\\-1/\sqrt2&1/2\end{pmatrix}$，其Ritz值为 $\mu_\pm=(5\pm\sqrt{17})/4$。min–max给 $\lambda_1\le\mu_-$、$\lambda_2\le\mu_+$，因此
$\omega_1+\omega_2\le\sqrt{\mu_-}+\sqrt{\mu_+}=\sqrt{5/2+\sqrt2}<2$。另一方面，$v$ 的Rayleigh商给 $\lambda_3\ge2L+1/2$。利用 $\omega_3(\omega_1+\omega_3)(\omega_2+\omega_3)<S^3$ 得

$$q(L)<\frac{\omega_1+\omega_2}{4\omega_3}<\frac1{2\sqrt{2L+1/2}},\qquad q(20000)<\frac2{4\cdot200}=\frac1{400}.\tag{B3}$$

式（B2）—（B3）及连续性给非空紧集合 $\mathcal Z=\{L\in[1,20000]:q(L)=1/400\}$。定义 $L_*=\min\mathcal Z$，则 $1<L_*<20000$。这个精确选择不依赖 $q$ 单调或根唯一；区间上端也不等于所选根。

固定该 $L_*$ 后，质量、刚度、输入分布、完整模态及输出 $\ell=L_*(0,-1,1)^T$ 全部固定。一般三层分子式（6）中 $c=L_*$，取 $\Omega_*=S(L_*)$、$\zeta_0=1/20$、$\zeta_1=2/25$，则

$$N_{\zeta_0}(\mathrm i\Omega_*;L_*)=0,\qquad
N_{\zeta_1}(\mathrm i\Omega_*;L_*)=-\frac{39L_*}{25}\ne0.\tag{B4}$$

模态分母在此处虚部为 $2\zeta\omega_i\Omega_*>0$；基准传递非恒零。取 $C_\zeta=2\zeta K(L_*)^{1/2}$，两状态及其增量均正定、稳定核一阶绝对矩有限。式（8）—（9）的全时刻包络估计直接适用，故该固定模型在固定5%/8%阻尼对之间具有共同有限输入族的完整峰比无界。两个绝对响应仍受BIBO界控制，输入时长随族增长；结论没有提供实际根值、工程可接受刚度比、固定天然记录或仅相邻层黏滞器实现。

### B.1 固定族在L≥1上的单调性与唯一根

令实际三个正频率的和为S、两两乘积和为R，乘积为 $\sqrt L$。谱不变量给 $S^2=3+2L+2R$、$R^2=1+5L+2\sqrt L S$、$D=SR-\sqrt L$。仅在本小节引入谱参数 $\xi=\sqrt L/S$（不同于失谐比r），令 $z=1/S^2$，则

$$A_\xi=1-2\xi^2,\quad B_\xi=8\xi^2+8\xi+6,\quad
5z^2-B_\xi z+A_\xi^2=0,\qquad 8q=A_\xi-(3+2\xi)z.\tag{B5}$$

实际谱满足 $0<\xi<1/\sqrt2$、$0<z<A_\xi/3\le1/3$；二次式顶点 $B_\xi/10\ge3/5$，故实际z是较小正根，判别式至少16，且 $B_\xi-10z>0$。这一步不把任意代数分支当实际谱。

记 $K_0=K(0)\succeq0$、$K_0\ne0$、$v=(0,1,-1)^T$。对 $L_2>L_1>0$，

$$\frac{K(L)}L=vv^T+\frac{K_0}L,\qquad
\frac{K(L_1)}{L_1}-\frac{K(L_2)}{L_2}
=\left(\frac1{L_1}-\frac1{L_2}\right)K_0\succeq0.\tag{B6}$$

差的迹严格正；min–max使有序特征值逐项不增且至少一项严格下降。因此 $S/\sqrt L=\operatorname{tr}\sqrt{K(L)/L}$ 严格下降，其正倒数 $\xi(L)$ 严格增加且连续，不需声称每阶频率相对增长率有序。

沿较小根分支，$z'=[(16\xi+8)z+8\xi A_\xi]/(10z-B_\xi)<0$。令 $d(\xi)=8q$，求导并用二次关系化简得

$$d'(\xi)=\frac{\mathcal N(\xi,z)}{B_\xi-10z},\quad
\mathcal N=20z^2+(16\xi^2+88\xi+12)z-16\xi^2(2\xi^2+5\xi+1).\tag{B7}$$

$\mathcal N$ 对z严格增加。若 $0<\xi\le1/3$ 且 $L\ge1$，由 $\xi^2=Lz$ 得 $z\le\xi^2$，于是 $\mathcal N(\xi,z)\le4\xi^2(\xi^2+2\xi-1)<0$。若 $\xi\ge1/3$，二次式在 $(1/3,1/12)$ 的值为 $-203/1296<0$，故该处较小根小于1/12，结合 $z'<0$ 得后续z均小于1/12。令 $u=\xi-1/3\ge0$，则

$$\mathcal N(\xi,z)<\mathcal N(\xi,1/12)
=-32u^4-\frac{368}{3}u^3-116u^2-\frac{914}{27}u-\frac{455}{324}<0.\tag{B8}$$

两段覆盖实际 $L\ge1$ 分支；$d'(\xi)<0$ 与 $\xi(L)$ 严格增加复合，证明q在该半轴严格下降。结合原严格端点和连续性，

$$\exists!\ L_*\in[1,\infty):q(L_*)=1/400,\qquad 1<L_*<20000.\tag{B9}$$

原区间最小根定义等于这个唯一根。这里不声称 $L<1$ 的根结构、全正L最小工程刚度或定向数值认证；唯一性不能把有限小数的近似符号与精确零点等同。


### B.2 低阻尼目标的谱极限与指定族参数成本

仍固定 $M=I$、$k=(1,1,L)$。令有序特征值为 $\lambda_1\le\lambda_2\le\lambda_3$。特征多项式及子空间 $u_2=u_3$ 的Ritz压缩给

$$\chi_L(\lambda)=\lambda^3-(3+2L)\lambda^2+(1+5L)\lambda-L,\quad
\mu_\pm=\frac{5\pm\sqrt{17}}4,\quad
0<\lambda_1\le\mu_-,\quad0<\lambda_2\le\mu_+.\tag{B10}$$

因此实际低两谱有界，而不只是降次多项式有两个根。仅本小节记 $t_L=\lambda_1+\lambda_2$、$\pi_L=\lambda_1\lambda_2$。由迹先得 $\lambda_3=2L+O(1)$，再依次用行列式和二阶主不变量得到

$$\pi_L=\frac L{\lambda_3}\to\frac12,\qquad
t_L=\frac{1+5L-\pi_L}{\lambda_3}\to\frac52,\qquad
\lambda_1\to\mu_-,\quad\lambda_2\to\mu_+,\quad
\lambda_3=2L+\frac12+o(1).\tag{B11}$$

低两谱结论由二次根式连续性给出，极限判别式17/4>0；最后一式回代迹，不假定根支路解析。记 $a=\omega_1$、$b=\omega_2$、$d=\omega_3$，则 $a+b\to A_0=\sqrt{5/2+\sqrt2}$、$d\sim\sqrt{2L}$。由精确定义，

$$q(L)=\frac{a+b}{4d}
\frac{(1+a/d)(1+b/d)}{[1+(a+b)/d]^3},\qquad
\lim_{L\to\infty}\sqrt L\,q(L)
=Q_0=\frac{\sqrt{5+2\sqrt2}}8.\tag{B12}$$

q>0，连续平方根给

$$\lim_{L\to\infty}L^{1/4}\zeta_*(L)
=Z_0=\sqrt{Q_0}=\frac{(5+2\sqrt2)^{1/4}}{2\sqrt2}.\tag{B13}$$

结合B.1，$\zeta_*$ 在 $[1,\infty)$ 连续严格下降至0，故恰一一映到 $(0,\zeta_*(1)]$，包括端点ε=ζ*(1)对应Lε=1。ε↓0时Lε→∞，否则某有界子列所在紧域上的正连续ζ*有正下界，矛盾。沿唯一逆映射代入式（B13）得

$$\varepsilon^4L_\varepsilon\longrightarrow Z_0^4=Q_0^2
=\frac{5+2\sqrt2}{64}.\tag{B14}$$

这证明式（10），不以渐近近似替换精确消零模型。每个目标ε先固定Lε后，式（7）仍给 $N_\varepsilon(iS)=0$、$N_{\kappa\varepsilon}(iS)=L_\varepsilon(1-\kappa^2)\ne0$，第3.1节有限输入构造适用；模型不随输入时长变化。本族成本不是所有三层模型的必要成本，未给有限L余项、起效阈值或定向根认证。

## 附录 C 固定失谐界与近临界参数族

固定第3.1节的一组正m/k三层链及κ>1。将式（6）除以正数 $2c\zeta/D$，得

$$p_\zeta(s)=s^3+2S\zeta s^2+S^2s+\frac D{2\zeta},\qquad
\text{Routh首列}:\ 1,\ 2S\zeta,\ S^2-\frac D{4S\zeta^2},\ \frac D{2\zeta}.\tag{C1}$$

当 $0<\zeta<\zeta_*$ 时有两次变号，正系数又排除正实根，故分子有一对右半平面共轭根；$\zeta>\zeta_*$ 时全部分子根在左半平面，约分后剩余零点仍在左半平面；$\zeta=\zeta_*$ 时由式（7）有简单零点 $\pm\mathrm iS$。各模态分母始终严格稳定，约分不能消去右半平面或临界虚轴零点。这些是输出零点分类。

记 $\Delta_\zeta(s)=\prod_i(s^2+2\zeta\omega_i s+\lambda_i)$。若固定 $\zeta_0>0$ 且 $\zeta_0\ne\zeta_*$，则

$$Q(s)=\frac{H_{\kappa\zeta_0}}{H_{\zeta_0}}=
\frac{N_{\kappa\zeta_0}}{N_{\zeta_0}}\frac{\Delta_{\zeta_0}}{\Delta_{\kappa\zeta_0}},
\quad Q(\infty)=\kappa,\quad
q=\kappa\delta_0+g(t)\,dt,\quad g\in L^1(\mathbb R).\tag{C2}$$

每个 $H_\zeta$ 的相对阶为3，故 $Q$ 为biproper；基准分子及新模态分母无虚轴根，约分后亦无虚轴极点。按部分分式将左半平面极点取因果项、右半平面极点取反因果项，得到式（C2）的稳定双边有限测度；重复离轴极点只附可积指数多项式。由Fourier唯一性和卷积结合律，同一紧支撑实L1输入的完整输出满足

$$y_1=q*y_0,\qquad
P_1\le\|q\|_{\rm TV}P_0=(\kappa+\|g\|_1)P_0.\tag{C3}$$

常数依赖模型和固定阻尼对，未证明最优，亦不能直接用于同一截断窗。仅新态 $\kappa\zeta_0=\zeta_*$ 不妨碍该有限界；基准精确临界时，式（7）中新分子非零，未消去虚轴极点与第3.1节无界输入族对应。κ=1时另有 $Q\equiv1$。

令 $r=\zeta_0/\zeta_*\ne1$，在 $\Omega=S$ 处

$$|Q(\mathrm iS)|=
\frac{|1-\kappa^2r^2|}{|1-r^2|}
\frac{|\Delta_{\zeta_0}(\mathrm iS)|}{|\Delta_{\kappa\zeta_0}(\mathrm iS)|}.\tag{C4}$$

对固定κ>1，后一个因子在 $r\to1$ 时趋于正有限值，所以同频比按 $1/|r-1|$ 发散。对每个固定失谐参数，足够长有限包络可使峰比下估计逼近该同频比，故能任意接近临界的参数集合一般没有统一有限常数；每个固定非临界对本身仍有限。这里先改变参数再选择输入，不是同一失谐对无界，本段同频推导本身不提供最优完整峰界的双侧阶；该加强结果另见附录E，仍不提供工程误差容限。

## 附录 D 正黏滞网络的解析实现

本附录限 $M=I$ 与附录B的 $K(L)$，L>0。令 $R(t)=(K+tI)^{-1}$，t≥0。其分母为

$$d(t)=t^3+(3+2L)t^2+(1+5L)t+L>0.$$

伴随矩阵的上三角依次为 $t^2+(1+2L)t+L$、$t+L$、L、$(t+2)(t+L)$、$L(t+2)$、$t^2+(3+L)t+1+2L$，全部严格正，因此R逐项严格正。记J为K的唯一对称正定平方根，由正谱上的标量积分有

$$J=\frac1\pi\int_0^\infty t^{-1/2}K(K+tI)^{-1}\,dt.\tag{D1}$$

矩阵积分在0端为 $O(t^{-1/2})$，∞端为 $O(t^{-3/2})$，绝对收敛。由KR=I−tR，对i≠j有

$$J_{ij}=-\frac1\pi\int_0^\infty t^{1/2}R_{ij}(t)\,dt<0.$$

改写后非对角被积函数在0端为 $O(t^{1/2})$、∞端为 $O(t^{-3/2})$，仍绝对收敛。又 $K\mathbf1=e_1$、KR=RK，给

$$J\mathbf1=\frac1\pi\int_0^\infty t^{-1/2}R(t)e_1\,dt>0\quad\text{（逐分量）}.\tag{D2}$$

这里利用特定K的resolvent和行和性质，未把一般SPD平方根误认成逐项正矩阵。取C=2ζJ，定义 $c_{ij}=-C_{ij}>0$、$g_i=(C\mathbf1)_i>0$，逐项核对得到

$$C=\operatorname{diag}(g)+\sum_{i<j}c_{ij}(e_i-e_j)(e_i-e_j)^T,\quad
v^TCv=\sum_i g_i v_i^2+\sum_{i<j}c_{ij}(v_i-v_j)^2>0\ (v\ne0).\tag{D3}$$

这恰是三条层间及三条共同接基底的被动黏滞支路；特别 $c_{13}>0$。增加ζ使全部六个系数同比增加。固定L=L*时，上述积分直接给精确器件定义，无需浮点根值或单位例系数。

设绝对位移为x，共同移动基底位移为q_g，$u=x-\mathbf1q_g$。层间速度差为 $\dot u_i-\dot u_j$，接基底速度差为 $\dot u_i$。由于g=C1，绝对坐标阻尼力 $C\dot x-g\dot q_g=C\dot u$，弹簧恢复力为Ku，故

$$M\ddot u+C\dot u+Ku=-M\mathbf1\ddot q_g.\tag{D4}$$

没有新增基底速度输入。若将某支路改接惯性固定地，该等价不再自动成立。被动支路耗散非负也不表示有外部基底输入时机械能单调下降。完整审核来源见[网络解析证明](../research/roles/verification/network-realizability-proof.md)。


## 附录 E 显式失谐界、局部双侧阶与有限包络

### E.1 归一化与逐固定对的根式界

沿第3.1节模型，令 $a=2\zeta_*$、$x=s/S$、$r=\zeta_0/\zeta_*$。AM–GM给 $0<a^2=D/S^3\le8/27$。归一化分子与其比为

$$p_r(x)=x^3+arx^2+x+a/r,\quad N_{\zeta_0}(Sx)/c=(r/a)p_r(x),\quad
V_r(x)=\kappa+\frac{(\kappa-1)(a/r)(\kappa r^2x^2-1)}{p_r(x)}.\tag{E1}$$

记 $A_\kappa=(3-2/\kappa)^3$。三个机械分母比分别用附录A标量核界控制，其核TV均不超过 $3-2/\kappa$，所以 $\|q_r\|_{\rm TV}\le A_\kappa\|v_r\|_{\rm TV}$。该拆分覆盖机械共极点、新态临界及过阻尼，避免将相碰机械极点的简单留数逐项估计。

记 $F_r=V_r-\kappa$，对 $p_r$ 的不同根λ及重数 $m_\lambda$，以高阶部分分式写 $F_r=\sum_{\lambda,\ell}A_{\lambda,\ell}(x-\lambda)^{-\ell}$，其中

$$A_{\lambda,\ell}=\left.
\frac1{(m_\lambda-\ell)!}\frac{d^{m_\lambda-\ell}}{dx^{m_\lambda-\ell}}
[(x-\lambda)^{m_\lambda}F_r(x)]\right|_{x=\lambda},\quad
\mathcal K_1(r)\le A_\kappa\left[\kappa+
\sum_{\lambda}\sum_{\ell=1}^{m_\lambda}
\frac{|A_{\lambda,\ell}|}{|\operatorname{Re}\lambda|^\ell}\right].\tag{E2}$$

$r\ne1$ 时无虚轴根；半轴指数多项式核的L1范数为 $|\operatorname{Re}\lambda|^{-\ell}$，尺度S及阶乘在积分中抵消。直接项为 $\kappa\delta_0$。式（E2）是给定根/系数后的数学保守表达式，包含双根；未经定向舍入求根代入不构成区间证书。三重根会迫使 $a^2=1/3>8/27$，不在物理谱形状内。

### E.2 局部根关系与统一上界

本节使用与式（12）相同的显式保守常数：

$$C_{0,\kappa}=\frac{36}{7}(\kappa-1)(1+3\kappa/2),\quad
C_{1,\kappa}=\frac{236}{35}(\kappa-1)(1+9\kappa/4),\quad
U_\kappa=A_\kappa\left[\frac{\kappa+C_{0,\kappa}}2+C_{1,\kappa}\right].\tag{E3}$$

下述TV上界取 $0<\delta\le1/2$，r=1不使用该有限测度界。在 $r\in[1/2,3/2]$，$(ar)^2\le2/3$、实轴上 $p_r'\ge7/9$。故恰有一个负实根−u和非实共轭对，写 $p_r=(x+u)(x^2+vx+w)$、$\lambda_\pm=-v/2\pm i\beta$。比较系数给

$$u+v=ar,\quad w+uv=1,\quad uw=a/r,\quad
v(1+u^2)=a(r-1/r),\qquad a/2\le u\le2a,\quad
ar/u,\ ru/a\le9/4.\tag{E4}$$

u在ar和a/r之间，由严格递增的 $u^3-ar u^2+u-a/r$ 在两端异号得到。进一步有

$$\beta^2=1-(ar)^2/3+(u-v/2)^2/3\ge7/9,\quad
|p_r'(-u)|\ge7/9,\quad |p_r'(\lambda_\pm)|\ge14/9,\quad
|v|\ge\frac{5a\delta}{3(1+4a^2)}.\tag{E5}$$

令 $R_0,R_\pm$ 为 $F_r$ 的三个简单留数。式（E4）—（E5）给实根核项和共轭核项

$$\frac{|R_0|}{u}\le\frac{36}{7}(\kappa-1)
(1+81\kappa a^2/16)\le C_{0,\kappa},\quad
|R_\pm|\le\frac{9a}{7}(\kappa-1)(1+9\kappa/4),\quad
\frac{4|R_+|}{|v|}\le\frac{C_{1,\kappa}}{\delta}.\tag{E6}$$

关键是共轭留数也带a，抵消离虚轴距离中的a；用 $a^2\le8/27$ 后，常数对全部正三层谱形状统一，不要求a远离0。由直接原子、三角不等式和 $\delta\le1/2$，

$$\|q_r\|_{\rm TV}\le A_\kappa
\left(\kappa+C_{0,\kappa}+\frac{C_{1,\kappa}}{\delta}\right)
\le U_\kappa/\delta.\tag{E7}$$

### E.3 下界与原L1输入类桥接

每固定失谐对，沿式（8）的同一实C1包络令时长增大，全时刻误差给 $\mathcal K_{C^1}\ge|Q(iS)|$。每个机械分母比幅值至少 $1/\kappa$；当 $0<\delta\le\eta_\kappa$，有 $\kappa r\ge(\kappa+1)/2$、$|1-r^2|\le5\delta/2$，所以

$$\mathcal K_{C^1}\ge
\frac{|1-\kappa^2r^2|}{|1-r^2|}\prod_i
\frac{|\omega_i^2-S^2+2i\zeta_0\omega_iS|}
{|\omega_i^2-S^2+2i\kappa\zeta_0\omega_iS|}
\ge\frac{(\kappa-1)(\kappa+3)}{10\kappa^3\delta}
=\frac{L_\kappa}{\delta}.\tag{E8}$$

对任意原实紧支撑L1输入，稳定严格真系统的核属于 $L^1\cap C_0$，故输出连续有界且属L1。非恒零有理基准传递及Fourier唯一性保证非零输入的 $P_0>0$；商核有限测度给 $y_1=q_r*y_0$ 及 $P_1\le\|q_r\|_{\rm TV}P_0$，不要求L1输入本身有界。C1包络是该输入类的子类，已经满足幅≤1；共同平移不改完整峰比。因此

$$L_\kappa/\delta\le\mathcal K_{C^1}(r)\le\mathcal K_1(r)
\le\|q_r\|_{\rm TV}\le U_\kappa/\delta.\tag{E9}$$

这里不证明两最优常数相等或等于TV；下界逼近时长可依赖模型和r。局部邻域排除新态恰临界的 $\kappa r=1$，全域根式上界仍允许该点；$r=1$ 则回到原无界构造，κ=1另为相同状态。所得阶数不是相邻两参数实际峰比翻倍律，也不是固定天然波或设备误差容限。


### E.4 有限包络与失谐的联合下界

固定正m/k三层模型、真实弹性topcut及κ，取 $I=[1-\eta_\kappa,1+\eta_\kappa]$。本小节 $H_0=H_{r\zeta_*}$、$H_1=H_{\kappa r\zeta_*}$。令 $\zeta_-=(1-\eta_\kappa)\zeta_*>0$、$\zeta_+=\kappa(1+\eta_\kappa)\zeta_*$，则两状态阻尼均在此固定紧区间。由 $S>\omega_i$ 和式（6），可取

$$D_-=\prod_i(S^2-\omega_i^2),\quad
D_+=\prod_i\sqrt{(S^2-\omega_i^2)^2+(2\zeta_+\omega_iS)^2},\quad
A_{\rm env}=\frac{c(2+\eta_\kappa)}{D_-},\quad
B_{\rm env}=\frac{c(\kappa-1)(\kappa+3)}{4D_+}.\tag{E10}$$

这些量严格正。因 $D_-\le|\Delta_\zeta(iS)|\le D_+$、$|1-r^2|\le(2+\eta_\kappa)\delta$ 及 $\kappa r\ge(\kappa+1)/2$，在整个I有 $|H_0(iS)|\le A_{\rm env}\delta$、$|H_1(iS)|\ge B_{\rm env}$，没有把新态同频零点κr=1纳入域内。

统一核矩须跨过临界阻尼。单模态位移核满足 $|g_{\zeta,\omega}(t)|\le t e^{-d(\zeta)\omega t}$：欠阻尼用 $|\sin x|\le|x|$，临界核恰为 $te^{-\omega t}$，过阻尼用 $\sinh(bt)/b\le te^{bt}$，其中 $d(\zeta)=\zeta$（ζ≤1）或 $\zeta-\sqrt{\zeta^2-1}$（ζ≥1）。于是可统一取

$$\gamma=\min\left\{\zeta_-,
\frac1{\zeta_++\sqrt{\max\{\zeta_+^2-1,0\}}}\right\}>0,\qquad
m_\zeta=\int_0^\infty t|h_\zeta(t)|\,dt
\le2\gamma^{-3}\sum_i\frac{|\rho_i|}{\omega_i^3}
=:M,\quad E_{\rm env}=\pi M/2.\tag{E11}$$

若ζ+<1，第二候选值大于1，故γ=ζ−；若ζ+≥1，过阻尼d递减，在ζ+最小。全区间因此均有d≥γ。式（E11）由 $h_\zeta=\sum_i\rho_i g_{\zeta,\omega_i}$ 及 $\int_0^\infty t^2e^{-\alpha t}dt=2/\alpha^3$ 得到，对两个状态和全部r统一；非零传递保证M>0。这不依赖欠阻尼公式中的奇异分母。

取全轴零延拓的 $a_T(t)=\sin^2(\pi t/(2T))$（$0\le t\le2T$），其余为0。因 $H_1(iS)\ne0$，可取

$$\theta_{T,r}=-ST-\arg H_1(iS),\qquad
f_{T,r}(t)=a_T(t)\cos(St+\theta_{T,r}),\qquad
\operatorname{Lip}(a_T)=\pi/(2T).\tag{E12}$$

每个输入非零、实C1、幅≤1、支撑[0,2T]；不同r可换相位，但两状态共用该r、T的同一输入。由全轴Lipschitz估计，对所有实t，

$$y_j(t)=\operatorname{Re}\!\left[e^{i(St+\theta_{T,r})}
\{a_T(t)H_j(iS)+R_j(t)\}\right],\quad
|R_j(t)|\le\frac{\pi m_j}{2T}\le\frac{E_{\rm env}}T,\quad
P_0\le A_{\rm env}\delta+\frac{E_{\rm env}}T,\quad
P_1\ge B_{\rm env}-\frac{E_{\rm env}}T.\tag{E13}$$

余项界来自 $\int|h_j(s)|\,|a_T(t-s)-a_T(t)|ds$，覆盖t>2T的全部自由尾段。新态仅在中心t=T取下界，相位使主项为正实数，未把复幅值无条件当实峰。基准非恒零有理传递及Fourier唯一性仍保证P₀>0，即使r=1亦然。

对每个r∈I、每个 $T\ge T_0=2E_{\rm env}/B_{\rm env}$，式（E13）给有量纲下界

$$\frac{P_1(T,r)}{P_0(T,r)}
\ge\frac{B_{\rm env}}{2(A_{\rm env}\delta+E_{\rm env}/T)}.\tag{E14}$$

$A_{\rm env},B_{\rm env}$ 有传递幅值单位、$E_{\rm env}$ 多一个时间单位；令 $T_{\rm env}=E_{\rm env}/A_{\rm env}$、$\tau=T/T_{\rm env}$、$C_{\rm env}=B_{\rm env}/(2A_{\rm env})$ 后，

$$\frac{P_1}{P_0}\ge\frac{C_{\rm env}}{\delta+1/\tau}
\ge\frac{C_{\rm env}}2\min\{\tau,\delta^{-1}\},\qquad T\ge T_0.\tag{E15}$$

δ=0时第一下界直接为Cenv τ，第二式采用δ⁻¹=∞约定；δ>0时由 $\delta+1/\tau\le2\max\{\delta,1/\tau\}$ 得到。r可随T变化但留在同一I，统一矩使此联合量词成立；T₀依赖固定模型与κ，不是κ-only通用秒数。τ≥1/δ只是使该证书达到Cenv/(2δ)的充分条件，本节设计包络论证本身只给下界；全类上界和联合双侧阶另见附录F，仍不提供必要最短时长。上述均为解析保守常数，不是已作定向舍入的数值证书。

## 附录 F 固定时长完整峰比与联合界

### F.1 临界附近的有界分子比核

固定第3.1节物理模型及κ。沿用附录E归一化，先取较大的紧域 $I_0=[1/2,3/2]$。由 $p_r'(x)\ge7/9$（实x），三次式恰有一个负实根和一对非实共轭根，均简单；非实重根连同共轭至少需四次。根及简单留数可按负实根与正/负虚部在I₀连续标记。这里a和模型已固定，所以紧域上的留数和有有限上界。

对r≠1，分子比 $V_r(s/S)$ 的离轴根取稳定半轴核；r=1时，对±iS取因果有界振荡核，负实根仍取衰减核。归一化简单留数为 $R_\lambda$ 时，其s变量普通核项为 $\pm S R_\lambda e^{S\lambda t}$ 乘相应半轴指示，幅不超过 $S|R_\lambda|$。于是

$$v_r=\kappa\delta_0+g_{v,r}(t)\,dt,\qquad
M_v:=\sup_{r\in I_0}\|g_{v,r}\|_\infty
\le S\max_{r\in I_0}\sum_\lambda|R_\lambda(r)|<\infty.\tag{F1}$$

共轭配对使普通核实。临界时仅要求g有界，不声称v是有限TV测度或在r上L1连续；半轴切换不影响上述幅界。

令 $\mu_r$ 为三个机械分母比 $B_i(s)=(s^2+2\zeta_0\omega_i s+\omega_i^2)/(s^2+2\kappa\zeta_0\omega_i s+\omega_i^2)$ 的乘积核，因果且 $\|\mu_r\|_{\rm TV}\le A_\kappa$；设 $z=\mu_r*y_0$。非临界时由稳定双边Fourier恒等式有 $y_1=v_r*z$。临界时z为实际因果L1输出，在 $\operatorname{Re}s>0$，精确有

$$V_1(s/S)\left(\prod_iB_i(s)\right)H_0(s)\widehat f(s)
=H_1(s)\widehat f(s).\tag{F2}$$

v₁的普通部分虽仅有界，仍可与z∈L1绝对卷积；加权Fubini和Laplace唯一性给相同身份。这里z必须来自实际基准输出像空间，不把任意L1信号送入临界振荡核都当作真实新状态输出。有限测度、L1输出与有界普通核的重排由 $M_v\|\mu_r\|_{\rm TV}\|y_0\|_1$ 控制，故

$$\|z\|_\infty\le A_\kappa P_0,\quad
\|z\|_1\le A_\kappa\|y_0\|_1,\qquad
P_1\le A_\kappa\{\kappa P_0+M_v\|y_0\|_1\}.\tag{F3}$$

新态机械临界、过阻尼或共极点仍由三个因子的测度界处理。

### F.2 完整自由尾控制与所有有限时长输入的上界

非零实L1输入支撑包含于[0,2T]。在模态状态 $X_0=(q_i,\dot q_i)_i$ 中，停止输入后有 $y_0(2T+s)=C_y e^{A_0(r)s}X_0(2T)$。真实topcut留数 $\rho_i=(\ell^T\phi_i)\Gamma_i$ 全非零，故每阶输出投影均非零。又 $\zeta_*^2\le2/27$ 给基准阻尼始终欠阻尼，六个机械极点互异；它们与传递零点±iS不同。PBH条件因此给六维对 $(C_y,A_0(r))$ 可观测。

固定观测时长 $\tau_{\rm obs}>0$，不随T或r改变。Gramian正定且随r连续，紧I₀给

$$0<\zeta_*/2\le\zeta_0\le1/\sqrt6<1,\qquad
W(r)=\int_0^{\tau_{\rm obs}}e^{A_0(r)^Ts}C_y^TC_y e^{A_0(r)s}\,ds,\quad
w_*=\min_{r\in I_0}\lambda_{\min}W(r)>0.\tag{F4}$$

完整P₀控制停止输入后这段未来响应，故 $X_0(2T)^TW(r)X_0(2T)\le\tau_{\rm obs}P_0^2$。基准机械系统在I₀一致指数稳定：固定正谱和正阻尼下界、统一欠阻尼间距允许取模型相关 $M_{\rm tail},\gamma_{\rm tail}>0$，使

$$\|X_0(2T)\|\le\sqrt{\tau_{\rm obs}/w_*}\,P_0,\quad
\|C_y e^{A_0(r)s}\|\le M_{\rm tail}e^{-\gamma_{\rm tail}s},\quad
C_{\rm tail}=\frac{M_{\rm tail}}{\gamma_{\rm tail}}
\sqrt{\tau_{\rm obs}/w_*}<\infty.\tag{F5}$$

即使输入本身无界，L1受迫状态仍连续、局部绝对连续，停止后齐次演化成立。对尾部积分，再加输入段的直接估计，得到

$$\int_{2T}^\infty|y_0(t)|\,dt\le C_{\rm tail}P_0,\qquad
\|y_0\|_1\le(2T+C_{\rm tail})P_0.\tag{F6}$$

这里没有把输出截到2T，也没有从输入L1大小反推P₀。结合式（F3），对全部允许输入，

$$\mathcal K_{1,T}(r)\le
A_\kappa[\kappa+M_v(2T+C_{\rm tail})],
\qquad r\in I_0,\quad T>0.\tag{F7}$$

Mv为时间倒数，Ctail为时间，右端无量纲；常数与T、r及输入无关，但保留固定模型和κ依赖。T=0的非零L1类为空，不在命题内。本证明未数值认证Gramian下界或计算最优系数；固定T上界不能替成同一截断观察窗的上界。

### F.3 共同域、正时长门槛与联合双侧阶

转取 $I_\kappa=[1-\eta_\kappa,1+\eta_\kappa]\subset I_0$，沿用E.4的原跨阻尼矩M及其原时长常数。所有输入类均与第4.2节同支撑，C1子类包含于L1类。记

$$\tau_0=\frac{T_0}{T_{\rm env}}=\frac{2A_{\rm env}}{B_{\rm env}}>0,\quad
C_{\rm env}=\frac{B_{\rm env}}{2A_{\rm env}},\quad
\alpha=A_\kappa(\kappa+M_vC_{\rm tail}),\quad
\beta=2A_\kappa M_vT_{\rm env},\quad
\Lambda_{\rm dur}=\beta+\frac\alpha{\tau_0}.\tag{F8}$$

τ₀Cenv=1，α/β/Λdur均无量纲。式（F7）换元后为 $\mathcal K_{1,T}\le\alpha+\beta\tau$；因τ≥τ₀，才可吸收常数项而得 $\mathcal K_{1,T}\le\Lambda_{\rm dur}\tau$。对δ>0，原L1输入类桥接及式（12）另给Uκ/δ，因此

$$\mathcal K_{1,T}(r)
\le\min\{\Lambda_{\rm dur}\tau,U_\kappa/\delta\}
\le c_+\Psi(\tau,\delta),\qquad
c_+=\max\{\Lambda_{\rm dur},U_\kappa\}>0
\quad(\delta>0,\ T\ge T_0).\tag{F9}$$

δ=0时仅用时长界 $\Lambda_{\rm dur}\tau\le c_+\tau$，不调用除δ的公式。下界由式（E14）—（E15）的每个r/T同支撑实C1设计输入给

$$\mathcal K_{C^1,T}(r)
\ge\frac{C_{\rm env}}{\delta+1/\tau}
\ge c_-\Psi(\tau,\delta),\qquad
c_-=\frac{C_{\rm env}}2>0,\quad
r\in I_\kappa,\ T\ge T_0.\tag{F10}$$

δ=0时原式直接为Cenvτ，比所列较弱下界更强。与类包含及式（F9）合并，证明式（13）。允许r随T在共同域内变化，但每次上确界先固定模型与阻尼对；不是在同一次时程中改变阻尼。上下界各自的像空间、输入支撑和完整尾段一致。c±及T₀/Tenv均有模型依赖，不因Uκ仅依赖κ而消失；T₀是充分门槛而非必要最短时长。这是两类最优峰比的联合同阶，既不要求它们相等，也不等同于任何单条波形的实际增幅。

## 参考文献

[1] Richiedei D., Tamellin I., Trevisani A. Beyond the Tuned Mass Damper: a Comparative Study of Passive Approaches to Vibration Absorption Through Antiresonance Assignment. Archives of Computational Methods in Engineering, 2022, 29:519–544. [DOI](https://doi.org/10.1007/s11831-021-09583-w)，本稿引用§2.2.1—2.2.2、印刷页521—522、式（9）。

[2] Rath S., Awtar S. Non-minimum Phase Zeros of Two-DoF Damped Flexible Systems. IFAC-PapersOnLine, 2021, 54(20):579–585. [DOI](https://doi.org/10.1016/j.ifacol.2021.11.234)，[作者存档全文](https://psdl.engin.umich.edu/pdf/C46.pdf)PDF第3—5页Result1/3/4。文献的留数比符号与本稿阻尼倍率κ分别使用。

[3] Rath S., Awtar S. On the zeros of three-DoF damped flexible systems. Journal of Sound and Vibration, 2023, 560:117698. [DOI](https://doi.org/10.1016/j.jsv.2023.117698)，[公开正式全文](https://par.nsf.gov/servlets/purl/10451384)第3—4页式（4）—（6），注意一个刚体模态加两个柔性模态的分类前提。

[4] Bruna J. Lecture notes, Harmonic Analysis minicourse. 19 April 2016. [公开讲义](https://www.maths.ox.ac.uk/system/files/media/HarmAnLectureNotes.pdf)，印刷第19页/PDF第20页§2.2卷积与Young界，印刷第39—40页/PDF第40—41页Fourier唯一性和Plancherel。有限测度直通项估计在附录A直接写出。

[5] Verwoerd M. H. A. Iterative Learning Control — a critical review. University of Twente博士论文，2005. [大学仓储全文](https://ris.utwente.nl/ws/portalfiles/portal/6036402/thesis_Verwoerd.pdf)，Appendix4.A印刷第96—99页/PDF第112—115页，双边算子及截断映射；原文频域∞范数属于L2诱导范数。


[6] Boyd S., Barratt C. Linear Controller Design: Limits of Performance. Prentice-Hall, 1991. [作者公开全书](https://web.stanford.edu/~boyd/lcdbook/lcdbook.pdf)，印刷第97页§5.2.5式（5.4）—（5.6）和第98页peak gain、冲激核L1及阶跃响应总变差；印刷第99页式（5.9）—（5.10）区分RMS/L2诱导增益。

[7] Hoagg J. B., Chandrasekar J., Bernstein D. S. On the Zeros, Initial Undershoot, and Relative Degree of Collinear Lumped-Parameter Structures. Journal of Dynamic Systems, Measurement, and Control, 129(4):493–502, July 2007. DOI:10.1115/1.2719764。[作者大学全文](https://public.websites.umich.edu/~dsbaero/library/ZerosUndershootASME2007.pdf)，印刷第498页§5三质点复NMP示例，印刷第500页§9式（9.5）—（9.6）及Theorem9.1为正参数相邻弹簧/阻尼拓扑下点力至单坐标位移的零点结果。
