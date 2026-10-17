"""Reproducible figures from frozen light summaries; no new physical inference."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from reportlab.graphics import renderSVG
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[4])
parser.add_argument('--out', type=Path, required=True, help='A new output directory; existing outputs are refused')
args = parser.parse_args()
OUT = args.out.resolve()
OUT.mkdir(parents=True, exist_ok=False)
REPO = args.repo.resolve()
ENERGY = REPO / 'research/sessions/20261017-2109/R001-energy-audit/energy_summary.csv'
COVERAGE = REPO / 'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/link_case_coverage_r001.csv'
CASES = ['RH4X', 'RH4Y', 'SHW4X', 'SHW4Y', 'SHW7X', 'SHW7Y']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    with path.open(encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (OUT / name).open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def canvas(w, h, title, subtitle):
    d = Drawing(w, h)
    d.add(Rect(0, 0, w, h, fillColor=colors.white, strokeColor=None))
    d.add(String(50, h - 32, title, fontName='Helvetica-Bold', fontSize=17))
    d.add(String(50, h - 53, subtitle, fontName='Helvetica', fontSize=10,
                 fillColor=colors.HexColor('#455869')))
    return d


def main():
    inputs = {str(p): sha(p) for p in [ENERGY, COVERAGE]}
    energy = read(ENERGY)
    coverage = read(COVERAGE)
    by = {r['case']: r for r in energy}
    assert set(by) == set(CASES) and len(energy) == 6
    for r in energy:
        assert abs(float(r['ratio_Elink_over_Eglobal']) -
                   float(r['Elink_increment_kNm']) / float(r['Eglobal_increment_kNm'])) < 1e-14
    d = canvas(850, 440, 'Native Maxwell energy partition',
               'Ratio of Link Damper Energy to Global Damping Energy over each exported record')
    chart = VerticalBarChart()
    chart.x, chart.y, chart.width, chart.height = 88, 108, 650, 238
    chart.data = [[float(by[event + direction]['ratio_Elink_over_Eglobal'])
                   for event in ['RH4', 'SHW4', 'SHW7']] for direction in ['X', 'Y']]
    chart.categoryAxis.categoryNames = ['RH4', 'SHW4', 'SHW7']
    chart.categoryAxis.labels.fontSize = 11
    chart.valueAxis.valueMin, chart.valueAxis.valueMax, chart.valueAxis.valueStep = 0, 1.6, .4
    chart.valueAxis.labels.fontSize = 10
    chart.valueAxis.visibleGrid = True
    chart.valueAxis.gridStrokeColor = colors.HexColor('#dce3e8')
    chart.groupSpacing, chart.barSpacing = 28, 12
    chart.bars[0].fillColor = colors.HexColor('#375e7a')
    chart.bars[1].fillColor = colors.HexColor('#bc6b42')
    chart.bars.strokeColor = None
    chart.barLabelFormat = '%.3f'
    chart.barLabels.fontSize, chart.barLabels.nudge = 10, 7
    d.add(chart)
    d.add(String(50, 361, 'E_link / E_global', fontSize=11))
    for x, label, col in [(110, 'X input', '#375e7a'), (250, 'Y input', '#bc6b42')]:
        d.add(Rect(x, 62, 12, 11, fillColor=colors.HexColor(col), strokeColor=None))
        d.add(String(x + 20, 63, label, fontSize=10))
    d.add(String(50, 39, 'Windows: RH4 0-50 s; SHW4 0-59 s; SHW7 0-53.9 s. Three records, two input directions each.', fontSize=9))
    d.add(String(50, 22, 'Energy ratio is dimensionless. No background damping value or individual modal damping is assumed.', fontSize=9))
    renderSVG.drawToFile(d, str(OUT / '01_native_energy_ratio.svg'))
    write('plot_energy_ratios.csv', [{key: r[key] for key in
          ['case', 'T_s', 'Eglobal_increment_kNm', 'Elink_increment_kNm',
           'ratio_Elink_over_Eglobal', 'source_row_final']} for r in energy])

    assert len(coverage) == 528 and len({(r['Link'], r['Case']) for r in coverage}) == 528
    links = defaultdict(set)
    for r in coverage:
        links[r['Story']].add(r['Link'])
    assert len(links) == 11 and all(len(v) == 8 for v in links.values())
    complete = Counter((r['Story'], r['Case']) for r in coverage if r['complete_export_grid'] == 'True')
    partial = Counter((r['Story'], r['Case']) for r in coverage
                      if r['complete_export_grid'] != 'True' and int(r['common_n']) > 0)
    assert sum(complete.values()) == 193 and sum(partial.values()) == 1
    d = canvas(1000, 560, 'Coverage of paired device force and deformation',
               'Complete P-I / P-J / U1 export grids per story and case, out of 8 devices')
    cells = []
    for story in range(1, 12):
        y = 102 + (story - 1) * 32
        d.add(String(58, y + 10, f'Story {story}', fontSize=10))
        for i, case in enumerate(CASES):
            count = complete[(f'Story{story}', case)]
            part = partial[(f'Story{story}', case)]
            x = 133 + i * 94
            color = '#375e7a' if count == 8 else '#c2d5df' if count else '#edf1f4'
            d.add(Rect(x, y, 91, 29, fillColor=colors.HexColor(color), strokeColor=None))
            d.add(String(x + 31, y + 10, f'{count}/8' + ('*' if part else ''), fontSize=10,
                         fillColor=colors.white if count == 8 else colors.HexColor('#223646')))
            cells.append({'Story': f'Story{story}', 'Case': case, 'complete': count,
                          'partial': part, 'no_common_data': 8 - count - part, 'devices_at_story': 8})
    for i, case in enumerate(CASES):
        d.add(String(146 + i * 94, 81, case, fontSize=10))
    for y, text in [(412, '193 / 528 complete'), (389, '1 / 528 partial'),
                    (366, '334 / 528 no common data'), (310, 'Complete upper-story subsets'),
                    (291, 'do not represent all 88 devices.'), (252, 'Missing is not zero force.'),
                    (218, 'I and J are checked separately;'), (199, 'they are not summed twice.')]:
        d.add(String(733, y, text, fontSize=10, fillColor=colors.HexColor('#334b5c')))
    d.add(String(50, 47, '* Story 7 / RH4Y includes one partial device record, excluded from complete counts.', fontSize=9))
    d.add(String(50, 28, 'Coverage refers to available output samples, not integration convergence, constitutive correctness or seismic performance.', fontSize=9))
    renderSVG.drawToFile(d, str(OUT / '02_device_coverage_by_story.svg'))
    write('plot_link_coverage_by_story.csv', cells)
    assert inputs == {str(p): sha(p) for p in [ENERGY, COVERAGE]}
    result = {'inputs': inputs, 'script_sha256': sha(Path(__file__)),
              'checks': {'six_ratios_recomputed': True, '528_unique_device_cases': True,
                         '88_devices_eight_per_story': True, '193_complete_one_partial': True,
                         'input_hashes_unchanged': True},
              'svg': {p.name: sha(p) for p in OUT.glob('*.svg')},
              'scope': 'Native energy ratio and output coverage only; no damping calibration, new fit, '
                       'response-reduction claim or novelty inference.'}
    (OUT / 'figure_data_validation.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
