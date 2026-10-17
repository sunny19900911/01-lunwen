"""Read-only stage-manuscript transcription/identity checks, no scientific rerun."""
import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def run(root, out):
    out.mkdir(parents=True, exist_ok=False)
    paper = root/'papers/damping-output-boundaries'
    draft = paper/'manuscript/maxwell-engineering-draft-v001.md'
    writer = paper/'research/roles/writing/maxwell-session004'
    review = paper/'research/roles/verification/maxwell-session004'
    assert sha(draft) == '8ec39aeb7692b7745dbd7622b7364ef19d3dd20404755444626ec93358ec24b6'
    m = json.loads((writer/'draft-v001-evidence-map.json').read_text(encoding='utf-8'))
    frozen = json.loads((writer/'frozen-draft-v001.json').read_text(encoding='utf-8'))
    for item in frozen['files']: assert sha(Path(item['path'])) == item['sha256']
    assert sha(draft) == m['draft']['sha256']
    source_states = []
    for name, item in m['sources'].items():
        actual = sha(Path(item['path']))
        mutable = name in {'plan','claims','handoff'}
        if not mutable: assert actual == item['sha256'], name
        source_states.append({'name':name,'read_sha256':item['sha256'],'current_sha256':actual,
                              'mutable_session_document':mutable,'matches_read_version':actual==item['sha256']})
    si = m['mutable_session_sources_frozen_snapshot']; snap_path = Path(si['path'])
    assert sha(snap_path) == si['sha256']
    snapshot = json.loads(snap_path.read_text(encoding='utf-8'))
    for name,item in snapshot['sources'].items():
        body = item['text_utf8'].encode('utf-8')
        assert hashlib.sha256(body).hexdigest() == item['source_identity']['sha256'], name
        assert len(body) == item['source_identity']['bytes']
    text = draft.read_text(encoding='utf-8'); lines = text.splitlines()
    tables=[]; current=[]
    for line in lines+['']:
        if line.startswith('|'): current.append([x.strip() for x in line.strip('|').split('|')])
        elif current:
            tables.append(current); current=[]
    numeric=[t for t in tables if t[0][0]=='工况']; assert len(numeric)==2
    with (review/'R001-review-data/energy_review_summary.csv').open(encoding='utf-8',newline='') as f:
        numbers={r['case']:r for r in csv.DictReader(f)}
    cells=0
    for index, table in enumerate(numeric):
        assert len(table[2:])==6 and len({r[0] for r in table[2:]})==6
        for row in table[2:]:
            x=numbers[row[0]]
            if index==0:
                expected=[x['case'],str(int(x['n'])),f"{float(x['T_s']):.1f}",
                          f"{float(x['Eglobal_delta_kNm']):.6f}",f"{float(x['Elink_delta_kNm']):.6f}",
                          f"{float(x['Elink_over_Eglobal']):.9f}",f"{float(x['conditional_added_damping_percent']):.6f}"]
            else:
                expected=[x['case'],f"{float(x['max_abs_balance_over_peak_input']):.6e}",
                          f"{float(x['max_balance_minus_EnergyError_kNm']):.6e}",
                          str(int(x['negative_Link_increment_count'])),f"{float(x['end_kinetic_plus_potential_kNm']):.6f}"]
            assert row==expected,(index,row,expected)
            cells+=len(row)-1
    assert sum(int(r['negative_Link_increment_count']) for r in numbers.values())==206
    assert re.findall(r'\\tag\{([^}]+)\}',text)==['1','2','3','4','5']
    assert len(re.findall(r'^## [1-6] ',text,re.M))==6
    assert text.count('$$')%2==0 and not re.search(r'!\[[^]]*\]\(',text)
    links=[]
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if target.startswith(('https://','http://')): continue
        path=(draft.parent/target).resolve(); assert path.exists(),target
        links.append(str(path))
    raw=draft.read_bytes(); assert not raw.startswith(b'\xef\xbb\xbf') and b'\r' not in raw
    assert all(x==x.rstrip() for x in lines)
    sources=[draft,writer/'draft-v001-evidence-map.json',writer/'frozen-draft-v001.json',
             writer/'draft-v001-report.md',writer/'draft-v001-validation.json',snap_path,
             review/'R001-review-data/energy_review_summary.csv',review/'原生能量证据独审-R001.md']
    record={'recorded_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'checks_passed':True,
            'scope':'Independent manuscript integration and transcription checks; not another native-reader or science rerun.',
            'script_sha256':sha(Path(__file__)),'freeze_time':frozen['frozen_at'],
            'two_six_row_numeric_tables_exact_to_display_precision':True,'numeric_cells_checked':cells,
            'formula_tags':['1','2','3','4','5'],'local_links':links,'source_states':source_states,
            'session_snapshot_text_hashes_valid':True,
            'inputs':[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sources]}
    (out/'stage_review_static.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'checks_passed':True,'numeric_cells_checked':cells,'frozen_files_verified':len(frozen['files']),
                      'map_sources':len(source_states),'mutable_current_mismatches':[x['name'] for x in source_states if x['mutable_session_document'] and not x['matches_read_version']],
                      'snapshot_sources':len(snapshot['sources']),'local_links':len(links)},ensure_ascii=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    a=p.parse_args();run(a.root.resolve(),a.out)
