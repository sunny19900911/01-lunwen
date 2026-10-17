from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re
base=Path(__file__).resolve().parent
roles=base.parents[2]
project=roles.parents[3]
session=project/'research/sessions/20261017-2109'
old=roles/'novelty/maxwell-session004/R027-RL-equivalent-prior-art'
def identity(p):
    b=p.read_bytes()
    return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def put(name,obj):
    (base/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
paths=[old/'report.md',old/'search-log.json',old/'mapping-addendum-input.json',session/'RL-equivalent-prior-art-protocol-v001.md',session/'RL-equivalent-prior-art-mapping-addendum-v001.md']
records=[identity(p) for p in paths]
assert records[-2]['sha256']=='9220db36a480305e2349f24ed901794ae3310148a2fd988a359bdf7cf7e4b606'
assert records[-1]['sha256']=='09c364fa7cecee649d7c9b1e140a35db06757d1ab34079c656f7a44977f540c9'
put('source-manifest.json',{'read_inputs':records,'new_primary_bodies_opened_or_retrieved':0,'new_fulltext_cache_files':0,'Goetz_body_reopened_or_hashed':False,'old_blocked_sources_retried':False,'source_scope':'Existing R027 report and mapping only; new search hits are metadata/snippets, not classified scientific bodies.','strict_publication_coverage':'unknown'})
queries=['"RL circuit" "optimal control" "voltage" "energy loss"','"inductor" "optimal charging" "voltage" "loss"']
put('search-log.json',{'new_queries':queries,'new_query_count':2,'query_tool':'web.run search_query','result_body_links_opened':0,'new_readable_primary_fulltexts':0,'new_downloads':0,'new_access_failure':False,'selection_failure':'No sufficiently relevant exact candidate identified from two query result sets; no candidate body was opened. This is not proof of unavailability or nonexistence.','query1_result_types':['supercapacitor ResearchGate metadata','converter and battery equalization','textbooks and aggregators'],'query2_result_types':['battery charging','converter efficiency and modulation','loss models'],'third_query_or_reference_chain':False,'captcha_login_paywall_mirror_bypass':False})
report=(base/'report.md').read_text(encoding='utf-8')
links=re.findall(r'\]\(([^)]+)\)',report)
loc=[x for x in links if not x.startswith('https://')]
assert all((base/p).resolve().exists() for p in loc)
now=datetime.now(timezone(timedelta(hours=8)))
start=datetime.fromisoformat('2026-10-18T05:40:38+08:00')
deadline=datetime.fromisoformat('2026-10-18T05:48:38+08:00')
assert now<deadline
put('validation.json',{'status':'bounded search complete; precise publication coverage remains unknown','new_queries':2,'new_primary_bodies':0,'old_small_input_hashes_checked':5,'old_protocol_and_mapping_SHA_matched':True,'local_links_checked':len(loc),'no_new_proof_solver_or_arrays':True,'no_shared_or_old_frozen_file_edits':True,'mapping_correction_retained':True,'no_first_publication_claim':True,'started_at':start.isoformat(),'frozen_at':now.isoformat(),'deadline':deadline.isoformat(),'within_deadline':True,'elapsed_seconds':(now-start).total_seconds()})
names=['report.md','source-manifest.json','search-log.json','validation.json','freeze_R031.py']
put('freeze.json',{'task':'R031-total-voltage-RL-prior-art','status':'frozen; unknown result; stop','started_at':start.isoformat(),'frozen_at':now.isoformat(),'deadline':deadline.isoformat(),'global_deadline':'2026-10-18T07:09:45+08:00','artifacts':[identity(base/n) for n in names]})
print(json.dumps({'frozen_at':now.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'artifacts':[identity(base/n) for n in names+['freeze.json']]},ensure_ascii=False,indent=2))
