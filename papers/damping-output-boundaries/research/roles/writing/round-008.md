# 写作第八轮：5%→8%物理topcut存在性推论

- W-R008；核读后的精确时钟2026-10-17 10:07:44 +08:00，完成时间见末尾。
- 起点HEAD：243cb3a141ca007ecec8b07902bb1e87ea970d1d。仅写manuscript和writing目录，无Git索引、求解器或大原始数据读取。
- 产物：[working-draft-v008.md](../../../manuscript/working-draft-v008.md)、[figure-map-v008.json](../../../manuscript/figure-map-v008.json)。v007在10:05:52已冻；C017到达后另写本版。

## 1 实质增量

主控正式接纳C017后，作者完整读取ideation round009、verification appendix-V011-low-damping-IVT及low-damping-bracket.json。新稿只在摘要、§3.3末短推论、结论2增加另一固定三层模型的精确5%→8%存在性，附录E给完整谱端点与IVT证明。C016 v2一般正m/k/每κ定理及unit .2606565→.4170504展示保持原样。

模型族为M=I、k=(1,1,L)，实际弹性topcut为L(u3−u2)；q(L)=D/(4S³)连续。L=1时det=1、trace=5，D≥8、S³<60，故q(1)>1/30。固定二维空间u2=u3的Ritz上界给ω1+ω2<2，v=(0,1,-1)的Rayleigh商给λ3≥2L+.5，故q(20000)<1/400。上下端严格，且不求端点特征值小数。

根集Z={L∈[1,20000]:q(L)=1/400}非空紧，精确定义L*=min Z∈(1,20000)。这个最小仅相对于指定区间根集，不是全局最小可行刚度；未证明单调或唯一、未计算实际根。20000是保守存在区间上界，不是L*数值或工程参数建议。

选定同一个L*后M/K/b/ell/完整模态固定，ζ0=1/20、ζ1=2/25恰为5%/8%。式（9）给基态分子在Ω*=S(L*)精确为0、新态为−39L*/25非零；模态分母无消零，C差(3/50)sqrt(K)正定。沿原全t包络，固定模型/阻尼对存在共同有限输入族使完整峰比无界，输入时长变化，绝对响应BIBO一致有界。

这项推论不是每组三层都在5%→8%失界；不改变单位链临界ζ约.2607的数值身份，也不解释E001原生5.571164%净差增长或工程风险。经典C可稠密、相邻逐层dashpot的更窄拓扑不在证明内。

## 2 新增源快照与SHA256

| 输入（相对仓库根目录） | SHA256 |
|---|---|
| papers/damping-output-boundaries/manuscript/working-draft-v007.md | 9124235fb7fd66b482eb6d3e4492c30917908378a1d1baaa5a067ee12ecdf74e |
| papers/damping-output-boundaries/research/roles/writing/frozen-round007.json | 6c9a17c8c316dd359fa3033d3ba70f029777bc8d3161312d5b7c01fc0059cf68 |
| papers/damping-output-boundaries/research/claims.md | 58f03db95225151d351de5678cae1f8c1636dab159d37d1675204442f9724eb0 |
| papers/damping-output-boundaries/research/roles/ideation/round-009.md | 886f37bd66938f3ec2c5a152588d7c6baade247d6fb034e39489dac31faa2b33 |
| papers/damping-output-boundaries/research/roles/ideation/low-damping-bracket.json | 01c37a54b4b21665cfed234c106f8f947363c8d33ed895f728fdcb0a7c05c299 |
| papers/damping-output-boundaries/research/roles/verification/appendix-V011-low-damping-IVT.md | c6c2877aa7ad31922ecaa22c0406efcc75f7c6622fa89dfe4938065266b26ee0 |
| papers/damping-output-boundaries/research/roles/verification/addendum-V011-general-topcut.md | 9e411f53f706d2cb5489f7e559a4ba064a0ac8176dd0c57676a50f7865b1b70e |

## 3 审核与范围

数学子代理完整读取源证明并实际对照v007/v008，未发现C017新增段的数学错误；Ritz方向、两个严格端点、紧根集、冻结L*后两个状态及全尾段均通过。按其建议，主文短段明确“区间[1,20000]内根集最小元”，附录E直接用ω1/ω2/ω3，避免标量b与输入向量b重名。

作者未运行Fraction脚本、谱求解、根定位或时程；low-damping JSON仅记录源角色两个端点有理检查，其值不能代替连续性/min–max证明。精确参数定义与解析存在性不需要把浮点数判为恰等于.05，也不虚称已完成数值模型实例或定向求根认证。

原3幅图、E001/E007数表、C011数值证据、C012排除及附录A/B/C/D全部保留；新增E1—E4。图序映射仅将draft改成v008，不为存在性补造数值曲线。仍无实际L*或低阻尼时程峰值表；unit六T若后续交付，需独立按其单位模型身份读入，不换成新L*模型。

## 4 下一步

优先接收主控已审核的单位模型有限输入展示与新文献对照。严格区分采样峰、全尾段、连续峰认证和解析无界结论；不重复实验、求L*或增设模型。一般物理结果的同条件先例/首创、真实工程完整投影和用户最终选题仍未闭合。研究截止2026-10-17 10:47:23 +08:00保持。

第二位子代理完成全文跨版本范围检查，结论无必需修复：C016每组/每κ、C017另一固定L*、unit参数标签、最少有效模态/仅1DOF链层数、旧C008/E004排除与新topcut相容、外部工具归引均通过。三项可选用词压缩（工程段泛称理论结果、附录B指向§5.1、[3]称含刚体的零点分类）留下一次收敛，不为措辞整理改变本版已核旧段落。

冻结时钟：2026-10-17 10:11:14 +08:00。最终QA通过：3个新文件UTF8无BOM/LF与行尾空白，全部图文链接，33个唯一式号/显示数学环境；4份旧清单所列冻结字节保持；原附录A/B/C/D、unit数值展示、工程/E007段逐段不变，6个图源SHA一致。C017的Ritz方向/严格端点/区间紧根集/固定L*与精确5%8%符号已由数学差异复核和全稿范围复核通过；git diff --check退出0。未重算谱/根/时程/拟合、改图或Git索引写。
