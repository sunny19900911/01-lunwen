"""Read-only preflight for the explicitly reviewed R012 checkpoint."""
from pathlib import Path
from datetime import datetime
import ast
import csv
import hashlib
import importlib.util
import json
import re
import subprocess

S = Path(__file__).resolve().parent
R = S.parents[2]
ROLE = R / 'papers/damping-output-boundaries/research/roles'
GIT = 'C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'


def main():
    spec = importlib.util.spec_from_file_location('r011_preflight', S / 'prepare_R011_publish.py')
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    paths = []
    folders = '''ideation/maxwell-session004/R019-robust-input-family
experiments/maxwell-session004/R016-addition-local-peak-synthetic
literature/maxwell-session004/R015-draft-v009-source-review
literature/maxwell-session004/R016-addition-output-review
verification/maxwell-session004/R026
verification/maxwell-session004/R027
novelty/maxwell-session004/R013'''.splitlines()
    allowed = {'.md', '.json', '.csv', '.py', '.txt', '.diff'}
    for folder in folders:
        d = ROLE / folder
        paths.extend(p for p in d.iterdir() if p.is_file() and p.suffix in allowed)
        for name, key in [('artifact-manifest.json', 'artifacts'),
                          ('delivery_manifest_r016.json', 'files')]:
            f = d / name
            if f.exists():
                for item in json.loads(f.read_text(encoding='utf-8'))[key]:
                    common.check_item(d / item['name'], item)
    for name in ['frozen-draft-v009.json', 'frozen-draft-v009-status-addendum.json']:
        f = ROLE / 'writing/maxwell-session004' / name
        paths.append(f)
        for item in json.loads(f.read_text(encoding='utf-8'))['files']:
            p = Path(item['path'])
            common.check_item(p, item)
            paths.append(p)
    names = '''status.json
claims.md
runs.md
rounds/R012.md
rounds/R011.md
topic-cards/events.md
topic-cards/T-M001-v011.md
R011-after-push-snapshot.json
R011-0202-live-snapshot.json
R011-0206-live-snapshot.json
R011-index-qa.json
R011-push.json
R011-late-evidence.md
R011-v009-root-preliminary.json
R011-new-evidence-root-read.json
R011-next-input-freeze.json
robust-input-protocol-v001.md
addition-local-peak-protocol-v001.json
addition-baseline-analytic-candidate-v001.md
addition-witness-certificate-protocol-v001.md
R012-role-snapshot.json
R012-adoption.json
R012-primary-source-root-note.md
prepare_R012_publish.py'''.splitlines()
    paths.extend(S / n for n in names)
    diff = ROLE / 'writing/maxwell-session004/draft-v009.diff'
    m = R / 'papers/damping-output-boundaries/manuscript'
    diff_record = common.check_diff(diff, m / 'maxwell-engineering-draft-v008.md',
                                     m / 'maxwell-engineering-draft-v009.md')
    items = []
    for p in sorted(set(paths)):
        relative = p.relative_to(R).as_posix()
        assert p.suffix in allowed and '/local-cache/' not in relative
        raw = p.read_bytes()
        assert len(raw) < 1000000
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
        items.append({'path': relative, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    head = subprocess.check_output([GIT, 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    assert head == 'c2ffd1bc339f1b4803d905fc5bd3a8461a0b4407'
    assert not subprocess.check_output([GIT, 'diff', '--cached', '--name-only'], cwd=R).strip()
    protected = R / 'papers/damping-output-boundaries/manuscript/theory-draft-v007.md'
    assert hashlib.sha256(protected.read_bytes()).hexdigest() == '93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
    state = json.loads((S / 'status.json').read_text(encoding='utf-8'))
    adoption = json.loads((S / 'R012-adoption.json').read_text(encoding='utf-8'))
    assert adoption['C026_reviewed'] is True
    assert state['checkpoint_open'] and state['current_round'] == 'R012'
    result = {'at': datetime.now().astimezone().isoformat(), 'expected_head': head,
              'files': items, 'file_count': len(items), 'total_bytes': sum(x['bytes'] for x in items),
              'checks_passed': True, 'diff_exceptions': [diff_record],
              'scope': 'v009 reviewed integration plus metadata addenda;C026 conditional robustinput proof;R016 finite static/transcription audit andprimarysource boundaries.',
              'excluded': 'R020 baseline candidate package,R017 witness implementation andanyactive/unreviewedfiles,NPZ/Excel/PDF/sourceimages,old dirtyfiles andunknown5E-07',
              'protected_theory_sha_verified': True}
    (S / 'R012-publish-manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: result[k] for k in ['file_count', 'total_bytes', 'checks_passed']}))


if __name__ == '__main__':
    main()
