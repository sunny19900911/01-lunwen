from pathlib import Path
import datetime,json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
md='papers/damping-output-boundaries/manuscript/p06-actual-main-session026-v003.md'
docx='papers/damping-output-boundaries/manuscript/p06-actual-main-session026-论文审阅稿-v003.docx'
hashes={md:'2aae66c26effa5c5436cd0b08cb883ead63d5f0ed12ffd88f47a9400a24cc370',docx:'a1a935b7f485c656b3e633c349b686fa9795a6d4caadbb47bae087c531cb964f'}
for p,h in hashes.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
qa={'passed':True,'at':now,'reviewer':'root','docx':docx,'docx_sha256':hashes[docx],'source':md,'source_sha256':hashes[md],
    'render':'word/local-cache/render-v003','pages':11,'actual_pages_viewed':list(range(1,12)),
    'editable_tables':7,'table_numeric_cells_checked':210,'native_OMML':43,'display_equations':5,'figures':4,
    'marker_success_count':1,'structural_gate':'word-identity-v003.json',
    'visual_observations':['11页均original-detail实际查看，标题、双语摘要和分栏阅读顺序可读。','第3页布置和配置表、第5页实际减幅图表、第6页双控制和装置力表、第7页时程及偏差表、第8页实际偏差散点均与源一致且无裁切重叠。','式1—4保留PD与PB及AD，选择式的rD/PD、式5的φ和q操作数完整；串联参数单位原生公式可读。','参考文献9在第10—11页连续排印，文本完整；第11页仅参考文献收尾，未见丢行。'],
    'render_method':'Canonical attempted; actual missing LibreOffice log retained, independent hidden Word COM and bundled PDFium completed. Only task-owned objects closed.'}
(S/'final-visual-review.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary=f'''# 实际方案为主的最终稿

实际完成时间：{now}。用户最新批准的“实际方案为工程主体、原模态参照作辅助”已完成。本轮没有新的后台任务或预算窗口。

## 交付

- MD：`{md}`，29375B，SHA256 `{hashes[md]}`。
- Word：`{docx}`，527193B，SHA256 `{hashes[docx]}`。
- Word共11页，7张可编辑表、210个数值单元格、5独立公式、43原生公式对象、4张原图已核；根实际查看最终全部11页。
- 完整工程表：`工程资料与完整附表.md`，保留72条及24组索引和范围。

## 这轮新增的实际数据

两份既有原生Story Forces缓存只读取B/D对应的72个主方向Bottom组，各自保存时间逐点一致，峰值及峰时与旧已审72表完全一致。新计算实际方案原峰时评价，不使用M参考值；独立实现从缓存核1728字段一致，汇总分位也独立排序核过。

实际减幅3.1238%—47.6719%。底层只在2/6方向工况恰是改善最小层；SHW7Y第6层减幅16.0082%，底层30.2486%、十二层平均27.1508%，分别高14.2404/11.1426个百分点。改善与需求控制不同12/24组；第8层RH4X与SHW7X的两类记录和原生同刻装置力保留。

实际d中位3.658646、95%19.705140、最大34.679005个百分点。最大RH4Y第12层：PB565.0421kN、PD523.5629kN；原峰时读数给42.0199%改善，自身完整峰只7.3409%，峰时20.22→12.26s。比例偏差大不等于该层绝对需求最大或最危险。

## 文章主次与解释

引言、双语摘要、模型、方法、工程结果、步骤及结论已重写为实际72条主体。公式1—4用D/B；真实布置提前至第2章。原14工况168条、19/24组移至第5节扩展，与同六M7/24分清。原固定300阶线性参照和人工三层例仅用一节机制及一段目标模态检查说明，不冒充实际非线性各阶分担。

必要背景/内部设置范围及QT与QD口径仍短写，详细记录放附表。未将模型数值写成现场实测；没有把全楼88几何和32只完整原生力范围混淆。完整实际非线性逐阶分解仍需其自身q与力恢复关系，本轮没有伪称闭合。

## 审核、失败与保留

数值/范围终审must0、方法终审must0。两项可选精确性修订已落实：原生逐阶剪力措辞；参照误差的分母和未舍入数据。均未改变科学数字。

最初脚本因末尾多一个换行触发参考文献字节断言，在写新稿前停止；修正拼接后参考条目原文不变。documents说明路径首次访问错误已改为tasks/create_edit.md。canonical渲染真实缺少LibreOffice，日志保留后用安全独立WordCOM/PDFium完成，未绕过策略或关闭用户Word。marker本任务只成功一次。

全部旧稿和旧会话原字节保留。没有求解器、模型API、新ODE、拟合或原大Excel读取；原件与大数组只读。

## Git同步

R001已正常提交并核远端一致：e03eb3b27ee587f08d749385607c7b85fb2800cd。最终白名单同步以`git-FINAL-receipt.json`的remote_equals_local/pending_push为准。只包含本轮已冻结小文件、新稿及通过QA的最终Word，不含任何local-cache、原件或旧脏文件；无强推或凭据访问。
'''
(S/'final-summary.md').write_text(summary,encoding='utf-8',newline='\n')
(S/'rounds/FINAL.md').write_text(summary,encoding='utf-8',newline='\n')
(S/'普通中文修改说明.md').write_text('''# 论文这次怎样推进了

现在工程主体已经是实际88只阻尼器方案。先用已有六个方向工况的72条完整响应，而不是把尚未取得的其他实际工况补成168条。原14工况的模态阻尼参考移到后面作扩展对照，线性模态分析保留用来讲明叠加机制。

这次不只是换章节顺序。我们直接从基准和实际方案的已有完整缓存里，算出了实际方案“只在原峰时读数会漏掉多少”。RH4Y第12层的例子最清楚：原峰时看起来减了42.02%，完整时程实际只减7.34%。所以检查时必须打开两种模型各自的峰附近，而不能只盯原来的最大时刻。

另一个实际结果是SHW7Y：底层减了30.25%，第6层却只减16.01%。只看底层和平均值，会把较弱改善藏起来。文章现在将“每层看改善范围、分别选两条控制输入、再检查各自峰时和装置出力”写成明确步骤。

第8层的RH4X与SHW7X仍是实际布置—剪力—装置出力联系起来的主例。原13阶的抵消解释保留在明确的线性参照中，不把它说成已经分解出的实际非线性第13阶力。

最终Word11页，公式和表格可编辑，全部页面已实际查看。工程数值和方法两项独审均无必须修改问题，两项精确性建议也已采纳。
''',encoding='utf-8',newline='\n')
(S/'claims.md').write_text('''# 最终主张

- C01 supported/reviewed：实际D/B六方向72条为正文主体，24组两类控制不同12组；旧M168/19组及同六M7组仅扩展对照。
- C02 supported/reviewed：实际逐层范围已派生24组、六工况底层/平均对照独算；底层仅2/6取最小。SHW7Y改善最小第6层与底层/平均差14.2404/11.1426pp。
- C03 supported/reviewed：完整B/D缓存各72组，保存轴全同，独核1728字段。实际d中位3.658646、95%19.705140、最大34.679005pp（RH4Y第12层）。不用旧M最大10.5831pp。
- C04 supported有限：背景模态阻尼与非线性装置分别描述；固定300与人工三层仅机制说明，不当D真实逐阶。实际q及恢复关系仍为后续缺口。
- C05 supported/reused：88几何/32只完整出力沿1458已审结果；J端nP内力抵抗项与外力反号，不物理扣QT求QS。
- C06 supported/reviewed：最终科学源v003，11页Word全部实际查看，210数值表格单元、43OMML及4原图身份通过。
''',encoding='utf-8',newline='\n')
with (S/'runs.md').open('a',encoding='utf-8',newline='\n') as f:f.write(f'\n{now}：实际响应生产及独审均完成，数值1728字段一致；最终稿两项精确性修订后v003冻结。marker一次，Word结构检查及全部11页实际查看通过。R001已核远端，下一最终白名单同步见正式receipt。\n')
st=json.loads((S/'status.json').read_text(encoding='utf-8'));st.update({'phase':'closed-complete','closed_at':now,'checkpoint_open':False,'final_manuscript':md,'final_word':docx,'final_word_sha256':hashes[docx],'visual_QA':'final-visual-review.json','final_git_receipt':'git-FINAL-receipt.json','remaining_work_in_approved_revision':[],'remaining_scientific_scope_limits':['实际六工况，不是14实际工况','实际q与剪力恢复未完整闭合','完整内部模型设置及QT包含口径沿配对范围保留']});(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'closed_at':now,'pages':11,'final_word':docx,'QA_passed':True},ensure_ascii=False))
