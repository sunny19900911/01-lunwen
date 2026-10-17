"""Small-file integrity only; no array/PDF/reference-chain execution."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
sources=read(HERE/'source-freeze.json')
assert len(sources)==12 and all(record(Path(x['path']))==x for x in sources)
r32=ROLE/'R032-target-peak-decision-review/validation.json'
assert record(r32)['sha256']=='c912491ec0635bde23eee2120a771d218c83b4f4b5de40cc3078d7251a6e5b74'
old=read(r32)['frozen_R001_R031']+[{'run_file':'R032-target-peak-decision-review/validation.json','sha256':record(r32)['sha256'],'outputs_verified':5}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outs)==item['outputs_verified']
    for x in outs:assert record(Path(x['path']))==x
    total+=len(outs)
assert len(old)==32 and total==102
c=read(HERE/'checks.json');assert c['required_changes']==0
assert not c['author_script_ODE_arrays_PDF_or_NPZ_access'] and not c['new_solver_implemented']
for p in HERE.iterdir():
    if p.is_file():
        b=p.read_bytes();s=b.decode('utf-8')
        assert not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b and '\ufffd' not in s,p
        assert all(line==line.rstrip() for line in s.splitlines()),p
now=datetime.now(timezone(timedelta(hours=8)))
assert now.isoformat()<'2026-10-18T03:18:00+08:00'
out={'review':'R033','session':'20261017-2109','started_at':'2026-10-18T03:10:00+08:00','frozen_at':now.isoformat(),'deadline':'2026-10-18T03:18:00+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00',
 'required_changes':0,'accepted_scope':'Classical full-port force-feedback Volterra equivalence under fixed bare operator, full kernels/constitutive law and compatible AC initial-data domain only; no existence/uniqueness, algorithm or engineering certification.',
 'independent_tiny_exact_Schur_affine_challenges_passed':True,'source_records_verified':12,'source_records_unchanged':True,
 'frozen_prior_records_verified':32,'frozen_prior_small_outputs_verified':102,'frozen_R001_R032':old,'old_manifest_array_references_not_followed':True,
 'cross_reviews':[{'agent':'kernel_sharp_audit','scope':'Closure signs, full matrix/modal mass, initial-affine signs and sufficient AC equivalence domain','required_changes':0},{'agent':'audit_double_mode','scope':'FNA/Volterra and nonclassical/multicomponent/support/Ritz limitations','required_changes':0},{'agent':'r006_sharp_challenge','scope':'Small source identity, alpha1 Schur and initial signs, non-overclaim boundaries','required_changes':0}],
 'remaining_unverified':['No time-domain or nonlinear force solved','No general existence/uniqueness or numerical convergence established','Actual full engineering B/kernel/FNA/constitutive data not certified','Unknown missing-port or approximate-kernel remainder R_H*F not set to zero','New layouts require new coupled F solution; old force not portable'],
 'outputs':[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json'],
 'UTF8_LF_no_BOM_replacement_or_trailing_whitespace':True,'ODE_arrays_NPZ_PDF_author_execution_external_search':False,'new_nonlinear_or_time_solver_implemented':False,'only_own_R033_written':True,'shared_manuscript_or_Git_changes':False,'following_task_not_started':True,'stopped_after_handoff':True}
(HERE/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'required_changes':0,'sources':12,'prior_records':32,'prior_small_outputs':102,'principal_files':[record(HERE/n) for n in ['report.md','checks.json','validation.json']]},ensure_ascii=True,indent=2))
