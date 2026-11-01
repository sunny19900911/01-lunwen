# 运行与隔离记录

真实开始2026-11-01T15:43:56UTC（23:43:56+08），8分钟15:51:56UTC，主要12分钟15:55:56UTC，15分钟硬限15:58:56UTC。预测先冻结15:44:35前；新目标仅6/7两个，在预测冻结后生成。

实际运行依次为prepare_frozen_algorithm_reuse.py、rh4_baseline_prediction_then_two_targets.py、prepare_saved_output_verification.py、verify_rh4_saved_outputs.py、report_and_freeze.py，均由Python UTF8模式执行。前四项实际exit0；本报告脚本退出见工具。算法复制来源、散列及限量变更记录在algorithm-reuse-provenance.json。旧R007的失败记录和旧冻结字节未改。

所有source数组只读；未读取旧RH4X8%、未开新模型/布局/CM或额外输入。单位、zeroIC和名义.02s步长直接按冻结缓存与旧构造固定。S及主项完全在有限目标生成前保存。1%容差和top5局部峰沿用；后验排序不用于选择模态或回调阈值。

所记性能时间为perf_counter wall-clock；没有process_time全CPU计量。核心时间不包含全部I/O、散列与验证，主脚本总时间包含大部分归档/验证。不把这些数字称作公平端到端提速证明。

核查脚本复用上一轮只读核查逻辑，改为本轮实际成功退出状态与4对倒置/1次点漏判文件名。动态目标未重算，额外目标状态求解0；当前通过组合为7%二阶，分母1个，非多个独立结构或事件。
