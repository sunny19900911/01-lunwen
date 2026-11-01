from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R012-publication.json').exists()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
snap=json.loads((S/'R012-actual-snapshot.json').read_text(encoding='utf8'))
t=json.loads((S/'threads.json').read_text(encoding='utf8'));d=json.loads((S/'status.json').read_text(encoding='utf8'))
for x in t['threads']:
 z=next(y for y in snap if y['role']==x['role']);x.update(cursor=z['cursor'],actual_status=z['status'],task=d['current_tasks'][x['role']],last_actual=now)
js(S/'threads.json',t)
d.update(checkpoint='R012-final-source-and-editable-document-in-progress',checkpoint_open=True,last_actual=now,recovery_file='rounds/R012.md')
d['document_status']='Sole author R013 Word active. First16pages actually viewed by author, layout/inline-math issues found and being corrected; no final Word visual qualification or root final-page QA claimed yet. Active Word and intermediate render files excluded from this checkpoint.'
js(S/'status.json',d)
with(S/'runs.md').open('a',encoding='utf8')as f:f.write('\nR012 '+now+': final v010/S1 source frozen01:17:49, root full main+S1 diffs read and standalone unchanged-table/display-formula/figure-path plus target/workflow/citation checks passed. First inline root regex command was corrupted by PowerShell dollar-parenthesis expansion; its result invalidated and standalone source check replaced it truthfully. Word actual first render reviewed by author, corrections in progress; final Word not yet staged.\n')
(S/'rounds/R012.md').write_text('# R012 最终科学稿已冻结 Word实际排版修订中\n\n'+now+'。最终v01039606B，SHA64ee1567ee775cdcf30aa28734ae0bb5003706970fddb708d5fa3afb648c942d，三项终审意见落实，目标、步骤和记录来源已澄清。主控读完正文/S1精确diff、QA及manifest，独立逐表行/10display公式/3图路径不变检查通过。没有新增科学实验。\n\n⑤R013正式Word在途，首轮16页已实际看图，发现短表表头分离、个别数字换行及两条行内公式下标问题，正在只修呈现并重新渲染。未把文件存在或XML检查当排版通过。Word在写不纳本次Git。主控已备OOXML身份核查脚本，待作者真正冻结后运行并逐页实看最终全部页。\n\n本检查点只收最终已审MD/S1、小检查脚本及共享记录；全部local-cache/原始Excel/大数组/旧脏文件不收。科研冻结，后续仅必要排版与行政收束，固定04:13:31最晚截止不变。\n',encoding='utf8')
files=[]
for p in (S/'roles/role5/R012').rglob('*'):
 if p.is_file() and 'local-cache'not in p.parts and p.suffix in ['.md','.json','.csv','.py','.cjs','.ps1','.svg','.png']and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R012.py','status.json','threads.json','runs.md','rounds/R012.md','R012-actual-snapshot.json','root-v010-change-check.py','root-v010-change-check.json','check_final_word_identity.py','git-R011-receipt.json','automation-R011-update-receipt.json']:files.append(S/n)
files.append(R/'papers/damping-output-boundaries/manuscript/damping-prediction-session021-v010.md')
files=sorted(set(files))
js(S/'git-R012-publication.json',{'checkpoint':'R012','time':now,'message':'paper: freeze reviewed engineering prediction source and preserve final document verification gates','files':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files]})
print(json.dumps({'time':now,'files':len(files),'bytes':sum(p.stat().st_size for p in files)}))
