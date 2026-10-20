from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
p=Path(__file__).resolve().parent;repo=p.parents[4]
def ident(f):
 b=f.read_bytes();return {'path':str(f),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
old=repo/'papers/damping-output-boundaries/research/roles/literature/engineering-session006'
inputs=[ident(old/'H003/source-scope.json'),ident(p/'R001-report.md')]
for n in [391,392,393,394,399,400,401,402,403]:inputs.append(ident(p/f'R003-local-cache/CSI-p{n}.txt'))
now=datetime.now(timezone(timedelta(hours=8)))
m={'task':'role3 R003','inputs':inputs,'source_works':2,'new_searches':0,'new_downloads':0,'CSI_machine_located_pages':[388,403],'CSI_actual_text_read':[391,392,393,394,399,400,401,402,403],'CSI_new_images_viewed':0,'unviewed_generated_images':['R003-local-cache/CSI-p393.png','R003-local-cache/CSI-p403.png'],'Song_scope_reused_from_R001':{'pages':[56,58],'equations':['3.58','3.59','3.63']},'original_quote_words':24,'comparison':'mass participation, static participation, dynamic participation and output-specific peak convergence distinguished','numerical_table_recalculated':False,'code_mass_90percent_clause_verified':False}
(p/'R003-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v={'status':'closed_on_controller_stop_after_budget_exhausted','first_observed_clock':'2026-10-20T19:58:57+08:00','last_observed_clock':'2026-10-20T20:05:13+08:00','controller_estimated_turn_start':'2026-10-20 approximately19:53+08:00','finished_at':now.isoformat(),'within_10minute_task_budget_claim':False,'science_stopped_on_controller_instruction':True,'new_searches':0,'new_downloads':0,'new_ODE_or_ETABS':0,'source_table_or_workbook_reads':0,'manuscript_or_shared_writes':False,'git_or_automation':False,'new_agents_or_chats':False,'first_claim':False}
(p/'R003-validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[]
for n in ['R003-report.md','R003-manifest.json','R003-validation.json','R003-locate.py','R003-close.py']:
 f=p/n;files.append({'file':n,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
z={'task':'role3 R003','frozen_at':now.isoformat(),'immutable':True,'files':files}
(p/'R003-freeze.json').write_text(json.dumps(z,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for n in ['R003-report.md','R003-freeze.json']:
 f=p/n;print(n,f.stat().st_size,hashlib.sha256(f.read_bytes()).hexdigest())
print(json.dumps(v,ensure_ascii=False))
