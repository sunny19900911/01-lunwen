from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
base=Path(__file__).resolve().parent
roles=base.parents[2]
project=roles.parents[3]
def identity(p):
    b=p.read_bytes()
    return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def put(n,o):
    (base/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
old=roles/'novelty/maxwell-session004/R027-RL-equivalent-prior-art'
protocol=project/'research/sessions/20261017-2109/Goetz2013-unread-pages-review-protocol-v001.md'
source=identity(old/'local-cache/Goetz2013.pdf')
assert source['sha256']=='6e7449324392802c8351138e3643fae8e966e89c34352a32cb2824d5b118e63f' and source['bytes']==977456
pages=[3,4,5,6,12]
caches=[]
for n in pages:
    text=base/f'local-cache/Goetz2013-p{n:02}.txt'
    png=base/f'local-cache/Goetz2013-{n:02}.png'
    assert text.stat().st_size>1000 and png.stat().st_size>10000
    caches.append({'page':n,'text':identity(text),'image':identity(png),'root_text_read':True,'root_image_viewed':True})
put('source-manifest.json',{'source':source,'prior_read_level':{'root_this_task_new_text_read':pages,'root_this_task_new_page_images_viewed':pages,'inherited_R027_text_pages':[1,2,7,8,9,10,11],'inherited_R027_image_pages':[2,10],'inherited_pages_not_reopened_this_task':True},'inputs':[identity(protocol),identity(old/'source-manifest.json')],'local_only_cache':caches,'new_network_requests':0,'new_sources_downloaded':0,'raw_cache_may_publish':False})
now=datetime.now(timezone(timedelta(hours=8)))
start=datetime.fromisoformat('2026-10-18T06:42:24+08:00')
deadline=datetime.fromisoformat('2026-10-18T06:48:24+08:00')
assert now<deadline
put('validation.json',{'status':'bounded original-page review complete; no change to unresolved exact coverage','source_SHA_and_bytes_match':True,'source_page_count_checked':12,'new_text_pages_read':pages,'new_images_viewed':pages,'new_cache_files_nonempty':10,'source_metadata_scope':'identity of formal cached PDF matched; title/authors/version inherited from R027, page1 not reopened','bibliographic_pointers_body_read':False,'no_new_proof_solver_scientific_arrays_or_original_tables':True,'no_new_search_or_download':True,'no_shared_old_frozen_or_Git_edits':True,'role6_followup_pass_not_claimed':True,'started_at':start.isoformat(),'frozen_at':now.isoformat(),'deadline':deadline.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'within_deadline':True})
names=['report.md','source-manifest.json','validation.json','prepare_R033.py','freeze_R033.py']
put('freeze.json',{'task':'R033-Goetz-unread-pages','status':'frozen; stop; main and role6 independently review','started_at':start.isoformat(),'frozen_at':now.isoformat(),'deadline':deadline.isoformat(),'global_deadline':'2026-10-18T07:09:45+08:00','artifacts':[identity(base/n) for n in names],'raw_cache_policy':'Only local-cache, never publish original PDF/text/images'})
print(json.dumps({'frozen_at':now.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'artifacts':[identity(base/n) for n in names+['freeze.json']]},ensure_ascii=False,indent=2))
