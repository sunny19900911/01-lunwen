# R013 Word 交付

完成并冻结于 2026-11-02T01:32:26+08:00。正文采用冻结 v010，S1 采用 R012，二者 SHA256 复核一致且未修改。

最终 Word：`E:\11-工作\001-workbuddy spaceV1\001-workbuddy space\109-论文写作\01-lunwen\papers\damping-output-boundaries\manuscript\damping-prediction-session021-论文审阅稿-v010.docx`

- 共 16 页，最终 render-v2 全部页 PNG 已按原分辨率实际查看。
- 15 张可编辑表格（13 张编号表、2 张决策表）、10 个编号独立公式，合计 118 个原生 OMML 公式对象、3 张图。
- 4 个外部实际超链接及真实可用的本地 S1 超链接；作者为空。
- 正文中文序列与来源一致（8701 字）；15 张表的逐单元格内容一致。
- 仅修复表格分页、数值换行、两处行内最大值表达式的 Word 原生数学排版。
- 标记仅成功运行一次。canonical renderer 实际失败日志已保留，原因是缺少 soffice.exe；随后仅用自有隐藏 Word COM 实例导出 PDF，再由 PDFium 栅格化。未使用 ExecutionPolicy 参数，未终止其他 Word 进程。
- DOCX SHA256：`b266932700e1c518215732026526c06275e5632aeebf54a8960ff548b36d8eb9`。源稿和 S1、链接清单、最终页哈希与视觉记录详见 manifest.json、QA.json、visual-QA.json。

可交 root 再看最终页图；本轮未修改科学内容，未开展额外计算或文献检索。
