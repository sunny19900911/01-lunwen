# R011 Word制作预备交接

本轮只准备脚本，不创建正式DOCX、不运行marker、不改v009、不启动Word、不重复COM环境探测。当前documents技能、模板规则和根预检已读，正式workspace依赖已重新载入。

## 可用入口

- build_word.py：--input Markdown --report JSON 为只读/XML预检；--author另需--output及--marker-receipt，真正作者命令须在最终稿采用后、marker成功一次之后执行。build默认authoring_enabled=False，输入输出、报告与布局可配置，拒绝覆盖已有DOCX。
- math_omml.py：复用旧已测试严格子集转换器，补P'_+一类prime与上下标组合；源稿10个display全部转成独立native OMML XML，未生成DOCX。行内变量补prime及预组合点导数字符。
- render_review.py：先真实运行canonical render_docx.py并保存canonical-render.log；仅失败且显式--allow-word-fallback后，普通powershell.exe -NoProfile -Command独立隐藏Word导PDF，PDFium生成page-N.png。自建doc与app嵌套finally清理，不改策略、不终止全局Word。未运行本入口。

## 数量及版面

v009有10个display公式、13个编号数据表，另2个未编号判定表，共15个editable table块、3图。脚本按实际输入自动计数，不写死旧稿6表/11式。layout-plan.json含全部15块、各列宽及行数。

沿旧论文阅读稿Letter纵向基线：左右2.25cm、正文SimSun/TNR11pt、数学Cambria Math，黑色标题。图15.8cm宽、等比、与caption保持同页；表宽17cm，按列类别定宽，9.5pt、灰边、浅蓝header、可重复表头、行不拆分、不固定行高。公式按quad分为可编辑eqArr避免长行。实际间距、公式及全部页必须待DOCX生成后render逐页实看；XML成功不等于视觉通过。

## 后续顺序

先根集中采用终审意见并冻结最终MD；运行本轮marker成功恰一次并保存stdout receipt；用参数化builder生成一个新DOCX；canonical真实渲染失败时保留日志再准许COM fallback；逐页PNG实际查看、修正并重渲染最终字节；核内容、原生公式、表格、3图及输出SHA后交付。依赖不安装。

旧渲染器已只读检查，含策略绕过参数的旧入口未运行。适配时曾因扩充inline token正则的引号产生一次SyntaxError，已修为双引号raw正则，随后AST和XML预检均退出0。当前没有实际DOCX版面或PDF可声称已通过。
