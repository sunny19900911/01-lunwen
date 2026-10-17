from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,re
H=Path(__file__).resolve().parent
def rec(p):
    d=p.read_bytes();return {'path':str(p),'bytes':len(d),'sha256':hashlib.sha256(d).hexdigest()}
def write(n,x):(H/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=json.loads((H/'input-rules-R027.json').read_text(encoding='utf-8'))
log=json.loads((H/'search-log-R027.json').read_text(encoding='utf-8'))
log['web_click_Gusev_PDF']='Internal Error with no PDF or HTTP status; subsequent landing retrieval to inspect advertised link had SSL handshake timeout; no body obtained; stopped without retry'
write('search-log-R027.json',log)
start=datetime.fromisoformat(r['started_at']);deadline=datetime.fromisoformat(r['deadline']);now=datetime.now(timezone(timedelta(hours=8)))
assert now<deadline and log['total_queries']==2 and log['fulltext_obtained_total']==2
end=[]
for old in r['inputs']:
    new=rec(Path(old['path']));new['unchanged']=new['bytes']==old['bytes'] and new['sha256']==old['sha256'];end.append(new)
assert all(x['unchanged'] for x in end)
names=['cots2021.html','liberzon_cvoc.pdf','liberzon_selected_pages.txt','liberzon-142.png','liberzon-143.png']
source={'recorded_at':now.isoformat(),'originals_cache_only':True,'files':[rec(H/'local-cache'/n) for n in names],'sources':[
 {'id':'Cots2021','url':'https://ct.gitlabpages.inria.fr/gallery/turnpike/1d/bsb_turnpike.html','version':'author date November2021','type':'author teaching/computational example, not verified peerreview theorem','read_scope':'sections I, II formulation, III original problem/multiple shooting; code not executed','previously_read_primary':True,'target_relation':'structural neighbor only, no drag/exact peak/full cost interval established'},
 {'id':'Liberzon2011','url':'https://liberzon.csl.illinois.edu/teaching/cvoc.pdf','version':'August9 2011 preliminary copy,200PDFpages,not publication page numbering','read_scope':'version note PDF1/2; selected text PDF95/96,120-122,129/130,142-144; actually viewed PDF142/143','previously_read_primary':True,'target_relation':'classical augmentation/existence and global HJB sufficiency; no complete M-C018 specialization performed'},
 {'id':'Gusev2017','doi':'10.15826/umj.2017.1.003','metadata_url':'https://umjuran.ru/index.php/umj/article/view/82','fulltext_obtained':False,'body_SHA':None,'read_scope':'publisher metadata only,not body-based coverage decision'}]}
write('source-manifest-R027.json',source)
text=(H/'report.md').read_text(encoding='utf-8');widths=[]
for block in re.findall(r'(?m)(?:^\|.*\|\n)+',text):
    widths.append([len(row.split('|'))-2 for row in block.strip().splitlines()])
assert len(widths)==2 and all(len(set(w))==1 for w in widths)
links=['input-rules-R027.json','search-log-R027.json','source-manifest-R027.json','report.md','freeze_R027.py','validation-R027.json','freeze-R027.json']
validation={'task':'R027','decision':'exact-condition publication/direct-complete-specialization unresolved; no first claim','validated_at':now.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'old_inputs_unchanged':end,'new_queries':2,'readable_fulltexts':2,'both_reused_primary_sources':True,'new_direct_samecondition_body_hits':0,'Gusev_body_unavailable':True,'new_proof_or_cost_calculation':False,'fixedD_inverse_adopted':False,'mapping_scope':'original and previously verified variable/control/cost/endpoint correspondences only,not optimality proof','peer_reviews':['local_literature old notes,failures and target quantifiers only;no new primary','weng2016_source old alpha1 mapping and same Liberzon selected excerpt;no proof/calculation/query'],'actually_viewed':['Liberzon PDF142','Liberzon PDF143'],'table_column_counts':widths,'table_absolute_values_abs_not_pipe':True,'no_arrays_excel_solver_shared_Git':True,'no_old_failed_entry_retries':True,'no_third_query_or_third_readable_fulltext':True,'explicit_artifact_links':links,'limits':'bounded positioning only; no whole-field priority certification, unread Gusev not excluded, no engineering conclusions'}
write('validation-R027.json',validation)
frozen=datetime.now(timezone(timedelta(hours=8)))
f={'task':'R027','frozen_at':frozen.isoformat(),'started_at':start.isoformat(),'deadline':deadline.isoformat(),'elapsed_seconds':(frozen-start).total_seconds(),'within_deadline':frozen<=deadline,'decision':'0 confirmed exact-condition matches in bounded review; unresolved,not novel-by-default','files':[rec(H/n) for n in links if n!='freeze-R027.json'],'cache_manifest':'source-manifest-R027.json','immutable_after_delivery':True}
assert f['within_deadline']
write('freeze-R027.json',f)
assert all((H/n).is_file() for n in links)
print(json.dumps({'freeze':f,'freeze_SHA':rec(H/'freeze-R027.json')['sha256'],'artifact_links_exist':True},ensure_ascii=False,indent=2))
