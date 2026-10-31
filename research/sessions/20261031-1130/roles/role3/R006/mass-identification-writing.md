# 18个质心集中质量的识别：工程说明候选段落

角色③写作支持。本文件只转述④R002已冻结结果及其适用范围，不重复识别质量、不提取原件。独审状态另见本目录冻结回执；工程数据结论以②R003和主控裁决为准。

## 方法段落

为减少对旧质量表的依赖，采用实际有控模型中同一Modal工况的质心振型和参与性质，识别18个质心集中方向质量。其依据是：同一组质量应同时解释不同阶振型的质量投影。参与表和振型表采用同一工况、相同模态序号，利用参与量的相对比例消去共同的单位倍率，再由多阶投影关系确定各质心质量所占比例。

X、Y两个方向分别识别。先使用前100阶建立约束，固定质量比例之和为1；在采用的数值秩判据下，两方向约束的秩均为17，对18个质量比例给出一维零空间。归一化后18项权重均为正。识别结果确定后，使用未参与识别的后200阶检查投影关系，再用同源参与质量比及广义质量确定总质量。旧质量数值仅用于事后逐组比较，不参与权重或总质量的确定。

## 结果段落

两个方向得到的总质量均约为47,440,864.27 kg，即47,440.86 t。后200阶的总质量估计相对训练中位数的最大偏差分别约为5.4×10⁻¹¹和1.7×10⁻¹¹。识别的18组方向质量与旧质量表逐组吻合，最大相对差约为3.6×10⁻¹⁴。这一结果支持所采用的18个质心集中质量表达与现有300阶模态投影相容，证据较仅比较全楼质量总和更充分。

上述检查均在同一模型的模态资料内部进行。后200阶没有用于确定质量，但它们仍来自相同模型和同一组输出，因此宜称为留出阶次检查，不写成其他结构或其他地震记录的外部验证。

## 质量投影进入楼层系数的说明

对于所选方向，集中质量表达成立时，切口以上质量投影可由各质心的方向质量和带符号平动振型加权求和。相应有效模态质量可以消去广义质量，因此不必仅为计算该方向质量投影而另行求齐每个质心的转动惯量。若目标是恢复实际模态坐标、完整动能或弹性切口力，则仍应核对相应自由度、质量内积和力恢复关系；这些任务所需的信息各不相同。

当前实际Modal类型为LinModRitz。质量识别推进了质量投影的计算基础，但Ritz切口残差、FNA有效刚度与目标弹性输出之间的差别，以及实际广义坐标时程，仍需分别处理。本文据此报告已识别的集中质量和条件性质量投影，不将它们直接改称真实有限元逐阶弹性剪力。

## 观测广义质量比例的准确用语

④还计算了每阶X/Y质心平动在该集中模型中的广义质量项，除以对应阶原生广义质量。该比值随阶次变化，最大约为0.9927。它描述的是所选坐标对某一阶广义质量项的表达程度，不能写成“全模型质量覆盖99.27%”，也不能据此给出楼层剪力误差上界。不同模式在竖向、转动或其他自由度上的分量不同，比值应逐阶保留。

这一观测检查也不能用来否定已成立的方向质量投影：某个输入方向的投影、完整广义质量和实际模态坐标恢复，对应不同的矩阵运算。是否需要遗漏自由度，应由具体计算对象决定。

## 英文对应段落

The directional masses of eighteen diaphragm centers were identified within a concentrated-mass representation using the signed modal displacements and participation data from the same modal case. Relative participation values were used to eliminate a common unit multiplier. The first one hundred modes determined the normalized mass weights, while the remaining two hundred modes were reserved for checking the resulting projection relations. All identified weights were positive. The directional total masses were approximately 47,440,864.27 kg, and the old mass values were used only for a subsequent comparison.

These checks support the consistency of the eighteen-center mass representation with the available modal projections. They do not, by themselves, establish complete finite element mass coverage or exact elastic story shear recovery. The modal type is LinModRitz; force recovery residuals, the stiffness definition used for the target output, and the actual generalized response histories therefore remain separate requirements.

## 引用及使用说明

- 识别数值仅来自本session④R002 README-CM-mass-identification及其freeze/verification。本文没有将这项工程识别归于Song或CSI。
- 方向输入投影及有效质量定义引用CSI印刷376–377/PDF398–399；原生参与因子的单位映射仍按④使用的比值方法处理，不另拟合倍率。
- 一般模态惯性力分布及基底有效质量引用Song印刷106–108/PDF124–126；局部切口应用和当前工程数据身份单独说明。
- 本文件中的“秩”“相容”“留出阶次”均保持数值与模型范围，不改为精确全空间证明或跨模型预测性能。

工作记录：②R003于12:08:34+08冻结独立审核，数值通过、必须修改0项；独立求解后再读取④数值和旧质量比较。所支持的范围仍为固定18个CM集中方向质量模型；未认证完整有限元质量、Ritz弹性恢复或实际FNA坐标。本项只是依据上述报告组织语言，没有代替该独审再次运行识别。
