from pathlib import Path
import csv,json,hashlib,re,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
src=R/'papers/damping-output-boundaries/manuscript/p06-actual-main-session026-v003.md'
old=src.read_text(encoding='utf-8');assert hashlib.sha256(src.read_bytes()).hexdigest()=='2aae66c26effa5c5436cd0b08cb883ead63d5f0ed12ffd88f47a9400a24cc370'
out=src.with_name('p06-actual-timing-session027-v001.md');assert not out.exists()
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
eight=read(S/'roles/response/Story8-actual-peak-accounting-6.csv')
ten=read(S/'roles/response/R002/Story10-RH4Y-peak-accounting-1.csv')[0]
one=next(r for r in eight if r['Case']=='RH4X')
selected=[one,ten]
def tt(r,k):return float(r[k])
peaktable=['|量|第8层RH4X|第10层RH4Y|','|---|---:|---:|']
for label,key in [('基准峰时t_B/s','t_B_s'),('实际方案峰时t_D/s','t_D_s'),('基准原峰/kN','B_signed_at_tB_kN'),('实际方案原峰时读数/kN','D_signed_at_tB_kN'),('基准在实际方案峰时读数/kN','B_signed_at_tD_kN'),('实际方案自身峰/kN','D_signed_at_tD_kN'),('原峰时降低/kN','old_direction_signed_weakening_S_kN'),('重新取峰比原峰时读数高/kN','own_peak_selection_recovery_M_kN'),('最终峰降低/kN','P_B_minus_P_D_kN'),('原峰时评价/%','r_at_percent'),('完整时程峰减幅/%','r_D_peak_percent')]:
 vals=[f'{tt(r,key):.2f}' if key in ['t_B_s','t_D_s'] else f'{tt(r,key):.4f}' for r in selected]
 peaktable.append('|'+label+'|'+'|'.join(vals)+'|')
qdtable=['|楼层/输入|QD(t_B)/kN|QD(t_D)/kN|QD自身绝对峰/kN|tQD/s|剪力峰时绝对值/自身峰/%|','|---|---:|---:|---:|---:|---:|']
for r in selected:
 qdtable.append('|'+r['Story'].replace('Story','第')+'层/'+r['Case']+'|'+'|'.join(f'{tt(r,k):.4f}' for k in ['QD_signed_at_tB_kN','QD_signed_at_tD_kN','P_QD_abs_kN'])+f"|{tt(r,'t_QD_s'):.2f}|{tt(r,'QD_abs_at_tD_over_own_peak_percent'):.4f}|")
# Preserve the old fixed-linear and three-story discussions in a separate appendix, outside actual-scheme mechanism claims.
linear=old.split('### 5.2 ',1)[1].split('## 6 ',1)[0]
annex='''# 补充A 线性叠加机制与实际模态恢复资料

本补充保留前版固定300阶线性参照和人工三层模型材料。它们不作为正文实际D方案的逐阶剪力。正文5.2已改为实际B/D响应、控制时刻与装置力。

## A1 原线性机制材料

### '''+linear+'''
## A2 本轮实际模态恢复尝试

实际读取D和B六方向工况各108个CM时程组，以同一actual300阶振型及方向质量计算2/13阶质量加权观测投影；旧线性前向q_ref只用于检验投影混叠，没有作为实际q。

- [实际模态坐标恢复诊断](roles/modal/实际模态坐标恢复诊断.md)
- [B/D同基观测投影](roles/modal/B-D观测投影补充对照.md)
- [第2/13阶投影峰12行](roles/modal/BD-common-basis-projection-peaks-12.csv)
- [两个控制时刻投影8行](roles/modal/BD-common-basis-two-control-anchors-8.csv)
- [恢复契约独审](roles/audit/q-recovery-contract.md)

RH4X第13阶观测投影在21.66s由B的−23.6061变为D的−15.3038，而在21.60s由−23.3221变为−24.4232，变化方向随所比较时刻不同。投影正负也不是楼层剪力正负，不能据某一个时刻保留旧“第13阶反号导致剪力减幅小”的结论。

完整质量内积/实际q和目标剪力恢复尚未齐备。本轮给出了实际运动的可检查投影进展，没有把投影与原生FNA坐标或逐阶力混称。后续闭合路线及缺项列于诊断和独审；不把瞬时观测秩不足扩大为所有时间域方法都不可能。
'''
# Source appendix paths originally were relative to manuscript directory; retarget them for this supplement directory.
for label,path in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',annex):
 if path.startswith('../../../'):
  target=(src.parent/path).resolve();newpath=Path(__import__('os').path.relpath(target,S)).as_posix();annex=annex.replace(']('+path+')',']('+newpath+')')
ap=S/'补充A-线性机制与实际模态恢复.md';assert not ap.exists();ap.write_text(annex,encoding='utf-8',newline='\n')
text=old
text=text.replace('两输入层剪峰时的装置水平合力绝对值分别为装置自身峰的58.6736%和63.4488%。原峰时评价的减幅高估量最大为10.5831个百分点。','两输入层剪峰时的装置水平合力绝对值分别为装置自身峰的58.6736%和63.4488%。') if False else text
text=text.replace('两条记录在楼层剪力峰时的装置水平合力绝对值分别为装置自身峰的58.6736%和63.4488%。增加3个百分点模态阻尼的14工况结果用于扩展对照，固定线性参照用于说明主导模态项与反向抵消的不同作用。','RH4Y第10层的实际控制时刻由16.62s变为21.64s，两时刻原有需求接近，但降低量不同，使原先略低的时段转为控制。装置水平合力的自身峰与楼层剪力控制峰分别保留；14工况模态增阻尼结果仅作扩展对照。')
text=text.replace('The simultaneous damper horizontal-force magnitudes are 58.6736% and 63.4488% of their respective peaks. Fourteen directional cases with three additional percentage points of modal damping provide an extended comparison, and a fixed linear reference illustrates changes in dominant modal terms and cancellation.','At Story 10 under RH4Y, the governing time changes from 16.62 to 21.64 s. Demand at these two times is initially similar, but unequal reductions make the previously lower response govern. Damper-force peaks are checked separately from story-shear peaks, while the 14 directional modal-damping cases provide an extended comparison.')
text=text.replace('增加3个百分点模态阻尼的14工况结果作为扩展对照；固定300阶线性参照和三层模型仅用于解释主导模态项下降、反向抵消变化与局部剪力的关系。','增加3个百分点模态阻尼的14工况结果作为扩展对照；通过实际模型在两个控制时刻的响应及装置出力，说明原控制峰降低后，另一个接近峰如何转为控制。')
text=text.replace('第5节用固定经典阻尼线性参照解释叠加作用，其中的模态项不作为实际非线性方案的原生逐阶剪力。','第5.2节直接比较实际B/D模型控制时段及装置出力。第2、13阶实际坐标的恢复另作有限诊断，观测投影与真实模态坐标的区别见[模态恢复补充](../../../research/sessions/20261103-1853/补充A-线性机制与实际模态恢复.md)。')
start=text.index('### 4.3 ');end=text.index('### 4.4 ',start)
new43='''### 4.3 实际方向下的装置水平合力

第8—11层共有24个楼层—工况组，每组8只装置的保存时间与楼层输出逐点一致。各主方向有4只装置的水平投影非零，按实际方向逐只合成；同一轴力的I/J重复列示只计一次。取单位向量n由I指向J，轴力P按原生正拉力约定，QD=Σn_eP表示J端结构内力抵抗项，装置施加于J节点的外力为−QD。

装置力分别在基准剪力峰时、实际方案自身峰时和装置合力峰时查看。它们对应的原生剪力与装置力见第5.2节；完整第8层六工况及追加一例的三时刻数据见[实际控制时段附表](../../../research/sessions/20261103-1853/实际控制时段与完整附表.md)。装置力用于同刻传力检查，与软件楼层剪力分别列示。

'''
text=text[:start]+new43+text[end:]
text=text.replace('**表6 实际方案原峰时评价与自身峰减幅的对照**','**表5 实际方案原峰时评价与自身峰减幅的对照**')
text=text.replace('![图4 实际方案原峰时评价偏差]','![图3 实际方案原峰时评价偏差]').replace('图4 实际方案72条成对记录','图3 实际方案72条成对记录')
text=text.replace('## 5 模态增阻尼对照与叠加机制','## 5 控制输入对照与实际峰值变化')
start=text.index('### 5.2 ');end=text.index('## 6 ',start)
actual52=r'''### 5.2 实际方案控制峰变化与装置出力时序

本节直接比较实际方案D与基准B的原生时程，不再用模态增阻尼参考解释实际方案。先保留第8层六工况的全部三时刻对照，再在第8—11层具有完整装置出力的24条记录中，取峰时迁移最大的第10层RH4Y作为控制时段变化例；第8层RH4X则用于说明两峰相距很近时的读数差别。表6与图4分别列出两条记录。

**表6 两条实际记录的原峰降低与自身控制峰**

@PEAKTABLE@

第8层RH4X的基准峰为21.66s的+6263.40kN，实际方案同刻降为+5528.21kN，降低735.20kN。但其自身峰在21.60s达到+5776.65kN，比原峰时读数高248.45kN，最终峰降低486.75kN，减幅7.7713%。两时刻只差0.06s，仍应取实际方案自身峰，而不是把接近的峰时视为完全相同。

第10层RH4Y的控制时段变化更明显。基准在16.62s为+4277.28kN，在21.64s仍有+4167.68kN，两个时刻仅差109.60kN。实际方案在前一时刻降为+2815.53kN，在后一时刻为+3395.92kN。原控制时刻降低1461.75kN，后一时刻降低771.76kN，前者降低得更多，使原先略低的时段转为实际方案的控制时段。两状态在这些时刻均为正剪力，此例不是正负峰号切换。

用两时刻的绝对值可写清这一关系。令t₁=t_B、t₂=t_D，b_i=|V_B(t_i)|、d_i=|V_D(t_i)|，δ_i=b_i−d_i为该时刻的降低量，则：

$$d_2-d_1=(\delta_1-\delta_2)-(b_1-b_2).$$

当两时刻降低量之差大于原需求差时，后一时刻在实际方案中更大。对第10层RH4Y，降低量之差689.99kN超过原需求差109.60kN，故实际方案在21.64s比16.62s高580.39kN。原峰时的34.1747%减幅因此回落为完整峰值减幅20.6055%，相差13.5692个百分点。该关系直接核对已得到的两状态时程，说明控制时刻为何重新选择。

![图4 实际方案原峰降低与控制时刻变化](../../../research/sessions/20261103-1853/roles/response/R003/actual-B-D-QD-two-records.png)

图4 两条实际记录的B/D楼层剪力与装置水平合力QD。左为第8层RH4X，右为第10层RH4Y，均保留0—50s完整保存时程；灰、蓝、橙虚线分别标t_B、t_D和QD自身峰时。上行纵轴为±8000kN，下行为±500kN；空心点为实际方案在基准峰时的读数。QD为J端结构内力抵抗项，装置对节点外力为−QD。

**表7 两条实际记录的同刻装置出力**

@QDTABLE@

第10层RH4Y的装置合力自身绝对峰411.91kN发生在16.46s；原剪力峰时16.62s仅为−111.21kN，实际方案自身峰时21.64s为−258.22kN。后两者绝对值分别为装置自身峰的26.9989%和62.6884%。第8层RH4X也有相同的检查必要：装置合力峰在11.50s，而剪力控制时刻在21.60s附近。

因此，装置最大出力、原剪力峰时出力和实际方案自身峰时出力应分别保留。控制时段的剪力降低既不能用装置自身峰直接代替，也不能仅由某一个同刻QD值解释。实际曲线说明了不同时段降低程度不同，以及原有接近峰重新控制的过程；具体模态作用还需由实际运动与一致的剪力恢复关系核查。第2、13阶的实际质心运动投影及恢复诊断见[补充资料](../../../research/sessions/20261103-1853/补充A-线性机制与实际模态恢复.md)。

'''.replace('@PEAKTABLE@','\n'.join(peaktable)).replace('@QDTABLE@','\n'.join(qdtable))
text=text[:start]+actual52+text[end:]
text=text.replace('第8层RH4X和SHW7X的剪力峰时装置水平合力绝对值，分别为装置自身峰的58.6736%和63.4488%。','第8层RH4X和第10层RH4Y的剪力峰时装置水平合力绝对值，分别为装置自身峰的58.6736%和62.6884%。')
old5='固定线性参照表明，主导模态项较大与反向抵消减弱是不同的叠加作用；其机制用于指导检查实际方案自身的模态运动，不代替实际非线性响应的分解。'
new5='第10层RH4Y在两个时刻的原需求仅差109.60kN，实际降低量却分别为1461.75kN和771.76kN，差异超过原需求差，使21.64s转为控制。工程解释应回到实际两状态的竞争时段，并继续核查对应运动与装置出力。'
assert old5 in text;text=text.replace(old5,new5)
assert text.count('**表')==7 and len(re.findall(r'\$\$.*?\$\$',text,re.S))==5
assert len(re.findall(r'!\[',text))==4
assert '参照第13阶项/kN' not in text and '689.99kN' in text
assert text.split('## 参考文献\n\n',1)[1]==old.split('## 参考文献\n\n',1)[1]
for target in re.findall(r'\]\(([^)]+)\)',text):
 if not target.startswith(('http://','https://')) and '实际控制时段与完整附表.md' not in target:assert (out.parent/target).resolve().is_file(),target
out.write_text(text,encoding='utf-8',newline='\n')
record={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'source':src.relative_to(R).as_posix(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output':out.relative_to(R).as_posix(),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'tables':7,'display_equations':5,'figures':4,'main_5_2_uses_actual_data_only':True,'linear_mechanism_moved_to':ap.relative_to(R).as_posix(),'actual_modal_projection_not_called_actual_q':True,'new_values_sources':['roles/response/Story8-actual-peak-accounting-6.csv','roles/response/R002/Story10-RH4Y-peak-accounting-1.csv'],'references_unchanged':True}
(S/'draft-v001-build.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
