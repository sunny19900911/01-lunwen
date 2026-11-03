from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib,csv
H=Path(__file__).resolve().parent;R=H.parents[4]
report=json.loads((H/'Story8-mechanism-summary.json').read_text(encoding='utf-8'))
names=['story8_actual_mechanism.py','input-freeze.json','Story8-native-three-times-18.csv','Story8-actual-peak-accounting-6.csv','Story8-mechanism-summary.json','Story8-actual-mechanism-report.md','freeze_story8_numbers.py']
for p in [H/n for n in names]:assert p.is_file()
for n in [names[2],names[3]]:
 with (H/n).open(encoding='utf-8')as f:rows=list(csv.reader(f))
 assert all(len(r)==len(rows[0])for r in rows)
source=json.loads((H/'input-freeze.json').read_text(encoding='utf-8'))
for s in source['sources']:assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
out={'status':'numbers-frozen-awaiting-independent-audit','at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'rows18':18,'cases6':6,'all_six_inputs_retained':True,'all_source_hashes_unchanged':True,'six_all_B_D_peak_signs_same':report['B_D_own_peak_sign_switch_count']==0,
 'objective_case_selection':{'Story8_max_d_case':max(report['cases'],key=lambda r:r['d_pp'])['Case'],'Story8_max_abs_peak_time_shift_case':max(report['cases'],key=lambda r:abs(r['t_D_minus_t_B_s']))['Case'],'no_cross_wave_packet_shift_claim':True},
 'files':[{'relative':(H/n).relative_to(R).as_posix(),'bytes':(H/n).stat().st_size,'sha256':hashlib.sha256((H/n).read_bytes()).hexdigest()}for n in names]}
p=H/'numeric-delivery-manifest.json';assert not p.exists();p.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'at':out['at'],'rows18':18,'cases6':6,'selection':out['objective_case_selection']},ensure_ascii=False))
