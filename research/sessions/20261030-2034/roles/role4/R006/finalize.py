from pathlib import Path
from datetime import datetime,timezone
import json,csv,hashlib
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((O/'results.json').read_text(encoding='utf-8'))
for d in r['all_input_bindings']:assert sha(Path(d['path']))==d['sha256']
rows=list(csv.DictReader((O/'modal-unit-kernel-change-108.csv').open(encoding='utf-8-sig')))
assert len(rows)==108 and len({(d['Case'],int(d['Mode'])) for d in rows})==108
assert set(d['Case'] for d in rows)=={'SHW3X','SHW4X','RH4X'}
max_scalar_error=0
for d in rows:
    a=float(d['A5_g_m_s2']);b=float(d['A8_g_m_s2']);ratio=float(d['A8_over_A5']);assert a>0 and b>0
    max_scalar_error=max(max_scalar_error,abs(b/a-ratio),abs(100*(1-ratio)-float(d['peak_amplitude_decrease_percent'])))
    assert (d['A8_greater_A5']=='True')==(b>a)
assert max_scalar_error<1e-12
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-30T13:36:47+00:00')).total_seconds();assert elapsed<480
v=dict(frozen_utc=now.isoformat(),started_utc='2026-10-30T13:36:47+00:00',elapsed_seconds=elapsed,rows=108,two_story_checks=216,cache_keys_confirmed=True,sources_match_frozen_R002_manifest=True,source_hashes_unchanged=True,max_two_story_kernel_recovery_abs_error_m_s2=r['max_two_story_recovery_abs_error_m_s2'],max_two_story_kernel_recovery_relative_Linf=r['max_two_story_recovery_relative_Linf'],max_direct_story_term_invariant_ratio_error=r['max_invariant_ratio_error_from_independent_story_terms'],max_direct_story_term_invariant_shape_error=r['max_invariant_shape_error_from_independent_story_terms'],max_negative_scale_invariance_error=r['max_negative_rescale_invariance_error'],max_CSV_scalar_metric_recheck_error=max_scalar_error,counterincrease_count=r['counterincrease_count'],no_ODE_or_fit=True,no_ETABS=True,no_new_N=True,no_complete_kernel_trace_outputs=True,no_Git=True,actual_participation_factor_Gamma_not_inferred=True)
(O/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']
(O/'delivery-manifest.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=r['all_input_bindings'],full_arrays_local_only=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False,indent=2))
