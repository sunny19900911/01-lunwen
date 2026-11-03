"""Read frozen factorized references; no solver, fitting, or source modification."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
OLD = ROOT / 'research/sessions/20261031-1130/roles/role4'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(name, rows):
    with (OUT / name).open('x', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


registry = json.loads((OLD / 'R004/results.json').read_text(encoding='utf-8'))
sources = [item for item in registry['arrays_local_only']
           if any(case in item['path'] for case in ('SHW3X', 'SHW4X'))]
assert len(sources) == 4
frozen_csv = OLD / 'R008/Story5-Story12-top5-other-symmetric-components-72.csv'
with frozen_csv.open(encoding='utf-8-sig') as stream:
    independent_rows = list(csv.DictReader(stream))
summaries, modes, checks, state_checks = [], [], [], []
constants = None
by_case = {}
for item in sources:
    source = Path(item['path'])
    assert sha(source) == item['sha256'], source
    case = 'SHW3X' if 'SHW3X' in source.name else 'SHW4X'
    zeta = .05 if '-z0.05-' in source.name else .08
    with np.load(source, allow_pickle=False) as data:
        time = data['t']
        omega = data['omega']
        coeff = data['B_direct'] * omega ** 2 / 1000
        assert np.allclose(np.diff(time), .02, rtol=0, atol=1e-9)
        assert np.all(data['s_unitGamma'][0] == 0)
        if constants is None:
            constants = (omega.copy(), data['B_direct'].copy())
        else:
            assert np.array_equal(omega, constants[0])
            assert np.array_equal(data['B_direct'], constants[1])
        if case in by_case:
            assert np.array_equal(time, by_case[case][0])
            assert np.array_equal(data['ag'], by_case[case][1])
        else:
            by_case[case] = (time.copy(), data['ag'].copy())
        for story in range(1, 13):
            native = data[f'shear_native_Story{story}_kN']
            parts = data['s_unitGamma'] * coeff[story-1]
            total = parts.sum(axis=1)
            assert np.max(abs(total - data['shear_elastic_inertia_predicted_kN'][:, story-1])) < 1e-8
            i = int(np.argmax(abs(native)))
            j = int(np.argmax(abs(total)))
            row = dict(Case=case, zeta=zeta, Story=story,
                       native_peak_time_s=float(time[i]), native_peak_signed_kN=float(native[i]),
                       native_peak_abs_kN=float(abs(native[i])),
                       reference_at_native_peak_signed_kN=float(total[i]),
                       reference_peak_abs_kN=float(abs(total[j])), reference_peak_time_s=float(time[j]),
                       reference_peak_error_percent=float(100*(abs(total[j])/abs(native[i])-1)),
                       absolute_curve_NRMSE_percent=float(100*np.linalg.norm(abs(total)-abs(native))/np.linalg.norm(native)),
                       reference_mode2_kN=float(parts[i, 1]), reference_mode10_kN=float(parts[i, 9]),
                       reference_mode13_kN=float(parts[i, 12]),
                       reference_modes1to3_kN=float(parts[i, :3].sum()),
                       reference_modes4to300_kN=float(parts[i, 3:].sum()),
                       mode2_over_reference_total_percent=float(100*parts[i, 1]/total[i]),
                       reference_mode10_own_peak_kN=float(max(abs(parts[:, 9]))),
                       reference_mode13_own_peak_kN=float(max(abs(parts[:, 12]))),
                       scope='conditional fixed300 linear reference; not native unique modal forces')
            summaries.append(row)
            if story == 5:
                for k in range(300):
                    modes.append(dict(Case=case, zeta=zeta, Story=story, Mode=k+1,
                                      time_s=float(time[i]), omega_rad_s=float(omega[k]),
                                      reference_signed_shear_kN=float(parts[i, k]),
                                      modal_own_abs_peak_kN=float(max(abs(parts[:, k]))),
                                      scope='reference motion and output coefficient; not observed native modal force'))
                for mode in (1, 2, 3, 10, 13):
                    anchor = 'native5_abspeak' if zeta == .05 else 'native8_abspeak'
                    matched = [r for r in independent_rows if r['Case'] == case and
                               r['Story'] == 'Story5' and r['anchor'] == anchor and r['Mode'] == str(mode)]
                    assert len(matched) == 1
                    value = float(matched[0]['v5_signed_ref_kN' if zeta == .05 else 'v8_signed_ref_kN'])
                    error = float(parts[i, mode-1]-value)
                    assert abs(error) < 1e-8
                    checks.append(dict(Case=case, zeta=zeta, Mode=mode, difference_vs_R008_kN=error))
        state_checks.append(dict(Case=case, zeta=zeta, input_PGA_m_per_s2=float(max(abs(data['ag']))),
                                 output_points=len(time), input_and_response_times_identical_to_frozen_cache=True))

priority = [r for r in summaries if r['Story'] == 5]
comparisons = []
for zeta in (.05, .08):
    left = next(r for r in priority if r['Case'] == 'SHW3X' and r['zeta'] == zeta)
    right = next(r for r in priority if r['Case'] == 'SHW4X' and r['zeta'] == zeta)
    comparisons.append(dict(zeta=zeta,
        native_SH4_minus_SH3_own_peak_kN=right['native_peak_abs_kN']-left['native_peak_abs_kN'],
        reference_SH4_minus_SH3_own_peak_kN=right['reference_at_native_peak_signed_kN']-left['reference_at_native_peak_signed_kN'],
        reference_mode2_difference_kN=right['reference_mode2_kN']-left['reference_mode2_kN'],
        reference_modes1to3_difference_kN=right['reference_modes1to3_kN']-left['reference_modes1to3_kN'],
        reference_modes4to300_difference_kN=right['reference_modes4to300_kN']-left['reference_modes4to300_kN'],
        scope='composition at each input own peak; different times, not same-time causal allocation'))

write_csv('all12-reference-checks-48.csv', summaries)
write_csv('story5-reference-checks-4.csv', priority)
write_csv('story5-all300-signed-reference-1200.csv', modes)
write_csv('independent-frozen-CSV-checks-20.csv', checks)
write_csv('story5-between-input-comparison-2.csv', comparisons)
result = dict(completed_utc=datetime.now(timezone.utc).isoformat(),
              input_sources=sources, frozen_CSV=dict(path=str(frozen_csv), sha256=sha(frozen_csv)),
              code_sha256=sha(Path(__file__)), states=state_checks, priority=priority,
              between_input=comparisons, no_new_ODE=True, no_output_fitting=True,
              no_native_modal_force_claim=True, sources_unchanged=all(sha(Path(i['path'])) == i['sha256'] for i in sources),
              max_independent_difference_kN=max(abs(i['difference_vs_R008_kN']) for i in checks),
              interpretation='This conditional reference does not support modes10/13 dominating SHW4X Story5. Native causal attribution remains unresolved.')
with (OUT / 'results.json').open('x', encoding='utf-8') as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
    stream.write('\n')
print(json.dumps(dict(priority=priority, between_input=comparisons,
                      sources_unchanged=result['sources_unchanged'],
                      max_independent_difference_kN=result['max_independent_difference_kN']),
                 ensure_ascii=False, indent=2))
