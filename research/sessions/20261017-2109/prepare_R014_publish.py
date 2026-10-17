"""Explicit R014 completed evidence whitelist. No active package or raw data."""
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
B = R / 'papers/damping-output-boundaries/research/roles'
GIT = 'C:/Users/mj528/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/git/cmd/git.exe'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    head = subprocess.check_output([GIT, 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    assert head == 'ec76a71839a4bc28ec3d1e0f549e0f240cb0ad58'
    assert not subprocess.check_output([GIT, 'diff', '--cached', '--name-only'], cwd=R).strip()
    state = json.loads((S / 'status.json').read_text(encoding='utf-8'))
    assert state['checkpoint_open'] and state['current_round'] == 'R014'
    adopted = json.loads((S / 'R014-adoption.json').read_text(encoding='utf-8'))
    assert sha(S / 'R014-root-review.json') == adopted['root_review']['sha256']
    for name, expected in adopted['checked_identities'].items():
        assert sha(R / name) == expected, name
    paths = []
    for folder in [
        'verification/maxwell-session004/R029-modal-sign-corollary',
        'verification/maxwell-session004/R030-force-target-interface-review',
        'ideation/maxwell-session004/R022-force-target-interface',
        'literature/maxwell-session004/R017-FNA-reference-force-scope',
        'literature/maxwell-session004/R017-history-repair',
        'literature/maxwell-session004/R018-modal-ledger-review',
        'experiments/maxwell-session004/R018-modal-ledger-diagnostic',
        'novelty/maxwell-session004/R015-v010-integration-review',
        'writing/maxwell-session004/layout-input-templates-v001',
    ]:
        paths.extend(p for p in (B / folder).iterdir() if p.is_file())
    w = B / 'writing/maxwell-session004'
    freeze = w / 'frozen-draft-v010.json'
    paths += [Path(item['path']) for item in json.loads(freeze.read_text(encoding='utf-8'))['files']]
    paths.append(freeze)
    names = '''status.json
plan.md
claims.md
runs.md
rounds/R013.md
rounds/R014.md
topic-cards/events.md
topic-cards/T-M001-v013.md
R013-FNA-history-root-review.json
R013-after-push-snapshot.json
R013-index-qa.json
R013-late-evidence.md
R013-push.json
R014-adoption.json
R014-dispatches.json
R014-initial-snapshot.json
R014-live-snapshot.json
R014-review-first-attempt.json
R014-root-review.json
force-replay-synthetic-protocol-v001.md
review_R014_integrations.py
prepare_R014_publish.py'''.splitlines()
    paths += [S / name for name in names]
    spec = importlib.util.spec_from_file_location('preflight011', S / 'prepare_R011_publish.py')
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    diff_path = w / 'draft-v010.diff'
    old = R / 'papers/damping-output-boundaries/manuscript/maxwell-engineering-draft-v009.md'
    diff_qa = common.check_diff(diff_path, old, old.with_name('maxwell-engineering-draft-v010.md'))
    archive = B / 'literature/maxwell-session004/R017-history-repair'
    source_context = B / 'literature/maxwell-session004/R017-FNA-reference-force-scope'
    archived_reports = {archive / 'recovered-first-report-f4f3e4b0.md', archive / 'current-report-a33c2080.md'}
    files = []
    for p in sorted(set(paths)):
        name = p.relative_to(R).as_posix()
        assert '/local-cache/' not in name and p.suffix in {'.md', '.json', '.py', '.csv', '.diff'}
        raw = p.read_bytes()
        assert len(raw) < 1000000
        text = raw.decode('utf-8')
        assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}', text)
        if p != diff_path:
            assert all(line.rstrip(' \t') == line for line in text.splitlines()), name
        if p.suffix == '.py':
            ast.parse(text)
        elif p.suffix == '.json':
            json.loads(text)
        elif p.suffix == '.csv':
            rows = list(csv.reader(text.splitlines()))
            assert rows and all(len(row) == len(rows[0]) for row in rows)
            if p.parent.name == 'layout-input-templates-v001':
                assert len(rows) == 1 and len(rows[0]) == len(set(rows[0]))
                assert len(rows[0]) == (27 if p.name == 'device_locations.csv' else 18)
                assert all(re.fullmatch('[a-z][a-z0-9_]*', column) for column in rows[0])
        elif p.suffix == '.md':
            context = source_context if p in archived_reports else p.parent
            for link in re.findall(r'\]\(([^\n)]+)\)', text):
                if '://' not in link and not link.startswith('#'):
                    assert (context / link.split('#')[0]).resolve().exists(), (name, link)
        files.append({'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    assert sha(R / 'papers/damping-output-boundaries/manuscript/theory-draft-v007.md') == '93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
    result = {'at': datetime.now().astimezone().isoformat(), 'expected_head': head, 'checks_passed': True,
              'files': files, 'file_count': len(files), 'total_bytes': sum(item['bytes'] for item in files),
              'diff_qa': diff_qa, 'archive_link_context': 'Two exact version copies resolved against original R017 directory as documented; bytes preserved.',
              'scope': 'Accepted R014 corollary/interface, v010 integration, source/history, finite ledger and empty templates only.',
              'excluded': 'Active R023/R031/actual-gap/contribution/companion稿, unreviewed R019 replay, original data/NPZ/PDF/page copies, old dirty/unknown files.'}
    (S / 'R014-publish-manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({key: result[key] for key in ['file_count', 'total_bytes', 'checks_passed']}))


if __name__ == '__main__':
    main()
