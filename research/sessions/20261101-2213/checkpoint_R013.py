from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R013-publication.json').exists()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
snap=json.loads((S/'R013-actual-snapshot.json').read_text(encoding='utf8'))
t=json.loads((S/'threads.json').read_text(encoding='utf8'));d=json.loads((S/'status.json').read_text(encoding='utf8'))
for x in t['threads']:
 z=next(y for y in snap if y['role']==x['role']);x.update(cursor=z['cursor'],actual_status=z['status'],task=d['current_tasks'][x['role']],last_actual=now)
js(S/'threads.json',t);d.update(checkpoint='R013-document-math-repair-in-progress',checkpoint_open=True,last_actual=now,recovery_file='rounds/R013.md');js(S/'status.json',d)
with(S/'runs.md').open('a',encoding='utf8')as f:f.write('\nR013 '+now+': author first Word froze01:32:26; root enhanced document review independently viewed all16pages and found inline summation operands omitted onpage6 despite scalar/Chinese identity. Root rejected that Word for delivery, preserved it locally, dispatched sole author presentation-only R014. Scientific Markdown unchanged; one marker retained. No unapproved Word or any render cache included in Git.\n')
(S/'rounds/R013.md').write_text('# R013 Word公式转换问题修正中\n\n'+now+'。科学正文最终v010不变。作者R013完成首Word16页，主控独立实际逐页看完并核15表、253数值单元格、3原图散列与4外部链接及S1，发现第6页两个行内求和式丢失p_r/v_r。单纯中文、数字和OMML数量检查不足以保证数学操作数完整，主控拒绝交付该版。\n\n已保留旧DOCX与真实QA记录，只让唯一作者R014修Word转换为显式原生公式、重渲染并逐页检查；不改科学内容、不重跑marker、不新增任何科研。增强身份检查加入两条公式的操作数结构断言。最终r2仍在途，必须根再次看全部最终页后才可交付。\n\n本检查点只上传已冻结第一轮文档代码/报告与根拒收记录，旧未批准Word不上传，所有渲染中间件和在写r2不收。剩余是交付排版与行政关闭，科研预算不延长。\n',encoding='utf8')
files=[]
for p in (S/'roles/role5/R013').rglob('*'):
 if p.is_file() and not any(x in p.parts for x in ['local-cache','__pycache__']) and p.suffix in ['.md','.json','.csv','.py','.cjs','.ps1','.svg','.png']and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R013.py','status.json','threads.json','runs.md','rounds/R013.md','R013-actual-snapshot.json','root-word-v010-r1-visual-review.json','root-final-word-identity.json','check_final_word_identity.py','git-R012-receipt.json','automation-R012-update-receipt.json']:files.append(S/n)
files=sorted(set(files))
js(S/'git-R013-publication.json',{'checkpoint':'R013','time':now,'message':'paper: preserve independent document review and repair inline modal-summation rendering','files':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files]})
print(json.dumps({'time':now,'files':len(files),'bytes':sum(p.stat().st_size for p in files)}))
