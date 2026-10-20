from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
p=Path(__file__).resolve().parent;c=json.loads((p/'R004-citation-checks.json').read_text(encoding='utf-8'))
def ident(f):
 b=f.read_bytes();return {'path':str(f),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
manifest={'task':'role3 R004','manuscript':c['input'],'reused_source_records':[ident(p/f'R00{i}-report.md') for i in [1,2,3]],'review_scope':['four verified bibliography entries','first citation sequence and range expansion','output formula support','linear versus nonlinear modal independence','mass/static/dynamic participation','no invented source equation numbers','no unsupported priority/scarcity statements'],'not_reviewed':['numerical tables and new solver output','actual engineering model identity'],'must':0,'should':0}
(p/'R004-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone(timedelta(hours=8)));v={'task':'role3 R004','must':0,'should':0,'started_at':'2026-10-20T20:48:35+08:00','finished_at':now.isoformat(),'deadline':'2026-10-20T20:54:35+08:00','within_task_deadline':now<datetime.fromisoformat('2026-10-20T20:54:35+08:00'),'full_v008_read':True,'references':4,'first_citation_order':c['first_citation_order'],'all_expected_bibliographic_fields':all(c['all_expected_fields_present'].values()),'all_citations_resolve':c['all_citations_resolve'],'all_refs_cited':c['all_references_cited'],'unsupported_priority_scarcity_terms':c['priority_or_scarcity_terms'],'new_searches':0,'new_downloads':0,'new_scientific_computation':0,'manuscript_or_shared_writes':False,'git_or_automation':False,'new_agents_or_chats':False}
(p/'R004-validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[]
for n in ['R004-check.py','R004-citation-checks.json','R004-report.md','R004-manifest.json','R004-validation.json','R004-close.py']:
 f=p/n;files.append({'file':n,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
z={'task':'role3 R004','frozen_at':now.isoformat(),'immutable':True,'files':files,'bound_manuscript':c['input']}
(p/'R004-freeze.json').write_text(json.dumps(z,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False))
for n in ['R004-report.md','R004-freeze.json']:
 f=p/n;print(n,f.stat().st_size,hashlib.sha256(f.read_bytes()).hexdigest())
