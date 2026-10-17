# v004范围方案：低阻尼目标与有限时长的有界整合

时间：2026-10-17 12:48:32 +08:00，Asia/Shanghai。按主控本次≤5分钟指令，仅写本方案；不改冻结v003，不实际升稿，须先等主控收齐v003数学整合与文献措辞两份审阅。C022/C023已获不同作者独审及主控接纳；原候选文件中的candidate为历史状态，不改原件。新经典norm替代路线本方案仍按待裁决候选处理。

## 结论与主次

建议纳入C022、C023，但保留原五主节和两幅主图。主线仍是“≤2有效模态有统一有限界—真实三层无界—固定失谐仍有限且局部倒数阶”；C022说明本指定族如何实现任意足够小的目标阻尼，C023说明一个设计输入族的时长与失谐残留如何共同进入下界。二者作为支撑主线的推论，不各开主节、不重写成工程设计优化论文。新增界图不为这两项所必需。

| 原位置 | 建议v004改动 | 正文保留量 | 详证与证据 |
|---|---|---|---|
| 摘要 | 现有唯一5%模型句后简述“小目标阻尼可唯一实现，指定族刚度比随ε⁻⁴增长”；现有失谐句后简述“设计包络有有限时长联合下界” | 各半句，不列新增常数和多条谱极限 | C022/C023 |
| §1、§2 | 保持固定对象、输入空间、完整峰及双模态证明 | 不因新结果扩写背景 | v003及审阅必修项 |
| §3.2 | 先保留精确5%→8%实例及L≥1唯一性，再给任意目标0<ε≤ζ*(1)的唯一Lε与首阶成本；可改小节名为“低阻尼目标的唯一存在模型” | 一段、一个组合公式；5%例子为ε=.05的特例但仍精确定义 | 附录B.2承接B.1，写实际低谱有界性、不变量、极限和逆映射 |
| §4.1 | 已有C020完整链后，补“有限包络时长”一段，写物理单位主式；后给无量纲解释 | 约两段、一个组合公式，不把所有A/B/E常数挤进主文 | 附录E.4接E.3，给统一核矩、相位、全时刻余项和联合量词 |
| §4.2 | 单位三层原六时长采样原样保留 | 一句说明其与C023解析证书分属不同证据，未代入C023统一常数作验证 | 原E010、图2 |
| §5.1、§5.2 | 依v003两份审阅必修项处理；不扩写新首创定位 | 工具先例与定理新颖性继续分开 | 文献角色及主控裁决 |
| §5.3 | 原三点结构内分别补C022、C023各半句 | 不列为两个同等篇幅的新核心定理 | 与正文一致 |

## C022：应保留的精确结论与应删的枝节

正文可用组合式：

$$\forall\,0<\varepsilon\le\zeta_*(1),\quad
\exists!\,L_\varepsilon\in[1,\infty):\zeta_*(L_\varepsilon)=\varepsilon,
\qquad L_\varepsilon\sim\frac{5+2\sqrt2}{64}\varepsilon^{-4}
\quad(\varepsilon\downarrow0).$$

这里先给ε再固定唯一模型Lε，随后才固定κ和增长输入时长；不能写成同一个已给定模型对任意ε均恰消零。L是指定M=I、k₁=k₂=1族的k₃/k₁比，不是跨模型必要刚度、最小材料或经济成本。ε的唯一性限L≥1；现有5%精确模型不以渐近数值替代。

附录B.2保留μ±=(5±√17)/4、λ₃=2L+1/2+o(1)、q~Q₀L⁻¹ᐟ²及ζ*~Z₀L⁻¹ᐟ⁴的简洁链，以Ritz界确认实际低两谱有界后再用不变量，避免仅凭降次多项式跳步。主文删去λ谱极限清单、L_(ε/2)/Lε→16例子和重复零点证明。无有限L余项、起效阈值或近似根认证。

采用独审的措辞修正：各阶共用ζ时不写“部分模态过阻尼”；写“无需κε<1，κε=1或κε>1时各模态仍稳定”。不新增施工/设备推论。

## C023：只写设计输入族的下界

固定模型及κ，r∈[1−ηκ,1+ηκ]，δ=|r−1|，存在正的模型相关A_env、B_env、E_env。对每个r及每个半支撑时长T≥T₀=2E_env/B_env，有一个两状态共同、实C1、幅≤1、支撑[0,2T]的sin²包络输入，完整峰满足

$$\frac{P_1(T,r)}{P_0(T,r)}
\ge\frac{B_{\rm env}}{2(A_{\rm env}\delta+E_{\rm env}/T)}
=\frac{C_{\rm env}}{\delta+1/\tau}
\ge\frac{C_{\rm env}}2\min\{\tau,\delta^{-1}\},\quad
T_{\rm env}=E_{\rm env}/A_{\rm env},\quad
\tau=T/T_{\rm env},\quad C_{\rm env}=B_{\rm env}/(2A_{\rm env}).$$

正文宜优先显示第一个带物理单位的式子，后两个式子可同行组合或留给附录，不直接将无量纲δ和带单位1/T相加。δ=0单独说明第一式为至少C_env τ，末式采用δ⁻¹=∞约定。T是半支撑时长，不能把2T误写成T。

详证保留四步：D±与局部正B_env；跨欠/临/过阻尼统一衰减及一阶核矩M；中心实相位和全时刻余项E_env/T；T₀统一量词及P₀>0。建议用env下标区别C020的Aκ/C0κ/C1κ和正文矩阵，公式系数仍逐项绑定已审原件。不同r允许换相位，对每个r两状态用同一输入；r可随T变化但留在同一邻域。

必须保留“仅设计输入族下界”。C020的全输入上界Uκ/δ不能补出随T的联合上界；不写最优完整峰比为Θ(min{T,1/δ})、必要最短时长、κ-only通用秒数或任意天然波的增幅。τ≥1/δ只是该证书达到C_env/(2δ)的充分条件。

## 现有新界图：推荐附录可选，不增加主图

已实际查看现有PNG，标题、双log轴、理论带、两支标记和脚注可读。它展示κ=8/5时的C020保守1/δ夹界及固定unit模型八个同频见证，既不呈现C022谱渐近，也不含C023的T联合面。因此不为“验证”C022/C023而加入它，不新作实验、谱图或时长图。

若主控确认E-EXP-T002-002图件/算术审核通过，可作为附录E图E1；主文仍两图，§4.1一句指向。建议图注明确：K为本图原定义的K_C1，虚/实线与阴影为Lκ/δ≤K_C1≤Uκ/δ的保守理论夹界；圆/加号为固定unit在Ω=S处的|Q(iS)|≤K_C1谐波下界见证，未测得K_C1或实际完整峰比、未求K在带中的位置。原L1桥接保证另一常数同阶，但不把图上K符号擅改为两常数相等。保留无最优性结论、局部域和unit高阻尼身份。

该图当前README仍记candidate；本方案只评价叙事用途，不替代主控图件接纳。若尚未接纳，则v004不嵌入图。八行数值不再另加主文表，避免与旧unit六T表争夺解释篇幅。

## v004准入与检查

1. 先收齐v003两份审阅，由主控交接必修项；冻结v003和全部既有图/原件保持。
2. 主控授权实际升版后，从v003另存v004；仅改上表指定位置，详证接B.2/E.4，统一重排新增本稿式号，不动外部文献原式号。
3. 扩展证据映射绑定C022/C023候选与独审身份；若无新图则不新增数值证据。摘要、主文、结论的量词/单位/适用域一致核对。
4. 新经典norm路线继续候选；以后若独审接纳，可另作证明精简比较，不在本轮替换核心推导或加入首创断言。
5. 保持用户已选A，不把方向再列待选；先例覆盖与投稿定位继续未决。本方案不运行实验或外部搜索、不派子任务、不操作Git或调度。

## 本次只读输入身份

以下仅记录本方案读取时的字节身份，不覆盖原候选的历史状态，不将图件自动晋升为已接纳。

- papers/damping-output-boundaries/research/roles/ideation/theory-session002/asymptotic-low-damping-candidate.md；SHA256 0b2cb2c59f8d00901a11e93379e6e3489b798d4eb92bd8e3a9e706a625ca686b；5945 bytes。

- papers/damping-output-boundaries/research/roles/verification/theory-session002/asymptotic-low-damping-review.md；SHA256 d519b911446d4d6074c742ff88a65de1d1f5aa8435cb783d4078b04c088f4515；4397 bytes。

- papers/damping-output-boundaries/research/roles/ideation/theory-session002/finite-envelope-detuning-candidate.md；SHA256 ea99a02b167720490242edc396adc6da154dd617a55dfc8df26c28c2daf3b3db；8892 bytes。

- papers/damping-output-boundaries/research/roles/verification/theory-round001/finite-envelope-detuning-review.md；SHA256 216b63ac6a84d37fceb770cd1c42a77824b6e3618395fbbc0cfc05d53010977c；5091 bytes。

- papers/damping-output-boundaries/experiments/theory-round002-detuning-bounds/README.md；SHA256 f72d78c98d901ebc912dea6f1c55f8992d35fdf90d6a10e686d179aa39d95fbc；2624 bytes。

- papers/damping-output-boundaries/experiments/theory-round002-detuning-bounds/exact_constants.json；SHA256 8b3fc9fea5b29918f090be8be424b3930511e0041f228561e9c05c391ab1b4a8；602 bytes。

- papers/damping-output-boundaries/experiments/theory-round002-detuning-bounds/fig_detuning_theory_bounds_and_harmonic_witnesses.png；SHA256 50a34b7dc93764769e47166cafee7c8f25a5bf5f79bbcf6f86e6d3f6e03b7022；337085 bytes。
