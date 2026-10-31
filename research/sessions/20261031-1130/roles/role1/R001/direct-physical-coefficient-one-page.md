# ①R001｜质量投影到弹性切口剪力：直接公式与核验条件

**解析结论：同一质量矩阵、输入与带符号模式下，非零总投影时有 \(B_{sr}=m_{\mathrm{eff},r}S_{sr}/S_r\)。它先是质量投影系数；全空间 Eigen 关系与全切口恢复成立后，才能作为单位参与核的精确弹性剪力系数。本文为独立推导，待②独审，未认证工程数据。**

**1．定义与消元。** 在同一约束后的实坐标中，\(M=M^T\succeq0\)、\(m_r=\phi_r^TM\phi_r>0\)，均匀X输入为 \(-Mr a_g\)。\(r_s\) 是上部沿X刚体虚平移对应的全切口选择向量。定义

\[
S_r=\phi_r^TMr,\quad S_{sr}=r_s^TM\phi_r,\quad
\Gamma_r=S_r/m_r,\quad m_{\mathrm{eff},r}=S_r^2/m_r.
\]
\[
\boxed{B_{sr}:=S_{sr}\Gamma_r=\frac{S_{sr}S_r}{m_r}
=m_{\mathrm{eff},r}\frac{S_{sr}}{S_r}\quad(S_r\ne0).}
\]

对任意非零实数 \(a\)，\(\phi_r\mapsto a\phi_r\) 使 \(S_r,S_{sr}\mapsto aS_r,aS_{sr}\)、\(m_r\mapsto a^2m_r\)、\(\Gamma_r\mapsto\Gamma_r/a\)，故 \(B\)、\(m_{\mathrm{eff}}\) 及投影比不变，包含振型反号。\(B\) 有正负；全楼切口 \(r_s=r\) 时 \(B=m_{\mathrm{eff}}\ge0\)。两投影采用相同振型单位，投影比无量纲，\(B\) 与有效质量同单位；以 m/s² 核乘 tonne 得 kN，以 m/s² 核乘 kg 得 N。

**2．质心小表何时足够。** 只有在完整质量投影确实满足下式时，才能用小表替代全自由度计算：
\[
S_r=\sum_{i\in\mathrm{all}}m_i\phi_{x,ir}^{CM},\qquad
S_{sr}=\sum_{i\in\mathrm{above\ cut}}m_i\phi_{x,ir}^{CM}.
\]
质量分区须无重漏，全部相关质量及跨切口构件质量的处理一致；刚性楼板的真实质心平移，或精确的质量加权平移平均，才有此表达。柔性楼板上的一个报告点不能自动充当该平均。平面刚体参考点O须换算 \(\phi_x^{CM}=\phi_x^O-(y_{CM}-y_O)\phi_z^\theta\)。在质心平移—转动解耦的刚体质量表达中，均匀X输入不直接投影到质心转动惯量或竖向分量；这些自由度仍可进入 \(m_r\)，但由同源 \(m_{\mathrm{eff}}\) 消元，**无需仅因缺转动惯量就否决本式**。一般耦合/一致质量仍以 \(\phi^TMr\) 为准，不能假定质心小表已完整。有效质量若由比例 \(\mu_r\) 换算，必须用同方向 \(M_X=r^TMr\)：\(m_{\mathrm{eff},r}=\mu_rM_X\)，百分数先除100；各表须同模型、同模式和同输入方向。

**3．弹性系数与 Ritz 残差。** 先验证切口符号及算子 \(V_s^{el}=r_s^TKu\)，涵盖所有跨切口弹性传力路径。令 \(e_r=K\phi_r-\omega_r^2M\phi_r\)，对任意该阶坐标 \(q_r\) 有
\[
V_{sr}^{el}=\underbrace{r_s^TK\phi_r}_{a_{sr}}q_r
=\bigl(\omega_r^2S_{sr}+r_s^Te_r\bigr)q_r.
\]
若完整 Eigen 关系成立，则 \(e_r=0\)。再在解耦线性、零初始条件下取 \(q_r=\Gamma_rs_r\)、\(\ddot s_r+2\zeta_r\omega_r\dot s_r+\omega_r^2s_r=-a_g\)，即有 \(V_{sr}^{el}=B_{sr}\omega_r^2s_r\)。Ritz 投影关系 \(\Phi^Te_r=0\) **不保证** \(r_s^Te_r=0\)；其核系数应为 \(B^{el}_{sr}=a_{sr}\Gamma_r/\omega_r^2=B_{sr}+\Gamma_r r_s^Te_r/\omega_r^2\)（\(\omega_r>0\)），或以原生模式内力恢复。即使全空间残差不为零，若指定切口投影 \(r_s^Te_r=0\) 已独立核实，该切口仍可精确恢复；不能把投影特征方程本身当成此核验。

**4．零参与、近零与实际 FNA。** \(S_r=0\Rightarrow\Gamma_r=m_{\mathrm{eff},r}=B_{sr}=0\)，比值式为0/0，禁硬除；有完整 \(M,\phi\) 时改用乘积式。近零投影可报告 \(\eta_r=|S_r|/\sum_i|m_i\phi_{x,ir}^{CM}|\) 及总投影误差界 \(\delta S_r\)：若 \(|S_r|\) 与误差同量级，停止报告比值精确数，不设无单位依据的固定小数阈值。真实 \(m_{\mathrm{eff}}\) 随 \(S_r^2\) 趋零，并不意味着真实 \(B\) 发散；风险来自分母抵消、截断和参与表舍入。

实际 FNA 的广义阻尼/非线性力可耦合各阶；\(B\) 的物理来源不能证明 \(q_r=\Gamma_rs_r\)。即使 \(\Gamma_r=0\)，该阶仍可能被耦合间接驱动；其真实弹性输出应以 \(a_{sr}q_r\) 计算。取不到实际 \(q_r\)，不能仅凭 \(B\) 宣称取得实际逐阶时程；截断位移与非线性连接力等剩余输出还须另计。

**给②④的最小执行顺序：** ①冻结质量/参与/振型的模型身份、单位、模式类型及符号，先核CM表达等于完整质量投影；②逐阶算 \(S_r,S_{sr},\eta_r\)，零/近零分流，再按上式得B；③核全楼切口 \(B=m_{\mathrm{eff}}\)、换号/缩放不变及 Cauchy 界 \(|B|\le\sqrt{(r_s^TMr_s)m_{\mathrm{eff}}}\)（不能无条件把首项换为整楼质量）；④取得K/原生模式切口力时独立核 \(a_{sr}=\omega_r^2S_{sr}+r_s^Te_r\)，未取得则标记弹性身份未核；⑤仅对完备M正交模态基核 \(\sum_rm_{\mathrm{eff},r}=M_X\)、\(\sum_rB_{sr}=r_s^TMr\)。有限阶只报告截断余项，不强行补齐；近重根须先对齐共同子空间，不凭阶号逐一迁移。
