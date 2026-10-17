# E007分组诊断图

文件：`fig07_ols_oof_local_changes.png`（300 dpi）与同名纯矢量SVG。脚本 `build_grouped_figure.py` 只读已冻结 `round007_grouped_diagnostic/oof_predictions.csv`、`summary_metrics.csv`、`frozen_protocol.json`；未拟合、重算系数、调整阈值或修改原四组图。

## 可直接引用图注

**图　七个记录ID组留出的局部输出代理误差。** 两面板分别为相邻Bottom截面同刻净差峰与楼层空间加速度峰，横轴为原生配对的实际峰变化率，纵轴为固定OLS模型的OOF预测变化率；模型仅含截距、同组Bottom截面峰变化率及归一化层序。每个record-ID组的两方向、12层共同留出，训练其余六组。虚线为y=x，横竖实线为固定零阈值。红三角标出全部4个实际上升点：净差SHW6-X-F1；空间加速度SHW3-Y-F1、SHW6-X-F1、SHW7-X-F1，均被预测为下降。图中比较训练目标均值基线与OLS的MAE/RMSE，单位百分点（pp）；平均误差下降并未检出这些稀有上升。每面板168组为7记录×2方向×12层，并非168个独立事件；7个record-ID组的地震学独立性未由该CSV认证，留出组的Bottom特征本身已知。结果为本批数据的描述/迁移诊断，不作机制或先验工程预测保证。净差不是已核实的纯惯性力，空间包络也不是固定节点加速度。

## 原值和科学范围

四个标记完全取冻结OOF原值：

| 输出/组 | 实际变化/% | OLS预测/% |
|---|---:|---:|
| 净差 SHW6-X-F1 | +5.571164 | −10.662210 |
| 空间加速度 SHW3-Y-F1 | +1.283725 | −8.920303 |
| 空间加速度 SHW6-X-F1 | +5.497465 | −9.213537 |
| 空间加速度 SHW7-X-F1 | +2.012480 | −13.898553 |

TP/FP/FN为净差0/0/1、加速度0/0/3。图中不报告多数类accuracy，不改变零阈值，也不把OOF误差改称外部新事件验证。图上OLS与训练均值MAE/RMSE直接摘录summary CSV；`plot_values.csv`仅保存336个已存在的OLS点，未增加独立样本。

**元数据措辞限制：** 冻结 `join_audit.json` 的denominator字符串曾写“7 independent event groups”，它只是旧分组元数据文字，不能证明地震学独立性。按主控要求不修改该冻结文件；本图、图注和QA统一采用“7个record-ID组，独立性未认证”。主控已用独立标准库LOEO复核OOF指标，这也不改变独立性范围。

## 渲染、字节与重绘

已实际查看PNG，首遍共用图例靠近横轴标题，移至上部后再次查看；标签、四个箭头、零线、y=x和误差框均清晰，无切字。两轴同范围/同比例；浅红区仅标真实上升但预测下降的象限。

`manifest.json`含三份输入和输出SHA-256、代码/依赖版本；`qa_record.json`记录PNG尺寸、DPI、SVG结构、源散列和原四组图保持不变的检查。SVG保留Matplotlib原生生成字节，不清理尾空格、不改Git全局配置；实际尾空格行数见qa_record。

重绘命令（仓库根目录）：

```powershell
& 'C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'papers/damping-output-boundaries/experiments/figures-grouped-diagnostic/build_grouped_figure.py'
```

复用本机既有Matplotlib3.11.2、numpy2.3.5，Agg/Arial；未新增依赖。未修改冻结OOF、原始数据或既有图，未执行Git。
