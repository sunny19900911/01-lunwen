# R003 Link轴向正号、质量与功端口接口

会话20261017-2109；角色3；2026-10-17 21:53:10 +08开始，单项≤10分钟。仅复用CSI既有手册及官方API定义，candidate交主控/角色2/4；不代替当前原生单元验证。R001/R002保持冻结。

**可认证部分：手册U1对应u₁ⱼ−u₁ᵢ，P对应轴向内部弹簧力，两者形成一个轴向本构功端口；Link属性质量集中至节点，不在单元内部产生惯性。不能认证部分：当前Element Joint Forces表/LinkJointForce的作用对象、坐标以及是否包含集中节点质量项，所读API未说明，仍unknown。**

## 1. 原页证据链

主来源：CSI *Analysis Reference Manual*, July2016 Rev15，[官方原件](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf)。既有本地PDF SHA256：`7f6f6890afee2e1890d33f5d34d53d8e23f60850890bd230848642b50a6291ac`。本次实际渲染并看了PDF283/288/289/293/295原页；其余下列位置为文本复读。

| 原文位置 | 已核定义 | 接口意义 |
|---|---|---|
| 印p255/PDF277，Longitudinal Axis1 | 有限长度Link的+1轴从I指向J；零长度默认+Z，另有高级轴定义 | Angle=0不是“轴向一定等于全局X”。当前I/J顺序与几何/局部轴必须另外核。 |
| 印pp260–261/PDF282–283，Internal Deformations | 二节点轴向du1=u1j−u1i；剪切还含端部转动项 | U1是相对轴向变形；不能以一个节点的位移或全局X位移直接代替。 |
| 印p266/PDF288，Figure65及Spring Force-Deformation Relationships | 图示正P在I端沿−1、J端沿+1；对应内部轴向弹簧fu1–du1 | 同一标量P对应相反端面方向，不是两端同向物理外力。 |
| 印p267/PDF289，Element Internal Forces及Eqn.1 | P=fu1，且这些内部力在单元各截面存在；线性轴向关系fu1=ku1 du1 | 轴向P是本构内部力；正P与伸长的内部正号相容。弯矩可另含剪力臂，不能把所有端部结果都视为常数。 |
| 印p273/PDF295，Internal Force and Deformation Output | 输出P/V/T/M对应内部力；U1/U2/U3/R1/R2/R3对应du1/du2/du3/dr1/dr2/dr3 | 关闭“Element Forces–Links P ↔ Element Deformations–Links U1”在手册定义层的映射；不自动关闭当前具体版本/表端口恢复细节。 |
| 印p271/PDF293，Mass | Link质量集中至I/J；单元本体内部不考虑惯性；总平动质量m各一半分给两个端节点的三个平动自由度 | 不能把mü另塞进P本构力；但总节点平衡必须保留已装配的该质量。单节点支承另有一半质量接地。 |
| 印pp334–335/PDF356–357，Mass Source | Link属性质量属于Element Self Mass；每个Mass Source可选择是否计入这一来源 | “属性Mass=25kg”并不独自证明当前分析M已计入。须核当前工况质量源、约束/自由度及装配结果。 |

原页图保存在本角色local-cache，已忽略且不上传：R003-CSI2016-PDFpage-283/288/289/293/295.png。其他角色同机可按manifest位置查看；Git交接只有自写定位与散列，不代表已共享原页。

## 2. 正号与轴向虚功：先定义作用对象

以下是根据手册定义整理的接口恒等式，**不是API对LinkJointForce作用对象的声明**。在一致局部坐标及二节点轴向通道中，令d=U1=u1j−u1i。为表示传入无质量本构子系统的正功，定义节点施加给Link的两端轴向力

\[
q_i^{\mathrm{node\to link}}=-P,\qquad
q_j^{\mathrm{node\to link}}=+P,
\qquad q_i\,\delta u_{1i}+q_j\,\delta u_{1j}=P\,\delta d.
\]

Link施加给结构节点的力为上述反号。若另一张表报告的是构件对节点、或在不同局部坐标下的量，必须相应换号/旋转后再作端口功；不能把表名相近当作同一约定。图65的箭头与这一内部正号一致，但当前节点力输出的作用对象仍待原生证据。

因此，轴向通道的端部输入功应按**一次**∫P dU1累计。若I/J只是同一轴向内部截面量的两条记录，P相同在该定义下合理；它不是两只装置，也不能把两行加起来做2P或两遍耗能。当前Location/PointElm与实际I/J的对应仍须连通性字段确认，不能仅凭两列相等认证。U1属于整个单元相对变形，不为两个端节点各复制一次。

只有轴向通道被研究、其他通道功另计或为零时，P dU1才代表所需的整器件变形功；“仅U1非线性激活”不证明其他通道的线性弹性储能全为零。对于Maxwell，变形功还包含串联弹簧储能差，不能直接等于纯黏滞耗散。R001已列的端部功减Δ(P²/2k)条件仍适用；k未取得前该修正不作数值认证。

正回线面积、拟合残差小、两端P相同均不能决定缺失的坐标/作用对象/输出端口定义。翻转局部轴时应同步变换力与变形；不得只翻一个量的符号来凑耗能。

## 3. 25kg质量如何进入、不能进入什么

按手册二节点规则，**若当前质量源计入该属性质量**，m=25kg意味着I端及J端各12.5kg用于每个平动方向，而不是再把12.5除以3。它是各方向质量矩阵系数的说明，不是三份独立实体质量；转动惯量是另行指定的属性。实际装配还受节点自由度、约束与质量源影响，本轮不认证当前M数值。

| 对象 | 质量/功的处理 |
|---|---|
| 手册内部力P及轴向本构端口 | P=fu1，无单元内部惯性项；∫P dU1是该通道的变形功，不包含节点集中质量的动能变化。 |
| 全结构节点平衡 | 需要完整装配质量和对应加速度，包括已计入的Link质量；不能把它算入M后又当作P再加一次。 |
| 含两个附属节点质量的局部子系统 | 若端口力确实包括驱动这些质量的作用，端口总功还需分离其动能变化及其他通道功；没有理由自动等于∫P dU1。 |
| 当前Element Joint Forces/LinkJointForce | 所读官方API没有说明集中质量惯性恢复是否计入，**unknown**。不能从“Link内部无惯性”跨步断言此输出也绝不含节点质量项。 |

总节点功还要求确认力作用方向、全部平动/转动通道和统一参考系。含惯性端口时，绝对与相对运动的基底功不可混算；R002中Story Accelerations身份尚unknown，不能用它冒充这些端节点的已知加速度/速度来补质量功。P若为kN、U1为mm，功先换至kN·m；质量kg乘m/s²为N，比较力前另换kN。

## 4. 官方API读取结果及unknown边界

本轮通过已读cAnalysisResults索引定点读三页；本版参数说明空白，仅签名/类型可核，未用JointReact类比补定义。

| 方法 | 可核返回接口 | 不能从本页得到 |
|---|---|---|
| [LinkForce](https://docs.csiamerica.com/help-files/etabs-api-2016/html/948a79a2-904f-21f2-eb6d-00a209dfc3eb.htm) | P,V2,V3,T,M2,M3，含Obj/Elm/PointElm及工况步 | 当前数据库I/J行身份的完整定义、惯性恢复细节 |
| [LinkDeformation](https://docs.csiamerica.com/help-files/etabs-api-2016/html/bb15d4bf-e983-61ef-25f2-993bdbeb82e3.htm) | U1,U2,U3,R1,R2,R3，含Obj/Elm/工况步，**无PointElm** | 不能据另一个端点标签强行复制为两个独立变形端口 |
| [LinkJointForce](https://docs.csiamerica.com/help-files/etabs-api-2016/html/4500bd02-6a4f-2728-6de4-433a5ce2aaa0.htm) | F1,F2,F3,M1,M2,M3，含PointElm及工况步 | 力坐标、node→element或element→node、是否含集中质量惯性均未明示，保留unknown |

手册定义与当前软件/数据库表版本之间仍需一次实证绑定。本次只作接口原文映射，不声明已经验证某只原生Link的节点功闭合。

## 5. 交角色2/4的下一项最小检验

选一只**时间完整、I/J连接与局部轴可确认**的Link，同一工况/时刻取P、U1、两端有符号节点运动、Element Joint Forces、当前Mass Source与节点装配质量。先用局部投影重构U1并核I/J行映射；再在已知作用对象/坐标后比内部轴力的端部转换。对含惯性端口另核质量动能项，不能预设其为0或靠正面积选号。若当前字段不足，先取得本版本表Field Description或已知符号的原生单元基准；不以当前响应拟合补官方定义。

本轮未启动该单元验证、ETABS或新时程实验；未重提大表。源指纹、API定点读取及页图散列见[source-manifest-R003.json](source-manifest-R003.json)。完成后冻结回报，R001/R002和共享文件不改。
