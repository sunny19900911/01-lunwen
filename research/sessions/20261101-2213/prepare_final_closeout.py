from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
doc=M/'damping-prediction-session021-论文审阅稿-v010-r2.docx'
assert hashlib.sha256(doc.read_bytes()).hexdigest()=='9d1a1963cb27d0d49f19295a3411e7fa87530e44afb19141a6bcddd324b37530'
render=S/'roles/role5/R014/local-cache/render-v1'
pages=[{'page':i,'path':str(render/f'page-{i}.png'),'sha256':hashlib.sha256((render/f'page-{i}.png').read_bytes()).hexdigest(),'actual_root_visual_review':'clean; no blocking clipping, missing math operand, table/figure split or unreadable citation observed'}for i in range(1,17)]
js(S/'root-final-word-r2-visual-QA.json',{'reviewed_at':now,'docx':str(doc),'docx_sha256':hashlib.sha256(doc.read_bytes()).hexdigest(),'all16pages_actually_viewed':True,'pages':pages,'key_page6':'U=sum_r p_r and P=max_t|sum_r v_r(t)| both complete, in native OMML and actual final page image','key_page9':'Predicted P and D hats visible in error definitions','key_page14':'Envelope maxima retain P operands','independent_identity_check':'root-final-word-r2-identity.json passed','approved_for_delivery':True,'previous_word':'Preserved locally, not approved or uploaded; omission and repair history retained','renderer':'Canonical render actually failed for absent soffice, then own hidden Word COM and bundled PDFium, final images actually reviewed; no execution-policy change'})
plain=(S/'普通中文研究说明-prepared-v001.md').read_text(encoding='utf8')
plain=plain.replace('本文稿与Word终审、渲染和实际关闭时间尚待完成。本文件为交付说明预备稿，不表示任务已经结束。','最终正文v010和16页可编辑Word已完成。作者与主控分别逐页查看最终版，两个行内公式转换漏项已修复；数学公式、表格、图及链接检查通过。实际研究与文档交付完成时间为'+now+'。正式自动化关闭和最终Git核验另存关闭回执。')
plain+='\n\n最终Word：[论文审阅稿v010-r2](<'+doc.as_posix()+'>)。\n'
(S/'普通中文研究说明.md').write_text(plain,encoding='utf8')
guide=(S/'工程应用方法-prepared-v001.md').read_text(encoding='utf8')
guide=guide.replace('本文件依据已独审结果整理，主稿与Word仍待最终成稿检查。实际非线性阻尼器对应的等效模态阻尼需在工程采用前另行确定。','本文件依据已独审结果与最终正文v010整理，可配合已完成逐页检查的Word使用。实际非线性阻尼器对应的等效模态阻尼需在工程采用前另行确定。')
(S/'工程应用方法.md').write_text(guide,encoding='utf8')
summary=f'''# 六小时授权窗口研究实际完成总结

本轮研究与最终文档于{now}实际完成，提前于2026-11-02 04:13:31+08的固定截止收束。授权窗口从2026-11-01 22:13:31起算，没有重置或延长；没有声称满六小时连续执行。随后仅作最终Git与自动化行政关闭。

## 可用结果

已建立基准5%响应之后的工程提前判断流程：用阻尼导数计算各层峰值改善敏感度S，按同一总峰时的各阶促进与抵消解释原因，再用候选完整预测历程和误差区间决定排除、通过或完整复算。理论和数值均经过独立检查，旧终版的物理系数、幅值与叠加机制已整合入新稿。

解析关系S=SU+SC把各阶自身峰值总和的变化与合成比例变化接起来。SHW3X第5层4.643−2.511=2.132，屋顶6.373+5.351=11.724，说明幅值下降与叠加变化为何产生不同楼层降幅。第13阶在第5层自身峰下降却削弱总峰时的原有抵消，两个时刻和归一化分母分开使用。

工程三条输入最大峰包络、全层至少下降10%的示例中，6%和7%候选可排除，8%和10%仍需完整复算。参照最小降幅分别为9.228100%和14.634810%，均第7层控制。逐输入全部达标与最大峰包络达标是不同目标。RH4X单输入7%二阶可确认全12层达到原定要求，不代替三输入判断。

## 最终交付

- 正文：[damping-prediction-session021-v010.md](<{(M/'damping-prediction-session021-v010.md').as_posix()}>),39606B，SHA64ee1567ee775cdcf30aa28734ae0bb5003706970fddb708d5fa3afb648c942d。
- Word：[论文审阅稿v010-r2](<{doc.as_posix()}>),591348B，SHA9d1a1963cb27d0d49f19295a3411e7fa87530e44afb19141a6bcddd324b37530。16页，15个可编辑表块、10个编号独立公式、112个原生OMML对象、3张已审图；4个真实外部链接及本地S1入口。
- 补充说明S1：roles/role5/R012/supplement-S1.md；工程使用步骤见工程应用方法.md，普通中文说明见普通中文研究说明.md。

Word曾在独立根复核中发现两处行内求和操作数遗漏，旧版已保留并拒收；最终r2修复后重新渲染，作者和主控分别实际查看全部16页，增强OOXML及253数字单元格检查通过。canonical renderer缺LibreOffice的真实失败日志保留，使用自有隐藏Word和捆绑PDFium完成渲染，未改执行策略、未操作用户文档。marker成功一次，没有因修订重跑。中间渲染文件只留local-cache。

## 证据与真实未决

共有两个固定线性模型、四组模型—输入、39个基准楼层—输入组合；312项单输入预测比较，另96项三输入包络区间。工程8%是旧已知参照，其他新目标按先冻结预测再求参照执行；相关楼层和候选不冒充独立事件。

保留局部排序反转、二阶有时更差、简单统一系数部分指标更优、区间过宽需要复算及当前总成本高于直接求解。研究没有把已有直接微分和Taylor基础称首创，没有给出期刊录用概率或速度优势。

方法目前适用于固定M/K/输入及统一经典模态阻尼的线性模型。实际Maxwell装置的等效模态阻尼、全FE恢复算子条件及实际FNA逐阶响应唯一性仍未一并闭合。S是局部指标，有限增量和控制峰变化由完整历程及区间继续判断。误差区间对应所用保存网格与数值约定。

## 关闭记录

六角色科学任务均已结束，未重启历史会话、未索取新数据、未运行ETABS/YJK求解器、未上传原Excel/EDB或大数组。原有脏文件和未知5E-07保持。最终正常白名单Git及远端SHA记录见git-FINAL-receipt.json；自动化正式暂停、view、实际配置与删除工具回执见final-automation-closeout.json。实际行政关闭时间在final-closeout-receipt.json中记录；本行在关闭前不预报工具成功。
'''
(S/'final-summary.md').write_text(summary,encoding='utf8')
d=json.loads((S/'status.json').read_text(encoding='utf8'));d.update(checkpoint='R013-complete',checkpoint_open=False,last_actual=now,phase='closing-completed-deliverables',research_and_document_completed_at=now)
d['git'].update(last_HEAD='9b79a9b0636780363bc55e81f20bbe1d68205626',remote_equals_local=True,receipt='git-R013-receipt.json')
d['current_tasks']={k:'Frozen idle; complete; no new dispatch'for k in d['current_tasks']}
d['document_status']='Final r2 Word approved after enhanced OMML identity check and root actual review of all16finalpages; p_r/v_r and hats preserved. Scientific sources unchanged.'
d['next_task']='Only final approved-artifact Git checkpoint, formal pause/view/actual-config verification/delete automation, actual closeout receipt. No science, writing or rendering remains.'
js(S/'status.json',d)
with(S/'claims.md').open('a',encoding='utf8')as f:f.write('\nC021-delivery-reviewed '+now+': final v010 scientific manuscript and r2 editable Word complete; root actual16page review plus enhanced operand and source identity checks passed. Old failed inline-math document preserved locally and not published. Scientific scope and known negative results unchanged.\n')
with(S/'runs.md').open('a',encoding='utf8')as f:f.write('\nFINAL preparation '+now+': all scientific and document work complete. R014 r2 frozen01:43:12, root actual16page final visual review and enhanced identity checks passed. Only final Git and formal automation shutdown remain; no further budget-filling research.\n')
print(json.dumps({'actual_completed_at':now,'approved_word':str(doc),'pages':16,'ready_for_final_git':True},ensure_ascii=False))
