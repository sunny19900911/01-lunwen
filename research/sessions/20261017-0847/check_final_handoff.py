"""Verify an explicit reviewed handoff list and optional Git staging bytes."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[3]
SESSION = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    listing = SESSION / 'ready-final-files.json'
    files = json.loads(listing.read_text(encoding='utf-8'))
    assert len(set(files)) == len(files)
    frozen = json.loads((SESSION / 'role-handoff-freeze.json').read_text(encoding='utf-8'))
    for item in frozen['files']:
        assert digest(ROOT/item['path']) == item['sha256'], item['path']
    links = 0
    for rel in files:
        p = ROOT / rel
        assert p.is_file() and p.stat().st_size < 1_000_000, rel
        assert 'local-cache' not in rel and not rel.endswith(('.npz', '.xlsx', '.EDB'))
        if p.suffix == '.json':
            json.loads(p.read_text(encoding='utf-8'))
        if p.suffix == '.md':
            t = p.read_text(encoding='utf-8')
            for m in re.finditer(r'!?\[[^\]\n]*\]\((<[^>]+>|[^)]+)\)', t):
                dest = m.group(1).strip('<>')
                if re.match(r'^(https?:|app:|codex:|#)', dest):
                    continue
                dest = unquote(dest.split('#')[0])
                target = Path(dest) if re.match(r'^[A-Za-z]:[/\\]', dest) else p.parent/dest
                assert target.exists(), (rel, dest)
                links += 1
    # Re-read current frozen manuscript and figures, without running experiments.
    prefix = ROOT / 'papers/damping-output-boundaries'
    mf = json.loads((prefix/'research/roles/writing/frozen-round009.json').read_text(encoding='utf-8'))
    for item in mf['frozen_files']:
        assert digest(ROOT/item['path']) == item['sha256']
    maps = json.loads((prefix/'manuscript/figure-map-v009.json').read_text(encoding='utf-8'))
    for fig in maps['selected_figures']:
        for item in fig['sources']:
            assert digest(ROOT/item['path']) == item['sha256']
    report = {'checked_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
              'files': [{'path': x, 'bytes': (ROOT/x).stat().st_size, 'sha256': digest(ROOT/x)} for x in files],
              'local_links_checked': links, 'role_handoff_hashes_match': True,
              'v009_and_six_figure_hashes_match': True,
              'experiments_rerun': False,
              'scope': 'file integrity and local references; does not certify proof, novelty, external links or original raw data'}
    report_rel = 'research/sessions/20261017-0847/final-handoff-validation.json'
    (ROOT/report_rel).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    if '--stage' in sys.argv:
        assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT).strip()
        staged = files + [report_rel]
        subprocess.run(['git', 'add', '--', *staged], cwd=ROOT, check=True)
        for rel in staged:
            assert subprocess.check_output(['git', 'show', ':'+rel], cwd=ROOT) == (ROOT/rel).read_bytes(), rel
        subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT, check=True)
    print(json.dumps({'files_checked': len(files), 'local_links_checked': links, 'passed': True}))


if __name__ == '__main__':
    main()
