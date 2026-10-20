# 振型响应贡献及其叠加对主体楼层水平剪力的影响

**Modal response contributions and their superposition in horizontal story shear of the main structure**

作者、单位及邮编：待作者填写。

## 摘要（候选）

针对总体响应减小而个别楼层剪力改善有限的问题，研究前几阶及较高阶振型响应在主体水平剪力中的叠加作用。拟比较既有基准结构、模态阻尼增加3个百分点及设置实体阻尼器三种状态，在核对输入和主体模型后，采用一致参考振型分析各阶响应幅值及关键时刻的有符号贡献。第一、二、三阶分别考察，较高阶合并报告，并用完整输出检查重构误差。已有无量纲三层模型中，前两阶累计方向有效质量参与系数达到95.21%，仅保留两阶重新计算时，第二层剪力峰仍相对完整模型偏差约36.84%～43.32%，说明质量覆盖不能代替局部剪力核验。真实案例将先比较各层整体响应，再在模态向量和响应资料允许的范围内分析叠加及装置出力时序。尚未取得的工程单阶贡献比例留待计算。

**关键词**：主体结构；楼层剪力；模态响应；振型叠加；黏滞阻尼器

## Abstract (candidate)

This study examines how modal response amplitudes and their signed superposition affect horizontal story shear in the main structure. Three states are considered: the existing reference structure, a state with an additional three percentage points of modal damping, and a structure equipped with physical dampers. Their inputs and underlying structural models must first be matched. The first three modal contributions will be examined separately, with higher modes grouped and reconstruction errors checked against the complete output. In a previously calculated dimensionless three-story model, the first two modes account for 95.21% of directional effective mass, yet a new two-mode analysis differs from the complete model by approximately 36.84–43.32% in second-story shear peaks. Directional mass coverage therefore cannot replace a local shear check. Engineering modal contribution percentages have not yet been determined.

## 1 研究问题

增加阻尼后，各阶响应的减小程度未必相同；不同振型对同一楼层剪力的作用也可能相互抵消或加强。只比较屋顶位移、某阶响应峰或累计质量参与系数，尚不能解释目标楼层的剪力变化。本文关注第一至第三阶及更高阶分别影响哪些楼层，减剪来自幅值降低还是关键时刻叠加关系改变，并以装置出力时序补充解释。

## 2 三种状态及比较条件

|状态|比较内容|需先核对的条件|
|---|---|---|
|既有基准结构|作为响应比较的参照|实际背景阻尼、主体质量刚度及输入；不预设为零阻尼|
|模态阻尼增加3个百分点|观察规定阻尼变化后的响应|作用于哪些阶、原有阻尼及总阻尼，保持输入与主体一致|
|设置实体阻尼器|观察结构—装置耦合响应|主体、输入、装置模型及输出范围；不预设与前一状态等效|

先按同工况比较各层水平剪力的绝对最大值和对应时刻，再分析组成。模型身份不同的结果分别报告，不能将全部差异归因于阻尼。模态序号还需辨认X向、Y向与扭转特征；比较前统一振型符号、尺度和对应关系，不预设安装装置后振型必然改变。

## 3 模态贡献与叠加方法

对于质量、刚度矩阵正定的线弹性主体，采用已知完整实参考振型基Φ，令ΦᵀMΦ=I，则位移可表示为u=Φq，且q=ΦᵀMu。若某层主体弹性剪力具有固定输出向量ℓs，则

$$V_s(t)=\sum_r(\ell_s^T\phi_r)q_r(t).$$

第一、二、三阶分别保留，第四阶及以上作为较高阶组。只取得部分振型或节点响应时，另列重构剩余量，不将缺失部分计为零。质量参与系数描述输入方向参与，剪力贡献还取决于输出系数ℓsᵀφr及实际广义响应qr。

先在同一时刻相加，再求剪力绝对最大值；各阶独立峰不能直接相加。在完整剪力峰时记录各阶带符号值，并对照各阶自身峰时，区分幅值变化、峰时迁移和抵消关系。完整响应投影后的删阶重构，与减少振型后重新求解分别报告。滤波所得频带响应若无振型映射，只作频带近似。

## 4 已有小模型的解释基础

已有二层无量纲模型中，三种方案按规定第一振型周期运动标定至约2%参考附加阻尼；低频输入下，同一上层位置的两组阻尼系数使底层剪力分别降低约15.46%和增大3.30%。这说明参考耗能相近仍需检查逐层反馈响应，但该结果本身没有给出各阶贡献比例。

已有三层无量纲模型中，前两阶累计方向质量为95.21%，真正两阶重耦合在H2下的第二层剪力峰相对完整模型偏差约36.84%～43.32%；屋顶位移峰对应偏差约1.16%～3.73%。两类输出对截断的敏感程度不同。这些是简化模型数值结果，不是本栋工程的模态贡献或闭式解。计算条件见[既有算例说明](horizontal-paper-session006-v020-notes.md)。

## 5 真实案例的章节安排

案例先交代三种状态的资料、输入及阻尼设置，再给各层X、Y向整体剪力比较。取得兼容振型向量与响应后，列第一至第三阶及较高阶的幅值、同刻有符号叠加和重构差；资料不足的楼层不填模态百分比。

已有上部四层32只装置的原生力可辅助观察装置出力与关键剪力时刻，但不能补齐全楼装置力。Bottom剪力须先统一截面侧别、正方向与Link包含关系。真实案例将分别报告整体响应、可实现的模态分解及出力时序解释，阶段结论随证据补充。
