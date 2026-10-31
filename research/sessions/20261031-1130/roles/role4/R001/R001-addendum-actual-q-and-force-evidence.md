# R001补充：实际q、Γ及已有模态力线索

已读plan-theory-addendum-v002.md。L_sr=r_sᵀMφ_r，Eigen弹性力为ω²Lq；B=ΓL只是单位基底输入归一的系数。实际非经典/FNA耦合、其他广义力或非零初始条件下，Γ=0仍可q≠0，不能据B=0删除实际模态内力。本次未恢复真实FNA q。

实际参与表UX/UY列标kN-m，ModalMass标kN-m-s²；CM平动原生mm已固定转m。因UX/UY字段量纲并非1/m，不未经软件字段定义确认直接称Γ，不由数值吻合拟合任何倍率。补充6行保留原生PF原值/单位，同时按条件质量投影定义Γ_cond=S/m_ref，核S=Γ_cond m_ref及μ_cond=Γ_cond²m_ref；这不是独立原生Γ检验。全300阶X/Y已用实际参与比例/ModalMass核对的600项结果仍有效，旧总质量相同不构成分层质量同源认证。

## 模态力已有小表与跳过行

1. **直接存在**：881KB同次模态导出的Base Reactions已有300行小CSV，Modal/LinModRitz/Mode，源行4—303。无需重提原件，已选mode2/10/13的X/Y六行，与固定负号的−ω²Σoldmφ/1000比较，结果见下表。它是基底模式反力，不是Story5/12模式切口力，也未改名为Γ归一单位响应。

|阶次|方向|同次导出模式反力 / kN|−ω²Σoldmφ / kN|差值 / kN|
|---|---|---:|---:|---:|
|2|X|0.927796618|0.927796619|-6.37815911e-10|
|2|Y|0.224869389|0.22486939|-8.7746424e-10|
|10|X|-6.50060839|-6.50109732|0.000488926664|
|10|Y|-0.331552543|-0.332172677|0.000620134054|
|13|X|-4.32080896|-4.31870933|-0.00209963414|
|13|Y|-0.153102387|-0.148982387|-0.00411999915|

2. 实际有控core-cache的Story Forces共有195552行，72组之和也是195552，Step Type全为Step By Step；Base Reactions为16296行、全Step By Step。元数据无Modal/Mode组，原目录没有Frame Forces表。此范围没有被Time筛选漏掉Mode行的计数证据，不能宣称原件存在模态层剪力。
3. 旧D +3提取脚本`extract_response_cache.py`第32—34行确实仅缓存Step By Step，Story Forces全462432行，其中缓存462408、跳过24；manifest将被跳过行Step Type记为None，**不是Mode**。CM全693648行中跳过36个None。baseline0的对应计数相同。尚无这些None行的Case/Step Number/源行明细，不能将它们称作模态力。
4. 如以后在既有原件中作最小定点核查，只需要Story Forces的Story、Output Case、Case Type、Step Type、Step Number、Location（A—F）及VX/VY（H—I），针对上述24个非Step By Step行；有可信索引后才取对应原行。当前未为定位而扫描大工作簿。模式切口力最少需同模型mode2/10/13×Story5/12×Bottom的Case/Mode/VX/VY/源行/单位；目前已有缓存未发现这些记录。

原来的R001冻结件保持原字节；本补充及6行表由delivery-manifest-v002.json另行绑定。
