# R009：Y方向输入与原生缓存资料准入（仅元信息）

**三组Y方向在元信息层面可以复用各自既有X向标量ag，不需要猜测或另乘倍率。证据是同一LoadCase表内引用同一个函数对象、完全相同SF/时间缩放/到达时间/初始状态，输入仅由Accel U1改为U2、Angle均0；不是由工况名相近推断。此次没有Y向积分、响应数组读取或预测。**

## 精确源行与输入对应

两个状态分别来自旧D `native0_small_tables.json`和`small_tables.json`的Load Cases - TH - Nonlin Modal，表头/单位行2/3。单位Trans Accel SF=mm/sec²、Time Factor=sec、Arrival Time=sec、Angle=deg。表中所有相关设置（除Name和Load Name方向字段）逐格比较一致；5%/8%同名Y工况除GUID/Notes外设置也逐格一致。

|Y工况|X/Y源行（两状态相同）|共同函数|SF / mm·s⁻²|输入方向|有效n / 终时刻|
|---|---|---|---:|---|---|
|SHW3Y|8/9|SHW3_NGA_1175KOCAELI.USK,Tg(0.9)-X|0.35|U2，Angle=0|2691 / 53.80s|
|SHW4Y|10/11|SHW4_NGA_1828HECTOR.0688c,Tg(0.9)-X|0.35|U2，Angle=0|2951 / 59.00s|
|RH4Y|6/7|ArtWave-RH4TG090,Tg(0.90)-X|3.5|U2，Angle=0|2501 / 50.00s|

全部工况Initial Condition=Unstressed、Mass Source=Previous (MsSrc1)、Modal Case=Modal、Motion Type=Transient、Step Size=.02s；对应X/Y的Number Steps及其余非方向设置相同。SHW3与SHW4的SF为0.35，RH4为3.5，**不得因既有缓存PGA同为0.35m/s²而把三个SF改成相同**。其函数数值本身归一不同，已有X输入配置已完成源函数×SF/1000的m/s²核验。

可复用字段为既有X输入配置中的SHW3X_t/ag、SHW4X_t/ag、RH4X_t/ag；cached ag已经以m/s²缩放，不再乘SF或g，也不将非零ag[0]强置零。这里“复用X ag”只指相同标量加速度函数，现在施加于U2；不能把X方向的Γ、B或剪力响应直接改名为Y。后续若派工，方向投影应使用同实际模态的ΣmYφY和相应切口投影。

函数源行沿用已核X配置：SHW3、SHW4、RH4的具体范围均写入3行准入表。SHW4函数结束58.98s、原生输出至59.00s的既有端点续值规则同样继承，不新增外推方法、不补零。LoadCase对象同函数且同参数，以及原5/8配对验证的same_input_all_samples=True，支持这一元信息准入；没有在本轮重新读取函数序列或输入数组。

## 缓存覆盖与5%/8%配对

两个manifest均存在SHW3Y、SHW4Y、RH4Y：每工况18个CM位置、12个Story Bottom切口，UX/UY为mm、VY为kN。X/Y的全部位置键及n、t0、t1、唯一时刻数、严格递增性和dt_min/max摘要逐组一致。180组精确key/group_id/路径已冻结；尚未读取时间向量，后续读取时仍须像X检验一样逐项核对时间，不以摘要相同代替运行时检查。

既有native_paired_validation.json已经对每个Y工况核5%/8%输入全部采样相同及18CM/12Forces覆盖，质量表全单元相同，LoadCase参数除GUID/Notes一致；周期/参与小表保留既有浮点差。5%/8%的ζ数值沿用已批准研究口径与X配置，本次LoadCase摘要不另含模态阻尼数值字段，不能把本轮读表称为独立再认证ζ。actual300受控Ritz基与旧D两状态的完整M/K身份混杂保持不变。

## 准入边界与停止位置

本轮结论为**标量输入及原生缓存的元信息准入通过**，是否执行Y输出检验由根另行派工；没有先执行六套Y积分。若使用同一actualω、ζ、零初始和标量ag，已有单位参与s核从方程上可代数复用，仍须单独使用Y投影并检验原生Y输出，不把这句话当作本轮已运行。

三组X/Y是同三个地震函数在不同方向的输入，不增加为六条独立地震事件。这里Y目标是旧D的5%/8%原生响应，不将实际装置缓存里的SHW7Y改名成SHW3Y，不恢复布局或扩展求解器。无原始Excel、NPZ数组值或大响应读取，无ODE、拟合、Git或新数据。
