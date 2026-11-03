from pathlib import Path
import hashlib,json,re,difflib

H=Path(__file__).resolve().parent
R=H.parents[2]
old=R/'papers/damping-output-boundaries/manuscript/p06-design-reflection-session024-v002.md'
new=old.with_name('p06-mechanism-classification-v001.md')
assert hashlib.sha256(old.read_bytes()).hexdigest()=='750b1dcc8fa38014d45307cec124c6ef83058a063b32a5bee7ba7c1bd95f1324'
assert not new.exists()
s=old.read_text(encoding='utf-8')
zh='''针对附加阻尼后各层剪力改善不同、改善较小与绝对需求较大未必由同一输入控制的问题，以双塔连体结构为例，建立逐层多输入剪力复核流程。比较相同输入的基准模型与增加3个百分点模态阻尼的参考模型，形成14个方向工况、12层的168条成对记录。24个楼层—方向组中有19组的两类控制输入不同。X向第5层最小减幅为SHW3X下的6.8513%，最大参考剪力则为SHW4X下的9027.7451kN，后者自身减幅为11.3022%。固定300阶线性参照显示，SHW3X的第13阶项在基准峰时由反向抵消转为同向作用，抵消部分剪力下降；SHW4X较大需求则对应更大的第2阶项。两类控制输入需分别辨认模态组成。底层仅在3个方向工况中取得最小减幅；仅在基准峰时评价的减幅高估量中位数为0.0558个百分点，最大为10.5831个百分点。复核流程据此分别检查改善、绝对需求、同刻模态项及装置两端运动，为主体受力与消能方案的进一步比选提供依据。'''
en='''A story-by-story, multi-input procedure is presented for shear assessment of a coupled twin-tower structure. The baseline model and a reference model with three additional percentage points of modal damping are compared under identical inputs, using 168 paired records from 14 directional cases and 12 stories. The inputs controlling minimum reduction and maximum reference shear differ in 19 of the 24 story-direction groups. At Story 5 in the X direction, SHW3X gives the minimum reduction of 6.8513%, whereas SHW4X governs the reference demand of 9027.7451 kN with its own reduction of 11.3022%. A fixed 300-mode linear reference distinguishes two modal effects. Under SHW3X, the mode-13 term changes from opposing to reinforcing the total shear at the baseline peak time, offsetting part of the shear decrease. The larger demand under SHW4X instead corresponds to a larger mode-2 term. Modal composition is therefore examined separately for the two governing inputs. The bottom story gives the minimum reduction in only three directional cases. Evaluation at the baseline peak time overstates the reduction by a median of 0.0558 and a maximum of 10.5831 percentage points. The procedure checks improvement, absolute demand, simultaneous modal terms and relative damper-end motion separately to inform subsequent comparison of structural and damping schemes.'''
s=re.sub(r'(?<=## 摘要\n\n).*?(?=\n\n\*\*关键词)',lambda _:zh,s,flags=re.S)
s=re.sub(r'(?<=## Abstract\n\n).*?(?=\n\n\*\*Keywords)',lambda _:en,s,flags=re.S)
oldpara='SHW4X在自身峰时的参照第2阶项大于SHW3X，第10阶项反而较小，第13阶为很小的反向项。因此，这组参照没有出现第10、13阶同向叠加主导SHW4X较高峰值的现象。两列比较的是不同输入在各自峰时的组成，不能将其差额解释为同一时刻的因果分担；绝对需求仍按表2的软件成对峰值复核。'
newpara='''SHW4X较高的峰值在模态组成上主要表现为第2阶项较大：8%阻尼参照中，该项为7753.76kN，高于SHW3X的6762.84kN；第10阶项则较小，第13阶项接近零。同一SHW4X输入下，第2阶项在两种阻尼状态各自软件峰时由8632.39kN降至7753.76kN，说明这里的“较大”指输入之间的幅值差异，而不是增阻尼使该阶响应放大。表4用于辨认各自峰时的组成，绝对需求仍按表2的软件成对峰值复核。

SHW3X的改善较小还可从反向模态项的变化理解。在同一基准峰时22.92s，阻尼由5%增至8%后，参照第2、10阶项分别下降389.52kN和254.14kN，而第13阶项由−42.62kN变为+37.90kN。第13阶原有的反向抵消消失并转为同向作用，其增加的80.51kN抵消了前述两项下降的一部分。因此，反向模态项抵消的变化与主导模态项的幅值差异，应作为两种不同的复核线索：前者帮助解释改善为何受限，后者帮助辨认较大绝对需求来自何种模态组成。两种作用可以并存，需在各控制输入下分别检查。两峰时的同刻对照见[机制对照表](../../../research/revisions/20261103-1407-mechanism-classification/机制分类与同刻对照.md)。'''
assert s.count(oldpara)==1
s=s.replace(oldpara,newpara)
start=s.index('### 6.1 工程启示与设计反思')
end=s.index('\n## 7 结论',start)
s=s[:start]+'''### 6.1 按模态组成确定进一步复核的重点

对改善较小或绝对需求较大的楼层，先分别确定最小减幅和最大参考剪力的控制输入，再查看各输入下两种阻尼状态的模态组成。比较时既列各自峰时的组成，也在同一控制时刻保留各阶项的符号与变化。只有这样，才能分清需求本来较大、主导项下降较少和原有抵消减弱这几种情况。

当较大需求主要对应较大的低阶项时，优先检查该阶振型对应的层间变形、受力构件及沿高度的刚度分布，并结合输入的频率特征判断目标层为何形成较大内力。SHW4X第5层首先应查看第2阶项；其随增阻尼下降但仍大于SHW3X，宜围绕这一主导响应比较主体刚度分布与附加阻尼方案，而不能仅因某阶项较大就直接确定增刚位置。

当反向高阶项在控制时刻具有明显幅值时，先比较它在同一输入、同一时刻随增阻尼的变化。若反向项趋零或反号，其变化会抵消部分同向项的下降，SHW3X第13阶即属此类。若进一步采用实体阻尼器方案，则检查这些模态下真实两端沿装置轴线的相对位移和速度，并按相关频段核查支撑、连接与阻尼单元的整体柔度及本构参数[2,8,9]。检查重点是端部运动能否有效传至耗能单元，以及各阶作用合成后的目标响应；振型曲率或单节点位移不能替代端部相对运动。

上述分类用于确定“先查哪条记录、哪一阶、哪一类构件或参数”。调整刚度分布、连接或阻尼参数后，应在相应结构模型中重新比较各层剪力、层间变形和控制输入，同时核查承载力、稳定、连接及装置力和行程，以综合响应作为方案比选依据。
''' + s[end:]
cs=s.index('## 7 结论')
ce=s.index('## 参考文献',cs)
c=s[cs:ce]
for oldn,newn in [(5,6),(4,5),(3,4)]:c=c.replace(f'（{oldn}）',f'（{newn}）')
pos=c.index('（4）')
c=c[:pos]+'''（3）固定300阶线性参照中，SHW3X第5层在基准峰时的第13阶项由−42.62kN变为+37.90kN，原有抵消消失并反号，抵消了部分剪力下降；SHW4X较大需求则对应更大的第2阶项。工程复核应区分反向模态项抵消的变化与主导项幅值较大，分别检查相关模态运动、主体受力及实体装置的端部运动和整体柔度。

''' + c[pos:]
s=s[:cs]+c+s[ce:]
new.write_text(s,encoding='utf-8',newline='\n')
orig=old.read_text(encoding='utf-8')
assert re.findall(r'^\|.*$',s,re.M)==re.findall(r'^\|.*$',orig,re.M),'Source tables changed'
assert re.findall(r'\$\$.*?\$\$',s,re.S)==re.findall(r'\$\$.*?\$\$',orig,re.S),'Display math changed'
assert re.findall(r'!\[.*?\]\(.*?\)',s)==re.findall(r'!\[.*?\]\(.*?\)',orig),'Figures changed'
assert s[s.index('## 参考文献'):]==orig[orig.index('## 参考文献'):],'References changed'
(H/'manuscript-change.diff').write_text(''.join(difflib.unified_diff(orig.splitlines(True),s.splitlines(True),fromfile=old.name,tofile=new.name)),encoding='utf-8',newline='\n')
report={'source':old.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'output':new.relative_to(R).as_posix(),'bytes':new.stat().st_size,'sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'tables_unchanged':True,'display_math_unchanged':True,'figures_unchanged':True,'references_unchanged':True,'changed_sections':['Chinese abstract','English abstract','4.2 interpretation','6.1','conclusion3 added; following renumbered']}
(H/'source-change-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
