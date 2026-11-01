from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R002-publication.json').exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
snap=json.loads((S/'R002-actual-snapshot.json').read_text());t=json.loads((S/'threads.json').read_text())
tasks={'role1':'R002 max10min admissible damping increment rule officiallysent22:35 actualactive; no engineeringarrays','role2':'R002 frozen22:38:24 baseline derivatives/prediction0must, pending newtarget truth audit','role3':'R002 max12min publicmultifloorbenchmark+onecorrespondingrecord sent22:39 actualstatusrefresh before nextdispatch','role4':'R002 max12-15min target6/7/10exact truth andold8reuse plus scalarcothbound; active since22:33, no R001changes','role5':'R001 failed manuscriptwrite deadline, adminrecordreal; newR0026min savepreparedv001 immediately sent22:39 latest22:46','role6':'R001frozen+role2review mathpassed, idle no duplicatecontract task'}
for x in t['threads']:
 z=next(p for p in snap if p['role']==x['role']);x.update(cursor=z['cursor'],actual_status=z['status'],task=tasks[x['role']],last_actual=now)
js(S/'threads.json',t)
d=json.loads((S/'status.json').read_text());d.update(last_actual=now,checkpoint='R002-baseline-prediction-reviewed',checkpoint_open=True,current_tasks=tasks,recovery_file='rounds/R002.md')
d['scientific_status'].update(derivative_math='role1 androle2 independent r1/r2/error contract correct; rootfullread; width/decision/peakregion distinct',engineering_prediction='role4R001 frozen22:28:46 all300/96layer peaks beforefinite targettruth; role2R002 independent ownRK4 3modes max4.29e-8/stepconvergence16;96rows576numeric192flags0must; actualfinite accuracy notyetknown',engineering_policy='Dreq10%,Wmax5pp demo rootpolicy22:35 before root receives targetresults; no normativeclaim; operational recompute if uncertainty OR widthfail',manuscript='authorR001 failed allwrite due deadline guard, no draft falselyclaimed; realadminfailure retained; newR0026min rescue assigned',literature='Liu2011 DDM firstsecond derivatives covers foundation;Xie2020 changesstiffness notsameproblem; no firstclaim; publiccantileveronlysinglemode notmulti-floorvalidation')
d['next_task']='Get role4R002 actualfreeze andread fullprediction-vs-truth/bound widths; then role2 auditthisnewtargetsmallresults. If scalarbound too wide, one targetedtime-residual-convolution sharpening, notnewdata scatter. ConfirmauthorR002 realv001saved. Role1R002maxincrement androle3R002publicmultilayer active. NextGitR003 ~22:58, hard04:13:31 unchanged.'
js(S/'status.json',d)
with(S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC021-01 supported/analytic-derivation reviewed: role1R001 +role2R001 independent z/w/r1/r2 zeroIC, outputc=Bomega²/1000 andresidualconvolution. No new basic sensitivityprinciple.\nC021-05 supported/numericalimplementation reviewed: role4R001 all300 baseline-only1/2order predictions frozen22:28:46; role2R002 independentlyownRK4 selected3modes maxrelative4.29e-8 and96peakrows0must. Thisis implementation correctness, finite-delta predictionaccuracy pending.\nC021-06 testing/engineering prediction: SHW3X8% Story5twoorders5.9408/7.5209% vsroof29.8177/25.8777%;10%Story5 orders9.3458/13.7083 across10%demo target. Frozenpredictions notvalidatedtargetresults.\n')
with(S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR002 '+now+': collectedmath/decision/publicsource andall300predictionfreeze; role2R002 actualindependentreview0must; targettruth newR002 stillinprogress. role5R001 nooutput/timeguardfailure preserved, newlimitedR002 recoveryassigned. Nonewmanuscript successclaimed.\n')
(S/'rounds/R002.md').write_text('# R002 基准预测已冻结并独核 有限目标验证在途\n\n'+now+'。④已由5%缓存解析微分递推得到全300阶导数与四目标96行楼层预测，22:28:46冻，未以8%数组作为输入。②R00222:38:24冻：自写增广RK4 selected2/10/13最大相对导数差4.29e-8、步减半约16；96行576数/192标志、B单位方向与曲线合成通过0must。根已读报告及生产代码。预测实算正确不等于有限δ目标准确度通过。\n\n①②残差理论与⑥工程判据一致，根冻结Dreq=.10/Wmax=.05演示政策，分类/宽度/峰区分开；目标结果尚未根读取。④新R002已正式生成有限目标参考，8%直接复用；先完整保守coth界，过宽如实记失败，下一项再收紧。\n\n③R001最近邻确认DDM已有，公开单柱仅单模态；新R002只找一多层基准+一配套记录。⑤R001写入超时断言阻断而无稿，行政事实保留，actualidle后根22:39新6min R002要求先2min落正文，不重读外围。首稿目前未冒称完成。\n\n本点Git只已冻role1R001、role2R001/R002、role3R001、role4R001、role6R001与角色5失败记录。活动R002文件不收，原件/完整数组/旧dirty不动。\n',encoding='utf-8')
files=[]
for role,rounds in {'role1':['R001'],'role2':['R001','R002'],'role3':['R001'],'role4':['R001'],'role6':['R001']}.items():
 for rr in rounds:
  for p in (S/'roles'/role/rr).rglob('*'):
   if p.is_file() and 'local-cache' not in p.parts and '__pycache__' not in p.parts and p.suffix in ['.md','.json','.csv','.py'] and p.stat().st_size<1048576:files.append(p)
base=S/'roles/role5/R001'
if base.exists():
 for p in base.iterdir():
  if p.is_file() and p.suffix in ['.md','.json']:files.append(p)
for n in ['checkpoint_R002.py','status.json','threads.json','claims.md','runs.md','rounds/R002.md','R002-actual-snapshot.json','engineering-policy-freeze-v001.json','git-R001-receipt.json']:files.append(S/n)
js(S/'git-R002-publication.json',dict(checkpoint='R002',time=now,message='research: freeze baseline-only modal predictions and independently verify sensitivities',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(files))]))
print(json.dumps(dict(time=now,files=len(set(files)),bytes=sum(p.stat().st_size for p in set(files))),ensure_ascii=False))
