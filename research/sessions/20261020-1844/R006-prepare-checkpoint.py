from pathlib import Path
import ast,json,hashlib,subprocess,sys,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];read=lambda p:json.loads(p.read_text('utf-8-sig'));v=read(S/'status.json');v.update(phase='final-writing',no_new_scientific_dispatch=True,current_round='R006',checkpoint_open=True,last_completed_checkpoint='R005',canonical_manuscript='papers/damping-output-boundaries/manuscript/modal-shear-session009-v009.md');(S/'status.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
groups={2:['R009','R010'],3:['R004'],5:['R008','R009'],6:['R006']};files=[]
for role,pres in groups.items():
 for pre in pres:files.extend(p for p in (S/'roles'/('role'+str(role))).glob(pre+'*') if p.is_file() and p.suffix.lower() in {'.md','.json','.csv','.py','.ps1','.cjs','.svg','.png'})
files.extend(S/n for n in ['R006-prepare-checkpoint.py','rounds/R006.md','topic-card-final-stage.md','root-v008-editorial-review.md','automation-final-phase-readback.json','status.json','threads.json','claims.md','runs.md','checkpoint_git.py','git-R005-receipt.json'])
files.extend(R/'papers/damping-output-boundaries/manuscript'/('modal-shear-session009-v%03d.md'%i) for i in [8,9]);assert len(files)==len(set(files));checks=0
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
source=R/'papers/damping-output-boundaries/manuscript/modal-shear-session009-v009.md';assert hashlib.sha256(source.read_bytes()).hexdigest()=='017fc68b82971b1ed6c3abe6bfbc82901a3bd76e6db846a41c68935d65a856ab'
out=S/'R006-freeze-check.json';out.write_text(json.dumps({'at':datetime.datetime.now().astimezone().isoformat(),'sha_checks':checks,'files':len(files),'v008_and_v009_master_full_read':True,'render_ps1_static_parser':'passed','current_minimal_v010_revision_excluded':True,'no_word_QA_claimed_yet':True},ensure_ascii=False,indent=2)+'\n','utf-8');files.append(out)
p=subprocess.run([sys.executable,'-X','utf8',str(S/'checkpoint_git.py'),'--label','R006','--files',*[p.relative_to(R).as_posix() for p in files]],cwd=R,capture_output=True,text=True);print(p.stdout);print(p.stderr);raise SystemExit(p.returncode)
