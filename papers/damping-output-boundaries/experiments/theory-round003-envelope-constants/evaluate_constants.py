"""C023 sufficient-envelope constants from frozen unit spectrum/rho, no responses."""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal as D, localcontext
from fractions import Fraction
import csv
import hashlib
import json
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
EXPECTED_PROTOCOL = '412ed81e06c892c75f35926f02df743f9536f1f626be12d342dcef025419cb84'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pi_decimal(precision):
    with localcontext() as ctx:
        ctx.prec = precision+25
        multiplier, linear, power, factor = 1, 13591409, 1, 6
        series = D(linear)
        for index in range(1, 12):
            multiplier = multiplier*(factor**3-16*factor)//index**3
            linear += 545140134
            power *= -262537412640768000
            series += D(multiplier*linear)/D(power)
            factor += 12
        value = D(426880)*D(10005).sqrt()/series
        ctx.prec = precision
        return +value


def stringify(value):
    if isinstance(value, D):
        return str(value)
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stringify(item) for item in value]
    return value


def evaluate(model, protocol, precision):
    with localcontext() as ctx:
        ctx.prec = precision
        omega, rho = [D(x) for x in model['omega']], [D(x) for x in model['rho']]
        S, zstar = D(model['S']), D(model['zeta_crit'])
        kf, ef = Fraction(protocol['kappa_exact']), Fraction(protocol['eta_exact'])
        kappa, eta = D(kf.numerator)/kf.denominator, D(ef.numerator)/ef.denominator
        c0 = D(protocol['c0_exact'])
        zminus, zplus = (1-eta)*zstar, kappa*(1+eta)*zstar
        gaps = [S*S-w*w for w in omega]
        dminus = D(1)
        dplus = D(1)
        for gap, w in zip(gaps, omega):
            dminus *= gap
            dplus *= (gap*gap+(2*zplus*w*S)**2).sqrt()
        bk = (kappa-1)*(kappa+3)/4
        A, B = c0*(2+eta)/dminus, c0*bk/dplus
        second_gamma = 1/(zplus+max(zplus*zplus-1, D(0)).sqrt())
        gamma = min(zminus, second_gamma)
        modal_absolute_sum = sum(abs(r)/w**3 for r,w in zip(rho, omega))
        M = 2*gamma**(-3)*modal_absolute_sum
        pi = pi_decimal(precision)
        E = pi*M/2
        T0, Tenv, C = 2*E/B, E/A, B/(2*A)
        constants = {'kappa': kappa, 'eta': eta, 'c0': c0, 'b_kappa': bk,
            'zeta_star': zstar, 'zeta_minus': zminus, 'zeta_plus': zplus,
            'D_minus': dminus, 'D_plus': dplus, 'A': A, 'B': B,
            'gamma': gamma, 'second_gamma_candidate': second_gamma,
            'sum_abs_rho_over_omega_cubed': modal_absolute_sum,
            'M': M, 'pi': pi, 'E': E, 'T0': T0, 'Tenv': Tenv, 'C': C}
        rows = []
        for text_delta in protocol['delta_values']:
            delta = D(text_delta)
            crossing = Tenv/delta
            combined = max(T0, crossing)
            rows.append({'delta': delta, 'Tenv_over_delta_half_duration_s': crossing,
                'T0_half_duration_s': T0, 'max_T0_Tcross_half_duration_s': combined,
                'full_input_support_2T_s': 2*combined,
                'crossing_half_duration_days': crossing/86400,
                'crossing_half_duration_years_365_days': crossing/(86400*365),
                'crossing_numerically_above_T0': crossing >= T0})
        return constants, rows


def main():
    started = time.perf_counter()
    protocol_path = HERE/'protocol.json'
    assert sha(protocol_path) == EXPECTED_PROTOCOL
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    sources = [(HERE/protocol[key]).resolve() for key in ['source_model', 'candidate_path', 'review_path']]
    expected = [protocol[key] for key in ['source_model_sha256', 'candidate_sha256', 'review_sha256']]
    assert all(sha(path) == digest for path,digest in zip(sources, expected))
    output_paths = [HERE/'envelope_constants.json', HERE/'four_crossover_durations.csv', HERE/'run_record.json']
    assert not any(path.exists() for path in output_paths), 'Refuse to overwrite frozen output'
    data = json.loads(sources[0].read_text(encoding='utf-8'))
    model = data['fixed_model']
    assert 'rho' in model and len(model['rho']) == len(model['omega']) == 3
    assert D(model['L']) == 1 and D(data['kappa']) == D('1.6')
    original_deltas = sorted({D(row['abs_r_minus_1']) for row in data['rows']}, reverse=True)
    assert original_deltas == [D(value) for value in protocol['delta_values']]
    values, rows = evaluate(model, protocol, protocol['precision_digits'])
    fine, _ = evaluate(model, protocol, protocol['arithmetic_crosscheck_digits'])
    with localcontext() as ctx:
        ctx.prec = protocol['precision_digits']
        relative_differences = {key: abs(values[key]/fine[key]-1) for key in ['A','B','gamma','M','E','T0','Tenv','C']}
        checks = {
            'rho_present_in_original_frozen_model': True,
            'four_original_delta_values_only': len(rows) == 4,
            'positive_amplitude_and_time_constants': all(values[key] > 0 for key in ['A','B','gamma','M','E','T0','Tenv','C']),
            'unit_interval_is_underdamped_and_gamma_equals_zeta_minus': values['zeta_plus'] < 1 and values['gamma'] == values['zeta_minus'],
            'all_original_deltas_within_eta': all(D(row['delta']) <= values['eta'] for row in rows),
            'pi_known_prefix': str(values['pi']).startswith('3.14159265358979323846264338327950288419716939937510'),
            'T0_over_Tenv_equals_inverse_C_numerically': abs(values['T0']/values['Tenv']-1/values['C']) < D('1e-80'),
            'arithmetic_90_vs_110_relative_difference_below_1e_80': max(relative_differences.values()) < D('1e-80'),
            'all_sources_and_protocol_unchanged': sha(protocol_path) == EXPECTED_PROTOCOL and all(sha(path) == digest for path,digest in zip(sources, expected)),
            'elapsed_under_420_seconds': time.perf_counter()-started < 420,
        }
    result = {'evidence_id': protocol['evidence_id'], 'session': protocol['session'], 'review_status': 'candidate',
        'finished_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.perf_counter()-started,
        'code_sha256': sha(__file__), 'protocol_sha256': EXPECTED_PROTOCOL,
        'precision_digits': protocol['precision_digits'], 'arithmetic_crosscheck_digits': protocol['arithmetic_crosscheck_digits'],
        'arithmetic': 'Decimal ROUND_HALF_EVEN, ordinary approximations; no directed rounding',
        'reused_original_values': {key: model[key] for key in ['omega','rho','S','zeta_crit']},
        'constants': values, 'four_existing_delta_rows': rows, 'arithmetic_relative_differences': relative_differences,
        'checks': checks, 'limits': protocol['limits'],
        'no_new_response_r_spectrum_or_fit': True,
        'duration_convention': 'T is envelope half-duration in consistent synthetic model seconds; complete input support is 2T; years use exactly 365 days for scale illustration.'}
    output_paths[0].write_text(json.dumps(stringify(result), ensure_ascii=False, indent=2), encoding='utf-8')
    with output_paths[1].open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(stringify(rows))
    passed = all(checks.values())
    record = {'evidence_id': protocol['evidence_id'], 'review_status': 'candidate',
        'finished_utc': result['finished_utc'], 'elapsed_seconds': result['elapsed_seconds'],
        'command_argv': [sys.executable, str(Path(__file__).resolve())], 'cwd': str(Path.cwd()),
        'python': platform.python_version(), 'dependencies': 'standard library only',
        'exit_code_after_checks': 0 if passed else 1, 'checks': checks,
        'protocol_file_last_write_utc': datetime.fromtimestamp(protocol_path.stat().st_mtime, timezone.utc).isoformat(),
        'sources': [{'file': str(path), 'sha256': digest} for path,digest in zip([protocol_path]+sources, [EXPECTED_PROTOCOL]+expected)],
        'files': [{'file': path.name, 'bytes': path.stat().st_size, 'sha256': sha(path)} for path in [Path(__file__)]+output_paths[:2]],
        'source_rho_present_no_gap_filled_by_new_spectrum': True,
        'no_new_response_r_spectrum_or_fit': True}
    output_paths[2].write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(stringify({'constants': values, 'rows': rows, 'checks': checks,
        'max_arithmetic_relative_difference': max(relative_differences.values()), 'elapsed_seconds': result['elapsed_seconds']}), ensure_ascii=False, indent=2))
    assert passed


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
