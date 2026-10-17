"""R016 exact reviewed core only; manuscript repairs and BE work excluded."""
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
    head = subprocess.check_output([GIT,'rev-parse','HEAD'],cwd=R,text=True).strip()
    assert head == 'bb0eac387db195b39d0e9dc257faa4a98d27cdd0'
    assert not subprocess.check_output([GIT,'diff','--cached','--name-only'],cwd=R).strip()
    state = json.loads((S/'status.json').read_text(encoding='utf-8'))
    assert state['checkpoint_open'] and state['current_round'] == 'R016'
    assert datetime.now().astimezone() >= datetime.fromisoformat(state['next_git_eligible_after'])
    adopted = json.loads((S/'R016-adoption.json').read_text(encoding='utf-8'))
    assert sha(S/'R016-root-review.json') == adopted['root_review']['sha256']
    for name,expected in adopted['checked_identities'].items():
        assert sha(R/name) == expected,name
    spec = importlib.util.spec_from_file_location('review016',S/'review_R016_integrations.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    paths = [p for folder in module.FOLDERS for p in (B/folder).iterdir() if p.is_file()]
    names = '''status.json
plan.md
claims.md
runs.md
rounds/R015.md
rounds/R016.md
topic-cards/events.md
topic-cards/T-M001-v014.md
R015-index-qa.json
R015-push.json
R015-after-push-snapshot.json
R015-late-handoff.md
R016-initial-snapshot.json
R016-root-review.json
R016-adoption.json
review_R016_integrations.py
prepare_R016_publish.py
forward-BE-synthetic-protocol-v001.md'''.splitlines()
    paths += [S/name for name in names]
    files = []
    tables_checked = 0
    for p in sorted(set(paths)):
        name = p.relative_to(R).as_posix()
        assert p.is_file() and '/local-cache/' not in name
        assert p.suffix in {'.md','.json','.py','.csv','.txt'}
        raw = p.read_bytes()
        assert len(raw) < 1000000
        text = raw.decode('utf-8-sig')
        assert not re.search(r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{25,}|sk-proj-[A-Za-z0-9_-]{30,}',text)
        assert all(line.rstrip(' \t') == line for line in text.splitlines()),name
        if p.suffix == '.py':
            ast.parse(text)
        elif p.suffix == '.json':
            json.loads(text)
        elif p.suffix == '.csv':
            rows = list(csv.reader(text.splitlines()))
            assert rows and all(len(row)==len(rows[0]) for row in rows)
        elif p.suffix == '.md':
            for link in re.findall(r'\]\(([^\n)]+)\)',text):
                if '://' not in link and not link.startswith('#'):
                    assert (p.parent/link.split('#')[0]).resolve().exists(),(name,link)
            lines = text.splitlines()
            for i,line in enumerate(lines):
                if re.fullmatch(r'\|[ \t:|\-]+\|',line) and i and lines[i-1].startswith('|'):
                    count = lines[i-1].count('|')
                    j = i
                    while j < len(lines) and lines[j].startswith('|'):
                        assert lines[j].count('|') == count,(name,j+1)
                        j += 1
                    tables_checked += 1
        files.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    assert sha(R/'papers/damping-output-boundaries/manuscript/theory-draft-v007.md') == '93fca22d3807d5a59e4a9db6750dce876a65ca974ee1889dbe415f16de8bd323'
    result = {'at':datetime.now().astimezone().isoformat(),'expected_head':head,'checks_passed':True,
              'files':files,'file_count':len(files),'total_bytes':sum(item['bytes'] for item in files),
              'markdown_tables_checked':tables_checked,
              'scope':'Reviewed classical C032/C033 plus frozen RH4X per-stream export lists and root forward experiment protocol candidate.',
              'excluded':'All compact drafts/reviews/repairs and BE theory/prototype/source work pending own audit;all arrays,original data,manual pages,old dirty/unknown files.'}
    (S/'R016-publish-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({key:result[key] for key in ['file_count','total_bytes','checks_passed','markdown_tables_checked']}))


if __name__ == '__main__':
    main()
