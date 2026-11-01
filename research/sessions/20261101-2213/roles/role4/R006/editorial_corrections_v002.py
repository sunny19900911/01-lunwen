from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
O=Path(__file__).resolve().parent
changes=[('one-page-baseline-sensitivity-engineering-result.md','one-page-baseline-sensitivity-engineering-result-v002.md','Story1二阶的抵消项','Story1第2阶模态的抵消项'),('run-isolation-notes.md','run-isolation-notes-v002.md','公开奖励不/1000','公开框架不/1000')]
for source,target,old,new in changes:
    text=(O/source).read_text(encoding='utf-8');assert text.count(old)==1
    with (O/target).open('x',encoding='utf-8') as f:f.write(text.replace(old,new))
def binding(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
out=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),status='editorial-only additive correction; all old frozen bytes preserved',changes=['Clarify mode2 rather than Taylor order2 for public Story1 opposing term','Correct public-frame wording typo in isolation note'],numerical_files_unchanged=True,original_manifest=binding(O/'delivery-manifest.json'),additive_files=[binding(O/d[1]) for d in changes]+[binding(Path(__file__))])
with (O/'delivery-manifest-v002.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print(out['recorded_utc'])
