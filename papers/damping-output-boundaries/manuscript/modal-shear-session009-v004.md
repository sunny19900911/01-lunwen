# 楼层水平剪力减幅差异及振型叠加的模型解释

**Differences in horizontal story-shear reduction and a modal-superposition explanation using a known model**

作者、单位及邮编：待作者填写。

## 摘要

为解释阻尼响应改善在不同楼层间的差异，比较既有标签0、模态附加阻尼标签3及实体装置三类原生计算结果，并在已知三层模型中分析振型响应的有符号叠加。已核同输入的标签0/3共14工况、12层、168条主方向Bottom剪力记录峰全部下降，减幅6.85%～30.55%，各层改善程度不同。共同六工况中，SHW4Y的Story7减幅最小，为7.561%。实体模型与标签3的72项对应峰值中，34项较高、38项较低，模型身份尚未完全配对，故分别解释。三态X向主要质量参与阶次为2/4/10，Y向为1/5/11，不能作为层剪力贡献排名。三层模型的同刻分解表明，第三阶在第二层剪力峰时与前两阶同向，而在屋顶峰时较小且反向；该模型前两阶累计方向质量达95.21%，仍不能保证局部剪力的两阶重构精度。结果说明应先确定具体输出和控制时刻，再区分整体减幅、各阶幅值及抵消关系。

**关键词**：楼层剪力；模态响应；振型叠加；黏滞阻尼器；时程分析

## Abstract

Native response results from reference label 0, modal-damping label 3 and a physical-damper model are compared to examine differences in horizontal story-shear reduction. Signed modal superposition is studied separately in a known three-story model. All 168 main-direction Bottom shear peaks from 14 cases and 12 stories decrease between the input-matched label-0 and label-3 states, by 6.85–30.55%. Story7 under SHW4Y has the smallest reduction among the six common cases, at 7.561%. Of 72 corresponding peaks, the physical-damper model is higher than label 3 in 34 and lower in 38; incomplete model matching prevents a damping-only interpretation. Modes 2/4/10 dominate directional mass participation in X, while modes 1/5/11 dominate in Y; these are not story-shear rankings. In the known model, the third-mode term reinforces the first two at the second-story shear peak but is smaller and opposing at the roof-displacement peak. Even 95.21% cumulative directional mass coverage does not ensure accurate local two-mode reconstruction. The results distinguish overall peak reduction from modal amplitudes and signed cancellation at specified times.

## 1 工程问题与已有基础

同样的阻尼设置变化，在不同楼层未必产生相同减幅。屋顶位移、方向有效质量参与系数和楼层剪力分别对应不同输出；解释减剪时，需要先确认实际比较的是哪种剪力、哪一层及哪个时刻。

Song等分别建立弹性层剪力与含阻尼作用的广义层剪力，二者采用不同输出系数[1]。Londoño等在线性Maxwell模型中说明，支撑柔度会随频率改变传力幅值和相位[2]。Conde和Bernabeu讨论储能、损耗及等能线性化的频率依赖，指出基本与高阶振型的表现可能不同[3]。本文据此先报告真实逐层响应差异，再以已知模型分析同刻叠加；装置出力时序作为辅助解释。

## 2 资料对照与模态输出方法

### 2.1 三类原生结果及比较范围

标签0与标签3各含14工况，已有输入配对记录表明输入逐样本一致。标签0不代表零阻尼；标签3的实际逐阶阻尼设置仍未由现有摘要落实。实体装置模型覆盖RH4、SHW4、SHW7各X/Y六工况；其与前两态的输入及完整主体身份尚未全部配对。因此，标签0/3的逐层比较和三态描述性对照分开报告。

各层比较均保留原生Bottom剪力名称，以自身保存时程绝对最大值为峰。令两态对应峰为P0、P3，减幅定义为1−P3/P0。峰时分别来自各态，不把两个独立峰当成同一时刻。Bottom的截面侧别、正方向与Link包含关系未闭合，当前实楼结果不改称已剔除装置项的主体弹性剪力。

### 2.2 方向阶次与精确分解的区别

三模型前三阶周期在所示精度下相同，约为2.7781、2.7322、2.5669s；主要方向参与质量分别为第一阶UY 65.22%、第二阶UX 64.87%、第三阶RZ 64.34%。原生参与因子换号本身不说明振型形状改变，周期接近也不足以证明完整形状相同。

进一步在各自300阶摘要中按方向质量率排序，三模型X向前三重要阶次均为2/4/10，Y向为1/5/11。全局1/2/3阶不是任一方向的前三剪力贡献。当前摘要缺节点振型及广义响应，不能恢复实楼精确单阶剪力占比；以下精确叠加仅用于资料完整的已知模型。

### 2.3 已知模型的弹性剪力输出

线弹性主体的弹性层剪力可写为固定输出F_IS=T_SK u；含阻尼的广义层剪力另由T_S(C udot+Ku)构造[1]。取第s层时，令ℓsᵀ=e_sᵀT_SK。在完整质量归一实参考基ΦᵀMΦ=I下，将u=Φq代入，得到本文使用的展开：

$$V_s(t)=\ell_s^Tu(t)=\sum_r(\ell_s^T\phi_r)q_r(t),\qquad q=\Phi^TMu.$$

式中剪力系数包含刚度和输出映射，不等于输入方向的质量参与率。各阶先在同一时刻有符号相加，再求整体绝对峰；第一至第三阶与其余阶分别组织。只用部分基时保留重构剩余项。非线性装置方案中的q来自完整耦合响应投影，不将各阶当作互不耦合的独立系统。

## 3 实楼逐层减幅及三类结果差异

### 3.1 标签0/3的减幅与峰时

14工况、12层共168条主方向记录峰全部下降，减幅为6.8513%～30.5458%，未发现主方向反增。表1列与实体模型共同的六工况中各自下降最少的楼层。

**表1 标签0/3共同六工况的最小减幅记录**

|工况|楼层|P0/kN|P3/kN|减幅/%|峰时0→3/s|
|---|---|---:|---:|---:|---|
|RH4X|Story7|6725.06|5438.72|19.128|21.58→21.56|
|RH4Y|Story1|10123.05|8735.50|13.707|12.20→12.20|
|SHW4X|Story1|11399.73|10174.19|10.751|29.94→29.92|
|SHW4Y|Story7|7343.57|6788.32|7.561|29.84→29.86|
|SHW7X|Story7|8481.83|7421.40|12.502|38.12→38.10|
|SHW7Y|Story6|8091.99|6909.98|14.607|48.88→38.10|

共同六工况中，SHW4Y的Story7减幅最小，约7.561%；全14工况最小值则来自SHW3X的Story5，为6.851%。样本范围不同，不能混作同一最小记录。本组各层记录均下降，但降幅随楼层和输入变化。

全14工况最大绝对峰时迁移为12.76s。峰时差可能包含不同波包或控制峰的切换，不是相位角，也不能单独判定某阶模态因果。

### 3.2 三态原生峰值对照

**表2 两组已核记录的三态峰值与各自峰时**

|工况／楼层|标签0峰/kN|标签3峰/kN|实体峰/kN|三态各自峰时/s|实体/标签3|
|---|---:|---:|---:|---|---:|
|SHW4Y／Story7|7343.5700|6788.3221|6715.1270|29.84／29.86／29.92|0.98921749|
|RH4X／Story1|10566.7533|8528.6654|8916.7141|21.68／12.20／12.08|1.04549934|

72个共同工况—楼层记录中，实体峰高于标签3为34项、低于为38项。RH4X／Story1的实体峰比标签3高约4.55%，而SHW4Y／Story7略低。这些是三类输出存在差异的描述，不据此比较两种阻尼方式的因果优劣。

实体模型六工况的原生剪力峰最大均在Story1，稀疏漂移记录中的控制层则为Story4、5或7。剪力峰所在层与变形控制层不同，且均不等于承载力最危险层。上部四层32只装置的原生力可补充查看出力时序，不据此补齐全楼装置作用。

## 4 已知三层模型中的振型叠加解释

采用已计算的无量纲三层模型，M=diag(1,1.2,.8)，K=[[2.4,−1,0],[−1,1.7,−.7],[0,−.7,.7]]，背景C=.02K。H2为既有包络多频输入，完整保存状态覆盖t∈[0,200]、步长h=.005。比较无装置与第一层一只κ=.5、c=.02、α=.3的装置方案，按同一参考基投影；QS2=u2−u1，roof=u3。

**表3 完整输出各自峰时的有符号模态项（模型量及时间无量纲）**

|方案／输出|t|第1阶|第2阶|第3阶|三阶和|
|---|---:|---:|---:|---:|---:|
|无装置／QS2|20.215|-0.024113170|-0.002564914|-0.039675603|-0.066353687|
|无装置／roof|70.395|+0.033002219|+0.171593784|-0.003758265|+0.200837738|
|层1装置／QS2|20.090|-0.027078427|-0.002214950|-0.033446139|-0.062739516|
|层1装置／roof|20.510|-0.045631229|-0.113265030|+0.004794006|-0.154102254|

每行的三项取自同一时刻；不同行是各自输出峰时，不能逐项相减解释装置因果。无装置QS2在t=20.215达到完整峰，第三阶约−.0396756，与前两阶同向，加强了局部剪力。只保留前两阶时，其峰改在17.225出现，前两项和约+.0376083，第三项则为−.0039561并反向抵消。因此，两阶峰与完整峰之差也不能直接叫作某一任选时刻的第三阶贡献。

无装置屋顶在其完整峰时，第三阶约−.0037583，与前两阶和反向，且相对较小。删除第三阶后的屋顶峰略增，而QS2峰明显偏小；第一层装置方案也呈现这一输出差异。完整状态后验删阶的QS2峰分别低估43.3215%和41.6360%，屋顶峰分别高估1.8839%和3.1416%。

该模型前两阶累计方向有效质量为95.2108%，仍有上述局部重构差。上述差异属于同一完整状态的后验删阶；减少振型后重新求解是另一类分析。质量覆盖不能代替目标层剪力核查。这里的模型机制不移作实楼逐阶占比。

## 5 讨论与阶段结论

（1）已核同输入的标签0/3记录中，168条主方向剪力峰全部下降6.85%～30.55%，但改善程度随楼层和输入变化。共同六工况中的SHW4Y／Story7仅下降约7.561%，应与较大减幅记录分别解释。

（2）方向参与排序与剪力贡献排序不同。三态X向主要参与阶次为2/4/10、Y向为1/5/11；周期与参与质量接近不能据以恢复各层实际响应组成。

（3）已知模型中，第三阶在局部剪力峰时可与低阶同向加强，在屋顶峰时却较小且反向。评价叠加应固定物理输出和时刻，再观察幅值与抵消；各阶独立峰不能直接相加，峰时迁移也不等同相位角。

（4）实体装置与标签3的72项峰值有34高、38低，当前仅作输出描述。工程整体结果与小模型机制分别成立，不将其拼成单一阻尼因果或实楼精确模态分解。

## 参考文献

[1] SONG J, CHU Y L, LIANG Z, LEE G C. Modal Analysis of Generally Damped Linear Structures Subjected to Seismic Excitations[R]. Buffalo: University at Buffalo, State University of New York, 2008. Technical Report MCEER-08-0005.

[2] LONDOÑO J M, WAGG D J, NEILD S A. Supporting brace sizing in structures with added linear viscous fluid dampers: A filter design solution[J]. Earthquake Engineering & Structural Dynamics, 2014,43:1999–2013. DOI:10.1002/eqe.2433.

[3] CONDE J, BERNABEU A. Influence of Maxwell Stiffness in Damage Control and Analysis of Structures with Added Viscous Dampers[J]. Applied Sciences, 2021,11:3089. DOI:10.3390/app11073089。

来源定位、完整比较及模型表采用状态见[补充说明](../../../research/sessions/20261020-1844/roles/role5/R004-notes.md)。
