# 连续速度许可类的完整耗散值域

v001；独立补稿，文字整合待复审。

本补稿补足[原连续端点附录](maxwell-continuous-velocity-endpoints-v001.md)没有证明的“全部中间耗散值”可达性；原附录当时只处理两端的范围和原文保留。

## 1 许可类、端点与所借引理

固定κ,c,V>0、0<α≤1、0<h<B=cV^α、T>0。F与总变形δ绝对连续，v=δdot连续且|v|≤V，初力为零，要求末力精确为h；末总δ自由，不限制端点速度、加速度或结构反馈。定义

$$
\begin{aligned}
q&=1/\alpha\ge1,\quad\gamma=c^{-q},\quad g(F)=\gamma\operatorname{sgn}(F)|F|^q,\quad
 \dot F_v=\kappa[v-g(F_v)],\quad F_v(0)=0,\\
\mathcal K&=\{v\in C([0,T]):\|v\|_\infty\le V\},\qquad
\mathcal A_h=\{v\in\mathcal K:F_v(T)=h\},\\
D(v)&=\int_0^T F_vg(F_v)\,dt=\gamma\int_0^T|F_v|^{q+1}\,dt.
\end{aligned}\tag{1}
$$

D是真实黏壶耗散，不是净端口功。q≥1使g在[−B,B]单调且C¹，所有许可速度的有限时力均满足|F_v|<B。为自足地定义边界，在0≤x<B置

$$
\begin{aligned}
\tau_\uparrow(x)&=\frac1\kappa\int_0^x\frac{ds}{V-\gamma s^q},&
\tau_\downarrow(x)&=\frac1\kappa\int_0^x\frac{ds}{V+\gamma s^q},\\
\Phi_\uparrow(x)&=\frac1\kappa\int_0^x\frac{\gamma s^{q+1}}{V-\gamma s^q}\,ds,&
\Phi_\downarrow(x)&=\frac1\kappa\int_0^x\frac{\gamma s^{q+1}}{V+\gamma s^q}\,ds,\\
t_{\min}&=\tau_\uparrow(h),\qquad
\tau_\uparrow(M_T)+\tau_\downarrow(M_T)-\tau_\downarrow(h)=T,\\
D_{\min}&=\Phi_\uparrow(h),\qquad
D_{\max}=\Phi_\uparrow(M_T)+\Phi_\downarrow(M_T)-\Phi_\downarrow(h).
\end{aligned}\tag{2}
$$

先限T>t_min，此时唯一M_T∈(h,B)。借用原端点结论：每个v∈𝒜_h满足D_min<D(v)<D_max，且𝒜_h内有两族逐条精确F(T)=h的连续保幅控制，其耗散分别趋于两端。这些sharp上下确界本身不能排除中间缺口；下文另证精确末力许可集的路径连通，再对成本用介值定理。

## 2 偏置校准：存在且仅在目标层唯一

任取v_A,v_B∈𝒜_h。其凸组合w_λ保幅连续，却不能预设末力仍为h。用常值偏置和截断校准：

$$
\begin{aligned}
w_\lambda&=(1-\lambda)v_A+\lambda v_B,\quad0\le\lambda\le1,\qquad
C(x)=\max(-V,\min(V,x)),\\
u_{\lambda,b}(t)&=C(w_\lambda(t)+b),\quad -2V\le b\le2V,\qquad
H(\lambda,b)=F_{u_{\lambda,b}}(T),\\
H(\lambda,-2V)&=-z(T)<h<z(T)=H(\lambda,2V),
\end{aligned}\tag{3}
$$

其中z是常值控制+V的零初力解；T>t_min给h<z(T)<B，g的奇对称性给常值−V的末力−z(T)。截断为1-Lipschitz，结合力的连续依赖，H联合连续，故每个λ至少有一个b_λ∈(−2V,2V)满足H(λ,b_λ)=h。

根唯一只针对目标h，不能称H在全部b上全局严格递增。若b₁<b₂都为根，两控制逐点有序；若不完全相同，由连续性可知正测度集合上严格有序，严格末力比较便给不同末力，矛盾。若两控制完全相同，不同偏置的相同截断值只能为−V或+V；共同控制在连通时间区间上连续，只能恒为一个饱和值。其末力为±z(T)，又不等于h。因此目标偏置根唯一，完全饱和处的平台并未被排除。

## 3 连续路径与每个耗散值的精确实现

若λ_n趋于λ，根b_{λ_n}都在固定紧区间[−2V,2V]。任取收敛子列，其极限由H联合连续仍是目标h的根；唯一性迫该极限为b_λ，故整个根函数随λ连续。λ=0、1时偏置0已分别给原控制v_A、v_B，由唯一性有b_0=b_1=0。

具体连续依赖及校准路径为

$$
\begin{aligned}
\|u_{\lambda,b}-u_{\mu,d}\|_\infty&\le2V|\lambda-\mu|+|b-d|,\\
\|F_u-F_v\|_\infty&\le\kappa\|u-v\|_1,\qquad
|D(u)-D(v)|\le\kappa T(q+1)V\|u-v\|_1,\\
\Gamma(\lambda)&=u_{\lambda,b_\lambda},\qquad
\Gamma(0)=v_A,\quad\Gamma(1)=v_B,\quad
F_{\Gamma(\lambda)}(T)=h\quad(0\le\lambda\le1).
\end{aligned}\tag{4}
$$

因此Γ在一致范数下连续，路径两端精确恢复原控制，每条控制均连续保幅且精确达末力。末δ可随路径改变，因为本题没有固定它。上述力差估计来自非负有界割线系数，耗散功率的Lipschitz常数可取(q+1)V。

成本λ↦D(Γ(λ))连续，不要求它单调。任给d∈(D_min,D_max)，利用已审两端逼近族选v_A,v_B使D(v_A)<d<D(v_B)，沿精确末力路径用介值定理，得到某λ*使D(Γ(λ*))=d精确成立。每个内部耗散值因而可达；反向包含与端点排除由原端点定理给出。取满依赖这一步连通与成本论证，不能只从sharp两端推出。

## 4 三个时间分支与使用边界

将非退化结果与最短时间比较合并，完整真实耗散值域为

$$
\{D(v):v\in\mathcal A_h\}=
\begin{cases}
\varnothing,&T<t_{\min},\\
\{\Phi_\uparrow(h)\},&T=t_{\min},\\
(D_{\min},D_{\max}),&T>t_{\min}.
\end{cases}\tag{5}
$$

T<t_min时所有v≤V，比较给F_v(T)≤z(T)<h。T=t_min时常值v≡V达末力；其他连续控制只要某处小于V，便在正测度集合严格较小，末力将严格小于h，所以𝒜_h仅有v≡V。此时偏置饱和根可能不唯一，第2—3节的唯一根论证明确只用于T>t_min。

本结果不解决连续类固定D的峰集合，也不保持指定力峰或指定末总变形；不扩展到端点速度、统一加速度、零延拓或结构反馈约束，不推广α>1或h=0，不给建筑/FNA实现或布置优劣保证。比较、截断、紧性、路径连通与介值均为经典工具；具体同条件发表覆盖未知，不作首创主张。

证明据[已审作者推导](../research/roles/ideation/maxwell-session004/R035-continuous-cost-image/report.md)及[先独立证明](../research/roles/verification/maxwell-session004/R050-continuous-cost-image-independent/report.md)整理，当前命题状态以[正式采用记录](../../../research/sessions/20261017-2109/C043-adoption-v001.json)为准。原端点附录的历史范围保留，新补稿另待独立整合审。
