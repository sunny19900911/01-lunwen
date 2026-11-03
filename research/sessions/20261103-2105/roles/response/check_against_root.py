from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
H=Path(__file__).resolve().parent;S=H.parents[1]
def read(p):
 with p.open(encoding='utf-8-sig')as f:return list(csv.DictReader(f))
rp=S/'root-four-records.csv';root=read(rp)
own={(r['Story'].replace('Story',''),r['Case']):r for r in read(H/'at-actual-QT-peak-4.csv')}
peaks={(r['Story'].replace('Story',''),r['Case']):r for r in read(H/'plus-minus-direction-sensitivity-4.csv')}
fields={'time_QT_peak_s':'time_s','QT_kN':'QT_D_signed_kN','QD_J_resisting_kN':'QD_J_resisting_signed_kN','QT_minus_QD_kN':'QT_minus_QD_algebraic_kN','QT_plus_QD_kN':'QT_plus_QD_algebraic_kN','SourceRow':'D_QT_SourceRow'}
pfields={'peak_abs_QT_kN':'QT_abs_peak_kN','peak_abs_QT_minus_QD_kN':'QT_minus_QD_abs_peak_kN','peak_abs_QT_plus_QD_kN':'QT_plus_QD_abs_peak_kN'}
res=[]
for r in root:
 key=(r['Story'],r['Case']);q=own[key];p=peaks[key]
 for name,local in fields.items():res.append(float(r[name])-float(q[local]))
 for name,local in pfields.items():res.append(float(r[name])-float(p[local]))
assert len(root)==4 and len(res)==36 and max(abs(x)for x in res)==0
d={'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'root_source_sha256':hashlib.sha256(rp.read_bytes()).hexdigest(),'own_numbers_computed_and_frozen_before_reading_root_table':True,'rows':4,'numeric_fields_compared':36,'max_absolute_difference':max(abs(x)for x in res),'must':0,'no_new_arrays_read':True,'figure_task':'Root owns requested 2x2 figure; this role did not begin or duplicate plotting'}
p=H/'root-cross-check.json';assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d,ensure_ascii=False))
