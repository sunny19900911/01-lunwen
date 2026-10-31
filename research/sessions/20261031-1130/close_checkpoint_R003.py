from pathlib import Path
from datetime import datetime,timezone,timedelta
import json
S=Path(__file__).resolve().parent
marker=S/'R003-closed-receipt.json';assert not marker.exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
pub=json.loads((S/'git-R003-receipt.json').read_text());assert pub['remote_equals_local']
d=json.loads((S/'status.json').read_text());d.update(phase='direct-physical-forward-running',checkpoint='R003-complete',checkpoint_open=False,last_actual=now,recovery_file='rounds/R003.md')
d['git'].update(current_HEAD_and_remote=pub['HEAD'],last_success_HEAD=pub['HEAD'],last_success_receipt='git-R003-receipt.json',publication='R003 normal push succeeded;remoteSHAequal; postpublication status administrative until next checkpoint')
d['current_tasks']['role5']='v002 frozen, root fullread; lastactual idle cursor28; wait newR004 evidence before newv003, preserveoldv002'
d['current_tasks']['role4']='R004 actualactive cursor26 observed12:13, newactual300 no-fit forward CM-first,12min first15min maximum from12:11; notrerunR003 oroldfits'
d['next_checkpoint']='Read role4R004 actual status and freeze: first CM nofit prediction vs old5/8 then both shear operator results. First collect all errors, do not tune signs/gains/time. Role2R004 independently audits B/observability active. Once frozen nofit output, review sources/root and route independentcheck and authorv003. NextGitR004 approximately12:27 based actual work, frozenonly; do not rerun gitR003 receipt. Clockdeadline15:30:11 fixed.'
(S/'status.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
t=json.loads((S/'threads.json').read_text())
for q in t['threads']:
 if q['role']=='role4':q.update(cursor='18d108d1-c129-40a5-b347-658f1f0c4b89:26',actual_status={'type':'active','activeFlags':[]})
 if q['role']=='role5':q.update(cursor='824ab043-4970-4d4a-8fa8-7ed81ac611bc:28',actual_status={'type':'idle'})
 q['task']=d['current_tasks'][q['role']]
(S/'threads.json').write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
marker.write_text(json.dumps({'actual_close_time':now,'checkpoint':'R003','no_new_scientific_results_after_last_Git':True,'remote_HEAD':pub['HEAD'],'next_role4_run':'R004 active; nofit physical forward, not native FNA q recovery','fixed_deadline':d['deadline']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'actual':now,'checkpoint_open':False,'HEAD':pub['HEAD']},ensure_ascii=False))
