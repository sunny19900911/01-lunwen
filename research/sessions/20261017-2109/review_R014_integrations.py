"""Root read-only identity and independent scalar checks; no cache/ODE execution."""
from pathlib import Path
from fractions import Fraction as F
from math import isqrt
from datetime import datetime
import hashlib
import importlib.util
import json
import re

S = Path(__file__).resolve().parent
R = S.parents[2]
B = R / 'papers/damping-output-boundaries/research/roles'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_records(obj, parent, checked):
    if isinstance(obj, list):
        for value in obj:
            verify_records(value, parent, checked)
    elif isinstance(obj, dict):
        if 'sha256' in obj and any(k in obj for k in ['path', 'file', 'name']):
            name = obj.get('path', obj.get('file', obj.get('name')))
            p = Path(name)
            if not p.is_absolute():
                p = parent / p
            if p.suffix.lower() not in {'.npz', '.xlsx', '.pdf', '.png', '.txt'} and p.is_relative_to(R):
                historical = {
                    'f4f3e4b0ec0d2b3a2bb61683292778fe0a8fe23285e95916e8b090ed74b457d4': ('R017-FNA-reference-force-scope.md', 'recovered-first-report-f4f3e4b0.md'),
                    '0e3de71a6ddf099f39d468d253f5112d4e28aa966edc33f252548397488fcb64': ('validation-R017.json', 'recovered-first-validation-0e3de71a.json'),
                }
                if obj['sha256'] in historical and p.name == historical[obj['sha256']][0] and p.parent.name == 'R017-FNA-reference-force-scope':
                    p = p.parent.parent / 'R017-history-repair' / historical[obj['sha256']][1]
                assert sha(p) == obj['sha256'], p
                if 'bytes' in obj:
                    assert p.stat().st_size == obj['bytes'], p
                checked[str(p.relative_to(R)).replace('\\', '/')] = sha(p)
        for value in obj.values():
            verify_records(value, parent, checked)


def root_interval(q):
    scale = 10 ** 60
    n = isqrt(q.numerator * scale ** 2 // q.denominator)
    a, b = F(n, scale), F(n + 1, scale)
    assert a * a <= q < b * b
    return a, b


def divide_interval(x, den):
    values = [a / b for a in x for b in den]
    return min(values), max(values)


def main():
    checked = {}
    folders = [
        'verification/maxwell-session004/R029-modal-sign-corollary',
        'verification/maxwell-session004/R030-force-target-interface-review',
        'ideation/maxwell-session004/R022-force-target-interface',
        'literature/maxwell-session004/R017-FNA-reference-force-scope',
        'literature/maxwell-session004/R017-history-repair',
        'literature/maxwell-session004/R018-modal-ledger-review',
        'experiments/maxwell-session004/R018-modal-ledger-diagnostic',
        'novelty/maxwell-session004/R015-v010-integration-review',
        'writing/maxwell-session004/layout-input-templates-v001',
    ]
    for folder in folders:
        d = B / folder
        for p in d.iterdir():
            if p.is_file() and p.suffix == '.json':
                verify_records(read(p), d, checked)
    w = B / 'writing/maxwell-session004'
    freeze = read(w / 'frozen-draft-v010.json')
    for item in freeze['files']:
        verify_records(item, w, checked)
    verify_records(read(w / 'draft-v010-input-freeze.json')['sources'], w, checked)
    old = R / 'papers/damping-output-boundaries/manuscript/maxwell-engineering-draft-v009.md'
    new = old.with_name('maxwell-engineering-draft-v010.md')
    a, b = old.read_text(encoding='utf-8'), new.read_text(encoding='utf-8')
    tables = lambda text: re.findall(r'(?m)^\|[^\n]*(?:\n\|[^\n]*)+', text)
    assert len(tables(a)) == 18 and len(tables(b)) == 20
    assert all(table in tables(b) for table in tables(a))
    formula = lambda text: re.findall(r'\$\$.*?\$\$', text, re.S)
    assert len(formula(a)) == 9 and formula(a) == formula(b)
    figures = lambda text: re.findall(r'!\[[^\]]*\]\([^\n)]+\)', text)
    assert len(figures(a)) == 4 and figures(a) == figures(b)
    assert a[a.index('## 参考文献'):] == b[b.index('## 参考文献'):]
    spec = importlib.util.spec_from_file_location('preflight011', S / 'prepare_R011_publish.py')
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    diff = common.check_diff(w / 'draft-v010.diff', old, new)
    d = B / 'verification/maxwell-session004/R029-modal-sign-corollary'
    q = read(d / 'checks.json')
    u1 = F(q['exact_binary64_node']['u1']['fraction'])
    u2 = F(q['exact_binary64_node']['u2']['fraction'])
    radius = F(q['I_J_full_state_error_radius']['fraction'])
    root2, root3 = root_interval(F(2)), root_interval(F(3))
    qp = divide_interval((u1 + u2, u1 + u2), root2)
    qm = divide_interval((u1 - u2, u1 - u2), root2)
    ptrue = (qp[0] - radius, qp[1] + radius)
    mtrue = (qm[0] - radius / root3[0], qm[1] + radius / root3[0])
    u2radius = root_interval(F(2, 3))[1] * radius
    tests = {
        'qplus_strict': ptrue[1] < F('-3.27'),
        'qminus_strict': mtrue[1] < F('-2.75'),
        'u2_strict': abs(u2) + u2radius < F('1.302'),
        'positive_modal_work_lower': F(3, 2) * F(11, 4) ** 2 == F(363, 32),
    }
    for name, interval in [('qplus', ptrue), ('qminus', mtrue)]:
        shown = q['certified_true_intervals_decimal'][name]
        tests[name + '_display_outward'] = F(shown[0]) <= interval[0] <= interval[1] <= F(shown[1])
    assert all(tests.values())
    protected = R / 'papers/damping-output-boundaries/manuscript/theory-draft-v007.md'
    assert sha(protected) == '93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
    assert sha(S / 'R013-addition-certificate-adoption.json') == '836a0d6e8e551dd594770fe1421f49780636cdb2d9d2c8cdbd2fd878cc2b729f'
    result = {
        'at': datetime.now().astimezone().isoformat(), 'checks_passed': True,
        'reviewed': ['v010 integration plus independent R015', 'C027 fixed-J true modal/work corollary R029',
                     'classical R022 interface plus R030 independent review', 'CSI R017 final scope and exact history restoration',
                     'R018 finite modal ledger plus limited static R018 source review', 'two header-only geometry/property templates'],
        'independent_root_method': 'Exact integer-isqrt rational enclosures at 60 decimal scale, using only frozen scalar binary64 fractions; no author script execution.',
        'root_scalar_checks': tests, 'v010_preservation': {'old_tables': 18, 'new_tables': 20, 'formulas': 9, 'figures': 4, 'references_preserved': True},
        'diff': diff, 'checked_small_file_identities': checked,
        'limits': 'Identity checking is not content reproof. Master read the named report/code/diff material; original primary pages visual-audited by role3, not root. No NPZ/Excel/PDF/source-page read or hash in this review. R018 remains a finite floating diagnostic. R019 replay awaits independent implementation review; R023 etc excluded.',
        'frozen_theory_and_R013_authority_unchanged': True,
        'historical_resolution': 'R017 original first-version pointers resolved to exact recovered copies using explicit original-path and expected-SHA mapping; frozen originals untouched.',
    }
    (S / 'R014-root-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'passed': True, 'small_identities': len(checked), 'scalar_checks': tests, 'diff': diff}))


if __name__ == '__main__':
    main()
