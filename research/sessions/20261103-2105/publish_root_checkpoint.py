from pathlib import Path
import hashlib,json,subprocess,sys,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
files=[p for p in S.iterdir()if p.is_file()and p.suffix in ['.md','.py','.json','.csv']and not p.name.startswith('git-')]
for dirname in ['equivalent','screen']:
 files += [p for p in (S/'roles'/dirname).rglob('*')if p.is_file()and 'local-cache'not in p.parts and p.suffix in ['.json','.csv']]
files=[p for p in files if p.name not in ['draft-build-v001.json','equivalent-text-refinement.json']]
assert all(p.stat().st_size<1048576 for p in files)
cfg={'checkpoint':'R001','frozen_at':datetime.datetime.now().astimezone().isoformat(),'message':'P06 simultaneous force, local equivalence and near-peak tests','scope':'root frozen calculations only; manuscript and in-progress role files excluded','files':[{'relative':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(files)]}
manifest=S/'git-R001-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
res=subprocess.run([sys.executable,'-X','utf8',str(S/'publish_checkpoint.py'),'--manifest',str(manifest)],cwd=R)
raise SystemExit(res.returncode)
