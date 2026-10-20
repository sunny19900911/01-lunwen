# R009 Word构建准备交付

本项仅准备代码和解析检查，未创建DOCX、PDF或逐页PNG，未修改v008和旧脚本，未安装依赖。最终Word须等20:59:25后主控明确最终canonical路径及SHA，不能自动选择目录最大版本。

## 可用入口

R009-build_word.py要求显式--source、--sha256、--output，支持--check-source只解析且不创建Word；--report可保存检查报告。源SHA错误、未知LaTeX命令、公式外LaTeX、未转换程序数组、不规则表格、超过三主图、缺图、输出或报告已存在时均报错。显示公式数、表数及图数按指定源动态统计。

例（检查最终冻结稿时替换占位值）：
python R009-build_word.py --source ABSOLUTE_CANONICAL_PATH --sha256 FROZEN_SHA256 --output ABSOLUTE_NEW_DOCX_PATH --check-source --report ABSOLUTE_NEW_REPORT_PATH

正式构建去掉--check-source。正式创建命令前，按documents技能运行一次mark_artifact_operation_started.mjs；本项没有运行标记，因为没有创建/编辑Word。本项仅确认该标记脚本的存在。

## 数学与版式

沿用旧builder的可编辑OMML路径，扩展Φ、ℓ、sin/cos/diag/sgn、cases及矩阵环境，未知命令直接失败。M、K等现稿固定字面量在排版层转为行内OMML，原数值不变；K为3×3原生数学矩阵，H2分段包络为带左花括号的两行矩阵。H2显示输入按两个因子分两行，避免过宽。表格宽度按现稿列结构设定，行可分页且表头重复；图只保留正文图注，不重复alt标签。末尾内部补充说明链接排除于Word正文，源稿保留。

R009-render_word_native.ps1复用原生隐藏Word COM流程，只关闭它打开的文档及新建实例，不保存输入DOCX。R009-render_preview.py接受--pdf、--out-dir、--scale，逐页生成PNG和实际查看标志初始为false的报告，不会自行声称视觉QA通过。Poppler也已定位可用，具体路径见validation。

## 已验证与待验证

v008 SHA核对；--check-source退出0；错误SHA退出1且拒绝；Python语法检查通过；包docx/PIL/reportlab/pypdf/pypdfium2/lxml可发现；8表3图4引用，3组显示数学和8组行内数学解析通过。没有最终Word的序列化、Word渲染和视觉QA证据，不能据此认定版面通过。仍需正式构建后先运行documents/render_docx.py并按真实日志诊断；按Windows交付合同需要时用已备原生Word路径。最终每页PNG必须实际查看，并核对OMML、矩阵、公式、表格、图注及分页。

科学/语言/引文意见留待下一项，特别是H2为考察较高阶影响的合成输入条件句；本项不改v008，真实未解决项均保留到终稿。
