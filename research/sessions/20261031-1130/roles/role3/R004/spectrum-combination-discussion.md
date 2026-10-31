# 反应谱、模态相关与楼层峰值：作者讨论段及引用

角色③，90分钟续写范围内；复用⑥R001冻结方法及CSI手册。本文不重算⑥反例，也不把尚待独审的数值写成已审核工程结果。

## 1. 原文可支持什么

CSI Analysis Reference Manual，July2016 Rev.15：

| 位置 | 原文内容的转述 | 本文用途 |
|---|---|---|
| 印刷384/PDF406，Overview | 反应谱以伪谱加速度表示，求各响应的统计最大量；不提供峰值出现时间，也不提供该时刻其他响应的值 | 谱权重只能用于幅值初筛，不能重建同刻模态项或控制峰转移 |
| 印刷385–386/PDF407–408，Response-Spectrum Function | 谱函数采用伪谱加速度—周期曲线；函数值按重力归一化，幅值乘有加速度单位的比例因子 | 明确S_pa=ω²S_d及谱纵坐标单位；无量纲谱值须先换成物理加速度 |
| 印刷388/PDF410，Modal Combination | 对各模态分别求最大响应，再按选定方法组合为相应方向的正值 | 组合结果不是实际时程中某时刻各阶带符号贡献的表格 |
| 印刷390/PDF412，CQC Method | CQC考虑近频模态响应之间的统计相关，相关程度受模态阻尼影响 | 将统计相关与运动方程中坐标相互驱动分开 |
| 印刷390–391/PDF412–413，SRSS/Absolute Sum | SRSS采用平方和开方，绝对和采用各阶绝对值求和 | 规则本身与各阶响应如何随阻尼变化分别说明；不把“组合规则不受阻尼影响”扩展为“响应不受阻尼影响” |

[CSI官方手册](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf)。本轮沿用R001已核原件指纹，无新文献下载。

## 2. 幅值总和与实际峰值（本轮方法的解释）

在固定物理输出关系V_s(t)=Σ_r B_sr g_r(t)适用时，令A_r=max_t|g_r(t)|。各阶峰幅绝对值之和为U_s=Σ_r|B_sr|A_r，同刻合成曲线的峰值为P_s=max_t|V_s(t)|。U_s>0时，C_s=P_s/U_s位于0至1之间。

U_s刻画各阶独立峰幅的总量，C_s反映这些峰幅合成后形成的相对峰值。C_s同时受模态项符号、峰时错开及波形影响；仅凭它的变化，不能分出纯相位改变造成的因果份额。若仅保留有限阶，这些量先对应保留项合成，软件总输出与截断项之间的差额另行记录。

比较5%和8%参照分析，分母均满足定义时，有

$$\frac{P_{s,8}}{P_{s,5}}=
\frac{U_{s,8}}{U_{s,5}}\,
\frac{C_{s,8}}{C_{s,5}}.$$

这只是既有响应量之间的恒等分解。它说明独立峰幅总和减小后，合成比例的变化仍影响楼层最终峰值。各阶均减幅不能单独给出合成峰必然减小的结论。若P_5或U_8为零，则直接报告P、U及相应曲线，不能硬算这一比值。

## 3. 可供正文选用的中文讨论

**增阻尼后的楼层差异。** 阻尼增加对各阶运动的影响，与各阶运动对楼层剪力的作用，需要分两步分析。前者由频率、阻尼和输入决定，后者由质量分布、振型和切口力恢复关系决定。同一组模态运动经过不同楼层的带符号系数组合后，可以形成不同的峰幅和控制时刻。因此，工程判断应同时检查各阶峰幅变化和同刻叠加关系。

**合成峰的解释。** 对给定输入，先求各阶剪力项的独立绝对峰，再求完整合成曲线的绝对峰。二者的比值反映各阶峰时、符号及波形共同作用的结果。增阻尼后，即使各阶峰幅均下降，只要这些模态项在控制时段的合成关系改变，楼层峰值仍可能下降较少，解析算例中也可能出现增幅。具体工程是否发生这一现象，应以相应输入下的完整曲线判断。

**谱权重的工程用途。** 只有设计谱时，可将各阶伪加速度谱值与该层物理输出系数相乘，按独立峰幅的大小安排重点检查层和重点阶次。采用5%与8%两条谱时，幅值总和的比值可描述这一包络随阻尼变化的程度。谱不包含实际峰时及模态项的同刻关系，故该比值用于检查排序，不能直接替代实际楼层峰值比。

**统计相关与实际耦合。** 线性经典阻尼体系的模态运动方程可以解耦，但各阶仍受同一地震输入驱动，其响应之间存在相关性。反应谱CQC组合考虑的是这一统计相关。非经典阻尼或非线性装置导致的广义坐标耦合，则表现为运动方程中不同坐标相互影响。本文分别说明这两种关系，避免仅由CQC相关系数随阻尼变化，推断实际体系的动力耦合程度。

## 4. 英文对应段落

Increasing modal damping changes the response of each mode, while the physical story shear coefficients determine how these modal responses contribute to a particular cut. The peak of their time-synchronous sum depends on the modal amplitudes, signs, waveforms, and the times at which they combine. A reduction in every individual modal peak therefore does not, by itself, establish a reduction in the peak of the combined story shear.

When only design spectra are available, the product of the physical output coefficient magnitude and the pseudo-spectral acceleration can be used to rank the modal amplitude contributions for further examination. This ranking does not recover the simultaneous signed modal forces or the time of the governing peak. Statistical modal correlation in response spectrum combination must also be distinguished from coupling of the actual modal equations caused by nonclassical damping or nonlinear devices.

## 5. 本轮实例进入正文时的口径

- ⑥的两层例为固定单频稳态、相同M/K及物理弹性输出；②独审后才引用其数值。不能把稳态例的增幅改写为零初始有限地震输入的实测或软件结果。
- 原12层三波36项已核峰值均下降，仍可用于说明各层削弱比例不同；两层反例说明的是一般保证不能从逐阶减幅直接推出。
- 模态局部系数为负表示所选方向投影的符号；应结合该阶实际响应时程判断同刻剪力，不能将负系数直接称为有利模态。
- 谱权重不作为已知曲线分担比例；本文U/P/C也不直接等于CQC相关系数或装置耗能比例。

本项只提供出处与文字，不新增ODE、扫频、拟合、工程数据提取或独立工程数值结论。
