from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
v=json.loads((O/'numeric-verification.json').read_text(encoding='utf-8'))
assert all(sha(Path(d['path']))==d['sha256'] for d in v['sources'])
for p in [*O.glob('*.svg'),*O.glob('*.png')]: assert p.stat().st_size<500000
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-30T13:13:35+00:00')).total_seconds()
assert elapsed<=600
qa={'frozen_utc':now.isoformat(),'started_utc':'2026-10-30T13:13:35+00:00','elapsed_seconds':elapsed,'svg_count':2,'png_count':2,'all_images_under_500000_bytes':True,'actual_render':'sharp/libvips; final PNGs opened using view_image','visual_QA':'Chinese labels, axes, units, legends, markers, 36 profile points and four stacked bars/table reviewed; no clipping or missing glyphs seen','source_hashes_rechecked':True,'max_four_point_closure_error_kN':v['max_closure_error_kN'],'no_new_fitting_or_N_extension':True,'no_full_time_history_output':True,'Git_operations':False}
(O/'visual-QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps({'frozen_utc':now.isoformat(),'outputs':files,'inputs':v['sources']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(qa,ensure_ascii=False,indent=2))
