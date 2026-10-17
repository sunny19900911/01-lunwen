# R019：实际有控模型的条件字段与最少补导出包

结论：当前小元数据已具备88只指定、Link1的U1属性摘要、300阶模态结果及七表六工况输出清单，**仍不具备直接套用完整器件力→目标位移差接口的工程认证条件**。主要缺口是Link1参数数据行、当前参考K/实际C与分析定义、端口几何和有符号投影、全部器件完整力及共同输入/初态/基线身份。缺导出不表示模型未定义；已审R022/R030只认证条件接口，未认证这些实际字段。

本轮开始2026-10-18 02:54:07 +08:00；冻结2026-10-18T03:00:16.380058+08:00，用时369.38秒，低于10分钟。[25项字段映射及R022全部38字段对应](field-gap-map-R019.json)、[输入SHA](input-rules-R019.json)、[validation](validation-R019.json)随本报告交付。

当前源身份沿用冻结清单：`E:\!!!!!!!!TO HOME\有控.xlsx`，635,525,054字节，SHA256 `9d999dfac02ad758b83b52f908ac5df6925b869b9d0a96c032c24e729bf82c23`。本轮没有访问原工作簿或重新计算其SHA，只读既有小表/headers/manifest/报告。未读任何NPZ或节点数组，未提取、求解、下载或联网。

## 当前事实与四类状态

“已拿到”仅指所列数据/字段确实存在，不能据此自动升级数学语义、全时程覆盖或工程收敛；“仅用户说明”保留主控转述的证据层次；“缺导出”表示此次资料中没有相应实际值；“定义未认证”表示虽有列名/结果或理论定义，仍缺当前模型对应认证。25项状态为7已拿到、1仅用户说明、11缺导出、6定义未认证，不是接口完成百分比。

当前新有控本身确有300条Case=Modal、Mode1—300；不能误称当前没有模态结果，也不能因此判定Eigen/Ritz或完整性。`Modal Participation Factors`的ModalMass/ModalStiff列存在，单位行分别kN-m-s²/kN-m；这些列名或数值不自动成为与当前振型缩放匹配的广义质量。旧0/3模型的300阶、Unstressed、质量源、5%/8%等定义不移植到当前新有控。

| ID | 条件字段 | 当前状态 | 已见证据/最小缺口 |
|---|---|---|---|
| F01 | 当前源文件身份 | 已拿到 | 既有清单记录有控.xlsx 635525054B及SHA9d999d…bf82c23；补：若后续导出来自变更模型，另给新模型/导出身份 |
| F02 | 88只device→property指定 | 已拿到 | 88条均Link1；Story1–11各8；补：当前模型若有更改，更新指定表 |
| F03 | 属性类型及摘要DOF | 已拿到 | Link1、Damper - Exponential、Degrees of Freedom=U1；补：运行工况实际引用/逐DOF开关另核 |
| F04 | 逐DOF实际非线性/Fixed/选项 | 缺导出 | Exp明细表仅3行标题/字段/单位；补：补Link1按Direction的全部数据行、Fixed和相关选项 |
| F05 | 参考有效ke/ce数值 | 缺导出 | Trans Linear KE/CE列和单位存在，值未导出；补：同一Link1版本各DOF的KE/CE实际值/选项 |
| F06 | Link1截图有效参数0 | 仅用户说明 | 旧R004/R017记录为主控转述，本角色未查看原截图；补：如用作证据需绑定当前模型/属性/DOF/工况；用原生数据行落实 |
| F07 | 实际串联κ、黏壶c、α及单位 | 缺导出 | Trans NL Stiffness/Damping/Exponent列存在但无数据；补：补Link1逐DOF实际值、单位与串联选项 |
| F08 | 属性质量/实际M及质量源 | 定义未认证 | Summary质量25kg已取得，但当前质量源/M未取得；补：当前质量源、是否含Link自质量、约束后质量身份 |
| F09 | Local Axes角度 | 已拿到 | 88条Angle=0deg；补：默认轴/高级轴及端点几何另核 |
| F10 | 全88端口I/J、XYZ、轴、偏置/约束→B | 缺导出 | JointForce结果有Joint列；指定表无I/J，局部轴表只有Angle；补：只补全部指定端口的I/J、轴或可复现几何、偏置/转角/刚臂/隔板约束 |
| F11 | P/U1结果列及单位 | 已拿到 | P(kN)、Location=I-End/J-End；U1(mm)等表头存在，原大表截断；补：保留组键/同刻/源行；缺组分批补导出 |
| F12 | 当前软件列→功共轭完整F/总δ的符号映射 | 定义未认证 | R003给CSI Rev15 P=轴向内部力、U1端差定义，当前版本/端口绑定未闭合；补：先用一只完整Link核I/J/轴、变形重构、作用对象/符号/单位；必要Field Description或已知符号基准 |
| F13 | 全部指定器件完整F_D时间史 | 缺导出 | 已审六工况共同完整子集32/88；原力/变形表触行上限；补：按已有组完整性清单仅补缺失/截断组；先一工况、全88指定端口完整窗 |
| F14 | 当前七表/工况输出时间窗 | 已拿到 | 七表小manifest列六工况、NonModHist、Step By Step、约0.02s输出窗；补：如果改窗/续算，提供新输出清单 |
| F15 | 模态频率/阶次结果 | 已拿到 | 当前有控自身Mode1–300，Case=Modal；CircFreq(rad/sec)等列存在；补：正确参考算子若不同，需对应已有模态结果/身份 |
| F16 | Eigen/Ritz、实际所得基、刚度来源/完整性 | 缺导出 | 当前清单没有Modal定义，参与率结果不代替定义；补：Modal Case实际类型、建基初态/参考K、实际阶数频带、独立起始载荷/循环和完整性/余项 |
| F17 | 显示振型缩放、m或质量归一 | 定义未认证 | Modal Participation Factors有ModalMass/ModalStiff列与单位；无当前端点振型配套认证；补：同一缩放的目标/端点模态形状及mj，或质量归一证据 |
| F18 | 固定目标ell及signedγ | 缺导出 | CM位移/Drift结果有目标类字段，尚未指定并绑定所需线性物理输出；补：先固定一处位移/相对位移目标，给其相关DOF和signedγ或所需少量节点振型 |
| F19 | 全端口signedβ | 缺导出 | 当前频率/参与因子表没有逐端口有符号模态投影；补：全部指定DOF逐mode signedβ或实际端点模态形状+B映射 |
| F20 | 物理裸K0或FNA Kref及力配对 | 定义未认证 | CSI定义已审，当前全部ke/实际Modal来源未拿到；补：选裸K0+完整F或Kref+残余，明确参考U；必要裸U修正 |
| F21 | 实际背景C/逐阶ζ及来源 | 缺导出 | 当前结果表无工况/材料阻尼定义；5%只作既有参考标尺；补：当前工况阻尼、材料合成、逐阶覆盖、参考K及共同对角化证据 |
| F22 | 同外力记录/方向/倍率/时间移位 | 缺导出 | 当前有输出工况名而无输入函数/工况定义；补：同记录/函数身份、方向、比例、时间移位/窗及case引用；既有波文件可用hash+配置绑定 |
| F23 | 主体初态/续算、器件初态、质量源case绑定 | 缺导出 | 当前结果CaseType=NonModHist，不是初态/质量源定义；补：当前时程case配置及引用、主体u/v初态/续算、器件初态和质量源 |
| F24 | 同M/K/C的去支路主体基线身份 | 定义未认证 | 当前只有单有控状态，旧0/3模型尚非公平成对裸主体；补：参考主体定义/差异清单；若要绝对响应/峰，再交已存在且身份合格的yU或参考解依据 |
| F25 | 采样力重构/求积/缺模态和缺器件余项 | 定义未认证 | 现有有限输出网格及缺组已知；补：声明插值/共同窗，未认证力误差和遗漏项单列；需要全时结论再补尾历史/证据 |


## 给用户的最少补资料包

先固定一个位移/相对位移目标和一个已有工况，补下面三组核心资料即可启动有限窗接口可用性核对；不用重新导出七张全楼结果或全楼节点时程。第四组只在要绝对响应/实际峰比较时需要。这里不安排新求解；当前没有的基线/模态结果先记缺口。

1. **小型属性与分析定义包。** 88只→Link1的指定已有，可沿用；优先补`Link Prop Def - Damper - Exp`中Link1按Direction的完整数据行：Fixed、Trans Linear KE/CE、Trans NL Stiffness/Damping/Exponent、串联/固定长度与相关选项及单位。无需把同一属性重复导88份，但必须将该属性版本与当前88只及运行工况绑定。另补实际软件版本、Modal Case的Eigen/Ritz/参考刚度和初态来源/实际阶数频带/Ritz载荷循环、时程工况的模态引用/输入记录方向倍率与时间移位/初态续算、质量源、背景工况+材料+逐阶覆盖。后面这些定义表在当前版本的精确名称尚未认证，可交实际定义导出或设置记录，不能编点击路径。5%标签不认证实际C，ke/ce不等于κ/c；改参考K或拆装导致模态变化时须重新核同C及经典对角化。

2. **只含目标和端口的几何/模态包。** 全部指定端口I/J、XYZ、局部轴或可复现定义、偏置/刚臂/转角/隔板及约束，以及固定目标ℓ所需少量DOF。给对应参考算子的逐模态有符号γ/β及质量归一/同缩放m证据即可；或者给这些端点和目标的振型后重建，不必给全楼其他节点。现有300条频率等结果可复用，但不是完整确切Eigen证书；缺模态或Ritz动力残差继续留项。连接/约束/振型导出的当前精确表名未知。`Link Assigns - Local Axes`已有Angle=0不能代替方向余弦，`Defined Length=1m`也不是I/J几何。

3. **一个工况的全端口完整力窗，按缺组补。** 已确认表名为`Element Forces - Links`，保留Story/Unique Name/Link Element/Output Case/Case Type/Step Type/Step Number/Location/P及单位；先按已有完整性清单仅补缺失或截断组，按工况/装置分批避免Excel上限。共同完整32/88不是每个工况恰好32，本轮不重新计算数组覆盖，不能机械规定每个工况都补56只。可先用RH4X现有0—50s、2501点作为试用窗；是否延长须另给力史和误差证据。先对一只完整器件核P/U1、I/J、轴和功共轭符号。若选裸K0+完整F，位移差公式本身不强制全88的U1；若选含ke的Kref残余力，则需相应全部总变形δ，使用`Element Deformations - Links`的U1及其余激活DOF，并核F−keδ及参考U。串联弹簧不能再次并入裸主体，两个端P不累计两遍。采样、插值和求积误差保留，输入停止不表示器件力同时为零。

4. **仅在需要绝对响应/峰时补基线输出。** 条件位移差接口不另外要求共同外力的模态参与因子，也不强制先交无控时程，但必须认证同外力和主体M/K/C/初态及裸K0或参考Ueff的身份。要得到两条绝对响应及各自峰，另需合格参考yU或独立的参考输入/初态解；先导出已有且身份合格的目标结果。当前单有控记录、旧0/3模型不能自动成为公平成对去支路基线。若没有已有结果，先保留缺口，不据此安排Solver。

## 已确认的实际表名与字段

以下名称来自当前小清单/表头，不是按经验补造：

| 用途 | 当前确有表名 | 本次确认范围 |
|---|---|---|
| 指定/属性 | Link Assigns - Link Properties；Link Assigns - Summary；Link Prop Def - Summary | 88只均Link1；Summary一行Damper - Exponential/U1，Mass25kg。仅摘要/指定，不补出运行激活和实际M。 |
| 参数 | Link Prop Def - Damper - Exp | 有Direction/Fixed/Trans Linear KE/CE/Trans NL Stiffness/Damping/Exponent等列，但数据0行。 |
| 轴/端部结果 | Link Assigns - Local Axes；Element Joint Forces - Links | 前者只有Name/Story/Angle；后者有Joint、F1…M3，且大表截断，不能代替全88 I/J拓扑或确定力作用对象/坐标/惯性恢复。 |
| 端口时程 | Element Forces - Links；Element Deformations - Links | 前者P(kN)、Location；后者U1(mm)、转角(rad)等。当前端口软件定义仍须与R003手册口径实际绑定。 |
| 模态结果 | Modal Periods And Frequencies；Modal Participation Factors；Modal Direction Factors；Modal Participating Mass Ratios；Modal Load Participation Ratios | CircFreq(rad/sec)、Mode、参与结果及ModalMass/ModalStiff列已见；无节点振型/当前模态定义认证。参与率不是有符号γ/β，也不是局部响应误差。 |
| 七表缓存 | Total Energy Components；Element NL Energy By Group；Base Reactions；Story Forces；Diaphragm CM Displacements；Story Accelerations；Story Drifts | 只复用manifest的headers/keys/groups，不读缓存数组；“complete”不能读成88器件力完整、局部覆盖充分或无限尾认证。 |

七表manifest实际列出RH4X/RH4Y各0—50s/2501点，SHW4X/SHW4Y各0—59s/2951点，SHW7X/SHW7Y各0—53.9s/2696点，约0.02s输出步。这里只证明所列输出窗，不认证内部步长、输入函数身份或尾响应结束。五张触行上限表为Element Deformations - Links、Element Forces - Links、Element Joint Forces - Links、Joint Accelerations - Absolute、Joint Velocities - Absolute；缺失/截断不可补0。

当前24表清单没有本任务所需的完整分析定义、输入函数、质量源、背景阻尼、完整端点连接/约束或节点模态形状。准确说法是“本次导出未包含/未认证”，不能说“软件模型没有这些定义”。程序账户/授权字段本轮不读取或复述，软件安装版本仍未认证。缺定义表的确切本版本表名/菜单路径保持未知。

## 审核范围与冻结

R022的38个schema字段已逐一对应到25个状态行，包含reference/mode/target/port/force/remainder六类；所有标成“当前已确认”的表名均在当前inventory中。元数据小表重算确认88指定、同Link1、摘要U1、Exp数据0行、当前300阶；headers和7表manifest只核清单/字段。两个只读协作者分别核接口条件和当前小元数据；后者未找到其直接候选manifest路径，因此七表具体时间窗由本角色主任务在已定位的实际manifest独立读取，未冒称双方都复核该部分。

R017及其history全不改，本轮只引用当前已归档身份的源范围；其看图主体按history修复说明为角色3主任务，不是总主控。R022/R030“0必须修改”不升级为当前工程参数或数据完整性认证。本轮只写自己R019字段映射、报告、输入及validation；未原Excel/数组/NPZ/求解/重提取/新下载/外搜，源/他人/共享/稿件/Git不动。完成冻结交接后停止。
