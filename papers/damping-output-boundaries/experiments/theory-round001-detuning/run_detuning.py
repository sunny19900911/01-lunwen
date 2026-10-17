"""Eight preregistered unit-topcut detunings; harmonic values only, no time response."""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal as D, localcontext
import ast
import csv
import hashlib
import json
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
TOPIC = HERE.parents[1]
EXPECTED_PROTOCOL = 'd78cddd9e48036c803be51ae50efcf43d49ed89cfce95e109a6cc329c3c640b8'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started = time.perf_counter()
    protocol_path = HERE/'protocol.json'
    assert sha(protocol_path) == EXPECTED_PROTOCOL, 'Frozen protocol changed; stop'
    protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
    outputs = [HERE/'detuning_values.json', HERE/'eight_harmonic_rows.csv', HERE/'run_record.json']
    assert not any(path.exists() for path in outputs), 'Refuse to overwrite a frozen run'
    helper = (HERE/protocol['existing_helper']).resolve()
    assert sha(helper) == protocol['expected_helper_sha256']
    source_paths = [protocol_path, helper,
                    TOPIC/'experiments/round010_unit_topcut_envelopes/unit_topcut_envelope_result.json',
                    TOPIC/'manuscript/working-draft-v009.md',
                    TOPIC/'research/roles/experiments/questions.md',
                    TOPIC/'research/roles/experiments/next-task.md']
    source_hashes = {str(path): sha(path) for path in source_paths}
    names = {'spectrum', 'add', 'sub', 'mul', 'div', 'magnitude', 'harmonic', 'stringify'}
    parsed = ast.parse(helper.read_text(encoding='utf-8'), filename=str(helper))
    functions = [node for node in parsed.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in functions} == names
    scope = {'D': D, 'localcontext': localcontext, 'PREC': protocol['working_precision_digits']}
    # Compiling these named functions runs no helper main and creates no pycache.
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(helper), 'exec'), scope)
    spectrum, harmonic, divide, magnitude, subtract, stringify = (
        scope[name] for name in ['spectrum', 'harmonic', 'div', 'magnitude', 'sub', 'stringify'])
    rows, details = [], []
    with localcontext() as ctx:
        ctx.prec = protocol['working_precision_digits']
        model = spectrum(D(1), ctx.prec)
        kappa, zeta_star = D(protocol['kappa']), model['zeta_crit']
        for text_r in protocol['r_values']:
            r = D(text_r)
            assert r != 1
            zeta0, zeta1 = r*zeta_star, kappa*r*zeta_star
            states = [harmonic(model, zeta, ctx.prec) for zeta in [zeta0, zeta1]]
            physical_Q = divide(states[1]['physical_H'], states[0]['physical_H'])
            modal_Q = divide(states[1]['modal_H'], states[0]['modal_H'])
            abs_Q = magnitude(physical_Q)
            difference = magnitude(subtract(physical_Q, modal_Q))
            row = {'r': r, 'abs_r_minus_1': abs(r-1), 'zeta0': zeta0, 'zeta1': zeta1,
                   'H0_abs': states[0]['physical_H_abs'], 'H1_abs': states[1]['physical_H_abs'],
                   'physical_Q_real': physical_Q[0], 'physical_Q_imag': physical_Q[1],
                   'abs_Q': abs_Q, 'abs_r_minus_1_times_abs_Q': abs(r-1)*abs_Q,
                   'modal_Q_real': modal_Q[0], 'modal_Q_imag': modal_Q[1],
                   'Q_absolute_route_difference': difference, 'Q_relative_route_difference': difference/abs_Q,
                   'physical_equation_max_absolute_residual': max(state['physical_equation_absolute_residual'] for state in states)}
            rows.append(row)
            details.append({'r': r, 'states': [{key: value for key, value in state.items() if key != 'C'} for state in states]})
        checks = {
            'exactly_eight_prespecified_r_values': [str(row['r']) for row in rows] == protocol['r_values'],
            'working_precision_at_least_60': ctx.prec >= 60,
            'fixed_complete_unit_spectrum_positive': all(value > 0 for value in model['lam']),
            'fixed_topcut_projection_moments': abs(sum(model['rho'])) < D('1e-70') and abs(sum(lam*rho for lam,rho in zip(model['lam'], model['rho']))) < D('1e-70'),
            'eigen_equation_residual_below_1e_70': model['eigen_residual'] < D('1e-70'),
            'all_positive_detuned_H0_H1': all(row['H0_abs'] > 0 and row['H1_abs'] > 0 for row in rows),
            'Q_relative_routes_below_1e_60': max(row['Q_relative_route_difference'] for row in rows) < D('1e-60'),
            'physical_equation_residual_below_1e_70': max(row['physical_equation_max_absolute_residual'] for row in rows) < D('1e-70'),
            'all_recorded_sources_unchanged': all(sha(path) == source_hashes[str(path)] for path in source_paths),
            'runtime_below_300_seconds': time.perf_counter()-started < 300,
        }
        result = {'evidence_id': protocol['evidence_id'], 'session': protocol['session'],
                  'review_status': 'candidate', 'evidence_type': 'numerical-test',
                  'finished_utc': datetime.now(timezone.utc).isoformat(),
                  'elapsed_seconds': time.perf_counter()-started,
                  'protocol_sha256': EXPECTED_PROTOCOL, 'code_sha256': sha(__file__),
                  'working_precision_digits': ctx.prec, 'arithmetic': 'stdlib Decimal ROUND_HALF_EVEN; no directed-interval claim',
                  'fixed_model': model, 'kappa': kappa,
                  'input_convention': 'f=-a; H=ell^T(K-Omega^2 I+i Omega C)^(-1)b; Q=H1/H0',
                  'frequency': 'Omega=S for every one of the eight points',
                  'helper_reuse': 'Only eight named function ASTs; no helper main, bisection or import/pycache execution',
                  'rows': rows, 'harmonic_details': details, 'checks': checks,
                  'limits': protocol['evidence_boundary']}
        outputs[0].write_text(json.dumps(stringify(result), ensure_ascii=False, indent=2), encoding='utf-8')
        with outputs[1].open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(stringify(rows))
    passed = all(checks.values())
    record = {'evidence_id': protocol['evidence_id'], 'review_status': 'candidate',
              'finished_utc': result['finished_utc'], 'elapsed_seconds': result['elapsed_seconds'],
              'command_argv': [sys.executable, str(Path(__file__).resolve())], 'cwd': str(Path.cwd()),
              'python': platform.python_version(), 'dependencies': 'Python standard library only',
              'exit_code_after_checks': 0 if passed else 1, 'checks': checks,
              'protocol_frozen_before_execution': True,
              'protocol_file_last_write_utc': datetime.fromtimestamp(protocol_path.stat().st_mtime, timezone.utc).isoformat(),
              'sources': [{'file': str(path), 'sha256': source_hashes[str(path)]} for path in source_paths],
              'files': [{'file': path.name, 'bytes': path.stat().st_size, 'sha256': sha(path)}
                        for path in [Path(__file__), outputs[0], outputs[1]]],
              'no_time_response_no_fit_no_extra_grid': True}
    outputs[2].write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(stringify({'rows': [{'r': row['r'], 'abs_Q': row['abs_Q'],
          'scaled_abs_Q': row['abs_r_minus_1_times_abs_Q']} for row in rows],
          'max_relative_Q_route_difference': max(row['Q_relative_route_difference'] for row in rows),
          'checks': checks, 'elapsed_seconds': result['elapsed_seconds']}), ensure_ascii=False, indent=2))
    assert passed


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
