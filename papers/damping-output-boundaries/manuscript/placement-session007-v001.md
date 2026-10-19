# 面向主体楼层水平剪力控制的黏滞阻尼器布置调整研究

**Placement adjustment of viscous dampers for controlling horizontal story shear in the main structure**

作者：待作者填写；单位及邮编：待作者填写。

Authors and affiliations: To be supplied by the authors.

## 摘要

针对既有减震结构中阻尼器出力与主体楼层剪力改善并不等同的问题，研究以主体水平层剪力为目标的少量布置调整方法。以某双塔连体结构的既有有控模型为对象，整理3416个节点及分布于11个装置层的88只阻尼器几何，并将上部4层32只阻尼器的原生轴力与三组地震输入各X、Y工况配对。根据装置方向计算水平合力，在统一截面及正方向后逐时求主体剪力，再比较整个计算时程的绝对最大值。现状结果中，Story10在RH4X下的原生Bottom剪力峰为3711.81kN，出现于21.64s；该层阻尼器X向合力绝对峰为363.16kN，出现于16.48s，表明两类峰值不能直接相减。基于真实已有节点，形成两项同层平移和一项相邻层调配草案，保持全楼装置总数及原参数不变，另设置阻尼系数0.8倍和1.2倍的少量辅助比较。明日按相同输入重新计算各层主体剪力、层间位移及装置需求，以确定布置是否值得保留。当前结果为现状受力分析与待检验操作方案，尚未获得改布置后的响应。

**关键词**：黏滞阻尼器；阻尼器布置；主体结构；楼层剪力；时程分析

## Abstract

This study develops a limited placement-adjustment plan for controlling horizontal story shear in an existing damped structure. The geometric data comprise 3,416 nodes and 88 dampers distributed over 11 damper stories. Native axial-force histories of 32 dampers in the upper four damper stories are paired with the X and Y cases of three earthquake-input groups. Horizontal damper forces are calculated from the installation directions. Main-structure shear is evaluated at each time step after the section scope and force directions have been made consistent, and its absolute maximum is then determined over the complete record. In the existing model, the Story10 Bottom shear in RH4X reaches 3,711.81 kN at 21.64 s, whereas the absolute maximum horizontal damper-force sum is 363.16 kN at 16.48 s. These two maxima should therefore not be subtracted directly. Two same-story translations and one transfer between adjacent stories are proposed using existing nodes, while maintaining the total number of dampers and their original parameters. Damping-coefficient factors of 0.8 and 1.2 are reserved for a small supplementary comparison. The revised models will be analyzed under the same inputs to compare story shear, interstory drift and damper demands. The present stage provides existing-response analysis and candidate operations; responses of the modified layouts have not yet been calculated.

**Keywords**: viscous damper; damper placement; main structure; story shear; time-history analysis

## 1 工程问题与研究思路

既有减震结构调整阻尼器位置时，需要判断改变的是否只是装置出力，还是主体各层承担的水平剪力也随之减小。阻尼器水平力、总楼层剪力与主体剪力达到最大值的时刻可能不同，应依据同一时刻的受力关系计算主体剪力，再求其在整个时程内的最大值[1–2]。

布置位置决定装置两端的相对运动，安装方向将轴力转换为结构水平作用[3]。已有时程设计方法将非线性阻尼器、支撑柔度和多项结构响应共同考虑，并通过另外的输入检验方案[4]。具体软件模型还需要明确装置局部轴、力输出与分析设置[5]，支撑柔度也会影响装置有效变形[6]。

本文以现有有控模型为基准，先整理全楼布置与现有原生力，再形成少量可实际改模的位置草案。位置调整为主要变量，阻尼系数的少量变化作为辅助。当前阶段完成方法、现状结果及复算安排；候选之间的选择以调整后结构的时程结果为依据。

## 2 工程资料与既有模型

### 2.1 全楼节点与装置布置

新几何导出包含3416个节点和88只Link装置，所有装置端点均可在节点表中找到。装置分布于Story1—Story11，每个装置层沿X、Y方向各4只。节点最高标高为53.5m，对应Story12标签。装置层数量与节点楼层标签分别描述。

**表1 当前资料覆盖范围**

|资料|实际覆盖|本阶段用途|
|---|---|---|
|节点及装置几何|3416节点、88只装置、Story1—Story11每层4X+4Y；另有Story12节点|定位全楼原布置、计算轴线、形成真实节点候选|
|原生轴力与总轴向变形|Story8—Story11的32只装置，三波族各X/Y共192条器件—工况记录|计算既有上部四层水平合力及装置需求|
|楼层剪力|与上述原生力逐点配对的Bottom输出|检查现状层剪峰、分担及峰值时刻|

几何资料中的Story4端点与此前资料一致，88个装置键也与旧属性赋值集合对应。新导出中非线性参数表无有效数据，参数辅助比较采用经模型核对后的原属性作为基准，不由几何表推定阻尼系数。现有节点位置可以核实几何，候选节点的梁柱连接、支撑及安装空间还需在模型中查看。

### 2.2 输入、原生力及配对

RH4、SHW4、SHW7分别取X、Y方向，形成六个工况。它们是三组输入的方向分量，不作为六个独立地震事件。现有上部四层每个楼层—工况均有8只装置的完整记录，原生力与楼层剪力时间轴一致。原生轴力P在I、J两端重复输出同一标量，每只装置只取一份；U1表示两端总轴向相对变形。

本稿直接使用已有原生P计算这32只装置的水平分力，不再用名义本构重算来替代它。其余装置已有几何，但不据此补齐其力时程。全楼改布置后的力和位移将在新模型求解后取得。

## 3 主体水平层剪力的评价方法

### 3.1 轴力的水平分量及截面受力

以节点I指向节点J定义阻尼器轴向，节点坐标分别为xI、xJ，长度为L，方向余弦为

$$\boldsymbol n=(\boldsymbol x_J-\boldsymbol x_I)/L. \tag{1}$$

若P取正拉力，装置作用在上端J节点的外力为−nP。在结构内力抵抗项一侧，该作用写为+nP。对选定水平截面以上的隔离体，令χJ、χI表示对应端点是否在隔离体内，沿水平轴e的装置抵抗项之和为

$$D_e(t)=\sum_d(\chi_J-\chi_I)n_{e,d}P_d(t). \tag{2}$$

先统一截面、侧别和正方向。若总截面剪力VT包含上述装置项且采用相同抵抗项约定，主体剪力为

$$V_{S,e}(t)=V_{T,e}(t)-D_e(t). \tag{3}$$

目前原生Story Forces只有Bottom输出，其包含范围与侧别需用同位置截面切割核对。核对前，Bottom±De只能作为同一有控响应的两种代数余量，不能从结果较小的一种反推正确符号。

### 3.2 布置前后的比较基准

原有控布置记为M0，单项位置调整模型记为Mm。对每个楼层s、工况k及方向e，分别计算

$$P_{s,k,e}^{(m)}=\max_{t\in T_k}|V_{S,s,k,e}^{(m)}(t)|,\qquad
R_{s,k,e}^{(m)}=P_{s,k,e}^{(m)}/P_{s,k,e}^{(0)}. \tag{4}$$

分母取同输入、同楼层及同物理输出的M0峰值；接近零时另报绝对值，不用小量强行形成比值。所有工况和楼层逐项列出，再用其最大比值识别是否有其他楼层恶化。原有控模型即可作为位置调整的直接基线；如另外比较设置阻尼器前后的减震率，需另设相应无装置模型。

主体剪力为主目标，同时列层间位移、屋顶响应、装置轴力及总变形。若增加楼层恢复力或其他约束，应单列其定义与要求，不用附加指标替代主体层剪力。所有峰均来自各自完整时程，不用不同信号的独立峰值相减。

## 4 现有布置的受力结果

### 4.1 上部四层原生水平出力

表2以RH4的X、Y工况展示已覆盖四层的原生Bottom剪力和装置水平合力。装置合力按式(2)的+nP抵抗项记号给出；主输入方向每层实际有4只非零水平投影装置，另一方向装置不混入该轴合力。

**表2 既有有控模型的原生峰值与同刻装置水平合力**

|层|工况/方向|Bottom绝对峰/kN|对应时刻/s|装置水平合力绝对峰/kN|对应时刻/s|Bottom峰时装置合力/kN|
|---|---|---:|---:|---:|---:|---:|
|Story8|RH4X/X|5776.65|21.60|405.83|11.50|-238.11|
|Story8|RH4Y/Y|5205.21|21.58|447.20|11.46|-279.63|
|Story9|RH4X/X|4896.35|21.62|385.60|16.44|-244.69|
|Story9|RH4Y/Y|4441.65|21.62|434.62|16.42|-254.85|
|Story10|RH4X/X|3711.81|21.64|363.16|16.48|-249.11|
|Story10|RH4Y/Y|3395.92|21.64|411.91|16.46|-258.22|
|Story11|RH4X/X|1797.28|21.68|320.97|16.54|-253.57|
|Story11|RH4Y/Y|1746.17|12.30|369.98|16.50|238.61|

Story10/RH4X的Bottom峰出现在21.64s，而装置X向合力绝对峰出现在16.48s。在21.64s，Bottom有符号值为+3711.81kN，装置抵抗项为−249.11kN，二者方向相反。由于软件截面包含性尚待核对，这里不将某一种加减结果命名为实际主体剪力。

三组输入中，已覆盖上部四层的Story8在SHW7X下Bottom峰约7132.29kN，在SHW7Y下约6707.70kN，可优先查看该层及邻层。总剪力大小还需结合主体刚度、层高和承载力，不能单凭它认定全楼最不利楼层。

### 4.2 现状结果对调整的启示

现有数据已经说明，应同时检查装置水平出力的方向、大小和发生时刻，再观察主体峰是否出现在其他时刻。移动装置后，两端相对运动和装置力都会改变，因此不能把旧力时程直接移到新位置，也不能按旧力乘倍率预填改布置后的减幅。

当前可用的原生力覆盖Story8—Story11，最终比较仍需检查全楼。若只改善目标层而使移出层、下部楼层或装置需求变差，应将这些变化同时列入方案比较。

## 5 待检验的少量位置与参数方案

### 5.1 三项未排序的位置草案

表3给出基于真实已有节点形成的三项草案，每个模型先只改一只装置。P1、P2为同层平移，P3为相邻层调配。编号用于区分操作，不表示优选顺序。最终保留哪两项或是否替换，应结合控制层、连接点运动及安装条件再确定。

**表3 单项位置调整草案（尚未计算改后响应）**

|草案|原装置/所在层|原I→J|拟改I→J|改动内容|
|---|---|---|---|---|
|P1|K83／Story8，Y向|2270→2361|2281→2421|Y向装置沿X平移2.717m，仍在Story8|
|P2|K10／Story8，X向|2203→2398|2272→2563|X向装置沿Y平移1.350m，仍在Story8|
|P3|K82／Story9，Y向|2554→2644|Story8的2281→2421|向下调配一层并沿X移动2.717m|

**表4 候选端点坐标与安装几何（坐标单位m）**

|草案|原I；原J坐标|拟改I；拟改J坐标|原/新几何长度|原/新轴线与水平夹角|
|---|---|---|---:|---:|
|P1|(67.655,55.115,31.200)；(67.655,62.810,35.500)|(64.938,55.115,31.200)；(64.938,62.810,35.500)|均8.814932m|均29.196652°|
|P2|(110.255,30.310,31.200)；(115.305,30.310,35.500)|(110.255,31.660,31.200)；(115.305,31.660,35.500)|均6.632684m|均40.413901°|
|P3|(67.655,55.115,35.500)；(67.655,62.810,39.800)|(64.938,55.115,31.200)；(64.938,62.810,35.500)|均8.814932m|均29.196652°|

三项均保持全楼88只装置及其原参数。P3使Story8由8只变9只、Story9由8只变7只，需特别比较移出层的不利影响。P1和P3采用同一新节点对，应分别建模，不能同时实施。表中长度为节点间几何长度，实际装置、支撑和锚固构造需一并检查。

同层平移还需检验是否改变装置运动。在上下楼层均只有水平刚体平动、且轴线不变的情况下，P1、P2的两端轴向相对运动不变；实际平动、扭转及局部变形可能使不同位置有差异。因此，它们首先是局部运动与可安装性的对照，尚不能仅凭换跨就判断更有效。P3改变沿高度的分配，作用更直接，但可能同时增加Story9或其他楼层响应。

### 5.2 阻尼系数的辅助比较

位置先比较，参数后比较。对保留的位置模型，将经模型核对的原阻尼系数记为c0，只增加表5两项辅助计算。复制为独立装置属性并明确赋给选定装置，避免改动共享Link1而使全楼装置同时变化。

**表5 少量参数对照**

|计算|所选位置|阻尼系数|串联刚度与速度指数|用途|
|---|---|---|---|---|
|原参数|保留的位置模型|c0|保持原κ0、α0|位置比较基准|
|小幅减小|与上行相同|0.8c0|保持原κ0、α0|检查剪力与装置需求对c的敏感性|
|小幅增大|与上行相同|1.2c0|保持原κ0、α0|与上行及原参数共同判断|

该倍率是待计算的工程幅度，不表示阻尼力或减幅将同比变化。若改动的是一个局部装置组，应事先列明组内所有编号并在两组参数模型中保持相同。

## 6 明日模型修改与复算安排

先另存原有控模型M0，并核对输入、质量刚度、背景阻尼、装置属性、模态/FNA设置、输出步长和完整计算时长。除本次明确改变的位置或c外，其他条件保持一致。

**表6 建议的操作与输出顺序**

|顺序|具体操作|必须保留的结果|
|---|---|---|
|1|在M0查看原/新节点相连构件、刚臂、支撑及安装空间|确认实际可实施的候选，不可实施者及原因也记录|
|2|在Story10/RH4X、21.64s作同位置主体截面与含Link截面核对|统一Bottom包含范围、侧别、正方向及对应有符号力|
|3|分别另存单项位置模型，P1/P3分开；记录旧/新节点及装置属性|M0及实际保留的M1、M2等模型清单|
|4|保持原三组输入的方向、倍率、持时及分析设置重新求解|全楼同截面主体层剪力及各自峰值/峰时，保留交叉方向|
|5|比较层间位移、屋顶响应、装置轴力与总变形|目标层改善、其他层代价及装置需求增大同时报告|
|6|位置方案保留后再作0.8c0、1.2c0两项辅助比较|同输入、同位置的完整响应；不能只缩放旧力|

原装置布局是位置调整的直接对照。方案若未使目标层更合理，或其他楼层、变形及连接需求的代价过大，保留原方案或更换候选。局部节点位置的改变不能替代全楼复算。

## 7 阶段结论

（1）新几何覆盖3416个节点、88只装置和11个装置层，最高节点另有Story12标签、标高53.5m。后续布置比较应覆盖全楼，并区分装置所在层与其他节点层。

（2）上部四层32只装置的原生轴力已可按真实方向转换为水平合力。Story10/RH4X的Bottom剪力与装置合力分别在21.64s和16.48s达到绝对最大值，主体剪力必须按同一时刻计算。Bottom截面的包含范围及侧别核对后，再形成相应主体剪力结果。

（3）现已形成两项同层平移和一项相邻层调配草案，均保持全楼88只装置。P1与P3互斥，P3需检查移出层代价；P1、P2则需先判断平移能否改变实际相对运动。三者尚未按减震效果排序。

（4）明日以原有控M0为基线，先比较少量位置模型，再辅助比较0.8c0与1.2c0。各层主体剪力、变形及装置需求应共同列出，改布置后的改善程度由新时程结果确定。

## 参考文献

[1] REINHORN A M, LI C, CONSTANTINOU M C. Experimental and Analytical Investigation of Seismic Retrofit of Structures with Supplemental Damping, Part 1: Fluid Viscous Damping Devices[R]. Buffalo: NCEER, 1995. NCEER-95-0001. [大学原件](https://www.eng.buffalo.edu/mceer-reports/95/95-0001.pdf).

[2] SONG J, CHU Y L, LIANG Z, et al. Modal Analysis of Generally Damped Linear Structures Subjected to Seismic Excitations[R]. Buffalo: University at Buffalo, 2008. MCEER-08-0005. [官方目录](https://www.buffalo.edu/mceer/catalog.html?start=135).

[3] LIN W C, WANG S J, HWANG J S, et al. Improvement of configuration and corresponding design formulation for viscous dampers in Taiwan[R]//NATIONAL CENTER FOR RESEARCH ON EARTHQUAKE ENGINEERING. 2016 NCREE Research Programs and Accomplishments. [S.l.]: National Center for Research on Earthquake Engineering, 2017:77–80. [官方汇编](https://www.ncree.narl.org.tw/assets/file/105E4.pdf).

[4] DE DOMENICO D, HAJIRASOULIHA I. Multi-level performance-based design optimisation of steel frames with nonlinear viscous dampers[J]. Bulletin of Earthquake Engineering, 2021, 19:5015–5049. DOI:10.1007/s10518-021-01152-7. [正式原文](https://doi.org/10.1007/s10518-021-01152-7).

[5] COMPUTERS & STRUCTURES, INC. CSi Analysis Reference Manual: for SAP2000, ETABS, SAFE and CSiBridge[M]. Rev.15. Berkeley: Computers & Structures, Inc., 2016. ISO#GEN062708M1. [官方手册入口](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf).

[6] LONDOÑO J M, WAGG D J, NEILD S A. Supporting brace sizing in structures with added linear viscous fluid dampers: A filter design solution[J]. Earthquake Engineering & Structural Dynamics, 2014, 43:1999–2013. DOI:10.1002/eqe.2433. [机构原文](https://eprints.whiterose.ac.uk/id/eprint/81371/1/WRRO_81371.pdf).


资料范围、完整现状表与研究过程另见[本阶段补充说明](../../../research/sessions/20261019-2045/roles/role5/R003-补充说明.md)。
