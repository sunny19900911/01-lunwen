"""Validate and optionally stage one explicit list of finished research artifacts."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import ast
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    files = json.loads((HERE/'ready-R004-files.json').read_text(encoding='utf-8'))
    assert len(files) == len(set(files))
    hashes = []
    for rel in files:
        p = ROOT/rel
        assert p.is_file() and p.stat().st_size < 1_000_000, rel
        assert not any(x in rel for x in ('local-cache', 'finite_input_witness.npz', '5E-07'))
        if p.suffix == '.json':
            json.loads(p.read_text(encoding='utf-8'))
        elif p.suffix == '.py':
            ast.parse(p.read_text(encoding='utf-8'))
        if p.suffix == '.md':
            text = p.read_text(encoding='utf-8')
            text = re.sub(r'(?s)\$\$.*?\$\$|\\\[.*?\\\]', '', text)
            for dest in re.findall(r'!?\[[^\]\n]*\]\((<[^>]+>|[^)]+)\)', text):
                dest = unquote(dest.strip('<>').split('#')[0])
                if not dest or re.match(r'^(https?:|app:|codex:)', dest):
                    continue
                target = Path(dest) if re.match(r'^[A-Za-z]:', dest) else p.parent/dest
                assert target.exists(), (rel, dest)
        hashes.append({'path': rel, 'bytes': p.stat().st_size, 'sha256': digest(p)})
    for name in ('theory-round001/frozen.json', 'theory-session002/frozen-v002.json', 'theory-session002/frozen-v003.json', 'theory-session002/frozen-v004.json', 'theory-session002/frozen-v005.json'):
        f = ROOT/'papers/damping-output-boundaries/research/roles/writing'/name
        for item in json.loads(f.read_text(encoding='utf-8'))['files']:
            assert digest(ROOT/item['path']) == item['sha256'], item['path']
    record = ROOT/'papers/damping-output-boundaries/experiments/theory-round001-detuning/run_record.json'
    run = json.loads(record.read_text(encoding='utf-8'))
    for item in run['files']:
        assert digest(record.parent/item['file']) == item['sha256']
    mapped_identities = []
    def check_map(node):
        if isinstance(node, dict):
            if 'path' in node and 'sha256' in node:
                target = Path(node['path'])
                target = target if target.is_absolute() else ROOT/target
                assert digest(target) == node['sha256'], node['path']
                if 'bytes' in node:
                    assert target.stat().st_size == node['bytes'], node['path']
                mapped_identities.append(node['path'])
            for value in node.values():
                check_map(value)
        elif isinstance(node, list):
            for value in node:
                check_map(value)
    check_map(json.loads((ROOT/'papers/damping-output-boundaries/manuscript/theory-figure-evidence-map-v005.json').read_text('utf-8')))
    report = {'checked_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
              'files': hashes, 'v005_mapping_identity_entries_matched': len(mapped_identities), 'writing_frozen_manifests_match': True,
              'experiment_run_hashes_match': True,
              'E3_independent_arithmetic': 'audit_envelope_constants.py actual exit0; Machin pi, max relative difference7.87e-90; no source rerun',
              'independent_Q_audit': 'actual exit0, eight rows, max relative component difference4.67e-84',
              'scope': 'JSON/AST/local references/frozen hashes/staged bytes, not formal proof or novelty certification'}
    report_rel = 'research/sessions/20261017-1219/R004-validation.json'
    (ROOT/report_rel).write_bytes((json.dumps(report, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))
    if '--stage' in sys.argv:
        assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT).strip()
        staged = files + [report_rel]
        subprocess.run(['git', 'add', '--', *staged], cwd=ROOT, check=True)
        for rel in staged:
            assert subprocess.check_output(['git', 'show', ':'+rel], cwd=ROOT) == (ROOT/rel).read_bytes(), rel
        subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, check=True)
    print(json.dumps({'checked_files': len(files), 'passed': True}))


if __name__ == '__main__':
    main()
