# 运行与隔离记录

实际开始2026-11-01T15:34:56UTC（23:34:56+08）；8分钟15:42:56UTC，主要12分钟15:46:56UTC，硬15分钟15:49:56UTC。预测/S/区间15:37:06.995117UTC冻结，约130.995s；随后两目标参照和results.json于15:37:08.108944UTC保存。

实际主命令python.exe -X utf8 shw4_baseline_prediction_then_two_targets.py，退出1，错误仅末尾print(json.dumps(...Story5...))包含NumPy int64。所有数值和JSON结果此前已经成功写盘，未覆盖或重跑。随后python.exe -X utf8 verify_saved_outputs_report_and_freeze.py检查保存数组/表、源散列、预测冻结散列，退出状态由工具记录。

只写④R007；无新结构/布局、CM修补、旧8%读取、Excel重新提取或ETABS/YJK调用。基准从缓存读取，解析一/二阶灵敏度按旧R001纯函数复用（AST只导入mul/coefficients，不运行其顶层）。新完整目标状态恰2套(.06/.07)，校验阶段0套。完整数组全部local-cache不入Git。

S单位为降幅百分数/阻尼百分点，不再×100；有符号促进/抵消与候选真实模态分担区分；精确活动峰采用计算等号，1%近峰只是诊断。所有楼层和全部300阶保留，排序翻转/漏判/宽区间均保留。
