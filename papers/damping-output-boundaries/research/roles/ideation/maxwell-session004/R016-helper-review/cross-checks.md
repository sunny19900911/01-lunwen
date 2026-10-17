# R016 作者侧交叉检查

两名内部子审只读源、用python -B/runpy执行有限挑战，未写根目录或源码、未ODE/外搜/真实数组。本记录不代替角色2独审。

- peak_bound_audit：整数次数及合法binary64输入合同下，四则、下溢、根精确幂、signed幂和导数权重未发现失包；确认多余平方和先求倒数的异常属于保守拒绝。补充API挑战后独立复现root_endpoint(.1,2.0)失包，明确须限制degree为真正int。
- spectral_zero_order：独立发现同一浮点degree失包；核Machin精确有理界、整数角约化、25次多项式加27阶余项正确，并检查大整数角和负角。指出point(Fraction)不是精确有理包络，应使用rational；根候选只能在整数次数路径由精确幂认证。

源SHA均匹配539c60958ececa73b72c160b60a1da7f4925bbdae268f79acef07101cde64a4b。当前内部真正整数次数调用未触发该例，但不能据此将完整API标为无条件通过。
