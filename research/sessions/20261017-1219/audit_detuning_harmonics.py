"""Check frozen eight-point physical Q via the independently organized cubic identity."""
from pathlib import Path
from decimal import Decimal as D, localcontext
from datetime import datetime, timezone, timedelta
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'papers/damping-output-boundaries/experiments/theory-round001-detuning/detuning_values.json'
EXPECTED = '7df5437996e7cf9a2f42d4dfc244ed481c96051236d1453861b03ae8ffeb9907'


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def div(a, b):
    norm = b[0]*b[0]+b[1]*b[1]
    return (a[0]*b[0]+a[1]*b[1])/norm, (a[1]*b[0]-a[0]*b[1])/norm


def main():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    data = json.loads(SOURCE.read_text(encoding='utf-8'))
    with localcontext() as ctx:
        ctx.prec = 90
        model = data['fixed_model']
        omega = [D(x) for x in model['omega']]
        S, star, kappa = D(model['S']), D(model['zeta_crit']), D(data['kappa'])
        assert len(data['rows']) == 8
        residuals = []
        for row in data['rows']:
            r = D(row['r'])
            # At iS the exact cubic numerator is c(1-r^2); c cancels.
            Q = ((1-kappa*kappa*r*r)/(1-r*r), D(0))
            for w in omega:
                real = w*w-S*S
                Q = mul(Q, div((real, 2*r*star*w*S), (real, 2*kappa*r*star*w*S)))
            reported = D(row['physical_Q_real']), D(row['physical_Q_imag'])
            err = max(abs(Q[j]-reported[j]) for j in (0, 1))
            rel = err/max(abs(reported[0]), abs(reported[1]))
            assert rel < D('1e-70')
            residuals.append({'r': str(r), 'max_relative_component_error': str(rel)})
    out = {'checked_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
           'source_sha256': EXPECTED, 'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'method': 'cubic numerator identity times three mechanical denominator ratios; no eigensolve, dynamic stiffness solve, time response or added parameter points',
           'rows': residuals, 'all_passed': True,
           'scope': 'independent algebra organization using frozen spectrum; numerical review, not directed interval or continuous-peak certification'}
    target = Path(__file__).with_name('detuning-harmonic-independent-audit.json')
    assert not target.exists(), 'Preserve frozen audit'
    target.write_bytes((json.dumps(out, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'eight_rows_passed': True, 'max_relative_component_error': max(float(x['max_relative_component_error']) for x in residuals)}))


if __name__ == '__main__':
    main()
