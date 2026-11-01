# R004 v009引用与来源最终检查

**结论：must 0，should 1，optional 3。** 检查对象仅为作者00:58:30冻结的v009，38210字节，SHA-256 `d622748a45b484d2a059a74d484c4c5c9f107e00f3ea628870fabf403e13c1f7`。本轮实际开始2026-11-02 00:59:56+08，8分钟主限；只核引用句及既有来源包，不搜索、下载、求解、拟合或改稿。终稿只读；supplement-S1亦按作者同轮清单绑定。

## 检查结果

| 范围 | v009定位及核对依据 | 判断 |
|---|---|---|
| [1]书目与直接微分句 | 主文L112、L446；S1 L157；③R001已核出版方全文文本。作者Q. Liu、J. Zhang、L. Gu、L. Yan，Journal of Mechanics 27(3),389–398,2011，DOI 10.1017/jmech.2011.41一致；p392式21–24、p393式26–30定位沿原核查。 | 可用。主文仅称线性动力响应导数的直接微分法，S1明确Liu采用Newmark；没有把本文的精确离散递推、活动峰右导数、误差包络或有限增量可靠性归给Liu，也未称导数理论首创。旧原页图像核验缺口仍保留，不将本轮书目检查说成逐符号原页重审。 |
| [2]框架来源 | 主文L318、L449；S1 L122–124；③R002已冻模型/单位库/参数JSON。 | 可用。三层三跨，保留12水平正质量DOF；四柱脚平动固定、转动自由，同层无刚性楼板；S1说明48总DOF、8约束、28零质量DOF凝聚，以及原nonlinearBeamColumn配Elastic截面/Linear几何。没有把自写重构称OpenSees求解结果或实际建筑。 |
| [3]记录身份与单位 | 主文L101、L318、L451；S1 L124；③R002原始记录header、record-metadata及散列。 | 数值与身份可用。H-E12140对应Imperial Valley 1979-10-15、El Centro Array #12、USGS931、140°；7802点、dt=.005s，首样本t=0约定下末样本39.005s；原PGA=.1433283g。in/kip/s下输入乘386.4成为in/s²，Bω²s为kip、不除1000，与SI工程例分开。建议补记录书目责任来源，见下。 |
| 原例与研究设置 | 主文L318；S1 L124–126；③R002原动力脚本L11–17、L25–41、L47–52。 | 可用。原例1.5倍、10s、1/3阶2%Rayleigh；本研究原幅值、全记录窗、统一模态5%及候选6/7/8/10%已明示为研究设置，不声称复现原默认响应。公开8%为本模型新目标，与工程旧8%已知结果分开。预测冻结顺序不在本角色重跑认证。 |
| 旧020同源桥 | 主文L19–21、L122、L149、L212、L248、L281–288、L438；S1 L174、L276、L284；③R003同源核查。 | 可用。两行U/C/P及参照/软件降幅与旧冻表一致，基准绑定d65da111…同源；有限U/C比值明确为事后解释，S/S_U/S_C为基准导数，不相互冒充。C未改写为纯相位因果份额。低误差未被升级为实际FNA原生q、全FE同M/K或有符号逐阶力的唯一证明；S1保留Ritz恢复条件。 |

## 必要程度与可直接采用的修订

**must：0。** 上述限定范围内没有发现必须停止成稿的来源矛盾。该结论不替代②的数学/数值终审或最终Word排版检查。

**should：1（记录来源更清楚）。** 主文L451目前以“OpenSees Example 5配套加速度记录”开头，只突出了随例下载位置。建议以`PEER STRONG MOTION DATABASE`作为可核的数据库来源标识，说明由Pacific Engineering处理，保留OpenSees官方镜像链接。这样区分原记录来源与示例分发者；不把140°写成严格东西向，不补造记录发布日期或时区。可采用下面[3]。

**optional：3。**

1. 主文[2]、[3]补本轮实际访问日`[2026-11-01]`；[2]可另附ElasticSection直接小文件链接，方便复算。其网站标题与脚本署名/2006年已分别核实；年份取自脚本，不声称网页2006年最后更新。是否按期刊体例保留访问日由作者统一。
2. 主文L248“说明既定输出的前向恢复程度”可改“说明既定输出的前向对照精度”，减少与严格弹性切口恢复的术语混用。现有S1已明确恢复条件，因此不列must。
3. S1 L215仍写“各层S和主模态数值在基准投影汇总后补入”，而v009正文已有数表。可删该句后半段；这是写作占位残留，不是数据或引用失实，不需科研重算。

## 可直接用的三条书目

[1] LIU Q, ZHANG J, GU L, YAN L. An Accurate Method for First and Second Derivatives of Dynamic Responses[J]. Journal of Mechanics, 2011, 27(3): 389–398. DOI: [10.1017/jmech.2011.41](https://doi.org/10.1017/jmech.2011.41).

[2] MAZZONI S, MCKENNA F. OpenSees Example 5: 2D Frame, 3-story 3-bay, Reinforced-Concrete Section & Steel W-Section[EB/OL]. 2006[2026-11-01]. [官方示例](https://opensees.ist.berkeley.edu/wiki/index.php?title=OpenSees_Example_5._2D_Frame%2C_3-story_3-bay%2C_Reinforced-Concrete_Section_%26_Steel_W-Section). 复算所用[ElasticSection输入](https://opensees.ist.berkeley.edu/wiki/images/8/85/Ex5.Frame2D.build.ElasticSection.tcl).

[3] PEER STRONG MOTION DATABASE. H-E12140: Imperial Valley, 1979-10-15, El Centro Array #12, 140°[DS/OL]. [2026-11-01]. [OpenSees Example 5随例记录下载](https://opensees.ist.berkeley.edu/wiki/images/9/98/H-E12140.zip). 记录头标明Processing by Pacific Engineering，USGS station 931。

以上只使用已有已核稳定链接，本轮没有重新测试在线可达性；访问日期指实际下载核查日。原脚本及完整记录仍在忽略的local-cache，不添加开放转载许可或完整原件上传的主张。
