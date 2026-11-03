from pathlib import Path
import csv,json,hashlib,re
H=Path(__file__).resolve().parent;R=H.parents[2]
M=R/'papers/damping-output-boundaries/manuscript'
src=M/'p06-mechanism-classification-v003.md';dst=M/'p06-actual-damper-session025-v001.md'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='afa9ccbef57335084d7bb57a8ed443644b7fd53c57623cf59ea02788212708df'
assert not dst.exists()
def readcsv(p):return list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
controls=readcsv(H/'roles/response/common-six-control-records-24.csv')
layout=readcsv(H/'roles/geometry/layout-by-story-11.csv')
timing=readcsv(H/'roles/response/Story8-native-device-timing-6.csv')
paired=json.loads((H/'roles/pairing/pairing-results.json').read_text(encoding='utf-8'))
assert paired['status']=='frozen' and paired['actual_base_vs_baseline_components_exact']==36
assert json.loads((H/'roles/response/delivery-manifest.json').read_text(encoding='utf-8'))['status']=='frozen'
s=src.read_text(encoding='utf-8')
zh='''附加阻尼后，同一楼层剪力“减幅最小”与“绝对需求最大”的控制输入可能不同，工程复核需分别保留两类记录。以双塔连体结构为例，比较基准与增加3个百分点模态阻尼的参考模型，14个方向工况、12层共168条成对记录中，24个楼层—方向组有19组的两类控制输入不同。固定300阶线性参照表明，SHW3X的第13阶原有抵消消失可抵消部分剪力下降，SHW4X较大需求则对应更大的第2阶项。进一步接入88只实际阻尼器的布置及模型响应，在导出基底输入逐样本一致的共有六工况中，实体方案有12/24组的两类控制输入不同。第8层X向较小减幅由RH4X控制，为7.7713%；较大需求由SHW7X控制，为7132.2925kN，其自身减幅为15.3907%。两输入层剪峰时的装置水平合力绝对值分别为自身峰的58.6736%和63.4488%。原峰时评价的减幅高估量最大为10.5831个百分点。该流程将实际布置、逐层需求和控制时刻装置出力联系起来，为主体与消能方案的复核及比选提供依据。'''
en='''After damping is added, the input producing the smallest story-shear reduction may differ from that producing the largest absolute demand, so both governing records need to be retained. For a coupled twin-tower structure, a baseline model and a reference model with three additional percentage points of modal damping are compared using 168 paired records from 14 directional cases and 12 stories. The two governing inputs differ in 19 of the 24 story-direction groups. A fixed 300-mode linear reference relates the SHW3X response to loss of cancellation by the mode-13 term, whereas the larger SHW4X demand corresponds to a larger mode-2 term. The actual layout of 88 dampers and the corresponding model responses are then examined. Under six common directional cases with identical exported base-acceleration samples, the actual-damper scheme has different governing inputs in 12 of the 24 groups. At Story 8 in the X direction, RH4X controls the minimum reduction of 7.7713%, while SHW7X governs the demand of 7132.2925 kN with its own reduction of 15.3907%. The damper horizontal-force sum at the story-shear peak reaches 58.6736% and 63.4488% of its own peak under these two inputs. Evaluation only at the baseline peak time overstates reduction by up to 10.5831 percentage points. The procedure links actual layout, story-specific demand and simultaneous damper forces to support engineering checks and scheme comparison.'''
s=re.sub(r'(?<=## 摘要\n\n).*?(?=\n\n\*\*关键词)',lambda _:zh,s,flags=re.S)
s=re.sub(r'(?<=## Abstract\n\n).*?(?=\n\n\*\*Keywords)',lambda _:en,s,flags=re.S)
old='通过底层和平均值对照、原峰时评价偏差及装置同刻出力，形成可由常规输出实施的分层复核步骤；三层模型仅辅助说明局部剪力与模态叠加的关系。'
new='通过底层和平均值对照、原峰时评价偏差，形成可由常规输出实施的分层复核步骤；再接入88只实际阻尼器的布置和共有六工况响应，以第8层为例核查两类控制输入及装置同刻出力。三层模型仅辅助说明局部剪力与模态叠加的关系。'
assert old in s;s=s.replace(old,new)
old='另有设置黏滞阻尼器的模型，覆盖RH4、SHW4、SHW7三组输入各X/Y方向，仅用于独立查看装置出力时序。'
new='另有按实际位置设置黏滞阻尼器的模型，记为实体方案D，覆盖RH4、SHW4、SHW7三组输入各X/Y方向，用于共有六工况下的方案响应与装置出力核查。'
assert old in s;s=s.replace(old,new)
old='现有资料尚未形成三模型完整质量、刚度及全部求解设置的逐项对照，阻尼器模型与另两模型的输入配对也未完全补齐。本文以已配对的基准—参考结果讨论逐层剪力变化，不将实体装置模型与参考模型的峰值差解释为安装装置产生的减剪率。[三模型峰值的补充对照](../../../research/sessions/20261102-1917/roles/role5/R001/descriptive-three-model-comparison.md)保留原有并列记录。'
new='基准与参考模型的输入逐样本一致，共有六工况的工况设置及质心质量、刚心汇总表相同。实体方案与基准模型在六工况共16296个保存时刻的基底加速度六分量逐点一致；实体模型18个质心方向质量与基准、参考表的逐组数值对应。因此，实体方案相对基准的软件峰值变化可按同一输入记录比较。本文将其作为工程提供方案之间的响应比较；实体方案的背景阻尼和完整内部求解设置未全部导出，不将三模型差别归为单一阻尼参数的作用。配对范围及完整结果见[实际方案资料与附表](../../../research/sessions/20261103-1458/实际方案资料与完整附表.md)。'
assert old in s;s=s.replace(old,new)
old='输入来源、倍率、时间缩放和完整模型设置的缺项集中列于该说明，以下结果限定于现有配对资料和保存时程。'
new='输入来源及完整模型设置的资料范围列于该说明；共有六工况下，基准与参考模型的荷载倍率均为3.5、时间倍率均为1，实体方案的有效基底输入另经逐样本核对。新增比较条件见[实际方案资料](../../../research/sessions/20261103-1458/实际方案资料与完整附表.md)，以下结果均按相应保存时程评价。'
assert old in s;s=s.replace(old,new)
s=s.replace('|阻尼器模型的楼层剪力|RH4、SHW4、SHW7各X/Y六工况，72条主方向记录|定位装置模型自身的剪力控制时刻，辅助独立出力时序检查|','|实际阻尼器模型的楼层剪力|RH4、SHW4、SHW7各X/Y六工况，72条主方向记录|共有输入下的方案峰值比较、两类控制输入与装置同刻出力核查|')
s=s.replace('|装置轴力与变形|第8—11层32只装置×六工况|分析已有楼层装置合力及出力时序|','|实际布置|3416节点坐标及88只Link连接位置|绘制布置、核对分层数量、安装方向与轴向力水平投影|\n|装置轴力与变形|第8—11层32只装置×六工况|分析完整范围内的装置合力及出力时序|')
# Preserve the original modal study and original peak-time-bias section; the old
# independent-device section is integrated into the new application section.
a=s.index('### 4.3 原峰时评价的偏差');b=s.index('### 4.4 独立装置模型的出力时序');c=s.index('## 5 局部剪力与模态叠加的简化说明')
bias=s[a:b].replace('### 4.3 原峰时评价的偏差','### 4.4 原峰时评价的偏差').replace('图2','图5')
lines=['### 4.3 实际阻尼器布置与共有工况的应用核查','','#### 4.3.1 实际布置与比较范围','',
'图2按88只装置的真实I/J端点坐标绘制。第1—11层每层8只，水平投影沿X、Y的装置各4只，全楼各44只；第12层没有该连接表所列的跨层装置。装置轴线长度为6.440～9.401m，水平倾角为29.20°～48.37°，各层配置见表5。灰色区段标出具有完整轴力记录的第8—11层。', '',
'实体方案采用工程提供的有限Maxwell参数κ=500000kN/m、c=477kN(s/m)^0.3、α=0.3。装置作用经过真实端部相对运动、非线性黏滞单元及串联柔度共同传递，与各阶统一增加3个百分点模态阻尼的参考方案分别评价[8,9]。几何相同数量并不意味着水平合力相同，轴力需按每只装置的实际方向余弦合成。','',
'![图2 实际88只阻尼器布置](../../../research/sessions/20261103-1458/roles/geometry/actual-damper-layout.png)','',
'图2 实际阻尼器轴线的X-Y、X-Z和Y-Z投影。坐标单位为m，线段按真实两端坐标绘制；不同装置在投影中可重合。图中线段表示装置，未绘主体梁柱。灰色区段定位第8—11层完整出力资料的范围。','',
'**表5 实际装置分层配置（按上端J所在层归类）**','',
'|上端所在层|连接标高/m|数量|X向/Y向数量|轴长/m|水平倾角/°|','|---|---|---:|---|---|---|']
for row in layout:
    num=int(row['Story'][5:]);lines.append(f"|第{num}层|{float(row['lower_z_m']):.1f}→{float(row['upper_z_m']):.1f}|{row['count_total']}|{row['X_only']}/{row['Y_only']}|{float(row['length_min_m']):.3f}～{float(row['length_max_m']):.3f}|{float(row['inclination_min_deg']):.2f}～{float(row['inclination_max_deg']):.2f}|")
lines += ['', '#### 4.3.2 共有六工况的分层响应与两类控制输入','',
'在RH4、SHW4、SHW7各X/Y六工况内，分别比较三模型共72条楼层记录。以实体方案完整保存时程的剪力绝对峰记为P_D，将式(2)中的P_M替换为P_D，得到相对基准的方案峰值减幅r_D；各模型仍保留自身峰时。图3为同方向三个输入的逐层绝对峰包络，各层可由不同输入控制，不能作为同一时刻的沿高度剪力分布。','',
'![图3 共有六工况三模型峰值包络](../../../research/sessions/20261103-1458/roles/response/common-six-three-model-peak-envelope.png)','',
'图3 共有六方向工况下三模型楼层剪力绝对峰包络。X、Y分别由RH4、SHW4、SHW7三个输入逐层取最大值，各模型按自身完整时程求峰。该图用于比较需求分布，不以两条包络直接计算同输入减幅。','',
'按每层每方向三个输入分别选取最小r_D和最大P_D，实体方案24组中有12组由不同输入控制；在完全相同的六工况范围内，模态增阻尼参考为7/24组。原14工况参考模型的19/24组仍按原输入集合报告。这说明“分别保留两类控制输入”的复核步骤在实际布置方案中仍有必要，但控制记录不能直接沿用参考模型。', '',
'实体方案相对参考模型，72条峰值中有34条较高、38条较低；最大需求的控制输入有2/24组改变，均位于第12层，X、Y方向分别由参考模型的SHW7X、SHW7Y转为实体方案的RH4X、RH4Y。这里比较的是所提供方案的输出，不据此将一种阻尼方式概括为对所有楼层更优。', '',
'**表6 实体方案代表层的两类控制输入及各自成对峰值**','',
'|方向/楼层|查看用途|输入|P_B/kN|P_D/kN|本输入r_D/%|','|---|---|---|---:|---:|---:|']
for axis,story in [('X','Story5'),('X','Story8'),('Y','Story8')]:
    row=next(x for x in controls if x['Axis']==axis and x['Story']==story)
    num=int(story[5:])
    for label,case,pb,pd,red in [
        ('最小方案减幅',row['conditional_min_D_reduction_case'],row['P_B_at_conditional_min_D_reduction_kN'],row['P_D_at_conditional_min_D_reduction_kN'],row['conditional_min_D_reduction_percent']),
        ('最大实体剪力',row['actual_max_demand_case'],row['P_B_at_actual_max_demand_kN'],row['actual_max_demand_kN'],row['conditional_r_D_at_actual_max_demand_percent'])]:
        lines.append(f'|{axis}/第{num}层|{label}|{case}|{float(pb):.2f}|{float(pd):.2f}|{float(red):.4f}|')
lines += ['',
'第8层X向的最小方案减幅由RH4X控制，为7.7713%，实体剪力峰5776.6513kN；最大需求却由SHW7X控制，为7132.2925kN，该输入自身减幅为15.3907%。Y向也需分别查看SHW4Y的9.3098%与SHW7Y的6707.7015kN，后者自身减幅为20.7852%。第5层X向的最小减幅输入为RH4X，但它与SHW4X只相差0.0181个百分点，宜将两条记录一并复核。实体数据中没有SHW3X，故不将第4.2节的控制输入或逐阶解释直接迁入本节。','',
'#### 4.3.3 实际布置下的控制时刻装置出力','',
'第8层8只装置均由下层I端连接至上层J端；每个主输入方向有4只装置的水平投影非零。取单位向量n由I指向J，轴力P按原生正拉力约定，QD=Σn_eP表示上端J的结构内力抵抗项，装置施加于J节点的外力为−QD。24个楼层—工况的8只装置时程均与楼层输出时间逐点一致，I/J重复列示的同一轴力只计一次。','',
'**表7 第8层六工况控制剪力时刻的实际装置合力**','',
'|工况|QT绝对峰/kN（时刻/s）|QD绝对峰/kN（时刻/s）|QT峰时QD/kN|同刻绝对值/自身峰/%|tQD−tQT/s|','|---|---|---|---:|---:|---:|']
for row in timing:
    lines.append(f"|{row['Case']}|{float(row['QT_peak_kN']):.4f}（{float(row['t_QT_peak_s']):.2f}）|{float(row['QD_abs_peak_kN']):.4f}（{float(row['t_QD_peak_s']):.2f}）|{float(row['QD_signed_at_QT_peak_kN']):.4f}|{float(row['abs_QD_at_QT_peak_over_QD_abs_peak_percent']):.4f}|{float(row['t_QD_minus_t_QT_s']):.2f}|")
lines += ['',
'图4进一步比较第8层X向两条控制记录。RH4X层剪峰为+5776.65kN，发生在21.60s；同刻QD为−238.11kN，而QD自身绝对峰405.83kN发生在11.50s。SHW7X层剪峰为−7132.29kN，发生在38.06s；同刻QD为+277.36kN，QD自身绝对峰437.15kN发生在32.04s。两条记录使用完全相同的实际布置，但控制时刻及出力不同。', '',
'![图4 第8层两控制输入的实际出力](../../../research/sessions/20261103-1458/roles/response/R002/Story8-RH4X-SHW7X-native-QT-QD-v003.png)','',
'图4 第8层在RH4X、SHW7X下的软件楼层剪力QT与装置水平合力QD保存时程。QD按该层8只实际装置的轴力及方向余弦合成；上下行纵轴分别为±8000kN和±500kN，虚线标出各自完整记录的绝对峰时。QD为上端J结构内力抵抗项，装置对节点外力为−QD。', '',
'两输入层剪峰时的QD绝对值为自身峰的58.6736%和63.4488%。因此，实际装置方案的复核既要回到需求或改善控制输入，也要查看该时刻的真实水平分力，不能由装置自身最大出力代替。该比例描述出力时序，不作为减震贡献率；软件Bottom剪力的Link包含方式和截面正方向仍按第2.1节保留，本文不由QT与QD相减另造主体剪力。', '',
'这一应用核查将实际布置、方案峰值与控制时刻出力联系起来，支持把相同的分层复核流程用于实体装置方案。实体单元的频率与幅值相关作用仍需结合实际本构、支撑连接柔度及完整结构响应评价，不能仅用均匀增加3个百分点模态阻尼替代。','']
s=s[:a]+'\n'.join(lines)+'\n'+bias+s[c:]
s=s.replace('表6中第三阶方向有效质量','表8中第三阶方向有效质量').replace('**表6 三层模型','**表8 三层模型')
s=s.replace('实体装置模型另查剪力峰时的有符号水平合力及装置自身峰。','实体装置模型按第4.3节保留两类控制输入，并查看实际安装方向下剪力峰时的有符号水平合力及装置自身峰。')
s=s.replace('X向第5层应同时查看SHW3X与SHW4X；','模态增阻尼参考的X向第5层应同时查看SHW3X与SHW4X；实体方案第8层X向则分别查看RH4X与SHW7X。')
cs=s.index('## 7 结论');ce=s.index('## 参考文献',cs);con=s[cs:ce]
con=con.replace('（6）','（7）').replace('（5）','（6）').replace('（4）','（5）')
pos=con.index('（5）');con=con[:pos]+'''（4）实际方案的88只阻尼器按真实位置分布于第1—11层，每层8只。共有六工况的方案响应比较中，24组有12组的最小减幅与最大需求由不同输入控制，同范围模态增阻尼参考为7组。第8层X向需分别查看RH4X的7.7713%减幅和SHW7X的7132.2925kN需求，表明两类控制记录应在实际方案中重新确定。

'''+con[pos:]
old='（6）第8层RH4X、RH4Y两例中，剪力峰时装置合力绝对值为其自身峰的58.6736%和62.5278%。装置自身峰不能替代控制剪力时刻的出力；这些比例用于说明时序，不作为减震贡献率。'
new='（6）第8层RH4X、SHW7X两条控制记录中，剪力峰时实际装置水平合力绝对值为其自身峰的58.6736%和63.4488%。实际布置的复核应同时保留控制输入、层剪峰时有符号出力及装置自身峰，以目标时刻的传力检查补充峰值评价。'
assert old in con;con=con.replace(old,new);s=s[:cs]+con+s[ce:]
oldtext=src.read_text(encoding='utf-8')
assert re.findall(r'\$\$.*?\$\$',s,re.S)==re.findall(r'\$\$.*?\$\$',oldtext,re.S),'Original display equations changed'
def tables(t):return re.findall(r'(?:^\|.*\n)+',t,re.M)
assert tables(s)[1:4]==tables(oldtext)[1:4],'Original 14-case and modal-result tables changed'
assert s[s.index('## 参考文献'):]==oldtext[oldtext.index('## 参考文献'):]
dst.write_text(s,encoding='utf-8',newline='\n')
report={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output':dst.relative_to(R).as_posix(),'bytes':dst.stat().st_size,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'original_tables2_to4_exact':True,'table1_scope_expanded_intentionally':True,'original_display_equations_exact':True,'references_exact':True,'tables':len(tables(s)),'figures':len(re.findall(r'!\[',s)),'comparisons':'14-case reference19/24, common-six reference7/24, provided actual scheme12/24 kept separate'}
(H/'manuscript-v001-change-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
