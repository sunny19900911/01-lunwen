from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,re
H=Path(__file__).resolve().parent
def rec(p):
    data=p.read_bytes();return {'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
def write(n,x):(H/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=json.loads((H/'input-rules-R028.json').read_text(encoding='utf-8'));now=datetime.now(timezone(timedelta(hours=8)))
start=datetime.fromisoformat(r['started_at']);deadline=datetime.fromisoformat(r['deadline']);assert now<deadline
end=[]
for old in r['inputs']:
    e=rec(Path(old['path']));e['unchanged']=e['sha256']==old['sha256'] and e['bytes']==old['bytes'];end.append(e)
assert all(x['unchanged'] for x in end)
cache=H/'local-cache';src=rec(cache/'MIT18_156_lecture25.pdf')
assert src['sha256']=='996490a8065004dbec4776388fb70730be2597588b4fb5b5e873e0d7e808ae43'
write('search-log-R028.json',{'query_attempts':[{'query':'Young convolution inequality Holder Lp L infinity lecture notes author conjugate exponents','result':'functions/web tool connection failed: error sending request after28.1s; no results returned','retried':False}],'new_query_attempts':1,'query_limit':1,'readable_primary_fulltexts':1,'new_network_downloads':0,'source_route':'reused existing local primary MIT lecture25 PDF from literature/local-cache, known source URL inherited','old_failed_downloads_not_retried':True,'no_second_fulltext':True})
write('source-manifest-R028.json',{'recorded_at':now.isoformat(),'source':{'title':'18.156 Lecture Notes, lecture25','date':'April10,2015','header_attribution':'trans. Jane Wang','course_host':'Larry Guth MIT course; do not infer sole note author','url':'https://math.mit.edu/~lguth/Math156/notes/25.pdf','course_url':'https://math.mit.edu/~lguth/Math156.html','pages':4,'read_scope':'four pages text; actually viewed PDF2/3; only section1.2 Theorem3 and r-infinity proof used','location':'PDF/printed2 Theorem3, PDF/printed3 first proof paragraph','exponents':'1+1/r=1/p+1/q; r=infinity uses conjugate p,q>1 directly by Holder','scope':'function convolution; not a Maxwell theorem or measure-atom theorem'},'files':[rec(cache/n) for n in ['MIT18_156_lecture25.pdf','MIT18_156_lecture25.txt','MIT25-2.png','MIT25-3.png']],'originals_text_images_cache_only':True})
text=(H/'report.md').read_text(encoding='utf-8');shapes=[]
for block in re.findall(r'(?m)(?:^\|.*\|\n)+',text):
    widths=[len(x.split('|'))-2 for x in block.strip().splitlines()];assert len(set(widths))==1;shapes.append({'columns':widths[0],'rows':len(widths)})
links=['input-rules-R028.json','search-log-R028.json','source-manifest-R028.json','report.md','freeze_R028.py','validation-R028.json','freeze-R028.json']
write('validation-R028.json',{'task':'R028','decision':'classical convolution Holder/Young r-infinity source confirmed; candidate math remains pending','validated_at':now.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'within_six_minutes':True,'old_inputs_unchanged':end,'source_PDF_SHA_matches_old_index':True,'new_query_attempts':1,'successful_search_results':0,'readable_primary_fulltexts':1,'source_visual_pages':[2,3],'table_shapes':shapes,'assumptions_recorded':['conjugate p,q>1','function kernel inLq and input inLp','finiteH causal truncation and zero extension only for estimate','essential sup versus continuous representative','complete devices and spatial output/port projections','actual same reference operator and initial state,homogeneous difference if needed','infiniteH kernelLq plus actualD finite;PSD C not automatically stable','no unsupported acceleration,total-shear or missing-channel extension'],'not_read_in_progress_role1_R030':True,'not_derived_Maxwell_coefficients_units_totalD_or_extremals':True,'no_arrays_rawExcel_solver_or_shared_Git_changes':True,'helper_review':'local_literature old protocol/interface/index only;no primary PDF/query','explicit_artifact_links':links,'limits':'source-index and application assumptions only,not candidate proof or engineering admission'})
frozen=datetime.now(timezone(timedelta(hours=8)));f={'task':'R028','frozen_at':frozen.isoformat(),'started_at':start.isoformat(),'deadline':deadline.isoformat(),'elapsed_seconds':(frozen-start).total_seconds(),'within_deadline':frozen<=deadline,'decision':'classical tool source located, no candidate correctness/novelty certification','files':[rec(H/n) for n in links if n!='freeze-R028.json'],'cache_manifest':'source-manifest-R028.json','immutable_after_delivery':True};assert f['within_deadline']
write('freeze-R028.json',f);assert all((H/n).is_file() for n in links)
print(json.dumps({'freeze':f,'freeze_SHA':rec(H/'freeze-R028.json')['sha256'],'links_exist':True},ensure_ascii=False,indent=2))
