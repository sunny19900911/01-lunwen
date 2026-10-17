from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib,json,re
base=Path(__file__).resolve().parent
parent=base.parent
def ident(p):
    b=p.read_bytes()
    return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def put(name,obj):
    (base/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
names=['local-cache/R004-CSI2016-PDFpage-475.png','local-cache/R004-CSI2016-PDFpage-476.png','R017-FNA-reference-force-scope/local-cache/CSI2016-PDFpage-475.txt','R017-FNA-reference-force-scope/local-cache/CSI2016-PDFpage-476.txt','R017-FNA-reference-force-scope/R017-FNA-reference-force-scope.md','R017-FNA-reference-force-scope/source-locations-R017.json']
records=[ident(parent/n) for n in names]
expected=['dd3630ca2373b3d1086c1d9658b19c134e3342593fce1aa642fc717b3d267603','00a353b076fb8ac14694f0da6b1cc9aa97bea84da847006109b9844fee6dd37b','679f423f92fba28d68a9edd5e80a3f84ea23b2a14d540b96dd1cbbd69fd5db0d','f4aa25ad7ffb7fb82240b42d1063bb9cedb6ebb488841a7a44368cfe1148864f']
assert [r['sha256'] for r in records[:4]]==expected
put('source-manifest.json',{'edition':'CSI Analysis Reference Manual July2016 Rev15','full_manual_identity_inherited_only':{'bytes':7811196,'sha256':'7f6f6890afee2e1890d33f5d34d53d8e23f60850890bd230848642b50a6291ac','opened_or_hashed_this_task':False},'actual_two_original_page_images_viewed':True,'physical_pdf_pages_1based':[475,476],'printed_pages':[453,454],'sources_actually_read_and_small_files_hashed':records,'network_requests':0,'manual_downloads':0,'large_arrays_read':0})
report=(base/'report.md').read_text(encoding='utf-8')
links=re.findall(r'\]\(([^)]+)\)',report)
local_links=[x for x in links if not x.startswith('https://')]
assert all((base/x).resolve().exists() for x in local_links)
assert all(('| '+k+' |') in report for k in ['S1','S2','S3','S4','B1','B2','B3','B4'])
now=datetime.now(timezone(timedelta(hours=8)))
start=datetime.fromisoformat('2026-10-18T05:22:11+08:00')
deadline=datetime.fromisoformat('2026-10-18T05:28:11+08:00')
assert now < deadline
put('validation.json',{'status':'complete within bounded source review','must_fix_existing_files':0,'source_identity_checks_passed':4,'small_sources_read_and_hashed':6,'actual_page_images_viewed':2,'local_links_checked':len(local_links),'external_url_opened':False,'source_inference_distinguished':True,'no_new_proof_or_project_failure_claim':True,'new_download_or_full_manual_hash':False,'large_arrays_or_solver':False,'frozen_at':now.isoformat(),'started_at':start.isoformat(),'deadline':deadline.isoformat(),'within_deadline':True,'elapsed_seconds':(now-start).total_seconds()})
deliveries=['report.md','source-manifest.json','validation.json','freeze_R030.py']
put('freeze.json',{'task':'R030-FNA-nonlinear-mode-coverage-source','status':'frozen; stop; main integrates independently','frozen_at':now.isoformat(),'started_at':start.isoformat(),'deadline':deadline.isoformat(),'global_deadline':'2026-10-18T07:09:45+08:00','artifacts':[ident(base/n) for n in deliveries]})
print(json.dumps({'frozen_at':now.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'artifacts':[ident(base/n) for n in deliveries+['freeze.json']]},ensure_ascii=False,indent=2))
