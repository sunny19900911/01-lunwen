from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R008-publication.json').exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=json.loads((S/'status.json').read_text())
d.update(checkpoint='R008-v006-review',checkpoint_open=True,last_actual=now,recovery_file='rounds/R008.md')
d['scientific_status']['manuscript']='v00627194B SHAcb301790edae381adb5da3edde6709f63190de07c434e6906a8bccbad158029e frozen13:29:41; rootfullread+S1/4links/manifests passed13:31; includes3PNGs, same-time exactmechanism,Y; role2R010 finalreviewpending'
d['current_tasks'].update(role2='R010 sole finalmanuscript review dispatched13:31 max10min freeze13:42; no numericexperiments',role5='R006/v006 frozenactualidle13:29:41; Wordnotstarted; waitfinalreviewthenonlyformat')
d['next_checkpoint']='Collect role2R010 actualfreeze andread corrections; if0must dispatch soleauthor Word editableformulas/tables withdocuments renderQA; ifmust onlynecessarynewversion first. NextGitR009~13:48; last45min14:45 anddeadline15:30:11 unchanged.'
js(S/'status.json',d)
t=json.loads((S/'threads.json').read_text())
for x in t['threads']:
 if x['role']=='role5':x.update(cursor='824ab043-4970-4d4a-8fa8-7ed81ac611bc:55',actual_status={'type':'idle'},last_actual='2026-10-31T13:30:26+08:00',task=d['current_tasks']['role5'])
 elif x['role']=='role2':x.update(task=d['current_tasks']['role2'],dispatch_actual='2026-10-31T13:31:00+08:00')
js(S/'threads.json',t)
(S/'rounds/R008.md').write_text('# R008 完整图文稿已冻结 新稿最终独审进行中\n\n实际记录'+now+'。⑤v006于13:29:41完成，27194B，SHA cb301790edae381adb5da3edde6709f63190de07c434e6906a8bccbad158029e。根已全文读主稿及S1，另补读截断表和公式；检查4个相对链接、三图SHA及全部manifest通过。三图、Y方向辅助和同刻削弱/两态峰差已统一，6表11组显示公式。旧稿字节保留。\n\n13:31仅向实际idle②派R010一次新稿终审，10min最晚13:42，不重新计算旧数组。待审核后⑤唯一制作Word：原生可编辑公式和表格，documents渲染逐页实际检查；目前尚未制作Word。没有新科研扩展，没有重启③。\n\n普通中文研究说明准备稿已写，明确可解释线性模态增阻尼的工程层差，尚非实体Maxwell非线性逐阶唯一恢复。后续只修必要稿件问题和排版，截止15:30:11不变。\n',encoding='utf-8')
with(S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR008 '+now+': v006 soleauthor9minfreeze; rootfullreadandartifactchecks passed; one finalrole2R010 manuscriptreviewdispatched13:31, no newnumericexperiment; Wordnotyetcreated.\n')
files=[]
base=S/'roles/role5/R006';assert (base/'manifest.json').exists()
for p in base.rglob('*'):
 if p.is_file() and 'local-cache'not in p.parts and p.suffix in ['.md','.json','.py','.csv'] and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R008.py','close_checkpoint_R007.py','status.json','threads.json','runs.md','rounds/R008.md','topic-card-R007.md','普通中文研究说明-成稿准备-v001.md','root-v006-artifact-check.py','root-v006-artifact-check.json','git-R007-receipt.json']:files.append(S/n)
files.append(R/'papers/damping-output-boundaries/manuscript/physical-modal-shear-session020-v006.md')
js(S/'git-R008-publication.json',dict(checkpoint='R008',time=now,message='paper: integrate modal shear engineering results figures and analytic explanation',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(files))]))
print(json.dumps(dict(time=now,files=len(set(files))),ensure_ascii=False))
