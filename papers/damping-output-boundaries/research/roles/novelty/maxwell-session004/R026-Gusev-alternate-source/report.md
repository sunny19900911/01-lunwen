# R026｜Gusev2017：MathNet替代全文通道核查

结论：**新定位到MathNet正式条目及全文链接，但仍未取得PDF正文，M-C018同条件发表覆盖继续 unresolved。** MathNet全文工具请求发生连接失败，随后一次直接请求发生SSL握手超时；没有HTTP状态或正文可供定位。到此停止，不重试旧出版方入口、不换镜像或协议、不从摘要裁定覆盖或排除。

本轮2026-10-18 04:53:04 +08:00开始，限8分钟，总截止07:09:45不变。只新建本目录；没有新证明、计算、数组、原工程表、求解器、共享或Git操作。

## 新确认的书目身份与实际访问

在本轮唯一查询 `"10.15826/umj.2017.1.003" Gusev MathNet` 后，实际打开[MathNet正式条目](https://www.mathnet.ru/eng/umj31)，核到：Mikhail I. Gusev，*An algorithm for computing boundary points of reachable sets of control systems under integral constraints*，Ural Mathematical Journal，2017，3(1)，44–51，DOI `10.15826/umj.2017.1.003`。这是官方书目层级的题名／作者／卷期页码确认，**尚未核验PDF内标题页、具体正文版本或页式**。

实际过程见[search-log.json](search-log.json)：

1. MathNet条目打开成功，返回同站archive页面，提供Full-text PDF链接；未访问页面登录／注册入口。
2. 对该条目的全文链接33进行web点击，工具返回 `Fatal error: connection failed: error sending request`；没有返回HTTP状态、正文或最终目标URL，不补造403／404。
3. 对检索已显示的[MathNet PDF候选](https://www.mathnet.ru/links/7b6f4d5c1811f3c1fea809beecf5190d/umj31.pdf)作**一次**直接请求，20秒超时；仅允许MathNet站内重定向，防止回到旧出版方入口。实际报错为 `<urlopen error _ssl.c:993: The handshake operation timed out>`；未取得任何PDF字节。详见[retrieval-attempt.json](retrieval-attempt.json)。

未重试R027已经失败的umjuran出版方PDF／SSL入口。检索结果中的其他站点未打开，没有第二条查询、HTTP降级、登录、付费、请求作者或绕过访问限制。local-cache为空；正文SHA为null，不能把失败日志的SHA当正文SHA。

## M-C018逐项覆盖状态

以下对照键来自已审旧[非零末力R017](../../../verification/maxwell-session004/非零末力耗散峰力区间独审-R017.md)与[文献R027](../../../literature/maxwell-session004/R027-nonzero-terminal-dissipation-prior-art/report.md)，本轮不重推定理。Gusev正文未得，因此不填“有”或“无”。

| 必须核对的同条件内容 | 本轮Gusev正文证据 |
|---|---|
| 带恢复漂移的Maxwell／等价阻力系统；总速度的固定幅值界，不能改成无漂移输入后沿用原界 | 未取得，未知 |
| 成本是真实状态耗散∫F g(F)，不是输入平方、净功或仅泛称积分成本 | 未取得，未知 |
| F0=0、FT=σh非零，末总δ自由；共同固定T | 未取得，未知 |
| 绝对峰恰为M并实际触峰，不只是abs(F)≤M的路径界 | 未取得，未知 |
| 全局最小Lh、全局最大UTh及各自实际达到 | 未取得，未知 |
| 两端之间每个耗散值均可达；换号轨迹、α范围与正则性条件兼容 | 未取得，未知 |

同样不能判断该原文是否提供**足以完整特例化**的通用可达工具：题名和摘要只构成检索线索，不证明它只给PMP必要条件，也不证明它没有充分性结果。即使今后取得一般定理，仍须保留控制／成本缩放、端点、触峰事件及全集取满的对应；“通用框架可表达”与“原文已打印同条件式”应分别登记。

固定D峰反解不是原M-C018查重所必需的额外条件，不能以此人为排除先例。当前C038仍只按已准入状态记为经典受限逆推论，不因本轮未取得Gusev正文而增添首创或发表空白主张。

## 与旧失败记录的关系及冻结

R027旧记录是：出版方元数据可读，PDF工具Internal Error但无HTTP状态，随后landing获取SSL超时；没有保存该旧PDF确切直链。其源状态为fulltext_obtained=false、body_SHA=null。只读协作者核对这条失败链及M-C018比较键，未查询、下载、计算或写文件。本轮新增的是MathNet书目确认和新的访问失败记录，不改写旧记录，也不宣称完成Gusev原文排重。

原输入SHA见[input-freeze.json](input-freeze.json)，新元数据和读取层级见[source-manifest.json](source-manifest.json)，最终身份／旧件保持及限时校验见[validation.json](validation.json)。本轮结论为真实unresolved；冻结后停止。
