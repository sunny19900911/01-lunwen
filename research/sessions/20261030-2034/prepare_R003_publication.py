from pathlib import Path
import json, hashlib, datetime
S=Path(__file__).resolve().parent
R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
st=json.loads((S/'status.json').read_text(encoding='utf-8'))
st.update(last_actual=now,checkpoint='R004',checkpoint_open=True,primary_task='All12 engineering comparison complete; physical coefficient scale check and full paper integration',next_checkpoint='Collect role1R003/role2R005 physical scale checks, role4R005 native peak ledger, role5R003 v003; no new fit')
st['root_R001']['audit']='role2 R001 independently passed48numbers'
st['independent_audit'].update(N36='role2/R00348numbers passed',all12='role2/R00448records288numbers passed; Story11 timing failure retained')
st['scientific_status'].update(N36='independently audited; physical high-modal attribution NOT established',all12='36 native peak comparisons and 48 held-out/cross-zeta records reviewed',physical_scale='pending role1R003/role2R005, very large within-high fitted cancellation')
st['current_tasks']={'role1':'R003 physical modal residue bound8min','role2':'R005 existing coefficients physical scale10min','role3':'R002 harmonic response ratio frozen;idle','role4':'R005 native all12 peak ledger8min','role5':'R003 full engineering manuscriptv00312min','role6':'R005 engineering interpretation without physical high attribution8min'}
st['role_tasks']='initial R001 tasks are completed history; current_tasks authoritative'
st['git'].update(last_success_HEAD='e60281649d81af4b888201a31d1b9ba08a72a9df',last_success_receipt='git-R002-receipt.json',publication='R003 reviewed all12/N36 publication in progress')
(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
th=json.loads((S/'threads.json').read_text(encoding='utf-8'))
sn=json.loads((S/'actual-snapshot-R003.json').read_text(encoding='utf-8'))
for q in th['threads']:
 p=next(x for x in sn if x['id']==q['threadId'])['data']['polls'][0]
 q.update(cursor=p['cursor'],actual_status=p['thread']['status'],task=st['current_tasks'][q['role']],last_snapshot=now)
 q['last_actual_note']='snapshot idle before new limited dispatch; role3 remains idle; recheck actual on wake'
(S/'threads.json').write_text(json.dumps(th,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
notes={
'rounds/R003.md':'''# R003真实检查点与角色交流
实际汇总21:29以后；上一共享文件21:04，不能据此虚称每15分钟均准时。科研任务在此间已实际完成并冻文件。
④N36及全12层扩展→②R003/R004独算，48条288数字通过。5%两波确定系数，8%三波沿用；全楼8%NRMSE0.469—4.552%，第11层RH4峰时误差5.06s保留。
④全楼原生36对峰→①⑥⑤；原生峰降6.851—29.173%，三波最弱层不同。①R002独核⑥屋顶，并给原生精确峰差D−M；SHW4屋顶旧点削弱31.915%，峰转移差2.7415个百分点，净29.173%。③R002单谐波幅比→⑤（不能套瞬态总峰）。
重要反证：高拟合组内部χ接近1，巨项相消不是已识别物理模态抵消。保持拟合输出预测身份，暂缓真实高阶占比；①R003推物理系数界、②R005核现有系数量级，属于主线解释的直接把关，不新拟合。⑤已获全楼结果开始v003；④仅从原生缓存推广36条D/M；⑥改写已有工程结论，不增加轨迹计算。
两图根实际查看，无缺字裁切；图2为拟合参照，物理解释待上述核验。仅已冻小件进入GitR003，活动R005不收。
''',
'topic-cards/T019-v002.md':'''# 主线演变：工程数据已扩到全楼
已实现：相同M/K与输入、模态阻尼5%到8%，全12层三波峰降差异有实数；保持输出系数不变对8%作预测，48条验证经独算。变化不是预设装置位置造成。
可直接使用：原峰同刻削弱D、新控制峰差M，峰差=D−M；工程屋顶已有一例明确说明旧点降幅不等于全程峰降。
未通过的物理链：高阶逆拟合项内部巨大抵消，不能凭总响应吻合便指定真实高阶占比。当前只检验小表物理系数量级，不恢复布置/CM外围。
论文以软件全楼结果、固定阻尼响应参照及控制峰转移方法为核心。三层机制短写；单频公式说明增阻尼的频率选择性，不当实际峰减幅定律。
'''}
for n,t in notes.items():(S/n).write_text(t,encoding='utf-8')
with (S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC019-05 reviewed：全12层48验证记录288数字核通过；原生36对峰降6.851—29.173%，Story11峰时失败保留。\nC019-06 proved accounting + reviewed example：P5−P8=D−M，M>=0；屋顶SHW4净29.1734%=31.9149%−2.7415%。不是纯相位或因果贡献。\nC019-07 pending physical interpretation：高拟合组内部χ近.99999，真实高阶物理占比暂不成立；小表物理量级检查正在进行。\n')
with (S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR003 completed: N36,all12; independent role2R003/R004; roof role1R002; source role3R002; figures role4R004; grouping role6R003/R004. New R004 limited physical scale/native peak ledger/v003 only. No N>36 or new fit.\n')
paths=[S/n for n in ['status.json','threads.json','claims.md','runs.md','actual-snapshot-R003.json','prepare_R003_publication.py','rounds/R003.md','topic-cards/T019-v002.md','git-R002-receipt.json']]
for role,roundid in [('role1','R002'),('role2','R003'),('role2','R004'),('role3','R002'),('role4','R002'),('role4','R003'),('role4','R004'),('role5','R002'),('role6','R003'),('role6','R004')]:
 d=S/'roles'/role/roundid
 paths.extend(p for p in d.iterdir() if p.is_file() and p.suffix in ['.md','.json','.csv','.py','.svg','.png'])
paths.append(R/'papers/damping-output-boundaries/manuscript/damping-superposition-session019-v002.md')
files=[]
for p in sorted(set(paths),key=str):
 assert p.is_file() and 'local-cache' not in p.parts and p.stat().st_size<1048576
 files.append({'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out=S/'git-R003-publication.json'
with out.open('x',encoding='utf-8') as f:json.dump({'checkpoint':'R003','message':'research: reviewed all-floor damping response and peak transfer','time':now,'files':files},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(files),'manifest':str(out)},ensure_ascii=False))
