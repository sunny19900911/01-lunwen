# 运行与隔离记录

实际命令：python.exe -X utf8 research/sessions/20261101-2213/roles/role4/R003/discrete_absolute_defect_envelopes.py，退出0。随后运行verify_report_and_freeze.py，退出状态由执行工具记录。只写R003，不覆盖旧文件。无求解器、模型API、新输入或目标状态求解。

开始观测2026-11-01T14:56:29+00:00；方法冻结见method-and-inputs-freeze.json；包络冻结2026-11-01T14:58:49.991013+00:00；Story5/12表于2026-11-01T14:58:50.044601+00:00保存，距开始约141s。8分钟截止15:04:29UTC；硬截止15:11:29UTC。

内核计时不含源读取/散列、直接卷积检查和数组保存。all_envelope_stage_seconds包括包络阶段的检查、保存等开销；total_script_seconds另含输入、真值读取和评价。不把仅无states调用视为低工作量。R001导数成本仍不可忽略。

冻结前只读基准、灵敏度、原预测、coth界及政策；冻结后仅读R002已保存真值数组，没有重算其状态。method_frozen_utc与envelope冻结时间可查。已知案例条件如实保留。

核以解析E(kdt)构造，避免直接对连续|Gc|以dt取样而漏掉dt内振荡。它与采样时刻的精确离散递推一致；没有延伸为连续时程极值界。浮点保护参数在读本轮目标数组前冻结，未按覆盖或宽度回调。
