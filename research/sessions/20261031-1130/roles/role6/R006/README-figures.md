# R006：论文图件

两图均由冻结processed小表制作，无新ODE、拟合或原表提取。SVG为可编辑矢量，PNG为2400×1728、300dpi，中文采用已安装Microsoft YaHei。两张PNG已实际view_image逐张检查，标题、图例、刻度及图注无截断或重叠；数字与源小CSV核对通过。独立数字/图义复核状态仍由主控裁决。

## 图1：隔板质心UX分量

- figure1-actual-CM-UX-modes2-10-13.svg / .png
- figure1-CM-UX-normalized-source-54.csv：3阶×18个CM，含原生UX、m值、各阶归一分母、归一值、同源周期及原表源行。
- 图注建议：实际有控LinModRitz第2、10、13阶的隔板质心X向模态位移分量。每阶在18个现有CM点内按最大绝对UX作图示归一，不能用于跨阶真实振幅比较。D1绘1—12层，D2仅绘源表3—8层；点间连线辅助阅读，不代表全节点变形或整层刚性。

## 图2：SHW3X的独立峰幅权重

- figure2-SHW3X-Story5-Story12-envelope-weights.svg / .png
- figure2-SHW3X-weights-source-10.csv：两层×5类别，保留独立峰和、全300阶U及权重。
- 图注建议：SHW3X、ζ=5%时，第5层与第12层的模态独立峰幅权重。固定展示2、10、13、18阶，“其他”为余下296阶；每层五类权重和为100%。各阶峰值可能发生在不同时刻，权重不是同刻剪力份额或能量比例。结果对应固定物理来源的弹性惯性线性参照，不自动等同原生FNA的唯一逐阶内力。

## 复现与记录

make_figures.py仅读冻结CM processed CSV、actual_controlled周期表和④R005的SHW3X/5%单阶包络CSV。render_figures.cjs复用现有Node sharp/libvips，不安装依赖；输出默认拒绝覆盖，复现请在新的隔离角色目录处理输出。首次Python括号错误与缺失SVG的渲染失败保留在initial-generation-failure.json，修正后两图成功。

源SHA、数值复核、渲染信息和实际目视检查分别见numeric-verification.json、render-record.json、visual-QA.json与delivery-manifest.json。未输出原始5400行CM全表、300阶全时程或字体文件。
