"""Freeze only R030; verify prior manifests and read-only source records."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
sources=read(HERE/'source-freeze.json')
assert len(sources)==31 and all(record(Path(x['path']))==x for x in sources)
r29=ROLE/'R029-modal-sign-corollary/validation.json'
assert record(r29)['sha256']=='dd6535373ad0ce6a8356b03734ec6b12963f4827e34d6013a0922b618714c291'
old=read(r29)['frozen_R001_R028']+[{'run_file':'R029-modal-sign-corollary/validation.json','sha256':record(r29)['sha256'],'outputs_verified':5}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outs)==item['outputs_verified']
    for x in outs:assert record(Path(x['path']))==x
    total+=len(outs)
assert len(old)==29 and total==87
for x in read(ROLE/'R028/R028-proof-evidence.json')['artifacts']:assert record(Path(x['path']))==x
for x in read(ROLE/'R029-modal-sign-corollary/source-freeze.json'):assert record(Path(x['path']))==x
c=read(HERE/'checks.json')
assert c['required_changes']==0 and c['complete_modal_transfer_identity_polynomial_all_s']
assert not c['actual_engineering_interface_certified']
for p in HERE.iterdir():
    if p.is_file():
        b=p.read_bytes();s=b.decode('utf-8')
        assert not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b and '\ufffd' not in s,p
        assert all(line==line.rstrip() for line in s.splitlines()),p
now=datetime.now(timezone(timedelta(hours=8)))
assert now.isoformat()<'2026-10-18T02:53:43+08:00'
out={'review':'R030','session':'20261017-2109','started_at':'2026-10-18T02:43:43+08:00','frozen_at':now.isoformat(),'deadline':'2026-10-18T02:53:43+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00',
 'required_changes':0,'accepted_scope':'Classical conditional full-force/same-reference displacement-difference interface only; no actual FNA operator, damping, export force or engineering reconstruction certified.',
 'independent_rational_polynomial_checks_passed':True,'source_records_verified':31,'source_records_unchanged':True,'historical_first_SHA_and_current_versions_preserved':True,
 'frozen_prior_records_verified':29,'frozen_prior_outputs_verified':87,'frozen_R001_R029':old,
 'cross_reviews':[{'agent':'kernel_sharp_audit','scope':'Modal convolution, mass scaling, force signs, IC cancellation and remainder/finite-window conditions','required_changes':0},{'agent':'audit_double_mode','scope':'FNA residual/reference pairing, U0 compensation and same-C/Link counterfactual limits','required_changes':0},{'agent':'r006_sharp_challenge','scope':'Minimum fields, partial devices/modes, sampling/tail and output limits','required_changes':0}],
 'outputs':[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json'],
 'UTF8_LF_no_BOM_replacement_or_trailing_whitespace':True,'no_PDF_arrays_ODE_external_search_or_source_execution':True,'only_own_new_R030_written':True,'no_shared_manuscript_or_Git_changes':True,'following_task_not_started':True,'stopped_after_handoff':True}
(HERE/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'required_changes':0,'sources':31,'prior_records':29,'prior_outputs':87,'principal_files':[record(HERE/n) for n in ['report.md','checks.json','validation.json']]},ensure_ascii=True,indent=2))
