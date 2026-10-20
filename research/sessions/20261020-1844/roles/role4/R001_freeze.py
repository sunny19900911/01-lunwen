from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
counts={'R001-story-forces-72.csv':72,'R001-story-drifts-144.csv':144,'R001-main-axis-controls-6.csv':6,'R001-three-model-availability.csv':3,'R001-response-cache-table-index.csv':22,'R001-first-three-modal-summary.csv':9}
for n,c in counts.items():
 with (O/n).open(encoding='utf-8-sig',newline='') as f:assert len(list(csv.DictReader(f)))==c
start=datetime.fromisoformat('2026-10-20T10:44:45+00:00');end=datetime.now(timezone.utc);p=O/'R001-delivery-manifest.json';assert not p.exists()
x={'status':'frozen complete scope; task budget exceeded','start_observed_utc':start.isoformat(),'first_table_saved_utc':'2026-10-20T10:45:23.721134+00:00','frozen_utc':end.isoformat(),'frozen_local':end.astimezone(timezone(timedelta(hours=8))).isoformat(),'elapsed_seconds':(end-start).total_seconds(),'within_8min':end<=start+timedelta(minutes=8),'first_table_within_8min':True,'new_workbook_reads':0,'solver_runs':0,'plotting_imports':0,'native_modal_decompositions':0,'CSV_readback_counts':counts,'files':[{'path':str(z),'bytes':z.stat().st_size,'sha256':sha(z)} for z in sorted(O.glob('R001*')) if z.is_file()]}
p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:x[k] for k in ['frozen_local','elapsed_seconds','within_8min']},ensure_ascii=False))
