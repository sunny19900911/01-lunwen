from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,xml.etree.ElementTree as ET
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
q=json.loads((O/'source-and-numeric-QA.json').read_text(encoding='utf-8'))
for d in q['sources']:assert sha(Path(d['path']))==d['sha256']
rows=list(csv.DictReader((O/'figure-modal-amplitude-reduction-source-12.csv').open(encoding='utf-8-sig')))
assert len(rows)==12 and {(d['Case'],int(d['Mode'])) for d in rows}=={(c,m) for c in ['SHW3X','SHW4X','RH4X'] for m in [1,2,3,9]}
svg=(O/'figure-modal-amplitude-reduction.svg').read_text(encoding='utf-8')
assert all(w not in svg for w in ['原生','锚点','接口','rcond'])
for d in rows:assert f">{float(d['peak_amplitude_decrease_percent']):.2f}</text>" in svg
assert all(p.stat().st_size<500000 for p in [*O.glob('*.svg'),*O.glob('*.png')])
orig=ET.fromstring(Path(q['sources'][1]['path']).read_text(encoding='utf-8'));new=ET.fromstring((O/'figure-floor-peak-reduction-calculated.svg').read_text(encoding='utf-8'))
geometry=lambda root:[(el.tag,dict(el.attrib)) for el in root.iter() if el.tag.split('}')[-1] in ['circle','line','rect','polyline','path']]
assert geometry(orig)==geometry(new)
assert (O/'figure-floor-peak-reduction-source-36.csv').read_bytes()==Path(q['sources'][2]['path']).read_bytes()
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-30T14:02:51+00:00')).total_seconds();assert elapsed<360
v=dict(frozen_utc=now.isoformat(),started_utc='2026-10-30T14:02:51+00:00',elapsed_seconds=elapsed,actual_render_and_view=True,visual_QA='Both final PNGs opened in view_image; labels, percent units, three colors, 12 values and notes legible; profile top green annotation moved clear of legend',SVG_count=2,PNG_count=2,all_images_under_500KB=True,source_rows_selected=12,source_SHA_unchanged=True,profile_graphics_and_numeric_geometry_identical=True,profile_csv_byte_identical=True,figure_notes_unit_participation_not_floor_contribution=True,Gamma_zero_note=True,no_new_ODE_fit_or_research=True,no_dependency_install=True,no_Git=True)
(O/'visual-QA.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=q['sources']),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False,indent=2))
