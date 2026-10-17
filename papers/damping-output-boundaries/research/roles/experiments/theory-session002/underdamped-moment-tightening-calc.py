"""Arithmetic comparison of two valid moment bounds; no response/spectrum/r evaluation."""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal as D, localcontext
import hashlib
import json
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
TOPIC = HERE.parents[3]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stringify(value):
    if isinstance(value, D):
        return str(value)
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stringify(item) for item in value]
    return value


def main():
    start = time.perf_counter()
    sources = [TOPIC/'experiments/theory-round001-detuning/detuning_values.json',
        TOPIC/'experiments/theory-round003-envelope-constants/envelope_constants.json',
        TOPIC/'research/roles/ideation/theory-session002/finite-envelope-detuning-candidate.md']
    expected = ['7df5437996e7cf9a2f42d4dfc244ed481c96051236d1453861b03ae8ffeb9907',
        '4da924405d0766f6108d53d67e42caa692b98230ea59516b1b94fc9f1ae7ac9b',
        'ea99a02b167720490242edc396adc6da154dd617a55dfc8df26c28c2daf3b3db']
    assert all(sha(path) == digest for path,digest in zip(sources, expected))
    output = HERE/'underdamped-moment-tightening-values.json'
    assert not output.exists(), 'Refuse to overwrite frozen arithmetic output'
    model = json.loads(sources[0].read_text(encoding='utf-8'))['fixed_model']
    frozen = json.loads(sources[1].read_text(encoding='utf-8'))
    assert frozen['reused_original_values']['rho'] == model['rho']
    assert frozen['reused_original_values']['omega'] == model['omega']
    with localcontext() as ctx:
        ctx.prec = 90
        old = {key: D(value) for key,value in frozen['constants'].items()}
        zminus, zplus = old['zeta_minus'], old['zeta_plus']
        assert 0 < zminus <= zplus < 1
        assert old['gamma'] == zminus
        modal_sum = sum(abs(D(r))/D(w)**3 for r,w in zip(model['rho'], model['omega']))
        root = (1-zplus*zplus).sqrt()
        alternative = modal_sum/(zminus*zminus*root)
        ratio = alternative/old['M']
        direct_ratio = zminus/(2*root)
        best = min(old['M'], alternative)
        E_alt = old['pi']*alternative/2
        values = {'zeta_minus': zminus, 'zeta_plus': zplus,
            'sqrt_1_minus_zeta_plus_squared': root,
            'frozen_modal_absolute_sum': modal_sum,
            'M_old': old['M'], 'M_alt': alternative, 'M_best_min': best,
            'new_over_old_factor': ratio, 'old_over_new_improvement_factor': 1/ratio,
            'remaining_percent': 100*ratio,
            'ratio_from_cancelled_formula': direct_ratio,
            'E_old': old['E'], 'E_alt': E_alt,
            'T0_old_half_s': old['T0'], 'T0_alt_half_s': 2*E_alt/old['B'],
            'Tenv_old_s': old['Tenv'], 'Tenv_alt_s': E_alt/old['A'],
            'T0_alt_half_days': (2*E_alt/old['B'])/86400,
            'Tenv_alt_days': (E_alt/old['A'])/86400,
            'A_unchanged': old['A'], 'B_unchanged': old['B'], 'C_unchanged': old['C']}
        checks = {'strict_underdamped_compact_interval': 0 < zminus <= zplus < 1,
            'same_original_omega_rho': True,
            'unit_old_gamma_equals_zeta_minus': old['gamma'] == zminus,
            'alternative_positive_and_smaller_here': 0 < alternative < old['M'],
            'direct_ratio_formula_matches_below_1e_80': abs(ratio-direct_ratio) < D('1e-80'),
            'E_T0_Tenv_scale_by_same_factor': all(abs(new/old_value-ratio) < D('1e-80') for new,old_value in
                [(E_alt,old['E']), (values['T0_alt_half_s'],old['T0']), (values['Tenv_alt_s'],old['Tenv'])]),
            'sources_unchanged': all(sha(path) == digest for path,digest in zip(sources, expected)),
            'elapsed_under_300_seconds': time.perf_counter()-start < 300}
    result = {'evidence_id': 'E-EXP-T002-004', 'review_status': 'candidate',
        'evidence_type': 'analytic-derivation / arithmetic-check',
        'finished_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.perf_counter()-start,
        'code_sha256': sha(__file__), 'command_argv': [sys.executable,str(Path(__file__).resolve())],
        'python': platform.python_version(), 'dependencies': 'standard library only',
        'precision_digits': 90, 'arithmetic': 'Decimal ROUND_HALF_EVEN; not directed interval certification',
        'sources': [{'file': str(path), 'sha256': digest} for path,digest in zip(sources,expected)],
        'values': values, 'checks': checks, 'exit_code_after_checks': 0 if all(checks.values()) else 1,
        'limits': 'M_alt requires the whole common damping interval to satisfy 0<zeta_minus<=zeta_plus<1. Both valid upper bounds can be minimized; M_alt need not be better in every underdamped interval. No new response, spectrum, root, r, delta table, plot or fit. These are conservative sufficient-condition improvements, not necessary duration or measured peaks.'}
    output.write_text(json.dumps(stringify(result),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(stringify({'values': values, 'checks': checks, 'elapsed_seconds':result['elapsed_seconds']}),ensure_ascii=False,indent=2))
    assert all(checks.values())


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
