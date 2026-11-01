from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-FINAL-publication.json').exists()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
snap=json.loads((S/'FINAL-actual-snapshot.json').read_text(encoding='utf8'));assert all(x['status']['type']=='idle'for x in snap)
t=json.loads((S/'threads.json').read_text(encoding='utf8'))
for x in t['threads']:
 z=next(y for y in snap if y['role']==x['role']);x.update(cursor=z['cursor'],actual_status=z['status'],task='Complete frozen idle; no further dispatch',last_actual=now)
js(S/'threads.json',t)
d=json.loads((S/'status.json').read_text(encoding='utf8'));d.update(checkpoint='FINAL-approved-deliverables',checkpoint_open=True,last_actual=now,recovery_file='rounds/FINAL.md');js(S/'status.json',d)
(S/'rounds/FINAL.md').write_text('# FINAL 工程预测论文与Word交付已核\n\n'+now+'。最终v010主稿及r2 Word已批准。根再次实际看完r2最终全部16页，修复的p_r/v_r、P帽/最大值表达式完整；15可编辑表块、10编号公式、3图、4外部文献链接及S1入口通过。增强身份检查独立核253数字单元格、源图散列和操作数结构。初版转换失败保留，不上传该旧Word。\n\n全部科学/作者/检查任务均完成且六角色真实idle。本轮在六小时上限内实际完成后提前收束，没有凑外围或宣称满六小时持续执行。最后只正式正常Git、暂停和删除当前自动化。最终summary、普通中文说明、工程步骤与真实未决已写。原Excel/EDB/完整时程/外部论文全文/所有local-cache及旧脏文件均不收。\n',encoding='utf8')
files=[]
for p in (S/'roles/role5/R014').rglob('*'):
 if p.is_file()and not any(x in p.parts for x in ['local-cache','__pycache__'])and p.suffix in ['.md','.json','.csv','.py','.cjs','.ps1','.svg','.png']and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_FINAL.py','prepare_final_closeout.py','FINAL-actual-snapshot.json','status.json','threads.json','claims.md','runs.md','rounds/FINAL.md','root-final-word-r2-identity.json','root-final-word-r2-visual-QA.json','check_final_word_identity.py','final-summary.md','普通中文研究说明.md','工程应用方法.md','git-R013-receipt.json']:files.append(S/n)
files += [R/'papers/damping-output-boundaries/manuscript/damping-prediction-session021-v010.md',R/'papers/damping-output-boundaries/manuscript/damping-prediction-session021-论文审阅稿-v010-r2.docx',S/'roles/role5/R012/supplement-S1.md']
files=sorted(set(files))
js(S/'git-FINAL-publication.json',{'checkpoint':'FINAL','time':now,'message':'paper: release verified engineering damping prediction manuscript and editable Word review copy','files':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in files]})
print(json.dumps({'time':now,'files':len(files),'bytes':sum(p.stat().st_size for p in files),'all_roles_idle':True}))
