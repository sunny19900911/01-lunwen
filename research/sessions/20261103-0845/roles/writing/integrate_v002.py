from pathlib import Path
import datetime,hashlib,json,difflib,re,csv
HERE=Path(__file__).resolve().parent;R=HERE.parents[4];S=HERE.parents[1]
SRC=R/'papers/damping-output-boundaries/manuscript/p06-sh3-sh4-session023-v001.md'
DST=SRC.with_name('p06-sh3-sh4-session023-v002.md')
assert not DST.exists()
old=SRC.read_text(encoding='utf-8');assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='75aaecf467284add1a15709eca6c182cdff750d0e13ced05cf95b21ef60bef43'
adopt=json.loads((S/'root-R001-adoption.json').read_text(encoding='utf-8'));assert adopt['must_numeric']==0
audit=json.loads((S/'roles/audit/R001/results.json').read_text(encoding='utf-8'))
alg=json.loads((S/'roles/audit/R001-algebra-addendum.json').read_text(encoding='utf-8'));assert alg['must']==0
rows=audit['states'];pair=[next(x for x in rows if x['Case']==c and x['zeta']==.08) for c in ['SHW3X','SHW4X']]
def signed(v):return f'{v:+.2f}'.replace('-','−')
fields=[('软件剪力绝对峰/kN','native_peak_abs_kN',False),('软件峰时/s','native_peak_time_s',False),('参照合成/kN','reference_at_native_peak_signed_kN',True),('参照第2阶项/kN','reference_mode2_kN',True),('参照第10阶项/kN','reference_mode10_kN',True),('参照第13阶项/kN','reference_mode13_kN',True)]
table='|量|SHW3X|SHW4X|\n|---|---:|---:|\n'
table_rows=[]
for label,key,sgn in fields:
 vals=[signed(x[key]) if sgn else f'{x[key]:.2f}' for x in pair]
 table+='|'+ '|'.join([label]+vals)+'|\n';table_rows.append({'row':label,'source_field':key,'values':vals})
new=old
for a,b in [('表5','表6'),('表4','表5')]:new=new.replace(a,b)
old_section=new[new.index('### 4.2 SHW3X与SHW4X的第5层辅助对照'):new.index('### 4.3 原峰时评价的偏差')]
section='''### 4.2 SHW3X与SHW4X的第5层辅助对照

Liu等通过指定响应的传递函数辨认重要模态，表明不同响应量需要分别考察模态作用[2]。经典阻尼体系中的目标输出可由模态输出系数与相应动态响应在同一时刻合成[7]。据此，对SHW3X和SHW4X下第5层的软件剪力峰作辅助核查。

采用在18个质心集中方向质量条件下识别的质量，配合300阶Ritz模态数据，建立固定经典阻尼线性参照。表4列出参照阻尼取8%时，两输入各自软件峰时的参照项；软件峰值取绝对值，参照项按参照方向保留符号。参照与工程模型的完整设置对应、切口恢复关系及软件正方向尚未逐项核实，这些项仅用于辅助比较，不视为原生软件剪力的唯一逐阶分解。四状态数据和计算条件见[辅助分析资料](../../../research/sessions/20261103-0845/roles/writing/SHW3X-SHW4X-辅助分析资料.md)。

**表4 第5层软件峰值与8%阻尼固定300阶线性参照的有符号项**

'''+table+'''
SHW4X在自身峰时的参照第2阶项大于SHW3X，第10阶项反而较小，第13阶为很小的反向项。因此，这组参照没有出现第10、13阶同向叠加主导SHW4X较高峰值的现象。两列比较的是不同输入在各自峰时的组成，不能将其差额解释为同一时刻的因果分担；绝对需求仍按表2的软件成对峰值复核。

'''
new=new.replace(old_section,section)
anchor='前一条用于查看改善较小的时段，后一条用于查看较大需求；不能把6.8513%的减幅标在9027.7451kN需求上。'
assert new.count(anchor)==1
sentence=f'从两条记录本身看，SHW4X的基准剪力比SHW3X高{100*(alg["baseline_SH4_over_SH3"]-1):.2f}%；增加模态阻尼后，其减幅虽较大，参考剪力仍高{100*(alg["reference_SH4_over_SH3"]-1):.2f}%。改善比例与绝对需求因而需要分别查看。'
new=new.replace(anchor,anchor+sentence)
supp='''# SHW3X与SHW4X第5层辅助分析资料

## 分析对象与用途

本文P06的工程评价仍采用同一输入下软件基准与增加3个百分点模态阻尼参考模型的成对楼层底部剪力。这里补充比较SHW3X与SHW4X在第5层各自控制峰附近的条件线性参照，以检查第10、13阶同向增强是否伴随SHW4X较高峰值。它不是原生逐阶内力导出，也不把其他楼层或人工三层模型的高阶结果移用于本例。

## 固定参照与数据来源

参照采用20261031-1130/R004已保存的四份因子化数组，质量由R002在18个隔板质心集中方向质量假定下识别，再结合实际300阶LinModRitz形状、频率及广义质量形成固定空间系数B；B不是由楼层剪力拟合得到。每项采用Bω²s/1000，单位为kN，s为相同输入下零初态、统一经典阻尼的单位参与响应。这里没有新求解ODE、没有重新拟合输出，也没有提取原始大表。

参照与P06基准—参考模型的完整质量、刚度和设置身份尚未逐项核对；18个质心集中质量对完整有限元模型的覆盖、Ritz切口的弹性力恢复及软件Bottom VX正方向仍有条件。四个控制峰处原生剪力为负，参照合成为正，故正文把软件绝对峰和参照自身有符号项分列，不依据幅值吻合选择符号。

## 四状态对照

下表均在该输入、该状态自身的软件绝对峰时刻取值。软件峰取绝对值，参照项为有符号值，单位kN。

|输入|阻尼状态/%|软件峰时/s|软件绝对峰/kN|参照合成/kN|参照第2阶/kN|参照第10阶/kN|参照第13阶/kN|
|---|---:|---:|---:|---:|---:|---:|---:|
'''
for x in rows:
 supp+='|'+ '|'.join([x['Case'],f'{100*x["zeta"]:.0f}',f'{x["native_peak_time_s"]:.2f}',f'{x["native_peak_abs_kN"]:.4f}',f'{x["reference_at_native_peak_signed_kN"]:+.4f}',f'{x["reference_mode2_kN"]:+.4f}',f'{x["reference_mode10_kN"]:+.4f}',f'{x["reference_mode13_kN"]:+.4f}']).replace('-','−')+'|\n'
supp+='''
四状态完整绝对值曲线的相对均方误差定义为100×||abs(V_ref)−abs(V_native)||₂/||V_native||₂；相应数值按SHW3X的5%、8%及SHW4X的5%、8%顺序为0.028441%、0.012329%、0.156387%、0.085873%。绝对峰误差分别为+0.001962%、+0.002450%、−0.028725%、+0.008059%。这些结果用于检查幅值对应，不将其转为有符号力身份或原生逐阶分解的证明。

## 与工程主线的联系

SHW4X基准剪力比SHW3X高17.1021%；两条输入各自增加阻尼后，虽SHW4X减幅11.3022%大于SHW3X的6.8513%，其绝对剪力仍高11.5066%。两条记录的自身峰差分别为595.4876kN和1150.3464kN，分母及峰时都保留各自输入身份。

8%状态下，第4—300阶参照项合计由SHW3X的512.8402kN降为SHW4X的321.8105kN，第2阶项则大990.9192kN；这只描述两输入各自峰时的组成，不能称第2阶解释了某个百分比的真实因果差额。当前参照不支持所检验的第10、13阶同向主导解释；它也不排除其他输入、楼层或完整结构中的高阶作用。

## 可追溯的小表与文献

- [独立四状态小表](../audit/R001/independent-story5-four-states.csv)
- [第5层四状态全300项参照小表](../audit/R001/independent-story5-all300-at-native-peaks.csv)
- [独立数字及方法核查](../audit/R001/正确性与数字独审.md)
- [已有文献原页定位](../literature/R001-source-review.md)

正文沿用Liu等2004[2]关于按目标响应辨认模态作用，以及Song等2008[7]关于经典阻尼体系模态静力输出与动态核组合的已有方法。它们提供解释框架，不直接给出本工程SHW4X的原因。全部详细数据仅用于辅助说明，P06中心仍是逐层、多输入以及改善与绝对需求分别保留控制记录。
'''
SUP=HERE/'SHW3X-SHW4X-辅助分析资料.md';assert not SUP.exists()
block=lambda s:re.findall(r'(?:^\|.*\n)+',s,re.M)
assert len(block(old))==5 and len(block(new))==6
assert [b for i,b in enumerate(block(new)) if i!=3]==block(old)
assert re.findall(r'\$\$[\s\S]*?\$\$',new)==re.findall(r'\$\$[\s\S]*?\$\$',old)
assert re.findall(r'!\[[^\]]*\]\([^)]+\)',new)==re.findall(r'!\[[^\]]*\]\([^)]+\)',old)
assert new[new.index('## 摘要'):new.index('## 1 引言')]==old[old.index('## 摘要'):old.index('## 1 引言')]
assert new[new.index('## 7 结论'):]==old[old.index('## 7 结论'):]
SUP.write_text(supp,encoding='utf-8',newline='\n')
DST.write_text(new,encoding='utf-8',newline='\n')
(HERE/'v001-to-v002.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=SRC.name,tofile=DST.name)),encoding='utf-8')
report={'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'stage':'R002 reviewed auxiliary integration','source':str(SRC),'target':str(DST),'target_bytes':DST.stat().st_size,'target_sha256':hashlib.sha256(DST.read_bytes()).hexdigest(),'supplement':str(SUP),'supplement_bytes':SUP.stat().st_size,'supplement_sha256':hashlib.sha256(SUP.read_bytes()).hexdigest(),'new_table_rows':table_rows,'mainline_peak_comparison_sentence':sentence,'old_five_tables_equations_figures_unchanged':True,'abstract_conclusions_references_unchanged':True,'new_display_equations':0,'Word_created':False,'marker_run':False}
(HERE/'R002-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
