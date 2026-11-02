# 官方模板执行契约 预备版

参考 `E:\11-工作\001-workbuddy spaceV1\001-workbuddy space\109-论文写作\01-lunwen\research\sessions\20261102-1917\roles\role3\R001\local-cache\建筑结构-正刊排版模板-2024.4.28.doc`，SHA `c21de684ade77cf7b7c062c05b81cd0327254db9d0426e4368186eb00b60bb18`。只读提取及PDF导出完成，未转换为DOCX，未改原件。模板共4页；节/段落排版证据见local-cache/template-audit.json及template-role-evidence.json。模板PNG尚未实际查看，模板蒸馏门尚未通过。

主文预计9—12页，仅按内容量估计。A4上2.7cm、其余2cm，页眉脚1.5cm，47行网格；题摘单栏，正文双栏；表图通过连续分节转通栏并恢复双栏。最终以实际模板sections参数与页图为准；不得重新采用旧Letter通用样式。正文预计五号宋体、英数TNR，题22pt、作者12pt仿宋，实际各角色字号见模板提取记录，不编造作者或基金、DOI。

源v002仅作数学预备；之后绑定主控采用v003的真实SHA。5个display与K/M矩阵、QD求和、argmin/max和分母已做原生OMML XML预检，详见freeze.json。最终须逐式查操作数，不以XML可解析或对象数量替代正确性。全部行内数学采用明确映射，不能复用旧贪婪下标正则。

可编辑正文与表格；表2六列8条记录（另有表头），其余表按源；3图和图注配对。模板真实表格/图/节模式须先看模板全部页。正文作者身份槽留空；删除模板示例作者/基金/假DOI，不将示例残留到正文。

已备math_omml.py和render_review.py，后者先实际调用canonical renderer，失败留日志后才--allow-word-fallback；fallback AutomationSecurity=3、hidden、ReadOnly、仅关闭自建对象，无ExecutionPolicy参数和kill。模板检查失败尝试不改变原件。尚未编完模板派生正文builder，不把预备当authoring或QA。

真实制作获派后：首次authoring前marker成功一次；只在本轮cache内转换/复制模板；构建后检查正文/表格/所有小数/5display/行内数学/3图hash/附录实际链接/作者空，再render、每页原分辨率view；修后重新渲染最终字节。
关键未决：官方模板实读三个节均为45行（LinesPage=45），与网页47行说明不同；上文47行仅网页规则，不能称模板实值。双栏栏距36pt、栏宽222.95pt；模板页面4页尚未实际view。下一制作任务先以模板实值为设计参照，向根报此差异后决定，不暗改模板。
