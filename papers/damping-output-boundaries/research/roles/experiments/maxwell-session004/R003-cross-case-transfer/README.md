# R003固定参数迁移（candidate）

主报告：[固定参数跨工况迁移](../R003-固定参数跨工况迁移.md)。只对K2/K5的SHW4X、SHW7X，固定R002/RH4X训练alpha/a/b。没有再拟合、选参、读Y数值时程或做独立事件外验。

轻量材料：`protocol.json`、`check_fixed_transfer.py`、`transfer_metrics_r003.csv`、`transfer_summary_r003.json`、`worst_points_r003.csv`、`run_record_r003.json`及本文。先冻协议；9检查通过、实际退出0、3.523 s。

本地材料：四份`local_input_*.csv`与`local_all_residuals_r003.csv`保存完整11294点及原行定位，用于独审。主控须逐个决定Git白名单；不默认上传这些整段CSV，没有NPZ。所有文件的大小/SHA在汇总JSON中，源Excel本轮实际重hash一次，读取前后size/mtime一致。

完整目标同刻/单位/IJ检查先于残差计算。小值、零力点、最大/偏置残差均保留；没有按结果删工况或去均值。条件关系的一致性不证明属性真值、LinkJointForce/质量源定义、全88只同参或能量闭合。给定原生力时程的变形关系检验，不是由地震输入前向预测整楼响应。
