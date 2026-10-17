"""Verify unchanged sources and prior rounds, then freeze this role's evidence."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
sources=read(HERE/'source-before.json')
assert all(record(Path(x['path']))==x for x in sources)
r27=ROLE/'R027/R027-review-validation.json'
assert record(r27)['sha256']=='66e7235daaf8dd061f512bb61687bb10d4c0d4c7b36db2dbd5974b5620989917'
old=read(r27)['frozen_R001_R026']+[{'run_file':'R027/R027-review-validation.json','sha256':record(r27)['sha256'],'outputs_verified':2}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outs)==item['outputs_verified'],p
    for x in outs:assert record(Path(x['path']))==x,(p,x)
    total+=len(outs)
assert len(old)==27 and total==80
fraction=read(HERE/'fraction-challenges-result.json');assert fraction['passed']
replay=read(HERE/'isolated-run/summary_r017.json')
assert read(HERE/'replay-invocation.json')['exit_code']==0
evidence={'review':'R028','session':'20261017-2109','required_changes':0,
 'scope':'Conditional all-time U bound plus fixed D point-witness comparison for the frozen synthetic addition model; U analytic proof independent of numerical helper.',
 'U_analytic':{'modal_eigenvalues':[1,3],'bare_zeta_exact':'1/20','Ap_squared_exact':'50/51','R_squared_exact':'40000/20349','loading_uniform_upper_strict':'241/100','full_free_tail_uniform_upper_strict':'141/80','all_time_supremum_strictly_below':'241/100'},
 'fixed_D':{'N':16384,'J':16529,'post_stop_segments':145,'not_author_T_example':True,'no_true_D_peak_or_tail_end_claim':True},
 'independent_fraction_checks':fraction,'isolated_replay':{'elapsed_seconds':replay['elapsed_seconds'],'all16529_segments':True,'exact_values_and_blocks_equal':True,'CSV_byte_equal':True,'independent_algorithm':False},
 'cross_reviews':[{'agent':'kernel_sharp_audit','scope':'U modal solution coefficients, uniform sup and all-tail bound','required_changes':0},{'agent':'audit_double_mode','scope':'Full source/model/weights/port/h+h4/input/sum/witness directions','required_changes':0},{'agent':'r006_sharp_challenge','scope':'Frozen cache columns/index/initial state and exact Fraction final subtraction directions','required_changes':0}],
 'source_records':sources,'all_source_records_unchanged':True,'frozen_prior_records_verified':27,'frozen_prior_outputs_verified':80,
 'contracts':['R024 full state residual theorem, continuous PL, zero initial error','Frozen helper v002 with complete binary64 nearest/gradual-underflow/no FTZ-DAZ/correct nextafter contract','Python Fraction arithmetic and NumPy decoder contract; builtin int root degrees 2/3','Role1 provenance/helper/machine review remains a separate root acceptance gate'],
 'safe_exact_decimal_publication_bounds':{'U_sup_strict_upper':'2.41','D_fixed_witness_lower':'4.34911558','strict_gap_lower':'1.93911558','I_J_strict_upper':'0.715880662'},
 'no_ODE_real_engineering_or_tuning':True,'only_own_R028_written':True,
 'artifacts':[record(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name not in ['R028-proof-evidence.json','R028-review-validation.json']]}
write(HERE/'R028-proof-evidence.json',evidence)
authored=[p for p in HERE.iterdir() if p.is_file()]
for p in authored:
    b=p.read_bytes();b.decode('utf-8');assert not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b,p
    assert not any(line.rstrip()!=line for line in b.decode('utf-8').splitlines()),p
now=datetime.now(timezone(timedelta(hours=8)))
assert now.isoformat()<'2026-10-18T02:25:00+08:00'
out={'review':'R028','session':'20261017-2109','started_at':'2026-10-18T02:13:00+08:00','frozen_at':now.isoformat(),'deadline':'2026-10-18T02:25:00+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','required_changes':0,
 'accepted_scope':'Conditional frozen addition-model U full-time bound and D fixed witness strict comparison; subject to complete helper/runtime contract and separate role1 audit.',
 'protocol_and_sources_unchanged':True,'source_records_verified':len(sources),'frozen_prior_records_verified':27,'frozen_prior_outputs_verified':80,'frozen_R001_R027':old,
 'outputs':[record(HERE/'R028-review-report.md'),record(HERE/'R028-proof-evidence.json')],
 'authored_UTF8_LF_no_BOM_or_trailing_whitespace':True,'raw_isolated_copies_preserve_frozen_line_endings':True,'no_ODE_or_real_engineering_read':True,'following_task_not_started':True,'stopped_after_handoff':True}
write(HERE/'R028-review-validation.json',out)
print(json.dumps({'required_changes':0,'prior_records':len(old),'prior_outputs':total,'sources':len(sources),'principal_files':[record(HERE/n) for n in ['R028-review-report.md','R028-proof-evidence.json','R028-review-validation.json']]},ensure_ascii=True,indent=2))
