from pathlib import Path
import datetime,hashlib,json,re
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
md='papers/damping-output-boundaries/manuscript/p06-actual-timing-session027-v004.md'
docx='papers/damping-output-boundaries/manuscript/p06-actual-timing-session027-论文审阅稿-v004.docx'
hashes={md:'f56b44fc5172778261364253e69eb8fa324f97af148e0fdd968e50b3dbe15a71',docx:'85350fbecf951a17e39e4e37f0394dc947237351ef6f24be895898b08fa5dc68'}
for p,h in hashes.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
links=[]
for p in [R/md,S/'补充A-线性机制与实际模态恢复.md',S/'实际控制时段与完整附表.md']:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  if target.startswith(('http://','https://')):continue
  q=(p.parent/target).resolve();assert q.is_file(),str(q);links.append({'from':p.relative_to(R).as_posix(),'to':q.relative_to(R).as_posix()})
(S/'final-link-check.json').write_text(json.dumps({'at':now,'all_links_exist':True,'checked':links},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
qa={'passed':True,'at':now,'reviewer':'root','source':md,'source_sha256':hashes[md],'docx':docx,'docx_sha256':hashes[docx],'docx_bytes':554281,
 'render_directory':'word/local-cache/render-v004','pages':10,'actual_pages_viewed':list(range(1,11)),
 'editable_tables':7,'numeric_table_cells_checked':191,'native_OMML':51,'display_equations':5,'figures':4,'structural_gate':'word-identity-v004.json','marker_success_count':1,
 'visual_observations':['最终10页均original-detail实际查看，无文字/图表裁切或重叠。','第8页实际B/D/QD新图及表6完整；第9页实际两时刻δ恒等式、同刻QD表和工程步骤可读，所有操作数完整。','旧11页版本第8页为容纳后续大图留下约5cm空白；仅将不变的图4和图注移至表6前，最终10页更紧凑，未缩小字体或图。','第10页参考文献跨栏连续排印，文字完整；作者身份未伪造，表/公式可编辑。'],
 'render_method':'Actual canonical attempt failed missing LibreOffice, retained log; independent task-owned hidden Word COM plus bundled PDFium succeeded. No execution-policy bypass or closing user Word.'}
(S/'final-visual-review.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary=f'''# 实际5.2节与模态恢复推进结果

实际交付关闭时间：{now}。本轮完成实际5.2改写、独审、Word全页QA；实际q恢复仍有真实数据缺口，未宣称已完成真实第2/13阶剪力分担。无新后台自动化或历史窗口恢复。

## 最终稿

- MD：`{md}`，29311B，SHA256 `{hashes[md]}`。
- Word：`{docx}`，554281B，SHA256 `{hashes[docx]}`。
- 10页，7可编辑表、191个数字单元、51原生公式对象、5独立公式、4原图核过；最终10页全部实际查看。
- 完整实际时段记录：`实际控制时段与完整附表.md`。
- 原线性机制与恢复诊断：`补充A-线性机制与实际模态恢复.md`。

## 实际5.2节已经完成

旧第5.2的SHW3X/SHW4X固定300线性项及人工三层例移到补充A；4.3与5.2重复的装置时序内容合并。现5.2直接对照实际B/D在两个控制时刻的QT与原生QD，摘要、引言及结论同步更新；原72/12组主体和14参考168/19组范围保持。

第8层全六三时刻先冻结；发现其最大峰时差仅0.22s，因此未强写大时段换峰。根据旧已核完整P第8—11层24项客观筛选最大峰移，追加RH4Y第10层，B16.62s→D21.64s为5.02s。图并列近原峰的第8层RH4X与第10层RH4Y，两条都是同号正峰。

第10层原控制时刻B4277.2798→D2815.5314kN，21.64s则B4167.6790→D3395.9230kN。原需求只差109.6008kN，降低量分别1461.7485和771.7560kN，差689.9925kN超过原需求差，故后一选定时刻在D中更高580.3917kN。两时刻恒等式独审残差0，用于核对已知响应，不是输入前预测或模态/相位因果份额。

该例原峰时评价34.1747%，完整峰减幅20.6055%，差13.5692pp。QD自身411.9139kN发生16.46s，在tB/tD分别−111.2123/−258.2223kN，分别为自身峰26.9989%/62.6884%。装置自身峰与两剪力控制时刻分开检查，不扣QT创造主体QS。第8层RH4X相应原峰降低735.1953kN、重新取峰回升248.4451kN、净峰降486.7502kN。

新实际21行三时刻及7组关系，独立读原缓存核591字段完全一致；两项新表45字段和正文终审must0。两类措辞精确化（t2而非时间“后一”；补充表A1/A1.2）已采用；布局重排不改数字、公式、表和图。

## 第2/13阶恢复实际做了什么

实际读取D六工况108个CM组及B对应108组，以actual300同基、已审方向质量和广义质量作2/13阶质量加权观测投影q_obs。未用剪力拟合、缩放、移时或新ODE。检查Gram：2阶本对角0.962748、13阶0.992053，但混叠仍存在；旧已知q_ref理想观测测试曲线误差约3.14%—7.14%，不能当作实际D误差界。

B/D投影峰12行、两个指定剪力控制时刻8锚点已冻结。例如RH4X第13阶投影在21.66s由−23.6061→−15.3038，在21.60s由−23.3221→−24.4232；变化方向不同，不能选一个时刻保留旧“第13阶反号导致减幅小”。投影符号也不能直接认作剪力同反向。算法/定义已独立短核，审核者未冒称重算全部CM。

未发现直接actual FNAq。20261019“有控全节点.xlsx”实际为262062B几何四表（3416点/88连接），不是全节点模态/时程；20261021Joint三表仅表头，5400行仍是18CM×300，后续缓存未增加全节点向量。本次仅读已有headers/报告/stat，没有重复读取原大Excel。

要把投影升级为真实q及逐阶剪力，仍需直接实际坐标或完整同源位移+MΦ投影；动力恢复路线则需完整非线性广义力、对应有效刚度补偿/背景阻尼/初态/输入。目前完整原生P32/88、端点模态映射及目标剪力恢复不足。瞬时rank36不被扩大成所有时间域恢复都不可能；本轮不继续无数据约束的回归或重做300阶实验。

## Git及保留

R001已正常提交并核远端相同：5680f7096a1a6f6f0f1b0683f7b6412580c8b25e。最终白名单同步结果以`git-FINAL-receipt.json`的remote_equals_local/pending_push为准。只收当前会话冻结小件及本轮稿和最终通过QA的Word，不收任何local-cache、原件、全时程数组、第三方全文或旧脏文件。无强推/模型API/求解/收费/投稿/凭据访问；全部旧稿保留。
'''
(S/'final-summary.md').write_text(summary,encoding='utf-8',newline='\n');(S/'rounds/FINAL.md').write_text(summary,encoding='utf-8',newline='\n')
(S/'普通中文修改说明.md').write_text('''# 这次完成到哪一步

5.2节现在全部来自实际方案。它把两件事讲清：原来的控制峰已经明显下降，不代表完整时程的减幅也同样大；另一处原本接近的响应可能因为降低得较少而转为控制。

第10层RH4Y就是实际例子：原来16.62s为4277.28kN，21.64s为4167.68kN，两者本来只差109.60kN。设置装置的方案在这两个时刻分别降低1461.75和771.76kN，前者下降得更多，所以实际方案转由21.64s控制。原峰时34.17%的改善，最终只对应20.61%的峰值改善。

正文配了真正的基准/实际两条曲线，以及实际装置合力，在原峰、实际方案峰和装置自身峰三个时刻分别看。原第8层近峰例也保留，避免只选峰移大的记录。

第2、13阶恢复不是只作文字讨论：已经从实际CM时程算了两阶运动投影、检查其他阶混叠，并和已有已知坐标的参照测试。但投影还不是完整实际模态坐标，不能据此保留真实第13阶反号或逐阶剪力结论。实际第13阶投影在两个控制时刻的变化方向也不同。所有这些实数留在补充资料，旧线性例没有再替实际模型说话。

这轮已完成实际5.2和一次有限恢复诊断。真实模态坐标及剪力合成仍需直接q或完整同源位移与MΦ/力恢复关系，现有几何和CM资料未补上这一项。最终Word10页，全部页面已实际检查，数据与文字独审均无科学必改问题。
''',encoding='utf-8',newline='\n')
(S/'claims.md').write_text('''# 最终主张

- C01 supported/reviewed：Story8六工况18同刻行及新增Story10RH4Y3行、7组关系独审591字段一致；QT和QD均原生，不物理扣为QS。
- C02 supported/reviewed：第10层RH4Y是完整P24项中最大峰移5.02s；两时刻原需求差109.6008kN、降低量差689.9925kN，D两时刻差580.3917kN，恒等关系独审残差0；不是输入前预测或装置单因果。
- C03 completed-diagnostic/unresolved-q：已实际处理B/D各108CM组，得到2/13观测投影及Gram/已知参考误差/12峰8锚点；混叠未消除，不是已恢复actual FNAq。真实2/13剪力结论未采用。
- C04 unresolved：完整质量内积或非线性广义力及对应目标剪力恢复尚不足；旧rank36不否定所有动力恢复路线。全节点旧文件确为几何资料，未漏已有完整q。
- C05 supported/reviewed：主5.2只用实际B/D与QD；旧线性300和三层移补充；摘要结论同步。最终10页Word全部实际查看，191数字单元/51OMML/5公式/7表/4图通过。
''',encoding='utf-8',newline='\n')
with (S/'runs.md').open('a',encoding='utf-8',newline='\n') as f:f.write(f'\n{now}：实际5.2、恢复诊断、资料可用性与两类独审完成。旧11页Word全看后发现图前空白，移动不变图4至表6前，最终10页全部实际查看通过；marker仅一次，结构gate通过。q/真实逐阶剪力仍有缺项，未伪称恢复完成。R001已远端核等，最后同步见正式receipt。\n')
st=json.loads((S/'status.json').read_text(encoding='utf-8'));st.update({'phase':'closed-delivered-with-modal-gap','closed_at':now,'checkpoint_open':False,'final_manuscript':md,'final_word':docx,'final_word_sha256':hashes[docx],'visual_QA':'final-visual-review.json','final_git_receipt':'git-FINAL-receipt.json','actual_5_2_completed':True,'actual_q2_q13_recovered':False,'modal_observation_projection_completed':True,'true_modal_shear_reconstruction_verified':False,'remaining_scientific_items':['直接actual q或完整位移及MΦ质量投影','若用动力恢复则完整非线性广义力及实际动力设置','与软件Bottom一致的目标剪力恢复关系'],'remaining_delivery_work':[],'no_new_numeric_experiments':True,'no_new_scientific_dispatch':True});(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'closed_at':now,'pages':10,'final_word':docx,'QA_passed':True,'actual_q_recovery_still_unresolved':True},ensure_ascii=False))
