# L026 Sultan 2013 作者与机构存档路线跟进 001

- 复查者：literature/history_methods；日期：2026-10-17。
- 实际检索与收束：约09:27–09:32 +08:00，少于本轮8分钟检索上限；未继续扩搜理论方向。
- 输入：已读c001-c006-targeted-search-001.md；主控交接C006新版V006界为(2κ−1)(3−2/κ)²，旧界仍正确。本角色没有重审该证明。
- 本轮结果：书目进一步获作者大学网页确认，指定机构公开路线未取得2013全文。L026继续为insufficient-text，不据未命中判断创新。
- 仅写本文件；不改index、旧轮次或主张。未下载ResearchGate正文、未用账号/key、未绕过限制、未发送作者邮件。

## 1. 已核书目与原文状态

Cornel Sultan. **Decoupling Approximation Design Using the Peak to Peak Gain.** Mechanical Systems and Signal Processing, 36(2):582–603, 2013.

- DOI 10.1016/j.ymssp.2012.10.007及正确PII S0888327012003809：由文献角色负责人（本聊天根代理）已核Crossref元数据后交接。本角色没有重复执行Crossref检索。
- 本角色直接核：[作者Virginia Tech Publications页](https://www.aoe.vt.edu/people/faculty/sultan/personal-page/publications.html)，“My favorite (10) publications”第5项，以及“All journal/book publications”第22项。HTML无页码，用栏目和条目号定位。
- 上轮已核：[作者2021履历](https://www.aoe.vt.edu/content/aoe_vt_edu/en/people/faculty/sultan/personal-page/resume/_jcr_content/content/download/file.res/Short%20Resume_CornelSultan_2021.pdf)，PDF第4页Journals第28项。该履历支持卷期页码，不是论文全文。
- 2013论文全文：本路线未取得，因此没有新增PDF页数、全文SHA256、论文内式号或定理号。印刷582–603来自书目，不能当已经读过这些原页。

## 2. 作者主页实际指向什么

实际打开了[作者个人主页](https://www.aoe.vt.edu/people/faculty/sultan/personal-page.html)、[学院作者资料页](https://www.aoe.vt.edu/people/faculty/sultan.html)及上述Publications页，并只读Publications原HTML中的附件链接。

- 收藏列表的2013论文条目href指向ResearchGate的publication/257271902_Decoupling_approximation_design_using_the_peak_to_peak_gain。没有发现该条目的大学PDF直链；本轮未打开它的正文。
- 全部期刊列表第22项仅列书目，无对应的机构全文附件。
- 邻近2022年不同题目的部分文字也共用了上述ResearchGate链接，故不能凭页面相邻超链接文字判定版本或论文身份。
- 本次所读Publications HTML的UTF-8文本SHA256：af28c8318b38b495df4cc0454a3cd09a60a6995bfb310ba0aae81ff03aab86a2。网页会变，指纹只冻结本次读取，不代表全文指纹。

本证据能确认作者承认该论文及其书目信息；不能把大学页上的外链存在写成“已取得机构全文”。

## 3. VTechWorks公开仓储检索

前端公开search页面在web工具中打开失败。随后直接读取同站公开Discovery API，均为无需登录的GET。通用入口：

https://vtechworks.lib.vt.edu/server/api/discover/search/objects?query=QUERY&size=100

除精确题名/DOI首次size=20外，下列变体使用size=100、page=0；没有读取无关命中全文。题名/作者元数据检查用于找目标文献，不将其他学生论文替代2013原文。

| query实际字符串 | HTTP/工具状态 | 返回总数 | 实际检查范围 | 是否找到目标论文 |
|---|---|---:|---|---|
| "Decoupling Approximation Design Using the Peak to Peak Gain" | API 200 | 0 | 返回页为空 | 未命中 |
| "10.1016/j.ymssp.2012.10.007" | API 200 | 0 | 返回页为空 | 未命中 |
| "Sultan, Cornel" | API 200 | 47 | size100返回全部47条，核题名及dc.contributor.author | 未命中 |
| dc.title:decoupling | API 200 | 18 | size100返回全部18条，核题名及作者 | 未命中 |
| decoupling | API 200 | 2783 | 只看首100条元数据，未读余2683条 | 当前页未命中，未穷尽 |
| "peak to peak" | API 200 | 1173 | 只看首100条元数据 | 当前页未命中，未穷尽 |
| "peak-to-peak" | API 200 | 478 | 只看首100条元数据 | 当前页未命中，未穷尽 |

可直接复做的精确请求：

- [精确题名](https://vtechworks.lib.vt.edu/server/api/discover/search/objects?query=%22Decoupling%20Approximation%20Design%20Using%20the%20Peak%20to%20Peak%20Gain%22&size=20)。
- [DOI](https://vtechworks.lib.vt.edu/server/api/discover/search/objects?query=%2210.1016%2Fj.ymssp.2012.10.007%22&size=20)。
- [作者词组，全部47条](https://vtechworks.lib.vt.edu/server/api/discover/search/objects?query=%22Sultan%2C%20Cornel%22&size=100)。
- [题名decoupling，全部18条](https://vtechworks.lib.vt.edu/server/api/discover/search/objects?query=dc.title%3Adecoupling&size=100)。

作者词组47条中，多条因Sultan为导师或其他元数据关系而命中，不等于47篇Sultan本人论文。返回的dc.contributor.author精确含“Sultan, Cornel”的一条为2023年不同题目文章，未将其错作目标。

这只能记录“给定公开查询未命中”，不能证明该仓储任何版本、别名、未索引附件都不存在，也不能证明论文没有合法公开作者稿。

## 4. 文献角色负责人补充的出版社公开请求：仅一次

文献角色负责人本轮提供Crossref登记的公开text-mining入口后，明确允许一次无认证请求；本角色执行：

https://api.elsevier.com/content/article/PII:S0888327012003809?httpAccept=text/xml

- 结果：Node fetch返回“fetch failed”，没有取得HTTP响应状态、Content-Type或正文。
- 没有证据将它写成HTTP401或403，也不能据传输失败判断文章访问政策。
- 未重试、未改为text/plain、未添加API key、未登录。没有采用search中过往错误PII或再次读取ResearchGate正文。
- 文献角色负责人提供的Crossref记录license=null只是一项登记状态；不能据它推断“全文开放”或“绝对禁止公开作者稿”。

文献角色负责人负责Crossref元数据小JSON和出版社综合定位；本文件只保留本角色真实请求结果。

## 5. 2017讲座旁证：不能代替2013论文

文献角色负责人已读取并交接：[University of Pittsburgh讲座页](https://www.mathematics.pitt.edu/seminar-colloquia-event/decoupling-approximation-design-using-operator-norms)，题名*Decoupling Approximation Design Using Operator Norms*，讲者Cornel Sultan，日期2017-09-29；摘要涉及用operator norms刻画近似误差、按最小误差选择系统参数，以及finite energy/finite peak设计。

本角色尝试打开该网页，工具在返回内容前连接失败，故以上属于**文献角色负责人已核来源的转交旁证**，不是本角色独立原页核验；不据它编造2013论文公式或页码。不另分新L-ID，也不把2017摘要与2013正文当同一版本。

## 6. 对C006还缺哪些具体原文

| 需要核定的字段 | 当前状态 | 取得全文后的最小检查 |
|---|---|---|
| 误差输出算子 | 未读2013正文 | 是否比较原系统与解耦近似的输出差；不能预设其算子就是H1/H0 |
| peak-to-peak范数 | 只有题名及2017旁证 | 信号点态范数、时间域、零初始条件、诱导L∞定义、是否含直通项 |
| 常数依赖 | 没有2013原式 | 增益界是否取决于完整A/B/C矩阵、极点、输出权重或优化参数 |
| 模型族统一性 | 无法裁定 | 是否有sup over ω/r/ζ0，是否仅依赖两状态共同阻尼比κ |
| 输出比与完整尾段 | 无法裁定 | 因果/双边算子、有限窗与完整域是否区分 |
| 三模态无界分类 | 没有直接原文依据 | 其维数、零点假设和输入族是否与本课题相同 |

在这些字段未核前，不能把L026标为same-claim，也不能肯定它与C006完全不等价。本轮仅将“书目真实”“全文尚缺”和“可能相关”分开。

新版V006常数与旧版之间的关系属于主控证明记录，本附件不改写旧轮次；若之后取得L026，须按最新精确命题重比，而不是只对照旧B的外观。

## 7. 新查询记录、失败边界与下一步

本轮Web查询：

1. "Decoupling Approximation Design" site:vt.edu
2. "Sultan" "2012.10.007" site:vt.edu
3. "Cornel Sultan" "publications" Virginia Tech
4. "Decoupling" "Peak to Peak" site:vtechworks.lib.vt.edu
5. "Sultan" "Decoupling" filetype:pdf -resume，域限定aoe.vt.edu/vtechworks.lib.vt.edu/vt.edu
6. "csultan" "peak" pdf，域限定vt.edu
7. "Cornel Sultan" "star norm"，域限定vt.edu
8. "Decoupling approximation design"，域限定experts.vt.edu/vt.edu

这8条查询与公开仓储变体已收束；命中目录、CV、其他学科decoupling材料，没有把名称相似的其他资料当2013全文。未遍历仓储所有泛词命中，未探测私有目录。

最高价值下一步是取得**该题名的合法作者接受稿或出版社全文**，而不是重复本附件的VT页面与精确API查询。可由作者自存档、用户现有合法副本或出版社公开入口补入；若需要联系作者，应另获发送消息授权，本轮没有发信。取得后优先核上表前四字段，暂不扩展理论分支。

本轮交付是准确的全文缺口与已试路线；未找到全文不构成创新证据。
