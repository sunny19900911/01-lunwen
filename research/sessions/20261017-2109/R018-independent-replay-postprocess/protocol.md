# R038失败后的小结果验收 v001

本阶段只完成原R038被UTF-8 BOM解析阻断的六项统计及四点二十状态值比较。R038原exit1、failure.json、报告、代码及所有冻结字节保持，不追记它为原样成功；本阶段不积分、不重跑、不读/hash/stat任何NPZ或原Excel。

输入仅R038已冻结reference_metrics.json、prediction_four_snapshots.csv、report.md/validation/closure_checks/原代码，以及原作者小summary/7快照和既有根独立协议。先记录全部实际SHA及本脚本/本协议SHA。CSV按utf-8-sig解析，严格唯一匹配N16384和0/16384/16529/98304四节点；对u1/u2/F的maxabs/RMS六统计及四点u1/u2/v1/v2/F二十值使用原冻结绝对差<1e-6门。任一门失败保留失败，不改门。还核独立全节点数98305和两位移原<.1门。

本阶段通过仅补齐小结果验收。结合R038已完成的独立模态Newton全窗计算与同参考逐点统计，可支持有限同模型数值一致性；不声称作者与独审两条完整预测时程已逐点互比、连续真解误差/阶、盲测、FNA或工程验证。全部新文件仅本新目录。结束前回核全部旧输入SHA，写小result/报告与冻结，不改角色文件。

