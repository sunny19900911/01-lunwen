# C023单位模型常数代入（candidate，待主控独核）

只读取E-EXP-T002-001冻结高精度谱/rho，按先冻protocol评价C023公式，不求谱、不算响应、不增加r或拟合。主要结果及4行充分交叉时长见[角色报告](../../research/roles/experiments/theory-session002/round-003-envelope-constants.md)。

- `protocol.json`：运行前冻结的定义、4个原delta、来源散列和证据边界。
- `evaluate_constants.py`：仅Python标准库Decimal/Fraction，90位求值、110位同源算术核对；拒绝覆盖已冻结果。
- `envelope_constants.json`：A/B/gamma/M/E/T0/Tenv/C、完整原omega/rho、4行时间条件与检查。
- `four_crossover_durations.csv`：Tenv/delta、T0、max项、完整输入2T及显示量级用天/365天年。
- `run_record.json`：实际命令、退出0、运行0.00613 s、源/代码/结果SHA及10项检查。

T是包络半时长。按此保守证书，T0约50.57天，原四delta对应交叉半时长约60天—165年；这只是该证书充分条件的近似代入，不是必要/实际最短时长、实际峰、通用工程秒数或定向舍入认证。主控独核前保持candidate，不自行发布为已审结论。
