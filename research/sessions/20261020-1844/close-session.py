"""Administrative closure only. No experiments or source-document edits."""
from pathlib import Path
import json,hashlib,datetime,tomllib,zipfile
S=Path(__file__).resolve().parent; R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
source=R/'papers/damping-output-boundaries/manuscript/modal-shear-session009-v010.md'
word=R/'papers/damping-output-boundaries/manuscript/modal-shear-session009-论文审阅稿-v010.docx'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='0d9fc8d6fb1e4f9e52613ab4f82b7338a3990b79fb98505ee1f99562c15ce7df'
assert hashlib.sha256(word.read_bytes()).hexdigest()=='591978e4488897e3e01de6a922e431b9a3a4e47e5826fcea5915ec151c6845bc'
configs={}
for name in ['automation-5','git','automation-3','automation-4']:
    data=tomllib.loads((Path('C:/Users/mj528/.codex/automations')/name/'automation.toml').read_text('utf-8'))
    configs[name]={k:data.get(k) for k in ['id','status','rrule','target_thread_id']}
    assert data['status']=='PAUSED'
write(S/'final-automation-readback.json',{'checked_at':now,'configs':configs,'formal_tool_receipts':'final-tool-receipts.json','toml_read_only':True})
pages=S/'roles/role5/local-cache/R011-v010/pages-v2'
qa={'recorded_at':now,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'word_sha256':hashlib.sha256(word.read_bytes()).hexdigest(),'page_count':9,'master_actually_viewed_pages':list(range(1,10)),'method':'Each final PNG displayed with view_image during preceding master turn; no new rendering or content edits at closure.','result':'No clipping, overlap, missing mathematical glyphs or broken tables seen. Figure 1 kept readable at original size; preceding-page whitespace accepted. All four references on page 9.','images':[{'page':i,'sha256':hashlib.sha256((pages/f'page-{i:02}.png').read_bytes()).hexdigest()} for i in range(1,10)]}
write(S/'root-final-word-QA.json',qa)
receipts=json.loads((S/'final-tool-receipts.json').read_text('utf-8'))
pollmap={p['role']:p for p in receipts['polls']}
v=json.loads((S/'status.json').read_text('utf-8'))
for r in v['roles']:
    p=pollmap[r['role']];r.update(cursor=p['cursor'],actual_status=p['thread']['status'],turn_status=p['latestTurn']['status'],task='finished_no_new_dispatch')
v.update(phase='closed-budget',closed_at=now,scientific_deadline='2026-10-20T21:44:25+08:00',administrative_closure_late=True,checkpoint_open=False,no_new_experiments=True,no_new_scientific_dispatch=True,canonical_manuscript=source.relative_to(R).as_posix(),canonical_word=word.relative_to(R).as_posix(),canonical_word_sha256=qa['word_sha256'],word_QA='root-final-word-QA.json',automation_actual_config=configs,final_git_status='pending_final_checkpoint',final_summary='final-summary.md')
write(S/'status.json',v)
t=json.loads((S/'threads.json').read_text('utf-8'));t['roles']=v['roles'];t['last_checked_at']=now;write(S/'threads.json',t)
with (S/'claims.md').open('a',encoding='utf-8') as f:f.write('\nC018 final reviewed：v010保持数值、公式、图及原文引用；必改意见已处理。Word9页、8表3图、13组原生数学对象，经作者和主控逐页实际查看。真实建筑精确模态剪力、三态完整模型对应及层剪包含性仍未认证。\nC008/C012/C013审核状态以后续review条目为准，早期candidate记录保留。\n')
with (S/'runs.md').open('a',encoding='utf-8') as f:f.write('\n最终行政收束 '+now+'：科研截止仍为2026-10-20 21:44:25。Word作者21:43:11冻结；主控已逐页查9页。行政关闭实际迟至本记录时间，不把间隔计为科研循环，不重开预算。自动化正式暂停及配置回读成功。最终Git结果见git-FINAL-receipt.json。\n')
summary=(S/'final-summary-prepared.md').read_text('utf-8')
summary+='\n## 最终交付与真实关闭\n\n最终Word为papers/damping-output-boundaries/manuscript/modal-shear-session009-论文审阅稿-v010.docx，755329字节，SHA256 '+qa['word_sha256']+'。最终9页，8张可编辑表、3幅图、13组原生数学结构；作者及主控已实际逐页查看1—9页。参考文献集中第9页，图1为保可读性保留前页留白。无后缀Word只是10页预览，最终交付使用-v010。\n\n作者最终冻结于2026-10-20 21:43:11，超过12分钟单项预算的记录保留；科研硬截止未延长。行政收束真实时间为'+now+'，并非准时关闭。当前六角色最新回合均completed，部分聊天notLoaded，不能把notLoaded伪写成active或idle；没有重新派研究。\n\n自动化automation-5已通过正式update设PAUSED，正式view及只读实际配置回读确认；旧git/automation-3/automation-4仍PAUSED。工具回执与配置见final-tool-receipts.json、final-automation-readback.json。\n\n最后一次常规Git检查点状态由git-FINAL-receipt.json记录；本总结先于该检查点写入，不预先宣称推送成功。最终用户交付以实际receipt为准。\n'
(S/'final-summary.md').write_text(summary,'utf-8')
(S/'rounds/R007-final.md').write_text('# 最终行政收束\n\n'+now+'，不再开展科学研究。最终v010及9页Word已核并冻结，六角色回合完成，自动化暂停实配核验。最小科学缺口保留于final-summary及普通中文研究说明。进行一次明确白名单Git同步，结果见git-FINAL-receipt.json。\n','utf-8')
print(json.dumps({'closed_at':now,'word':str(word),'automation':configs},ensure_ascii=False))
