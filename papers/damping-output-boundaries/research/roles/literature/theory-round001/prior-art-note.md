# 理论主线首轮：二阶核先例的新增定位

2026-10-17 12:25 +08:00；范围：L034、L035与C006/V006。限8条搜索，实际8条；未扩查Sultan，未登录、付费或联系作者，未改共享账本和旧稿。

## 人话结论

我们找到了其中一篇老论文的作者公开版本。它研究的是“一个振子怎样被最不利的外力激起最大位移”。我们的核心问题是“同一个外力下，加阻尼前后两个结果能差多少”。两者有关，但不能直接画等号。另一篇更接近的老论文仍缺全文，所以现在不能宣称首次。

## 真实新增与证据限度

L035公开页标明Jiecai Luo于2015-06-16上传原文。本轮web成功解析两页作者上传PDF：印刷311页§II式(1)以x1为输出，输入进入x2导数方程；式(3)为该系统的BIBO积分。312页续证明采用几何级数，并讨论其他阻尼分支。因此它比书目线索多了原文对象和页式定位，不能继续一概写“未见正文”。

但是：本轮PDF文本提取丢失若干根号、正负号及范数下标。截图调用返回成功标识，当前接口没有把像素交给本角色；不能冒称视觉核过。直接下载为403；未重试绕过。原文精确积分常数、式(1)全部系数、阻尼分支的完整结论仍需原页视觉复核。没有本地PDF，不能提供PDF SHA-256。

- [作者公开页与上传说明](https://www.researchgate.net/publication/3023605_On_Evaluating_the_bounded-input-bounded-output_stability_integral_for_second-order_systems)
- [两页作者上传PDF](https://www.researchgate.net/profile/Jiecai-Luo/publication/3023605_On_Evaluating_the_bounded-input-bounded-output_stability_integral_for_second-order_systems/links/55802f8008ae87edac4c900d/On-Evaluating-the-bounded-input-bounded-output-stability-integral-for-second-order-systems.pdf)
- [正式DOI](https://doi.org/10.1109/9.839956)

本轮只在上述原页已可读的变量和文字范围内判断；没有从乱码重建并归引精确公式。原页夹带上一篇末尾与下一篇开头，比较只针对Lee/Luo题名至其参考文献，不混用相邻文章。

## 对C006的定位：相关但不等价

本研究对象以冻结[V006](../../verification/round-006.md)为准：R=s/(s²+2αs+β)，α>0、β>0，核k=g′。从它的定义可独立看出，这是位移核的导数；若一般振子输出取位移，其常数分子冲激核就是g的缩放，而不是g′。原文输出x1与本研究纯s分子之间因此还有具体映射步骤；不能把原文式(3)直接标成V006的速度核公式。

即使将来证实老论文涵盖该速度核，仍须另核以下三个层次：

1. 一个给定二阶系统的精确输入→输出增益，是否还给出了对所有α>0、β>0统一的1/α估计。
2. 是否讨论β→0+的标量锐性及β=0约消后范数的差别；本轮原文可读片段不足以回答。
3. 由单核因子推到同一输入下H1/H0的输出→输出比较，需要额外的因子分解、可消零点、双边核、直通项和退化分支控制；它与单系统BIBO积分不是同一个量词。双模态κ-only界是否已被其他文献覆盖仍未排除。

关系标签：L035对一般BIBO计算背景为`related-not-equivalent`；对V006具体1/α、标量锐性及全部退化分支为`insufficient-text`。这不是主张“老论文没有这些结果”。

## L034：本轮未补到全文

新定向搜索只找到[ResearchGate条目](https://www.researchgate.net/publication/242505922_BIBO_stability_integral_L-gain_for_second-order_systems_with_numerator_dynamics)，明确无全文。题名与公开摘要指向带有限零点的二阶系统，是更应优先补核的候选；摘要不能确认它覆盖纯s分子、全阻尼参数统一常数或锐性。页面打开一次为工具Internal Error；搜索返回的无全文状态可读。没有重试先前429的ScienceDirect/API，也没有把题名/摘要替代证明。

## 可用于新理论稿的表述

“本文采用经典BIBO/冲激核L1工具组织峰值比较。二阶系统BIBO积分已有专门研究；本文所用标量估计的先例覆盖尚需进一步核查。当前研究重点是共同阻尼变化下、同一输入与固定输出的完整时程比较，以及两模态可统一控制与三模态物理反例之间的边界。”

作者可将L035作为二阶BIBO主题背景，附p.311 §II式(1)–(3)、p.312续证明定位；正式写入精确式之前补视觉核。不要称“新L1原理”“首次得到速度核公式”，也不要因当前检索未得L034而宣称核心定理首创。用户已选A理论主线；该选择不等于创新性审核已经完成。

## 实际查询与失败记录

本轮精确8条查询见[运行清单](manifest.json)。新增有价值入口为L035作者公开上传；L034无全文。DBLP题名记录打开为Internal Error；RG的相对下载链接被工具错误拼到/publication/profile而404，将同一页面所给/profile/Jiecai-Luo路径按站点根目录正常解析后web成功读取PDF，不是规避访问限制。另一Read full-text相对链接被拼成/publication/publication而404，未再重试。直接PowerShell下载同一公开PDF及smallpreview均403，未保存文件；浏览器一次只读查看超时，未重试。

全文缓存没有新文件。既有literature/.gitignore的local-cache/规则已只读确认；未将全文、长摘录或截图写入交付目录。manifest记录实际输入SHA，而不是把自写笔记SHA冒充原文SHA。

下一项最高价值工作：由能显示PDF像素的已有环境核L035两页，确认输出、式(3)与结论实际范围；另一次有新入口的任务再补L034，避免重复同样的失败搜索。该次视觉复核可以关闭局部证据缺口，不能单独关闭整个论文的新颖性问题。
