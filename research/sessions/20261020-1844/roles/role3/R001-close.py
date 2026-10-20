from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
p=Path(__file__).resolve().parent;repo=p.parents[4];old=repo/'papers/damping-output-boundaries/research/roles/literature/engineering-session006';session=p.parents[1]
def ident(f):
 b=f.read_bytes();return {'path':str(f),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
inputs=[ident(session/'plan.md'),ident(session/'threads.json')]
for rel in ['H001/source-scope.json','H001/local-cache/MCEER-p003.txt','H001/local-cache/MCEER-p056.txt','H001/local-cache/MCEER-p058.txt','H012/local-cache/Londono-p04.txt','H012/local-cache/Londono-p05.txt','H012/local-cache/Conde-p04.txt']:
 inputs.append(ident(old/rel))
manifest={'task':'20261020-1844 role3 R001','inputs':inputs,'sources':[{'id':'L1','authors':['Jianwei Song','Yi-Lun Chu','Zach Liang','George C. Lee'],'title':'Modal Analysis of Generally Damped Linear Structures Subjected to Seismic Excitations','year':2008,'report':'MCEER-08-0005','source_sha256_reused':'941a58f7a8e88975405ccfdfeea412a42d9f982ca7ff3c6a055a93c8c25fda48','text_read':[3,56,58],'image_viewed_current':[56],'printed_pages':[38,40],'equations':['3.58','3.59','3.63'],'scope':'generally damped linear systems; output-specific modal coefficients; not nonlinear modal independence'},{'id':'L2','authors':['Julian M. Londono','David J. Wagg','Simon A. Neild'],'year':2014,'doi':'10.1002/eqe.2433','source_sha256_reused':'cf7e469e0897cb095fa45274d5ff98c0269d68eb2084d128bc4c6775817a0a1d','text_read':[4,5],'printed_pages':[2001,2002],'equations':['1b','2','5','6'],'figure':'2','scope':'linear Maxwell support filter, magnitude and phase frequency dependence'},{'id':'L3','authors':['Jorge Conde','Alejandro Bernabeu'],'year':2021,'doi':'10.3390/app11073089','source_sha256_reused':'a7dd7754cb9840eefada8b698067a956a31cf392645979755cbfddadd78cadef','text_read':[4],'equations':['4–9'],'scope':'linear harmonic storage/loss and nonlinear equivalent coefficient; modal/higher-mode caution'}],'current_original_image':ident(p/'R001-local-cache/MCEER-p56.png'),'original_pdf_identity_note':'previously verified original hashes reused; no new PDF download or full scan','contribution_boundary':'facts only; role6 owns contribution classification','direction3_scarcity_status':'not established; no search-count or systematic-review evidence; phase mechanism explicitly precedented','new_queries':0,'new_downloads':0,'new_ODE_or_ETABS':0,'mass_participation_equals_shear_share_claim':False,'frequency_band_equals_exact_mode_claim':False,'modal_plus3_equals_physical_Maxwell_claim':False,'input_model_background_identity_assumed':False}
(p/'R001-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone(timedelta(hours=8)));v={'task':'role3 R001','status':'completed_bounded_primary_source_reuse','started_at':'2026-10-20T19:25:50+08:00','finished_at':now.isoformat(),'task_deadline':'2026-10-20T19:33:50+08:00','session_deadline':'2026-10-20T21:44:25+08:00','within_task_deadline':now<datetime.fromisoformat('2026-10-20T19:33:50+08:00'),'new_primary_works':0,'reused_primary_works':3,'new_original_page_images_viewed':1,'searches':0,'downloads':0,'raw_workbook_reads':0,'ODE_runs':0,'ETABS_or_API':0,'git_or_automation':False,'new_agents_or_chats':False,'manuscript_or_shared_writes':False,'first_or_scarcity_claim':False}
(p/'R001-validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[]
for name in ['R001-report.md','R001-manifest.json','R001-validation.json','R001-close.py']:
 f=p/name;files.append({'file':name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
z={'task':'role3 R001','frozen_at':now.isoformat(),'immutable':True,'files':files,'ignored_original_image':manifest['current_original_image']}
(p/'R001-freeze.json').write_text(json.dumps(z,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False))
for n in ['R001-report.md','R001-freeze.json']:
 f=p/n;print(n,f.stat().st_size,hashlib.sha256(f.read_bytes()).hexdigest())
