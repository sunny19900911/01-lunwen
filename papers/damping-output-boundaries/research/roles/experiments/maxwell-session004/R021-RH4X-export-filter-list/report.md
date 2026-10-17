# RH4X 补件筛选清单使用说明

按既有逐流覆盖记录，原88只指定器件中，RH4X 的 P-I/P-J 各33只完整、U1有65只完整；建议补 **55只P、23只U1**。这些数量分别使用每流点数、缺失、额外、重复及无效记录判断，没有把共同32只或联合完整33只套给其他流。窗口严格为原 **0–50 s、2501点、RH4X / NonModHist / Step By Step**；完整仅指已有导出网格，不代表物理尾段或工程算子已认证。

`RH4X-88-device-coverage.csv` 是总清单，含原 Name、Story、Link1、各流完整性、点数/缺点、原表行范围、覆盖CSV行号与小表原行号。缺失55只的P两端均为0条；缺失23只的U1为0条。原两张结果表均触及Excel行上限，但不能逐器件证明缺失机制；0条不等于物理响应为0，禁止补零。`RH4X-supplement-P-filter.csv` 和 `RH4X-supplement-U1-filter.csv` 是分别可筛选的清单，对应TXT每行一个原Name。

**键名必须区分。** 指定小表字段确为 `Name / Story / Link Property`；结果表为 `Story / Unique Name / Link Element`。冻结R001程序优先以落在88个Name集合的Unique Name归组，否则用Link Element；覆盖表保留归一后的Link，88个Link与原Name集合、Story全部相符，原审计记录无未知键/位置。但没有保留每只器件的原始双键对照，本清单将该对照填unknown，不声称三列总是相等。筛选时以清单的原Name和Story识别指定对象，在已有表格预览中核对Unique Name/Link Element后再导出；若一个对象出现多个分析Element，保留真实映射并重新检查分组，不能猜映射或直接丢重复行。

**裸K0路线：** 补齐全88只所需共轭F，并保留至少一只完整P/U1作符号和端口校准。K2、K5的RH4X配对已有完整覆盖，可作为校准候选；“候选”不等于端口已认证。该路线不强制再补全部U1。**Keff残余路线：** 另须对应总δ及匹配参考解，故补23只U1；U1为mm，使用m时除1000。P为kN；I/J是同器件两个位置，不能算两只或把两端相加。当前按两端都齐全保守列P补件，后续单端代表力仍需端口符号证据。

在现有结果表的筛选/所选对象导出功能中，只选对应清单的指定对象、RH4X及原时间窗；若不能直接筛时间，导出此工况后检查是否恰为2501点。保留Story、Unique Name、Link Element、Output Case、Case Type、Step Type、Step Number；P另保留Location及P，U1保留U1与单位。具体菜单名称依当前软件界面核对，此处不编写未验证的点击路径。

`RH4X-batch-plan.csv` 按Story分为7个P批次、3个U1批次；在每器件一个Element且每端2501点的条件下，最大P批次40016行、最大U1批次20008行，远低于单工作表上限。每批先看预览行数与对象映射，再导出到独立文件；若实际行数更多，继续细分对象，不能让导出静默截断。新文件后续按真实键和时间检查缺点、重复、窗端及I/J，不以合并内连接隐藏缺口。不必重导七张全楼表或全部节点结果。

本包仅为来源可审的筛选辅助，不含新时程、参数、求解或工程结论。输入/结果指纹见 `source_manifest.json`、`delivery_manifest.json`，核验结果见 `validation.json`。只读既有小元数据、覆盖CSV和manifest；未访问原Excel、NPZ或数组，未运行ETABS。
