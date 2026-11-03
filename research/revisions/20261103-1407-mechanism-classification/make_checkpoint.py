from pathlib import Path
import argparse,hashlib,json,datetime
ap=argparse.ArgumentParser();ap.add_argument('checkpoint',choices=['R001','R002','FINAL']);a=ap.parse_args()
H=Path(__file__).resolve().parent;R=H.parents[2]
manifest=H/('git-'+a.checkpoint+'-manifest.json');assert not manifest.exists()
paths=[]
for p in sorted(H.rglob('*')):
    if not p.is_file() or 'local-cache' in p.parts or '__pycache__' in p.parts:continue
    if p.name.startswith('git-') and p.name.endswith('-manifest.json'):continue
    if a.checkpoint!='FINAL' and p.name in ['word-identity-v1.json','final-summary.md','final-visual-review.json']:continue
    if p.suffix in ['.md','.json','.csv','.py']:paths.append(p)
M=R/'papers/damping-output-boundaries/manuscript'
paths.extend([M/'p06-mechanism-classification-v001.md',M/'p06-mechanism-classification-v002.md'])
if a.checkpoint=='FINAL':
    assert (H/'final-visual-review.json').is_file()
    paths.append(M/'p06-mechanism-classification-论文审阅稿-v002.docx')
files=[{'relative':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths]
assert len(files)==len({x['relative'] for x in files})
cfg={'checkpoint':a.checkpoint,'frozen_at':datetime.datetime.now().astimezone().isoformat(),'message':{'R001':'Clarify modal mechanisms and engineering review steps','R002':'Clarify modal mechanisms with independently checked same-time evidence','FINAL':'Deliver verified mechanism classification manuscript and Word'}[a.checkpoint],'files':files}
manifest.write_text(json.dumps(cfg,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'manifest':str(manifest),'files':len(files),'bytes':sum(p.stat().st_size for p in paths),'word_included':a.checkpoint=='FINAL'},ensure_ascii=False))
