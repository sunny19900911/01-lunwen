from pathlib import Path
import ast,csv,hashlib,json,subprocess,sys,datetime
S=Path(__file__).resolve().parent; R=S.parents[2]
def read(p): return json.loads(p.read_text('utf-8-sig'))
snap=read(S/'R002-thread-snapshot.json'); status=read(S/'status.json')
status.update(roles=snap['roles'],current_round='R002',checkpoint_open=True,last_completed_checkpoint='R001',canonical_manuscript='papers/damping-output-boundaries/manuscript/modal-shear-session009-v003.md',last_scientific_snapshot=snap['recorded_at'])
(S/'status.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n','utf-8')
(S/'threads.json').write_text(json.dumps({'session':S.name,'roles':snap['roles']},ensure_ascii=False,indent=2)+'\n','utf-8')
p=S/'claims.md'; text=p.read_text('utf-8')
new='''\nC007 R002已审：角色2独立核168行0/3减幅和72行三态比，六缓存组抽核一致；主方向无反增，减幅6.851271%—30.545762%。\nC008 R003已算未完成独审：三层H2同状态两阶重构QS2低估43.3215%/41.6360%，roof高估1.8839%/3.1416%；不认真实工程模态贡献。\nC009 文献基础：Song弹性输出与含阻尼输出分开，Londono及Conde已论Maxwell幅相/频率作用；不能称相位原理首次。\nC010 实际X主要质量参与阶2/4/10、Y为1/5/11，不是剪力贡献排名；三态摘要近同不认证完整振型相同。\nC011 真实三态72项实体/标签3为34高38低，只是原生输出对照，完整主体/输入身份未配对，不能归因为阻尼策略。\n'''
assert 'C007' not in text
p.write_text(text.rstrip()+'\n'+new,'utf-8')
p=S/'runs.md'; p.write_text(p.read_text('utf-8').rstrip()+'\n\n2026-10-20 19:47 R002：0/3全层减幅及三态比较通过角色2R003；角色1H2同状态模态表完成，角色2R004独审在途；四角色R004已派并actual active。源文件仅复用冻结缓存，无求解器。Git真实结果另见本检查点receipt。\n','utf-8')
files=[]
for role in range(1,7):
 for p in (S/'roles'/('role'+str(role))).glob('R00[123]*'):
  if p.is_file() and p.suffix in {'.md','.json','.py','.csv'}:
   if p.suffix=='.json':read(p)
   if p.suffix=='.py':ast.parse(p.read_text('utf-8-sig'))
   files.append(p)
for name in ['R001-root-check.json','R002-thread-snapshot.json','R002-root-check.py','rounds/R002.md','topic-card-R002.md','status.json','threads.json','claims.md','runs.md','git-R001-receipt.json']:files.append(S/name)
for i in range(1,4):files.append(R/'papers/damping-output-boundaries/manuscript'/('modal-shear-session009-v%03d.md'%i))
assert len(files)==len(set(files))
f=read(S/'roles/role1/R003-final-manifest.json')
for item in f['files']:
 p=S/'roles/role1'/item['file']; assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],str(p)
f=read(S/'roles/role5/R003-freeze.json')
for item in f['files']:
 p=Path(item['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],str(p)
counts={}
for name,n in [('R002-all14-main-axis-168.csv',168),('R003-three-model-peaks-72.csv',72),('R003-top3-participating-modes-18.csv',18)]:
 p=S/'roles/role4'/name
 rows=list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')));assert len(rows)==n;counts[name]=n
out={'checked_at':datetime.datetime.now().astimezone().isoformat(),'counts':counts,'role1_R003_manifest_ok':True,'v003_freeze_ok':True,'scope':'Frozen R001-R003 only; current R004 excluded; candidate theory remains awaiting role2','file_count':len(files)}
check=S/'R002-root-check.json';check.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8');files.append(check)
args=[sys.executable,'-X','utf8',str(S/'checkpoint_git.py'),'--label','R002','--files',*[p.relative_to(R).as_posix() for p in files]]
result=subprocess.run(args,cwd=R,text=True,capture_output=True)
print(result.stdout);print(result.stderr);raise SystemExit(result.returncode)
