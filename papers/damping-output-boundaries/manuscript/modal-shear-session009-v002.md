# 振型响应贡献及其叠加对主体楼层水平剪力的影响

**Modal response contributions and their superposition in horizontal story shear of the main structure**

作者、单位及邮编：待作者填写。

## 摘要（候选）

针对总体响应减小而个别楼层剪力改善有限的问题，研究前几阶及较高阶振型响应在主体水平剪力中的叠加作用。拟比较既有基准结构、模态阻尼增加3个百分点及设置实体阻尼器三种状态，在核对输入和主体模型后，采用一致参考振型分析各阶响应幅值及关键时刻的有符号贡献。第一、二、三阶分别考察，较高阶合并报告，并用完整输出检查重构误差。已有无量纲三层模型中，前两阶累计方向有效质量参与系数达到95.21%，仅保留两阶重新计算时，第二层剪力峰仍相对完整模型偏差约36.84%～43.32%，说明质量覆盖不能代替局部剪力核验。真实案例将先比较各层整体响应，再在模态向量和响应资料允许的范围内分析叠加及装置出力时序。真实三态前三阶周期和参与质量在摘要显示精度下相同，单阶剪力贡献比例仍待计算。

**关键词**：主体结构；楼层剪力；模态响应；振型叠加；黏滞阻尼器

## Abstract (candidate)

This study examines how modal response amplitudes and their signed superposition affect horizontal story shear in the main structure. Three states are considered: the existing reference structure, a state with an additional three percentage points of modal damping, and a structure equipped with physical dampers. Their inputs and underlying structural models must first be matched. The first three modal contributions will be examined separately, with higher modes grouped and reconstruction errors checked against the complete output. In a previously calculated dimensionless three-story model, the first two modes account for 95.21% of directional effective mass, yet a new two-mode analysis differs from the complete model by approximately 36.84–43.32% in second-story shear peaks. Directional mass coverage therefore cannot replace a local shear check. Available native summaries give matching first-three modal periods and mass ratios at the displayed precision. Node mode-shape vectors and modal response histories are unavailable, so engineering modal shear contributions have not yet been determined.

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

## 5 真实案例：可用资料与现有结果

### 5.1 三种状态的资料对应

既有标签0与标签3各有14工况响应缓存，已有配对记录表明输入逐样本相同；背景阻尼实际数值及标签3对应的逐阶增量仍待核。实体装置状态有六工况核心响应，其与前两态的同输入和完整主体身份尚需对应。因此先分别报告原生结果，再决定哪些状态可以直接比较，暂不把标签写成已落实的阻尼取值。

### 5.2 前三阶模态摘要

三态的前三阶周期及参与质量在表1的显示精度下相同。表中百分数分别对应UX、UY或RZ方向的参与质量，不是某层剪力占比。

**表1 三态前三阶原生模态摘要（在所示精度下相同）**

|阶次|周期/s|主要参与方向|该方向参与质量/%|
|---|---:|---|---:|
|1|2.7781|UY|65.22|
|2|2.7322|UX|64.87|
|3|2.5669|RZ|64.34|

这里的第一阶不能直接称为X向第一阶，第三阶也不能当作平动高阶。实体装置摘要的第一阶参与因子与前两态反号；整体换号不改变振型所代表的运动，符号差异本身不说明形状改变。现有资料缺节点振型向量、模态坐标时程及逐阶层剪力，因此周期和参与质量接近尚不能证明完整振型相同，也不能据此填写各阶剪力百分比。

### 5.3 实体装置状态的楼层响应

六工况的原生Bottom剪力峰最大均在Story1，已记录漂移峰的控制层则分布于Story4、Story5和Story7，见表2。剪力控制层与变形控制层不同，需分别追踪，不能把最大剪力所在层直接视为承载力最不利层。

**表2 实体装置模型的主输入方向记录峰控制层**

|工况|Bottom剪力峰最大所在层|剪力峰/kN|已记录漂移峰控制层|
|---|---|---:|---|
|RH4X|Story1|8916.71|Story5|
|RH4Y|Story1|8426.40|Story4|
|SHW4X|Story1|11043.62|Story5|
|SHW4Y|Story1|10366.27|Story5|
|SHW7X|Story1|9563.90|Story7|
|SHW7Y|Story1|8945.72|Story7|

Bottom的截面侧别、正方向与Link包含关系尚未核清，表2保留原生剪力名称，不改称主体弹性剪力。漂移为稀疏原生记录中的峰值，不作插值补零或固定节点信号；剪力与漂移独立峰也不拼接为同刻剖面。

### 5.4 后续解释与待补结果

真实案例先在可比状态间比较各层整体响应。取得兼容模态向量、质量矩阵及节点响应后，再按第3节列第一至第三阶及较高阶的同刻贡献和重构差。尚缺资料时，小模型只提供机制参考，频带结果保留近似身份。上部四层32只装置的原生力可辅助说明出力时序，不补齐全楼装置力。
