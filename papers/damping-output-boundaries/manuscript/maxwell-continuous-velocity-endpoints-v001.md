# 连续速度许可类中的耗散端点

v001；经典正则性边界说明，文字整合待独立复审。

## 1 许可类与已有耗散外界

固定κ,c,V>0、0<α≤1、0<h<B=cV^α。考虑单个Maxwell器件，F与总变形δ绝对连续，v=δdot∈C([0,T])且|v|≤V，F(0)=0、F(T)=h。**不规定端点速度v(0)、v(T)，不限制加速度，末总δ自由**；也不加建筑动力反馈。记

$$
\begin{aligned}
q&=1/\alpha\ge1,\quad\gamma=c^{-q},\quad
 g(F)=\gamma\operatorname{sgn}(F)|F|^q,\quad
 \dot F=\kappa[v-g(F)],\\
r(x)&=\gamma x^q,\qquad P(x)=xr(x),\qquad
 M=\max_{[0,T]}|F|,\qquad D=\int_0^T P(|F|)\,dt.
\end{aligned}\tag{1}
$$

有限时间内|F|<B。对0≤x<B定义上升/下降积分，并沿用可测速度类的边界函数：

$$
\begin{aligned}
\tau_\uparrow(x)&=\frac1\kappa\int_0^x\frac{ds}{V-r(s)},&
\tau_\downarrow(x)&=\frac1\kappa\int_0^x\frac{ds}{V+r(s)},\\
\Phi_\uparrow(x)&=\frac1\kappa\int_0^x\frac{P(s)}{V-r(s)}\,ds,&
\Phi_\downarrow(x)&=\frac1\kappa\int_0^x\frac{P(s)}{V+r(s)}\,ds,\\
\tau_h(M)&=\tau_\uparrow(M)+\tau_\downarrow(M)-\tau_\downarrow(h),\\
L_h(M)&=\Phi_\uparrow(M)+\Phi_\downarrow(M)-\Phi_\downarrow(h),\qquad
U(M)=L_h(M)+P(M)[T-\tau_h(M)],\\
t_{\min}&=\tau_\uparrow(h),\quad
D_{\min}=\Phi_\uparrow(h),\quad
D_{\max}=L_h(M_T)=U(M_T),\quad\tau_h(M_T)=T.
\end{aligned}\tag{2}
$$

以下先限T>t_min，此时唯一M_T∈(h,B)。已有[固定峰取满证明](../research/roles/verification/maxwell-session004/非零末力耗散峰力区间独审-R017.md)及[反演附录](maxwell-fixed-dissipation-peak-appendix-v002.md)给出可测类外界D_min≤D≤D_max、h≤M≤M_T；L_h与U在[h,M_T]严格递增，虽U′(M_T)=0。连续类是其子类，故仍满足这些外界。

可测类下端速度b_min先零力等待w*=T−t_min，再以V最快升力；上端速度b_max先以V升至M_T，再以−V降至h，切换时刻s*=τ↑(M_T)∈(0,T)。下文说明：连续类不能取到这两个端点，但两端仍分别是精确下确界和上确界。

## 2 两端等号为何排除连续速度

下端用有符号原函数，不能预先假定整个力史非负：

$$
\Psi(F)=\frac1\kappa\int_0^F\frac{s\,g(s)}{V-g(s)}\,ds,
\qquad\Psi(h)=D_{\min},\qquad
D-D_{\min}=\int_0^T\frac{Fg(F)[V-v]}{V-g(F)}\,dt\ge0.\tag{3}
$$

实际轨迹上分母为正，Fg(F)≥0。若取等号，则每个非零力开区间上v=V几乎处处，由连续性进而处处为V。负力分支不可能从左端零力出发，因为该分支F′=κ(V+γ|F|^q)>0；正力分支一旦出现便严格增加，不能再回零。末力为h>0，故只能先F≡0等待w*>0，再最快正升t_min。零力段迫v=0，随后迫v=V，无法在内部w*连续接合。因此连续许可轨迹严格有D>D_min。

上端若D=D_max，由D≤U(M)和U严格递增先得M=M_T。任取达绝对峰时刻t*，已有时间界为

$$
t^*\ge\tau_\uparrow(M_T),\qquad
T-t^*\ge\tau_\downarrow(M_T)-\tau_\downarrow(h),\qquad
\tau_\uparrow(M_T)+\tau_\downarrow(M_T)-\tau_\downarrow(h)=T.\tag{4}
$$

两项时间缺口非负且和为零，故分别取等号，迫绝对力先最快增幅、后最快降幅。过程中不能经零换号；末力为正迫峰也为正。因此t*=s*，v在峰前几乎处处为V，峰后几乎处处为−V。两段长度均正，因为M_T>h>0；连续v无法在内部s*由V跳至−V。因此连续类还严格有D<D_max。

## 3 保幅ramp与每一条轨迹的精确末力

仅把跳变抹平会改变末力，必须再校准ramp的位置。取足够小ε>0，使下列斜坡都留在[0,T]，定义

$$
\begin{aligned}
v^-_{a,\varepsilon}(t)&=
\begin{cases}0,&t\le a,\\V(t-a)/\varepsilon,&a\le t\le a+\varepsilon,\\V,&t\ge a+\varepsilon,\end{cases}\\
v^+_{s,\varepsilon}(t)&=
\begin{cases}V,&t\le s-\varepsilon,\\-V(t-s)/\varepsilon,&s-\varepsilon\le t\le s+\varepsilon,\\-V,&t\ge s+\varepsilon.\end{cases}
\end{aligned}\tag{5}
$$

两族均连续且|v|≤V。q≥1使g在[−B,B]上为C¹、单调且导数有界。两控制之差方程的非负割线系数给严格比较：若一控制几乎处处较大，且正测度集合上严格大，则其末力严格大。控制的L¹变化还给末力连续依赖。

下端取a∈[w*−ε,w*]：a=w*−ε时控制≥b_min且有严格区间，末力>h；a=w*时控制≤b_min且有严格区间，末力<h。末力随a连续且严格递减，介值定理给a_ε∈(w*−ε,w*)，使每条校准运动精确满足F⁻_ε(T)=h。

上端取s∈[s*−ε,s*+ε]：左端ramp恰在s*结束，控制≤b_max且有严格区间，末力<h；右端ramp恰在s*开始，控制≥b_max且有严格区间，末力>h。末力随s连续且严格递增，故有s_ε∈(s*−ε,s*+ε)精确满足F⁺_ε(T)=h。这里没有要求平滑后的峰仍等于M_T。

对同零初态的控制v,w，由非负割线系数及P(|F|)的Lipschitz常数(q+1)V得到连续依赖估计；校准后的ramp另有面积和平移量界：

$$
\begin{aligned}
\|F_v-F_w\|_\infty&\le\kappa\|v-w\|_1,\qquad
|D(v)-D(w)|\le\kappa T(q+1)V\|v-w\|_1,\\
\|v^-_\varepsilon-b_{\min}\|_1&\le2V\varepsilon,\qquad
\|v^+_\varepsilon-b_{\max}\|_1\le3V\varepsilon,\\
F^-_\varepsilon(T)&=F^+_\varepsilon(T)=h,\qquad
D^-_\varepsilon\longrightarrow D_{\min},\quad
D^+_\varepsilon\longrightarrow D_{\max}.
\end{aligned}\tag{6}
$$

因此T>t_min时，每条连续许可运动均满足D_min<D<D_max，而连续类的下确界为D_min、上确界为D_max；两端均不取到。结论依赖的是逐条精确末力校准及成本连续性，不是仅在极限中满足末力。

## 4 退化情形与结论边界

T=t_min时M_T=h、D_min=D_max=Φ↑(h)，常值v≡V本身连续并精确达末力，端点可以取到。T<t_min无许可运动。若另要求端点速度为零、区间外零延拓连续、统一加速度界或末δ闭合，许可类已改变，不能沿用本构造；上述ramp斜率V/ε随ε趋零发散，不满足统一有限加速度界。

本说明只处理0<α≤1的两个耗散端点；**没有证明连续类取满整个耗散开区间，也没有解决连续类固定D的峰集合**。不推广α>1，不给真实建筑或FNA可实现性保证。所用比较、AC链式、介值校准与连续依赖均属经典工具，不作新颖性主张。证明转录自[已审推导](../research/roles/ideation/maxwell-session004/R034-continuous-velocity-endpoints/report.md)与[先独立核验](../research/roles/verification/maxwell-session004/R048-continuous-velocity-independent/report.md)，其当前状态以[正式采用记录](../../../research/sessions/20261017-2109/C042-adoption-v001.json)为准；本短附录的文字整合另待复审。
