from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R011-publication.json').exists()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
snap=json.loads((S/'R011-actual-snapshot.json').read_text(encoding='utf8'))
t=json.loads((S/'threads.json').read_text(encoding='utf8'))
d=json.loads((S/'status.json').read_text(encoding='utf8'))
for x in t['threads']:
 z=next(y for y in snap if y['role']==x['role']);x.update(cursor=z['cursor'],actual_status=z['status'],task=d['current_tasks'][x['role']],last_actual=now)
js(S/'threads.json',t)
d.update(checkpoint='R011-final-reviews-adopted',checkpoint_open=True,last_actual=now,recovery_file='rounds/R011.md')
d['scientific_status']['manuscript']='v009 full final reviews completed and root full reports read/adopted. Final v010/S1 surgical edit current; no new science. Word builder prepared and native10display XML preflight passed, but no final DOCX/visual qualification yet.'
js(S/'status.json',d)
with(S/'runs.md').open('a',encoding='utf8')as f:f.write('\nR011 '+now+': three final reviews and Word-preparation scripts frozen; root full reports and safe renderer read. Final text revision remains separate from Word creation and visual QA. Scientific numbers unchanged. XML-only preflight assets remain local-only and are excluded from Git; no DOCX or marker yet.\n')
(S/'rounds/R011.md').write_text('# R011 终审意见与文档工具冻结\n\n'+now+'。②R013正确性must0，③R004来源must0，⑥R009要求明确最大峰包络目标与第4节操作步骤；主控已阅读全文合并采纳，作者只作一次必要修订。保留所有公式与已审数字，不重新进行科学实验。\n\n⑤R011参数化Word builder与受控renderer预备完成，10个独立公式原生OMML XML预检通过；13编号表加2判定表共15表、3图。XML预检不是排版验收，尚未创建Word或运行marker。canonical渲染与最终全部页实际查看仍是交付条件。预检XML属于本地中间件，不上传。\n\n本轮白名单仅收已冻结终审报告、小脚本与共享交接，不收在写v010及任何local-cache。科研截止04:13:31不变，完成可提前关闭，不为了预算再开外围任务。\n',encoding='utf8')
files=[]
for role,rr in [('role2','R013'),('role3','R004'),('role6','R009'),('role5','R011')]:
 for p in (S/'roles'/role/rr).rglob('*'):
  if p.is_file() and not any(x in p.parts for x in ['local-cache','__pycache__']) and p.suffix in ['.md','.json','.csv','.py','.cjs','.ps1','.svg','.png'] and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R011.py','status.json','threads.json','runs.md','rounds/R011.md','R011-actual-snapshot.json','final-review-adoption-v001.md','final-summary-prepared-v002.md','git-R010-receipt.json','automation-R010-update-receipt.json','automation-R010a-final-review-update-receipt.json']:files.append(S/n)
files=sorted(set(files))
js(S/'git-R011-publication.json',{'checkpoint':'R011','time':now,'message':'paper: adopt final engineering and source reviews and prepare editable Word rendering','files':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files]})
print(json.dumps({'time':now,'files':len(files),'bytes':sum(p.stat().st_size for p in files)}))
