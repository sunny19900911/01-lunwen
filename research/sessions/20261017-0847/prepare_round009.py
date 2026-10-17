"""Explicit frozen-file publication check; never stages raw or active role files."""
from pathlib import Path
import ast
from decimal import Decimal, localcontext
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
SESSION = ROOT / 'research/sessions/20261017-0847'
PREFIX = 'papers/damping-output-boundaries/'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    files = []
    checked = []
    for n in (8, 9):
        manifest = PREFIX + f'research/roles/writing/frozen-round{n:03}.json'
        obj = json.loads((ROOT / manifest).read_text(encoding='utf-8'))
        for item in obj['frozen_files'] + [obj['predecessor']]:
            p = ROOT / item['path']
            assert sha(p) == item['sha256'], item['path']
            if 'bytes' in item:
                assert p.stat().st_size == item['bytes']
            checked.append(item['path'])
        files.extend(x['path'] for x in obj['frozen_files'])
        files.append(manifest)
    for item in json.loads((ROOT / (PREFIX + 'manuscript/figure-map-v009.json')).read_text(encoding='utf-8'))['selected_figures']:
        for source in item['sources']:
            assert sha(ROOT / source['path']) == source['sha256']
            checked.append(source['path'])
    code = PREFIX + 'experiments/round012_low_damping_bisection.py'
    data = PREFIX + 'experiments/round012_low_damping_bisection/low_damping_bisection.json'
    obj = json.loads((ROOT / data).read_text(encoding='utf-8'))
    assert sha(ROOT / code) == obj['code_sha256']
    assert len(obj['bisection_trace']) == 80 and all(obj['checks'].values())
    with localcontext() as ctx:
        ctx.prec = 120
        fin = obj['final_numerical_bracket']
        assert Decimal(fin['hi']) - Decimal(fin['lo']) == Decimal(19999) / Decimal(2)**80
    for source in obj['sources']:
        assert sha(Path(source['file'])) == source['sha256'], source['file']
    files.extend([code, data, PREFIX + 'experiments/round012_low_damping_bisection/run_record.json'])
    files.extend(PREFIX + p for p in [
        'research/claims.md', 'research/decisions-pending.md',
        'research/topic-cards/T001.md', 'research/topic-cards/events.md',
        'research/topic-cards/history/T001/v009.md',
        'research/roles/verification/network-realizability-proof.md',
        'research/roles/verification/manuscript-review-v008.md',
        'research/roles/literature/contribution-audit-v008.md',
        'research/roles/ideation/topic-options-final-candidate.md',
        'research/roles/experiments/round-012-low-damping-bisection.md'])
    files.extend('research/sessions/20261017-0847/' + p for p in ['R009.md', 'status.json', 'prepare_round009.py'])
    files = sorted(set(files))
    for rel in files:
        p = ROOT / rel
        assert p.is_file() and p.stat().st_size < 1_000_000, rel
        if p.suffix == '.json':
            json.loads(p.read_text(encoding='utf-8'))
        elif p.suffix == '.py':
            ast.parse(p.read_text(encoding='utf-8'))
    report = {'round': 'R009', 'frozen_source_hash_checks': checked,
              'E012_code_and_sources_match': True, 'E012_checks': len(obj['checks']),
              'E012_actual_record_reviewed_not_rerun': True,
              'E012_trace_and_exact_decimal_width_checked': True,
              'scope': 'JSON/AST/hash/byte checks, not formal mathematical or directed interval certification',
              'files': [{'path': p, 'bytes': (ROOT/p).stat().st_size, 'sha256': sha(ROOT/p)} for p in files]}
    validation = 'research/sessions/20261017-0847/ready-round009-validation.json'
    listing = 'research/sessions/20261017-0847/ready-round009-files.json'
    (ROOT/validation).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    files += [validation, listing]
    (ROOT/listing).write_text(json.dumps(files, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT).strip(), 'Existing index: inspect first'
    subprocess.run(['git', 'add', '--', *files], cwd=ROOT, check=True)
    for rel in files:
        assert subprocess.check_output(['git', 'show', ':'+rel], cwd=ROOT) == (ROOT/rel).read_bytes(), rel
    subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, check=True)
    print(json.dumps({'staged_explicit_files': len(files), 'hashes_and_bytes': 'passed', 'excluded': ['5E-07', 'finite_input_witness.npz', 'raw exports', 'fulltext cache', 'active final reviews']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
