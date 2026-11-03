from pathlib import Path
import subprocess,json,datetime
H=Path(__file__).resolve().parent;R=H.parents[2]
manifest=H/'git-R001-manifest.json';cfg=json.loads(manifest.read_text(encoding='utf-8'))
allowed={x['relative'] for x in cfg['files']}|{manifest.relative_to(R).as_posix()}
p=subprocess.run(['git','diff','--cached','--name-only','-z'],cwd=R,capture_output=True,check=True)
staged={x.decode('utf-8') for x in p.stdout.split(b'\0') if x}
assert staged and staged<=allowed,'Never alter unrelated staging'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
subprocess.run(['git','restore','--staged','--']+sorted(staged),cwd=R,check=True)
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=R).strip()
d={'at':datetime.datetime.now().astimezone().isoformat(),'attempt':'R001','result':'stopped before commit at ordinary whitespace check','reason':'Unified diff context blank lines contain their required space prefix; this diagnostic remains local and is excluded from the next publication. Paper text is unchanged.','HEAD_unchanged':head,'only_own_manifest_paths_unstaged':len(staged),'next_checkpoint':'R002','no_commit_or_push_attempted':True}
(H/'git-R001-precommit-failure.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
