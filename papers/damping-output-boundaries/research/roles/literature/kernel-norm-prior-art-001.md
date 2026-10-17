# 二阶核范数既有背景核查 001

- 时间：2026-10-17 09:33 +08:00；角色：local_literature；本轮定向检索12条查询后收束，不扩理论分支。
- 冻结输入：verification/round-006.md，SHA256 `6A9E9758D4F9B07D0D57CBBFF80BD8B8B15349C155C4FF504724C2C1DEFAAD60`；仓库HEAD `045739d2bd1dba51c47c6a21c4622ebe578240e6`。V006的α、β均各自严格正，不能缩写成仅αβ>0。
- 本包不验证V006证明或创新性；不将单个标量核的L1/peak gain结果提升为双模态模型族的输出/输出统一界。

## 结论

已确证经典工具：稳定SISO系统的peak gain等于冲激核L1范数，也等于阶跃响应总变差；频域H∞与peak gain是不同范数。作者公开全书L033给出原页及式号。

检索还命中与具体二阶核高度相关的既有题名L034（2000，带分子动力学的二阶系统BIBO积分）和L035（2000，二阶谐振子BIBO积分评论）。两篇书目已由出版登记核实，原刊全文本轮未取得。因此本轮不能声称V006中Rαβ的精确L1式或统一1/α界已被原文覆盖，也不能声称它们未被覆盖。正式写作不采用“新核引理”创新措辞；先补核L034正文。

## 1. 原文、定位与获取程度

| L-ID | 来源与公开链接 | 获取程度与版本 | 准确支持及未核范围 |
|---|---|---|---|
| L033 | Stephen Boyd & Craig Barratt, *Linear Controller Design: Limits of Performance*, Prentice-Hall, 1991, ISBN0-13-538687-X；[作者Stanford主页](https://web.stanford.edu/~boyd/lcdbook/)，[完整PDF](https://web.stanford.edu/~boyd/lcdbook/lcdbook.pdf) | 全文426页。作者页明确版权已归还作者；本轮下载公开完整PDF。印刷p.97/98/99/118（PDF106/107/108/127）已渲染并视觉核 | p.97 §5.2.5式(5.4)-(5.6)：peak gain定义、等于冲激响应L1及反时符号最坏输入；p.98开头及Fig.5.3：等于阶跃响应TV；p.99式(5.9)-(5.10)：RMS=L2诱导增益=频域最大幅值；p.118 §5.5.1式(5.33)：H∞≤peak gain，并给依赖极点数n的一般比较界。没有在本轮核页发现专门针对R=s/(s²+2αs+β)的闭式/1/α界；这不是全书排除性核查。 |
| L034 | K.H. You & E.B. Lee, *BIBO stability integral (L∞-gain) for second-order systems with numerator dynamics*, Automatica, 2000, 36(11):1693-1699；[DOI](https://doi.org/10.1016/S0005-1098(00)00075-3)，[出版社记录](https://www.sciencedirect.com/science/article/pii/S0005109800000753) | `insufficient-text`：Crossref出版登记返回真实题名、作者、卷期页码、DOI，无abstract；[IFAC官方卷期目录](https://www.ifac-control.org/publications/1998-2000/2000_5/at_download/file)列出同题名与作者。出版社正文和官方Article API本轮429，未取得全文 | 只能确认已有论文专门研究“二阶系统+分子动力学+BIBO积分”这一主题。不能凭题名断言含速度核R、对全部阻尼分支有效、给1/α界，亦不能凭不可读判定不重合。页1693-1699是书目范围，不是已读公式定位。 |
| L035 | E.B. Lee & J.C. Luo, *On “Evaluating the bounded-input-bounded-output stability integral for second-order systems”*, IEEE Transactions on Automatic Control, 2000, 45(2):311-312；[DOI](https://doi.org/10.1109/9.839956)，[IEEE记录](https://ieeexplore.ieee.org/document/839956) | `insufficient-text`：Crossref出版登记确认作者、题名、卷期页码、DOI；本轮IEEE正文工具不可访问，未给具体HTTP码。第三方搜索文本有原文线索，但不作为本包已核一手公式 | 可登记为更早的二阶BIBO积分文献线索；不能填入未从原页看见的Proposition公式、输出坐标、阻尼范围或常数。页311-312仅是书目范围。 |

L033 p.118式(5.33)原式为

    ||H||H∞ ≤ ||H||peak ≤ (2n+1)||H||Hankel ≤ (2n+1)||H||H∞.

此处n为该传递函数的极点数；它是固定系统的范数比较，不是阻尼变化对H1/H0商的统一估计。书内该式追溯Boyd & Doyle [BD87]，本轮未另取1987论文原文，引用时不能声称已复核其原始证明。

## 2. 与V006的精确映射

| V006对象/问题 | 原文可支持 | 仍需区分 |
|---|---|---|
| Rαβ=s/(s²+2αs+β)，α>0、β>0；因果核k=g' | L033式(5.4)-(5.5)提供由k的L1范数衡量有界输入到峰值输出的标准框架 | 这只定义一个标量系统的输入/输出增益，不提供β全域上的具体最优系数 |
| g为1/(s²+2αs+β)的冲激响应，k=g'；通过极值计算∫|g'| | 因R/s=1/(s²+2αs+β)，g又是R的阶跃响应；L033 p.98的TV框架直接相关 | 精确欠/临/过阻尼表达式和1/α统一估计仍须读L034或另作独立审核；本包没有把团队公式归给Boyd |
| 把若干有理因子组合以控制同一输入下两阻尼输出之比 | 经典卷积/有限测度范数工具可供应用，参见既有linfty-background-001.md | 单因子核范数≠双模态模型族输出/输出统一常数；还要检查商Q、可消零点、proper、双边核、固定输出和完整时程等模型前提 |
| 某个因子常数可逼近 | 对标量输入增益的极限或锐性，量词只在该标量类内 | 不能推出多个因子可同时饱和，更不能推出C006最终乘积常数锐 |
| supω|R(iω)|与∫|k| | L033 p.99式(5.9)-(5.10)、p.118清楚区分L2/H∞与peak gain | 不能把H∞频域最大幅值直接作为任意时程峰值增益；本轮没有把两者数值相等作为假设 |

对作者的建议表述：“采用经典peak gain/冲激核L1及阶跃响应总变差工具，计算所需二阶因子估计。”具体参数统一估计的已有覆盖状态仍待L034原文复查。不要写“提出新的L1原理”，也不要将本轮未取得正文写成排除先例的证据。

## 3. 12条定向查询与筛除结果

实际查询依次为：

1. `"second order" "L1 norm" "impulse" control`
2. `"second-order" "peak-to-peak" "norm" impulse`
3. `"L1 norm" "second order" "coth"`
4. `"s/(s" "L1" "damping" norm`
5. `"L1 norm" "second-order systems"`
6. `"impulse response" "coth" control norm`
7. `"L1" "damped" "cos" transfer function norm`
8. `"peak-to-peak gain" "second order" -Sultan`
9. `"BIBO stability integral" "second-order"`
10. `"Optimized parameter selection using" "L1"`
11. `"Computing the L1 norm" transfer function Boyd`
12. `site.stanford.edu boyd "peak-to-peak" "L1"`

命中L034/L035以及L033后停止扩搜。未重搜分配给其他角色的Sultan全文。搜索结果中的机械系统L1燃料最优化、离散IIR滤波器、图像总变差/稀疏回归属于不同对象，未作为当前核估计先例。

另有Rutland & Lane(1995), *Computing the 1-norm of the impulse response of linear time-invariant systems*, Systems & Control Letters26(3):211-221，DOI10.1016/0167-6911(95)00022-2的真实书目（Crossref已核）。它是一般数值算法线索，本轮没有原文，没有分配新L-ID或借题名补写二阶闭式，避免增加无实质证据的引用条目。

## 4. 输入指纹、失败路径与交接

原文/取回记录只放本角色被忽略的local-cache。新写本报告可版本化。

| 缓存 | SHA256 |
|---|---|
| kernel-boyd-barratt-1991.pdf | 7287E1EE59E6155976BD1AFC19E9BE799F7B5BE359E497B15CE121B3C054DD18 |
| kernel-crossref-metadata.json（L034/L035及Rutland1995公开书目） | 29A6431F32E79760979B80003395A9DA7A4FCBEC4BF87F2146713BA213AF98FC |

- 取回时间：2026-10-17约09:29 +08:00。公开Stanford PDF经Invoke-WebRequest成功；pdftotext定位，pdftoppm指定PDF106/107/108/127页生成页图，view_image视觉核对。
- Poppler有“Symbol display font”警告，但四页实际公式均可辨读；OCR/提取文本把∞错成1，因此以页图判断(5.4)-(5.5)、(5.9)-(5.10)、(5.33)的范数下标。
- ScienceDirect正文URL：`https://www.sciencedirect.com/science/article/pii/S0005109800000753`，web返回HTTP429。官方Article API：`https://api.elsevier.com/content/article/PII:S0005109800000753?httpAccept=text/xml`，直接公开请求返回HTTP429。未重试规避限流，未登录。
- DOI跳转和IEEE页面工具返回不可访问，无可核HTTP码；不把工具不可访问擅自记成403。Crossref公开metadata实际成功，无abstract，不等于原文已读。
- 下一项最高价值取材是合法取得L034 pp.1693-1699，核其一般分子如何映射R的纯s分子、阻尼分支、精确积分式及是否给统一上界。取得之前，具体二阶式的prior-art状态保持未闭合；C006结构性输出比结论另由主控与验证者处理。

