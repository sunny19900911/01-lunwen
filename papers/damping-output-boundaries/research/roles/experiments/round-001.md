# 实验第001轮：原生局部需求的独立数值口径核验

日期：2026-10-17，Asia/Shanghai。证据ID：E-EXP-001，类型 `observed-data` + `numerical-test`；角色自检，待主控/验证者审核。仓库起点 `57fae1c7097e0f61063592997ccd94a9a64b1923`。

## 结论及当前状态

已独立重算两份原生导出缓存的14方向工况×12层，历史主结果重现：168个楼层Bottom截面剪力绝对峰均下降；168个相邻Bottom截面同刻差中仅SHW6-X最下区段增大，1129.168234→1192.076049 kN，即5.571164%；3个第1层空间加速度绝对峰增加，最大为SHW6-X的5.497465%。两状态区段净力峰均在20.60 s，峰增量62.907815 kN全部来自原控制时刻变化，重新寻峰恢复量为0。

原工作簿10个控制单元格已精确匹配，所有9项汇总断言通过；最终运行退出码0，耗时66.07 s。首遍因脚本单位字面量 `mm/sec2` 与源表 `mm/sec²` 不同而断言失败，数值逐个相同；已保留 `audit_result_initial_unit_assertion_failure.json`，修正为源表精确单位并复跑。最终状态见 `../../../experiments/round001/audit_result.json`。

## 冻结输入与范围

原始资料只读，本轮未操作ETABS求解器、未拟合、未提交Git、未上传大文件。

| 来源 | SHA-256 | 身份 |
|---|---|---|
| `E:/!!!!!!!!TO HOME/小震阻尼0.xlsx`，218138409 bytes | `c14e71ab0e1d244d3e13d72108ebf85cd6d603eef9a41992f979f35e23e3216d` | 无附加状态；0不等于结构总阻尼0 |
| `E:/!!!!!!!!TO HOME/20261016附加阻尼3.xlsx`，619327468 bytes | `c21073336ae48383a7e18375ebdcb63d5e9c3a0ca4bb83bb3d2d44af8b923d24` | 附加3个百分点状态 |
| `W5-重燃双塔连体/02-数据/增阻尼多目标研究-20261016/` | 每个使用的NPZ单独散列写入运行JSON | 两源的缓存、历史小结果和脚本只读 |

检查前后文件大小、mtime和SHA-256稳定；没有取Program Control账户/授权字段。运行JSON保留本脚本散列、Python/numpy版本和运行秒数。

本轮读取全量缓存时间轴，而非inner join。14方向工况来自7条记录，方向不算独立事件。两状态基底实际输入逐样本相等；各工况时间网格无重复、单调、间隔0.02 s，全部24个截面/楼层响应组与同工况基底轴严格相同。窗口分别为R1/RH4 50 s、SHW3 53.8 s、SHW4 59 s、SHW5 48 s、SHW6 70.5 s、SHW7 53.9 s。完整性仅指现有导出窗口，不声称尾段已充分衰减或已确定连续时间极值。

原表小元数据复读：质量/质心表完全一致；Load Cases - TH - Nonlin Modal前23列求解/输入字段一致（GUID/注释不计）；300阶圆频率最大相对差约5e-8。原始源散列与缓存提取时散列相同。逐阶阻尼定义仍为独立缺口。

## 原始单元格与净力定义

只先做有符号同刻差，再求绝对峰：`N_j(t)=V_j,Bottom(t)-V_(j+1),Bottom(t)`；顶端声明为0。逐时刻望远镜和回到Story1剪力，残差小于1e-9 kN。该代数恒等式不单独建立楼层自由体惯性力等式。

| 原生状态 | Story Forces!H451020：Story1 VX/kN | Story Forces!H412484：Story2 VX/kN | 同刻N1/kN |
|---|---:|---:|---:|
| 无附加 | -2856.078275462 | -1726.910041011 | -1129.168234451 |
| 附加3个百分点 | -3552.812649456 | -2360.736600421 | -1192.076049036 |

以上均为SHW6X、Bottom、20.60 s，力单位kN。加速度控制源值为两文件的Story Accelerations!G437334（SHW3Y）、F450998（SHW6X）、F457867（SHW7X），单位 `mm/sec²`；仍是空间控制量，不能视为固定节点信号。

## 支持、反对与失败路径

- 支持C004的范围：这两份稳定导出、7记录×2方向、指定窗口中，累计截面峰改善与局部净结构力/空间加速度峰增大可并存。
- 反对过强表述：本批168个截面剪力峰全部下降，不支持“本工程增阻尼导致某层截面剪力峰增大”；相对基底分配增大也不是绝对剪力峰增大。
- 尚不支持：相邻截面差是纯楼层惯性力、空间加速度是质心/固定节点加速度、3处增幅都由同一模态抵消机理唯一造成、任何普遍阻尼单调性或概率结论。
- 失败路径：默认PATH Python缺numpy，使用已带numpy/lxml的Codex依赖Python完成，无安装新依赖；首遍单位字面量断言失败已保留，不能删除或将失败称为数据不配对。

## 可复现产物

- 脚本：`papers/damping-output-boundaries/experiments/round001_native_audit.py`，新实现缓存读组、时间轴和峰值预算，流式原表读取复用skill的 `stream_csi.Workbook`。
- `experiments/round001/adjacent_cut_net.csv`：168组同刻净力峰、控制时刻及精确峰值预算。
- `experiments/round001/story_cut_and_spatial_acceleration.csv`：168组截面/空间加速度峰。
- `experiments/round001/time_grid_audit.csv`：14个时间窗和一致性。
- `experiments/round001/SHW6X_control_window.csv`：20.60±0.10 s的小型源值窗口，单位kN/s。
- `experiments/round001/audit_result.json`：源指纹、10原表控制单元格、环境、状态和摘要。
- `experiments/round001/run_record.json`：实际命令、退出码、脚本与读取器散列、依赖版本及成功/失败运行记录。

运行命令（cwd为01-lunwen）：

```powershell
& 'C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'papers/damping-output-boundaries/experiments/round001_native_audit.py'
```

理论小模型的并行只读盘点见 `source-inventory-theory-20261017.md`；下一项最高价值检验见 `next-task.md`；参数定义和输出映射质询见 `questions.md`。以上新增证据未直接升级为普遍证明。
