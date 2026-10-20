# R007来源与离散定义说明

本项只核已有H021正式冻结版本，未运行或导入runner，未重新生成输入数组、未读状态NPZ或新原表。参数与本轮R006使用的M/K逐项相同。

## 正式身份

|文件|SHA256|
|---|---|
|H021-delivery-manifest.json|`971ff81e6af86f179268bc3332e388d8676952d71aab7758cd34de2f45f263e7`|
|three_floor_prospective.py|`4554d99b467b429631fe60d7a70af72107962d1cfd33bd1da088ed5e8a2172b8`|
|pre-run-freeze.json|`506258b0aa9858f9424eae4ba7305e1ebcb18cb743f6fe54a0908705491c8572`|

## 源码精确定位

全部行号按冻结 `three_floor_prospective.py` 的UTF-8文本1起算；完整绝对路径见 [R007-source-evidence.json](R007-source-evidence.json)。

|已核项目|行号|
|---|---:|
|mass_stiffness_difference_matrix|10|
|damping_and_Maxwell_parameters|11|
|port_vectors|12|
|bare_frequency_definition|14|
|envelope|27|
|H2_full_input|33|
|inverse_dashpot|35|
|integrator_allocation_grid|64|
|zero_initial_states|65|
|negative_mass_input|68|
|midpoint_device_solve|71|
|node_state_updates|74|
|constitutive_increment|81|
|save_node_states|92|
|full_time_input_midpoint_grid|186|
|save_state_npz|174|

## 复算不能省略的细节

- 载波始终用全局t：第二段包络中不能把两个正弦换成从t−50重新起相位；只有包络本身使用t−b。
- 0.1是输入式系数及该构造的解析幅值上界，h=.005冻结中点样本峰为0.08480783895471444，不是强制缩放至0.1。中点输入SHA256为`468bcb0b8f39080b0b50e09d8d188741ae28bff5de3f4dcbe3d683160664058a`，本项仅引用已冻记录。
- 外力向量是−M1ag，源码明确三个分量−ag、−1.2ag、−.8ag，不能把三层非等质量模型误写成−1ag。
- 中点内部未知量Fm=(F_(n+1)+F_n)/2，满足 (F_(n+1)−F_n)/κ=h[Bᵀv_m−g(Fm)]；节点更新u_(n+1)=u_n+h v_m、v_(n+1)=2v_m−v_n、F_(n+1)=2Fm−F_n。表中保存的是节点状态，不是中点状态。
- 输入中点网格为t_(n+1/2)=(n+.5)h，n=0..39999；状态网格为t_n=nh，n=0..40000。旧工程轴力的原输出步内16子步做法不用于描述本三层计算。
- 内部状态F0=0在源码直接赋值；程序没有单独保存其他黏壶位移初态，不补写额外未导出的内部变量。整段积分持续进行，包络间隙及第二段开始均不重置状态。
- 非线性标量中点求根最多80次，绝对残差容许值为1e−13 max(1,|b|)（runner36—43行）。这是原算法定义，不在本项重跑或放宽其门槛。

未发现本任务请求的输入式、参数、初态、端口或步长关系缺项。当前说明只为旧无量纲三层模型复算，不借此认证真实结构的阻尼、输入身份或软件实现。

完成与文本检查见 [R007-validation.json](R007-validation.json)，交付字节身份见 [R007-manifest.json](R007-manifest.json)。
