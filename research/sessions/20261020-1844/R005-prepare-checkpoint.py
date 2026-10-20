from pathlib import Path
import ast,json,hashlib,subprocess,sys,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];read=lambda p:json.loads(p.read_text('utf-8-sig'))
snap=read(S/'R005-checkpoint-snapshot.json');snap['recorded_at']='2026-10-20T20:43:47+08:00';(S/'R005-checkpoint-snapshot.json').write_text(json.dumps(snap,ensure_ascii=False,indent=2)+'\n','utf-8')
v=read(S/'status.json');v.update(roles=snap['roles'],current_round='R005',checkpoint_open=True,last_completed_checkpoint='R004',canonical_manuscript='papers/damping-output-boundaries/manuscript/modal-shear-session009-v007.md',last_scientific_snapshot=snap['recorded_at'])
(S/'status.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8');(S/'threads.json').write_text(json.dumps({'session':S.name,'roles':snap['roles']},ensure_ascii=False,indent=2)+'\n','utf-8')
groups={1:['R006','R007'],2:['R008'],4:['R008'],5:['R007']};files=[]
for role,pres in groups.items():
 for pre in pres:files.extend(p for p in (S/'roles'/('role'+str(role))).glob(pre+'*') if p.is_file() and p.suffix.lower() in {'.md','.json','.csv','.py','.cjs','.svg','.png'})
files.extend(S/n for n in ['R005-prepare-checkpoint.py','R005-thread-snapshot.json','R005-checkpoint-snapshot.json','rounds/R005.md','routing-2026.md','word-delivery-contract.md','status.json','threads.json','claims.md','runs.md','git-R004-receipt.json'])
files.append(R/'papers/damping-output-boundaries/manuscript/modal-shear-session009-v007.md');assert len(files)==len(set(files));checks=0
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
  assert target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256'],str(target)
  checks+=1
out=S/'R005-freeze-check.json';out.write_text(json.dumps({'checked_at':datetime.datetime.now().astimezone().isoformat(),'sha_checks':checks,'explicit_files':len(files),'v007_full_read':True,'current_v008_not_published_this_checkpoint':True,'no_raw_arrays_or_original_workbooks':True},ensure_ascii=False,indent=2)+'\n','utf-8');files.append(out)
p=subprocess.run([sys.executable,'-X','utf8',str(S/'checkpoint_git.py'),'--label','R005','--files',*[p.relative_to(R).as_posix() for p in files]],cwd=R,capture_output=True,text=True);print(p.stdout);print(p.stderr);raise SystemExit(p.returncode)
