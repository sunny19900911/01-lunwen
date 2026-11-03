from pathlib import Path
import re,csv,json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
old=M/'p06-actual-timing-session027-v004.md';out=M/'p06-control-check-session028-v001.md';assert not out.exists()
t=old.read_text(encoding='utf-8')
t=t.replace('# 附加阻尼作用下双塔连体结构楼层剪力的分层评价','# 黏滞阻尼器作用下楼层剪力控制输入与控制时刻的识别')
t=t.replace('Story-by-story assessment of shear changes under added damping in a coupled twin-tower structure','Identification of governing inputs and times for story shear in a structure with viscous dampers')
# Keep original tables and original figure intact while reserving numbers for the new comparison.
t=re.sub(r'表([67])',lambda m:'表'+str(int(m[1])+1),t)
t=t.replace('图4','图5')
abs_cn='''加设阻尼器后，楼层剪力复核需要同时回答“哪条输入控制”和“哪个时刻控制”。以布设88只非线性黏滞阻尼器的双塔连体结构为例，分析六个方向工况下基准与实际方案的72条成对楼层剪力时程，分别保留最小减幅、最大需求的控制输入及各模型自身峰时。24个楼层—方向组中有12组的两类控制输入不同；仅在基准峰时评价减幅，其高估量中位数为3.6586个百分点，RH4Y第12层达到34.6790个百分点。第10层RH4Y的控制时刻由16.62s变为21.64s，两时刻基准需求差为109.60kN，降低量之差为689.99kN，使原先较低的时段转为控制。提出基准接近峰及其邻近时段的优先检查方法，并在全部72条记录上检验：采用5%近峰范围和±0.10s时段时，可覆盖41条记录的实际控制峰，故仍需完整时程取峰。两层、两输入的装置水平合力与软件剪力同刻列示；局部Maxwell等效线性化另用于检查装置出力次序。由控制输入、控制时刻和同刻装置出力形成逐层复核流程，明确总体减幅、局部需求与传力时序各自的检查对象。'''
abs_en='''Story-shear assessment after damper installation requires identifying both the governing input and the governing time. A coupled twin-tower structure with 88 nonlinear viscous dampers is examined using 72 paired story-shear histories from a baseline and an actual-damper scheme under six directional cases. The input governing the smallest reduction is distinguished from that governing the largest demand, and each model's own peak time is retained. The two inputs differ in 12 of 24 story-direction groups. Evaluating reduction only at the baseline peak time overstates it by a median of 3.6586 percentage points and by up to 34.6790 percentage points at Story 12 under RH4Y. At Story 10 under RH4Y, the governing time changes from 16.62 to 21.64 s: a baseline demand gap of 109.60 kN is outweighed by a difference of 689.99 kN in the reductions at the two times. A checking procedure prioritizes near-equal baseline peaks and their neighboring time intervals. Across all 72 histories, a 5% near-peak threshold with intervals of ±0.10 s captures 41 actual-scheme peaks, so complete-history peak evaluation remains necessary. Simultaneous software shear and projected damper forces are compared for two stories and two inputs. A local Maxwell linearization separately examines the ordering of damper forces. The resulting procedure combines governing inputs, governing times and simultaneous device forces for story-by-story assessment.'''
t=re.sub(r'(## 摘要\n\n).*?(\n\n\*\*关键词)',lambda m:m[1]+abs_cn+m[2],t,flags=re.S)
t=re.sub(r'(## Abstract\n\n).*?(\n\n\*\*Keywords)',lambda m:m[1]+abs_en+m[2],t,flags=re.S)
t=t.replace('控制输入；时程分析','控制输入；控制时刻；时程分析').replace('governing input; response-history analysis','governing input; governing time; response-history analysis')
t=t.replace('研究重点是把常规时程输出转为需要重点复核的楼层、输入和时段。','研究重点是同时识别控制输入和控制时刻，把常规时程输出转为需要重点复核的楼层、输入与时段，并检验接近峰筛查和装置等效线性化能提供多大程度的解释。')
t=t.replace('本文直接比较该软件截面输出，装置力另用于同刻检查，不从楼层剪力中扣出主体剪力。','本文直接比较该软件Bottom输出；第4.5节另外列出装置水平合力及代数差。该差值的主体内力含义，需要由相同切口、相同受力侧的独立结构内力确认。')
method=r'''### 3.4 控制时刻变化的接近峰检查

先仅用基准剪力绝对值曲线识别保存网格上的局部峰，保留不低于基准绝对最大值95%的候选峰。平台峰取最早保存点，端点作单侧比较，不按实际方案结果合并或删除候选峰。对每个候选时刻，再查看实际方案在该时刻及其前后0.10s内的响应。5%与0.10s是本例的检查参数，同时用2%、10%近峰范围作敏感性比较。

对基准原峰时刻t₁和任一候选时刻t₂，按第5.2节的绝对值定义比较原需求差与两时刻降低量之差：

$$\delta_1-\delta_2>b_1-b_2.$$

该式成立时，实际方案在t₂的剪力绝对值大于t₁，候选时段应优先复核。它判断这两个时刻的相对大小；完整控制时刻仍取实际方案全部保存时刻中的绝对最大值。本方法使用已算得的实际方案时程，作用是组织复核和识别竞争峰，不是仅凭基准响应预测设置阻尼器后的峰值。

'''
t=t.replace('## 4 实际阻尼器方案的分层结果',method+'## 4 实际阻尼器方案的分层结果')
def read(p):
 with p.open(encoding='utf-8-sig',newline='')as f:return list(csv.DictReader(f))
four=read(S/'root-four-records.csv')
balance='''### 4.5 同一时刻的软件剪力与装置水平合力

选取第8、10层的RH4X、RH4Y，共四条记录。每条记录中，楼层剪力QT、按真实轴线投影的QD以及QT−QD均取相同保存时刻，完整曲线见图4；表6列实际方案自身剪力峰时的数值。两峰不能分别取出后相减。

**表6 四条记录在实际方案剪力峰时的同刻对照**

|楼层/输入|时刻/s|QT/kN|QD/kN|QT−QD/kN|QT+QD/kN|
|---|---:|---:|---:|---:|---:|
'''
for r in four:balance+=f"|第{r['Story']}层/{r['Case']}|{float(r['time_QT_peak_s']):.2f}|{float(r['QT_kN']):.2f}|{float(r['QD_J_resisting_kN']):.2f}|{float(r['QT_minus_QD_kN']):.2f}|{float(r['QT_plus_QD_kN']):.2f}|\n"
balance+='''
QD沿用第4.3节的J端结构内力抵抗项约定。四个剪力控制时刻的QD均为负，因此表中QT−QD大于QT，而QT+QD小于QT；两种结果的大小不能决定哪一种是主体剪力。Section Cut合力需要明确所含对象、受力侧及坐标方向[11]。本例现有导出没有同一切口独立的框架、墙或Section Cut合力，故QT−QD在此列为代数差，不作为主体剪力或独立平衡残差。该对照明确了已知装置分力与软件输出的数值关系，主体内力的包含关系另需同切口内力核对。

![图4 两层两输入的同刻剪力与装置水平合力对照](../../../research/sessions/20261103-2105/roles/response/four-record-QT-QD-difference.png)

图4 第8、10层在RH4X、RH4Y下的完整QT、QD与QT−QD曲线，单位为kN。QD是J端结构内力抵抗项，装置施加于J节点的外力方向相反；差值不标为主体剪力。完整三时刻数值和正负号对照见本轮补充资料。

'''
t=t.replace('## 5 控制输入对照与实际峰值变化',balance+'## 5 控制输入对照与实际峰值变化')
eq=read(S/'roles/equivalent/equivalent-QD-two-times.csv')
extra='''### 5.3 规定端部运动下的等效线性化检查

以第10层RH4Y为例，保留装置串联弹簧刚度κ=500000kN/m，仅将非线性黏滞单元替换为等效线性黏滞单元。由原生轴力和α=0.3本构求黏滞单元速度，在0—15s内按耗能相同确定等效黏滞系数，再用原生装置总变形驱动线性Maxwell模型；15s后的响应用于检验。两处待检查的16.62s和21.64s均不参与系数确定。线性模型按相邻保存点之间总变形线性变化作精确递推，保持串联弹性变形。

**表9 第10层RH4Y装置水平合力的局部等效对照**

|时刻/s|实际QD/kN|规定运动下线性等效QD/kN|
|---|---:|---:|
'''
for r in eq:extra+=f"|{float(r['time_s']):.2f}|{float(r['native_QD_kN']):.2f}|{float(r['linear_prescribed_u_QD_kN']):.2f}|\n"
extra+='''
两种装置计算均保留21.64s出力绝对值大于16.62s的次序，但15—50s装置合力的相对RMS差为46.00%。这一差异说明，用一个固定等效黏滞系数概括整段非线性装置响应仍有较大偏差。这里规定了原生端部运动，并未求解安装等效装置后的新结构运动，也未得到新的楼层剪力；因此表9检验的是局部出力次序，不能据此认定楼层剪力控制时刻在线性等效结构中仍会迁移。完整结构检验需要把全部装置的等效作用组装到相同结构方程后重新计算，而非由这一层合力指定统一附加阻尼比。系数、能量定义和逐只结果见[本轮补充资料](../../../research/sessions/20261103-2105/四项补强资料说明.md)。

### 5.4 接近峰筛查在全部实际记录中的表现

对72条记录按第3.4节先冻结基准候选峰，再读取实际方案结果。表10同时列出单点读取和邻近时段检查的效果。完整时程中的实际控制峰为对照值，所有记录和漏检均保留。

**表10 三种近峰范围的检查结果（共72条记录）**

|距基准峰范围/%|候选峰总数|仅候选时刻误差≤1%/条|±0.10s覆盖实际峰/条|±0.10s峰误差≤1%/条|邻近时段最大低估/%|
|---|---:|---:|---:|---:|---:|
'''
for r in read(S/'roles/screen/screening-summary-3.csv'):extra+=f"|{float(r['epsilon_percent']):.0f}|{r['candidate_count_total']}|{r['peak_error_le_1_percent']}|{r['neighborhood_exact_capture']}|{r['neighborhood_error_le_1_percent']}|{float(r['maximum_neighborhood_peak_miss_percent']):.2f}|\n"
extra+='''
第10层RH4Y在5%范围内保留两个基准候选峰，其中21.68s附近的实际方案峰发生在21.64s。只读21.68s会低估实际峰2.3360%，检查其前后0.10s即可找到3395.9230kN的实际峰。这说明即使基准竞争峰已被保留，也应检查邻近时段，不能只读一个相同时间点。

然而，5%范围加邻近时段仅覆盖41/72条实际控制峰。RH4Y第12层的实际峰发生在12.26s，该时刻基准绝对值比基准最大值低23.0727%，未进入5%接近峰时段，筛查峰比实际峰低31.7364%。将阈值放宽到10%也不能消除全部漏检。因此，接近峰检查适合安排人工复核的先后顺序；最终需求与减幅仍由实际方案完整时程确定。两个时刻的大小关系可以精确核算，有限近峰集合能否覆盖全部控制时段则需单独检验。

'''
t=t.replace('## 6 实际方案的工程复核步骤',extra+'## 6 实际方案的工程复核步骤')
t=t.replace('（4）检查方案自身控制时段。','（4）检查方案自身控制时段。先按5%近峰范围列基准竞争峰及其前后0.10s的实际方案响应，比较原需求差与降低量之差；再以完整实际时程确认控制峰，不能因候选时段中没有较大峰而省略这一步。')
t=t.replace('（5）把装置需求放回实际时刻。','（5）把装置需求放回实际时刻。先统一截面侧别与装置力正方向；如需计算主体剪力，应补上独立的同切口主体内力对照，不凭QT−QD曲线的平滑程度确认受力含义。')
t=t.replace('上述两种作用可能在同一输入下并存。','上述两种作用可能在同一输入下并存。局部装置等效须保留串联柔度，并核查适用响应范围；它不能替代等效装置与结构共同求解。')
t=t.replace('（5）14工况模态增阻尼参考中，','（5）控制输入与控制时刻应分别识别，回答哪条输入产生较大需求、该输入下哪个时段真正控制。14工况模态增阻尼参考中，')
t=t.replace('## 参考文献','''（6）基准接近峰可用于优先安排时段检查，但不能代替完整实际时程取峰。采用5%范围及±0.10s时段时，72条记录中覆盖41条实际控制峰，最大峰值低估31.7364%；10%范围仍有漏检。同刻装置出力对照和局部等效线性化则分别用于核查传力方向、出力次序及其适用范围。

## 参考文献''')
t+='\n[11] COMPUTERS & STRUCTURES, INC. Section Cuts[EB/OL]. ETABS Help. [2026-11-03]. https://docs.csiamerica.com/help-files/etabs/Menus/Define/Section_Cuts.htm.\n'
out.write_text(t,encoding='utf-8',newline='\n')
result={'source_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'tables':len(re.findall(r'\*\*表\d+ ',t)),'displays':len(re.findall(r'\$\$.*?\$\$',t,re.S)),'figures':len(re.findall(r'!\[',t)),'actual_global_equivalent_story_shear_claim':False,'independent_QS_balance_claim':False}
(S/'draft-build-v001.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
