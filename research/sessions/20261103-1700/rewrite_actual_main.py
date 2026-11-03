"""Reorganize reviewed P06 around the actual-damper scheme; preserve source files."""
from pathlib import Path
import csv, hashlib, json, re, datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
src=R/'papers/damping-output-boundaries/manuscript/p06-actual-damper-session025-v004.md'
old=src.read_text(encoding='utf-8')
assert hashlib.sha256(src.read_bytes()).hexdigest()=='b66b072aeca3019146e41664ce71ae81475d198410bf505e53afaf054d76ffe3'
out=src.with_name('p06-actual-main-session026-v001.md');assert not out.exists()
def load(n):
    with (S/'roles/response'/n).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
rows=load('actual-versus-baseline-time-peak-72.csv');ranges=load('actual-layer-direction-ranges-24.csv');screen=load('actual-bottom-mean-screening-6.csv')
assert len(rows)==72 and len(ranges)==24 and len(screen)==6
summary=json.loads((S/'roles/response/actual-response-summary.json').read_text(encoding='utf-8'))
assert summary['all_72_saved_time_axes_exact'] and summary['B_D_native_peaks_match_1458_reviewed72']
def table_block(caption):
    tail=old.split(caption,1)[1].lstrip();lines=[]
    for ln in tail.splitlines():
        if ln.startswith('|'):lines.append(ln)
        elif lines:break
    assert lines;return '\n'.join(lines)
geom=table_block('**表5 实际装置分层配置（按上端J所在层归类）**')
controls=table_block('**表6 实体方案代表层的两类控制输入及各自成对峰值**')
timing=table_block('**表7 第8层六工况控制剪力时刻的实际装置合力**')
modal=table_block('**表4 第5层软件峰值与8%阻尼固定300阶线性参照的有符号项**')
case_table=['|工况|最小减幅层|该层减幅/%|底层减幅/%|12层减幅平均/%|底层与该层差/百分点|',
            '|---|---|---:|---:|---:|---:|']
for r in screen:
    story=r['least_reduction_Story'].replace('Story','第')+'层'
    case_table.append('|'+r['Case']+'|'+story+'|'+ '|'.join(f"{float(r[k]):.4f}" for k in ['least_reduction_percent','bottom_reduction_percent','mean_12_story_reduction_percent','bottom_minus_least_pp'])+'|')
pick=[('RH4Y','Story12'),('SHW7Y','Story6'),('SHW4X','Story1')]
bias_table=['|工况/楼层|基准峰/kN|实际方案峰/kN|原峰时评价/%|自身峰减幅/%|高估量/百分点|峰时（基准→实际）/s|',
            '|---|---:|---:|---:|---:|---:|---|']
for case,story in pick:
    r=next(x for x in rows if x['Case']==case and x['Story']==story)
    vals=[case+'/'+story.replace('Story','第')+'层']+[f"{float(r[k]):.4f}" for k in ['P_B_kN','P_D_kN','r_at_percent','r_peak_percent','d_pp']]+[f"{float(r['t_B_s']):.2f}→{float(r['t_D_s']):.2f}"]
    bias_table.append('|'+ '|'.join(vals)+'|')
text=r'''# 附加阻尼作用下双塔连体结构楼层剪力的分层评价

**Story-by-story assessment of shear changes under added damping in a coupled twin-tower structure**

## 摘要

设置阻尼器后，楼层剪力减幅较小的地震输入未必产生最大的剪力需求，底层或全楼平均减幅也可能掩盖局部改善不足。以一座布设88只非线性黏滞阻尼器的双塔连体结构为例，对基准与实际阻尼器方案在六个方向工况下的72条楼层剪力记录进行配对分析，分别保留最小减幅和最大需求的控制输入，并检查各模型自身峰时及该时刻装置出力。结果表明，24个楼层—方向组中有12组的两类控制输入不同；六工况中仅两个工况的底层恰为减幅最小层。SHW7Y下底层减幅为30.2486%，第6层仅为16.0082%。若只在基准峰时读取实际方案响应，减幅高估量的中位数为3.6586个百分点，RH4Y第12层达到34.6790个百分点。第8层X向需分别检查RH4X的7.7713%减幅与SHW7X的7132.2925kN需求，两条记录在楼层剪力峰时的装置水平合力绝对值分别为装置自身峰的58.6736%和63.4488%。增加3个百分点模态阻尼的14工况结果用于扩展对照，固定线性参照用于说明主导模态项与反向抵消的不同作用。提出由成对峰值、两类控制输入、各自峰时及同刻装置出力组成的复核流程，为实际消能方案的逐层检查与比选提供依据。

**关键词**：楼层剪力；黏滞阻尼器；分层评价；控制输入；时程分析

## Abstract

After dampers are installed, the input producing the smallest story-shear reduction may differ from that producing the largest demand. Base-story and building-average reductions can also conceal smaller improvements at individual stories. A coupled twin-tower structure with 88 nonlinear viscous dampers is examined using 72 paired story-shear records from a baseline model and the actual-damper scheme under six directional cases. The two governing inputs, each model's own peak time, and simultaneous damper forces are retained. Different inputs govern the smallest reduction and largest demand in 12 of the 24 story-direction groups. The base story has the smallest reduction in only two of the six cases. Under SHW7Y, the base-story reduction is 30.2486%, whereas Story 6 achieves only 16.0082%. Reading the actual-scheme response only at the baseline peak time overstates reduction by a median of 3.6586 percentage points and by 34.6790 percentage points at Story 12 under RH4Y. At Story 8 in the X direction, RH4X controls the reduction of 7.7713%, while SHW7X governs the demand of 7132.2925 kN. The simultaneous damper horizontal-force magnitudes are 58.6736% and 63.4488% of their respective peaks. Fourteen directional cases with three additional percentage points of modal damping provide an extended comparison, and a fixed linear reference illustrates changes in dominant modal terms and cancellation. A practical checking procedure combines paired peaks, both governing inputs, individual peak times and simultaneous damper forces to assess actual damping schemes story by story.

**Keywords**: story shear; viscous damper; story-by-story assessment; governing input; response-history analysis

## 1 引言

阻尼器方案的工程复核既要判断剪力降低了多少，也要确定哪一条输入产生较大需求。减幅是相对基准的变化比例，绝对剪力则对应受力需求；一条记录改善较小，不代表它产生的剪力最大。底层剪力或各层减幅平均值可以概括方案，却不能替代每层检查。此外，实际装置出力和楼层剪力往往不在同一时刻达到峰值，仅看装置最大轴力或基准峰附近的响应，可能遗漏方案自身的控制时段。

已有研究从不同目标与沿高度配置评价阻尼设置。柳博哲、汪梦甫比较了阻尼参数对框架—核心筒结构基底剪力和变形的影响[1]。Liu等依据指定响应的重要模态调整钢框架阻尼器配置，指出较大的有效阻尼未必使不同目标同时获得最佳控制效果[2]。De Domenico和Hajirasouliha采用沿高度性能反馈调整非线性黏滞阻尼器，并用地震记录检验结构响应[3]。张敏、李阳研究阻尼器布置与各层变形响应[4]；陈泰锟等比较沿高度设置非对称阻尼器的响应并开展混合模拟验证[5]。这些工作表明，方案评价需要把具体目标响应与楼层位置联系起来。

Cetin等分别评价多输入下的位移、绝对加速度及层间位移角[6]。对于楼层剪力，还需区分最小减幅与最大需求各自由哪条输入控制。Song等区分弹性层剪力和含阻尼作用的广义层剪力输出[7]，说明比较应先固定受力定义。Londoño等与Conde、Bernabeu分别讨论支撑柔度及Maxwell整体刚度对装置传力和结构响应的影响[8,9]。实际非线性装置通过端部运动及整体柔度产生作用，不能由统一增加模态阻尼完全代替。

本文以实际布设88只黏滞阻尼器的双塔连体结构为主体，利用共有六方向工况的基准与实际方案输出，建立逐层成对峰值、两类控制输入、各自峰时和同刻装置出力的工程检查表。增加3个百分点模态阻尼的14工况结果作为扩展对照；固定300阶线性参照和三层模型仅用于解释主导模态项下降、反向抵消变化与局部剪力的关系。研究重点是把常规时程输出转为需要重点复核的楼层、输入和时段。

## 2 实际阻尼器方案与比较资料

### 2.1 工程模型和共有输入

采用双塔连体结构的ETABS分析结果，基准模型记为B，按工程真实位置设置黏滞阻尼器的方案记为D。主体比较覆盖RH4、SHW4、SHW7三组输入各X/Y方向，共六个方向工况；每工况有12层，形成72条主方向楼层记录。X/Y是对应输入的转向计算，不计为六次独立地震事件。另有增加3个百分点模态阻尼的参考模型M，覆盖14个方向工况、168条记录，用于第5节扩展比较。

基准与实际方案共有六工况的基底加速度，在16296个保存时刻、六分量共97776个数值上逐点一致。实际模型18个质心的X/Y方向质量与基准对应数值吻合。以下评价所提供实际方案相对基准的软件响应变化；背景阻尼、完整内部积分及初始设置的导出范围见[计算资料与完整工程表](../../../research/sessions/20261103-1700/工程资料与完整附表.md)。

楼层剪力统一取Story Forces表的Bottom输出，第1—12层对应Story1—12。各模型在各自完整保存时程中求剪力绝对峰；同条成对记录的保存时间逐点一致，名义间隔为0.02s，输入PGA为350mm/s²。保存间隔与内部积分步分别记录。本文直接比较该软件截面输出，装置力另用于同刻检查，不从楼层剪力中扣出主体剪力。

**表1 资料范围与用途**

|资料|范围|用途|
|---|---|---|
|基准与实际方案楼层剪力|六方向工况×12层，72条成对记录|工程主分析：逐层减幅、两类控制输入、峰时与原峰时评价偏差|
|实际布置|3416节点坐标、88只Link两端位置|安装层、方向、倾角及轴力水平投影|
|原生装置轴力与变形|第8—11层32只×六工况|完整范围内的同刻装置水平合力|
|基准与模态增阻尼参考剪力|14方向工况×12层，168条成对记录|扩展输入对照与线性机制说明|

### 2.2 实际布置与装置参数

88只装置按真实I/J端点坐标绘于图1。第1—11层每层8只，水平投影沿X、Y的装置各4只，全楼各44只；第12层没有该连接表所列跨层装置。装置轴线长度为6.440～9.401m，与水平面的夹角为29.20°～48.37°，各层配置见表2。图中灰色区段为具有完整原生轴力时程的第8—11层。

![图1 实际88只阻尼器布置](../../../research/sessions/20261103-1458/roles/geometry/actual-damper-layout.png)

图1 实际88只阻尼器轴线的X-Y、X-Z和Y-Z投影，坐标单位为m。不同装置在投影中可重合，未绘主体梁柱；灰色区段标出第8—11层完整装置力资料的范围。

实体方案采用工程提供的有限Maxwell参数κ=500000kN/m、c=477kN(s/m)^0.3、α=0.3。装置总变形由串联弹性变形和黏滞单元变形组成，出力取决于端部运动、本构与整体柔度[8,9]。比较方案峰值无需先把这些作用换算为统一附加模态阻尼比。

**表2 实际装置分层配置（按上端J所在层归类）**

@GEOMETRY@

### 2.3 模态分析的解释范围

工程模型前三阶周期在所示精度下约为2.7781、2.7322和2.5669s，主要方向参与分别对应UY、UX与RZ；方向质量参与率不是目标层剪力分担。非线性模态时程仍可用选定振型或Ritz向量表示结构运动，但装置非线性力进入广义受力，各阶响应需考虑其相互影响[10]。

因此，背景模态阻尼与装置作用分开描述。本文主要结论直接由实际方案的原生剪力和装置力得到，不依赖等效阻尼转换；第5节用固定经典阻尼线性参照解释叠加作用，不将其中的模态项写成实际非线性方案的逐阶实测分担。

## 3 逐层成对峰值与控制记录

### 3.1 逐输入保留各模型自身峰

对楼层s、方向a和同一输入c，在共同保存时间集T内分别求基准与实际方案的剪力绝对峰：

$$P_{B,s,a,c}=\max_{t\in T}|V_{B,s,a,c}(t)|,\qquad P_{D,s,a,c}=\max_{t\in T}|V_{D,s,a,c}(t)|.$$

实际方案相对基准的减幅定义为：

$$r_{D,s,a,c}=1-\frac{P_{D,s,a,c}}{P_{B,s,a,c}},\qquad P_{B,s,a,c}>0.$$

两模型各自峰时记为t_B和t_D。每条记录同时保留工况、两峰、减幅、峰时和所在层；按每层每方向三个输入统计减幅最小值、中位值与最大值。全楼各层减幅的算术平均仅作对照，不代表总剪力减幅。

### 3.2 分别确定改善与需求的控制输入

对固定楼层和方向，在相同输入集合C内分别取最小减幅输入c_r与最大实际方案剪力输入c_V：

$$c_r\in\operatorname{argmin}_{c\in C}r_{D,s,a,c},\qquad c_V\in\operatorname{argmax}_{c\in C}P_{D,s,a,c}.$$

c_r用于查看改善较小的记录，c_V用于查看较大绝对需求。两条记录各自列P_B、P_D、r_D与峰时，不将一个输入的百分比标在另一个输入的需求上。并列控制可保留全部输入，或按事先确定的顺序列示；本例按工况名稳定排序。零基准峰的归一减幅不定义。

在缺少承载力和组合资料时，减幅小不等于受力危险，需求大也不单独决定方案优劣。两类记录用于指定需要打开的时程，再结合相应构件、变形与装置需求复核。

### 3.3 检查原峰时读数是否遗漏方案自身峰

记A_D=|V_D(t_B)|，仅在基准峰时读取实际方案响应所得减幅记为r_at,D，其相对自身峰减幅的高估量为d_D：

$$r_{\mathrm{at},D}=1-\frac{A_D}{P_B},\qquad d_D=\frac{P_D-A_D}{P_B}\ge0,\qquad r_D=r_{\mathrm{at},D}-d_D.$$

P_D是同一保存时间集内的绝对最大值，因此d_D非负，乘100后单位为百分点。d_D反映评价时刻不同造成的读数差别，不是相位或某阶振型的贡献。本文对并列绝对峰取最早保存时刻，并保留并列数量。应先逐条计算，再汇总各层和输入，不能把不同记录的百分比和偏差相减。

## 4 实际阻尼器方案的分层结果

### 4.1 底层与平均减幅不能代替逐层检查

实际方案的72条主方向记录相对基准均下降，减幅为3.1238%～47.6719%，但分布随楼层和输入变化。图2按每层每方向三个输入给出最小、中位与最大减幅；表3另按每个工况列出改善最小层，并与该工况底层及十二层平均值比较。

![图2 实际方案各层减幅范围](../../../research/sessions/20261103-1700/roles/response/actual-device-story-reduction-range.png)

图2 实际阻尼器方案相对基准的逐层剪力峰减幅范围。X、Y分别统计RH4、SHW4、SHW7三个输入，横线为最小至最大值，圆点为中位数。

**表3 各实际工况的改善最小层及总体指标对照**

@CASE_TABLE@

六工况中只有SHW4X、SHW4Y的底层恰为改善最小层。SHW7Y底层减幅为30.2486%，而第6层仅16.0082%，前者高14.2404个百分点；十二层平均减幅27.1508%，仍高11.1426个百分点。若仅看底层或平均值，就会掩盖第6层的较小改善。SHW4X则从另一侧说明平均值的局限：底层仅下降3.1238%，十二层平均为15.6557%，相差12.5319个百分点。

这两类情况都要求逐层保留成对记录。图2用于定位改善较小的层，表3用于说明某一输入下底层和平均值能否代表该层；它们均不能代替后续的绝对需求检查。

### 4.2 改善较小与需求较大由不同输入控制

在24个楼层—方向组中，有12组的最小减幅和最大实际方案需求由不同输入控制。表4列出第5、8层代表记录，完整24组见附表。每一行的两峰和减幅均来自同一输入。

**表4 实际方案代表层的两类控制输入**

@CONTROLS@

第8层X向的较小减幅由RH4X控制，为7.7713%，实际方案剪力峰5776.6513kN；较大需求由SHW7X控制，为7132.2925kN，该输入自身减幅为15.3907%。Y向也需分别检查SHW4Y的9.3098%与SHW7Y的6707.7015kN，后者自身减幅为20.7852%。因此，若只沿用最小减幅对应的输入，可能遗漏同层更大的剪力需求。

第5层X向的最小减幅为RH4X的9.6048%，最大需求来自SHW4X的9198.67kN；两输入减幅仅相差0.0181个百分点，宜同时保留，不把近似并列的排序夸大为机制差异。控制记录应按实际方案重新确定，而不能沿用模态增阻尼参考模型的记录。

### 4.3 控制时刻的实际装置出力

第8层8只装置均由下层I端连至上层J端，各主方向有4只装置的水平投影非零。取单位向量n由I指向J，轴力P按原生正拉力约定，QD=Σn_eP表示J端结构内力抵抗项，装置施加于J节点的外力为−QD。同一轴力的I/J重复列示只计一次。第8—11层共24个楼层—工况组，每组8只装置的保存时间与楼层输出逐点一致。

**表5 第8层剪力峰时的实际装置水平合力**

@TIMING@

图3比较第8层X向两条控制记录的完整保存时程。RH4X层剪峰为+5776.65kN，发生在21.60s；同刻QD为−238.11kN，而QD自身绝对峰405.83kN发生在11.50s。SHW7X层剪峰为−7132.29kN，发生在38.06s；同刻QD为+277.36kN，QD自身绝对峰437.15kN发生在32.04s。布置和参数相同，输入改变后，控制时段和同刻出力均不同。

![图3 第8层两条控制记录的实际出力](../../../research/sessions/20261103-1458/roles/response/R002/Story8-RH4X-SHW7X-native-QT-QD-v003.png)

图3 第8层RH4X、SHW7X下的楼层剪力QT和装置水平合力QD。上下行纵轴分别为±8000kN和±500kN，虚线标出各自绝对峰时。QD为J端结构内力抵抗项，装置对节点外力为−QD；两曲线分别检查，不据其直接扣出主体剪力。

两输入层剪峰时的QD绝对值分别为自身峰的58.6736%和63.4488%。这两个比例描述装置出力时序，不是减震贡献率。工程复核应同时查看目标层剪力峰时的有符号出力与装置自身峰：前者对应控制时刻的传力，后者用于装置和连接需求检查。

### 4.4 实际方案自身峰的遗漏与读数偏差

实际方案72条记录的原峰时评价高估量d_D中位数为3.6586个百分点，95%分位数为19.7051个百分点，最大为34.6790个百分点。分位数按排序位置(n−1)p线性插值。三条记录的两模型保存峰时相同，其d_D为零；其余记录均应返回实际方案自身峰附近查看。

**表6 实际方案原峰时评价与自身峰减幅的对照**

@BIAS_TABLE@

RH4Y第12层的基准峰为565.0421kN，发生在20.22s；该时刻实际方案剪力为−327.6119kN，若只读此处可得到42.0199%的减幅。但实际方案完整时程绝对峰为523.5629kN，发生在12.26s，实际峰值减幅仅7.3409%，两种读数相差34.6790个百分点。这个例子应同时保留12.26s与20.22s附近的曲线，不能用基准控制时段的较小响应替代方案整体峰值。

![图4 实际方案原峰时评价偏差](../../../research/sessions/20261103-1700/roles/response/actual-device-old-peak-vs-complete-peak.png)

图4 实际方案72条成对记录的原峰时评价减幅与自身峰减幅。虚线为两者相等，点相对虚线的竖向差为d_D，单位为百分点；标注RH4Y第12层的最大差例。

该偏差与控制峰选择直接相关，不要求先确定等效模态阻尼比。峰时改变还可能包含波包或正负控制峰切换，故不把时间差单独解释为纯相位改变。

## 5 模态增阻尼对照与叠加机制

### 5.1 较大输入范围的扩展对照

基准B与均增加3个百分点模态阻尼的参考M共有14方向工况、168条记录，其峰减幅为6.8513%～30.5458%。按同样流程，24组中有19组的最小减幅和最大参考需求来自不同输入；X向第5层分别由SHW3X的6.8513%和SHW4X的9027.7451kN控制。该扩展输入分析说明两类控制记录也需要分别保留，完整结果见[原14工况附表](../../../research/sessions/20261102-1917/roles/role5/R002/engineering-data-and-full-tables.md)。

若把输入集合限制为与实际方案相同的六方向工况，模态增阻尼参考中两类控制输入不同的为7/24组，实际方案为12/24组。72条实际峰相对参考峰有34条较高、38条较低；第12层X/Y的最大需求控制输入由参考的SHW7X/SHW7Y转为实际方案的RH4X/RH4Y。工程上不能用统一增加3个百分点的结果代替真实布置方案，也不能把两个不同输入集合的19组和12组直接作为阻尼方式优劣指标。

### 5.2 主导模态项与反向抵消的机制解释

对参数和输出关系明确的线性参照，目标层弹性剪力可写为各模态项的同刻合成[7]：

$$V_s(t)=\sum_r(\ell_s^T\phi_r)q_r(t).$$

ℓ_s表示目标层的刚度与内力输出映射，φ_r和q_r分别为振型及相应坐标。改变阻尼后，各阶响应幅值和波形发生变化；同向项下降可能降低合成峰，原有反向项若向零变化则会削弱抵消。两种作用可以同时存在，应在相同输入与相同时刻比较。

采用18个质心方向质量与同源模态资料建立的固定300阶经典阻尼线性参照，辅助比较SHW3X和SHW4X下第5层。表7列8%阻尼参照在各自软件峰时的组成，参照合成与软件绝对峰的相对差分别为0.00245%和0.00806%；项的符号按参照方向保留。该线性参照用于说明机制，实际非线性方案的逐阶项仍需由其自身响应及对应内力恢复关系确定。计算条件见[辅助分析资料](../../../research/sessions/20261103-0845/roles/writing/SHW3X-SHW4X-辅助分析资料-v002.md)。

**表7 第5层软件峰与固定300阶线性参照项**

@MODAL@

SHW4X较高需求主要对应更大的第2阶项：7753.76kN，高于SHW3X的6762.84kN；第10阶项反而较小，第13阶项接近零。这里比较的是输入之间的响应差异，不表示增加阻尼使第2阶放大。SHW3X改善较小则还涉及原有抵消的变化：在同一基准峰时22.92s，阻尼由5%增至8%后，第2、10阶项分别下降389.52kN、254.14kN，第13阶却由−42.62kN变为+37.90kN，增加的80.51kN抵消了部分下降。

上述关系把“需求本来较大”“主导项下降较少”和“原有抵消减弱”区分开。实际装置方案若要沿此路径解释，应取得其模态运动与非线性装置广义力，并检查目标剪力合成；不能把本节SHW3X的项直接放到实际六工况中。

### 5.3 目标层内力与模态数量检查

参数明确的无量纲三层模型可进一步说明局部输出的差别。既有人工H2输入例中，第三阶方向有效质量仅4.7892%，第1、2层反向运动却形成较大的第2层弹性剪力项；同一完整响应后验仅保留前两阶时，虽然累计方向质量达到95.2108%，第2层峰值仍分别低估43.3215%和41.6360%。模型参数和本构见[三层模型资料](../../../research/sessions/20261021-0737/roles/role5/R001-methods-supplement.md)。这一说明用于提醒工程师按目标层剪力检查模态数量影响，不把人工高频输入的低估比例直接移用于工程结构。CSI手册同样要求结合动力荷载频率特征检查模态数量对响应的影响[10]。

## 6 实际方案的工程复核步骤

（1）明确比较对象。首先核对基准与实际方案的输入方向、量级、时间轴、单位和模型设置；把模态增阻尼参考另列。按实际安装方向、所在层和两端连接位置核查装置清单。

（2）形成逐条成对记录。按楼层、方向、输入和截面位置列P_B、P_D、r_D、t_B与t_D，检查完整保存时程，而不是在基准峰时只读一次。对多个峰值时刻保留预定取值规则。

（3）同时查看改善与需求。在每层每方向分别找最小r_D和最大P_D，对两条控制记录分别保留成对峰值和时间。第8层X向先打开RH4X与SHW7X；第5层X向的RH4X、SHW4X减幅接近，应一并保留。底层及平均减幅只作总体对照。

（4）检查方案自身控制时段。计算d_D并标注两模型峰时。RH4Y第12层应分别查看12.26s与20.22s；SHW7Y第6层则分别查看38.02s与48.88s。较大d_D提示原峰时读数漏掉了方案自身更大的响应，不由此直接认定某阶模态或相位的原因。

（5）把装置需求放回实际时刻。在改善或需求控制输入下，按真实方向余弦合成装置水平力，分别列楼层剪力峰时出力和装置自身峰。随后检查装置轴力、行程、支撑与连接需求，并同时检查层间位移角，不能由剪力减幅直接替代这些项目。

（6）按可用模态信息确定深入检查的重点。若较大需求主要对应某个较大的低阶项，查看该阶层间变形、受力构件和沿高度刚度分布；若反向项在控制时刻明显，比较其变化是否削弱原有抵消。实际非线性方案应使用自身响应恢复的项，并检查各阶合成与软件输出的对应。

上述两种作用可能在同一输入下并存。进一步调整装置或连接参数时，还需核查真实两端沿轴线的相对位移和速度、整体柔度与相应频段传力[2,8,9]。分类用于决定先查哪条记录、哪一阶和哪类构件；具体参数调整后仍应重新比较各层剪力、变形、控制输入以及承载力和连接需求。

## 7 结论

（1）实际布设88只黏滞阻尼器的双塔连体结构中，共有六方向工况的72条楼层剪力峰均下降3.1238%～47.6719%，但底层仅在两个工况中恰为改善最小层。SHW7Y底层下降30.2486%，第6层仅下降16.0082%；底层与十二层平均减幅分别高14.2404和11.1426个百分点，说明总体指标不能替代逐层复核。

（2）实际方案24个楼层—方向组中，有12组的最小减幅与最大需求由不同输入控制。第8层X向应分别检查RH4X的7.7713%减幅和SHW7X的7132.2925kN需求；同一输入的百分比、成对峰值和峰时应一起保留，不能把两类控制记录拼为一个结果。

（3）只在基准峰时评价实际方案，会遗漏其自身控制峰。72条记录中该评价高估量的中位数为3.6586个百分点，RH4Y第12层达到34.6790个百分点；该例原峰时读数给出42.0199%改善，而完整时程峰减幅仅7.3409%。工程复核应分别查看两模型自身控制时段。

（4）第8层RH4X和SHW7X的剪力峰时装置水平合力绝对值，分别为装置自身峰的58.6736%和63.4488%。实际布置方案应把目标剪力峰时的有符号出力与装置自身峰同时列入检查，使改善、需求和传力时序对应到相同输入。

（5）14工况模态增阻尼参考中，两类控制不同的为19/24组；相同六工况范围内为7/24组，实际方案则为12/24组，控制输入需要在方案变化后重新确定。固定线性参照表明，主导模态项较大与反向抵消减弱是不同的叠加作用；其机制用于指导检查实际方案自身的模态运动，不代替实际非线性响应的分解。

@REFERENCES@
'''
refs='## 参考文献\n\n'+old.split('## 参考文献\n\n',1)[1]
for key,val in {'GEOMETRY':geom,'CASE_TABLE':'\n'.join(case_table),'CONTROLS':controls,'TIMING':timing,'BIAS_TABLE':'\n'.join(bias_table),'MODAL':modal,'REFERENCES':refs}.items():text=text.replace('@'+key+'@',val)
text=text.split('## 参考文献\n\n',1)[0]+'## 参考文献\n\n'+old.split('## 参考文献\n\n',1)[1]
assert not re.search(r'@[A-Z_]+@',text)
# Keep frozen table values, geometry and referenced figures intact. New tables are derived only from the reviewed response outputs.
assert old.split('## 参考文献\n\n',1)[1]==text.split('## 参考文献\n\n',1)[1]
for block in [geom,controls,timing,modal]:assert block in text
assert len(re.findall(r'\$\$.*?\$\$',text,re.S))==5
assert text.count('**表')==7
out.write_text(text,encoding='utf-8',newline='\n')
record={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'source':src.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output':out.relative_to(R).as_posix(),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'actual_record_count':72,'actual_main_control_groups':24,'actual_two_controls_differ':12,'reference168_is_auxiliary':True,'display_equations':5,'tables':7,'new_scientific_inputs':['actual-versus-baseline-time-peak-72.csv','actual-layer-direction-ranges-24.csv','actual-bottom-mean-screening-6.csv'],'references_unchanged':True,'frozen_geometry_controls_timing_modal_tables_unchanged':True}
(S/'draft-v001-build.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
