"""Plot the six frozen E010 rows; no response calculation, fitting or extrapolation."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import sys
import time
import numpy as np

EXTRA = Path.home() / '.codex/tmp/mechanism20261013-pydeps'
if EXTRA.exists():
    sys.path.append(str(EXTRA))
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.ticker import FixedLocator, ScalarFormatter

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / 'round010_unit_topcut_envelopes'
BASE = 'fig08_physical_topcut_envelope_peaks'
BLUE = '#235789'
RED = '#b43f46'
DARK = '#303d4b'
GRAY = '#66717d'
plt.rcParams.update({
    'font.family': 'Arial', 'font.size': 10, 'axes.titlesize': 11,
    'axes.labelsize': 10, 'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'axes.spines.top': False, 'axes.spines.right': False,
    'axes.linewidth': .7, 'grid.color': '#dbe0e5', 'grid.linewidth': .5,
    'svg.fonttype': 'path',
})


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started = time.perf_counter()
    sources = [SRC / 'six_envelope_sampled_peaks.csv',
               SRC / 'unit_topcut_envelope_result.json', SRC / 'run_record.json']
    before = {str(p): sha(p) for p in sources}
    old_figures = sorted((HERE.parent / 'figures').glob('*.png'))
    old_figures += sorted((HERE.parent / 'figures').glob('*.svg'))
    old_figures += sorted((HERE.parent / 'figures-grouped-diagnostic').glob('*.png'))
    old_figures += sorted((HERE.parent / 'figures-grouped-diagnostic').glob('*.svg'))
    old_hashes = {str(p): sha(p) for p in old_figures}
    with sources[0].open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    result = json.loads(sources[1].read_text(encoding='utf-8'))
    assert len(rows) == 6
    fields = ['T_s', 'sampled_P0', 'sampled_P1', 'sampled_peak_ratio']
    for row, frozen in zip(rows, result['six_sampled_peak_rows']):
        assert all(float(row[key]) == frozen[key] for key in fields)
    values = {key: np.array([float(row[key]) for row in rows]) for key in fields}
    T = values['T_s']
    assert T.tolist() == [20., 40., 80., 160., 320., 640.]

    fig, axes = plt.subplots(1, 2, figsize=(11.8, 6.6))
    left, right = axes
    p0, = left.loglog(T, values['sampled_P0'], 'o-', color=BLUE,
                      lw=1.4, ms=5, label=r'Baseline $P_0$')
    p1, = left.loglog(T, values['sampled_P1'], 's-', color=RED,
                      lw=1.4, ms=5, label=r'Increased damping $P_1$')
    left.set(title='(a) Absolute complete sampled peaks',
             ylabel=r'Peak of $|u_3-u_2|$ (consistent model units)',
             ylim=(1.5e-6, 2.2e-3))
    left.text(.965, .78, r'$P_1 \approx 1.10\times10^{-3}$' + '\nAcross the six shown inputs',
              transform=left.transAxes, ha='right', va='top', color=RED,
              fontsize=9.5, linespacing=1.5)
    left.annotate('Baseline peak decreases',
                  xy=(160, values['sampled_P0'][3]), xytext=(32, 4.6e-6),
                  color=BLUE, fontsize=9.5,
                  arrowprops={'arrowstyle': '-', 'color': BLUE, 'lw': .8})
    right.semilogx(T, values['sampled_peak_ratio'], 'o-', color=DARK,
                   lw=1.4, ms=5)
    right.set(title='(b) Complete sampled peak ratio',
              ylabel=r'$P_1/P_0$', ylim=(0, 510))
    for t, ratio in zip(T, values['sampled_peak_ratio']):
        right.annotate(f'{ratio:.2f}', (t, ratio),
                       xytext=(-7 if t >= 80 else 0, 8),
                       textcoords='offset points',
                       ha='right' if t >= 80 else 'center',
                       fontsize=9, color=DARK)
    right.text(.035, .96, 'Ratio growth reflects a smaller baseline.\nSix points; no fit or extrapolation.',
               transform=right.transAxes, va='top', fontsize=9.5,
               color=GRAY, linespacing=1.5)
    for ax in axes:
        ax.set_xlabel('Envelope half-duration T (s); input support = 2T')
        ax.set_xlim(17, 760)
        ax.xaxis.set_major_locator(FixedLocator(T))
        ax.xaxis.set_major_formatter(ScalarFormatter())
        ax.minorticks_off()
        ax.grid(which='major')

    fig.suptitle('E010 | Physical top-cut peaks under finite input envelopes',
                 fontsize=14, x=.53, y=.98)
    fig.text(.53, .925, 'Fixed unit three-storey model; same bounded input in both states for each T',
             ha='center', fontsize=10.5, color=GRAY)
    fig.text(.53, .882, r'$\zeta_0=0.2606565\ \longrightarrow\ \zeta_1=0.4170504$'
             '   |   zero initial state   |   no input normalization',
             ha='center', fontsize=10)
    fig.legend(handles=[p0, p1], loc='upper center', bbox_to_anchor=(.53, .85),
               ncol=2, frameon=False, fontsize=10, handlelength=2.5, columnspacing=3)
    fig.text(.06, .18, 'Peaks: dt = 0.01 s over the full input + 300 s free tail; all later tails have analytic envelopes.',
             fontsize=9, color=GRAY)
    fig.text(.06, .137, 'T = 640 s: dt = 0.005 s gives the same recorded peaks. Continuous-time extrema are not certified.',
             fontsize=9, color=GRAY)
    fig.text(.06, .094, 'Lines guide the eye only. Six values are numerical illustrations; the analytic argument is separate (I009/V011).',
             fontsize=9, color=GRAY)
    fig.text(.06, .051, 'Consistent unit model, not engineering units; passive network includes 1-3 coupling and three ground connections.',
             fontsize=9, color=GRAY)
    fig.subplots_adjust(left=.075, right=.98, bottom=.29, top=.775, wspace=.24)
    outputs = [HERE / (BASE + '.png'), HERE / (BASE + '.svg')]
    fig.savefig(outputs[0], dpi=300, bbox_inches='tight', pad_inches=.12)
    fig.savefig(outputs[1], bbox_inches='tight', pad_inches=.12)
    plt.close(fig)

    assert all(sha(p) == before[str(p)] for p in sources)
    assert all(sha(p) == old_hashes[str(p)] for p in old_figures)
    manifest = {
        'evidence': 'E-EXP-010 frozen six rows only',
        'finished_utc': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': time.perf_counter() - started,
        'script_sha256': sha(__file__),
        'sources': [{'file': str(p), 'sha256': before[str(p)], 'bytes': p.stat().st_size} for p in sources],
        'outputs': [{'file': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size} for p in outputs],
        'frozen_plot_values': [{key: float(row[key]) for key in fields} for row in rows],
        'numpy': np.__version__, 'matplotlib': matplotlib.__version__,
        'backend': matplotlib.get_backend(), 'font': 'Arial, SVG text as paths',
        'source_hashes_unchanged': True, 'previous_figures_unchanged': old_hashes,
        'new_response_calculation': False, 'fit_or_extrapolation': False,
        'notes': 'All six T values retained. Left log-log, right log-x/linear-y. No kappa reference line. Generated SVG bytes retained without whitespace normalization.',
    }
    (HERE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'figure': BASE, 'elapsed_seconds': manifest['elapsed_seconds'],
                      'rows': len(rows), 'original_figures_unchanged': len(old_hashes)}, ensure_ascii=False))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
