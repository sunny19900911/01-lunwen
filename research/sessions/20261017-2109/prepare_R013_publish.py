"""Explicit completed C027 publication; never stage active interfaces or drafts."""
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
    spec = importlib.util.spec_from_file_location('r011preflight', S / 'prepare_R011_publish.py')
    common = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(common)
    paths = []
    for folder in ['ideation/maxwell-session004/R020-addition-baseline-proof',
                   'ideation/maxwell-session004/R021-addition-parameter-audit',
                   'experiments/maxwell-session004/R017-addition-witness-certificate']:
        d = ROLE / folder
        paths.extend(p for p in d.iterdir() if p.is_file())
        f = d / 'artifact-manifest.json'
        if f.exists():
            for item in json.loads(f.read_text(encoding='utf-8'))['artifacts']:
                common.check_item(d / item['name'], item)
        f = d / 'delivery_manifest_r017.json'
        if f.exists():
            for item in json.loads(f.read_text(encoding='utf-8'))['files']:
                common.check_item(d / item['name'], item)
    d = ROLE / 'verification/maxwell-session004/R028'
    names = ['R028-review-report.md', 'R028-proof-evidence.json', 'R028-review-validation.json']
    paths.extend(d / n for n in names)
    for item in json.loads((d / 'R028-proof-evidence.json').read_text(encoding='utf-8'))['artifacts']:
        p = Path(item['path'])
        assert p.is_relative_to(d)
        common.check_item(p, item)
        paths.append(p)
    d = ROLE / 'novelty/maxwell-session004/R014-contribution-card'
    paths.extend(d / n for n in ['report.md', 'input-freeze.json', 'validation.json'])
    for item in json.loads((d / 'validation.json').read_text(encoding='utf-8'))['files']:
        common.check_item(d / item['file'], item)
    names = '''status.json
plan.md
claims.md
runs.md
rounds/R012.md
rounds/R013.md
topic-cards/events.md
topic-cards/T-M001-v012.md
R012-index-qa.json
R012-push.json
R012-late-evidence.md
R012-0217-live-snapshot.json
R012-modal-ledger-input-freeze.json
R013-0228-live-snapshot.json
R013-addition-certificate-adoption.json
addition-modal-ledger-protocol-v001.md
addition-modal-sign-corollary-protocol-v001.md
force-to-target-interface-protocol-v001.md
加装阻尼器后局部为什么可能更大-白话说明.md
prepare_R013_publish.py'''.splitlines()
    paths.extend(S / n for n in names)
    items = []
    for p in sorted(set(paths)):
        relative = p.relative_to(R).as_posix()
        assert '/local-cache/' not in relative
        assert p.suffix in {'.py', '.md', '.json', '.csv', '.txt'}
        raw = p.read_bytes()
        assert len(raw) < 1000000
        text = raw.decode('utf-8')
        assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}', text)
        assert all(line.rstrip(' \t') == line for line in text.splitlines()), relative
        if p.suffix == '.py':
            ast.parse(text)
        elif p.suffix == '.json':
            json.loads(text)
        elif p.suffix == '.csv':
            rows = list(csv.reader(text.splitlines()))
            assert rows and all(len(row) == len(rows[0]) for row in rows)
        elif p.suffix == '.md':
            for link in re.findall(r'\]\(([^\n)]+)\)', text):
                if '://' not in link and not link.startswith('#'):
                    assert (p.parent / link.split('#')[0]).exists(), (relative, link)
        items.append({'path': relative, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    head = subprocess.check_output([GIT, 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    assert head == '4815d450a7124c0a0b65931bbfa69989041917e3'
    assert not subprocess.check_output([GIT, 'diff', '--cached', '--name-only'], cwd=R).strip()
    state = json.loads((S / 'status.json').read_text(encoding='utf-8'))
    assert state['checkpoint_open'] and state['current_round'] == 'R013'
    assert hashlib.sha256((S / 'R013-addition-certificate-adoption.json').read_bytes()).hexdigest() == '836a0d6e8e551dd594770fe1421f49780636cdb2d9d2c8cdbd2fd878cc2b729f'
    old = R / 'papers/damping-output-boundaries/manuscript/theory-draft-v007.md'
    assert hashlib.sha256(old.read_bytes()).hexdigest() == '93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
    result = {'at': datetime.now().astimezone().isoformat(), 'expected_head': head,
              'files': items, 'file_count': len(items), 'total_bytes': sum(x['bytes'] for x in items),
              'checks_passed': True, 'scope': 'Reviewed conditional C027 Ualltime vsfixedD certificate,parameteraudit,replay/challenges andcontributionboundaries;rootfutureprotocols clearlycandidate.',
              'excluded': 'v010 unreviewed integration,activeR029/R022/CSI R017andhistoryrepair,R018diagnostics,NPZ/rawtables/PDF/pages,old dirty/unknownfiles',
              'protected_theory_sha_verified': True}
    (S / 'R013-publish-manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: result[k] for k in ['file_count', 'total_bytes', 'checks_passed']}))


if __name__ == '__main__':
    main()
