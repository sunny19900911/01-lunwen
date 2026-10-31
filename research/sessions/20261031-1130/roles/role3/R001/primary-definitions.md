# 参与质量、质量投影与弹性层剪力：原文定位

角色③，session020/R001。首项开始11:39:21+08，原定10分钟；本文件仅核对定义并提供作者用语，不裁决工程数据是否满足条件。人类在本聊天另要求继续写90分钟，后续仍遵守角色所有权；不改主控窗口、不设第二调度。

结论：CSI定义支持从有效模态质量与一致的带符号质量投影消去广义质量；不能仅据此把Ritz质量投影认作精确有限元弹性层剪力。Song支持区分弹性恢复力输出和包含阻尼力的输出，不直接证明本候选公式。

## 1. 最近的一手定义

| 原文与定位 | 已核内容 | 支持范围 |
|---|---|---|
| CSI Analysis Reference Manual，July 2016，Revision 15；印刷366/PDF388，Eigenvector Analysis | 自由振动特征问题为(K−ω²M)φ=0；模态工况可采用不同状态的刚度与质量源 | 同模型、同状态的真正特征模态满足全空间关系；工况名称或相近周期不足以确认共同M/K |
| 同上，印刷372/PDF394，Ritz-Vector Analysis | 从起始荷载的静力位移生成Ritz向量，随后正交化，输出振型和频率；其性质依赖起始荷载，足够多时部分结果才可能接近固有模态 | Ritz有频率及模态输出，不意味着每列都满足全空间特征关系。投影关系的数学解释见下文，非手册逐字公式 |
| 同上，印刷376/PDF398，Participation Factors | f_xr=φ_rᵀm_x；m_x为单位X向平动加速度荷载；φ_rᵀMφ_r=1 | 手册中参与因子同时是该归一化下的广义荷载；不能不看归一化就替换任意振型的Γ |
| 同上，印刷377/PDF399，Participating Mass Ratios | r_xr=f_xr²/M_x；M_x为X向总未约束质量 | 有效模态质量可由r_xr M_x恢复。分母不是未经核对的建筑全部重量/g或某一张局部楼层质量表 |
| Song等，MCEER-08-0005，2008；印刷38/PDF56，§3.3.2–3.3.3，式(3.58)–(3.59) | 弹性层剪力F_IS=T_S Kx；广义层剪力F_GS=T_S(Cẋ+Kx) | 阻尼力是否包含在输出中必须单独定义；该文此处对象为剪切楼模型，T_S不能不加说明直接用于一般三维有限元切口 |
| 同上，印刷40/PDF58，§3.3.7，式(3.63) | 不同响应量对应不同输出系数；一般阻尼表达含多种坐标项 | 支持输出系数随物理量改变，不支持把一般阻尼系统直接拆成互不耦合的实模态SDOF |

CSI手册：[官方PDF](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf)。本轮优先使用已存本地原文，未重新下载。

## 2. 与候选式的映射（本轮解释性推导）

对一致自由度、质量矩阵M和均匀X向影响向量l，令

μ_r=φ_rᵀMφ_r，L_r=φ_rᵀMl，Γ_r=L_r/μ_r，m_eff,r=L_r²/μ_r。

令a_s选择切口以上X向质量合力，则S_sr=a_sᵀMφ_r。只有当所用集中质量和质心振型完整表达这一投影时，才可写为Σ上部m_iφ_ir；同理S_r=L_r可写为Σ全部m_iφ_ir。L_r≠0时，

B_sr=Γ_r S_sr=m_eff,r S_sr/L_r。

这是定义消元，不是从CSI或Song逐字摘取的新定理。φ→cφ时，L、S_sr同乘c，μ乘c²，Γ除以c，B不变；有效质量和B具有质量量纲。原始振型及参与因子的数值/量纲受归一化与坐标单位影响，不宜一律写成无量纲。手册的单位模态质量规范不能证明“仅质心子集”的广义质量也为1。

若采用独立模态输入核s_r，需明确定义q_r=Γ_r s_r。只有满足全空间特征方程及完整、方向一致的切口恢复，弹性层剪力才可写为V_sr=B_sr ω_r²s_r。B作为质量投影的成立不要求古典阻尼；但将s_r由独立SDOF计算，另需相应模态解耦条件。一般非古典阻尼或FNA中的实际q_r不得默认由该SDOF给出。

对Ritz模态，Vᵀ(Kφ_r−ω_r²Mφ_r)=0是投影层面的条件；并不使全空间残差e_r=Kφ_r−ω_r²Mφ_r为零。若弹性切口算子可写为a_sᵀK，则精确输出含a_sᵀe_r q_r。因此应先保留质量投影/惯性系数称谓，弹性力恢复另核。这里的惯性系数也不等于已取得实际绝对加速度时程或全部阻尼力。

## 3. 两项官方输出说明及其空白

1. [Mode Shapes in ETABS](https://web.wiki.csiamerica.com/wiki/spaces/etabs/pages/1474693/Mode%20Shapes%20in%20ETABS)，2023-04-03：确认在Diaphragm Center Of Mass Displacements表中、选定Modal Load Case后可取得振型。该短文没有给出质心采用的质量源、自动主节点与质心等同关系，也没有证明表中质心子集涵盖全模型质量。
2. [ETABS2016 ModalParticipationFactors接口说明](https://docs.csiamerica.com/help-files/etabs-api-2016/html/eeed62fb-02ee-ccc7-294e-801669425bf0.htm)：确认LoadCase、StepType、StepNum、Period、UX/UY/UZ、ModalMass、ModalStiff等字段存在；页面只列类型，不提供这些量的详细单位定义。仅阅读文档，未调用ETABS API。不能据此把ModalMass字段自动解释为有效模态质量，或替代实际导出表头与工况身份核对。

本轮补充资料限以上两项，不扩大外围检索。已读资料未闭合实际Excel单位、CM质量覆盖或实际Modal工况类型；应由④的同源小表核查确定。

## 4. 作者可用段落与必要条件

“模态参与质量反映各阶振型在给定方向均匀基底激励下的受激程度。为将其转换为楼层系数，本文采用切口以上质量与带符号振型的加权和，并以全结构相同方向的质量投影作归一化。该系数不随振型的任意缩放和反号而改变。计算中要求质量、振型和参与质量来自同一模态工况，并检查质心自由度对质量投影的覆盖。对于满足全空间特征方程的振型，在完整切口恢复条件下，可进一步将该系数用于弹性层剪力重构；采用Ritz模态时，还需检验力恢复残差。”

不可省略：同模型/同状态/同模态；均匀X输入及方向一致；质量聚合与约束映射一致；切口范围明确；L_r远离零。L_r=0时本比值为0/0，不能由它反推局部输出系数；近零时对漏质量与舍入敏感。基底全切口应给B=m_eff；该检查是必要一致性检验，不单独证明中间各层恢复正确。

文献关系：与CSI参与因子定义为直接映射；与Song输出区分为related-not-equivalent。未作首创或全文献覆盖判断。建议①②重点核对Ritz残差、零参与及坐标/质量聚合；⑤仅在④确认条件后把候选方法写成实际工程结果。

## 5. 原文指纹（原件只读、不纳入本次发布）

- CSI本地：`W5-重燃双塔连体/research/maxwell-20261017/roles/verification/csi-analysis-reference-2016.pdf`，7,811,196 bytes；SHA-256 `7f6f6890afee2e1890d33f5d34d53d8e23f60850890bd230848642b50a6291ac`。
- Song本地：`W5-重燃双塔连体/research/maxwell-20261017/roles/novelty/evidence/MCEER-08-0005.pdf`，1,798,029 bytes；SHA-256 `941a58f7a8e88975405ccfdfeea412a42d9f982ca7ff3c6a055a93c8c25fda48`。
- Song书目：SONG J, CHU Y L, LIANG Z, LEE G C. Modal Analysis of Generally Damped Linear Structures Subjected to Seismic Excitations. Buffalo: University at Buffalo, State University of New York, 2008. Technical Report MCEER-08-0005.
