# 增阻尼输出边界文献索引

版本v003，更新：2026-10-17 09:20 +08:00。v001随提交`dacdc49`冻结，v002对应[round-002](../research/roles/literature/round-002.md)；本轮新增见[round-003](../research/roles/literature/round-003.md)，不改写旧轮次。索引存在不等于全文已核。公开全文保存在角色目录被Git忽略的local-cache或仅内存读取；指纹见[来源001](../research/roles/literature/public-source-manifest-001.json)、[002](../research/roles/literature/public-source-manifest-002.json)、[003](../research/roles/literature/public-source-manifest-003.json)及各附件。不上传原论文。

## 本轮一手原文与待核材料

| L-ID | 核实书目、稳定来源 | 版本/可得程度 | 原文定位与当前关系 |
|---|---|---|---|
| L001 | Richiedei D., Tamellin I., Trevisani A. *Beyond the Tuned Mass Damper: a Comparative Study of Passive Approaches to Vibration Absorption Through Antiresonance Assignment*. ACME 29:519–544 (2022), online2021. [DOI](https://doi.org/10.1007/s11831-021-09583-w)，[大学全文](https://iris.univr.it/retrieve/46bbe105-6514-4eba-9877-e8d007960b69/s11831-021-09583-w.pdf) | 正式版26页，全文已取；SHA256 715eb3878dc7c945cfd93bfe94f16275216d61bed67641952d6e78dcb9cb7fb5 | 已看印刷521–522/PDF3–4页，§2.2.1–2.2.2式(9)；C002 related-not-equivalent；符号及反共振框架是先例 |
| L002 | **Mario Bonk**, *Complex Analysis*, UCLA Math246A/B. [作者讲义](https://www.math.ucla.edu/~mbonk/complana.pdf) | 无核实年份/版号，187页；SHA256 f403a267bd38a622dba8c28177191b074404bd0596cb45ab81dfe77808d13019 | 已看页108 Theorem13.5式45–46、页111 Example13.9(a)；C002 conditional-extension；旧笔记误署Michael |
| L003 | Eugen J. Skudrzyk, *Understanding the Dynamic Behavior of Complex Vibrators*. [IOA旧源链接](https://www.ioa.org.uk/system/files/publications/EJ%20SKUDRZYK%20UNDERSTANDING%20THE%20DYNAMIC%20BEHAVIOR%20OF%20COMPLEX%20VIBRATORS.pdf) | 本轮原站Not found，未取得新全文；旧记录称1983 Rayleigh Medal Lecture，年份未本轮核实 | insufficient-text；不继承旧记录的全文状态，不给虚构页码 |
| L004 | De Domenico D., Ricciardi G. *Using a tuned fluid inerter for improving the seismic performance of structures isolated with friction pendulum system*. REC2021. [会议全文](https://rec2021.unime.it/papers/REC2021-67.pdf) | 会议全文14页；SHA256 2fdeab5d3b8d5d3d9ca42c7d342183cd1b313047fdac5a71e5484877c8deab47 | **印刷530/PDF7** §4，协方差及无TFI归一化，FEI另定义；页图已补核；round-001印刷页码更正见round-002 |
| L011 | Yi J., Xu W. *Effect of damping on the seismic response of long-period structures considering crossover phenomena*. Engineering Structures 293:116627 (2023), DOI [10.1016/j.engstruct.2023.116627](https://doi.org/10.1016/j.engstruct.2023.116627)；[作者机构成果清单第132项](https://www.succ.edu.cn/xxgk/Home/News/view/xwid/f23741017ea607d3fb866d9c4f5b7c77) | 作者机构题名/作者/卷号已核；出版社访问失败；未获全文，insufficient-text | 暂不据摘要判断crossover与本稿双模态公式同一，须补原文公式和输入/输出定义 |

## 继承的候选书目：本轮尚未从原文重新核验

以下仅从W5/01-文献/RY候选文献逐条核验-20261014.md读取，不能写成本轮全文复查完成。原笔记指纹见round-001。

| L-ID | 候选书目与来源 | 继承状态和所需定位 |
|---|---|---|
| L005 | Takewaki I. (1997), *Optimal damper placement for minimum transfer functions*, EE&SD26:1113–1124. DOI `10.1002/(SICI)1096-9845(199711)26:11<1113::AID-EQE696>3.0.CO;2-X` | 旧核验为仅出版社摘要；与1999为不同论文。需全文目标函数/频率/响应量；insufficient-text |
| L006 | Takewaki I. et al. (1999), *Non-monotonic optimal damper placement via steepest direction search*, EE&SD28:655–670. DOI `10.1002/(SICI)1096-9845(199906)28:6<655::AID-EQE833>3.0.CO;2-T` | 旧摘要的non-monotonic指最优布置路径，不能转为增阻尼响应必非单调；待本轮原文，insufficient-text |
| L007 | Politopoulos I. (2008), *A review of adverse effects of damping in seismic isolation*, EE&SD37:447–465. [DOI](https://doi.org/10.1002/eqe.763) | 旧核验仅摘要；隔震/楼层反应谱与本稿固定恢复力不同，insufficient-text |
| L008 | De Domenico D., Ricciardi G., Takewaki I. (2019), *Design strategies of viscous dampers for seismic protection of building structures: A review*, SDEE118:144–165. [DOI](https://doi.org/10.1016/j.soildyn.2018.12.024) | 旧核验为公开预览；SPI式13–18及31–32未核，不因L004全文可读而当同文已核 |
| L009 | Santos-Santiago M.A., Ruiz S.E., Valenzuela-Beltrán F. (2022), *Influence of Higher Modes of Vibration on the Seismic Response of Buildings with Linear and Nonlinear Viscous Dampers*, JEE26(8):3914–3937. [DOI](https://doi.org/10.1080/13632469.2020.1822223) | 旧核验仅摘要，52%的分母未核，不作本稿定量依据；insufficient-text |
| L010 | Renault A., Thomas O., Mahé H. (2019), *Numerical antiresonance continuation of structural systems*, MSSP116:963–984. [DOI](https://doi.org/10.1016/j.ymssp.2018.07.005)，[作者机构](https://sam.ensam.eu/handle/10985/15256) | 本轮未重取原文；非线性极小点延拓与固定线性体系有限ζ变化需分开；insufficient-text |

## 本地全文与新增零点专题（v002）

本地桥梁原文根目录：`E:/11-工作/001-workbuddy spaceV1/001-workbuddy space/109-论文写作/W5-重燃双塔连体/02-数据/综合研究-20261013/文献核验/`。详细指纹与原页逐项对照见[local-sources-001](../research/roles/literature/local-sources-001.md)。

| L-ID | 书目与稳定来源 | 全文/版本/指纹 | 已核原文定位、比较范围 |
|---|---|---|---|
| L012 | 马安财、谭平、周福霖(2021)，超高墩大跨铁路连续钢桁梁桥粘滞阻尼消能减震研究，地震工程与工程振动41(3):95–105。[DOI](https://pubs.cstam.org.cn/article/doi/10.13197/j.eeev.2021.03.95.maac.010) | 本地Ma2021full.pdf，11页；A1E147E0281EEB0E332D1053551606A7C421C3F822D7CF6F768AB8376CA66AB3 | 亲看印刷95/100/102；表2的51.0/60.1%是阻尼建模不同的弯矩，不能转述为增剪；C001–C004 related-not-equivalent |
| L013 | 邵长江等(2024)，近断层大跨RC轻柔拱桥纵向阻尼器减震研究，吉林大学学报(工学版)54(5):1355–1367。[DOI](https://xuebao.jlu.edu.cn/gxb/CN/10.13229/j.cnki.jdxbgxb.20220845) | 本地Shao2024-原刊核验.pdf，13页；00E1C8E0E2FDA138B86D667CEC3CA08F696E3870D7E2394FE181D0E7E9B2A492 | 亲看1360/1361，表4/5；P18-FF局部墩剪与位移目标分叉；局部非线性装置，非共同ζ解析模型 |
| L014 | Chen B., Feng Z., You H.(2018)，Seismic response analysis of long-span cable-stayed bridge with nonlinear viscous dampers under different periodic seismic waves，CEJ27(1):114–131，Article10。[期刊页](https://ojs.cvut.cz/ojs/index.php/cej/article/view/8922) | 本地CEJ2018.pdf，18页；BF0D0F596A8D562DE050560E0C360FD423ED710987D5F8FB636696BB73FF972E；metadata题名为模板，已按实际题名页辨识 | 亲看126/129表3/4；上半部明确列可作分叉先例；后半部重复列头不用于定量拟合 |
| L015 | Rath S., Awtar S.(2021)，Non-minimum Phase Zeros of Two-DoF Damped Flexible Systems，IFAC-PapersOnLine54(20):579–585。[DOI](https://doi.org/10.1016/j.ifacol.2021.11.234)，[大学全文](https://psdl.engin.umich.edu/pdf/C46.pdf) | 作者存档稿7页、无印刷页号；5ff0ae1f328473ee293bf094a70f2cec4d770251c69455bfefbb1d5c0618b12a | 已读§2–4；亲看PDF4–5，Result3式11及Result4式17。共同ζ为χ=1特例；零点分类是C006背景，非同一统一L∞常数 |
| L016 | Rath S., Awtar S.(2023)，On the zeros of three-DoF damped flexible systems，JSV560:117698。[DOI](https://doi.org/10.1016/j.jsv.2023.117698)，[NSF全文](https://par.nsf.gov/servlets/purl/10451384) | 正式版15页，online11 April2023；26d61b5fc57d1bd9c3884156aecaef724753a8443ad6f5259dcf0ce49b338bcd | 亲看页3式4–5、页4§3式6；最低阶取ωR=ζR=0。与本稿正刚度稳定三模态反例系统类不同；related-not-equivalent |
| L017 | Liu W., Tong M., Wu Y., Lee G.C.(2004)，Optimized Damping Device Configuration Design of a Steel Frame Structure Based on Building Performance Indices，Earthquake Spectra20(1):67–89。[DOI](https://doi.org/10.1193/1.1648334) | W6/01-文献/参考文献-Liu2004-性能目标与模态阻尼配置.pdf；23页；9E8A3B997F91D57A0F816B0E9F859CC8F00D1D7510AA2B7EB1E1EB15B14A1D17 | 已看14页；68式1b、79/81方法、82–84图16、87–88限制。一般目标振型配置原则same-claim；对C001–C003 related-not-equivalent。详见[原文跟进](../research/roles/literature/liu2004-followup.md) |
| L018 | MIT18.156 lecture25，[课程](https://math.mit.edu/~lguth/Math156.html)，[讲义](https://math.mit.edu/~lguth/Math156/notes/25.pdf)；未自动把教师署为讲义执笔人 | 全文4页；996490A8065004DBEC4776388FB70730BE2597588B4FB5B5E873E0D7E808AE43 | 亲看页2§1.2 Theorem3，Young端点；C006经典工具，不评价统一常数 |
| L019 | Joaquim Bruna，Harmonic Analysis minicourse notes，19 April2016，[Oxford托管](https://www.maths.ox.ac.uk/system/files/media/HarmAnLectureNotes.pdf) | 全文57页；0DBEA90B2053579BF1E23254EFF8C0C020033F7B408C975C6EBC063788290EFB | 亲看印刷19/PDF20，§2.2 Definition1、Theorem5；测度卷积定义、函数Young不等式；测度×L∞推论另列，非原文逐字定理 |
| L020 | Markus H.A. Verwoerd，Iterative Learning Control — a critical review，Twente博士论文(2005)，ISBN90-365-2133-5，[大学全文](https://ris.utwente.nl/ws/portalfiles/portal/6036402/thesis_Verwoerd.pdf) | 全文175页；836F38946E4067EC368DE41EF1A7EFDCA8420B4FA86231A6DF758CB77FD6E038 | 亲看96–99/PDF112–115，Appendix4.A；proper无虚轴极点、稳定双边核、未来信息和截窗；式4.56为L2诱导，非峰值增益 |

L018–L020逐项支持范围、失败路径、缓存文件名见[linfty-background-001](../research/roles/literature/linfty-background-001.md)。Devasia作者公开研究说明可读，但其1996/1999原刊全文尚未取得，仍为insufficient-text，未据概述补造定理定位。

## 历史方法复查范围

[history-methods-001](../research/roles/literature/history-methods-001.md)逐页读完三条来源共27轮，nextCursor均null；实际来源turn ID及条件/失败路径已记录。它核实历史方法的存在与当时修正，不代表重新确认全部历史计算。567组是合成简化模型，均分必然最优已撤回，RY>1不能直接当有限记录峰值预报。

## 输入类边界与有限变化/峰值界专题（v003）

| L-ID | 原文、稳定链接和版本 | 可得程度及指纹定位 | 已核位置与关系 |
|---|---|---|---|
| L021 | Paul Garrett，Paley-Wiener theorems，5 Jan2020，[作者Minnesota讲义](https://www-users.cse.umn.edu/~garrett/m/real/notes_2019-20/08g_Paley-Wiener.pdf) | 全文4页；SHA256 B5404CC3F3E5424A4A326D787AEC0F8559C25E3DB8F4622E00476386B82A0847 | 亲看p1定理1.1、p2定理2.1；紧支撑变换的整函数延拓，经典背景 |
| L022 | Frederik J. Simons，Slepian Functions and Their Use in Signal Estimation and Spectral Analysis，Handbook of Geomathematics ch30(2010)，891–923，[作者正式章](https://geoweb.princeton.edu/people/simons/PDF/reprints/Handbook-2010.pdf)，DOI10.1007/978-3-642-01546-5_30 | 全文34个PDF页；62769166C4D9299D6F272D736595F4090A281B6D36A5F1A628E65BA4AEBDCCB0 | p894/PDF4式1–2、p895/PDF5式3及正文；严格限带与有限时窗能量集中不同 |
| L023 | **Steve Shkoller**，Notes on Lp and Sobolev Spaces，19 Mar2009，[UC Davis全文](https://www.math.ucdavis.edu/~hunter/m218a_09/Lp_and_Sobolev_notes.pdf) | 全文52页；D821AD5B8FEEBB81500E9C0F6DB2EBD137F4298D6C26EFE5E0F0FE21F294AA7A；作者不能按hunter托管目录误署 | p33微分乘子、p38 Theorem3.20 Plancherel，均看原页；相对谱矩为标准组合推论 |
| L024 = L030 | Ascoli-Arzelà Theorem，MIT18.100B，[同一4页讲义](https://math.mit.edu/~rbm/18.100B/Ascoli-Arzela.pdf) | 两个独立复查路径取得同一SHA256：9F5E55753F508472C81E1DA0CE3D488107CD33743CA2B449B01E8779C6768EF0；**别名，不重复计文献** | p1未编号Theorem及式1。文件未署作者/日期；C010的经典紧性工具，不直接给结构峰值界 |
| L025 | G.A. Papagiannopoulos、D.E. Beskos，Seismic Inelastic Design of Steel Structures by Spectrum Analysis and Equivalent Damping，14WCEE(2008)，[会议全文](https://www.iitk.ac.in/nicee/wcee/article/14_05-05-0038.PDF) | 全文8页，仅内存读取；85b72983a5ea9ea2cffab1c261bcd043f801d16f9f423fef3b165b629ef0ea19 | 看PDF3–4，式2.1–2.3；绝对加速度含直通项、频率曲线平滑，与C001相关非等价 |
| L026 | Cornel Sultan，Decoupling Approximation Design Using the Peak to Peak Gain，MSSP36(2):582–603(2013)，[作者CV](https://www.aoe.vt.edu/content/aoe_vt_edu/en/people/faculty/sultan/personal-page/resume/_jcr_content/content/download/file.res/Short%20Resume_CornelSultan_2021.pdf) | 作者CV第4页Journals28核书目；论文全文未取，DOI候选未一手独立核；insufficient-text | 连续结构解耦/peak-to-peak的具体全文优先项，不能据题名判C006重复或新颖 |
| L027 | Z. Tomljanović、C. Beattie、S. Gugercin，Damping Optimization of Parameter Dependent Mechanical Systems by Rational Interpolation，arXiv1707.01789v1，6 Jul2017，[作者大学全文](https://vtechworks.lib.vt.edu/server/api/core/bitstreams/f2f89fa1-d571-46cc-b97f-3db584535cee/content) | 预印本v1共25页，仅内存读取；7df1cbda2759b9ef7cfa5160771a3b0bb35e7dc0c0ca25ba2f82f900b40d661b | 亲看页3；式3及6–7，具体模型H2范数控制单位L2输入峰值，不是输出/输出κ-only界 |
| L028 | J. Abedor、K. Nagpal、K. Poolla，A Linear Matrix Inequality Approach to Peak-to-Peak Gain Minimization，IJRNC6(9–10):899–927(1996)，[Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1002/%28SICI%291099-1239%28199611%296%3A9/10%3C899%3A%3AAID-RNC259%3E3.0.CO%3B2-G) | 仅出版社摘要/引文；insufficient-text | 可确认peak-to-peak/star-norm研究背景，不能据摘要核定理或裁定C006 |
| L029 | S. Schuler、F. Allgöwer，ℓ∞-Gain Model Reduction for Discrete-Time Systems via LMIs，ACC2009:5701–5706，[会议全文](https://skoge.folk.ntnu.no/prost/proceedings/acc09/data/papers/0884.pdf) | 全文6页，仅内存读取；ca5a6791099a1b7271bde582a2734c41c585f59cf03440ee5295c538d7469a22 | 亲看5702/PDF2，Theorem1式4a,b、Remark1及式5；单离散模型LMI上界，非C006相同量词 |
| L031 | Romyar Sharifi，Point-Set Topology Chapter3，[作者UCLA HTML](https://www.math.ucla.edu/~sharifi/notes/topology-ch03.html) | 公开全文HTML已读/缓存，d32e470eb7a173772207144d52756bdebf9316c4a7a9661bf884bc2eb1def43d | §3.2 Prop3.2.9、Thm3.2.10、Cor3.2.11；紧集映射/逆连续的定性背景 |
| L032 | Leon Simon，Lectures on PDE，[作者Stanford全文](https://math.stanford.edu/~lms/lecs-on-pde.pdf) | 全文118个PDF页、每页双印刷页；e1f1b2f51d2558aa467a8c064fe82e7b9e157ad28c9c75f01e38596cde656870 | 亲看印刷48–49/PDF27，Lecture5 Lemma4(Rellich)、式c/f；相对H0^1输入类的经典工具，文本乱码处已看图 |

附件：[严格支撑/限带及相对约束](../research/roles/literature/support-bandwidth-background-001.md)、[紧性原文背景](../research/roles/literature/compactness-primary-background-001.md)、[映射校对](../research/roles/literature/compactness-mapping-audit.md)、[C001/C006专题查重](../research/roles/literature/c001-c006-targeted-search-001.md)。

创新核查状态：未完成专题穷尽检索；已检查来源中的相似基础不等于完整重复，未查到等价式亦不代表首次。
