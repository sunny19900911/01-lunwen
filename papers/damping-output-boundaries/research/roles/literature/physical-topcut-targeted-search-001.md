# 物理topcut专题检索001：八条限定查询

2026-10-17，10:02起。**取得1篇新的作者公开全文，找到相关但条件不同的零点结果；本轮没有取得与C016 v2全部条件及量词相同的既有结论，novelty unresolved。** 未命中不是首次证据。原条件表、unit附件及其freeze清单均不改。

## 锁定的比较命题

先完整读取[一般三层审核补充](../verification/addendum-V011-general-topcut.md)，SHA256 `9e411f53f706d2cb5489f7e559a4ba064a0ac8176dd0c57676a50f7865b1b70e`。C016 v2是：每一组固定正m/k标准三层链、共同基底输入、真实顶层弹性剪力、完整质量归一模态及每状态各阶共同ζ；定义`S=Σωi、D=Πi<j(ωi+ωj)、ζ*=√[D/(4S³)]`，对每个固定κ>1，固定ζ*与κζ*两态，允许共同有界有限支撑输入族的支撑随T增长，则含全部尾段的峰比无界。**基准ζ*由模型决定，不是任意预定ζ0。** 临界/过阻尼亦由稳定核及有限一阶绝对矩处理。

本轮未用另行审核的精确5%→8%构造扩张上述比较对象；Routh判别、一般L1卷积和包络工具不作为新原理。

## 实际取得的证据与相关候选

| 标识 | 一手来源、版本及可得程度 | 真正已读位置/条件 | 对当前命题的关系 |
|---|---|---|---|
| **L036** | Jesse B. Hoagg、Jaganath Chandrasekar、Dennis S. Bernstein，*On the Zeros, Initial Undershoot, and Relative Degree of Collinear Lumped-Parameter Structures*，JDSMC **129(4):493–502，July2007**，DOI [10.1115/1.2719764](https://doi.org/10.1115/1.2719764)；[作者大学全文](https://public.websites.umich.edu/~dsbaero/library/ZerosUndershootASME2007.pdf)。全文10页，已取并看PDF6/8原页 | 印刷498/PDF6 §5有三质点非共点点力→位移的三次分子`5s³+5s²+75s+100`及复NMP示例。印刷500/PDF8 §9式9.5–9.6限制相邻弹簧/阻尼连接，K/C三对角；Theorem9.1对点力→单坐标位移给无闭右半平面零点 | **related-not-equivalent。** 本稿分布基底输入、截面差输出、一般稠密经典C须分别对照；不能把该串联局部拓扑定理直接当本稿的排除结论。三质点NMP或三次分子本身不是本稿可重新认领的贡献 |
| **L037** | Trevor Williams，*Transmission-zero bounds for large space structures, with applications*，JGCD12:33–38(1989)；[NASA正式记录](https://ntrs.nasa.gov/citations/19890035134)，[公开元数据API](https://ntrs.nasa.gov/api/citations/19890035134)。元数据/摘要实际取回；论文全文未得 | 官方摘要限定共点传感器/执行器，讨论由固有频率和阻尼比限定零点区域；当前记录downloads为空。本轮没有已读定理或公式页 | **insufficient-text。** 只能确认零点界已有研究背景，不能据摘要裁定非共点基底输入＋真实topcut的公式，亦不能据它证明本文新颖 |
| CAND-A，既有旧稿路径 | Rath/Awtar，*On the Zeros of Two and Three-DoF Damped Flexible Systems*；[作者机构J41旧稿](https://psdl-dev.engin.umich.edu/wp-content/uploads/sites/561/2022/02/J41.pdf)、[实验室页面](https://psdl-dev.engin.umich.edu/research/non-minimum-phase-zeros-of-flexible-systems/)。搜索摘要级，两个open均502 | 搜索内容称SISO、classical damping及NMP消除，实验室条目称2021 in review；无新增原页。与L015/L016正式版的版本关系未核 | **insufficient-text。** 不新分确定版本L-ID，不将摘要补成正刚度三模态结果；沿用已缓存L016 p4式6/p14的刚体条件，不将两个版本合并 |
| CAND-B，筛除 | [NCKU机构报告](https://nckur.lib.ncku.edu.tw/bitstream/987654321/80781/1/3010802303009.pdf)，*Investigation on Transmission Zeros in z-Domain of Mass-Dashpot-Spring Systems*。搜索命中，open为工具Internal Error、无HTTP码，未得全文 | 搜索内容指向零阶保持离散系统及输入/输出矩阵约束；没有核原页公式 | 当前连续时间基底/topcut问题不据此取结论；保留检索痕迹，不以报告摘要替代Lin1999原刊，也不另扩参考文献 |

L036本轮使用实际印刷卷期July2007；Crossref分别登记线上2006-10-19与印刷2007-07-01，故L016参考文献列2006可能对应线上日期，不据年份差异判书目错误。初次只核Crossref通用published字段不足以区分两者，补读published-print/online后已分别记录。L036有限读页只核上述结果，未声称穷尽该文全部推论。其他全文指纹、页图及来源取回记录见[本轮manifest](physical-topcut-search-manifest-001.json)，全文只留忽略缓存。

## 八条查询的真实范围

以下共8条search query，根角色4条、辅助角色4条；其后仅打开命中公开入口、取作者全文和NASA元数据，没有追加搜索词。

1. `"base excitation" "transmission zeros" damping`
2. `"base excitation" "shear force" "transmission zeros"`
3. `"On Transmission Zeros of Mass-Dashpot-Spring Systems"`
4. `"Transmission-zero bounds" "Williams"`
5. `"On the Zeros of Flexible Systems" Rath 2023`
6. `"classical damping" "three" "zeros" "base"`
7. `"damping" "unbounded" "peak" "zero"`
8. `"modal damping" "antiresonance" "shear building"`

前4条批次命中L036、L037及CAND-B；后4条命中CAND-A、L016出版社入口和其他不同对象。L016出版社本轮open返回403，未重试，实际比较仍用已有正式PDF。四条辅助查询没有返回可核读的Rath博士论文；这不证明论文不存在。第三方聚合、教程、零阻尼/负刚度材料未作为同条件证据。未重试L034/L026/L035入口，未联系作者、登录账号或付费。

## 可交给作者的结论边界

可引用L036说明非共点结构零点、三质点NMP及拓扑对最小相位的约束有既有研究。C016 v2的待比较对象须完整写明真实基底/截面投影、共同模态阻尼、模型决定ζ*、每固定κ和可增长支撑的完整峰比；不能把一般零点存在、通用Routh/L1工具或“与某文条件不同”替代贡献判断。

本次未取得把阻尼路径上的精确消零与**同条件**输出峰比无界相连的既有原页证据；检索只有上述8词，不能据此排除先例。已有数学支持与文献新颖性分别登记，novelty保持unresolved。按限量任务收束，不继续展开引用链或追加失败请求。
