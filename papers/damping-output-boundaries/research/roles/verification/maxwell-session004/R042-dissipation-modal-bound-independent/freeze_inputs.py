"""Small input identities only; no author candidate or numerical data."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
paths=[ROOT/'research/sessions/20261017-2109/dissipation-modal-output-bound-protocol-v001.md',ROLE/'R030-force-target-interface-review/report.md',ROLE/'R030-force-target-interface-review/validation.json',ROOT/'research/sessions/20261017-2109/R014-adoption.json',ROLE/'R041-fixed-D-appendix-integration/validation.json']
assert rec(paths[1])['sha256']=='70a7504fa6901051b325db2ee707b7c6fcbb75e22f8ce30781811f113a28ccb5'
target=HERE/'source-freeze.json';assert not target.exists()
out={'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'started_at':'2026-10-18T04:51:37.185518+08:00','deadline':'2026-10-18T04:59:37+08:00','global_deadline':'2026-10-18T07:09:45+08:00','sources':[rec(p) for p in paths],'mathematical_inputs':'Frozen protocol and already audited/adopted C029 only; other validation used for preservation metadata.','new_ideation_R030_candidate_read':False}
target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'protocol':out['sources'][0],'sources':len(paths),'at':out['at']},ensure_ascii=False))
