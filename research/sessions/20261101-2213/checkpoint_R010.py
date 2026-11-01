from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R010-publication.json').exists()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
snap=json.loads((S/'R010-actual-snapshot.json').read_text(encoding='utf8'))
t=json.loads((S/'threads.json').read_text(encoding='utf8'))
tasks={'role1':'Frozen idle; science complete','role2':'R013 one final v009 correctness review, no ODE or old numeric reruns','role3':'R004 one final citation/source consistency review, existing evidence only','role4':'Frozen idle; science complete','role5':'R0118min Word builder/preflight preparation; no DOCX or marker before final review adoption','role6':'R009 one final engineering prose and operational workflow review'}
for x in t['threads']:
 z=next(y for y in snap if y['role']==x['role']);x.update(cursor=z['cursor'],actual_status=z['status'],task=tasks[x['role']],last_actual=now)
js(S/'threads.json',t)
d=json.loads((S/'status.json').read_text(encoding='utf8'))
d.update(checkpoint='R010-complete-final-review-candidate',checkpoint_open=True,last_actual=now,current_tasks=tasks,recovery_file='rounds/R010.md')
d['next_task']='Collect one final correctness/source/engineering-language review, formally adopt necessary corrections; sole author revises and builds editable Word. Canonical renderer first, own hidden Word COM fallback without execution-policy change if needed, all final page PNGs actually viewed. No new scientific cases.'
js(S/'status.json',d)
with(S/'runs.md').open('a',encoding='utf8')as f:f.write('\nR010 '+now+': v009 author froze00:58:30, root actual complete diff/new-section/QA/manifest read. Final correctness/source/engineering-language checks formally dispatched once, author only prepares Word tools while reviews run. Root ordinary PowerShell hidden Word.COM16.0 preflight succeeded, no policy change and no user document touched. No new science.\n')
(S/'rounds/R010.md').write_text('# R010 完整论文终审与Word准备\n\n'+now+'。v009共38210字节，SHA d622748a45b484d2a059a74d484c4c5c9f107e00f3ea628870fabf403e13c1f7，13表3图、完整中英文摘要、解析机制、三输入工程决策与真实不利结果均已整合。主控读完相对已读v008的精确差异及新增内容。\n\n②R013、③R004、⑥R009仅作一次完整终稿正确性/引用来源/工程语言检查，不新实验。尚未正式冻结前不把初步意见写为通过。⑤R011预备可编辑Word工具，不在最终意见采纳前生成正式文件。普通PowerShell独立Word COM16.0已实际成功，禁止旧脚本ExecutionPolicy Bypass和关闭用户Word。最终所有页实际看图。\n\n科学主线已闭合到本轮有限模型下的提前判断和解析解释，不再扩展外围。用户说明和工程应用步骤已写预备稿，清楚标明尚未结束。最终关闭时间将使用实际时间。\n',encoding='utf8')
files=[]
for p in (S/'roles/role5/R010').rglob('*'):
 if p.is_file() and 'local-cache' not in p.parts and p.suffix in ['.md','.json','.csv','.py','.cjs','.svg','.png'] and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R010.py','R010-actual-snapshot.json','status.json','threads.json','runs.md','rounds/R010.md','topic-cards/R009.md','git-R009-receipt.json','automation-R009-update-receipt.json','word-render-preflight-v001.md','final-stage-handoff-v001.md','普通中文研究说明-prepared-v001.md','工程应用方法-prepared-v001.md']:files.append(S/n)
files.append(R/'papers/damping-output-boundaries/manuscript/damping-prediction-session021-v009.md')
files=sorted(set(files))
js(S/'git-R010-publication.json',{'checkpoint':'R010','time':now,'message':'paper: integrate baseline shear-reduction mechanism and complete engineering prediction manuscript','files':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files]})
print(json.dumps({'time':now,'files':len(files),'bytes':sum(p.stat().st_size for p in files)}))
