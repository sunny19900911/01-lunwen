# R003｜弹性切口模态系数的 Cauchy 量级界

**结论：指定的物理弹性输出下，\(|B_{sr}|\le\sqrt{M_s m_{\mathrm{eff},r}}\) 成立；不能无条件以整楼质量替换右端。此界是必要条件，不证明拟合系数的物理唯一性。**

## 1. 公式、符号与坐标条件

取同一组约束处理后的实坐标，质量矩阵 \(M=M^T\succeq0\)，实模态满足 \(K\phi_r=\omega_r^2M\phi_r\)、\(m_r=\phi_r^TM\phi_r>0\)。输入为 \(-Mr\,a_g\)，且 **已验证** 有符号弹性切口力为 \(V_s=r_s^TKu\)。令单位参与核满足

\[
\ddot s_r+2\zeta_r\omega_r\dot s_r+\omega_r^2s_r=-a_g,\quad
g_r=\omega_r^2s_r,\quad
\Gamma_r=\frac{\phi_r^TMr}{m_r}.
\]

则 \(q_r=\Gamma_rs_r\)，且

\[
V_{sr}=B_{sr}g_r,\qquad
B_{sr}=\frac{(r_s^TM\phi_r)(\phi_r^TMr)}{m_r},\quad
M_s=r_s^TMr_s,\quad
m_{\mathrm{eff},r}=\frac{(\phi_r^TMr)^2}{m_r}.
\]

质量半内积的 Cauchy 不等式给出

\[
(r_s^TM\phi_r)^2\le M_s m_r
\ \Longrightarrow\ 
\boxed{B_{sr}^2\le M_s m_{\mathrm{eff},r}}.
\]

若 \(M_s=0\) 或 \(m_{\mathrm{eff},r}=0\)，则 \(B_{sr}=0\)。\(\phi_r\mapsto a\phi_r\)（含模态反号）不改变 \(B_{sr}\)；其正负由输出投影与输入投影的乘积决定。若核改为右端 \(+a_g\)，系数为 \(-B_{sr}\)；若切口正方向相反，也须整体反号。本地 `modal_linear.py::states` 已核对为右端 \(-a_g\)。

## 2. 哪些“质量”可以使用

- **平动集总质量：** 对角质量矩阵、\(r\) 为全楼同方向单位平移、\(r_s\) 为切口以上同方向 0/1 选择向量时，\(M_s\) 等于上部方向质量，\(M_{\mathrm{dir}}=r^TMr\) 等于全楼方向质量。此时 \(M_s\le M_{\mathrm{dir}}\)、\(m_{\mathrm{eff},r}\le M_{\mathrm{dir}}\)，可用较松的 \(|B_{sr}|\le M_{\mathrm{dir}}\)。
- **一致或耦合质量：** 必须实际计算 \(r_s^TMr_s\)；它一般不等于 \(r_s^TMr\)，不能直接称为“上部质量”，也不能自动断言 \(M_s\le M_{\mathrm{dir}}\)。普遍成立的较松界仅为 \(|B_{sr}|\le\sqrt{M_sM_{\mathrm{dir}}}\)。平动、转动、刚性楼板参考点和约束变换须一致，不能混用质心质量、节点模态与转动自由度，或把各方向质量相加充作此界。
- **输出限定：** \(r_s\) 必须是使 \(r_s^TKu\) 等于该切口合力的虚位移向量，并包括全部跨切口弹性传力路径。仅凭拟合较好不能认定原生 `Bottom VX` 就是此算子；含阻尼、连接单元或其他直接项的总输出，须另核算子后才能使用本系数解释。

## 3. 给②的小表核验口径

每阶仅列：模态号、**恢复训练缩放后的原始** \(B^{\mathrm{fit}}\)、\(m_{\mathrm{eff},r}\)、经确认的 \(M_s\)、界 \(L_r=\sqrt{M_sm_{\mathrm{eff},r}}\)、\(|B^{\mathrm{fit}}|/L_r\)；零界单独判断。若设计矩阵列为 \(g_r/\mathrm{scale}_r\)，则原始系数为 \(\mathrm{coef}_r/\mathrm{scale}_r\)，不能拿归一化系数比较。

**先统一单位：** 若输出为 kN、核为 m/s²，则 \(B_{\mathrm{kg}}=1000B^{\mathrm{fit}}\)；若质量以 tonne 计，可直接与该原始系数数值比较。输入加速度实际缩放须由②核对，不假定为 m/s²；使用 g 单位的核须计入重力加速度换算。

只有在输出、坐标、核及单位均确认后，显著超界才否定“该拟合系数就是上述真实模态系数”的识别；未超界不能排除截断补偿或病态拟合。R002 的高阶组内部 \(\chi\approx0.999987\!\sim\!0.999998\) 仅提示拟合分量存在强抵消，不能单凭该值判定真实模态系数非物理。本页不新增拟合或模型。
