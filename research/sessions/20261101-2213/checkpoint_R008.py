from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R008-publication.json').exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
snap=json.loads((S/'R008-actual-snapshot.json').read_text(encoding='utf-8'))
tasks={'role1':'R0078min existing U/C tobaseline S analytic rightderivative bridge, active, no new states', 'role2':'R01212min needed15 independent baseline39floor U/C derivative mechanisms, active00:28; R011ensemble0must adopted', 'role3':'R003 sourcebridge frozen00:15 rootfullread adopted, idle no search', 'role4':'R01112min existing-cache39floor SU/SC tabulation, active00:22 no newODE; allproduction cases frozen', 'role5':'R00912min v008 engineering ensemble+factor/simplebaseline+oldUPC/Englishabstract integration active00:28', 'role6':'R0088min needed10 three-input S comparison figure from reviewed36floor table, active00:25'}
t=json.loads((S/'threads.json').read_text(encoding='utf-8'))
for x in t['threads']:
 z=next(v for v in snap if v['role']==x['role']);x.update(cursor=z['cursor'],actual_status=z['status'],task=tasks[x['role']],last_actual=now)
js(S/'threads.json',t)
d=json.loads((S/'status.json').read_text(encoding='utf-8'));d.update(last_actual=now,checkpoint='R008-reviewed-project-envelope-and-source-integration',checkpoint_open=True,current_tasks=tasks,recovery_file='rounds/R008.md')
d['scientific_status'].update(engineering_ensemble='reviewedrole2R0110must rootfullread:288individualintervals/144refs/96envelopes/8decisions14924fields; 8%trueenvelope min9.2281004%,10%14.6348095%Story7;6/7reject,8/10recompute. Senv Story5=4.676272 notmin2.132064; baseline slowest8; controller7 changesSHW4toSHW3',old_mechanism_bridge='role3R003 same5%path/bytes/SHA d65da111 matchedoldapproved020UPC;two-row5to8 postknownmechanism and300mode/18CMsource facts adopted; oldcurve/peaktruncation errors keptdistinct',manuscript='v007 frozen00:11:17 includes RH4reviewedpass and2approvedfigures; rootnewtables/images/QAread; v008 engineering3-input case integration current; noWordyet',baseline_derivative_bridge='role1R007math/role4R011existingcache39floorSU=-Uright/U andSC=-Cright/C inprogress, role2R012independent; not finite-delta prediction ornewcases')
d['next_task']='Collect andindependentlycheck baselineSU/SC39floor bridge; rootview threeinputfigure thenauthorinclude. Finish integratedv008 andone compact analyticmechanism. Productioncases frozen no more inputs/targets/models, references/Word/engineerworkflow remain. NextGitR009~15min;03:13writing/04:13:31end unchanged.'
js(S/'status.json',d)
with(S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC021-17 upgraded-reviewed: role2R011 specified-input absolutepeak envelope andSenv0must;14924fields/newselectedRK4. 8%trueDenvmin9.2281fails/10%14.6348meets atStory7;predictions8/10uncertain,6/7reject. Originalperinput strongerobjective preserved, not code/normoranyeventguarantee.\nC021-18 literature-source-reviewed: role3R003originalfrozen020UPC/inputbinding confirms same5%baselineSHA, oldtwo-stateU/C mechanism reusable with metric distinctions; no new targetstates orreclaimed FNAuniqueness.\nC021-19 testing-existing-cache: baseline U,C rightderivative bridge S=SU+SC proposed algebra andderived39floor table underindependentreview; newcaseproduction remainsfrozen.\n')
with(S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR008 '+now+': rootread ensembleR011independentaudit andsame-sourceoldUPC bridge, adopted concrete projectgrid. Currentjobsderive baseline mechanism only, no new inputs/targetreferences. Authorv008 integrates engineeringcase/Englishabstract. SourceoldRitz/fullFE/FNA distinctions andperformance failures preserved outside repetitive prose.\n')
(S/'rounds/R008.md').write_text('# R008 三输入工程案例已独核，接回原终版机制\n\n'+now+'。固定04:13:31截止，无重置。\n\n②R011独核三输入包络0must：各输入先独自求峰，跨输入取最大，区间[maxL,maxU]有效；基准Senv选原控制输入，非所有S最小。8%真包络最小9.228100%未达10，10%14.634810%达，均第7层；6/7可提前拒绝，8/10仍需完整复算。原逐输入强目标与RH4单输入通过全部保留。\n\n③R003核旧020实际字节与同SHA基准，允许复用5%→8%两行U/C表：第5层幅总下降而合成比例增大，屋顶两者均减小。它说明已知两态机制，不是事前预测。工程来源18CM/300Ritz和绝对输出校核的范围保留，旧N10质量95.18%而屋顶峰差25.15%、曲线差64.73%分清。\n\n当前①/④把这种机制接到基准导数S：U是各阶自己峰幅之和，P是总峰，C=P/U；希望只从现存基准导数给出SU、SC与S闭合，独审②R012在途，未提前认数值。没有新状态/波/ζ扫描。\n\n⑤v007图表与RH4通过已冻结，v008整合项目应用例、物理因子、简便对照、英文摘要；⑥三输入S对比图在途仅已审小表，不混未审派生值。继续把主线写通，不扩外围或放大提速/创新声称。\n',encoding='utf-8')
files=[]
for role,rrs in {'role1':['R006'],'role2':['R010','R011'],'role3':['R003'],'role4':['R010'],'role5':['R008']}.items():
 for rr in rrs:
  for p in (S/'roles'/role/rr).rglob('*'):
   if p.is_file() and not any(q in p.parts for q in ['local-cache','__pycache__']) and p.suffix in ['.md','.json','.csv','.py'] and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R008.py','status.json','threads.json','claims.md','runs.md','rounds/R008.md','R008-actual-snapshot.json','R007-postpublish-actual-snapshot.json','git-R007-receipt.json','automation-R007-update-receipt.json']:files.append(S/n)
files.append(R/'papers/damping-output-boundaries/manuscript/damping-prediction-session021-v007.md')
js(S/'git-R008-publication.json',dict(checkpoint='R008',time=now,message='research: verify engineering envelope decisions and bridge prior modal mechanism evidence',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(files))]))
print(json.dumps({'time':now,'files':len(set(files)),'bytes':sum(p.stat().st_size for p in set(files))}))
