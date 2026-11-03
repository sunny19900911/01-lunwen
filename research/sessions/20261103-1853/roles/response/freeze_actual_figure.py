from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[4];O=H/'R003';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for m in [H/'numeric-delivery-manifest.json',H/'R002/numeric-delivery-manifest.json']:
 obj=json.loads(m.read_text(encoding='utf-8'))
 for q in obj['files']:assert sha(R/q['relative'])==q['sha256']
names=['actual-B-D-QD-two-records.png','actual-B-D-QD-two-records.svg','plot-record.json','actual-mechanism-writing-note.md']
paths=[O/n for n in names]+[H/'plot_actual_B_D_QD.py',Path(__file__)]
manifest={'status':'frozen-figure','at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'actual_PNG_original_detail_viewed':True,'all_source_numeric_manifests_unchanged':True,'all_saved_points_preserved':True,'displayed_examples':['Story8 RH4X','Story10 RH4Y'],'new_ODE_or_fit':False,
 'files':[{'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in paths]}
p=O/'delivery-manifest.json';assert not p.exists();p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'at':manifest['at'],'frozen_files':len(paths),'png_sha256':manifest['files'][0]['sha256']},ensure_ascii=False))
