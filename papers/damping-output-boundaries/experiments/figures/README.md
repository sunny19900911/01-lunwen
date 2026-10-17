# 论文图与可引用图注

2026-10-17。4幅Matplotlib科学图，每幅300 dpi PNG与纯矢量SVG各一份。使用冻结E-EXP-001、E-EXP-003、E-EXP-004和V002/V006产物，未重跑响应实验或修改原结果。全部图已实际查看PNG渲染；首遍图2峰值标注靠近标题，已移入绘图区并重新检查。

| 图 | 文件基名 | 可引用内容 |
|---|---|---|
| 1 | `fig01_native_output_changes` | 两原生导出状态的截面剪力峰、同刻净差峰和空间加速度峰的不同变化 |
| 2 | `fig02_window_and_complete_peaks` | T4关断后完整峰位置，以及不同T的截断/完整峰值比 |
| 3 | `fig03_complete_peak_witness` | 同一有限输入及双状态合成输出，完整峰比1.81183 |
| 4 | `fig04_peak_bound_comparison` | 旧/新非尖锐完整峰粗界、κ线和合成见证点 |

## 建议图注

**图1　不同输出定义的原生配对变化。** 每种输出含168组＝7条记录×2方向×12层，分别排序展示，组序不代表同一个控制对象，不能将168当作独立事件数。变化率统一为100(P3/P0−1)。Bottom截面剪力峰168组下降；相邻Bottom同刻差峰167组下降、1组上升；空间加速度峰164组下降、1组相等、3组上升。净差定义Nj=Vj−Vj+1，最顶区段上端声明为0，不能直接改称纯楼层惯性力。Story Accelerations为变化控制点的空间输出，不能改称固定节点或质心加速度。仅为指定导出窗口内的采样峰值。

**图2　冻结观测窗与完整尾段峰值的区别。** 合成双模态固定输出，ω=(1,3)、r=(1,−2)、ζ0=0.05、ζ1=0.08。T=4 s时，冻结[0,T]内峰值比为113.079，完整峰值比为0.933615；两状态完整峰分别发生在5.262 s和5.253 s。左图仅展示前12 s，右图取冻结完整结果，全部自由尾段已由原实验计算至T+600 s并附解析余项界。图中展示抽样线与完整峰位置，不据可视窗口重新寻峰。

**图3　双模态合成输出的有限输入见证。** ω=(1,3)、r=(1,−8.9)、ζ0=0.05、ζ1=0.08；同一输入支撑[0,600] s，统一max|f|=1，零初始。完整峰值比约1.81183，高于κ=1.6，低于新非尖锐粗界6.7375。输入线来自冻结NPZ的绘图抽样；输出线使用既有0.25 s显示样本，峰值标志/标签来自冻结细网格结果，不以图上线条的插值重新识别峰。完整尾段原实验核至输入后900 s并有解析界。图为合成固定实线性输出，不是工程楼剪。

**图4　双模态完整峰值粗界的精化。** 旧B=(4κ−3)(5−4/κ)²，新B=(2κ−1)(3−2/κ)²；κ=8/5时分别21.25和539/80=6.7375。二者均未证明为最优双模态常数。适用原审核范围：固定实留数/输入分布、统一经典阻尼、同一紧支撑实输入、零初始、峰值包含全部自由衰减尾段。κ线只表示谐波及完整L2界，不作为完整峰界。橙点为E-EXP-004有限输入见证，不是工程数据或总体界的锐性证明。新界来源见 `research/roles/verification/round-006.md`、`reply-C006-refinement.md`。

## 数据清单与复现

`figure_manifest.json`逐项记录实际读取文件的SHA-256/大小、8个图文件散列、绘图代码散列、Matplotlib/numpy/Python版本和字体。`plot-data/`保存图1排序变化、图2逐T比值、图3绘图输入抽样、图4公式曲线；这些是图形派生数据，原实验数值保持冻结。

在仓库根目录运行：

```powershell
& 'C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'papers/damping-output-boundaries/experiments/figures/build_paper_figures.py'
```

本机复用已有 `C:/Users/mj528/.codex/tmp/mechanism20261013-pydeps` 的Matplotlib 3.11.2，未安装新依赖。脚本先使用环境已有numpy2.3.5，再追加该Matplotlib路径；Agg后端、Arial字体，SVG文字转路径。其他环境需现有numpy/Matplotlib及相应字体，不需要原始工程Excel。若本地5 MB输入不在，已有 `plot-data/fig03_input_plot.csv` 可用于原图重绘，但不能代替全输入见证的独立响应复算。

## 5 MB witness本地身份及重建

本轮只读、未复制或Git提交如下原见证：

- 文件：`papers/damping-output-boundaries/experiments/round004/finite_input_witness.npz`。
- 大小：4,990,769 bytes。
- SHA-256：`e1bacdc2938750250eb829c54357eba17e4d3bee8694cc33a18f65c7647d859e`。
- 内容：t/input两数组；614401点，dt=0.0009765625 s，支撑[0,600]，首尾0、max绝对值1。

重建无需该数组作为输入：复制已冻结 `experiments/round004_complete_peak_witness.py` 到新隔离目录（例如 `experiments/figures/local-rebuild/`），用numpy2.3.5运行复制的脚本，产物将写入该新目录下的 `round004/`，不会覆盖冻结round004。先核对脚本与原 `round004/run_record.json` 的散列，再核对重建NPZ散列；若环境差异导致字节散列不同，另查t/input数组和逐网格结果，不直接冒称相同文件。本轮未执行该重建，也未决定5 MB文件的上传范围，留主控选择。
