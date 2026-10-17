"""Verify small records only; explicit suffix guard prevents NPZ/PDF access."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
sources=read(HERE/'source-freeze.json')['verified_small_sources']
assert len(sources)==21 and all(record(Path(x['path']))==x for x in sources)
r30=ROLE/'R030-force-target-interface-review/validation.json'
assert record(r30)['sha256']=='26559abd4a51d2d0fee7a96452d6c38cc18de8295209d667be458aadf632a4da'
old=read(r30)['frozen_R001_R029']+[{'run_file':'R030-force-target-interface-review/validation.json','sha256':record(r30)['sha256'],'outputs_verified':5}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outs)==item['outputs_verified']
    for x in outs:assert record(Path(x['path']))==x
    total+=len(outs)
assert len(old)==30 and total==92
c=read(HERE/'checks.json');assert c['required_changes']==0 and not c['NPZ_read_decode_or_rehash'] and not c['full98305_data_certified']
assert not c['recomputed_whole_window_max_or_RMS'] and not c['nonlinear_ODE_or_author_replay_executed']
for p in HERE.iterdir():
    if p.is_file():
        b=p.read_bytes();s=b.decode('utf-8')
        assert not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b and '\ufffd' not in s,p
        assert all(line==line.rstrip() for line in s.splitlines()),p
now=datetime.now(timezone(timedelta(hours=8)))
assert now.isoformat()<'2026-10-18T03:04:06+08:00'
out={'review':'R031','session':'20261017-2109','started_at':'2026-10-18T02:54:06+08:00','frozen_at':now.isoformat(),'deadline':'2026-10-18T03:04:06+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00',
 'required_changes':0,'accepted_scope':'R019 source/small-file implementation review plus two low-dimensional rounded-operator and four scalar baseline challenges only; whole98305 data and error statistics not independently certified.',
 'independent_challenges_passed':True,'verified_small_source_count':21,'small_sources_unchanged':True,'NPZ_read_decode_or_rehash':False,'whole_window_replay_or_ODE':False,
 'frozen_prior_records_verified':30,'frozen_prior_small_outputs_verified':92,'frozen_R001_R030':old,'old_manifest_NPZ_references_not_followed':True,
 'cross_reviews':[{'agent':'kernel_sharp_audit','scope':'FOH endpoint reversal, A/E/inverse and thirteen-term integral series','required_changes':0},{'agent':'audit_double_mode','scope':'Modal force/output signs, U cutoff and snapshot step indexing/scope','required_changes':0},{'agent':'r006_sharp_challenge','scope':'Small manifest, four snapshots and recorded finite-error gate consistency','required_changes':0}],
 'remaining_unverified':['Current NPZ identity and actual contents not read/decode/rehashed','Whole98305 maximum/RMS and recurrence not rerun','Exact-model parameter rounding, force interpolation, source trajectory and recursive/continuous all-window errors not bounded','No independent physical/new-input/new-layout prediction or unknown force-tail certification'],
 'outputs':[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json'],
 'UTF8_LF_no_BOM_replacement_or_trailing_whitespace':True,'only_own_R031_written':True,'shared_manuscript_Git_or_external_changes':False,'following_task_not_started':True,'stopped_after_handoff':True}
(HERE/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'required_changes':0,'small_sources':21,'prior_records':30,'prior_small_outputs':92,'NPZ_access':False,'principal_files':[record(HERE/n) for n in ['report.md','checks.json','validation.json']]},ensure_ascii=True,indent=2))
