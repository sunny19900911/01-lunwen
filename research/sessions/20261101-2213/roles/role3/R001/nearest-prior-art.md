# R001 原文对照与一个公开基准线索

角色③；实际首查2026-11-01 22:21:58+08；本轮比较对象为固定M/K、基准ζ0=0.05的一二阶阻尼灵敏度、有限增量楼层剪力整窗峰值预测。只核查下列两篇原文，不据此宣称全面检索或首次。

## 两篇原文与当前候选的关系

| 一手资料与定位 | 原文支持及条件 | 本研究的关系判断 |
|---|---|---|
| Q. Liu, J. Zhang, L. Gu, L. Yan. *An Accurate Method for First and Second Derivatives of Dynamic Responses*. Journal of Mechanics 27(3),389–398,2011. [DOI](https://doi.org/10.1017/jmech.2011.41)。p389/PDF1式(1)；p391/PDF3式(12)；p392/PDF4式(21)–(24)；p393/PDF5式(26)–(30)。 | 线性动力方程经直接微分，结合Newmark递推一、二阶响应导数；例中设计变量涉及结构几何，Rayleigh系数取常量。已读出版方全文解析文本；公式尚未完成原页图像核验。 | `related-not-equivalent`。一般DDM和复用动力算子属于已有基础；令M/K不变、C随ζ变化得到z/w是其专门化，不能列为新理论。已查段落不能支持有限δ峰值误差保证、近等高峰切换及工程筛选可靠性；也不能据此断言文献从未研究这些问题。 |
| Liyu Xie, Li Zhang, Chao Pan, Ruifu Zhang, Tianli Chen. *Uniform damping ratio-based design method for seismic retrofitting of elastoplastic RC structures using viscoelastic dampers*. SDEE 128(2020)105866. [DOI](https://doi.org/10.1016/j.soildyn.2019.105866)，[作者单位原文](https://vibcon.tongji.edu.cn/Upload/file/20200630/202006300122332503669.pdf)。p3–4§2.3；p4式(10)–(20)；p5式(24)–(25)；p6式(27)。 | 弹塑性RC结构的等效单自由度、能力谱与黏弹性阻尼器改造；附加储能刚度改变等效周期和阻尼。 | `related-not-equivalent`。适合引言交代阻尼取值的工程设计背景；不属于固定M/K、统一改变结构模态ζ的同条件先例。UDR不应被改写成所有结构振型相同阻尼比。 |

可供作者采用的表述：线性动力响应对参数的一、二阶导数可通过直接微分求得；本文在该基础上，用基准响应构造候选阻尼下的楼层剪力时程近似，并研究整窗峰值预测及其误差对筛选结论的影响。此句后半部分是本研究任务，尚须实际验证。

以下是本轮提出的审核条件，**不是上述论文的定理**：固定旧峰时刻的导数需要唯一活动峰等条件；近等高峰可能切换，应比较全时程。若已经独立建立同一时间集合上的响应误差界ε，则峰值误差不超过ε；连续时间结论还需控制采样间遗漏。误差界是否足够窄、低改善或不利响应是否漏判，须由角色②④检查，不能用三角不等式代替工程有效性验证。

## 唯一公开结构基准线索

采用[OpenSees官方弹性悬臂柱教程](https://opensees.berkeley.edu/wiki/index.php/Time_History_Analysis_of_a_2D_Elastic_Cantilever_Column)，提供者Vesna Terzic（UC Berkeley）。页面“Create the model”明确：单位kip、in、s；高432 in；柱底固定；顶端水平质量5.18 kip·s²/in，竖向和转动质量为0；A=3600 in²、E=3225 kip/in²、I=1080000 in⁴；Linear几何变换，elasticBeamColumn。脚本[Ex1a.Canti2D.EQ.modif.tcl](https://opensees.berkeley.edu/wiki/images/e/e8/Ex1a.Canti2D.EQ.modif.tcl)定位已确定，web工具不支持其MIME，本轮未运行或完整核验脚本。

这是公开数值教学模型，不能称实测建筑。可从明确边界条件凝聚其水平质量/刚度，独立检查单模态阻尼增量误差；不能承担多模态抵消或多楼层峰值切换验证。页面给定参数与自行凝聚的M/K须分别标注。本轮只选择这一结构基准，不另选地震记录，也未下载配套记录。

[官方Copyright and License](https://opensees.github.io/OpenSeesDocumentation/developer/license.html)含研究/非商业使用、保留版权及免责条款、商业分发限制等规定；不标成公有领域或无条件BSD。若复制代码需保留适用声明；本轮只保存链接和自写参数摘要，不转存脚本。

## 原文可得性与交接

- Liu：出版方全文解析文本可读；只保留[稳定出版页](https://academic.oup.com/jom/article/27/3/389/5943808)，不存临时签名URL，无本地PDF散列。截图缓存失败，负号/下标的最终原页核验列为缺口，不以本记录替代独立推导。
- Xie：本地cache PDF共12页、3648826字节，SHA-256 `f9763258414c4fe6aace2f0469b8485c91f41e37fba634d44fafd81b8a032ad5`；页码与PDF页序相同。全文只在忽略的local-cache，不上传；未确认开放转载许可。
- Song/CSI旧读段落可支持模态方程与输出口径；没有据旧读段落找到阻尼有限增量峰值误差证书。H2/有理插值索引条目不直接替代本问题的时程峰值证书，本轮不新增第三篇。
- 下一项最有价值核查：角色②确认残差至峰值区间的假设与采样误差；角色④冻结预测后比较新ζ真值。贡献结论待其结果，本记录不修改共享账本或正文。
