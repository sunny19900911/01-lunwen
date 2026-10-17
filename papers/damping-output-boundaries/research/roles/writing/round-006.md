# 写作第六轮：物理投影边界与分组代理诊断

- W-R006；落稿前实际时钟2026-10-17 09:46:09 +08:00，完成时间见末尾。
- 本轮读取起点HEAD：b4ae85c9034d41233acf4b66a924c74601d41635。仅写manuscript和writing角色目录，不操作Git索引、求解器或原始数据。
- 产物：[working-draft-v006.md](../../../manuscript/working-draft-v006.md)、[figure-map-v006.json](../../../manuscript/figure-map-v006.json)。v005及此前所有冻结版本保留。

## 1 实质增量与审核依据

主控已接纳C012。作者完整读取V008、physical-projection-audit.json，子代理另做只读推导范围核对；新§5.1写完整质量归一基的物理留数矩恒等式，明确f=-a、相对于a整体取负、p=-1可逆条件，以及振型逐阶换号不改变留数。整体ℓ=Kb的非负留数没有被解释成阻尼峰值单调性。

两行表仅排除两个指定见证的标准剪切截面身份：附录B/C008的ω=(1,2,3)、ρ=c(1,-2,1)排除标准三层任一弹性层剪/净弹性层力；§3.2/E004的ω=(1,3)、ρ=c(1,-89/10)排除标准两层相应输出，增加严格零留数模态也无效。c非零可任意缩放/换号。第3.3节C005的(565,-14,951)慢包络模型未被混入此项排除。

完整投影恒等式适用一般正定M/K；局部符号和排除另依赖正对角质量、标准一维固定基剪切K、b=1及完整基。未知非零截断余项、三维耦合、非对角质量、其他截面算子不在排除范围。真实工程仍缺M/K/b/约束、完整有序质量归一模态、Γ、带符号局部弹性投影与阻尼定义；净弹性力、含阻尼惯性平衡、固定点绝对加速度及空间包络继续分开。

主控新接纳E007时本版尚未冻结。作者完整读取其报告、冻结协议、执行脚本、汇总CSV、运行记录及主控独立audit，在§4.4加入3行表，结论3仅补一项指定代理的实际负结果。使用已探索CSV，7个record-ID前缀LOEO，同一编号两方向12层共24组整体留出，其余144组训练。三个预定模型均漏报净差1组、空间加速度3组上升，TP=FP=0、precision未定义；OLS只改善汇总误差，不保证每折改善。

7个record-ID组不是已认证的7个地震学独立事件；测试记录的Bottom响应已作为已知特征。1008条OOF只是168组×2目标×3模型重复评价。正文不说先验工程预测、外部确认或所有模型均不可能预测；空间TN165仍含164下降+1相等。

## 2 输入快照与SHA256

下表为本轮新增或重新读取的直接证据。旧稿证明、E001/E004源值和三幅图指纹沿用round005与figure-map；未重算响应、拟合、模态或图件。

| 输入（相对仓库根目录） | SHA256 |
|---|---|
| papers/damping-output-boundaries/manuscript/working-draft-v005.md | 45d13203d0ce55d326a2d0cdd120e1283b703a03b59b931baa60ab775b8edfc3 |
| papers/damping-output-boundaries/research/roles/writing/frozen-round005.json | bbffbcd715519c926d0f4aa51378edd0dcb9beb1a43a7ea7d46abed4bde597c6 |
| papers/damping-output-boundaries/research/claims.md | 955871cfc50c79b8e84c10324b65125d01a4e53e4a648ae72827010e1612599e |
| papers/damping-output-boundaries/research/roles/verification/round-008.md | 4c87b1770fc6a4d440fcdf789cf48decc373336345d4c1e3eb6b177677415cb9 |
| papers/damping-output-boundaries/research/roles/verification/physical-projection-audit.json | 355fe8a4e33a00e0e5d01431c8d0116627e09c1ea8764196afa73639718a8a37 |
| papers/damping-output-boundaries/research/roles/experiments/round-007-grouped-diagnostic.md | 967d2ec6791eb5278c7a41e0c1ec16c1bbf9a051f0e4d068a77dbaad931decee |
| papers/damping-output-boundaries/experiments/round007_grouped_diagnostic.py | 389a058787ef48c6af27a213a9da1e636a93ac1a08b1f8af7f653dcb36be7a75 |
| papers/damping-output-boundaries/experiments/round007_grouped_diagnostic/frozen_protocol.json | da6f6bf7bc1861b8e10c60c99ea317e8a04ddc8e6b378825df2d7eb2c72ae136 |
| papers/damping-output-boundaries/experiments/round007_grouped_diagnostic/grouped_diagnostic_result.json | 3274a862fe2d98b250eb0b9a624b32604f0a5ddd9b9770ad0991f68807c145dd |
| papers/damping-output-boundaries/experiments/round007_grouped_diagnostic/summary_metrics.csv | a3926499d8f33f5d47130cfac06543a15b659d6994630b880358407469c77753 |
| research/sessions/20261017-0847/grouped-diagnostic-independent-audit.json | 7e4a2efca598925f1ab5ddc81037e80b1727a7384d06d3746a0662c904877278 |
| papers/damping-output-boundaries/research/roles/literature/writing-citation-audit-001.md | 6b6e6484be18bf866ca8b0c348a44a3efd1f5626debb88fac4a5e68ea2e7ba3d |
| papers/damping-output-boundaries/research/roles/verification/round-009.md | 1364c5d6facd0ee38406d61e86947aebbe40df1447fc56fee76f764094f0921d |

## 3 证据强度与数值口径

C012为独立解析审核后的经典模态/静态平衡应用。V008的2/3/4层小模型最大归一化矩差约4.7962e-14，只作恒等式的数值补充；普遍结论来自完整投影和静态必要条件，不来自少量算例。排除不是正m/k逆实现的充分判定，也不否定两个见证的广义输出身份。

E007属于fitted-model/numerical-test reviewed。协议实际09:41:41冻结、09:41:51执行；设计矩阵14个均rank3。主控以独立标准库3×3消元、原两CSV重新连接，复核1008预测、最大差3.0198e-14，未将NumPy内部同方法复算当独立证明。作者未运行拟合，只逐项核入稿表与冻结summary CSV。

文献角色对v005的8项引用审阅未发现必须改写的越界归引，已读取writing-citation-audit-001.md。经典peak gain/L1/TV工具与本稿输出比恒等式、模型族统一界仍分别归属。L034/L035的具体1/α先例及Sultan全文缺口继续保留，不借缺全文确定创新性。

## 4 新桥接只入研究记录

主控已将一般谐波裕度到有限输入完整峰超κ的桥接接纳为C013，将E002b具体数值条件实例接纳为C014。作者实际读取V009；本版不加正文新分支。一般条件是实因果L1核且一阶绝对矩有限，正裕度Δ>0时可设计同一sin²有限包络输入；量词是存在性，非固定天然记录。

具体正m/k合成topcut在Ω50处的充分半时长约1.382059e16 s（约4.38亿年），支撑门槛约8.76亿年；选T=2e16则支撑4e16 s。模型数值外包未定向舍入，没有实际生成/模拟该巨大输入，不称最短、工程可用、物理层剪失界或风险结论。另频点35.2286的不同阈值不与Ω50拼接；经典C正定也不等于逐层dashpot拓扑。

## 5 QA和下一步

本版图序映射仅将draft改为v006，仍为源fig04/fig03/fig01，六个原始图文件指纹保持。v005三幅PNG已实际查看；本轮不重复生成或改图，E007新图未作为本版依赖。

本轮优先完成有限增量、差异复核和冻结。文献全文、工程完整投影字段、最终题目/路线与期刊选择继续记录为缺口或用户待决；不主动扩大理论支线或增加拟合模型。截止仍为2026-10-17 10:47:23 +08:00。

只读差异复核发现一处方法措辞需修正：初稿“平方误差汇总后开方”遗漏了取平均的说明。已按实际公式sqrt(sum(e²)/168)改成“全部168个留出平方误差取平均后开方”，明确不是逐折RMSE的算术平均，并补上剪切楼顶边界S_{n+1}=0及矩式整数p。子代理对C012符号、两个见证身份、E007数值和分组范围未发现其他实质问题。上述修正发生在冻结前，没有改v005。

冻结时钟：2026-10-17 09:54:05 +08:00。最终QA通过：新稿/图序/轮次所有图文链接存在，23个式号无重复，显示数学环境成对；v005摘要至原§4及附录逐段保持，v004/v005冻结清单2份所列文件SHA均保持；6个原图文件SHA一致，E007六组MAE/RMSE与CSV一致。差异只读复核的RMSE平均定义已修正，顶边界与整数p补齐。范围内git diff --check退出0；新文件另查行尾空白、UTF8无BOM/LF。新topcut候选不在本版确定结论内。未重算响应或拟合、改图、读大原始数据、操作Git索引或上传。
