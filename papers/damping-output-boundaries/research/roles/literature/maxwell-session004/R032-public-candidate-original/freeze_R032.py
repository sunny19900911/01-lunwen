from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
base=Path(__file__).resolve().parent
def ident(p):
    b=p.read_bytes()
    return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def put(n,obj):
    (base/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
start=datetime.fromisoformat('2026-10-18T06:00:15+08:00')
deadline=datetime.fromisoformat('2026-10-18T06:06:15+08:00')
now=datetime.now(timezone(timedelta(hours=8)))
assert now<deadline
put('retrieval.json',{'url':'https://vbn.aau.dk/files/539141579/1-s2.0-S0360544222023301-main.pdf','tool':'web.run','operation':'open','attempt_count':1,'tool_result':'Internal Error; Failed to fetch; (403) Forbidden','http_status_as_reported_by_tool':403,'direct_HTTP_recheck':False,'readable_body_obtained':False,'body_sha256':None,'body_bytes':None,'metadata_verified':False,'metadata_query_count':0,'new_primary_bodies_read':0,'download_count':0,'retry_or_alternate_entry':False,'failure_origin_inferred':False})
put('validation.json',{'task':'R032-public-candidate-original','result':'one retrieval failed; candidate scientific relevance and exact publication coverage remain unclassified/unknown','source_page_or_equation_locations_available':False,'title_authors_version_verified':False,'exact_target_conditions_checked_in_body':False,'new_proof_solver_array_shared_or_Git_operation':False,'original_cache_or_upload':False,'started_at':start.isoformat(),'frozen_at':now.isoformat(),'deadline':deadline.isoformat(),'within_deadline':True,'elapsed_seconds':(now-start).total_seconds(),'stop_on_single_failure':True})
names=['report.md','retrieval.json','validation.json','freeze_R032.py']
put('freeze.json',{'task':'R032-public-candidate-original','status':'frozen; retrieval failure; unknown coverage; stop','started_at':start.isoformat(),'frozen_at':now.isoformat(),'deadline':deadline.isoformat(),'global_deadline':'2026-10-18T07:09:45+08:00','artifacts':[ident(base/n) for n in names]})
print(json.dumps({'frozen_at':now.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'artifacts':[ident(base/n) for n in names+['freeze.json']]},ensure_ascii=False,indent=2))
