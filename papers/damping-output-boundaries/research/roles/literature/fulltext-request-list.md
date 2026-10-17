# 待补全文：按优先顺序共3项

2026-10-17。按下列DOI寻找完整论文或合法作者接受稿即可；团队取得后负责核公式、版本及来源指纹。三项当前均为 **insufficient-text**，已知入口不代表已取得正文。本清单只整理既有记录，本轮没有新搜索或请求。

## 1. L034 — 二阶核具体公式，优先补

**K.H. You、E.B. Lee.** *BIBO stability integral (L∞-gain) for second-order systems with numerator dynamics.* **Automatica 36(11):1693–1699 (2000).**

- DOI：[10.1016/S0005-1098(00)00075-3](https://doi.org/10.1016/S0005-1098(00)00075-3)；[ScienceDirect正式记录](https://www.sciencedirect.com/science/article/pii/S0005109800000753)。已知[IFAC官方目录](https://www.ifac-control.org/publications/1998-2000/2000_5/at_download/file)只能核书目。
- **为何影响贡献判断：** 题名直接涉及带分子动力学的二阶BIBO积分。若其公式覆盖本稿核，可将相应计算明确作为已有结果使用；这仍不自动等于覆盖整个双模态阻尼模型族的κ-only输出比界。
- **拿到后必核：** 一般分子是否允许纯s分子，怎样精确映射到`R=s/(s²+2αs+β)`；欠/临/过阻尼及`α>0、β>0`范围；是否给`∫|k|dt`闭式或对全部参数统一的`1/α`界，是否讨论`β→0+`、`β=0`和系数锐性。记录实际公式号，区分单核输入→输出增益与本稿输出→输出比较的量词。
- **已试至何处：** Crossref和IFAC书目成功；ScienceDirect正文、[官方Article API](https://api.elsevier.com/content/article/PII:S0005109800000753?httpAccept=text/xml)各返回HTTP429，未重试规避限流。DOI跳转工具不可访问、无可核HTTP码。正文未读，1693–1699只是书目页段。

## 2. L026 — 连续结构peak-to-peak问题的等价性

**Cornel Sultan.** *Decoupling approximation design using the peak to peak gain.* **Mechanical Systems and Signal Processing 36(2):582–603 (2013).**

- DOI：[10.1016/j.ymssp.2012.10.007](https://doi.org/10.1016/j.ymssp.2012.10.007)；[出版社登记入口](https://linkinghub.elsevier.com/retrieve/pii/S0888327012003809)，正确PII为`S0888327012003809`；[Virginia Tech作者出版物页](https://www.aoe.vt.edu/people/faculty/sultan/personal-page/publications.html)的全部期刊列表第22项核书目，未提供机构PDF。
- **为何影响贡献判断：** 这是连续结构和peak-to-peak增益的直接候选。需确定它处理的误差算子、模型参数及统一性是否与本稿相同，才能判断本稿应怎样限定相对于已有工作的贡献。
- **拿到后必核：** 输出是原系统与解耦近似之差，还是涉及`H1/H0`的输出比；诱导L∞的输入/输出范数、时间域、初始条件及直通项；常数是否依赖完整矩阵、极点和输出权重，或对频率、留数、基准阻尼变化的整个指定模型族只依赖`κ=ζ1/ζ0`；有无固定M/K/输入/输出、共同经典阻尼和完整尾段等同一前提。未核前不预设其与本稿等价或不等价。
- **已试至何处：** Crossref与作者页已核书目。VT仓储精确题名/DOI查询均0条，作者47条与题名decoupling18条元数据未找到目标；泛词只看首100条，未穷尽。作者页外链未作为已读2013正文。一次[公开XML请求](https://api.elsevier.com/content/article/PII:S0888327012003809?httpAccept=text/xml)为`fetch failed`、没有HTTP状态；正确出版社入口也仅为工具不可访问。2017官方讲座摘要和作者CV不能替代论文全文。

## 3. L035 — 二阶BIBO积分的早期讨论

**E.B. Lee、J.C. Luo.** *On “Evaluating the bounded-input-bounded-output stability integral for second-order systems”.* **IEEE Transactions on Automatic Control 45(2):311–312 (2000).**

- DOI：[10.1109/9.839956](https://doi.org/10.1109/9.839956)；[IEEE正式记录](https://ieeexplore.ieee.org/document/839956)。
- **为何影响贡献判断：** 可核二阶BIBO积分的已有公式与适用范围，帮助确定本稿标量步骤的正确引用和定位；不能凭评论题名认定其已给本稿速度核公式。
- **拿到后必核：** 原文传递函数和输出是位移、速度还是一般线性组合，能否映射到纯s分子；所给结论是否覆盖欠/临/过阻尼及哪些参数范围；BIBO积分、最坏有界输入或统一界是否对应本稿`∫|k|dt`、`1/α`及相关极限，而不只是另一输出核。区分一个系统的积分公式与跨阻尼状态/模型族的统一输出比结论。
- **已试至何处：** Crossref书目成功、无摘要；IEEE正文及DOI跳转工具不可访问，未返回具体HTTP码，不能记作403。原刊正文未读，311–312只是书目页段。

详细取回记录见[二阶核先例包](kernel-norm-prior-art-001.md)、[Sultan跟进](sultan2013-followup-001.md)及[登记元数据](sultan2013-crossref-metadata-001.json)。全文缺口保留为贡献判断待核项，现有证明、数值与工程核验仍按各自证据评价。本角色交付后保持检查点；仅在新证明、新稿或新原文产生具体比较需求时继续，不重复既有失败检索。
