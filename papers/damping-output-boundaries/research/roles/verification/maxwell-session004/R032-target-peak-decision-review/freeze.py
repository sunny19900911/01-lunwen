"""Freeze R032 small-file review; never open/hash array or PDF files."""
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
r31=ROLE/'R031-force-replay-review/validation.json'
assert record(r31)['sha256']=='33d41c7219c5a6fb1adf329b849e98c69c3608126b2b32b5614a59acf110d864'
old=read(r31)['frozen_R001_R030']+[{'run_file':'R031-force-replay-review/validation.json','sha256':record(r31)['sha256'],'outputs_verified':5}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outs)==item['outputs_verified']
    for x in outs:assert record(Path(x['path']))==x
    total+=len(outs)
assert len(old)==31 and total==97
c=read(HERE/'checks.json');assert c['required_changes']==0
assert not c['author_script_ODE_arrays_or_NPZ_access'] and not c['unknown56_remainder_assumed_zero']
for p in HERE.iterdir():
    if p.is_file():
        b=p.read_bytes();s=b.decode('utf-8')
        assert not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b and '\ufffd' not in s,p
        assert all(line==line.rstrip() for line in s.splitlines()),p
now=datetime.now(timezone(timedelta(hours=8)))
assert now.isoformat()<'2026-10-18T03:09:12+08:00'
out={'review':'R032','session':'20261017-2109','started_at':'2026-10-18T03:01:12+08:00','frozen_at':now.isoformat(),'deadline':'2026-10-18T03:09:12+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00',
 'required_changes':0,'accepted_scope':'Classical conservative finite-window peak sufficient decision rule under same-reference identity and certified uniform/sampling/peak budgets only; not actual engineering or new-layout prediction.',
 'independent_exact_function_challenges_passed':True,'source_records_verified':12,'source_records_unchanged':True,
 'frozen_prior_records_verified':31,'frozen_prior_small_outputs_verified':97,'frozen_R001_R031':old,'old_manifest_array_references_not_followed':True,
 'cross_reviews':[{'agent':'kernel_sharp_audit','scope':'Uniform-error peak intervals, strict verdicts and shared-reference-error counterexample','required_changes':0},{'agent':'audit_double_mode','scope':'PL union, endpoint-inclusive Lipschitz h/2 and nodal-error bounds','required_changes':0},{'agent':'r006_sharp_challenge','scope':'Author/source integrity, abstract counterexamples, finite scope and unknown56 remainder','required_changes':0}],
 'remaining_unverified':['No real same-reference force/target data or finite missing56 remainder budget established','No engineering peak direction concluded','No ODE realizability claimed for abstract functional challenges','No infinite-tail/new-layout/output-type extension'],
 'outputs':[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json'],
 'UTF8_LF_no_BOM_replacement_or_trailing_whitespace':True,'NPZ_arrays_ODE_author_execution_or_external_search':False,'unknown56_remainder_assumed_zero':False,'only_own_R032_written':True,'shared_manuscript_or_Git_changes':False,'following_task_not_started':True,'stopped_after_handoff':True}
(HERE/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'required_changes':0,'sources':12,'prior_records':31,'prior_small_outputs':97,'principal_files':[record(HERE/n) for n in ['report.md','checks.json','validation.json']]},ensure_ascii=True,indent=2))
