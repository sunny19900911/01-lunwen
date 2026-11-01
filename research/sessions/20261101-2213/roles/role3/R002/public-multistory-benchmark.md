# R002 可组装的公开三层线性框架与同例地震记录

**已找到可交给角色④的完整小型输入。** 采用一套OpenSees官方Example 5的三层三跨平面框架、ElasticSection分支，以及该例列出的H-E12140加速度记录。原模型、单位库、加载脚本、读记录程序和40,000字节记录压缩包均已实际读取；本轮没有调用OpenSees、ETABS或其他求解器，没有组装M/K或计算响应。

实际开始2026-11-01 22:39:56+08，本任务上限12min、截止22:51:56。角色③只准备输入，不替代④生产数值、②独立审查或⑤正文整合。

## 1. 官方出处与小文件

[官方示例页](https://opensees.ist.berkeley.edu/wiki/index.php?title=OpenSees_Example_5._2D_Frame%2C_3-story_3-bay%2C_Reinforced-Concrete_Section_%26_Steel_W-Section)，实际HTML标示revision 6146。该页分别列Elastic Element与Uniform Earthquake Ground Motion所需文件。源码署名Silvia Mazzoni & Frank McKenna, 2006。

| 小文件与官方直接下载 | 字节数 | 实际用途 |
|---|---:|---|
| [Ex5.Frame2D.build.ElasticSection.tcl](https://opensees.ist.berkeley.edu/wiki/images/8/85/Ex5.Frame2D.build.ElasticSection.tcl) | 10,946 | 节点、截面、质量、约束、单元、重力 |
| [LibUnits.tcl](https://opensees.ist.berkeley.edu/wiki/images/b/b5/LibUnits.tcl) | 1,290 | in、kip、s及g换算 |
| [Ex5.Frame2D.analyze.Dynamic.EQ.Uniform.tcl](https://opensees.ist.berkeley.edu/wiki/images/7/79/Ex5.Frame2D.analyze.Dynamic.EQ.Uniform.tcl) | 4,393 | 配套输入与原默认缩放/阻尼/分析窗 |
| [ReadSMDFile.tcl](https://opensees.ist.berkeley.edu/wiki/images/0/02/ReadSMDFile.tcl) | 2,668 | AT2文件头、步长与数据段规则 |
| [H-E12140.zip](https://opensees.ist.berkeley.edu/wiki/images/9/98/H-E12140.zip) | 40,000 | 同例唯一选择的地震记录；只含H-E12140.AT2 |

各原文件SHA-256见`source-manifest.json`。五项均成功，未扩展第二套基准。主域名部分链接现重定向，web工具不能读取Tcl；官方ist子域以标准HTTPS实际下载成功。GitHub API一次遇公开限流403后未重试、不访问账户。所有原件只在忽略的`local-cache/`；可提交的是自写说明、参数JSON、元信息和提取脚本。

## 2. 可直接用于线性代数组装的参数

完整节点和单元连接表见`assembly-inputs.json`，无须执行Tcl。单位为in、kip、s，质量单位kip·s²/in，位移自由度次序ux、uy、rz。

| 项目 | 参数与原脚本定位 |
|---|---|
| 层跨 | 三层、三跨；每层14 ft=168 in，每跨24 ft=288 in；模型L17–46、L51–52 |
| 节点 | 16个；编号11–14、21–24、31–34、41–44；x=0,288,576,864，y=0,168,336,504；L30–46 |
| 支承 | **11–14节点ux、uy固定，rz自由**，原命令`fix ... 1 1 0`；L55–59 |
| 材料 | E=29,000 kip/in²；L63 |
| 柱 | A=33.5 in²，Iz=4090 in⁴；L67–69；12根柱：每列相邻层连接；L92–103 |
| 梁 | A=27.7 in²，Iz=2700 in⁴；L70–72；9根梁：非地面各层相邻列连接；L105–113 |
| 物性/几何 | `section Elastic`（L76–77）；柱梁均Linear几何变换（L84–86）。实际单元命令为`nonlinearBeamColumn`、5积分点，**并非elasticBeamColumn**；名称含nonlinear不表示此分支材料非线性。自写平面框架组装应保留弹性截面、线性几何，不添加P-Delta。 |
| 楼板约束 | 脚本无equalDOF/rigidDiaphragm约束；不得擅自把同层4个水平节点合并成1个层位移。 |
| 质量归属 | 只在21–44节点x方向集中；uy及rz质量为0，单元命令无分布质量；L129–142。 |

单位库L23给g=32.2 ft/s²=386.4 in/s²。模型L119–127：楼板重度150 lbf/ft³、厚6 in、横向分担宽度288 in；梁自重94 lbf/ft、柱114 lbf/ft。由原公式作单位换算，单根柱重1.596 kip，单根梁及楼板重45.456 kip。质量应按节点分配保留：

| 物理层 / 源节点层号 | 外侧节点 / 每节点质量 | 内侧节点 / 每节点质量 | 全层质量 |
|---|---|---|---:|
| 第1层 / 2 | 21、24：`(Wcol+Wbeam/2)/g` | 22、23：`(Wcol+Wbeam)/g` | 0.3694409937888198 |
| 第2层 / 3 | 31、34：同上 | 32、33：同上 | 0.3694409937888198 |
| 第3层 / 4 | 41、44：`(Wcol/2+Wbeam/2)/g` | 42、43：`(Wcol/2+Wbeam)/g` | 0.3611801242236024 |

建议④用标准2D弹性框架刚度组装：48总自由度，删8个支承平动约束后40自由度；12个水平自由度有正质量，其余28个自由度质量为0。检查Kzz可逆后凝聚为`Kc=Kxx−Kxz Kzz⁻¹ Kzx`及12阶水平对角质量Mxx；该尺寸是输入计数，本轮未核验Kzz可逆性、正定性或固有频率。也可直接处理对应描述系统。不能给零质量自由度添加任意小质量而不记录模型改变。

楼层剪力输出应由原框架水平弹性恢复力的楼层截面求和建立并固定B，不把3层等效剪切模型替代原拓扑；阻尼力、总支座反力和弹性构件剪力需区分。具体输出映射及自由度凝聚交②④核验，本记录不冒充完成软件等价验证。

## 3. 同一示例附带的唯一地震输入

ZIP实际解出H-E12140.AT2，120,405字节，SHA-256 `e1e260f8434d147553c9a088a04985dc9ee3bb0d4b2ad19e99529b401d00edd4`。文件头确认：Imperial Valley，1979-10-15，时间字段2316（未标时区）；El Centro Array #12，USGS station 931，140°分量；PEER strong-motion database，Pacific Engineering处理。加速度单位g，HP=0.1 Hz、LP=40.0 Hz；NPTS=7802，DT=0.005 s。记录本身具有独立事件/台站身份，但单条记录不构成多事件外部泛化验证。

实际解析检查7802数值全部有限，与头部一致；原样本PGA=0.1433283 g。若以首样本t=0，末样本t=39.005 s；时间原点需在实验协议中明确。完整header和min/max/PGA见`record-metadata.json`，未改写原数据或重新滤波。

**冻结实验选择前注意原例的默认值不同。** 动力脚本L11–17、L25–41、L47–52使用x方向、GMfact=1.5、g换算386.4、分析步长0.01 s、仅分析10 s；Rayleigh在1、3阶目标0.02，其他阶不必相同。主线若使用统一模态ζ0=.05、其他目标ζ、原始幅值或全记录窗口，必须明确是本研究预先指定的设置，不能声称复现原例默认响应。先冻结预测与输入选择，再生成目标真值。

## 4. 权限、适用性与完成状态

[OpenSees官方许可页](https://opensees.github.io/OpenSeesDocumentation/developer/license.html)含科研/非商业使用及声明保留等条件，不称公有领域或无条件BSD。地震记录虽能从官方示例公开下载，本轮未确认单独再分发许可；原脚本、完整记录及压缩包均不进入Git。此模型是公开数值教学模型，不能称独立真实建筑或物理试验；以它组装的线性系统可用于独立多模态方法检验，最终模态参与、峰值切换是否有区分力仍需实算。

运行`prepare_public_benchmark.py`已实际成功，核对5项源散列、16节点、21单元、4支承、12正质量节点和记录点数/有限性，生成`assembly-inputs.json`与`record-metadata.json`。脚本只解析和单位算术，不执行Tcl、不组装矩阵、不计算响应。后续最高价值动作是④在冻结设置下组装与审查，再做基准预测/候选真值；③本轮定位任务已完成。
