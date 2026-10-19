"""Administrative closeout only; no science, array load, workbook or plotting."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=O/n;assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save('R003-run-record.json',{'status':'incomplete_stopped_after_deadline','start_observed_utc':'2026-10-19T13:33:53+00:00','task_12min_deadline_utc':'2026-10-19T13:45:53+00:00','session_hard_deadline_utc':'2026-10-19T14:45:41+00:00','first_failed_execution_observed_utc':'2026-10-19T14:56:44+00:00','second_clock_and_host_confirmation_utc':'2026-10-19T14:57:08+00:00','attempted_command':'python -X utf8 roles/role4/R003-analysis.py','exit_code':1,'error':'ModuleNotFoundError: No module named matplotlib, line 6; stopped before input freeze/NPZ processing/output generation','new_profile_CSVs_created':0,'new_figures_created':0,'new_peak_analysis_completed':False,'source_workbooks_read':0,'new_solver_or_ODE_runs':0,'arrays_read_for_R003_peak_analysis':0,'candidate_native_motion_rankings':0,'post_deadline_actions':'clock verification; read existing role1 question and 3 frozen geometry rows to resolve conflicting axis labels; administrative incomplete handoff only','axis_conflict':'Actual frozen geometry K82/K83 is Y (nx=0,ny~0.87295); master in-flight X label conflicts. K10 is X. No source modified.'})
files=[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.glob('R003*')) if p.is_file()]
save('R003-delivery-manifest.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'task':'R003','status':'incomplete; administrative closeout after hard deadline','within_12min':False,'within_research_deadline':False,'new_science_after_deadline':False,'files':files})
print(json.dumps({'status':'incomplete frozen','frozen_utc':datetime.now(timezone.utc).isoformat(),'files':len(files)},ensure_ascii=False))
