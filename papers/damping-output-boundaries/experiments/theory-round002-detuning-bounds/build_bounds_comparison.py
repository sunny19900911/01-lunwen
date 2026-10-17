"""Fraction constants and one figure from eight frozen harmonic rows; no responses."""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction as F
from decimal import Decimal, localcontext
import csv
import hashlib
import json
import sys
import time
import numpy as np

EXTRA = Path.home()/'.codex/tmp/mechanism20261013-pydeps'
if EXTRA.exists():
    sys.path.append(str(EXTRA))
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

HERE = Path(__file__).resolve().parent
TOPIC = HERE.parents[1]
SRC = HERE.parent/'theory-round001-detuning/eight_harmonic_rows.csv'
BASE = 'fig_detuning_theory_bounds_and_harmonic_witnesses'
BLUE, ORANGE, GRAY = '#235789', '#c75b28', '#66717d'
plt.rcParams.update({'font.family': 'Arial', 'font.size': 10,
    'axes.spines.top': False, 'axes.spines.right': False, 'axes.linewidth': .7,
    'grid.color': '#dbe0e5', 'grid.linewidth': .5, 'svg.fonttype': 'path'})


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decimal_text(value):
    with localcontext() as ctx:
        ctx.prec = 60
        return str(Decimal(value.numerator)/Decimal(value.denominator))


def main():
    started = time.perf_counter()
    assert sha(SRC) == '668662586b10829103c10f1ec2de8e6d1439040aaa5155ccf41204648a1b5ece'
    sources = [SRC, SRC.with_name('detuning_values.json'),
        TOPIC/'research/roles/verification/theory-round001/explicit-detuning-bound-candidate.md',
        TOPIC/'research/roles/verification/theory-session002/explicit-detuning-bound-review.md']
    hashes = {str(path): sha(path) for path in sources}
    with SRC.open(encoding='utf-8', newline='') as stream:
        original = list(csv.DictReader(stream))
    assert [row['r'] for row in original] == ['0.9', '1.1', '0.99', '1.01', '0.999', '1.001', '0.9999', '1.0001']
    kappa = F(8, 5)
    eta = min(F(1, 2), (kappa-1)/(2*kappa))
    c0 = F(36, 7)*(kappa-1)*(1+F(3, 2)*kappa)
    c1 = F(236, 35)*(kappa-1)*(1+F(9, 4)*kappa)
    factor = (3-2/kappa)**3
    lower = (kappa-1)*(kappa+3)/(10*kappa**3)
    upper = factor*((kappa+c0)/2+c1)
    assert (eta, lower, upper) == (F(3, 16), F(69, 1024), F(528563, 4000))
    rows = []
    for row in original:
        delta = abs(F(row['r'])-1)
        assert delta == F(row['abs_r_minus_1']) and 0 < delta <= eta
        rows.append({'r': row['r'], 'delta_exact': str(delta), 'delta_decimal': decimal_text(delta),
            'frozen_harmonic_abs_Q': row['abs_Q'],
            'L_over_delta_exact': str(lower/delta), 'L_over_delta_decimal': decimal_text(lower/delta),
            'U_over_delta_exact': str(upper/delta), 'U_over_delta_decimal': decimal_text(upper/delta)})
    table = HERE/'eight_bound_comparisons.csv'
    with table.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    constants = {name: {'exact': str(value), 'decimal': decimal_text(value)} for name, value in
        [('kappa', kappa), ('eta', eta), ('C0', c0), ('C1', c1), ('A', factor), ('L_kappa', lower), ('U_kappa', upper)]}
    (HERE/'exact_constants.json').write_text(json.dumps(constants, indent=2), encoding='utf-8')

    unique = sorted({abs(F(row['r'])-1) for row in original})
    x = [float(value) for value in unique]
    ylo, yhi = [float(lower/value) for value in unique], [float(upper/value) for value in unique]
    fig, ax = plt.subplots(figsize=(10.2, 6.4))
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.fill_between(x, ylo, yhi, color='#e7edf3', zorder=0)
    ax.plot(x, ylo, '--', lw=1.5, color=BLUE, label=r'$L_\kappa/\delta\ \leq\ K$ (theory)')
    ax.plot(x, yhi, '-', lw=1.5, color=BLUE, label=r'$K\ \leq\ U_\kappa/\delta$ (theory)')
    for below, marker, color, label in [
        (True, 'o', ORANGE, r'$r<1$: frozen $|Q(iS)|\leq K$ witness'),
        (False, '+', BLUE, r'$r>1$: frozen $|Q(iS)|\leq K$ witness')]:
        selected = [row for row in original if (F(row['r']) < 1) == below]
        xx = [float(abs(F(row['r'])-1)) for row in selected]
        yy = [float(row['abs_Q']) for row in selected]
        if marker == 'o':
            ax.scatter(xx, yy, marker=marker, s=80, facecolors='white', edgecolors=color,
                       linewidths=1.5, zorder=4, label=label)
        else:
            ax.scatter(xx, yy, marker=marker, s=65, color=color, linewidths=1.5, zorder=5, label=label)
    ax.set(xlabel=r'Relative detuning $\delta=|r-1|$, $r=\zeta_0/\zeta_*$',
           ylabel='Bound / harmonic-witness value (K is not measured)',
           xlim=(7e-5, .14), ylim=(.3, 2.5e6))
    ax.set_xticks(x, labels=[r'$10^{-4}$', r'$10^{-3}$', r'$10^{-2}$', r'$10^{-1}$'])
    ax.minorticks_off()
    ax.grid(which='major')
    ax.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='none', fontsize=9)
    ax.text(.035, .075, 'Harmonic markers are lower-bound witnesses for K.\nNo time-response K values were computed.',
            transform=ax.transAxes, fontsize=9, color=GRAY, linespacing=1.5)
    fig.suptitle('C020 | Complete-peak bounds and harmonic witnesses', fontsize=14, y=.98)
    fig.text(.53, .925, r'$\kappa=8/5,\quad\eta_\kappa=3/16,\quad L_\kappa=69/1024,\quad U_\kappa=528563/4000$',
             ha='center', fontsize=11)
    fig.text(.07, .18, r'Shaded band: conservative theoretical bounds for K, valid for $0<\delta\leq3/16$; no optimality is claimed.',
             fontsize=8.8, color=GRAY)
    fig.text(.07, .137, 'K is the supremum of complete peak ratios over common real finite-support C1 inputs, with zero initial state.',
             fontsize=8.8, color=GRAY)
    fig.text(.07, .094, r'Markers: the frozen unit topcut at $\Omega=S$, $\zeta_*=0.2606565$; no new response, r point, or fit.',
             fontsize=8.8, color=GRAY)
    fig.text(.07, .051, 'The plot illustrates reviewed theory; it does not prove the theorem or identify K with the harmonic ratio.',
             fontsize=8.8, color=GRAY)
    fig.subplots_adjust(left=.105, right=.98, bottom=.29, top=.86)
    outputs = [HERE/(BASE+'.png'), HERE/(BASE+'.svg')]
    fig.savefig(outputs[0], dpi=300, bbox_inches='tight', pad_inches=.12)
    fig.savefig(outputs[1], bbox_inches='tight', pad_inches=.12)
    plt.close(fig)
    assert all(sha(path) == hashes[str(path)] for path in sources)
    outputs += [table, HERE/'exact_constants.json']
    manifest = {'evidence_id': 'E-EXP-T002-002', 'review_status': 'candidate',
        'finished_utc': datetime.now(timezone.utc).isoformat(), 'elapsed_seconds': time.perf_counter()-started,
        'script_sha256': sha(__file__), 'exact_constants': constants,
        'sources': [{'path': str(path), 'sha256': hashes[str(path)]} for path in sources],
        'outputs': [{'file': path.name, 'bytes': path.stat().st_size, 'sha256': sha(path)} for path in outputs],
        'checks': {'exact_rational_constants': True, 'eight_original_rows_only': len(rows) == 8,
                   'all_deltas_in_eta_domain': True, 'sources_unchanged': True,
                   'no_new_response_no_new_r_no_fit': True},
        'K_values_computed': False, 'bounds_scope': 'Reviewed C020 Cc1 definition; no new L1-class bridge claim',
        'plot_data': '4 unique original delta coordinates, exact theory values; 8 original harmonic markers',
        'python': sys.version, 'numpy': np.__version__, 'matplotlib': matplotlib.__version__,
        'svg_bytes': 'Native generated bytes retained, including generator trailing whitespace.'}
    (HERE/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'constants': constants, 'rows': len(rows), 'elapsed_seconds': manifest['elapsed_seconds']}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
