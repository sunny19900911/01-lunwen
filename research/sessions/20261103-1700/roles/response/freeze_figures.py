from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
frozen=json.loads((H/'numeric-delivery-manifest.json').read_text(encoding='utf-8'))
for q in frozen['files']:assert sha(R/q['relative'])==q['sha256']
names=['actual-device-story-reduction-range.png','actual-device-story-reduction-range.svg','actual-device-old-peak-vs-complete-peak.png','actual-device-old-peak-vs-complete-peak.svg','plot_actual_only.py','plot-record.json','figure-QA.md','freeze_figures.py']
d={'status':'frozen-figures','at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'numeric_manifest_unchanged':True,'actual_original_detail_viewed':['actual-device-story-reduction-range.png','actual-device-old-peak-vs-complete-peak.png'],'new_response_computation':False,
 'files':[{'relative':(H/n).relative_to(R).as_posix(),'bytes':(H/n).stat().st_size,'sha256':sha(H/n)}for n in names]}
p=H/'figure-delivery-manifest.json';assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':d['status'],'at':d['at'],'png_hashes':[q['sha256']for q in d['files']if q['relative'].endswith('.png')]},ensure_ascii=False))
