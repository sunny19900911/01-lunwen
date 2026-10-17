# R002条件积分回归产物

本轮主报告为[条件积分回归诊断](../R002-条件积分回归诊断.md)，状态candidate，等待功符号/附质量及实现独审。

- `protocol.json`：21:48:33先冻，91个alpha及K2训练/K5同波检查规则；原生正号，不暗换，不删点。
- `fit_integral_model.py`：两列缩放NNLS活动集、累计梯形积分，不做时间微分，不读Excel。
- `alpha_profile_r002.csv`：完整91点alpha剖面、约束/边界/设计秩与条件数、原单位残差；只由K2选参。
- `fit_summary_r002.json`：最小网格行、1%/5%/10%描述性集合与解释边界。
- `all_point_residuals_r002.csv`：两器件全部5002点，包括小幅与困难点，残差为预测减数据。
- `screenshot_conditional_residuals_r002.csv`：仅在假定kN/m及kN·(s/m)^alpha单位下代入500000/477/.3，不是真属性检查。
- `run_record_r002.json`：实际命令、输入/代码/结果SHA、退出0和7项检查，原R001未改。

网格最小点.30和正系数不证明原生功符号、三参数唯一性或实际属性。K5不是独立地震外验。未经主控/角色2独审，不升格或推广全88只耗能。
