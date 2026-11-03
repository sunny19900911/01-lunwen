from pathlib import Path
import datetime,json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,o):(S/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=json.loads((S/'roles/writing/R003-Word-freeze.json').read_text(encoding='utf-8'))
word=Path(f['word']);assert sha(word)==f['word_sha256']=='df41034546824b89c1d43eb5fe59eb660a432bbce5d6f8dfb048e99e135e55a8'
assert len(f['pages'])==10
for p in f['pages']:assert sha(Path(p['path']))==p['sha256']
for p in json.loads((S/'roles/writing/R003-shareable-manifest.json').read_text(encoding='utf-8'))['files']:assert sha(Path(p['path']))==p['sha256']
marker=json.loads((S/'roles/writing/local-cache/marker-receipt.json').read_text(encoding='utf-8'));assert marker['exit_code']==0 and marker['success_count']==1
for p in json.loads((S/'input-manifest.json').read_text(encoding='utf-8')):assert sha(R/p['path'])==p['sha256'],p['path']
qa={'reviewed_at':now,'word_sha256':sha(word),'word_bytes':word.stat().st_size,'root_pages_actually_viewed_original':list(range(1,11)),'page_hashes_verified':10,'identity_gate':'root-final-word-identity.json','native_editable_tables':6,'numeric_table_cells':115,'native_OMML':43,'display_equations':5,'unchanged_original_figures':3,'marker_success_count_verified':1,'blocking_issues':[],'nonblocking_notes':['Page6 lower whitespace before full-width figure2; original labels retained readable.','Last references page naturally has unused right column.'],'title_orphan_fixed':True,'new_signed_reference_table_and_conditions_clear':True,'author_and_root_independent_visual_review_completed':True,'submission_compliance_not_claimed':True}
put('root-final-word-visual-review.json',qa)
put('git-R001-remote-recovery.json',{'verified_at':now,'read_only_ls_remote_exit_code':0,'HEAD':'45b2e70166dcbea3357f94ac54669039609d45e2','remote_HEAD':'45b2e70166dcbea3357f94ac54669039609d45e2','remote_equals_local':True,'initial_receipt_preserved':True,'no_repush_for_verification':True,'earlier_TLS_failures':'git-R001-verification-issue.json'})
status=json.loads((S/'status.json').read_text(encoding='utf-8'));assert not status['checkpoint_open']
status.update({'phase':'final-delivery-accepted','current_task':'Scientific manuscript and10page Word accepted; final normal sync then pause/readback/delete automation only.','delivery_accepted_at':now,'no_new_scientific_dispatch':True,'Word_QA_passed':True})
status['word']={'path':word.relative_to(R).as_posix(),'bytes':word.stat().st_size,'sha256':sha(word),'pages':10,'root_all_pages_actually_viewed':True}
status['git'].update({'remote_verification_pending':False,'pending_push':False,'remote_verified':True,'remote_recovery':'git-R001-remote-recovery.json'});put('status.json',status)
t=json.loads((S/'threads.json').read_text(encoding='utf-8'))
for a in t['agents']:a.update({'actual_status':'completed','task':'R003 Word frozen and root accepted' if a['role']=='writing' else 'Frozen; all assigned finite work completed','last_actual':now})
put('threads.json',t)
summary=f'''# P06 SHW3X／SHW4X辅助机制核查最终总结

固定窗口2026-11-03 08:45:53—11:15:53+08，150分钟为上限，未恢复旧窗口。实际成果验收时间{now}。研究问题、稿件与全页QA已完成，随后仅行政收束和最后正常同步；不为用满预算另扩题。实际关闭时间及自动化回执见status与关闭记录。

## 回答与工程主线
P06仍以逐层、多输入、同输入成对记录为中心，保留19/24组最小减幅与最大参考剪力控制输入不同的结论。新增正文仅4.1一句原生峰对照、4.2一辅助小节一紧凑表及2.3用途说明，摘要/题名/首要贡献不转向模态机制。原5表数据、5独立公式、3原图、摘要结论与10引用均保持，表序顺延。

SHW3X第5层由8691.64降至8096.15kN，减幅6.85%；SHW4X由10178.09降至9027.75kN，减幅11.30%。SHW4X基准需求高17.10%，参考需求仍高11.51%。应各自保留输入/成对峰值/各自峰时，不能混配改善比例与需求。

固定300阶线性参照不支持第10、13阶同向主导SHW4X较高峰值：8%参照中，第10阶项309.55小于506.93kN，第13阶为−1.68kN的小反向项。第2阶参照项较大，但未据此声称原工程已证第2阶唯一因果。18CM识别质量、Ritz恢复、旧D完整模型对应及软件方向条件邻表保留；两输入各自峰的比较不是共同物理时刻的因果分摊。

audit独立实现复算64字段通过，最大浮点差2.19e−11，明确非盲核；最终文字/表格审查40个新增数字格通过，must0，2should和2optional精确澄清已采纳，未更改数字。文献角色实际重看Liu印刷81—85、Song105—109共10页，复用已有目标响应分析，未漫搜或新增下载。历史Liu表7末行误读另记更正、不改旧报告。

## 交付入口
- 科学MD：papers/damping-output-boundaries/manuscript/p06-sh3-sh4-session023-v003.md，27706B，SHA a16f4e6893f4f96b94ed5ef312f4b396682db68c254b104345bbadb22b21a310。
- 可编辑Word：papers/damping-output-boundaries/manuscript/p06-sh3-sh4-session023-论文审阅稿-v003.docx，652641B，SHA {sha(word)}，10页。
- 辅助资料：roles/writing/SHW3X-SHW4X-辅助分析资料-v002.md，3754B，SHA dbfa620a7f389fd667ede28589dedf3c26333b8a3a549ae2bec16bf6572260af；含四状态、误差定义、源条件和完整300项入口。
- 原完整24组工程表继续使用旧022已审附表；新旧均有真实链接。普通中文入口为普通中文研究说明.md。

## 实际Word验收
作者09:27:21冻结，marker09:23:50成功一次；canonical真实缺LO日志保留后安全独立hidden Word COM/PDFium渲染，无策略绕过或kill用户Word。作者与主控均实际查看最终10页，主控另执行OOXML/数字/原图/新旧链接身份gate：6可编辑表、115数值格、43原生公式对象含5display和K矩阵，3原图SHA保持，作者元数据空。标题孤行已修，表3和新表4整表可读；page6因下一原图完整显示留底部余白，末参考页右栏自然留白，无裁切或漏项。最终字节未再修改。

## 真实未决与过程
实际工程原生逐阶剪力身份仍未闭合，不能把低绝对幅值误差当因果认证。作者资料及官方参考数量要求差异等旧投稿待办仍未解决，当前交科学审阅稿，不称完整投稿合规。无新ODE/拟合/布局/CM修补/原大表/求解器/费用/投稿/外联。

作者R002脚本首次表插入索引错误已保留未采用自有草稿于cache，校验前置后再写正式稿；原稿和科学数字未改。根一次补件路径、审核者一次文献路径只读错误如实记录。

R000同步a265f9f4efde03a5f96732aa79fe948e95e5269e远端已核。R001 45b2e70166dcbea3357f94ac54669039609d45e2推送退出0，随后TLS核验失败；后续正常只读lsremote已确认远端同SHA，原失败回执保留，未重复推送作核验。最终新稿Word与关闭回执按后续正式Git receipt记录，不预报同步成功。白名单排除raw/cache/大数组/第三方全文/模板/评测目录/旧dirty，未强推/reset/改全局或读凭据。
'''
(S/'final-summary.md').write_text(summary,encoding='utf-8')
(S/'rounds/R002.md').write_text('# 最终成果验收\n\n'+now+'：v003精确契约通过；作者与根均实际看10最终页，根115数字/43OMML/3图/全部链接gate通过。数据/原文/工程正文已完成，不再科学派工。仅最后正常Git、正式暂停核回读删除自动化。R001 TLS核验已恢复同远端SHA，失败原记录保留。\n',encoding='utf-8')
(S/'next-task.md').write_text('# 只余关闭\n\n'+now+' 最终MD/Word/补充已验收，科学全部停。先核status/checkpoint_open，完成最后正常白名单Git；正式pause/view/实际TOML读回再delete p06-sh3-sh4-150，旧git/automation3/4保持PAUSED。保存实际关闭时间和回执，不恢复科研。不重跑旧receipt。\n',encoding='utf-8')
print(json.dumps({'accepted_at':now,'all10pages_reviewed':True,'word_sha256':sha(word),'initial_inputs_unchanged':True}))
