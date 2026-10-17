"""Preflight an explicit frozen R011 whitelist. No index or network mutation."""
from pathlib import Path
from datetime import datetime
import ast
import csv
import hashlib
import json
import re
import subprocess

S = Path(__file__).resolve().parent
R = S.parents[2]
ROLE = R / 'papers/damping-output-boundaries/research/roles'
GIT = 'C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'


def check_item(p, item):
    b = p.read_bytes()
    assert len(b) == item['bytes'], str(p)
    assert hashlib.sha256(b).hexdigest() == item['sha256'], str(p)


def check_diff(p, old, new):
    lines = p.read_text(encoding='utf-8').splitlines()
    a0 = old.read_text(encoding='utf-8').splitlines()
    b0 = new.read_text(encoding='utf-8').splitlines()
    assert lines[0].startswith('--- ') and lines[1].startswith('+++ ')
    i, hunks, spaces = 2, 0, 0
    while i < len(lines):
        m = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', lines[i])
        assert m, lines[i]
        a, b, ca, cb = int(m[1])-1, int(m[3])-1, 0, 0
        i += 1
        hunks += 1
        while i < len(lines) and not lines[i].startswith('@@'):
            line = lines[i]
            assert line and line[0] in ' +-'
            spaces += line == ' '
            if line[0] in ' -':
                assert a0[a] == line[1:]
                a += 1
                ca += 1
            if line[0] in ' +':
                assert b0[b] == line[1:]
                b += 1
                cb += 1
            i += 1
        assert (ca, cb) == (int(m[2] or 1), int(m[4] or 1))
    return {'path': p.relative_to(R).as_posix(), 'hunks': hunks,
            'single_space_context': spaces, 'both_sources_checked': True}


def main():
    paths = []
    folders = '''ideation/maxwell-session004/R015-residual-certificate
ideation/maxwell-session004/R016-helper-review
ideation/maxwell-session004/R017-helper-v002-fix-review
ideation/maxwell-session004/R018-interval-parameter-audit
experiments/maxwell-session004/R014-midpoint-residual-prototype
experiments/maxwell-session004/R015-outward-residual-certificate
experiments/maxwell-session004/R015-outward-residual-certificate/v002-run
literature/maxwell-session004/R013-draft-v007-review
literature/maxwell-session004/R014-draft-v008-diff-review
novelty/maxwell-session004/R012'''.splitlines()
    for folder in folders:
        d = ROLE / folder
        paths.extend(p for p in d.iterdir() if p.is_file())
        for name, key in [('artifact-manifest.json', 'artifacts'),
                          ('delivery_manifest_r014.json', 'files'),
                          ('delivery_manifest_r015.json', 'files')]:
            f = d / name
            if f.exists():
                for item in json.loads(f.read_text(encoding='utf-8'))[key]:
                    check_item(d / item['name'], item)
    for version in ['v007', 'v008']:
        freeze = ROLE / ('writing/maxwell-session004/frozen-draft-' + version + '.json')
        paths.append(freeze)
        for item in json.loads(freeze.read_text(encoding='utf-8'))['files']:
            p = Path(item['path'])
            check_item(p, item)
            paths.append(p)
    d = ROLE / 'verification/maxwell-session004'
    paths.extend(d / n for n in ['全残差误差储能与中点预算独审-R024.md',
                               'R024-proof-evidence.json', 'R024-review-validation.json'])
    v = d / 'R025/R025-review-validation.json'
    paths.append(v)
    for item in json.loads(v.read_text(encoding='utf-8'))['outputs']:
        p = Path(item['path'])
        check_item(p, item)
        paths.append(p)
    names = '''status.json
plan.md
claims.md
runs.md
rounds/R011.md
topic-cards/events.md
topic-cards/T-M001-v010.md
R010-before-return-snapshot.json
R010-index-qa.json
R010-late-evidence.md
R010-push.json
R010-v008-root-review.json
R011-certificate-adoption.md
R011-nonlinear-certificate-adoption.json
R011-role-snapshot.json
outward_float_v001.py
outward_float_v002.py
outward-float-v001-selfcheck.json
outward-float-v002-selfcheck.json
非线性0.3全尾验证-白话说明.md
prepare_R011_publish.py'''.splitlines()
    paths.extend(S / n for n in names)
    diff_records = []
    for a, b in [('v006', 'v007'), ('v007', 'v008')]:
        diff = ROLE / ('writing/maxwell-session004/draft-' + b + '.diff')
        m = R / 'papers/damping-output-boundaries/manuscript'
        diff_records.append(check_diff(diff, m / ('maxwell-engineering-draft-' + a + '.md'),
                                       m / ('maxwell-engineering-draft-' + b + '.md')))
    diff_paths = {x['path'] for x in diff_records}
    items = []
    for p in sorted(set(paths)):
        relative = p.relative_to(R).as_posix()
        assert 'v009' not in relative and '/local-cache/' not in relative
        raw = p.read_bytes()
        assert len(raw) < 1000000
        assert p.suffix in ['.md', '.json', '.csv', '.py', '.txt', '.diff']
        t = raw.decode('utf-8')
        assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}', t)
        for line in t.splitlines():
            assert line.rstrip(' \t') == line or (relative in diff_paths and line == ' '), (relative, line)
        if p.suffix == '.json':
            json.loads(t)
        if p.suffix == '.py':
            ast.parse(t)
        if p.suffix == '.csv':
            rows = list(csv.reader(t.splitlines()))
            assert rows and all(len(row) == len(rows[0]) for row in rows)
        if p.suffix == '.md':
            for link in re.findall(r'\]\(([^\n)]+)\)', t):
                if '://' not in link and not link.startswith('#'):
                    assert (p.parent / link.split('#')[0]).exists(), (relative, link)
        items.append({'path': relative, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    head = subprocess.check_output([GIT, 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    assert head == 'd6a4aa6938dc790ac3ded9b8906807fb1959b6bc'
    assert not subprocess.check_output([GIT, 'diff', '--cached', '--name-only'], cwd=R).strip()
    protected = R / 'papers/damping-output-boundaries/manuscript/theory-draft-v007.md'
    assert hashlib.sha256(protected.read_bytes()).hexdigest() == '93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
    result = {'at': datetime.now().astimezone().isoformat(), 'expected_head': head,
              'files': items, 'file_count': len(items),
              'total_bytes': sum(x['bytes'] for x in items), 'checks_passed': True,
              'scope': 'C025 conditional validated numerics, audited helper repair/failure history, v007 historical and v008 repaired integration.',
              'excluded': 'active engineeringv009, localNPZ/arrays/Excel/PDF/sourceimages, old dirty and unknown5E-07',
              'diff_exceptions': diff_records, 'protected_theory_sha_verified': True}
    (S / 'R011-publish-manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: result[k] for k in ['file_count', 'total_bytes', 'checks_passed']}))


if __name__ == '__main__':
    main()
