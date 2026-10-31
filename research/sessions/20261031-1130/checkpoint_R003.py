from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2];now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert not(S/'git-R003-publication.json').exists()
d=json.loads((S/'status.json').read_text());d.update(checkpoint='R003-direct-forward',checkpoint_open=True,last_actual=now,active_plan='plan.md + plan-direct-forward-v003.md',recovery_file='rounds/R003.md')
tasks={
'role1':'R002 nullspace theorem/R003 forward units frozen; currentlyidle after reply; wait actual experiment, no peripheral task',
'role2':'R003 independent CM mass identification frozen12:08:34,0must adopted; newR004 B72/sum24/coordinate3+role6theory independent10min active',
'role3':'R001-R005 source notes frozen; own human90min ends13:11:38; optional precise citation check only',
'role4':'R0037200B/observability frozen12:09:49, actualidle verified; R004 direct actual300 no-fit forward .05/.08 CM-first then shear dispatched12:11,12min first results15min cap',
'role5':'R002 v002 frozen12:03:28, root full read; mass audit upgrade routed, preserve frozenv002; check actual before newv003',
'role6':'R003 observability theorem frozen; idle awaiting actual forward result, no repeated matrix experiment'}
d['current_tasks']=tasks;d['scientific_status'].update(engineering_mass='role2R003 independent source reconstruction passed0must; within18CM lumped model, not fullFE coverage',engineering_B='role4R003 frozen7200 inertia projection B; base/Cauchy pass; finite300 sumB above-mass maxrelative.000136626; role2R004 reviewactive',q_observability='36x300 CM translation matrixrank36;2/10/13 rowdistance .192081/.051293/.050333 nonzero; instantaneous arbitraryq notunique; temporal dynamics not excluded',direct_forward='role4R004 new actualRitz diagonal linear5/8 CM-first reference experiment active; no fitted shear map; no actual FNA q claim',manuscript='v002 frozen10218B SHA13645bd103bcbd4b5c67121680d50eb52bb7e143c96a2ce7c351cef6388b6e02; root fullread, later mass review update routed')
d['git'].update(current_HEAD_and_remote='845da158d6595cc3ef2371a20afb7b7d2aa59b04',last_success_HEAD='845da158d6595cc3ef2371a20afb7b7d2aa59b04',last_success_receipt='git-R002-receipt.json',publication='R002 normalpush remotesame; R003 preparation')
d['next_checkpoint']='Collect role4R004 first18CM prediction metrics and all preserved failure cases. Actual mode basis vs oldbaseline is explicit reference condition. First motion then shear, both operators retained, no sign/gain/timeshift tuning. Collect role2R004 independent B audit, author v003 once actualidle. Fixed cutoff15:30:11.'
write(S/'status.json',d)
t=json.loads((S/'threads.json').read_text())
cur={'role1':'a4ac1686-5034-48ef-9e7c-fe6208750c15:13','role2':'11a056de-2e65-48d9-90d8-2d3233b00402:25','role3':'3e1edb6e-1082-4df0-a7b1-358e7b877471:13','role4':'18d108d1-c129-40a5-b347-658f1f0c4b89:25','role5':'824ab043-4970-4d4a-8fa8-7ed81ac611bc:27','role6':'6334fe63-a9e8-4b7f-b356-e2608cd0403d:11'}
for q in t['threads']:q.update(task=tasks[q['role']],cursor=cur[q['role']],last_actual=now,last_actual_note='latest snapshots12:08-12:11; newR004 messages after actualidle; refresh realstatus, do not treat fileactive as running')
write(S/'threads.json',t)
with (S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC020-07 supported/CM-model numerical identification, reviewed: role2R003 independently reconstructed source arrays/SVD and totalmass before comparison;0must. Conditional18CM model class only, not fullFE location/mass certification.\nC020-08 testing/physical-data projection: role4R003 7200B/72selected/24summass frozen; root read README/results, role2R004 independent reviewactive. Not yet trueelastic coefficients.\nC020-09 supported/conditional linear-algebra: role6R003 singleq iff e_r in row(A); role4reports2/10/13 nonzero distances. Root readderivation and exactnull directions. Independentrole2reviewactive. Static arbitraryq nonuniqueness does not negate temporal dynamics recovery.\nC020-10 testing/forwardphysical-reference: newactualRitz300 Γfrommass, fixed5/8 inputstates, predictCM first and then two shear operators. No shearfit, no migrationoldinversecoef. Role4R004 sole newrun active.\n')
(S/'rounds/R003.md').write_text('# R003｜质量独审通过，进入无拟合前向检验\n\n实际记录'+now+'。②R003独立同源质量识别0must通过，根全文读；④R003全12层×300×XY7200惯性投影B已冻，基底/质量界通过，sumB最大质量偏差0.01366%。瞬时CM观测不足以唯一恢复2/10/13实际q，已知动力方程的时间观测另论。\n\n已派新任务：②R004独审72主B/24sum/3可观测距离及⑥理论，10min；④R004仅一次新actual300线性5/8前向，无输出拟合，先18CM运动对原生旧0/+3，再两种剪力参照，对全部三波保留失败；12min首交15min封存。①物理单位/符号先验契约已根全文读交④。⑤v002根全文已读，质量独审升级已路由，旧稿保留。\n\nGitR002 845da158d6595cc3ef2371a20afb7b7d2aa59b04远端一致，本点只已冻小文件。未改旧11项dirty、未读原件凭据/ETABSAPI。\n\n下一恢复：先看实际线程再收R004结果，不重复ODE；比对CM先验定义、正向/单位/输入，而非挑有利口径。若实际CM先失配，先查模型身份/接口，不能以低剪力误差倒推真实分担。固定总截止15:30:11、14:45:11成稿。\n',encoding='utf-8')
with (S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR003 '+now+': independentmassreview adopted; fullB/root-read candidate then independentaudit; actualnew no-fit forward role4R004 dispatched only afteridle. v002 readfull, preservehash. GitR003 frozen-only preparation, no fullarray upload.\n')
files=[]
for role,rounds in {'role1':['R002','R003'],'role2':['R003'],'role4':['R003'],'role5':['R002'],'role6':['R003']}.items():
 for rr in rounds:
  b=S/'roles'/role/rr
  assert any((b/n).exists()for n in ['manifest.json','freeze.json','delivery-manifest.json'])
  for p in b.rglob('*'):
   if p.is_file() and 'local-cache'not in p.parts and p.suffix in ['.md','.json','.csv','.py','.svg','.png'] and p.stat().st_size<1048576:files.append(p)
for n in ['checkpoint_R003.py','checkpoint_R002.py','status.json','threads.json','claims.md','runs.md','rounds/R003.md','plan-direct-forward-v003.md','engineering-method-draft-v001.md','topic-card-R002.md','automation-R002-update-receipt.json','git-R002-receipt.json']:files.append(S/n)
p=R/'papers/damping-output-boundaries/manuscript/physical-modal-shear-session020-v002.md';assert hashlib.sha256(p.read_bytes()).hexdigest()=='13645bd103bcbd4b5c67121680d50eb52bb7e143c96a2ce7c351cef6388b6e02';files.append(p)
write(S/'git-R003-publication.json',dict(checkpoint='R003',time=now,message='research: verify CM mass identification and publish physical modal projection tables',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(set(files))]))
print(json.dumps(dict(time=now,files=len(set(files))),ensure_ascii=False))
