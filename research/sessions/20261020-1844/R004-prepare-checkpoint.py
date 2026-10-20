from pathlib import Path
import ast,json,hashlib,subprocess,sys,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];read=lambda p:json.loads(p.read_text('utf-8-sig'))
snap=read(S/'R004-thread-snapshot.json');v=read(S/'status.json')
v.update(roles=snap['roles'],current_round='R004',checkpoint_open=True,last_completed_checkpoint='R003',canonical_manuscript='papers/damping-output-boundaries/manuscript/modal-shear-session009-v006.md',last_scientific_snapshot=snap['recorded_at'])
(S/'status.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');(S/'threads.json').write_text(json.dumps({'session':S.name,'roles':snap['roles']},ensure_ascii=False,indent=2)+'\n','utf-8')
p=S/'claims.md';t=p.read_text('utf-8');assert 'C013-review' not in t
t+='\nC013-review role2 R006独审采用role1R004共同时间与各阶峰比；reviewed numerical-test。两个控制时刻三项同向，不能称抵消损失。\nC015 supported numerical-test reviewed role2R007独核人为幅值参照，逐阶峰匹配但合成峰不匹配；不具预测/相位独立归因资格。\nC016 supported literature reviewed role3R003核CSI2016 PDF403印381，要求改变模态数检查具体动态响应；既有原则非本文首创。\n'
p.write_text(t,'utf-8')
p=S/'runs.md';p.write_text(p.read_text('utf-8').rstrip()+'\n\nR004约20:19准备，实际提交/同步时间以git-R004-receipt为准：已审峰幅参照、CSI定位、四幅自绘PNG及v006。在途R008/R007未加入；不声称所有目标间隔严格按时。\n','utf-8')
groups={1:['R005'],2:['R006','R007'],3:['R003'],4:['R006','R007'],5:['R006'],6:['R005']};files=[]
for role,pres in groups.items():
 for pre in pres:files.extend(p for p in (S/'roles'/('role'+str(role))).glob(pre+'*') if p.is_file() and p.suffix.lower() in {'.md','.json','.csv','.py','.cjs','.svg','.png'})
names=['R004-prepare-checkpoint.py','R004-thread-snapshot.json','rounds/R004.md','topic-card-R004.md','routing-2006.md','status.json','threads.json','claims.md','runs.md','checkpoint_git.py','git-R003-receipt.json']
files.extend(S/n for n in names);files.append(R/'papers/damping-output-boundaries/manuscript/modal-shear-session009-v006.md')
assert len(files)==len(set(files));checks=0
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
  checks+=1
out=S/'R004-freeze-check.json';out.write_text(json.dumps({'checked_at':datetime.datetime.now().astimezone().isoformat(),'sha_checks':checks,'files':len(files),'visual_root_review':['R007-six-case-reduction-profiles.png','R007-local-modal-terms.png','R007-Story8-QT-QD-two-cases-qa.png'],'role4_four_images_reviewed':True,'new_wording_figures_pending_R008':True},ensure_ascii=False,indent=2)+'\n','utf-8');files.append(out)
p=subprocess.run([sys.executable,'-X','utf8',str(S/'checkpoint_git.py'),'--label','R004','--files',*[p.relative_to(R).as_posix() for p in files]],cwd=R,capture_output=True,text=True);print(p.stdout);print(p.stderr);raise SystemExit(p.returncode)
