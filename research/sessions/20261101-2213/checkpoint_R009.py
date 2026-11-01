from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not (S/'git-R009-publication.json').exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
snap=json.loads((S/'R009-actual-snapshot.json').read_text(encoding='utf-8'))
tasks={r:'Frozen idle; no new scientific production' for r in ['role1','role2','role3','role4','role6']}
tasks['role5']='R010 v009 sole final-review-candidate integration, active00:49; baseline SU/SC bridge formally adopted, no new science'
t=json.loads((S/'threads.json').read_text(encoding='utf-8'))
for x in t['threads']:
 z=next(y for y in snap if y['role']==x['role']);x.update(cursor=z['cursor'],actual_status=z['status'],task=tasks[x['role']],last_actual=now)
js(S/'threads.json',t)
adoption={'time':now,'review':'roles/role2/R012/one-page-independent-baseline-UC-audit.md','review_read_in_full':True,'author_wording_read_in_full':True,'must_fix':0,'adopted':'Baseline right derivative S=SU+SC with own-modal peaks distinguished from total peak; 39 layer-input combinations independently checked, no new ODE or target response.','key_rows':{'SHW3X_Story5':[4.642958506,-2.510894071,2.132064435],'SHW3X_roof':[6.373211228,5.350637578,11.723848806],'public_Story1':[.560312394,-.572694343,-.012381949]},'author_dispatch':'R010 v009, actual idle confirmed before message','scope':'Derivative identity on fixed saved grid, not finite-increment exact formula, pure phase or actual FNA modal-share certification'}
js(S/'root-R009-baseline-UC-adoption.json',adoption)
d=json.loads((S/'status.json').read_text(encoding='utf-8'))
d.update(checkpoint='R009-baseline-mechanism-adopted-and-complete-paper',checkpoint_open=True,last_actual=now,current_tasks=tasks,no_new_scientific_dispatch=True,recovery_file='rounds/R009.md')
d['scientific_dispatch_exception']='Only necessary independent final manuscript checks, source consistency checks, editorial corrections and Word rendering/QA; no new science, inputs, models, target states or parameter scans.'
d['scientific_status']['baseline_derivative_bridge']='Reviewed role2R0120must, root full report and author wording read:39 layer-input combinations/10836 modal scalars, closure1.78e-15. SHW3floor5 SU4.64296+SC-2.51089=S2.13206; roof6.37321+5.35064=11.72385; publicfloor1 locally negative. Baseline derivative, not finite delta.'
d['scientific_status']['manuscript']='v008 frozen00:37:22, root full text read in3bounded chunks; figures/ensemble/English abstract integrated. v009 R010 currently adds independently reviewed baseline SU/SC relation. Final single review then editable Word with per-page QA.'
d['next_task']='Collect sole author v009; one final correctness/source/engineering-language review, author corrections, then Word preflight and actual rendered per-page QA. Production science complete. No filler cases or repeated old reviews. Fixed04:13:31 deadline unchanged.'
js(S/'status.json',d)
with (S/'claims.md').open('a',encoding='utf-8') as f:f.write('\nC021-19 upgraded-supported-reviewed '+now+': independent role2R012 baseline right-derivative S=SU+SC passed0must. 39 layer-input combinations, modal own peaks vs total peak distinguished. Counterexample publicStory1 SU positive yet S negative retained. No new target/ODE.\n')
with (S/'runs.md').open('a',encoding='utf-8') as f:f.write('\nR009 '+now+': root full R012 independent audit and author wording read; v008 entire text read in bounded chunks. Adopted baseline U/C analytic bridge and dispatched actual-idle author R010 v009. All numeric production and new scientific dispatch stopped; final single manuscript/source/language review and Word QA remain.\n')
(S/'rounds/R009.md').write_text('# R009 基准解析机制与工程预测接通\n\n'+now+'。独审②R012正式0must，主控阅读全文采用。各阶独立峰总和U与合成峰P之比C满足S=SU+SC。第5层4.643−2.511=2.132，屋顶6.373+5.351=11.724，直接说明各阶幅值下降与叠加变化共同决定楼层改善快慢。公开第1层幅值总和下降而合成峰局部略增的反例保留。39指层-输入组合。\n\n⑤v008完整稿主控分三段读完，工程包络、物理因子、简单基线及旧终版两态机制均已接入；下一v009只整合已审基准导数机制、摘要和结论。各角色实际状态存本轮快照。科学生产已完成，不新ODE/模型/目标/搜索，也不为剩余预算凑实验。随后一次最终正确性/来源/工程语言检查，再做可编辑Word及逐页实际渲染检查。\n\n保留所有不利结果：局部排序反转、二阶不总优、区间需复算、当前无总成本优势。正文用简短工程讨论解释，过程日志留附件。04:13:31科研硬截止不变。\n',encoding='utf-8')
files=[]
for role,rounds in {'role1':['R007'],'role2':['R012'],'role4':['R011'],'role5':['R009'],'role6':['R008']}.items():
 for rr in rounds:
  for p in (S/'roles'/role/rr).rglob('*'):
   if p.is_file() and not any(q in p.parts for q in ['local-cache','__pycache__']) and p.suffix in ['.md','.json','.csv','.py','.cjs','.svg','.png'] and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R009.py','status.json','threads.json','claims.md','runs.md','rounds/R009.md','R009-actual-snapshot.json','root-R009-baseline-UC-adoption.json','root-figure3-v002-adoption.json','git-R008-receipt.json','automation-R008-update-receipt.json']:files.append(S/n)
files.append(R/'papers/damping-output-boundaries/manuscript/damping-prediction-session021-v008.md')
files=sorted(set(files))
js(S/'git-R009-publication.json',{'checkpoint':'R009','time':now,'message':'research: connect baseline modal amplitude and superposition derivatives to engineering forecasts','files':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]})
print(json.dumps({'files':len(files),'bytes':sum(p.stat().st_size for p in files),'time':now}))
