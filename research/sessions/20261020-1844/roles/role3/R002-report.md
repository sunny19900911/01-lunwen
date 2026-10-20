# R002：第3节模态剪力方法的引用定位

**第3节弹性输出式有合适引用。** Song等[1]的PDF56/印38式(3.58)直接给出F_IS=T_S Kx。v002可先说明“主体弹性层剪力是位移的固定线性输出[1]”，再采用已声明的完整质量归一参考基。稿中求和式是将u=Φq代入该输出的直接展开，不宜称为Song原文同一公式。对其第s层，ℓ_sᵀ可对应e_sᵀT_SK，已包含主体刚度和楼层力汇总。

## 引用定位表（8行）

|本文采用的内容|原文定位|能支持的具体表述|不能据此推出|
|---|---|---|---|
|主体弹性剪力为固定线性输出|[1] PDF56/印38，§3.3.2式(3.58)|F_IS=T_SKx，选取一行即可定义ℓ_sᵀu|原生Bottom剪力必然就是该弹性输出|
|完整参考基下的位移与坐标|[1] PDF58/印40，§3.3.7式(3.63)为模态组合背景；稿内另明示ΦᵀMΦ=I|u=Φq、q=ΦᵀMu按稿内完整参考基定义使用|把该投影恒等式说成原文式(3.63)原样公式，或由此得到非线性装置逐阶独立方程|
|各阶对层剪力的输出系数|[1] PDF56式(3.58)，PDF58式(3.63)|本文代入得到V_s=Σ_r(ℓ_sᵀφ_r)q_r，各输出系数不同|把输入方向质量参与系数当作某层剪力占比|
|有符号时程叠加及整体峰|[1] PDF58式(3.63)的时程组合形式；峰值操作为本文直接应用|同一时刻求和，再取整个计算时程的绝对最大值|把各阶各自峰值相加写成实际整体峰|
|弹性剪力与含阻尼剪力分开|[1] PDF56，式(3.58)与§3.3.3式(3.59)|前者由Kx构造，后者由Cẋ+Kx构造|混用两种输出的模态贡献或以同一名称报告|
|前几阶与较高阶组合针对具体输出|[1] PDF56式(3.57)–(3.59)、PDF58式(3.63)|位移、漂移、剪力采用各自输出变换，不能仅按质量覆盖判断局部剪力|质量累计达到某百分比即保证各层剪力同等重构精度|
|实际线性Maxwell传力相位|[2] PDF4/印2001式(1b)、(2)、(5)；PDF5/印2002 §2.1、图2|支撑柔度使传力幅值和相位随频率变化|把该线性滤波相位直接用作α=.3器件的精确相位，或视作固定附加阻尼比|
|模态附加阻尼与实体器件分开比较|[3] PDF4 §2.1式(4)–(6)及其后基本/高阶讨论，式(9)|实体Maxwell含储能、损耗和频率作用，等能线性化还依赖参考幅频|软件指定增加3个百分点即与当前器件逐阶等效，或实体器件必改变振型形状|

表中“本文代入/应用”与“原文直接表达”已分列，局部引用号[1]—[3]供作者统一并入全文。

## 可放入第3节的一段理论基础

主体保持线弹性时，楼层弹性剪力可由位移通过固定线性输出得到；含阻尼作用的广义层剪力则采用另一输出变换[1]。在完整质量归一参考振型基下，将位移展开代入弹性输出，可得到各阶广义响应及其剪力系数的有符号组合。本文在同一时刻叠加各阶贡献，再求剪力绝对最大值，以考察响应幅值变化与抵消、加强关系。支撑柔度会使Maxwell装置传递力的幅值和相位随频率变化[2]，其储能、损耗及对基本与高阶振型的作用也不同[3]；因此，模态附加阻尼模型与实体阻尼器模型分别计算，并按同一剪力输出比较其响应。

## 完整参考文献（3条）

[1] SONG J, CHU Y L, LIANG Z, LEE G C. Modal Analysis of Generally Damped Linear Structures Subjected to Seismic Excitations[R]. Buffalo: University at Buffalo, State University of New York, 2008. Technical Report MCEER-08-0005. Publication date: 2008-03-04. [已读正式原件](<E:/11-工作/001-workbuddy spaceV1/001-workbuddy space/109-论文写作/W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence/MCEER-08-0005.pdf>)。

[2] LONDOÑO J M, WAGG D J, NEILD S A. Supporting brace sizing in structures with added linear viscous fluid dampers: A filter design solution[J]. Earthquake Engineering & Structural Dynamics, 2014,43:1999–2013. DOI:[10.1002/eqe.2433](https://doi.org/10.1002/eqe.2433)。

[3] CONDE J, BERNABEU A. Influence of Maxwell Stiffness in Damage Control and Analysis of Structures with Added Viscous Dampers[J]. Applied Sciences, 2021,11:3089. DOI:[10.3390/app11073089](https://doi.org/10.3390/app11073089)。

本轮仅复用R001已核三份原文，为v002第3节提供引用与表述；没有改稿、检索、下载或科学计算。
