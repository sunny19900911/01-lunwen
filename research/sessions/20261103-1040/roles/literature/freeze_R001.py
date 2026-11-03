from pathlib import Path
import datetime,json,hashlib,ast
P=Path(__file__).resolve().parent
start=datetime.datetime.fromisoformat('2026-11-03T10:48:07+08:00');now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
record=json.loads((P/'source-read-record.json').read_text(encoding='utf-8'))
for s in record['sources']:assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
for p in [P/'read_local024.py',Path(__file__)]:ast.parse(p.read_text(encoding='utf-8'))
viewed={'Londono2014':list(range(4,9)),'Conde2021':list(range(3,9))}
for key,pages in viewed.items():
 for n in pages:assert (P/f'local-cache/{key}-pdf{n}.png').is_file()
names=['R001-brace-and-Maxwell-review.md','source-read-record.json','read_local024.py','freeze_R001.py']
out={'task':'session024/literature/R001','status':'frozen-completed','started_at':start.isoformat(),'frozen_at':now.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'within_12min':(now-start).total_seconds()<=720,'within_15min':(now-start).total_seconds()<=900,'PDF_pages_actually_viewed':viewed,'page_count':11,'additional_read_after_main_script':'Conde PDF5 was separately rendered/read with an inline bundled Python PDFium command to check the start of section2.2; included in actual viewed pages, not in initial10-page source-read-record.','source_hashes_unchanged':True,'web_requests':0,'new_downloads':0,'new_solver_or_experiments':0,'old_Liu_Song_record_reused':True,'source_PDFs_and_page_images_local_only':True,'shareable_outputs':[{'path':n,'bytes':(P/n).stat().st_size,'sha256':hashlib.sha256((P/n).read_bytes()).hexdigest()} for n in names],'supports':'Review target modal relative end motion, frequency band and whole-series compliance of brace, mounting and damper; no generic stiffness ratio, start threshold or low-mode-only rule.','whole_paper_review_claimed':False}
dest=P/'freeze.json';assert not dest.exists();dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'at':out['frozen_at'],'seconds':out['elapsed_seconds'],'actual_pages':11,'within_12min':out['within_12min']}))
