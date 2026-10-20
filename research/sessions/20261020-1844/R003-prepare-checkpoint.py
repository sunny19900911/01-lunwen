from pathlib import Path
import ast,json,hashlib,subprocess,sys
S=Path(__file__).resolve().parent;R=S.parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
snap=read(S/'R003-checkpoint-snapshot.json');v=read(S/'status.json')
v.update(roles=snap['roles'],current_round='R003',checkpoint_open=True,last_completed_checkpoint='R002',canonical_manuscript='papers/damping-output-boundaries/manuscript/modal-shear-session009-v005.md',last_scientific_snapshot=snap['recorded_at'])
(S/'status.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
(S/'threads.json').write_text(json.dumps({'session':S.name,'roles':snap['roles']},ensure_ascii=False,indent=2)+'\n','utf-8')
p=S/'claims.md';t=p.read_text('utf-8');assert 'C012-review' not in t
t+='\nC012-review role2R005限定范围采纳真实Story8六例同刻力表：RH4X/Y独立缓存复算，其余四例小表算术；reviewed observed-data，不扣QS。\nC013 candidate role1R004 H2各阶峰幅不同，控制时刻三项同向，第三项改善被前两项变化部分抵消；role2R006独审在途，不称抵消损失。\nC014 reviewed numerical-test 主控独组role4R004统计48行192数字零差，沿层减幅图可用；自身波形不同时间峰不拼同刻剖面。\n'
p.write_text(t,'utf-8')
p=S/'runs.md';p.write_text(p.read_text('utf-8').rstrip()+'\n\n2026-10-20 20:03 R003：Story8实际装置时序通过role2R005；H2同刻表独审在途。唯一作者v006在途，已冻v005主控全文读取。角色4做R006时序图，角色1后验幅值参照R005。Git按本次冻结白名单执行，详情receipt。\n','utf-8')
allowed={1:['R004'],2:['R004','R005'],4:['R004','R005'],5:['R004','R005'],6:['R004']}
files=[]
for role,prefixes in allowed.items():
 for pre in prefixes:
  files.extend(p for p in (S/'roles'/('role'+str(role))).glob(pre+'*') if p.is_file() and p.suffix in {'.md','.py','.csv','.svg','.json'})
rootnames=['R003-prepare-checkpoint.py','R003-checkpoint-snapshot.json','R003-thread-snapshot.json','R003-root-profile-check.py','R003-root-profile-check.json','rounds/R003.md','rounds/R003-in-progress.md','next-checkpoint-handoff.md','status.json','threads.json','claims.md','runs.md','git-R002-receipt.json']
files.extend(S/n for n in rootnames)
files.extend(R/'papers/damping-output-boundaries/manuscript'/('modal-shear-session009-v%03d.md'%i) for i in [4,5])
assert len(files)==len(set(files))
sha_checks=0
for p in files:
 if p.suffix=='.py':ast.parse(p.read_text('utf-8-sig'))
 if p.suffix!='.json':continue
 d=read(p)
 if not isinstance(d,dict):continue
 for item in d.get('files',[]):
  if not isinstance(item,dict) or not item.get('sha256'):continue
  name=item.get('file') or item.get('path')
  if not name:continue
  target=Path(name)
  if not target.is_absolute():target=p.parent/target
  if not target.exists():target=R/name
  assert target.exists(),str(target)
  assert hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256'],str(target)
  sha_checks+=1
check=S/'R003-freeze-check.json';check.write_text(json.dumps({'manifest_sha_checks':sha_checks,'explicit_files':len(files),'current_tasks_excluded':['role1R005','role2R006','role3R003','role4R006','role5R006'],'candidate_labels_preserved':True},ensure_ascii=False,indent=2)+'\n','utf-8');files.append(check)
cmd=[sys.executable,'-X','utf8',str(S/'checkpoint_git.py'),'--label','R003','--files',*[p.relative_to(R).as_posix() for p in files]]
p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);print(p.stdout);print(p.stderr);raise SystemExit(p.returncode)
