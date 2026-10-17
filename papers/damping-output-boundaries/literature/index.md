# 增阻尼输出边界文献索引

更新：2026-10-17 09:00 +08:00。索引存在不等于全文已核。比较包见[round-001](../research/roles/literature/round-001.md)。公开全文保存在角色目录被Git忽略的local-cache；元数据与指纹见[公开来源清单](../research/roles/literature/public-source-manifest-001.json)。不上传原论文。

## 本轮一手原文与待核材料

| L-ID | 核实书目、稳定来源 | 版本/可得程度 | 原文定位与当前关系 |
|---|---|---|---|
| L001 | Richiedei D., Tamellin I., Trevisani A. *Beyond the Tuned Mass Damper: a Comparative Study of Passive Approaches to Vibration Absorption Through Antiresonance Assignment*. ACME 29:519–544 (2022), online2021. [DOI](https://doi.org/10.1007/s11831-021-09583-w)，[大学全文](https://iris.univr.it/retrieve/46bbe105-6514-4eba-9877-e8d007960b69/s11831-021-09583-w.pdf) | 正式版26页，全文已取；SHA256 715eb3878dc7c945cfd93bfe94f16275216d61bed67641952d6e78dcb9cb7fb5 | 已看印刷521–522/PDF3–4页，§2.2.1–2.2.2式(9)；C002 related-not-equivalent；符号及反共振框架是先例 |
| L002 | **Mario Bonk**, *Complex Analysis*, UCLA Math246A/B. [作者讲义](https://www.math.ucla.edu/~mbonk/complana.pdf) | 无核实年份/版号，187页；SHA256 f403a267bd38a622dba8c28177191b074404bd0596cb45ab81dfe77808d13019 | 已看页108 Theorem13.5式45–46、页111 Example13.9(a)；C002 conditional-extension；旧笔记误署Michael |
| L003 | Eugen J. Skudrzyk, *Understanding the Dynamic Behavior of Complex Vibrators*. [IOA旧源链接](https://www.ioa.org.uk/system/files/publications/EJ%20SKUDRZYK%20UNDERSTANDING%20THE%20DYNAMIC%20BEHAVIOR%20OF%20COMPLEX%20VIBRATORS.pdf) | 本轮原站Not found，未取得新全文；旧记录称1983 Rayleigh Medal Lecture，年份未本轮核实 | insufficient-text；不继承旧记录的全文状态，不给虚构页码 |
| L004 | De Domenico D., Ricciardi G. *Using a tuned fluid inerter for improving the seismic performance of structures isolated with friction pendulum system*. REC2021. [会议全文](https://rec2021.unime.it/papers/REC2021-67.pdf) | 会议全文14页；SHA256 2fdeab5d3b8d5d3d9ca42c7d342183cd1b313047fdac5a71e5484877c8deab47 | 页7 §4，协方差及无TFI归一化，FEI另定义；C003 related-not-equivalent；页图待本轮补核 |
| L011 | Yi J., Xu W. *Effect of damping on the seismic response of long-period structures considering crossover phenomena*. Engineering Structures 293:116627 (2023), DOI [10.1016/j.engstruct.2023.116627](https://doi.org/10.1016/j.engstruct.2023.116627)；[作者机构成果清单第132项](https://www.succ.edu.cn/xxgk/Home/News/view/xwid/f23741017ea607d3fb866d9c4f5b7c77) | 作者机构题名/作者/卷号已核；出版社访问失败；未获全文，insufficient-text | 暂不据摘要判断crossover与本稿双模态公式同一，须补原文公式和输入/输出定义 |

## 继承的候选书目：本轮尚未从原文重新核验

以下仅从W5/01-文献/RY候选文献逐条核验-20261014.md读取，不能写成本轮全文复查完成。原笔记指纹见round-001。

| L-ID | 候选书目与来源 | 继承状态和所需定位 |
|---|---|---|
| L005 | Takewaki I. (1997), *Optimal damper placement for minimum transfer functions*, EE&SD26:1113–1124. DOI `10.1002/(SICI)1096-9845(199711)26:11<1113::AID-EQE696>3.0.CO;2-X` | 旧核验为仅出版社摘要；与1999为不同论文。需全文目标函数/频率/响应量；insufficient-text |
| L006 | Takewaki I. et al. (1999), *Non-monotonic optimal damper placement via steepest direction search*, EE&SD28:655–670. DOI `10.1002/(SICI)1096-9845(199906)28:6<655::AID-EQE833>3.0.CO;2-T` | 旧摘要的non-monotonic指最优布置路径，不能转为增阻尼响应必非单调；待本轮原文，insufficient-text |
| L007 | Politopoulos I. (2008), *A review of adverse effects of damping in seismic isolation*, EE&SD37:447–465. [DOI](https://doi.org/10.1002/eqe.763) | 旧核验仅摘要；隔震/楼层反应谱与本稿固定恢复力不同，insufficient-text |
| L008 | De Domenico D., Ricciardi G., Takewaki I. (2019), *Design strategies of viscous dampers for seismic protection of building structures: A review*, SDEE118:144–165. [DOI](https://doi.org/10.1016/j.soildyn.2018.12.024) | 旧核验为公开预览；SPI式13–18及31–32未核，不因L004全文可读而当同文已核 |
| L009 | Santos-Santiago M.A., Ruiz S.E., Valenzuela-Beltrán F. (2022), *Influence of Higher Modes of Vibration on the Seismic Response of Buildings with Linear and Nonlinear Viscous Dampers*, JEE26(8):3914–3937. [DOI](https://doi.org/10.1080/13632469.2020.1822223) | 旧核验仅摘要，52%的分母未核，不作本稿定量依据；insufficient-text |
| L010 | Renault A., Thomas O., Mahé H. (2019), *Numerical antiresonance continuation of structural systems*, MSSP116:963–984. [DOI](https://doi.org/10.1016/j.ymssp.2018.07.005)，[作者机构](https://sam.ensam.eu/handle/10985/15256) | 本轮未重取原文；非线性极小点延拓与固定线性体系有限ζ变化需分开；insufficient-text |
| L012 | Ma2021，本地全文待盘点 | 由local-sources-001补入实际题名、指纹及原页 |
| L013 | Shao2024，本地原刊待盘点 | 同上 |
| L014 | CEJ2018，本地PDF待盘点 | 同上 |

创新核查状态：未完成专题穷尽检索；已检查来源中的相似基础不等于完整重复，未查到等价式亦不代表首次。
