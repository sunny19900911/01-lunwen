"""Freeze small analytical R034 review, preserving all preceding records."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
sources=read(HERE/'source-freeze.json')
assert len(sources)==17 and all(record(Path(x['path']))==x for x in sources)
r33=ROLE/'R033-force-feedback-closure-review/validation.json'
assert record(r33)['sha256']=='3bfd9e9865afd913fc4cf6b6147d956783ed8a2c259cbedbc2034e093b36b3f3'
old=read(r33)['frozen_R001_R032']+[{'run_file':'R033-force-feedback-closure-review/validation.json','sha256':record(r33)['sha256'],'outputs_verified':5}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outs)==item['outputs_verified']
    for x in outs:assert record(Path(x['path']))==x
    total+=len(outs)
assert len(old)==33 and total==107
c=read(HERE/'checks.json');assert c['required_changes']==0 and c['fixed_thresholds_passed']
assert c['nominal_radius_lt_1_098'] and c['not_inferred_from_output_tail']
assert not c['NPZ_arrays_ODE_helper_source_execution_or_spectral_scan']
for p in HERE.iterdir():
    if p.is_file():
        b=p.read_bytes();s=b.decode('utf-8')
        assert not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b and '\ufffd' not in s,p
        assert all(line==line.rstrip() for line in s.splitlines()),p
now=datetime.now(timezone(timedelta(hours=8)))
assert now.isoformat()<'2026-10-18T03:28:07+08:00'
out={'review':'R034','session':'20261017-2109','started_at':'2026-10-18T03:18:07+08:00','frozen_at':now.isoformat(),'deadline':'2026-10-18T03:28:07+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00',
 'required_changes':0,'accepted_scope':'Conditional analytic whole continuous fixed-parameter |a|<=1e-6 family, fixed physical C0, same-layout comparison and true all-time peak separation; all original C025 contracts inherited.',
 'nominal_H_complete_true_state_radius_source_gate_passed':True,'binary64_Fraction_square_and_sum_checks_passed':True,'all_original_thresholds_passed_without_tuning':True,
 'source_records_verified':17,'source_records_unchanged':True,'frozen_prior_records_verified':33,'frozen_prior_small_outputs_verified':107,'frozen_R001_R033':old,'old_manifest_array_references_not_followed':True,
 'cross_reviews':[{'agent':'kernel_sharp_audit','scope':'Global solution, Ka error storage/forcing, norm conversions, true passive tail and uniform strict sup','required_changes':0},{'agent':'audit_double_mode','scope':'Original complete-state triangle and terminal full-energy implementation provenance','required_changes':0},{'agent':'r006_sharp_challenge','scope':'Independent exact endpoints, q/rho/thresholds and fixed-C/history limits','required_changes':0}],
 'not_claimed':['Time-varying parameter a(t)','Same-a A/B energy or device histories after asymmetry','Reset modal 5percent damping while keeping physical C0','Engineering manufacturing tolerance, actual building transfer, optimized layout or priority','Unconditional machine/formal certification'],
 'outputs':[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json'],
 'UTF8_LF_no_BOM_replacement_or_trailing_whitespace':True,'NPZ_arrays_ODE_source_execution_helper_import_PDF_or_spectral_scan':False,'only_own_R034_written':True,'shared_manuscript_or_Git_changes':False,'following_task_not_started':True,'stopped_after_handoff':True}
(HERE/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'required_changes':0,'sources':17,'prior_records':33,'prior_small_outputs':107,'principal_files':[record(HERE/n) for n in ['report.md','checks.json','validation.json']]},ensure_ascii=True,indent=2))
