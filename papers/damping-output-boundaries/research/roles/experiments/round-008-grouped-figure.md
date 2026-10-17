# 第008轮：E007冻结OOF图示

2026-10-17约09:45～09:49 +08:00；只读冻结结果作图，无新拟合/调阈值。目录 `experiments/figures-grouped-diagnostic/` 已交付两面板PNG/SVG、Matplotlib脚本、manifest、336点原值派生CSV、中文图注和QA。

横轴实际变化、纵轴OLS OOF预测，零线/y=x同尺度；标4个实际上升组，全部位于漏判象限。每面板注OLS和训练均值基线的MAE/RMSE（pp），不使用多数类accuracy。已实际查看两遍，修正共用图例靠近横轴标题的问题，最终标注清晰。

按主控最新提醒，图注/QA明示“7个record-ID组，地震学独立性未认证、同组Bottom特征已知”；冻结join_audit旧字符串不修改。该图不能升级模型科学范围，也不改已有四组图。

最终绘图退出0，约0.452 s，复用现有依赖。PNG300dpi、SVG纯矢量，保留SVG生成字节；尾空格计数和散列在新qa_record，不改Git设置。停止在检查点，未Git。
