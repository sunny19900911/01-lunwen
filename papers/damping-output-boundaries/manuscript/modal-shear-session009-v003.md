# 振型响应贡献及其叠加对主体楼层水平剪力的影响

**Modal response contributions and their superposition in horizontal story shear of the main structure**

作者、单位及邮编：待作者填写。

## 摘要（候选）

针对总体响应减小而个别楼层剪力改善有限的问题，研究前几阶及较高阶振型响应在主体水平剪力中的叠加作用。拟比较既有基准结构、模态附加阻尼参考状态及设置实体阻尼器三种状态，在核对输入和主体模型后，采用一致参考振型分析各阶响应幅值及关键时刻的有符号贡献。第一、二、三阶分别考察，较高阶合并报告，并用完整输出检查重构误差。已有无量纲三层模型中，前两阶累计方向有效质量参与系数达到95.21%，仅保留两阶重新计算时，第二层剪力峰仍相对完整模型偏差约36.84%～43.32%，说明质量覆盖不能代替局部剪力核验。真实案例将先比较各层整体响应，再在模态向量和响应资料允许的范围内分析叠加及装置出力时序。真实标签0/3的168组主方向层剪力记录峰全部下降6.85%～30.55%，不同楼层减幅及峰时迁移不同。三态前三阶周期和参与质量在摘要显示精度下相同，单阶剪力贡献仍待计算。

**关键词**：主体结构；楼层剪力；模态响应；振型叠加；黏滞阻尼器

## Abstract (candidate)

This study examines how modal response amplitudes and their signed superposition affect horizontal story shear in the main structure. Three states are considered: the existing reference structure, a modal-damping reference state labelled 3, and a structure equipped with physical dampers. Their inputs and underlying structural models must first be matched. The first three modal contributions will be examined separately, with higher modes grouped and reconstruction errors checked against the complete output. In a previously calculated dimensionless three-story model, the first two modes account for 95.21% of directional effective mass, yet a new two-mode analysis differs from the complete model by approximately 36.84–43.32% in second-story shear peaks. Directional mass coverage therefore cannot replace a local shear check. All 168 main-direction story-shear record peaks decrease by 6.85–30.55% from label 0 to label 3, with different reductions and peak-time shifts across stories. Available native summaries give matching first-three modal periods and mass ratios at the displayed precision. Node mode-shape vectors and modal response histories are unavailable, so engineering modal shear contributions have not yet been determined.

## 1 研究问题

增加阻尼后，各阶响应的减小程度未必相同；不同振型对同一楼层剪力的作用也可能相互抵消或加强。只比较屋顶位移、某阶响应峰或累计质量参与系数，尚不能解释目标楼层的剪力变化。本文关注第一至第三阶及更高阶分别影响哪些楼层，减剪来自幅值降低还是关键时刻叠加关系改变，并以装置出力时序补充解释。

Song等分别构造弹性层剪力和包含阻尼作用的广义层剪力，其模态表达使用相应输出系数[1]。本文据此区分不同剪力输出，而不把质量参与率当作剪力占比。Londoño等在线性Maxwell支撑—阻尼器模型中说明，支撑柔度会随频率改变传力幅值与相位[2]。Conde和Bernabeu讨论Maxwell储能、损耗及等能线性化的频率依赖，指出基本振型与高阶振型的表现可能不同[3]。因此，本文将模态附加阻尼参考状态与实体装置状态分别考察，出力时序作为辅助解释，不预设二者等效。

## 2 三种状态及比较条件

|状态|比较内容|需先核对的条件|
|---|---|---|
|既有基准结构|作为响应比较的参照|实际背景阻尼、主体质量刚度及输入；不预设为零阻尼|
|模态附加阻尼标签3|观察参考状态的响应变化|拟定3个百分点的逐阶设置、原有及总阻尼仍需核对；保持输入与主体一致|
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

### 5.3 标签0/3的逐层剪力减幅与峰时迁移

14工况、12层共168组主输入方向的原生Bottom剪力峰，从标签0到标签3全部下降，范围为6.8513%～30.5458%，未发现主方向反增。该结果说明本组输入下整体剪力峰均降低，但各层减幅并不均匀，不能为寻找反例而把降幅较小写成剪力增大。

表2取与实体装置状态共同的六个工况，分别列其中下降最少的楼层。减幅为1−P3/P0，两个峰各取自本状态完整原生记录，不是相同参考时刻的响应差。

**表2 标签0/3共同六工况中主方向剪力减幅最少的楼层**

|工况|楼层|标签0峰/kN|标签3峰/kN|减幅/%|标签0峰时/s|标签3峰时/s|
|---|---|---:|---:|---:|---:|---:|
|RH4X|Story7|6725.06|5438.72|19.128|21.58|21.56|
|RH4Y|Story1|10123.05|8735.50|13.707|12.20|12.20|
|SHW4X|Story1|11399.73|10174.19|10.751|29.94|29.92|
|SHW4Y|Story7|7343.57|6788.32|7.561|29.84|29.86|
|SHW7X|Story7|8481.83|7421.40|12.502|38.12|38.10|
|SHW7Y|Story6|8091.99|6909.98|14.607|48.88|38.10|

共同六工况中，SHW4Y的Story7减幅最小，约7.561%；而同一工况其他楼层可以有更大降幅。全14工况的最小值来自SHW3X的Story5，约6.851%，两者样本范围不同。表中SHW7Y的Story6还出现明显峰时迁移，说明重新寻找本状态的最大值十分必要。

峰时差是两个绝对峰出现时刻之差，不是相位角；它可能伴随不同波包或不同峰的切换。这里先描述减幅不均和控制时刻变化，尚不把它归因于某一阶振型。Bottom输出也保留其原生范围，不能直接改名为已分离的主体弹性剪力。

### 5.4 实体装置状态的楼层响应

六工况的原生Bottom剪力峰最大均在Story1，已记录漂移峰的控制层则分布于Story4、Story5和Story7，见表3。剪力控制层与变形控制层不同，需分别追踪，不能把最大剪力所在层直接视为承载力最不利层。

**表3 实体装置模型的主输入方向记录峰控制层**

|工况|Bottom剪力峰最大所在层|剪力峰/kN|已记录漂移峰控制层|
|---|---|---:|---|
|RH4X|Story1|8916.71|Story5|
|RH4Y|Story1|8426.40|Story4|
|SHW4X|Story1|11043.62|Story5|
|SHW4Y|Story1|10366.27|Story5|
|SHW7X|Story1|9563.90|Story7|
|SHW7Y|Story1|8945.72|Story7|

Bottom的截面侧别、正方向与Link包含关系尚未核清，表3保留原生剪力名称，不改称主体弹性剪力。漂移为稀疏原生记录中的峰值，不作插值补零或固定节点信号；剪力与漂移独立峰也不拼接为同刻剖面。

### 5.5 后续解释与待补结果

真实案例先在可比状态间比较各层整体响应。取得兼容模态向量、质量矩阵及节点响应后，再按第3节列第一至第三阶及较高阶的同刻贡献和重构差。尚缺资料时，小模型只提供机制参考，频带结果保留近似身份。上部四层32只装置的原生力可辅助说明出力时序，不补齐全楼装置力。

## 6 阶段结论

（1）标签0/3的168组主方向楼层剪力记录峰全部下降，减幅为6.8513%～30.5458%；本组数据没有主方向反增。共同六工况中，SHW4Y的Story7降幅最少，后续优先解释其与其他楼层的差异。

（2）前三阶周期及参与质量接近，尚不足以确定各层剪力的组成。质量参与、位移响应和剪力输出系数属于不同量，真实逐阶贡献仍需兼容振型及广义响应。

（3）不同状态的剪力峰时会迁移，应先比较各自完整时程峰，再追踪同刻组成。峰时差不等于相位角；各阶幅值和抵消变化的精确机制将先由已知小模型说明，真实数据只在其资料范围内对应。

## 参考文献

[1] SONG J, CHU Y L, LIANG Z, LEE G C. Modal Analysis of Generally Damped Linear Structures Subjected to Seismic Excitations[R]. Buffalo: University at Buffalo, 2008. MCEER-08-0005. [官方目录](https://www.buffalo.edu/mceer/catalog.html?start=135).

[2] LONDOÑO J M, WAGG D J, NEILD S A. Supporting brace sizing in structures with added linear viscous fluid dampers: A filter design solution[J]. Earthquake Engineering & Structural Dynamics, 2014, 43:1999–2013. DOI:10.1002/eqe.2433.

[3] CONDE J, BERNABEU A. Influence of Maxwell Stiffness in Damage Control and Analysis of Structures with Added Viscous Dampers[J]. Applied Sciences, 2021, 11:3089. DOI:10.3390/app11073089.
