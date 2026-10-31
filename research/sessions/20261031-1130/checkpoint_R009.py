from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R009-publication.json').exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=json.loads((S/'status.json').read_text());d.update(last_actual=now,checkpoint='R009-final-text-reviewed',checkpoint_open=True,no_new_scientific_dispatch=True,phase='final-text-accepted-Word-production',recovery_file='rounds/R009.md')
d['scientific_status']['manuscript']='v006 finalreview role2R010 frozen13:40:20,0must2optional; rootfullreadreview/manifest;v007 only2clarifications/S1link thenWord, no newscience'
d['current_tasks'].update(role2='R010 finalreview frozenactualidle13:41:38,0must; no further scientific tasks',role5='R007 sole finalclarification/v007 andWord formallydispatched13:41; initialprogress14:15 finalQAby14:40; no duplicateauthor')
d['next_checkpoint']='Collect authorR007 actualWord progress. Do not read stillwritingdraft. On freeze rootcheck v006-v007 exactdiff anddocx fidelity; inspect renderedpages. No newscientificdispatch. NextGitR010 near14:00 frozenonly, deadline15:30:11 unchanged.'
js(S/'status.json',d)
t=json.loads((S/'threads.json').read_text())
for x in t['threads']:
 if x['role']=='role2':x.update(cursor='11a056de-2e65-48d9-90d8-2d3233b00402:61',actual_status={'type':'idle'},last_actual=now,task=d['current_tasks']['role2'])
 if x['role']=='role5':x.update(cursor='824ab043-4970-4d4a-8fa8-7ed81ac611bc:56',actual_status={'type':'active','activeFlags':[]},last_actual='2026-10-31T13:40:45+08:00',task=d['current_tasks']['role5'])
js(S/'threads.json',t)
(S/'rounds/R009.md').write_text('# R009 最终科学稿审通过 转Word排版\n\n实际记录'+now+'。②R010于13:40:20冻结，0必须修改、2可选清晰度；根已读review/manifest与定向核对记录。全文294行与S1全文211行、8文件SHA及25定向检查通过。没有新ODE/数组复算。\n\n根13:41正式仅向⑤派R007：旧v006保留，v007只补二层同模态阻尼和S1峰比正分母及相应链接，给精确diff；随后单一Word制作。初步稿尽量14:15前，最终逐页QA14:40前。要求先读documents、权威runtime、marker一次、可编辑公式与表格、三图、render_docx及实际逐页查看；目前Word尚未交付，不称排版通过。\n\n科学派工全面停止。③窗口已闭，①②④⑥待命不重启。最后45min14:45和硬截止15:30:11保持。保留全有限元及非线性实际逐阶解释的真实缺口。Git本点只收冻结R010终审与共享记录，不收在写Word。\n',encoding='utf-8')
with(S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR009 '+now+': rootadopted finalmanuscriptreview0must; soleauthorR007 final2clarifications/Word assigned13:41; no newscience.\n')
files=[];base=S/'roles/role2/R010'
for p in base.iterdir():
 if p.is_file() and p.suffix in ['.md','.json','.csv','.py'] and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R009.py','status.json','threads.json','runs.md','rounds/R009.md','git-R008-receipt.json']:files.append(S/n)
js(S/'git-R009-publication.json',dict(checkpoint='R009',time=now,message='paper: accept independent final review and start editable Word production',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(files))]))
print(json.dumps(dict(time=now,files=len(set(files))),ensure_ascii=False))
