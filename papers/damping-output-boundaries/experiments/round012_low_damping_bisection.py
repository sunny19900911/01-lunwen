"""One prescribed sign-bracket bisection; Decimal spectra and physical H checks only."""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal as D, localcontext
import hashlib
import json
import platform
import sys
import time

HERE = Path(__file__).resolve().parent
OUT = HERE / 'round012_low_damping_bisection'
TOPIC = HERE.parent
PREC = 90
STEPS = 80


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def spectrum(L, precision=PREC):
    with localcontext() as ctx:
        ctx.prec = precision
        zero, one = D(0), D(1)
        K = [[D(2), -one, zero], [-one, one+L, -L], [zero, -L, L]]
        A = [row[:] for row in K]
        Q = [[one if i == j else zero for j in range(3)] for i in range(3)]
        tolerance = D(10) ** (-precision+15)
        for iteration in range(200):
            p, q = max(((i, j) for i in range(3) for j in range(i+1, 3)),
                       key=lambda ij: abs(A[ij[0]][ij[1]]))
            if abs(A[p][q]) < tolerance:
                break
            tau = (A[q][q]-A[p][p])/(2*A[p][q])
            tangent = (one if tau >= 0 else -one)/(abs(tau)+(one+tau*tau).sqrt())
            cosine = one/(one+tangent*tangent).sqrt()
            sine = tangent*cosine
            apq = A[p][q]
            A[p][p] -= tangent*apq
            A[q][q] += tangent*apq
            A[p][q] = A[q][p] = zero
            for i in range(3):
                if i not in [p, q]:
                    x, y = A[i][p], A[i][q]
                    A[i][p] = A[p][i] = cosine*x-sine*y
                    A[i][q] = A[q][i] = sine*x+cosine*y
                x, y = Q[i][p], Q[i][q]
                Q[i][p], Q[i][q] = cosine*x-sine*y, sine*x+cosine*y
        else:
            raise ArithmeticError('Jacobi did not converge; stop without extending models')
        order = sorted(range(3), key=lambda j: A[j][j])
        lam = [A[j][j] for j in order]
        assert all(x > 0 for x in lam)
        phi = [[Q[i][j] for j in order] for i in range(3)]
        gamma = [sum(phi[i][j] for i in range(3)) for j in range(3)]
        for j in range(3):
            if gamma[j] < 0:
                gamma[j] = -gamma[j]
                for i in range(3):
                    phi[i][j] = -phi[i][j]
        omega = [x.sqrt() for x in lam]
        S = sum(omega)
        pair_product = (omega[0]+omega[1])*(omega[0]+omega[2])*(omega[1]+omega[2])
        qvalue = pair_product/(4*S**3)
        rho = [L*(phi[2][j]-phi[1][j])*gamma[j] for j in range(3)]
        eigen_residual = max(abs(sum(K[i][k]*phi[k][j] for k in range(3))-lam[j]*phi[i][j])
                             for i in range(3) for j in range(3))
        orthogonal_residual = max(abs(sum(phi[k][i]*phi[k][j] for k in range(3))-(one if i == j else zero))
                                  for i in range(3) for j in range(3))
        return {'L': L, 'K': K, 'lam': lam, 'phi': phi, 'Gamma': gamma, 'omega': omega,
                'S': S, 'D': pair_product, 'q': qvalue, 'zeta_crit': qvalue.sqrt(), 'rho': rho,
                'jacobi_rotations': iteration, 'remaining_offdiag': max(abs(A[i][j]) for i in range(3) for j in range(3) if i != j),
                'eigen_residual': eigen_residual, 'orthogonal_residual': orthogonal_residual}


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def sub(a, b):
    return a[0]-b[0], a[1]-b[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def div(a, b):
    den = b[0]**2+b[1]**2
    return (a[0]*b[0]+a[1]*b[1])/den, (a[1]*b[0]-a[0]*b[1])/den


def magnitude(a):
    return (a[0]**2+a[1]**2).sqrt()


def harmonic(model, zeta, precision=PREC):
    with localcontext() as ctx:
        ctx.prec = precision
        zero, one = D(0), D(1)
        phi, omega, K, S, L = (model[key] for key in ['phi', 'omega', 'K', 'S', 'L'])
        C = [[sum(phi[i][j]*2*zeta*omega[j]*phi[k][j] for j in range(3))
              for k in range(3)] for i in range(3)]
        matrix = [[(K[i][j]-(S*S if i == j else zero), S*C[i][j]) for j in range(3)] for i in range(3)]
        original = [row[:] for row in matrix]
        rhs = [(one, zero)]*3  # f=-a, so the physical RHS is +b f.
        for p in range(3):
            pivot = max(range(p, 3), key=lambda i: magnitude(matrix[i][p]))
            matrix[p], matrix[pivot] = matrix[pivot], matrix[p]
            rhs[p], rhs[pivot] = rhs[pivot], rhs[p]
            for i in range(p+1, 3):
                factor = div(matrix[i][p], matrix[p][p])
                for j in range(p, 3):
                    matrix[i][j] = sub(matrix[i][j], mul(factor, matrix[p][j]))
                rhs[i] = sub(rhs[i], mul(factor, rhs[p]))
        u = [(zero, zero)]*3
        for i in range(2, -1, -1):
            remainder = rhs[i]
            for j in range(i+1, 3):
                remainder = sub(remainder, mul(matrix[i][j], u[j]))
            u[i] = div(remainder, matrix[i][i])
        physical_H = mul((L, zero), sub(u[2], u[1]))
        modal_H = (zero, zero)
        for lam, w, rho in zip(model['lam'], omega, model['rho']):
            modal_H = add(modal_H, div((rho, zero), (lam-S*S, 2*zeta*w*S)))
        residual = max(magnitude(sub(add(add(mul(original[i][0], u[0]), mul(original[i][1], u[1])),
                                             mul(original[i][2], u[2])), (one, zero))) for i in range(3))
        return {'zeta': zeta, 'frequency': S, 'C': C, 'physical_H': physical_H,
                'modal_H': modal_H, 'physical_H_abs': magnitude(physical_H),
                'modal_physical_absolute_difference': magnitude(sub(physical_H, modal_H)),
                'physical_equation_absolute_residual': residual}


def stringify(value):
    if isinstance(value, D):
        return str(value)
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [stringify(item) for item in value]
    return value


def main():
    started = time.perf_counter()
    sources = [TOPIC/'research/roles/ideation/round-009.md',
               TOPIC/'research/roles/verification/appendix-V011-low-damping-IVT.md',
               TOPIC/'research/roles/ideation/low-damping-bracket.json',
               HERE/'round002_extended_frequency_check.py']
    source_hashes = {str(p): sha(p) for p in sources}
    with localcontext() as ctx:
        ctx.prec = PREC
        target = D(1)/400
        lo, hi = D(1), D(20000)
        low_model, high_model = spectrum(lo), spectrum(hi)
        flo, fhi = low_model['q']-target, high_model['q']-target
        assert flo > 0 and fhi < 0
        initial = {'lo': lo, 'hi': hi, 'q_lo': low_model['q'], 'q_hi': high_model['q'],
                   'f_lo': flo, 'f_hi': fhi}
        trace = []
        for step in range(1, STEPS+1):
            mid = (lo+hi)/2
            model = spectrum(mid)
            fmid = model['q']-target
            assert fmid != 0, 'Rounded q equality is not an exact root; stop and inspect'
            trace.append({'step': step, 'L_mid': mid, 'q_minus_target': fmid})
            if fmid > 0:
                lo, flo = mid, fmid
            else:
                hi, fhi = mid, fmid
            assert flo > 0 and fhi < 0
        midpoint = (lo+hi)/2
        rounded = spectrum(midpoint)
        physical = [harmonic(rounded, D('.05')), harmonic(rounded, D('.08'))]
        # Higher working precision checks only the already chosen endpoints and midpoint.
        high_lo, high_hi = spectrum(lo, 120), spectrum(hi, 120)
        high_mid = spectrum(midpoint, 120)
        high_H = [harmonic(high_mid, D('.05'), 120), harmonic(high_mid, D('.08'), 120)]
        convergence = {'q_mid_90_vs_120_absolute': abs(rounded['q']-high_mid['q']),
                       'H0_90_vs_120_absolute': magnitude(sub(physical[0]['physical_H'], high_H[0]['physical_H'])),
                       'H1_90_vs_120_absolute': magnitude(sub(physical[1]['physical_H'], high_H[1]['physical_H']))}
        final = {'lo': lo, 'hi': hi, 'width': hi-lo, 'midpoint_L_tilde': midpoint,
                 'q_lo_minus_target': flo, 'q_hi_minus_target': fhi,
                 'q_lo_minus_target_120_digits': high_lo['q']-target,
                 'q_hi_minus_target_120_digits': high_hi['q']-target,
                 'midpoint_q_minus_target': rounded['q']-target}
        checks = {
            'exactly_80_sign_bracket_bisections': len(trace) == 80,
            'initial_signs_opposite': initial['f_lo'] > 0 > initial['f_hi'],
            'final_signs_rechecked_at_120_digits': high_lo['q'] > target > high_hi['q'],
            'width_equals_initial_width_over_2_pow_80': hi-lo == D(19999)/(D(2)**80),
            'small_90_vs_120_q_difference': convergence['q_mid_90_vs_120_absolute'] < D('1e-65'),
            'small_90_vs_120_H_differences': max(convergence['H0_90_vs_120_absolute'], convergence['H1_90_vs_120_absolute']) < D('1e-65'),
            'full_spectrum_residual_small': rounded['eigen_residual'] < D('1e-70'),
            'physical_modal_H_agreement': max(item['modal_physical_absolute_difference'] for item in physical) < D('1e-65'),
            'physical_equation_residual_small': max(item['physical_equation_absolute_residual'] for item in physical) < D('1e-70'),
            'H1_nonzero': physical[1]['physical_H_abs'] > D('1e-10'),
            'sources_unchanged': all(sha(p) == source_hashes[str(p)] for p in sources),
            'runtime_under_360_s': time.perf_counter()-started < 360,
        }
        result = {'evidence_id': 'E-EXP-012', 'finished_utc': datetime.now(timezone.utc).isoformat(),
                  'elapsed_seconds': time.perf_counter()-started, 'code_sha256': sha(__file__),
                  'python': platform.python_version(), 'arithmetic': 'stdlib Decimal, round-half-even, not directed intervals',
                  'working_precision_digits': PREC, 'crosscheck_precision_digits': 120,
                  'bisection_steps': STEPS, 'target_q': target,
                  'sources': [{'file': str(p), 'sha256': source_hashes[str(p)]} for p in sources],
                  'initial_bracket': initial, 'final_numerical_bracket': final,
                  'midpoint_model': rounded, 'same_frequency_harmonic_checks': physical,
                  'precision_crosscheck': convergence, 'bisection_trace': trace, 'checks': checks,
                  'stopping_rule': 'Exactly 80 bisections from [1,20000]; arithmetic precision is not root-location precision. The width is 19999/2^80, about 1.65e-20.',
                  'scope': 'L dagger denotes this sign-preserving branch limit, not proved to equal the minimum-root L star of C017. No monotonicity or uniqueness claimed. L tilde is a finite midpoint approximation; tiny H0 does not prove an exact zero or an unbounded complete-peak ratio for the rounded fixed model. Strict existence and exact-zero conclusions remain C017. No time response, new parameter grid, engineering-unit or local-dashpot claim.'}
    OUT.mkdir(exist_ok=True)
    (OUT/'low_damping_bisection.json').write_text(json.dumps(stringify(result), ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(stringify({'bracket': final, 'omega': rounded['omega'], 'S': rounded['S'],
          'rho': rounded['rho'], 'zeta_crit': rounded['zeta_crit'], 'H': physical,
          'precision_crosscheck': convergence, 'checks': checks, 'elapsed_seconds': result['elapsed_seconds']}), ensure_ascii=False, indent=2))
    assert all(checks.values())


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
