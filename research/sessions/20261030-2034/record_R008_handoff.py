from pathlib import Path
import json,datetime,ast
S=Path(__file__).resolve().parent
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
st=json.loads((S/'status.json').read_text(encoding='utf-8'));p=json.loads((S/'git-R007-receipt.json').read_text(encoding='utf-8'))
assert p['pending_push'] and p['HEAD']=='499025d006544f27e4119b2a541b88ba7bb2c35f'
st.update(last_actual=now,recovery_file='rounds/R008-close-handoff.md',phase='delivery-frozen-await-budget-close',no_new_scientific_dispatch=True)
st['git'].update(publication='R007 local commit pending: GitHub Internal Server Error twice; final R008 may retry normal push',pending_push=True,pending_local_HEAD=p['HEAD'],last_success_HEAD=p['remote_HEAD'],last_success_receipt='git-R006-receipt.json',pending_receipt='git-R007-receipt.json')
st['next_checkpoint']='No new science/Word edits. At or after22:34:43 final-summary actual close, formalpause/view/config and delete completed automation, final scoped GitR008. To resume exact pending Git commit set manifest resume_pending_receipt=research/sessions/20261030-2034/git-R007-receipt.json; publisher verifies unchanged remote and ancestor. No force/credentials.'
(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(S/'rounds/R008-close-handoff.md').write_text('''# 最终行政收束交接
真实22:23左右，唯一两小时窗口20:34:43—22:34:43，不重算。六角色均已实际idle，scientific dispatch关闭；作者22:16:35冻结v005，根完整读MD并实际查看7页Word渲染图，25可编辑公式/4表/2图检查通过。最终MD SHA f0e4e9fe37ba80920da016dcdded9284c2e86ef224366af1d11b3808dee264fd；DOCX SHA638e0f5d152c0e216f138250abd0f402c55e1f157229461842fb6da9de62658a。不得重开研究/排版/重复审核。
重要同步失败：R007已本地commit499025d006544f27e4119b2a541b88ba7bb2c35f，但GitHub服务器两次Internal Server Error（非凭据/冲突），远端仍R00630bdc6f2b63723eae7dd44bf854734735e7ee293。当前新稿/Word只本地和本地提交，不可宣称远端已同步。最终R008再按新检查点最多一次正常push及一次重试；publisher已支持精确R007 pending receipt + unchanged remote + ancestor校验，不强推/等登录/读凭据。manifest必须填resume_pending_receipt为本session/git-R007-receipt.json，不覆盖历史失败receipt。若远端变更或仍500，保留本地待推并真实汇报。
到22:34:43后：据final-summary-prepared-v001和root-final-document-QA生成final-summary.md，含真实关闭时间/最终Word与普通中文入口/主线已达与真实逐层物理分担缺口；当前无最小新增数据索取，不要求用户再给表。正式automation_update暂停5、view、读取实际TOML核状态并保存回执，然后按最新heartbeat规则删除已完成automation5并保存实际回执。旧git/3/4只读核仍PAUSED。status closed-budget，最后R008明确白名单Git包括新稿已提交的父提交与小行政记录；最终receipt本地保存后核远端SHA，不为自指SHA反复提交。
最终用普通中文说明：同增阻尼的模态响应比变化已核、全12层降幅差异与控制峰迁移已核；各层真实逐阶物理分担仍未闭合，不能用拟合巨项冒充。Word是7页可编辑审阅稿，不是投稿认证。只交Word和必要说明链接，QA中间PDF/PNG不交用户。正式收束真实逾时如有必须记录，不延科研。
''',encoding='utf-8')
ast.parse((S/'publish_checkpoint.py').read_text(encoding='utf-8'))
print(json.dumps({'saved':now,'pending_push':True,'Word_ready':True},ensure_ascii=False))
