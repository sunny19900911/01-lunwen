# R014 Word 数学转换修复交付

完成并冻结于 2026-11-02T01:43:12+08:00，仅修 Word 呈现。v010 MD、R012 S1 与旧 DOCX 均保持原 SHA。

- 最终文件 `E:\11-工作\001-workbuddy spaceV1\001-workbuddy space\109-论文写作\01-lunwen\papers\damping-output-boundaries\manuscript\damping-prediction-session021-论文审阅稿-v010-r2.docx`，591348 B，SHA256 `9d1a1963cb27d0d49f19295a3411e7fa87530e44afb19141a6bcddd324b37530`。
- 16 页最终 PNG 均已按原分辨率实际查看。第 6 页 U 与 P 两式分别保留独立的 p_r、v_r(t) 操作数；第 9 页 e_P 中预测 P 的帽号为原生 m:acc 且视觉清楚。
- builder 显式映射全部行内求和与最大值相关源片段，避免无括号下标的贪婪匹配；帽号均使用原生重音结构。20 个显式公式片段 XML 保存于 local-cache。
- 15 张可编辑表格内容逐格一致，302 个小数按序一致；8701 个中文字符序列一致，英文摘要一致。10 个独立公式 XML 与原 Word 完全一致；共 112 个 OMML 对象，3 图字节一致，4 外部 URL 与本地 S1 链接存在，作者为空。
- marker 未重跑。canonical renderer 实际缺 soffice.exe 的失败日志保留；仅自有隐藏 Word 实例导出 PDF，PDFium 出页。
- 完整内容合同、关键数学 XML、逐页 hash 和视觉说明见 QA.json、visual-QA.json、manifest.json。旧 DOCX 保留为本轮比较依据，不作为此次最终交付。

可交根复核最终第 6、9 页及完整 16 页。未改科学稿，未重算数据。
