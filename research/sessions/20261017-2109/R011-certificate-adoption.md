# M-C025：非线性同能量布局反例的条件准入

主控已合并准入数学、辅助包络修复、参数/时间及完整实现独审。在下列明确数值运算合同内，冻结alpha=3/10合成例满足

\[
\sup_{t\ge0}|u_{1,A}(t)|<1.325,
\qquad |u_{1,B}(T)|>8.809.
\]

因此B的完整峰也大于8.809。A的全部停载后尾段另有上界1.098；两个比较界的严格间隙大于7.485。这里采用保守十进制数，方向已对原binary64界用精确Fraction重新核验；原二进制值、hex编码及来源指纹见[准入JSON](R011-nonlinear-certificate-adoption.json)。

## 对象与同条件

模型是两个各自接地、由正弹簧相连的质量：M=I，K=I+0.001[[1,−1],[−1,1]]，C=0.1√K。裸主体两模态阻尼恰为5%。同一个正参数非线性Maxwell器件，只将到固定参考端的端口由B_A=(1,0)移到B_B=(0,1)。共同输入为(1,1)sin(t)，0≤t≤T=20π，此后为零，全部初态为零。kappa/c的精确代数定义绑定[冻结协议](layout-nonlinear03-protocol-v001.json)。

评价对象始终为固定物理坐标u1。交换解使器件F、总变形/总速度、所列整体储能、两种耗散及输入功历史完全相同，相同定义且分母非零的能量等效指标亦同。这个等同是[R023](../../../papers/damping-output-boundaries/research/roles/verification/maxwell-session004/非线性交换与条件尾能量独审-R023.md)的解析恒等，不从数值余额推断。

## 三道证据门

| 门 | 已审内容与范围 |
| --- | --- |
| 误差数学 | [R024](../../../papers/damping-output-boundaries/research/roles/verification/maxwell-session004/全残差误差储能与中点预算独审-R024.md)：完整状态误差储能、运动学/动量/本构三残差、连续PL早期、固定T下界及真正停载被动尾合并；不把余额当状态误差。 |
| 数值辅助与参数 | [R017](../../../papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R017-helper-v002-fix-review/report.md)修复v001非整数根次数API漏洞，[R018](../../../papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R018-interval-parameter-audit/report.md)核精确参数、相位、特殊函数与调用域；旧失败不抹。 |
| 完整实现 | [R025](../../../papers/damping-output-boundaries/research/roles/verification/maxwell-session004/R025/report.md)：98,304段预算、前缀/总和、末能量及比较方向；隔离复跑逐位一致，另有未导入helper的独立Fraction残差/末能/方向挑战。 |

本次近似轨迹由一条隐式中点计算的最终存储端点在真网格上作连续分段直线定义。对所有参数、pi/sin、非线性幂及导数、端点重构、残差积分、总和、末能和上下界进行有向包络。I(T)和I(6T)的上端分别约0.756118486764、1.015881720802。有限段覆盖采样间隙，尾段依真实停载系统的能量耗散；6T不是人为宣布尾峰结束。

原[候选实现](../../../papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R015-outward-residual-certificate/v002-run/report.md)的pending标签保留为当时冻结状态，后续准入由本主控记录绑定，不回写历史报告。v001公共API的失败样例及v002修复均保留。

## 必须随结论保留的合同与限制

有向数值结论依赖IEEE binary64有限基本运算、nearest舍入、渐进下溢、正确nextafter和精确Fraction语义，以及已记录的Python/NumPy float64解码/运行模式合同。有限探针和独立复算不构成对所有硬件、所有未来运行或历史全程模式的形式化证明。本裁决是明确前提下的解析与验证数值证书，不是无条件机器形式认证。

源端点NPZ留本地，未上传。仓库保存生成和包络代码、指纹、小结果与独审；完整运行复核需要本地缓存，或按记录环境重建并核对身份，不能假定外部读者已持有完整数组。

这不是实际ETABS建筑、真实477/500000参数或普通两层剪切链的结论。跨指数沿用数字c不代表同物理器件。保护u1的同时，较大反应被交换到u2，两位置的全局最大仍相同，因此不推出整体优胜、最优布置或实际楼层安全保证。

交换、模态投影和增量耗散/残差工具均归经典方法，来源与具体装配分开。同条件发表覆盖尚未闭合，不称首创；此证书没有填补真实模型端口、背景阻尼、归一、输入及成对布局数据缺口。
