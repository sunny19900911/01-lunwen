from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
p=Path(__file__).resolve().parent;repo=p.parents[4];paper=repo/'papers/damping-output-boundaries/manuscript/modal-shear-session009-v002.md'
def ident(f):
 b=f.read_bytes();return {'path':str(f),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
report=(p/'R002-report.md').read_text(encoding='utf-8');table=[x for x in report.splitlines() if x.startswith('|')];row_count=len(table)-2
manifest={'task':'role3 R002','purpose':'eight-row citation table, v002 section3 elastic output citation and one publishable theory paragraph','inputs':[ident(paper),ident(p/'R001-report.md'),ident(p/'R001-manifest.json'),ident(p/'R001-freeze.json')],'source_scope':'reuse exactly the three primary works and original page locators of frozen R001; no new source retrieval','table_rows':row_count,'v002_formula_reference':{'mother_equation':'Song2008 PDF56 printed38 Eq3.58 F_IS=T_S Kx','mapping':'ell_s^T=e_s^T T_S K; substitute u=Phi q under the manuscript complete mass-normalized real reference basis','direct_inference_not_verbatim_source_formula':True,'not_claimed':'nonlinear mode-by-mode independence or exact engineering Bottom identity'},'references':[{'number':1,'authors':['Song J','Chu Y L','Liang Z','Lee G C'],'year':2008,'report':'MCEER-08-0005','pages':[56,58],'equations':['3.57–3.59','3.63']},{'number':2,'authors':['Londono J M','Wagg D J','Neild S A'],'year':2014,'doi':'10.1002/eqe.2433','pages':[4,5],'equations':['1b','2','5'],'figure':2},{'number':3,'authors':['Conde J','Bernabeu A'],'year':2021,'doi':'10.3390/app11073089','page':4,'equations':['4–6','9']}],'new_searches':0,'new_downloads':0,'new_scientific_computation':0,'manuscript_changed':False}
(p/'R002-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone(timedelta(hours=8)));v={'task':'role3 R002','status':'completed_citation_table_and_theory_paragraph','started_at':'2026-10-20T19:38:50+08:00','finished_at':now.isoformat(),'task_deadline':'2026-10-20T19:46:50+08:00','within_task_deadline':now<datetime.fromisoformat('2026-10-20T19:46:50+08:00'),'table_rows':row_count,'row_count_pass':6<=row_count<=8,'complete_references':3,'theory_paragraphs':1,'new_searches':0,'new_downloads':0,'ODE_or_ETABS':0,'workbook_reads':0,'manuscript_or_shared_writes':False,'git_or_automation':False,'new_agents_or_chats':False}
(p/'R002-validation.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[]
for n in ['R002-report.md','R002-manifest.json','R002-validation.json','R002-close.py']:
 f=p/n;files.append({'file':n,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
z={'task':'role3 R002','frozen_at':now.isoformat(),'immutable':True,'files':files}
(p/'R002-freeze.json').write_text(json.dumps(z,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False))
for n in ['R002-report.md','R002-freeze.json']:
 f=p/n;print(n,f.stat().st_size,hashlib.sha256(f.read_bytes()).hexdigest())
