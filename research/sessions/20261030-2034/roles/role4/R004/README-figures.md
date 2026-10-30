# R004 两张供稿小图

图1：`figure1-native-peak-reduction-profile.svg`及同名PNG。原生Bottom截面X向剪力，12层×SHW3X、SHW4X、RH4X全部36对；峰值降幅为各自全时程绝对峰的`100×(1−P8/P5)`，不要求峰时刻一致。源为冻结R003的`native-all12-peak-change-36.csv`。复算点表为`figure1-native-profile-36.csv`。

图2：`figure2-Story12-SHW4X-two-anchors.svg`及同名PNG。Story12/SHW4X，28.34s、20.58s两个锚点，每个锚点分别显示5%、8%的同刻有符号参照低组1—12、所表示高组13—36和原生减参照残差，黑点为原生总剪力。仅采用冻结N36、elastic、rcond=1e-10映射；8%沿用5%系数。精确四点见`figure2-same-time-points-4.csv`。四个原生值已与R003原生峰及交叉值核对。图中分组不是唯一物理分力或能量占比，不跨锚点拼成百分比。

不新增拟合、加阶或依赖；未操作Git。仅从本地冻结数组提取4点，没有输出或上传完整时程。SVG由标准库生成，PNG由现有sharp渲染。所有SVG/PNG均小于500KB，已实际查看；`numeric-verification.json`、`render-record.json`、`visual-QA.json`和`delivery-manifest.json`记录来源SHA、数值闭合、渲染尺寸、视觉检查及封存校验。
