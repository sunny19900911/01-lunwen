# R017 v002根次数守卫：定点修复复核通过

角色1；开始2026-10-18 01:18:01 +08:00，限4分钟。只核v002对[R016](../R016-helper-review/report.md)最小反例的修复，不扩展原审查范围。输入及实跑结果见[review-results.json](review-results.json)。

## 裁决

v002 SHA256=`d4c8443436a48c7ed96194d58ad6795633a8365c415bc539042cd52acc396fcd`与指令匹配。两个根入口在任何Fraction幂计算前均用`type(degree) is not int`抛TypeError。原反例`root_endpoint(.1,2.0)`及`root(I.point(.1),2.0)`现均TypeError，修复有效。

真正builtin int的2/3路径保持：统一换行后，删除新增守卫的两个函数数学正文与v001逐字符相同；AST比较亦相同，其余数学函数AST不变。须区分“数学正文未改”和“原始字节未改”：v001使用LF，v002转换成CRLF，故不能声称整个原路径原始文件字节原样保留。该格式差异不影响本次修复判断；本轮未写回源码。

## 实跑验证

只读python -B/runpy执行v002自检，453项通过，包括新增10项：2.0、3.0、Fraction(2,1)、字符串'2'及True，分别在两个入口拒绝。本人额外逐项调用同10种组合，均TypeError；另作20次真正整数根的精确Fraction端点幂检查，均包住输入。内部作者子审独立核了SHA、两入口守卫、AST不变及453项通过；不等于角色2独审。

v001源SHA仍为`539c60958ececa73b72c160b60a1da7f4925bbdae268f79acef07101cde64a4b`，未改，原R016缺陷报告保持。v002只修复这个API缺陷，有限自检不是普遍机器认证。

## 保留合同与停止

继续依赖IEEE binary64 nearest、渐进下溢、无FTZ/DAZ、运行舍入模式保持、正确nextafter及精确Fraction语义；sys.float_info与有限检查不单独证明这些运行假设。I.point代表转换后的float点，精确有理数须I.rational；本修复未改变该区别。v001审查中列出的保守溢出拒绝与其他输入边界仍保留。

本裁决仅为“v002封闭已定位的浮点degree漏洞，原整数路径保持”，不代表ODE残差实现、认证I累积、末能量或连续全尾峰证书通过。只写本R017新目录的报告与小JSON；未ODE、真实数组、外搜、旧R016、源代码、共享或Git修改。冻结交接后停止。
