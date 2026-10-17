# 真实器件力如何连接固定位置响应

装置耗能较多，并不能单独说明某个楼层或连接点的位移较小。诊断还需要知道：装置向哪个方向传力、该方向在各模态中怎样参与，以及这些有符号贡献在同一时刻相加还是抵消。端点、局部轴和属性小表先把装置位置说清，随后才能把力历史与目标响应对应。

在参考主体、输入和主体初态完全相同、真实器件力已经完整已知时，经典卷积可重构装置引起的目标位移差。它帮助追查力从何处进入、哪些模态参与及资料缺口；它不预测新输入或新布局下尚未知的器件力，也不能单靠这个差值给出两方案各自的实际峰值。

版本v001，2026年10月18日；短附稿，待独立整合复审。当前依据为[根R014接纳](../../../research/sessions/20261017-2109/R014-adoption.json)、[作者R022](../research/roles/ideation/maxwell-session004/R022-force-target-interface/report.md)及[独审R030](../research/roles/verification/maxwell-session004/R030-force-target-interface-review/report.md)，不是新理论或实际工程认证。

## 1 固定参考、输出与符号

在同一约束后坐标，M、K正定，背景C相同。U去掉全部指定非线性支路，D保留支路；外力f及主体初始位移、速度相同。端口总变形δ=Bu，F_D为与端口速度功共轭的**完整恢复力**，在D左端组装为+BᵀF_D。令w=u_D−u_U，则

$$
M\ddot w+C\dot w+Kw=-B^{T}F_D,
\qquad w(0)=\dot w(0)=0. \tag{1}
$$

器件初力若非零，其施力已含在F_D内，不再另加一遍主体初力齐次项。同f并不表示同输入功。去支路也不等于删除整只Link；若线性DOF、质量或约束随之变化，式（1）需另列差异项。外力、M/K/C或主体初态不同时，还须保留相应算子差、未列非线性力与初态齐次项。

要求所选参考的**完整确切共同Eigen基**：ΦᵀMΦ=I、ΦᵀKΦ=diag(ω²)，且实际ΦᵀCΦ=diag(2ζω)。对固定线性位移或相对位移y=ℓᵀu，令γ_j=ℓᵀφ_j、β_dj=B_dφ_j。ω_j>0、0≤ζ_j<1时，

$$
\begin{aligned}
y_D(t)-y_U(t)&=-\sum_{j,d}\gamma_j\beta_{dj}
 \int_0^tG_j(t-\tau)F_{D,d}(\tau)\,d\tau,\\
G_j(t)&=e^{-\zeta_j\omega_jt}
\frac{\sin(\omega_j\sqrt{1-\zeta_j^2}\,t)}
{\omega_j\sqrt{1-\zeta_j^2}},\quad t\ge0.
\end{aligned}\tag{2}
$$

核在负时间为零。零阻尼仍可用有限窗身份，但不能套无限时L1核增益；其他阻尼类型或非经典C需相应核，不能冒用式（2）。

若原形状ψ_j为同一确切模态的一致缩放，系数改为(ℓᵀψ_j)(B_dψ_j)/m_j，m_j=ψ_jᵀMψ_j。两投影同尺度、同相位，不能拼接另一缩放的质量列或用参与率平方替代。模态共同翻号不改乘积；改B_d符号必须同时改F_d符号。实际I/J交换、局部轴、偏置、转角及约束须一并核查，不能只反一列或逐节点取绝对值。

## 2 完整性及FNA配对

只算模态子集I和力子集S，必须保留“遗漏模态×全部器件”和“已算模态×遗漏器件”两个不重叠余项。现有32/88只仅为部分贡献，另56只不能补零；有符号部分和没有天然总差上、下界，也不是实际移除这32只后的反事实响应。采样力F̂另缺核作用于F_D−F̂的误差；时间轴、插值、求积和遗漏投影需认证。输入停止不表示Maxwell力同时为零，记录窗外及无限尾不能自动补零。

按[CSI口径复查R017](../research/roles/literature/maxwell-session004/R017-FNA-reference-force-scope/R017-FNA-reference-force-scope.md)及R030，在端口装配已核、同M/C条件下，设K_eff=K0+Bᵀk_eB、R_D=F_D−k_eBu_D，以L0、L_eff表示相应二阶主体算子，则

$$
\begin{aligned}
L_0u_D&=f-B^TF_D,\qquad L_{eff}u_D=f-B^TR_D,\\
L_{eff}(u_D-u_{U0})&=-B^T(R_D+k_eBu_{U0}),
\qquad L_0u_{U0}=f.
\end{aligned}\tag{3}
$$

**K0配完整F_D；Keff配残余R_D。**只删残余得到Ueff，通常不是物理无支路U0；比较U0须式（3）的补偿。有效k_e不是实际串联κ，不能擅给CSI此残余加有效阻尼补偿。改参考刚度后，原FNA振型、频率和ζ未必仍共同对角化同一C；两边均填5%不证明实际C相同。实际Eigen/Ritz、建基刚度、背景与P列全力/余力及符号均尚未认证，有限Ritz也不能冒充完整确切Eigen。

## 3 最小字段与可用范围

| 资料 | 最小内容及当前门槛 |
|---|---|
| 参考身份 | 模型/约束、质量源、K0或Keff及状态、实际C；同f和主体初态证据 |
| 模态 | 完整共同Eigen或余项；ω用rad/s、实际ζ、质量归一或一致m/尺度/相位 |
| 固定目标 | ℓ的点位、方向或差分定义，各模态有符号γ |
| 装置端口 | 全部指定装置/工作DOF、有符号β或I/J形状及原生轴、偏置/转角/约束映射 |
| 力与误差 | 同一D工况完整F_D、共轭符号/单位、共同时间窗；采样、积分、缺模态/器件及尾余项 |

可直接交经认证的γ/β，无需全楼其他节点。差值中共同f已抵消，不另需输入模态参与因子，但同输入身份仍必需；恢复绝对y_D还需y_U或参考输入/初态解。已有[装置位置CSV](../research/roles/writing/maxwell-session004/layout-input-templates-v001/device_locations.csv)、[属性CSV](../research/roles/writing/maxwell-session004/layout-input-templates-v001/link_properties.csv)及[中文填写说明](../research/roles/writing/maxwell-session004/layout-input-templates-v001/README.md)只承接几何/属性，不代表上述动力资料已齐。未知留空，零长Link须原生轴，图只复查编号。

一个直观例子是已审[C028/R029](../research/roles/verification/maxwell-session004/R029-modal-sign-corollary/report.md)：C027指定合成模型中取q±=(u1±u2)/√2；同一真见证处q+<−3.27、q−<−2.75，u1两贡献同号、u2异号；从零到该时刻，反对称裸模态获器件功>363/32，对称模态功<−363/32，两者合计仍非正。它说明总端口被动与某裸模态获功相容，F反馈仍耦合模态；不是主动供能、新机制理论或实际FNA模态独立。该例继承C027的binary64 nearest、渐进下溢且无FTZ/DAZ、正确nextafter/Fraction、float64解码和稳定运行模式合同，有限探针不证明历史全程模式。

式（2）仅限已知真实F_D后的条件位移重构，同源重放不等于独立预测验证。旧力移到新布局只定义规定外力重放；位移式不能直接改名为加速度或总层剪。本文不纳仍在途的R019新FOH、R023峰值判据及actual-gap/R016，不推出工程改善、全楼最优或发表优先权。
