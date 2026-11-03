from pathlib import Path
import json,hashlib,datetime,ast
P=Path(__file__).resolve().parent
start=datetime.datetime.fromisoformat('2026-11-03T08:50:22+08:00')
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
record=json.loads((P/'source-read-record.json').read_text(encoding='utf-8'))
for s in record['sources']:
 assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
for p in [P/'review_local_sources.py',Path(__file__)]:ast.parse(p.read_text(encoding='utf-8'))
names=['R001-source-review.md','source-read-record.json','review_local_sources.py','freeze_R001.py']
manifest=[{'path':str((P/n).relative_to(P)),'bytes':(P/n).stat().st_size,'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest()} for n in names]
out={'task':'session023/literature/R001','status':'frozen-completed','started_at':start.isoformat(),'frozen_at':now.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'within_12_minute_budget':(now-start).total_seconds()<=720,'source_pdfs_read_only':True,'source_hashes_unchanged':True,'pages_actually_viewed':{'Liu2004':{'pdf':[15,16,17,18,19],'print':[81,82,83,84,85]},'Song2008':{'pdf':[123,124,125,126,127],'print':[105,106,107,108,109]}},'visual_method':'PDFium1.5scale; each original-detail PNG viewed in tool results; no montage substitution','existing_theory_reused':True,'new_web_searches':0,'new_downloads':0,'no_new_numeric_or_solver':True,'shareable_outputs':manifest,'local_only':['selected source PDF page PNGs','selected source page text'],'conclusion':'Existing primary pages support target-response-specific modal interpretation, not high-mode attribution for SHW4X Story5. Two restrained Chinese paraphrase sentences supplied.','historical_correction':'Liu print85 Table7 final row actually reads Cfg V; prior followup claim of duplicate Cfg IV not adopted.'}
dest=P/'freeze.json';assert not dest.exists()
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frozen_at':out['frozen_at'],'elapsed_seconds':out['elapsed_seconds'],'page_images_actually_viewed':10,'shareable_outputs':len(manifest)},ensure_ascii=False))
