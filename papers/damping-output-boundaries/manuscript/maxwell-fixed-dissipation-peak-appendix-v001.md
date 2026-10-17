# 固定真实耗散的完整可达峰集合

v001，2026年10月18日；独立短附录，待整合复审。依据[根C038采用记录](../../../research/sessions/20261017-2109/R020-C038-adoption.json)、[作者R029](../research/roles/ideation/maxwell-session004/R029-fixed-dissipation-peak-inverse/report.md)、[独立R040](../research/roles/verification/maxwell-session004/R040-fixed-D-inverse-independent/report.md)及其[冻结后比对](../research/roles/verification/maxwell-session004/R040-fixed-D-inverse-independent/post-freeze-comparison/report.md)。全文统一采用作者的D_min、D0、D_max，不混用独审中同名D0的另一含义。

## 1 问题与许可类

相同耗散不一定确定唯一峰力：在下面非退化耗散域的内部，可以有不同峰；但耗散域两端及最短时间情形各只有一个峰。结论只讨论单个Maxwell器件的许可运动，不涉及楼层响应或布置优劣。

固定κ,c,α,V,T>0、h>0、σ∈{−1,+1}。总变形δ和力F绝对连续，v=δdot为有界可测速度，abs(v)≤V几乎处处；F(0)=0、F(T)=σh，**末总变形自由，不要求位移闭合**。记

$$
\begin{aligned}
q&=1/\alpha,\quad\gamma=c^{-q},\quad
\dot F=\kappa[v-g(F)],\quad g(F)=\gamma\operatorname{sgn}(F)|F|^q,\\
r(x)&=\gamma x^q,\quad P(x)=xr(x),\quad B=cV^\alpha,\quad r(B)=V,\\
M&=\max_{0\le t\le T}|F(t)|,\qquad
D=\int_0^T Fg(F)\,dt=\int_0^T P(|F|)\,dt.
\end{aligned}\tag{1}
$$

这里D是不可逆真实耗散，不是净端口功。P是耗散功率函数，不是峰值记号。下述积分仅在0≤x<B定义：

$$
\begin{aligned}
\tau_\uparrow(x)&=\frac1\kappa\int_0^x\frac{ds}{V-r(s)},&
\tau_\downarrow(x)&=\frac1\kappa\int_0^x\frac{ds}{V+r(s)},\\
\Phi_\uparrow(x)&=\frac1\kappa\int_0^x\frac{P(s)}{V-r(s)}\,ds,&
\Phi_\downarrow(x)&=\frac1\kappa\int_0^x\frac{P(s)}{V+r(s)}\,ds.
\end{aligned}\tag{2}
$$

先排除h≥B。若0<h<B，对h≤M<B置

$$
\begin{aligned}
\tau(M)&=\tau_\uparrow(M)+\tau_\downarrow(M)-\tau_\downarrow(h),\\
L(M)&=\Phi_\uparrow(M)+\Phi_\downarrow(M)-\Phi_\downarrow(h),\\
U(M)&=L(M)+P(M)[T-\tau(M)],\qquad
 t_{\min}=\tau(h)=\tau_\uparrow(h).
\end{aligned}\tag{3}
$$

已审[非零末力固定峰取满定理M-C018](../research/roles/verification/maxwell-session004/非零末力耗散峰力区间独审-R017.md)给出：指定峰M可达，当且仅当h≤M<B且τ(M)≤T；在该峰下D恰取满[L(M),U(M)]，允许反号峰或换号过程也不扩大此区间。本附录反演这项已有完整正问题。

## 2 可行峰域与两个严格单调边界

对h≤M<B，

$$
\begin{aligned}
\tau'(M)&=\frac{2V}{\kappa[V^2-r(M)^2]}>0,\qquad
L'(M)=P(M)\tau'(M)>0,\\
P'(M)&=(1+q)\gamma M^q>0,\\
U'(M)&=L'(M)+P'(M)[T-\tau(M)]-P(M)\tau'(M)
=P'(M)[T-\tau(M)].
\end{aligned}\tag{4}
$$

r在B附近光滑且r′(B)>0，故τ(M)在M趋于B时发散。T≥t_min时存在唯一M_T∈[h,B)使τ(M_T)=T，可行峰域J=[h,M_T]。T=t_min时J={h}，单独处理；以下逆函数结论先限T>t_min。

非退化时U′在[h,M_T)严格为正，仅右端U′(M_T)=0。任意M1<M2≤M_T的区间都有正长度内段，积分U′严格为正，所以U在整个闭区间J严格递增。L也严格递增；这不要求右端逆导数有限或存在。

## 3 先判耗散域，再用受限逆

规范统一定义

$$
\begin{aligned}
D_{\min}&=L(h)=\Phi_\uparrow(h)>0,\qquad D_0=U(h)
=D_{\min}+P(h)(T-t_{\min}),\\
D_{\max}&=L(M_T)=U(M_T),\qquad D_{\min}<D_0<D_{\max},\\
L_J^{-1}&:[D_{\min},D_{\max}]\longrightarrow J,\qquad
U_J^{-1}:[D_0,D_{\max}]\longrightarrow J.
\end{aligned}\tag{5}
$$

必须先判D是否在[D_min,D_max]：域外为空集，不调用逆，不把非法D截成合法耗散。域内的所有可达绝对峰恰为

$$
\begin{aligned}
M_+(D)&=L_J^{-1}(D),\qquad
M_-(D)=U_J^{-1}(\max\{D,D_0\})
=\begin{cases}h,&D\le D_0,\\U_J^{-1}(D),&D>D_0,\end{cases}\\
\mathcal M(D)&=[M_-(D),M_+(D)].
\end{aligned}\tag{6}
$$

必要性来自L(M)≤D等价M≤M_+，D≤U(M)等价M≥M_−。M_+本身满足L(M_+)=D≤U(M_+)，故两端有序；源取满定理保证每个中间M均可达。任意域内D也可先取M=L_J⁻¹(D)，因此完整耗散域没有缺口。若D_min<D<D_max，则h<M_+<M_T且U(M_+)>L(M_+)=D，故M_−<M_+。

特别地，D=D_min合法，但低于U逆的像域下端D0；裸写U_J⁻¹(D)无定义，事后再取max(h,逆值)不能补救。式（6）的max在**逆函数参数内**，只用于合法D的U像域截取。

| 前置条件 | 固定D的完整结论 |
|---|---|
| h≥B | 所有D为空；不求h处上升积分 |
| 0<h<B，T<t_min | 所有D为空；不定义后续逆 |
| 0<h<B，T=t_min | 仅D=Φ↑(h)有峰集合{h}，其余为空 |
| 0<h<B，T>t_min，D在[D_min,D_max]外 | 空集；不靠截取D伪造可达性 |
| 非退化，D=D_min或D=D_max | 分别为{h}或{M_T} |
| 非退化，D_min<D<D_max | 式（6）为非退化闭区间；D=D0时下端仍为h |

## 4 所有峰的实现与端口功换元

对任意M∈[M_−,M_+]，取

$$
\Delta=T-\tau(M)\ge0,\qquad
\ell=\frac{D-L(M)}{P(M)}\in[0,\Delta],\qquad
D=L(M)+P(M)\ell,\qquad
W=\int_0^T Fv\,dt=D+\frac{h^2}{2\kappa}.\tag{7}
$$

实现依次为：零力等待Δ−ℓ；以v=σV按幅值最快升至σM；以v=σr(M)驻留ℓ；以v=−σV按幅值最快降至σh。上升用时τ↑(M)，下降用时τ↓(M)−τ↓(h)，四段总时长恰T。r(M)<V保证驻留许可；M≥h>0保证P(M)>0。Δ=0时ℓ=0，不除以零余时；M=h时下降段为零。积分v得到总δ，末δ自由，所以两端及全部中间峰都真正实现。σ同时翻转F和v，不改耗散或绝对峰。

若给定净端口功W，必须先作D=W−h²/(2κ)，再走上述判域。非退化W域是[D_min+h²/(2κ),D_max+h²/(2κ)]；最短时间单点同样平移，不能直接把W代入D公式。

## 5 使用范围与归属

速度开关可以跳变，F/δ仍绝对连续；这不是连续速度或连续加速度类的边界取等保证。增加末δ闭合、其他容量或结构动力约束会改变充分性。实际κ/c/α、连续速度界V、真实D及端口身份仍须证据，建筑不一定能实现每一种许可速度；此结果不给结构布置、楼层反应或实际工程保证。

按[贡献分级R023](../research/roles/novelty/maxwell-session004/R023-contribution-grading/report.md)及[发表覆盖R027末段](../research/roles/literature/maxwell-session004/R027-nonzero-terminal-dissipation-prior-art/report.md)，比较/积分、快过渡—驻留和受限单调逆是经典工具；具体同条件发表覆盖仍未知，不认首创或新理论。R027当时未纳固定D逆问题是历史范围，当前数学准入以根C038记录为准，不回写旧源。本附录未做新积分、时程、数组或绘图；尚待独立整合审后发布。
