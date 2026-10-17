# R002 Story Drifts与Story Accelerations：定义及缺行边界

会话20261017-2109；角色3；2026-10-17 21:44:19 +08开始，单项≤10分钟；当前报告candidate，交主控裁决。R001已先冻结，本任务不回改R001，也不改变完整能量/层剪分析。

**结论：Story Drifts有楼层范围空间最大值的直接技术说明；缺行是否代表零、阈值过滤或其他选择仍为unknown。Story Accelerations的空间归约及绝对/相对身份均未得到该表的直接官方定义，继续unknown。** 不补零、不把移动Label包络当固定节点有符号时程。

## 1. 冻结输入及本次读取边界

实际全文复读辅助文件“楼层响应定义与覆盖补充核查.md”，路径为W5-重燃双塔连体/research/maxwell-20261017/roles/verification/response-coverage/；SHA256与主控指定一致：

`2ed6b1666c0dd97a85ff1b94fe38adb27c925082820b54c6995aa69962fcd8b0`。

该文件实查144组Story Drifts全稀疏、共缺161802参照时刻，Label随时刻变化、导出值均正；Story Accelerations完整但仅Story字段，无Diaphragm/节点字段。本任务只读这份冻结核查，不重读原Excel或缓存大数组，不把正值/稀疏性当成省零规则的证明。

## 2. 能直接核到的源定义

| 来源/实际访问等级 | 本次定位及支持 | 不足与当前数据的映射限制 |
|---|---|---|
| [CSI ETABS2016 API：StoryDrifts](https://docs.csiamerica.com/help-files/etabs-api-2016/html/e55e16e2-b7b0-2864-f3dc-b781f4062325.htm)，已读HTML正文 | 方法签名及Parameters列Story、LoadCase、StepType、StepNum、Direction、Drift、Label、X/Y/Z；Label定义为point labels。Return Value中的0表示API调用成功。 | 没有给零行省略、漂移阈值、完整时间网格保证或逐步符号规则。调用成功的0不是物理漂移0。API页面对X/Y/Z文字写displacements，不能据该页单独认证当前表的坐标字段；以实际表字段/元数据定位为准。 |
| [筑信达技术知识库259：各种位移结果的相互关系](https://www.cisec.cn/Support/knowledgeBase/KnowledgeBaseMenu.aspx?menuid=259)，已读正文；页面更新2018-04-25 | “楼层位移角（Story Drifts）”节：楼层标高范围内全部节点的最大位移角；楼层范围可大于隔板范围。同文Joint Drifts说明相邻层同标签节点位移差/层高，斜构件情形另说明。 | 是该技术页面/版本背景的直接解释，不是当前ETABS版本数据库字典。未明列逐时正负/绝对值选择、数值门槛或缺行策略；不能由“最大”及本表全正推导精确符号规则。 |
| [CSI ETABS2016 API：cAnalysisResults](https://docs.csiamerica.com/help-files/etabs-api-2016/html/3abebdb5-a279-ddcb-f2de-a058c9468c42.htm)，已读正文 | Methods列表明确JointAcc报告指定point elements的**相对加速度**，并另列JointAccAbs。 | 没有把任一方法映射到**Story Accelerations**表；更没有给该表质心/隔板/全楼层节点最大值的选择规则。不能由JointAcc或JointAccAbs名称决定当前楼层表身份。 |

筑信达原页还对部分表的工况输出范围给出其当时版本说明；本任务不将旧版静力/规范指标说明反套为当前非线性时程的逐行过滤规则。当前软件版本、中文扩展及导出选项均未核，必须保留版本限制。

## 3. 空间包络可说明什么

官方/产品技术定义支持把Story Drifts看成楼层范围统计，而非任选隔板质心或一根柱的固定位置响应。结合辅助文件的移动Label，当前宜用“某层、某方向、某已导出时刻的最大漂移记录”及其控制Label/坐标；整体统计暂称**导出记录最大值**。多个隔板或加强层中，控制位置可能不在拟比较的那个隔板或竖向构件上。

这说明空间选择问题，但**没有解决时间覆盖**。不论空间最大值怎样定义，若没有缺行规则，就不能证明已导出点的峰值等于该工况完整时间网格峰值；也不能在稀疏点间补零/插值后算RMS、谱、相位、正负循环、微分或耗能。记录最大值作为已导出集合统计仍有效，必须保留这个限定。

## 4. 缺行原因与加速度身份：保留unknown

- 本轮针对官方资料的zero/threshold查询没有得到可用的Story Drifts数值省略门槛。API成功返回码不提供这种门槛。
- CSI旧版本发布说明检索命中个别标签、绘图或多塔输出问题；相关PDF本轮打开失败或仅有检索片段，且当前软件版本未核。未把这些片段当成161802缺时刻的原因，更未断言当前软件有相同缺陷。
- 筑信达633“转换模型位移表格异常”检索线索涉及节点标签匹配，但正文打开一次超时。本轮不据其片段诊断当前模型标签错误。缺项可来自何种设置/筛选/软件机制仍须直接证据，不枚举猜测后挑一个当结论。
- **Story Accelerations：空间归约=unknown；absolute/relative=unknown。** 仅Story且含Base不证明全局绝对量；时间网格完整只确认覆盖，不确认位置/物理定义。不能把它和任取D1质心位移绑定作同点动力学或直接F=ma。

这些限制不否定当前已有的能量/层剪结果；它们只是阻止使用未经确认的漂移补全和加速度物理映射。

## 5. 下一项最小可判别检验

请模型持有人/实验角色提供**该ETABS版本的数据库表Field Description或API数据库字段字典**及当前输出选择设置；优先核Story Accelerations的表级定义。对一条已知缺失的交叉方向时刻，另给对应楼层全部候选Joint Drifts，或相邻层匹配标签节点的有符号位移与层高；可重构空间最大值，与数据库/API的同一时刻结果核对。全节点重构为非零而Story Drifts缺行，将直接否定“缺行统一补零”；若重构为零，也只支持该时刻，不能立刻认证所有缺行。

本任务没有启动软件、重提大表或执行该检验，只交付具体判别路径。源查询/访问失败及角色内辅助核查见[source-manifest-R002.json](source-manifest-R002.json)；原R001和其他角色旧文件均保持。
