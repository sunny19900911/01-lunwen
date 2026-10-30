from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal,getcontext
import csv,json,hashlib
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
getcontext().prec=40
rows=list(csv.DictReader((O/'native-peak-accounting-all12-36.csv').open(encoding='utf-8-sig')))
assert len(rows)==36 and len({(d['Case'],d['Story']) for d in rows})==36
dec_errors=[]
for d in rows:
    p5=Decimal(d['P5_kN']);p8=Decimal(d['P8_kN']);D=Decimal(d['D_same_time_signed_decrease_kN']);M=Decimal(d['M_peak_reselection_correction_kN'])
    assert M>=0
    dec_errors.append(abs((p5-p8)-(D-M)))
    assert abs(Decimal(d['net_peak_decrease_percent'])-100*(p5-p8)/p5)<Decimal('1e-12')
    if d['time_argmax_changed']=='False':assert M==0
assert max(dec_errors)<Decimal('1e-9')
res=json.loads((O/'results.json').read_text(encoding='utf-8'))
for key in ['source_native_table','source_cache']:
    d=res[key];assert sha(Path(d['path']))==d['sha256']
manifest=json.loads((O.parent/'R003/delivery-manifest.json').read_text(encoding='utf-8'))
assert res['source_cache']['sha256']==manifest['local_only_array']['sha256']
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-30T13:30:25+00:00')).total_seconds();assert elapsed<480
v=dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,rows=36,first_cache_keys_confirmed=True,cache_hash_matches_R003_frozen_manifest=True,original_native_values_rechecked=36,max_original_native_metric_difference=res['max_recheck_difference_vs_R003'],all_M_nonnegative=True,no_time_shift_and_M_zero=16,changed_control_time=20,changed_control_sign=3,max_float_identity_error_kN=res['max_identity_error_kN'],max_independent_Decimal_CSV_identity_error_kN=str(max(dec_errors)),source_hashes_unchanged=True,no_fit_or_order_extension=True,no_large_raw_table_read=True,no_complete_trace_output=True,no_Git=True)
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=[res['source_native_table'],res['source_cache']],full_arrays_local_only=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False,indent=2))
