from pathlib import Path
import hashlib,json,datetime,argparse,ast
H=Path(__file__).resolve().parent;R=H.parents[2]
ap=argparse.ArgumentParser();ap.add_argument('checkpoint');a=ap.parse_args()
old=R/'research/revisions/20261103-error-coexistence/publish_checkpoint.py'
p=H/'publish_checkpoint.py'
if not p.exists():
    s=old.read_text(encoding='utf-8').replace("p.name.startswith('p06-mechanism-classification-')","p.name.startswith('p06-actual-damper-session025-')")
    s=s.replace('len(b)<1048576','len(b)<(3145728 if p.suffix==\'.docx\' else 1048576)')
    ast.parse(s);p.write_text(s,encoding='utf-8',newline='\n')
manifest=H/('git-'+a.checkpoint+'-manifest.json');assert not manifest.exists()
paths=[]
for p in sorted(H.rglob('*')):
    if not p.is_file() or 'local-cache' in p.parts or '__pycache__' in p.parts:continue
    if p.name.startswith('git-') and p.name.endswith('-manifest.json'):continue
    if p.suffix not in ['.md','.json','.csv','.py','.svg','.png']:continue
    if 'roles/response/R002/' in p.as_posix() and p.suffix in ['.png','.svg'] and '-v003' not in p.name:continue
    paths.append(p)
M=R/'papers/damping-output-boundaries/manuscript'
if a.checkpoint!='R001':
    paths.extend(sorted(M.glob('p06-actual-damper-session025-v*.md')))
if a.checkpoint=='FINAL':
    d=json.loads((H/'final-visual-review.json').read_text(encoding='utf-8'));assert d['passed']
    paths.append(R/d['docx'])
cfg={'checkpoint':a.checkpoint,'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'message':'P06 actual damper application '+a.checkpoint,'files':[{'relative':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]}
assert len(paths)==len(set(paths))
manifest.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checkpoint':a.checkpoint,'files':len(paths),'total_bytes':sum(p.stat().st_size for p in paths)},ensure_ascii=False))
