# 叙述稿的复现与证据边界附录

本附录服务于[叙述正文](../../../../../manuscript/maxwell-paper-narrative-v001.md)，将机器条件与研究编号移出正文，不扩大任何科学结论。正文候选待独立整合审，最终选题仍由用户决定。

## 解析来源与符号

正文式（1）—（7）来自[固定耗散峰集合附录](../../../../../manuscript/maxwell-fixed-dissipation-peak-appendix-v001.md)及其已接纳证明链C038；原固定峰正问题为M-C018。正文仅将耗散功率P改写为𝒫、驻留时长ℓ改写为θ，并将1/α显写，避免和结构峰P_X及Hölder指数q混用；不增加新推导。末δ自由、可测有界v、F0=0与FT=σh≠0、真实D与W分账均在正文保留。原附录历史“待审”标签不回写，当前状态取正式采用记录。

正文式（8）—（10）来自已接纳C029/C039的完整力接口与经典Hölder条件界。MIT18.156讲义第2页§1.2 Theorem3及第3页r=∞证明为工具出处；[R028一手来源记录](../../../literature/maxwell-session004/R028-convolution-holder-source/report.md)和[source manifest](../../../literature/maxwell-session004/R028-convolution-holder-source/source-manifest-R028.json)登记实际原页读取。本文作者只读冻结小报告与manifest，没有新开原PDF或外搜。MIT讲义不是Maxwell专门定理；当前公式系数/单位与范围沿已审R030/R042及正式采用链，不由文献题名代替数学验证。

## 双质量例的精确对象与数值合同

图1复用既有PNG/SVG和[完整图注](../C025-layout-explanation-figure-v001/caption.md)，不读数组、不重绘。精确参数与公共截断输入由[冻结协议](../../../../../../../research/sessions/20261017-2109/layout-nonlinear03-protocol-v001.json)固定。协议的candidate文字属于历史阶段；当前C025条件准入以[根采用说明](../../../../../../../research/sessions/20261017-2109/R011-certificate-adoption.md)和其[JSON](../../../../../../../research/sessions/20261017-2109/R011-nonlinear-certificate-adoption.json)为准。

该近似轨迹是隐式中点最终存储端点在真网格上的连续分段直线；完整r_u/r_v/r_F误差预算覆盖运动学、动量和本构，连续PL间隙与真实停载被动尾相连。A在6T后的真实尾上界为1.098，6T不是人为宣布真实峰已结束。B只需固定T真幅值下界；T不是B已定位真峰。差>7.485沿更紧的原有向端点，不用8.809−1.325显示数推导。

数值条件完整保留：IEEE binary64有限基本运算、round-to-nearest、渐进下溢、无FTZ/DAZ、正确nextafter、精确Fraction语义、已记录Python/NumPy float64解码及稳定运行模式；参数/pi/sin/非线性幂与导数/端点重构/残差积分/总和/末能/比较方向均须有向包络。有限探针、复跑一致或独立小结果不能证明历史全程机器模式，也不是所有硬件上的形式认证。

原端点NPZ与原文PDF/抽取页图未在本文新包共享，复现需获准本地缓存，或按已记录环境重建并核对身份；不能假定外部读者已持有完整数组。图生成/渲染脚本及字体环境仍见原图包；本文未运行它们。图示并非实际ETABS建筑、真实477/500000属性、真实几何或普通两层剪切链；两位置全局最大相同，不能推出整体布局优胜。

## 工程资料与主张来源

工程表逐字保留已审compact-v004的审计表，不重提取原始工作簿。唯一训练与191个条件检查属于共同192组合；193个完整组合和共同192组合不混同。背景5%参考、原生能量定义、单位/几何/端口/实际C缺口、微小负增量与非零末能均保留；没有工程成对预测或设计增益结果。

[正式R022采用](../../../../../../../research/sessions/20261017-2109/R022-adoption.json)接纳compact-v004及其数学/来源整合审；C038/C039源的当前接纳沿[正式R021](../../../../../../../research/sessions/20261017-2109/R021-adoption.json)及[provenance纠正附记](../../../../../../../research/sessions/20261017-2109/R021-provenance-addendum.json)。早期illustration采用的旧QA散列失配保留为历史，不冒称旧QA字节已恢复。

逐项主张、正文位置与输入SHA见本目录evidence-map.json和input-freeze.json；新正文作者静态核对见validation.json，不替代独立整合审。正文不纳入未获本任务准入的新支线，不将条件证书、许可类或工具应用称为首次、建筑sharp可达或工程验证成功。
