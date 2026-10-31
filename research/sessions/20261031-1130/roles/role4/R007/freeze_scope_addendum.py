from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.loads((O/'delivery-manifest.json').read_text(encoding='utf-8'))
for d in old['outputs']:assert sha(O/d['name'])==d['sha256']
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T04:30:33+00:00')).total_seconds();assert elapsed<720
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest-v002.json']
(O/'delivery-manifest-v002.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,outputs=files,inputs=old['inputs'],local_only_arrays=old['local_only_arrays'],array_upload_allowed=False,scope_addendum='all N are retained prefixes of fixed300 Ritz basis, not regenerated N-mode software Ritz; thresholds not code sufficiency or efficiency claims',existing_frozen_results_unchanged=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,previous_outputs_unchanged=True),ensure_ascii=False))
