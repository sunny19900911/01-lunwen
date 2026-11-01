from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,tomllib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R001-publication.json').exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
snap=json.loads((S/'R001-first-real-snapshot.json').read_text())
t=json.loads((S/'threads.json').read_text())
for x in t['threads']:
 z=next(p for p in snap if p['role']==x['role']);x.update(cursor=z['cursor'],actual_status=z['thread']['status'],task='R001 officiallysent22:19:50; actualactive22:22, do not duplicate',last_actual=now)
js(S/'threads.json',t)
d=json.loads((S/'status.json').read_text());d.update(last_actual=now,checkpoint='R001-started-real-science',checkpoint_open=True,automation='git-2 newlycreated forsession021, formalview andactualTOMLverified; oldID reused byscheduler, not oldscope resumed')
d['current_tasks']={x['role']:x['task'] for x in t['threads']}
d['scientific_status']={'root_harmonic_sanity':'36known2floor steady harmonic cases; baseline sensitivity residualmax4.44e-16; sqrt2/5to8 firstorderpeakerror4.78%,second.558%; notzeroICearthquakevalidation','engineering_prediction':'role4R001 actualactive baseline5only; no targettruth yet','manuscript':'role5R001 actualactive newmethod writing; no newmanuscriptclaimedfrozen'}
d['next_task']='Near22:30-22:35 collectfirstrolefreezes, no redispatchactive. Predictor coefficients/criterion freezebefore newtargettruth; passmath to2, outputs to2then5. FirstGitR001frozenrootonly; nextR002 ~22:40; hard04:13:31 unchanged.'
js(S/'status.json',d)
p=Path('C:/Users/mj528/.codex/automations/git-2/automation.toml');b=p.read_bytes();c=tomllib.loads(b.decode());assert c['status']=='ACTIVE' and c['name']=='楼层剪力提前判断｜六小时预测研究与Git同步' and '20261101-2213'in c['prompt']
js(S/'automation-config-check.json',dict(actual=now,id='git-2',status=c['status'],name=c['name'],rrule=c['rrule'],target_thread_id=c['target_thread_id'],sha256=hashlib.sha256(b).hexdigest(),view_succeeded=True,hard_deadline='2026-11-02T04:13:31+08:00',id_reuse='schedulerreused deletedoldID; newpromptscopeverified'))
with(S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC021-04 supported/numerical-sanity candidate: known2DOF harmonic baseline derivatives andfirst/secondorderresiduals checked36cases;max4.44e-16. AtΩsqrt2δ.03 firstorderPerror4.78%,second.558%; actualP rises46.459%. Thisis equationimplementationsanity, notnewengineering orzeroICgroundmotion validation.\n')
with(S/'runs.md').open('a',encoding='utf-8')as f:f.write('\n'+now+' R001: six formaldispatches22:19:50 +actualallactive22:22; root36harmonicchecks executed; formal15minheartbeatnewgit-2 create/view/TOMLverified; firstrootonlyfrozenGitmanifest. No roleworkingfilesstaged.\n')
(S/'rounds/R001.md').write_text('# R001 预测研究已实际启动\n\n'+now+'。固定六小时22:13:31—明04:13:31；六角色22:19:50正式派发且22:22实际全active。①候选推导、②独审反例、③最多两原文/公开基准线索、④5%基准敏感度、⑤新方法稿、⑥工程分类基线，首轮12min、④15min。工作中不重派、不收未冻结角色文件。\n\n根已运行36个已知两层稳态传递函数组合，灵敏度与残差代数核到4.44e-16；sqrt2/5→8的一阶/二阶峰误差4.78%/.558%。两层稳态不冒充地震或工程预测。原时程/完整旧ODE未重提。根小结果交①②，不要求重复计算。\n\n正式15minheartbeat成功创建、view及实际TOML核对，调度器复用旧已删ID git-2，但新任务名称/目录/截止均为021，不恢复020。旧git/automation3/4仍暂停。末15min调度余量只行政，不延04:13:31科学截止。\n\n下一轮收实际冻结产物，优先全300预测与新目标隔离验证；不因旧8%已看过称盲测，不因延拓误差不利改目标。当前首Git只共享计划/根已算小表/代码/工具配置回执，白名单不含旧脏文件与任何local-cache。\n',encoding='utf-8')
(S/'topic-card-R001.md').write_text('# 方向卡021 首轮\n\n目标是从基准响应提前预判候选阻尼的楼层剪力，输出改善不足和需复算建议。现有020只作为物理投影/输入/工程解释基础，不把其整体重构精度当新预测精度。当前主候选为一/二阶阻尼灵敏度，须处理有限δ、峰切换及误差区间判别力。首次稳态小核验显示二阶比一阶在一个反升例更准确，但完整工程和独立记录尚待检验。\n\n本轮可争取增量为具体剪力预测/工程决策流程与可核误差，而非经典Taylor或三角不等式本身。下一最高信息任务是冻结预测后检验目标阻尼真值，保留不利样本和成本。\n',encoding='utf-8')
files=[]
for n in ['start_session.py','plan.md','status.json','threads.json','claims.md','runs.md','authorization-evidence.json','publish_checkpoint.py','root_harmonic_sanity.py','R001-first-real-snapshot.json','automation-create-receipt.json','automation-config-check.json','checkpoint_R001.py','rounds/R001.md','topic-card-R001.md']:files.append(S/n)
files+=list((S/'root-R001-harmonic-sanity').iterdir())
js(S/'git-R001-publication.json',dict(checkpoint='R001',time=now,message='research: start six-hour baseline damping prediction study with six roles',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(files))]))
print(json.dumps(dict(time=now,files=len(set(files))),ensure_ascii=False))
