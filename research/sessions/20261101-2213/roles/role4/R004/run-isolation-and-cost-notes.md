# 运行隔离记录

实际运行public_baseline_sensitivity_predictions.py退出0；随后verify_baseline_and_freeze.py实际运行，退出由执行工具记录。只写④R004，无新线程/代理、无Git/求解器/模型API，无候选真值。

实际开始2026-11-01T15:08:59UTC（23:08:59+08），8分钟截止15:16:59UTC，12分钟截止15:20:59UTC。首张24行预测表于15:11:10.936988UTC保存。候选预测及包络冻结见prediction-and-envelope-freeze.json；后续验证没有改写这些文件。

名义步长直接取冻结的.005s，未使用median(diff(t))；计算时间轴np.arange(N)*dt，仅以容差检查终点39.005s。R003旧字节不动。输入原样本首点并非强制改成0。

状态缓存、完整时程和完整记录仅local-cache；Git可选小文本、CSV与自写脚本。新预测独立于公开模型候选真值；后续不能按真值回调两阶预测、界或政策。
