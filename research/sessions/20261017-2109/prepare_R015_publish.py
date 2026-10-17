"""R015 exact completed whitelist; no active follow-up or source arrays."""
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
    assert head == 'ca9c2f82382da1c7c63759f93e3b51dd61c6d830'
    assert not subprocess.check_output([GIT, 'diff', '--cached', '--name-only'], cwd=R).strip()
    state = json.loads((S / 'status.json').read_text(encoding='utf-8'))
    assert state['checkpoint_open'] and state['current_round'] == 'R015'
    assert datetime.now().astimezone() >= datetime.fromisoformat(state['next_git_eligible_after'])
    adopted = json.loads((S / 'R015-adoption.json').read_text(encoding='utf-8'))
    assert sha(S / 'R015-root-review.json') == adopted['root_review']['sha256']
    for name, expected in adopted['checked_identities'].items():
        assert sha(R / name) == expected, name
    spec = importlib.util.spec_from_file_location('review015', S / 'review_R015_integrations.py')
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    paths = [p for folder in common.FOLDERS for p in (B / folder).iterdir() if p.is_file()]
    paths += list((S / 'R014-force-replay-FFT').iterdir())
    paths += [R / 'papers/damping-output-boundaries/manuscript/maxwell-force-response-interface-v001.md']
    names = '''status.json
claims.md
runs.md
rounds/R014.md
rounds/R015.md
R014-index-qa.json
R014-push.json
R014-after-push-snapshot.json
R014-late-handoff.md
R015-initial-snapshot.json
R015-root-review.json
R015-adoption.json
review_R015_integrations.py
prepare_R015_publish.py
force-replay-independent-FFT-protocol-v001.md
replay_force_via_fft.py
asymmetric-neighborhood-protocol-v001.md
下一次只补这些资料.md'''.splitlines()
    paths += [S / name for name in names]
    mathematical_report = B / 'literature/maxwell-session004/R020-force-replay-FFT-review/R020-force-replay-FFT-review.md'
    mathematical_false_link = 'L[n−1−k]F[k]+R[n−1−k]F[k+1]'
    assert sha(mathematical_report) == 'aa63dd62bfa6d695bb98a64a27c353f7cb1c3e37d78fe3c072a3325453279ac8'
    files = []
    for p in sorted(set(paths)):
        name = p.relative_to(R).as_posix()
        assert p.is_file() and '/local-cache/' not in name
        assert p.suffix in {'.md', '.json', '.py', '.csv'}
        raw = p.read_bytes()
        assert len(raw) < 1000000
        text = raw.decode('utf-8')
        assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}', text)
        assert all(line.rstrip(' \t') == line for line in text.splitlines()), name
        if p.suffix == '.py':
            ast.parse(text)
        elif p.suffix == '.json':
            json.loads(text)
        elif p.suffix == '.csv':
            rows = list(csv.reader(text.splitlines()))
            assert rows and all(len(row) == len(rows[0]) for row in rows)
        elif p.suffix == '.md':
            for link in re.findall(r'\]\(([^\n)]+)\)', text):
                if p == mathematical_report and link == mathematical_false_link:
                    continue
                if '://' not in link and not link.startswith('#'):
                    assert (p.parent / link.split('#')[0]).resolve().exists(), (name, link)
        files.append({'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    assert sha(R / 'papers/damping-output-boundaries/manuscript/theory-draft-v007.md') == '93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
    result = {'at': datetime.now().astimezone().isoformat(), 'expected_head': head, 'files': files,
              'file_count': len(files), 'total_bytes': sum(item['bytes'] for item in files), 'checks_passed': True,
              'scope': 'Reviewed C030 finite peak rule,C031 finite conditional replay,actual-field gaps,companion integration and root candidate perturbation protocol only.',
              'false_math_link_context': 'One exact bracket expression in SHA-bound R020 report, explained by frozen delivery-QA; all actual artifact links resolved.',
              'excluded': 'Unreviewed R024/R033 and R025,active RH4X filter,all original data/NPZ/manual pages/old dirty/unknown files'}
    (S / 'R015-publish-manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({key: result[key] for key in ['file_count', 'total_bytes', 'checks_passed']}))


if __name__ == '__main__':
    main()
