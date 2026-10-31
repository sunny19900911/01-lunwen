from pathlib import Path
from datetime import datetime, timezone, timedelta
import json, hashlib
S=Path(__file__).resolve().parent; R=S.parents[2]
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
tasks={
'role1':('R002 same-source PF-ratio nullspace identification derivation, dispatched11:55, active','a4ac1686-5034-48ef-9e7c-fe6208750c15:12'),
'role2':('R003 independent actual mass identification from source CM/PF/mu; no role4 code import, dispatched12:01','11a056de-2e65-48d9-90d8-2d3233b00402:19'),
'role3':('R001-R005 source paragraphs frozen; human own window until13:11:38; no third literature','3e1edb6e-1082-4df0-a7b1-358e7b877471:13'),
'role4':('R002 mass identification frozen11:58:31, actualidle; next all-floor B after new task','18d108d1-c129-40a5-b347-658f1f0c4b89:22'),
'role5':('R002 v002 integrated manuscript dispatched12:01 after actualidle; source/results reviewed status explicit','824ab043-4970-4d4a-8fa8-7ed81ac611bc:20'),
'role6':('R002 conditional selected3-mode floor comparison frozen11:58:14; idle','6334fe63-a9e8-4b7f-b356-e2608cd0403d:11')}
d=json.loads((S/'status.json').read_text());d.update(phase='mainline-running',checkpoint='R002',checkpoint_open=True,last_actual=now,theory_addendum='plan-theory-addendum-v002.md',current_tasks={k:v[0]for k,v in tasks.items()},primary_task='Actual same-source 18-CM mass identification -> all-floor modal inertia projection -> output recovery validation, no inverse shear fit',recovery_file='rounds/R002.md')
d['scientific_status'].update(engineering_mass='role4 R002 frozen: first100 X/Y rank17 positive18 masses; last200 validation; total47440864.269713kg; root read full code/results; independent role2R003 active',engineering_data='600 oldmass/actualmodal consistency adopted only as conditional check; new same-source identification stronger; actualLinModRitz so no automatic elastic shear attribution',engineering_method='role2R002 independently passed U/P/C, exact2DOF steady-state example and known3floor small-table identities; not earthquake engineering peak guarantee')
d['next_checkpoint']='Collect role1R002/role2R003 independent mass audit, role4 next all12floor300 B and physical output gate; authorv002; do not reidentify same masses or rerun old inverse fits.'
write(S/'status.json',d)
t=json.loads((S/'threads.json').read_text())
for q in t['threads']:
 q.update(task=tasks[q['role']][0],cursor=tasks[q['role']][1],last_actual=now,last_actual_note='actual compact snapshots11:58; new dispatch12:01 where stated; refresh before further dispatch')
 q['actual_status']={'type':'idle' if q['role']in ['role4','role6'] else 'active','activeFlags':[]}
write(S/'threads.json',t)
with (S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC020-06 supported/conditional, reviewed: role2R002 independent dynamic-stiffness/Eigen routes validate U/P/C and twoDOF steady harmonic example; known3floor9B and3ratio identities independently checked. Not commonzeroIC finiteearthquake example.\n\nC020-07 testing/observed-data+linear-algebra: actualCM/PF ratios first100 identify positive18 directional masses within CM lumped model (rank17), remaining200 verify; total47440864.269713kg X/Y. No oldmass used until postcomparison. Root read full code/results; role2R003 independent check pending. Does not certify fullFE coverage or Ritz elastic output.\n')
with (S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR002 actual '+now+': collected role4R001/R002 frozen smalltable results; root full code/README/results read, no rawextract or rerun. Role2R002 frozen method independent check adopted; dispatchedrole2R003 actualmass independent; role5v002 integration. New Git manifest only frozenR001/R002 and sourceR001-R005, excludes activeR002 ofrole1/5 and role2R003.\n')
(S/'rounds/R002.md').write_text('# R002｜同源质量识别与真实分担系数的接入\n\n实际记录：'+now+'。窗口11:30:11—15:30:11不变。\n\n已新增：④从实际CM与原生参与列的全阶共同投影关系，在前100阶独立识别18个正方向质量，约束rank17；后200阶检查，X/Y总质量47,440,864.269713kg。之后才读旧质量作事后对照，逐组差3.60e-14。根已读全文代码/README/结果，②R003独算中。实际Modal为LinModRitz，识别质量不自动认证弹性剪力恢复。\n\n②R002已独核⑥两层稳态解析与U/P/C、根3层9系数/3比值小表，0must。三层表是已知模型，非工程实测。③同一本Song§5.2给出直接MphiGamma/基底有效质量出处，局部切口公式属经典应用。⑤v002整合已派。\n\n下一步：实际全12层300阶惯性投影系数＋质量恒等/观测可辨识检验，之后用原生响应验证恢复口径。禁止把质量率、仅三阶内部权重直接称真实剪力分担；不回到N6/12/24/36输出逆拟合。\n',encoding='utf-8')
# Frozen directories only; R002 new outputs being authored are deliberately excluded.
files=[]
for role,rounds in {'role1':['R001'],'role2':['R001','R002'],'role3':['R001','R002','R003','R004','R005'],'role4':['R001','R002'],'role5':['R001'],'role6':['R001','R002']}.items():
 for rr in rounds:
  base=S/'roles'/role/rr
  if base.is_dir():
   for p in base.rglob('*'):
    if p.is_file()and 'local-cache'not in p.parts and p.suffix in ['.md','.json','.csv','.py','.svg','.png']and p.stat().st_size<1048576:files.append(p)
for n in ['status.json','threads.json','claims.md','runs.md','plan-theory-addendum-v002.md','root-R001-model-definition.json','save_R001_handoff.py','checkpoint_R002.py','rounds/R001-collection.md','rounds/R002.md','git-R001-receipt.json']:files.append(S/n)
files.append(R/'papers/damping-output-boundaries/manuscript/physical-modal-shear-session020-v001.md')
manifest=dict(checkpoint='R002',time=now,message='research: identify modal CM masses and independently verify superposition mechanism',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(set(files))])
assert not(S/'git-R002-publication.json').exists()
write(S/'git-R002-publication.json',manifest)
print(json.dumps(dict(actual=now,files=len(manifest['files']),total_bytes=sum(x['bytes']for x in manifest['files'])),ensure_ascii=False))
