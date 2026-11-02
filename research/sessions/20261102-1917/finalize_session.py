from pathlib import Path
import datetime,json,hashlib,subprocess,sys
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,obj): (S/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
freeze=json.loads((S/'roles/role5/R004/freeze.json').read_text(encoding='utf-8'))
word=Path(freeze['docx']);assert sha(word)==freeze['docx_sha256']=='1b8063e1599c94a312eb96c29aa8cc50a3bb8bac8b2adce0b477269517492431'
qa=json.loads((S/'root-word-all-pages-review.json').read_text(encoding='utf-8'));assert qa['pages_actually_viewed']==list(range(1,10)) and qa['word_sha256']==sha(word)
put('root-final-word-adoption.json',{'at':now,'author_freeze':'roles/role5/R004/freeze.json','word_sha256':sha(word),'source_sha256':freeze['manuscript_sha256'],'root_actual_all_pages':True,'root_independent_identity_gate_passed':True,'author_partial_QA_preserved':True,'author_finite_task_overrun_preserved':True,'approval':'Readable scientific review manuscript. Minor title line balance remains; not certified submission-ready. No layout mutation after full root render.'})
text=f'''# P06工程主线最终总结

本轮固定窗口为2026-11-02 19:17:23—21:47:23+08。科学工作已提前停止；交付验收记录时间为{now}，未延长研究窗口。最终行政关闭时间见status.json与自动化回执。

## 取得的结果
新增24组楼层—方向双控制工程表，关联已有168条成对记录。19/24组中，减幅最小的输入与参考模型剪力需求最大的输入不同。因此工程复核应分别保留两条完整记录，而不是只看底层、各层平均值，或把不同输入的数字拼成一行。

第5层X向：SHW3X减幅最小，为6.8513%；SHW4X控制最大参考剪力9027.7451kN，其自身减幅11.3022%。工程流程明确先看逐层改善，再另查绝对需求及两模型各自峰时附近曲线。新表经独立审核6415字段0must，新稿与附表502显示数值通过；正确性、来源、工程三项最终审查完成。

## 最终交付
- 科学正文：papers/damping-output-boundaries/manuscript/p06-engineering-session022-v003.md，25712B，SHA256 b546eb7e9afe6dfde8f8bc57f705ee6e283b60141000a408965d39921fffdac3。
- Word：papers/damping-output-boundaries/manuscript/p06-engineering-session022-论文审阅稿-v003.docx，651399B，SHA256 {sha(word)}，9页。
- 完整工程附表：roles/role5/R002/engineering-data-and-full-tables.md，含24组48条用途记录与资料说明。
- 普通中文入口：普通中文研究说明.md；真实投稿待办：投稿前待办.md。

## 实际Word验收
作者21:40:18冻结，个人只看完1—4页且有限任务逾时的记录完整保留。主控独立对同一字节只读快照重新渲染，实际看完全部9页，核对5张可编辑表100个数值格、43个原生公式对象、原生矩阵、3张原图散列及附件链接。公式未发现漏项；跨页表有重复表头。标题末行仅两字，保留为轻微版面不足，当前交付为可读科学审阅稿，不称排版毫无瑕疵或可直接投稿。

## 真实未决
作者姓名单位待本人。官网10条建议与官方模板至少20/大于20及期刊比例条款不一致，当前10条均有支持但不认全部投稿合规；详见来源更正。完整M/K、事件缩放和内部积分步等元信息仍有缺项。软件Bottom剪力未扣成真实主体剪力；实体装置模型只作独立出力时序说明。14方向工况非14独立事件；d是保存网格评价差值。三层人工H2后验删阶仅作机制说明。

## 同步及行政
R000—R006均普通白名单同步并核远端；R006为123fccf6aa0b87dcab6700884efec4ac923807ae。最终交付及自动化回执由新FINAL检查点同步，真实结果见git-FINAL-receipt.json。R005根JSON首字多加号及R006标准diff空白检查失败均已如实保留修复记录，未修改冻结作者diff、未强推或覆盖旧工作。仅本轮小文件/新稿Word进入白名单，原始数据、缓存、第三方全文、评测目录与旧脏文件均排除。

本轮p06-150已正式暂停并实际读回，旧git/automation-3/automation-4均保持PAUSED。最终删除回执及实际不存在验证另存。没有ETABS/YJK/API、付费、投稿或外部联系。
'''
(S/'final-summary.md').write_text(text,encoding='utf-8')
status=json.loads((S/'status.json').read_text(encoding='utf-8'));status.update({'phase':'delivery-accepted-administrative-close','current_task':'Scientific and Word deliverables frozen; final Git and automation deletion only','delivery_accepted_at':now,'checkpoint_open':False})
status['word_task'].update({'Word_QA_passed':True,'author_personal_QA_incomplete':True,'root_independent_all_pages_reviewed':True,'docx_sha256':sha(word),'cosmetic_title_issue_retained':True,'formal_completion_not_observed':False})
status['automation']['state']='PAUSED';put('status.json',status)
(S/'rounds/FINAL.md').write_text('# 最终交付检查点\n\n'+now+'：同一冻结字节9页经根独立实际查看；100表格数值/43原生公式/3图通过。作者个人QA未完成和逾时记录保留。科学已停，仅行政收束与普通白名单同步。\n',encoding='utf-8')
print(json.dumps({'accepted_at':now,'word_sha256':sha(word),'ready_for_final_git':True}))
