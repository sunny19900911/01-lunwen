from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
sources=read(HERE/'source-freeze.json')
assert len(sources)==14 and all(record(Path(x['path']))==x for x in sources)
r35=ROLE/'R035-compact-math-review/validation.json'
assert record(r35)['sha256']=='846af33000b29e1449e0863107b99b7b37b0c0c05d62a2d5ea18cbc5a43587fe'
old=read(r35)['frozen_R001_R034']+[{'run_file':'R035-compact-math-review/validation.json','sha256':record(r35)['sha256'],'outputs_verified':5}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outs)==item['outputs_verified']
    for x in outs:assert record(Path(x['path']))==x
    total+=len(outs)
assert len(old)==35 and total==117
c=read(HERE/'checks.json');assert c['required_changes']==0
assert c['reported_fine_u1_failure_preserved'] and c['reported_gate_not_independently_recomputed']
assert not c['NPZ_arrays_ODE_source_execution_PDF_or_full_statistics_audit']
for p in HERE.iterdir():
    if p.is_file():
        b=p.read_bytes();s=b.decode('utf-8')
        assert not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b and '\ufffd' not in s,p
        assert all(line==line.rstrip() for line in s.splitlines()),p
now=datetime.now(timezone(timedelta(hours=8)))
assert now.isoformat()<'2026-10-18T03:43:33+08:00'
out={'review':'R036','session':'20261017-2109','started_at':'2026-10-18T03:35:33+08:00','frozen_at':now.isoformat(),'deadline':'2026-10-18T03:43:33+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00',
 'required_changes':0,'accepted_scope':'Exact finite-dimensional BE step under symmetric SPD M/K, symmetric PSD C, arbitrary conjugate B and positive independent kappa/c/alpha; elimination, coercive C1 strongly convex existence/uniqueness and complete residual energy identity only.',
 'independent_tiny_exact_algebra_challenges_passed':True,'source_records_verified':14,'sources_unchanged':True,'frozen_prior_records_verified':35,'frozen_prior_small_outputs_verified':117,'frozen_R001_R035':old,'array_or_PDF_references_not_followed':True,
 'cross_reviews':[{'agent':'kernel_sharp_audit','scope':'General elimination/strongly convex existence, scalar-only bracket and alpha>1 scope','required_changes':0},{'agent':'audit_double_mode','scope':'Three numerical dissipations, nonzero E0 and complete residual work signs','required_changes':0},{'agent':'r006_sharp_challenge','scope':'Source/classical attribution, small checks and failed experimental gate preserved','required_changes':0}],
 'remaining_unverified':['Experiment R022 implementation/feed order/roots/full trajectories not audited','Fine u1 .1 diagnostic remains failed, not changed or independently recomputed','No floating algorithm success or continuous convergence/order/precision established','No engineering solver, model or physical prediction validation'],
 'outputs':[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json'],
 'UTF8_LF_no_BOM_replacement_or_trailing_whitespace':True,'ODE_time_solver_arrays_NPZ_PDF_source_execution_or_external_search':False,'only_own_R036_written':True,'shared_manuscript_or_Git_changes':False,'following_task_not_started':True,'stopped_after_handoff':True}
(HERE/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'required_changes':0,'sources':14,'prior_records':35,'prior_outputs':117,'principal_files':[record(HERE/n) for n in ['report.md','checks.json','validation.json']]},ensure_ascii=True,indent=2))
