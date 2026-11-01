from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-CLOSE-publication.json').exists()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
release=json.loads((S/'git-FINAL-receipt.json').read_text(encoding='utf8'));assert release['remote_equals_local']and not release['pending_push']
auto=json.loads((S/'final-automation-closeout.json').read_text(encoding='utf8'));assert auto['future_wakeups_stopped']and not auto['actual_toml_exists_after_delete']
assert json.loads((S/'root-final-word-r2-visual-QA.json').read_text(encoding='utf8'))['approved_for_delivery']
d=json.loads((S/'status.json').read_text(encoding='utf8'));d.update(phase='closed-completed',checkpoint='CLOSE-completed',checkpoint_open=False,last_actual=now,closed_at=now,closure_reason='Authorized research and document goal completed before fixed upper deadline; no further peripheral tasks',automation='git-2 formally PAUSED and viewed/read back, then formally deleted; actual TOML absent; future wakeups stopped',next_task=None)
d['git']={'release_HEAD':release['HEAD'],'release_remote_verified':True,'release_receipt':'git-FINAL-receipt.json','administrative_checkpoint':'CLOSE','administrative_receipt':'git-CLOSE-receipt.json'}
js(S/'status.json',d)
summary=(S/'final-summary.md').read_text(encoding='utf8')
start=summary.index('## 关闭记录')
summary=summary[:start]+f'''## 关闭记录

实际行政关闭时间{now}。六角色全部实际idle，无在途科学或文档任务。最终成果已普通commit/push并核远端等于本地，发布提交{release['HEAD']}，回执git-FINAL-receipt.json。行政状态与回执的末次同步见git-CLOSE-receipt.json。

git-2已正式设PAUSED、正式view并读取实际TOML确认后，正式delete成功；实际配置文件已不存在，未来唤醒停止。工具回执见final-automation-tool-receipts.json、final-automation-closeout.json。旧git、automation-3、automation-4均实际PAUSED，历史窗口未恢复。

本轮未操作ETABS/YJK求解器、未索取新数据或读取凭据、未上传原Excel/EDB、完整时程、大数组、外部论文全文或任何local-cache；12个历史tracked脏文件与未知5E-07保持。当前交付不是已投稿稿件，也未填作者身份。实际完成早于原截止，没有把空余时间伪装成连续科研。
'''
(S/'final-summary.md').write_text(summary,encoding='utf8')
for name in ['普通中文研究说明.md','工程应用方法.md']:
 p=S/name;text=p.read_text(encoding='utf8');text+='\n\n本轮已实际结束。成果已同步GitHub，定时唤醒已正式删除；实际关闭时间'+now+'。\n';p.write_text(text,encoding='utf8')
close={'actual_closed_at':now,'science_and_document_completed_at':d['research_and_document_completed_at'],'fixed_deadline':d['deadline'],'early_complete':True,'all_six_roles_idle':True,'approved_word':'papers/damping-output-boundaries/manuscript/damping-prediction-session021-论文审阅稿-v010-r2.docx','approved_word_sha256':'9d1a1963cb27d0d49f19295a3411e7fa87530e44afb19141a6bcddd324b37530','release_commit':release['HEAD'],'release_remote_verified':True,'automation_delete_actual_verified':auto,'final_admin_git_receipt':'git-CLOSE-receipt.json','no_remaining_scientific_or_document_tasks':True}
js(S/'final-closeout-receipt.json',close)
with(S/'runs.md').open('a',encoding='utf8')as f:f.write('\nCLOSE '+now+': final release commit '+release['HEAD']+' remote verified. Formal automation PAUSED/view/actual-read then delete succeeded; actual config absent, historical three PAUSED. Research and document goal achieved early; all roles idle. Only this administrative record commit remains, no science resumed.\n')
(S/'rounds/CLOSE.md').write_text('# CLOSE 实际关闭\n\n'+now+'。本轮成果与Word最终版已核、六角色全部实际idle，正式自动化已先暂停及读回再删除，未来唤醒停止。此提交仅把真实关闭状态与工具回执同步，不包含新科学、原件或中间缓存。发布提交见git-FINAL-receipt.json，行政末次提交见git-CLOSE-receipt.json。\n',encoding='utf8')
names=['close_session.py','status.json','runs.md','final-summary.md','普通中文研究说明.md','工程应用方法.md','final-closeout-receipt.json','rounds/CLOSE.md','git-FINAL-receipt.json','final-automation-pause-actual.json','final-automation-tool-receipts.json','final-automation-closeout.json']
files=[S/n for n in names]
js(S/'git-CLOSE-publication.json',{'checkpoint':'CLOSE','time':now,'message':'research: record completed paper delivery and verified automation shutdown','files':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(files)]})
print(json.dumps({'closed_at':now,'release_commit':release['HEAD'],'automation_deleted':True,'files':len(files)}))
