from pathlib import Path
import argparse,hashlib,json,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
ap=argparse.ArgumentParser();ap.add_argument('checkpoint');a=ap.parse_args()
p=S/'publish_checkpoint.py'
if not p.exists():
    source=R/'research/sessions/20261103-1458/publish_checkpoint.py'
    text=source.read_text(encoding='utf-8').replace('p06-actual-damper-session025-','p06-actual-main-session026-')
    p.write_text(text,encoding='utf-8',newline='\n')
manifest=S/f'git-{a.checkpoint}-manifest.json';assert not manifest.exists()
paths=[]
for f in sorted(S.rglob('*')):
    if not f.is_file() or 'local-cache' in f.parts or '__pycache__' in f.parts:continue
    if f.name.startswith('git-') and f.name.endswith('-manifest.json'):continue
    if f.suffix in ['.md','.json','.py','.csv','.png','.svg']:paths.append(f)
paths+=sorted((R/'papers/damping-output-boundaries/manuscript').glob('p06-actual-main-session026-v*.md'))
if a.checkpoint=='FINAL':
    qa=json.loads((S/'final-visual-review.json').read_text(encoding='utf-8'));assert qa['passed']
    paths.append(R/qa['docx'])
assert len(paths)==len(set(paths))
cfg={'checkpoint':a.checkpoint,'frozen_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'message':'P06 actual-scheme main analysis '+a.checkpoint,'files':[{'relative':f.relative_to(R).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in paths]}
manifest.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'checkpoint':a.checkpoint,'files':len(paths),'bytes':sum(f.stat().st_size for f in paths)},ensure_ascii=False))
