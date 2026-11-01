from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-R006-publication.json').exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
tasks={'role1':'R005 competingpeakwarning frozen .2480256362pp, shortaudit inrole2R009', 'role2':'R009 max12needed15 RH4 independent audit+shortpeakwarning math sent23:54, active; SHW4R0080must adopted', 'role3':'R002 public source frozen idle, no filler', 'role4':'R009 max10needed12 factorize c sign causes using existing three baseline caches andmodalperiods; active no newODE', 'role5':'R007 max10needed12 v006 mainS table andmodal explanation officiallyadopted; SHW4review passed sent, active', 'role6':'R006 max10needed12 standardchart figures from reviewed SHW3S andmodalterms; no new science, active'}
snap=json.loads((S/'R006-actual-snapshot.json').read_text(encoding='utf-8'));t=json.loads((S/'threads.json').read_text(encoding='utf-8'))
for x in t['threads']:
 z=next(v for v in snap if v['role']==x['role']);x.update(cursor=z['cursor'],actual_status=z['status'],task=tasks[x['role']],last_actual=now)
js(S/'threads.json',t)
d=json.loads((S/'status.json').read_text(encoding='utf-8'));d.update(last_actual=now,checkpoint='R006-S-reviewed-SHW4-counterexample',checkpoint_open=True,current_tasks=tasks,recovery_file='rounds/R006.md')
d['scientific_status'].update(SHW4_candidate='reviewedrole2R0080must rootfullread:12955fields, selectedownRK4; 48curvescovered,2pointlowimprovementmisses caught; S1slowest but6%truthStory6, 2/1pairinversions;no universalStory5slowest',RH4_candidate='role4R008 frozen rootfullreportread pendingrole2R009:48coverage; 7%2nd firstpass underunchangedrule,minDL12.41229%,maxwidth3.821629pp;truthmin13.731792%Story7, no reliabilityprobabilityclaim;2/2rankinversions',simple_baselines='role6R005 source report read, perlayerS*b vsuniformmedianS*b vswholecurve pointandinterval separately, quantitative independentreview pending; no dominance claim',manuscript='v005 frozen23:44:18/root全文read; publicauditednumbers included but noactualS due adoptiontiming. Newv006 currentmustinsert reviewed S/mastermodal table; oldbytes preserved')
d['next_task']='Collect role2R009 RH4 audit andpeakwarning; factor signsR009 andfiguresR006 freeze then independentreview/rootimageview, authorv006. Later review simplebaselineaggregate and prepare engineering synthesis, no new solver/layout. NextGitR007 ~15min, writing03:13:31/end04:13:31 fixed.'
js(S/'status.json',d)
with(S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC021-12 upgraded-reviewed: role2R00715layerS/3636modalterms/19910fields0must, rootadopted and authornotified; S5/roof13modeopposingsigns concrete.\nC021-14 reviewed-SHW4: role2R00812955fields/ownselectedRK4 verify first-rankcounterexampleStory1->Story6 at6%,2/1pairinversions despitehighrho;48curveintervalscovered,pointmisses2 caught. Doesnot invalidateconditional localderivative law butinvalidatesuniversalrankclaim.\nC021-15 testing-RH4: rootreportread firstcandidatepass7%2nd fixedthresholds verifiedbyproducer, independentR009pending; no acceptance/physicsprobability conclusion.\n')
with(S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR006 '+now+': rootreadSapprovedauthor tables,SHW4independentaudit,RH4candidate report, v005fulltext, role1warning androle6simplebaseline report. Fresh actualsnapshots; four boundedcurrenttasks afteractualidle; no prematureRH4adoption. Originaldirty/arrays/oldmanuscripts preserved.\n')
(S/'rounds/R006.md').write_text('# R006 工程主表已独核，另一输入给出排序反例\n\n'+now+'。六小时终点04:13:31不变。\n\n根正式采用②R007的15层S与模态改善来源：SHW3第5层S2.132064、屋顶11.723849，第13阶−.527229/+7.173442，主项余项闭合。用户已通知这条有范围的结果，不把该模式定性永久有利/不利。\n\n②R008 SHW4独核通过0must。原基准排序最慢第1层而6%目标最慢第6层，差仅.027379pp但首位真实错；2/1排序倒置保留。48区间覆盖与两项漏判接住可采用。不能再宣传第5层总最慢。\n\nRH4第三输入已冻，根全文报告读：第7层控制，7%二阶首次通过原区间/宽度规则，目标参照确认，但②R009独审正在进行，本点仍候选不升级。①固定局部峰一阶交点只是预警，②本项短核，根已读标量.2480pp提示。⑥简单基线对照仍待独核，无普遍复杂方法支配结论。\n\n④新R009仅由现存基准提取同一模式c变号的固定B/ω与变化z/峰号因子，完成物理解释；⑥从已审小表作两图，根待逐图查看；⑤v006纳正式S主表/工程句，不继续外围。全部在写文件不入本点Git。\n',encoding='utf-8')
files=[]
for role,rrs in {'role1':['R005'],'role2':['R007','R008'],'role4':['R007','R008'],'role5':['R006'],'role6':['R005']}.items():
 for rr in rrs:
  for p in (S/'roles'/role/rr).rglob('*'):
   if p.is_file() and not any(q in p.parts for q in ['local-cache','__pycache__']) and p.suffix in ['.md','.json','.csv','.py'] and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R006.py','status.json','threads.json','claims.md','runs.md','rounds/R006.md','R006-actual-snapshot.json','git-R005-receipt.json','automation-R005-update-receipt.json','automation-postR005-S-adoption-receipt.json','root-R005-S-adoption.md']:files.append(S/n)
files.append(R/'papers/damping-output-boundaries/manuscript/damping-prediction-session021-v005.md')
js(S/'git-R006-publication.json',dict(checkpoint='R006',time=now,message='research: verify floor sensitivity mechanism and retain cross-input rank counterexamples',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(files))]))
print(json.dumps({'time':now,'files':len(set(files)),'bytes':sum(p.stat().st_size for p in set(files))}))
