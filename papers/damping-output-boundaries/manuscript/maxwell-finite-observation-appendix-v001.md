# 有限精度六类观测与固定局部峰：条件附录

v001，2026年10月18日；独立短附录，待整合复审。本文只整理[根R019采用的C037](../../../research/sessions/20261017-2109/R019-adoption.json)、[作者R028](../research/roles/ideation/maxwell-session004/R028-finite-observation-neighbor/report.md)与[独审R039](../research/roles/verification/maxwell-session004/R039-finite-observation-neighbor-review/report.md)，不改变compact v003或原C025。

## 1 模型、观测与量词

沿用C025正参数κ、c及α=3/10，M=I，K0=I+0.001[[1,−1],[−1,1]]，D=diag(1,−1)，μ=10⁻⁶，Ka=K0+aD。每条轨迹中a固定不随时间变化，a绝对值≤μ。物理C0=0.1√K0保持，不按Ka重新设各阶5%。端口B_A=e1ᵀ、B_B=e2ᵀ，两布局采用**同一个a**，不是A(a)对B(−a)。共同f=(1,1)ᵀsin(t)仅在0≤t≤T=20π作用，此后为零；u、v、F初态全零。

先给任意有限H≥6T及六个正有限尺度s_i。观测为整段连续标量历史，有限指量种数及窗口，不只指采样点：

$$
\begin{aligned}
O_{L,a}&=(E_{L,a},D_{b,L,a},D_{d,L,a},W_{L,a},F_{L,a},\delta_{L,a}),\\
E_{L,a}&=\tfrac12(u^TK_au+v^Tv+F^2/\kappa),\qquad\delta_{L,a}=B_Lu,\\
D_b(t)&=\int_0^t v^TC_0v\,ds,\quad D_d(t)=\int_0^t p(F)\,ds,
\quad W(t)=\int_0^t v^Tf\,ds.
\end{aligned}\tag{1}
$$

这里δ是含弹簧及黏壶的**总端变形**。记g(x)=sgn(x)(abs(x)/c)^(10/3)，p(x)=xg(x)=c^(−10/3)abs(x)^(13/3)。观测不携带器件实际安装位置的B标签。a=0时原交换给六量精确同史；**非零a只给下面的近邻界，不承诺精确同史**。

## 2 全状态预算与六个常数

令R=40√2、χ=(1−μ)^(−1/2)、θ=√(1+μ)，并用Ka≽(1−μ)I及Ka≼(1+μ)K0。完整储能被动性、输入绝对面积和单调增量耗散分别给全状态及同布局差半径：

$$
\begin{aligned}
N_a(z)^2&=u^TK_au+v^Tv+F^2/\kappa,\quad
N_a(z_{L,a}(t))\le R,\quad N_0(z_L^0(t))\le R,\\
N_a(z_{L,a}-z_L^0)&\le R|a|t,\qquad N_a(z_L^0)\le\theta R.
\end{aligned}\tag{2}
$$

上标0是同一布局的a=0轨迹，不是无装置模型。零能量处先正则化再积分；这些预算并非从局部峰或尾界反推。Ka≽(1−μ)I给位移差≤χR·a绝对值·t，速度差≤R·a绝对值·t，力差≤√κR·a绝对值·t；同布局误差强迫为−aD u_L^0。

储能还随Ka显式改变。逐布局必须保留

$$
\begin{aligned}
E_a(z_a)-E_0(z_0)&=\tfrac12[N_a(z_a)^2-N_a(z_0)^2]
+\tfrac a2u_0^TDu_0,\\
|E_a(z_a)-E_0(z_0)|&\le\tfrac12R^2[(1+\theta)t+1]|a|.
\end{aligned}\tag{3}
$$

不能把两条储能之差当作差状态储能。令C*=∥C0∥₂=0.1√(501/500)、P=√κR。全部轨迹均在abs(F)≤P内；p为C¹，导数绝对值上界Lp=(13/3)c^(−10/3)P^(10/3)有限，零点导数为零。背景功率差≤2C*R²·a绝对值·t，器件功率差≤Lp√κR·a绝对值·t，须分别积分；不能只说状态连续便略过累计量。输入在T后停止，每布局输入功差≤R²T·a绝对值。

再以a=0名义同史连接两布局，得到下表：各观测在[0,H]内的两布局绝对差上确界≤Li(H)乘以**a绝对值**。

| 观测量i | Li(H) |
|---|---|
| 完整机械储能E | R²[(1+θ)H+1] |
| 累计背景耗散Db | 2C*R²H² |
| 累计器件耗散Dd | Lp√κR H² |
| 累计输入功W | 2R²T |
| 器件力F | 2√κR H |
| 总端变形δ | 2χR H |

六常数与a无关，对给定有限H均有限。累计耗散的H²来源是逐时差预算积分；W利用输入有限支持。不能把此表直接取H=∞。

## 3 同一非零a与公共观测记录

按逐量尺度定义距离，并在预给窗口、尺度及η后选择参数：

$$
\|Z\|_s=\max_i\frac{\sup_{0\le t\le H}|Z_i(t)|}{s_i},\qquad
C_{\rm obs}=\max_i\frac{L_i(H)}{s_i}\in(0,\infty),\qquad
a_\eta=\min\{\mu/2,\eta/C_{\rm obs}\}>0.\tag{4}
$$

准确量词是“∀有限H≥6T，∀六个s_i∈(0,∞)，∀η>0，∃同一个非零a_η用于A/B”。于是两观测距离≤η。它不是一个固定非零a适用于所有精度、尺度或窗口；a_η是精确实数，可能小于软件浮点或制造分辨率。

观测合同允许每量任意确定性绝对误差ηs_i，即误差球Bη(O)={Z:∥Z−O∥s≤η}。中间记录Z*=(O_A,aη+O_B,aη)/2到两侧均≤η/2，因此是两球公共记录。Z*不必是另一个真实系统的精确输出；若另加物理一致性、概率或量化器限制，已改变此误差集合，需要另证。

## 4 同一有限窗口峰差及估计器下界

令P_L^H(a)=sup_[0,H]abs(u1,L,a(t))。R039由[已审C033统一界（R034）](../research/roles/verification/maxwell-session004/R034-asymmetric-neighborhood-review/report.md)继承UA=1.34634002134、LB=8.805443996444，其中P_A∞指A全时绝对峰。H≥6T包含T，所以

$$
P_A^H(a)\le P_A^{\infty}(a)\le U_A,\qquad
P_B^H(a)\ge|u_{1,B,a}(T)|\ge L_B,\qquad
P_B^H(a)-P_A^H(a)\ge7.459103975104.\tag{5}
$$

这些是无量纲的继承保守常数，不是新时程数据。分离在包含T的同一观测窗内已经成立，不是仅由H后未知反应造成，也不需假定峰取得。

令单值估计器只看Z及共同辅助信息，估计该窗固定u1绝对峰。共同Ka、C0、输入、器件参数乃至两候选端口集合可以已知，但**实际采用的B及其空间标签不提供**。同一Z*必须返回同一P̂；两点三角式给

$$
\max_{L\in\{A,B\}}|\widehat P(Z_*)-P_L^H(a_\eta)|
\ge\tfrac12[P_B^H(a_\eta)-P_A^H(a_\eta)]
\ge3.729551987552.\tag{6}
$$

即存在一个共同容许记录，使至少一侧有上述误差；不是所有记录都模糊，也不否定额外空间信息或完整已知B后的前向预测。这里没有噪声概率下界、实际量化比特相同、无限H或工程容差保证，也未证明全参数开放球结论。

## 5 继承合同与贡献范围

κ/c精确定义及原数值证书见[R011采用合同](../../../research/sessions/20261017-2109/R011-certificate-adoption.md)与[准入JSON](../../../research/sessions/20261017-2109/R011-nonlinear-certificate-adoption.json)。数值来源仍依赖IEEE binary64 nearest、渐进下溢且无FTZ/DAZ、正确nextafter、精确Fraction、Python/NumPy float64解码及稳定运行模式；有限探针不是历史全程形式认证。源NPZ仍留本地，重建端点不同须重做包络。附录的新不等式是经典连续依赖、有界导数、积分和两点误差集合工具的特定条件整理，具体发表覆盖仍未知，不称新理论、首创或实际建筑不可预测。

本文没有噪声曲线，也不将原a=0图冒充非零a的精确同史图。原作者候选标签保留为历史，当前状态按根R019接纳；新R029/R040逆问题在途，未纳此附录。
