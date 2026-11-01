from pathlib import Path
from datetime import datetime, timezone, timedelta
import json, hashlib
S=Path(__file__).resolve().parent
R=S.parents[2]
assert not (S/'git-R003-publication.json').exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
snap=json.loads((S/'R003-actual-snapshot.json').read_text(encoding='utf-8'))
tasks={'role1':'R003 discrete-defect proof frozen23:03:37, independent short math review passed; idle no new algebra task', 'role2':'R004 max12min independent public static assembly audit, officiallysent23:08; no dynamic production', 'role3':'R002 public 3story frame and AT2 frozen22:44:58; idle no redundant search', 'role4':'R004 max12min public baseline-only predictions/intervals, officiallysent23:10; target truth not yet authorized in this task; static audit pending', 'role5':'R004 max12min v003 integrate independently reviewed finite-target accuracy and new candidate-level engineering policy, active23:09', 'role6':'R003 max8min retrospective candidate-level policy accounting on reviewed SHW3 small tables, active23:08; no dynamic response'}
t=json.loads((S/'threads.json').read_text(encoding='utf-8'))
for x in t['threads']:
    z=next(y for y in snap if y['role']==x['role'])
    x.update(cursor=z['cursor'],actual_status=z['status'],task=tasks[x['role']],last_actual=now)
js(S/'threads.json',t)
d=json.loads((S/'status.json').read_text(encoding='utf-8'))
d.update(last_actual=now,checkpoint='R003-target-validation-and-discrete-envelope',checkpoint_open=True,phase='prediction-usefulness-and-independent-benchmark',current_tasks=tasks,recovery_file='rounds/R003.md')
d['scientific_status'].update(engineering_prediction='role4R002 finite targets6/7/10 and old8 reuse independently audited role2R003:7608 fields, own selected RK4, 0must; second order worse14/48; max peak error15.7633% at10%; rawpoint predictions2low-improvement misses',engineering_policy='v001 coth bound96/96 coverage but all8groups require wholebuildinganalysis. New v002 candidate-level policy frozen23:00, retrospective SHW3 development only; alltargetfloorcriterion required.',discrete_envelope='role4R003 frozen23:01:12, root fullreportread; math independently correct; numeric independent review pending. median width2nd6%=.28523pp, 7%=2.00446pp; per-floor recompute0/12 at6%,1/12 at7%; no speedup claim:8envelopes2.364s vs direct target~.06s each',public_benchmark='OpenSees official Example5 ElasticSection/Linear topology and one H-E12140 AT2 source checked; selfwritten16node21member assembly,12massDOF, base rotations free, no rigidfloor. role6R002 static frozen, role2R004 independent audit active. No public targetresponse yet.',manuscript='v00112367B then v00218576B frozen/root fullread; v002 includes admissible increment radius and classical DDM attribution; v003 integration active; oldauthorR001 failure preserved')
d['next_task']='Collect role2R004 static audit; role4R004 public baseline prediction freeze then only new separate task for candidate target truth. Get independent numeric review of role4R003 discrete envelope before result adoption. Role6R003 candidate-level counts, authorv003. No new layout/CM repair/large data. Next checkpoint15min; fixed04:13:31 deadline.'
js(S/'status.json',d)
with (S/'claims.md').open('a',encoding='utf-8') as f:
    f.write('\nC021-07 reviewed-numerical: role4R002 targets and role2R003 independent audit reveal finite prediction limitations: secondorder14/48worse, maxerr15.7633% at10%;2 point-prediction low-improvement falsepasses. No universalaccuracy claim.\nC021-08 reviewed-policy: coth96intervals cover reference but all8candidate/ordergroups need fullanalysis underv001; candidate-level v002 fixed23:00 permits earlyreject when any targetfloor DU<10%, developmental SHW3 only until newmodel/input validation.\nC021-09 analytic-reviewed/numeric-pending: discrete defect e_next=Ac e+d gives absolute matrixpower convolution and timevaryingpeakintervals. role4R003 numeric narrowerall96, but independent numeric audit pending. No speedup:2.364s8envelopes vs~.06s/directcandidate.\nC021-10 static-pending-audit: public12massDOF frame sourceverified and independently assembledrole6R002, full eigen/cut identities tinyresidual; role2R004 audit ongoing, not a dynamicvalidation result yet.\n')
with (S/'runs.md').open('a',encoding='utf-8') as f:
    f.write('\nR003 '+now+': root read v002, role1discrete proof, role4R002/R003 reports and role6publicstaticonepage. Independentfinite-targetaudit adopted; discrete numericcandidate pendingaudit. Current four finite tasks dispatched only after actualidle. Public dynamic baseline only, targettruth separate. Actual gap sinceR002 recorded, not claim exact15minute cadence.\n')
(S/'rounds/R003.md').write_text('# R003 从预测准确性转入工程判别与另一模型检验\n\n'+now+'。原定六小时截止04:13:31保持。上一点至本点约30min，未冒称严格每15分钟。\n\n## 采用的真实增量\n④R002有限目标对照经②R003独核7608字段及独立选阶RK4，0must。6%二阶最大峰误差.134881%，8%3.407483%，10%15.7633%；14/48二阶较差。点估计有两个低改善误放行。保留全部失败与代价，不把误差区间全部覆盖称判别成功。\n\n①R002给阻尼允许增量预算和单调误差界，v002已纳。①R003给离散缺陷绝对卷积，②短理论核通过。④R00396区间全覆盖且较coth窄，二阶6%全部层判定、7%1层待复算；但尚待独立数值核，当前只候选。8组包络2.364s，高于直接线性求解成本，不称加速。\n\n## 主线工程动作\n根23:00冻结新候选级策略：全楼各目标层均需达标时，任一有效上界不足即可提前淘汰候选；所有层下界达标且宽度合格才采纳，其余一次完整分析。⑥R003只回顾开发集计数，不冒充独立验证。公开三层框架源参数/记录实得；⑥静态组装完，②R004独核，④R004只基准及候选预测先冻结，不提前生产目标。\n\n⑤v001/v002已全文读，R004写v003整合已审实数与操作方法，过程日志不塞正文。源原件/数组只local-cache，本点Git显式冻结清单；当前活动R004/R003不收。\n',encoding='utf-8')
(S/'topic-card-R003.md').write_text('# 方向卡R003 工程师何时能提前作决定\n\n核心问题保持：基准5%响应是否足以提前判断候选阻尼的楼层剪力。现在已完成导数预测—有限目标独核—误差区间；单点预测存在误放行，误差范围和整候选动作才有工程意义。\n\n较小增量6%/7%的逐时包络有用性出现；较大增量10%仍明显失败，二阶不保证更好。现阶段不以加速为卖点，直接线性求解很便宜。后续价值门：新公开框架及留出输入下，预定区间能否正确淘汰不满足目标的方案，并解释哪些楼层控制该决定。\n\n已用经典直接微分法，创新定位为有范围限制的工程判断流程而非新微分原理。继续主线，禁止转布局/质量参与率替代剪力/CM修补。\n',encoding='utf-8')
files=[]
scopes={'role1':['R002','R003'],'role2':['R003'],'role3':['R002'],'role4':['R002','R003'],'role5':['R002','R003'],'role6':['R002']}
for role,rrs in scopes.items():
    for rr in rrs:
        for p in (S/'roles'/role/rr).rglob('*'):
            if p.is_file() and not any(x in p.parts for x in ['local-cache','__pycache__']) and p.suffix in ['.md','.json','.csv','.py'] and p.stat().st_size<1048576: files.append(p)
for v in ['001','002']: files.append(R/f'papers/damping-output-boundaries/manuscript/damping-prediction-session021-v{v}.md')
for n in ['checkpoint_R003.py','status.json','threads.json','claims.md','runs.md','rounds/R003.md','topic-card-R003.md','R003-actual-snapshot.json','candidate-level-policy-v002-freeze.json','public-benchmark-settings-freeze-v001.json','git-R002-receipt.json','automation-R002-update-receipt.json']: files.append(S/n)
js(S/'git-R003-publication.json',dict(checkpoint='R003',time=now,message='research: test prediction limits and develop actionable damping screening',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(files))]))
print(json.dumps({'time':now,'files':len(set(files)),'bytes':sum(p.stat().st_size for p in set(files))}))
