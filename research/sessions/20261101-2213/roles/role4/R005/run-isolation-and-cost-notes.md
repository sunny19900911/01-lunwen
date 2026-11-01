# 运行、计时与隔离记录

实际开始2026-11-01T15:15:48UTC（23:15:48+08）；8分钟15:23:48UTC，主要12分钟15:27:48UTC，15分钟硬限15:30:48UTC。小表于15:17:42.477079UTC保存，约114.48s。四个参照仅生成一次，后续目标数组只读。

实际命令依次为python.exe -X utf8加evaluate_public_frozen_predictions.py、measure_frozen_prediction_pipeline_cost.py、verify_report_and_freeze.py，全部在R005执行；退出状态以工具结果为准。完整数组只进local-cache，未运行OpenSees/ETABS/YJK，未开新参数/记录/模型或读取外部账户。

代价定义：complete_candidate_core_seconds是输入已在内存时的候选完整状态求解+一个物理输出+峰值/决策指标。公共源输入解析另加到两边；第二物理输出为验证，归档写盘另记。条件流水线以真实测得组件加总，不声称single-wall端到端实跑。原fair-complete-pipeline-vs-direct-cost-4.csv未含基准输出/寻峰，新的fair-pipeline-cost-including-baseline-output-4.csv显式补齐，旧文件保持不动。

重放的基准、Z/ZD、W/WD和候选预测、包络与R004最大差均为0；不含目标响应重放。first/second导数独立计时，二阶准备包含一阶；每个单独方法每候选都计核设置。输入/导数实现与对照直接求解同为NumPy/既有exact helper。未按计时挑选最好重复值。

小表冻结后只进行有限验证及成本报告。R004全部字节保持；本轮冻结后如有修正应以新文件/新manifest交付。
