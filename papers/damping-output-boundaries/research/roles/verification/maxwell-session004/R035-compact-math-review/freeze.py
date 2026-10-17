from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
sources=read(HERE/'source-freeze.json')
assert len(sources)==22 and all(record(Path(x['path']))==x for x in sources)
r34=ROLE/'R034-asymmetric-neighborhood-review/validation.json'
assert record(r34)['sha256']=='f6be5daa1dd85abcc8ceda164a5d8660397fbb3641c6de9e2f7b4026a01d7311'
old=read(r34)['frozen_R001_R033']+[{'run_file':'R034-asymmetric-neighborhood-review/validation.json','sha256':record(r34)['sha256'],'outputs_verified':5}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outs)==item['outputs_verified']
    for x in outs:assert record(Path(x['path']))==x
    total+=len(outs)
assert len(old)==34 and total==112
assert read(HERE/'findings.json')['required_changes']==1
for p in HERE.iterdir():
    if p.is_file():
        b=p.read_bytes();s=b.decode('utf-8')
        assert not b.startswith(b'\xef\xbb\xbf') and b'\r' not in b and '\ufffd' not in s,p
        assert all(line==line.rstrip() for line in s.splitlines()),p
now=datetime.now(timezone(timedelta(hours=8)))
assert now.isoformat()<'2026-10-18T03:32:44+08:00'
out={'review':'R035','session':'20261017-2109','started_at':'2026-10-18T03:24:44+08:00','frozen_at':now.isoformat(),'deadline':'2026-10-18T03:32:44+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00',
 'required_changes':1,'clarification_recommendations':2,'integration_acceptance':'Hold v001 pending explicit C026 nominal-sine cutoff correction; no bottom-level result challenged.',
 'source_records_verified':22,'sources_and_draft_unchanged':True,'frozen_prior_records_verified':34,'frozen_prior_small_outputs_verified':112,'frozen_R001_R034':old,'array_references_not_followed':True,
 'cross_reviews':[{'agent':'kernel_sharp_audit','scope':'Mathematical scopes and finite input; table amplitude clarified separately from certain error','certain_mustfix':1},{'agent':'audit_double_mode','scope':'RMSE denominator, model/native dissipation and endpoint-energy terminology','certain_mustfix':0},{'agent':'r006_sharp_challenge','scope':'Compact/source identities, C031 comparison and C028-C030 range','certain_mustfix':0}],
 'verification_scope':'Static integration, safe decimal/hex transcript and source/line/link checks only; no original data, proof recertification or replay.',
 'outputs':[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json'],
 'UTF8_LF_no_BOM_replacement_or_trailing_whitespace':True,'original_draft_author_freeze_shared_or_Git_modified':False,'ODE_arrays_NPZ_PDF_source_execution_external_search':False,'only_own_R035_written':True,'following_task_not_started':True,'stopped_after_handoff':True}
(HERE/'validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'required_changes':1,'clarifications':2,'sources':22,'prior_records':34,'prior_outputs':112,'principal_files':[record(HERE/n) for n in ['report.md','findings.json','validation.json']]},ensure_ascii=True,indent=2))
