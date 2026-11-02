# 执行与边界记录

实际开始2026-11-02T11:26:57UTC（19:26:57+08）；主要12分钟11:38:57UTC，硬15分钟11:41:57UTC。工程24行CSV、14行简化筛查和元信息JSON在11:31:55.463538UTC先保存，然后才写报告。窗口仍为本session固定19:17:23—21:47:23，不延长。

实际运行build_engineering_review_table.py退出0；随后verify_report_and_freeze.py只读小CSV/JSON、核数及报告，退出由工具记录。只写本session角色4/R001。原168、d表及审查/旧稿/旧session全部只读，无Git/自动化/新ODE/预测/CM或求解器。

另读取两个443/510KB既有响应缓存manifest的Story Forces字段和单位，不读其中Program Control，不读任何NPZ或Excel。原生Time单位行为空，如实保留。native_paired_validation.json仅读已有比较元信息，不重新认证原始输入或完整模型身份。

最小r与最大PM两组键各自保留同输入配对PB/PM/d/峰时，未混组。严格相等控制值的全部并列键保留，展示首个字典序键；简化读数的数值差计数容差1e−10个百分点，不是工程目标。未设置是否满足规范或承载力的判据。
