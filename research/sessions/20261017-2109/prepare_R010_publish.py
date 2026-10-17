"""Read/validate explicit completed research artifacts; write R010 manifest.

No index mutation, commit, push, source changes, or raw-data reads.
"""
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


def main():
    paths = []
    folders = '''ideation/maxwell-session004/R014-nonlinear-symmetry
experiments/maxwell-session004/R013-layout-nonlinear03-synthetic
literature/maxwell-session004/R010-appendix-v001-review
literature/maxwell-session004/R011-appendix-v002-diff-review
literature/maxwell-session004/R012-nonlinear-output-review
novelty/maxwell-session004/R011'''.splitlines()
    for folder in folders:
        paths.extend(p for p in (ROLE / folder).iterdir() if p.is_file())
    for stem in ['theory-appendix-v001', 'theory-appendix-v002', 'modal-interface-v001']:
        freeze = ROLE / ('writing/maxwell-session004/frozen-' + stem + '.json')
        paths.append(freeze)
        for item in json.loads(freeze.read_text(encoding='utf-8'))['files']:
            p = Path(item['path'])
            assert p.stat().st_size == item['bytes']
            assert hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256']
            paths.append(p)
    for name in ['模态最小接口稿整合独审-R022.md', 'R022-proof-evidence.json',
                 'R022-review-validation.json', '非线性交换与条件尾能量独审-R023.md',
                 'R023-proof-evidence.json', 'R023-review-validation.json']:
        paths.append(ROLE / 'verification/maxwell-session004' / name)
    names = '''status.json
plan.md
claims.md
runs.md
rounds/R010.md
topic-cards/events.md
topic-cards/T-M001-v009.md
R009-push.json
R009-index-qa.json
R009-late-evidence.md
R009-modal-interface-root-read.json
R009-appendix-v002-root-diff.json
R009-0054-role-snapshot.json
R010-role-snapshot.json
layout-nonlinear03-protocol-v001.json
nonlinear03-residual-certificate-proposal-v001.md
prepare_R010_publish.py'''.splitlines()
    paths.extend(S / name for name in names)

    # Frozen unified diff whitespace is syntax, checked against both sources.
    diff = ROLE / 'writing/maxwell-session004/theory-appendix-v002.diff'
    lines = diff.read_text(encoding='utf-8').splitlines()
    assert lines[0].startswith('--- ') and lines[1].startswith('+++ ')
    old = (R / 'papers/damping-output-boundaries/manuscript/maxwell-theory-appendix-v001.md').read_text(encoding='utf-8').splitlines()
    new = (R / 'papers/damping-output-boundaries/manuscript/maxwell-theory-appendix-v002.md').read_text(encoding='utf-8').splitlines()
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
                assert old[a] == line[1:]
                a += 1
                ca += 1
            if line[0] in ' +':
                assert new[b] == line[1:]
                b += 1
                cb += 1
            i += 1
        assert (ca, cb) == (int(m[2] or 1), int(m[4] or 1))

    items = []
    for p in sorted(set(paths)):
        relative = p.relative_to(R).as_posix()
        raw = p.read_bytes()
        assert len(raw) < 1000000
        assert p.suffix in ['.md', '.json', '.csv', '.py', '.txt', '.diff']
        t = raw.decode('utf-8')
        assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}', t)
        for line in t.splitlines():
            assert line.rstrip(' \t') == line or (p == diff and line == ' '), relative
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
        items.append({'path': relative, 'bytes': len(raw),
                      'sha256': hashlib.sha256(raw).hexdigest()})
    head = subprocess.check_output([GIT, 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    assert head == '8da9846975e34fcab16370c47a452a9d4d072fa8'
    assert not subprocess.check_output([GIT, 'diff', '--cached', '--name-only'], cwd=R).strip()
    state = json.loads((S / 'status.json').read_text(encoding='utf-8'))
    result = {'at': datetime.now().astimezone().isoformat(), 'expected_head': head,
              'last_verified_remote': state['last_remote_commit'], 'files': items,
              'file_count': len(items), 'total_bytes': sum(x['bytes'] for x in items),
              'scope': 'Reviewed limited interfaces, repair history, nonlinear symmetry/conditional tail, static/source numerical support; residual proposal remains candidate.',
              'active_excluded': ['engineeringv007/v008', 'residual code/helper audits and implementations', 'R024/R016 andnoveltyR012'],
              'local_sources_excluded': 'Excel/NPZ/arrays/PDF/PNG/old dirty files/unknown5E-07',
              'unified_diff_exception': {'path': diff.relative_to(R).as_posix(),
                                         'hunks': hunks, 'context_single_space_lines': spaces,
                                         'syntax_and_both_sources_verified': True},
              'per_file_limit': 1000000, 'checks_passed': True}
    (S / 'R010-publish-manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['file_count', 'total_bytes', 'checks_passed']}))


if __name__ == '__main__':
    main()
