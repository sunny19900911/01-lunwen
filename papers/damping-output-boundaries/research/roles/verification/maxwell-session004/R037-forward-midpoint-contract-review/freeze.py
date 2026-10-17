from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
sources=read(HERE/'source-freeze.json')
assert len(sources)==11 and all(record(Path(x['path']))==x for x in sources)
r36=ROLE/'R036-forward-BE-contract-review/validation.json'
assert record(r36)['sha256']=='96bb8f34ea01f87f0a6d547852b45c1f0416e28a28082313f247f4908f5ec58c'
old=read(r36)['frozen_R001_R035']+[{'run_file':'R036-forward-BE-contract-review/validation.json','sha256':record(r36)['sha256'],'outputs_verified':5}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outs)==item['outputs_verified']
    for x in outs:assert record(Path(x['path']))==x
    total+=len(outs)
assert len(old)==36 and total==122
c=read(HERE/'checks.json');assert c['required_changes']==0
assert c['all_three_work_midpoint_corrections_nonzero'] and c['force_work_midpoint_different_and_nonlinear_g_evaluation_changed']
assert not c['NPZ_arrays_ODE_time_integration_author_execution_or_new_statistics_certified']
for p in HERE.iterdir():
    if p.is_file():
        b=p.read_bytes();s=b.decode('utf-8')
        assert not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b and '\ufffd' not in s,p
        assert all(line==line.rstrip() for line in s.splitlines()),p
now=datetime.now(timezone(timedelta(hours=8)))
assert now.isoformat()<'2026-10-18T03:54:44+08:00'
out={'review':'R037','session':'20261017-2109','started_at':'2026-10-18T03:46:44+08:00','frozen_at':now.isoformat(),'deadline':'2026-10-18T03:54:44+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00',
 'required_changes':0,'accepted_scope':'Exact full-cross implicit midpoint finite-step elimination/existence/energy/residual contract only under stated symmetric positivity and independent monotone law conditions; no experiment/statistics/continuous accuracy admission.',
 'independent_tiny_exact_algebra_challenges_passed':True,'source_records_verified':11,'sources_unchanged':True,'frozen_prior_records_verified':36,'frozen_prior_small_outputs_verified':122,'frozen_R001_R036':old,'array_or_PDF_references_not_followed':True,
 'cross_reviews':[{'agent':'kernel_sharp_audit','scope':'Halfstep full-cross elimination, convex unique Fmid and scalar bracket limits','required_changes':0},{'agent':'audit_double_mode','scope':'Stored-mid energy/residual and nonlinear force work-midpoint correction','required_changes':0},{'agent':'r006_sharp_challenge','scope':'Source identity and BE/new-midpoint/statistical scope boundaries','required_changes':0}],
 'remaining_unverified':['New midpoint experiment implementation and full statistics remain outside this audit/candidate','Old BE fine u1 .1 failure retained','No floating bracket/root success, temporal convergence/order/true precision proved','No unique error mechanism, FNA/engineering/physical validation or new theory'],
 'outputs':[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json'],
 'UTF8_LF_no_BOM_replacement_or_trailing_whitespace':True,'ODE_time_solver_arrays_NPZ_PDF_author_execution_external_search':False,'only_own_R037_written':True,'shared_manuscript_or_Git_changes':False,'following_task_not_started':True,'stopped_after_handoff':True}
(HERE/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'required_changes':0,'sources':11,'prior_records':36,'prior_outputs':122,'principal_files':[record(HERE/n) for n in ['report.md','checks.json','validation.json']]},ensure_ascii=True,indent=2))
