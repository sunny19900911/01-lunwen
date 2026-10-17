"""Freeze only specified old analytic inputs and preservation metadata."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
paths=[ROOT/'research/sessions/20261017-2109/input-budget-dissipation-corollary-protocol-v001.md',ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R010-system-energy-interface/report.md',ROLE/'主体Maxwell位移能量界接口独审-R018.md',ROLE/'R018-review-validation.json',ROLE/'R042-dissipation-modal-bound-independent/report.md',ROLE/'R042-dissipation-modal-bound-independent/post-freeze-comparison/report.md',ROOT/'research/sessions/20261017-2109/R021-adoption.json',ROLE/'R044-mass-participation-independent/validation.json',ROLE/'R044-mass-participation-independent/post-freeze-comparison/comparison-freeze.json']
assert rec(paths[1])['sha256']=='676f41e6b0826e0dd0a358568c0f212458738d952d041b5c630be0386894f3e3'
out={'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'started_at':'2026-10-18T05:26:02.880167+08:00','protocol_started_at':'2026-10-18T05:25:50.718195+08:00','conservative_deadline':'2026-10-18T05:33:50+08:00','global_deadline':'2026-10-18T07:09:45+08:00','sources':[rec(p) for p in paths],'new_counterparty_package_read':False,'scope':'Old R010/R018 and admitted C039 only; other validations are identity metadata. No arrays or scientific data.'}
p=HERE/'source-freeze.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'at':out['at'],'sources':len(paths),'protocol':out['sources'][0],'old_R018':out['sources'][2]},ensure_ascii=False))
