from pathlib import Path
import json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
st=json.loads((S/'status.json').read_text(encoding='utf-8'))
st.update(last_actual=now,checkpoint='R002',checkpoint_open=False,independent_audit={'N12':'role2/R001 8records48numbers0must','N24':'role2/R002 8records48numbers0must'},current_tasks={'role1':'R001 Story5 explanation frozen;idle','role2':'N12 andN24 independently audited;idle','role3':'2existing primary citations frozen;idle','role4':'R002 N36elastic2rc finite convergence test in progress,do not repeat','role5':'R002 manuscriptv002 concrete integration dispatched','role6':'R002 N12to24 grouped interpretation frozen;idle,next highgroup aggregate check afterN36freeze'},next_checkpoint='collect frozenN36, route finite grouped stability >=13 to role6 and numerical checks to role2; no N beyond36; manuscriptv002 and next Git tick')
st['git']['last_success_HEAD']='53b60df8da82e4b5455fbdc5816f853fbb413e12';st['git']['publication']='R002 frozen first-loop role exchange publication pending'
(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
threads=json.loads((S/'threads.json').read_text(encoding='utf-8'))
for q in threads['threads']:
 q['task']=st['current_tasks'][q['role']];q['last_check_note']='actualcompleted before nexttask or frozen scientific output; recheck on wake'
(S/'threads.json').write_text(json.dumps(threads,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
texts={
'claims.md':'''# 主张账本R002
C019-01 supported/reviewed numerical fitted-model：原生5%两波确定固定映射，8%不重拟合。N12elastic Story5跨ζNRMSE2.58—4.07%、峰误差<.125%，Story12误差45.28—60.19%；角色2独立8记录48数字核通过。
C019-02 supported/reviewed numerical fitted-model：N24elastic Story12固定8%误差2.576—5.034%、5%留出4.384%；Story5固定8%1.328—1.763%，角色2独立8记录48数字核通过。不能升级真实单阶唯一，N24前12系数变52%是截断不稳定警告。
C019-03 supported conditional grouping：Story5的1—3阶组合N6to12差约原生L2.50—.65%，峰附近抵消弱；其幅值削弱随波不同，与整体降幅差异对应。不是全部差异纯相位，也不是L2比能量份额。role1/6冻结，仍需主文保留输出拟合身份。
C019-04 testing：N24to36的低高组整体收敛。N36候选输出改善不单独证明13—24高阶组稳定；下一核把>=13聚合（N24中13—24、N36中13—36）与1—12对比，保留新增组和旧项的补偿，不再无限加阶。
''',
'runs.md':'''# 当前运行与去重R002
已执行：root-R001 N6/N12八配置96行；role4/R001 N24两算子24行；role2/R001、R002分别8条独立核；role6/R001、R002组敏感性（无新拟合）；role1/R001主组解释。
正在：role4/R002唯一N36elastic2rc收敛；role5/R002新稿v002整合。actual状态优先，不重复仍active任务。
待依赖：N36冻结后②核数字、⑥只核<=12与>=13合成组的稳定性并做真实峰同刻幅值/波形；无N>36计划。旧300成功证据复用不重跑。
Git：R001正常push53b60df已远端SHA核等同；R002只收本轮冻结小文件，publisher按明确manifest执行。每15分钟新检查点用新ID，receipt已存在先看，不重复commit。local-cache永远排除。
''',
'rounds/R002.md':'''# 首次15分钟角色交流与进展汇总
真实窗口20:34:43—22:34:43。首组新计算20:38已完成，20:44初始白名单Git已推53b60df并远端核验。
①Story5实数→⑤；②N12与N24独立核数→①⑤；③原文两条→①⑤；⑥主组/小组稳定性→①⑤；④N24新结果→②独审，并派仅一次N36收敛；⑥N24组记账→后续低高组检查。上述交流已正式跨六现有聊天并存角色输出。
核心结果：N12能复原Story5但不能屋顶，N24在同训练/验证条件下显著改善屋顶，已独审。Story5峰附近组抵消弱，不能为迎合相位论而强说抵消主导。N24高阶项缺进一步稳定性，N36候选不得先当真单阶。
当前③待命，不为凑角色忙碌新搜文献；①/⑥科学输出冻结；②空闲等N36冻结；④唯一N36，⑤v002整合。实际15分钟汇总写于约20:58，不伪称精确20:49。第一次上传20:44，第二次本检查点执行。
''',
'topic-cards/T019-v001.md':'''# 已选主线的演变
问题仍是增加模态阻尼改变响应叠加、影响各层剪力，不回到布置原因。
旧状态：两层只有总曲线差，工程新分解未执行。本轮现有5%->8%固定映射已真正执行并独审，Story5低阶参照可用；屋顶N12失败经N24显著改善。
最强支持：跨波/跨ζ两层预测误差小，稳定低阶主组的响应幅度变化可解释Story5降幅差。反对证据：峰附近抵消弱，不支持把该层现象主要归因相位抵消；N24与N36更高子组可相互补偿，低总误差不保证细阶唯一。
后续仅一次N36收敛后优先报告稳定低组与>=13高组、残差，论文区分机制存在性与真实工程解释。无首创/期刊命中率承诺，不另要求用户选题。
'''}
for n,c in texts.items():
 p=S/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(c,encoding='utf-8')
root=['status.json','claims.md','runs.md','threads.json','git-R001-receipt.json','publish_checkpoint.py','prepare_R002_publication.py','rounds/R002.md','topic-cards/T019-v001.md']
paths=[S/n for n in root]
for role,roundid in [('role1','R001'),('role2','R001'),('role2','R002'),('role4','R001'),('role5','R001'),('role6','R001'),('role6','R002')]:
 d=S/'roles'/role/roundid
 assert d.is_dir()
 paths.extend(p for p in d.iterdir()if p.is_file()and p.suffix in ['.md','.json','.csv','.py'])
paths.extend(p for p in (S/'roles/role3').glob('R001-*')if p.is_file()and p.suffix in ['.md','.json'])
paths.append(R/'papers/damping-output-boundaries/manuscript/damping-superposition-session019-v001.md')
paths=sorted(set(paths),key=str)
files=[]
for p in paths:
 assert p.is_file() and 'local-cache'not in p.parts and p.stat().st_size<1048576
 files.append({'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
cfg={'checkpoint':'R002','time':now,'message':'research: session019 reviewed engineering modal comparisons','scope':'frozen role artifacts plus reviewed candidate interpretation; no arrays/raw/old dirty work','files':files}
with (S/'git-R002-publication.json').open('x',encoding='utf-8')as f:json.dump(cfg,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(files),'manifest':str(S/'git-R002-publication.json')},ensure_ascii=False))

