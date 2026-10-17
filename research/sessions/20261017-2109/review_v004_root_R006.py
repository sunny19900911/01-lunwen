"""Independent integration checks; reads small frozen artifacts only."""
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
import csv, hashlib, json, re, datetime

ROOT = Path(__file__).resolve().parents[3]
SESSION = Path(__file__).resolve().parent
ROLES = ROOT / 'papers/damping-output-boundaries/research/roles'
DRAFT = ROOT / 'papers/damping-output-boundaries/manuscript/maxwell-engineering-draft-v004.md'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def tables(text):
    out, cur = [], []
    for line in text.splitlines() + ['']:
        if line.startswith('|'):
            cur.append(line)
        elif cur:
            out.append(cur)
            cur = []
    return out

def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

def main():
    output = SESSION / 'R006-v004-root-review-pass.json'
    if output.exists():
        raise FileExistsError(output)
    checks = {}
    text = DRAFT.read_text('utf-8')
    checks['draft_identity'] = sha(DRAFT) == '7403a532b8dd8714ffc1a8c49943397c804e7ca573ed3084089cf0e50bc75fe9'
    freeze = json.loads((ROLES/'writing/maxwell-session004/frozen-draft-v004.json').read_text('utf-8'))
    checks['freeze_7_files'] = len(freeze['files']) == 7 and all(sha(Path(x['path'])) == x['sha256'] and Path(x['path']).stat().st_size == x['bytes'] for x in freeze['files'])
    mapping = json.loads((ROLES/'writing/maxwell-session004/draft-v004-evidence-map.json').read_text('utf-8'))
    checks['sources_52_hashes'] = len(mapping['sources']) == 52 and all(sha(Path(x['path'])) == x['sha256'] for x in mapping['sources'])
    new = tables(text)
    old = tables((DRAFT.parent/'maxwell-engineering-draft-v003.md').read_text('utf-8'))
    checks['five_inherited_tables_exact'] = new[:5] == old and len(old) == 5
    distribution = tables((ROLES/'experiments/maxwell-session004/R006-device-distribution/report.md').read_text('utf-8'))
    checks['48_distribution_rows_exact'] = new[6][2:] == distribution[0][2:] and new[7][2:] == distribution[1][2:] and len(new[6][2:]) == 24
    drift = tables((ROLES/'literature/maxwell-session004/R005-drift-location-review/R005-drift-location-review.md').read_text('utf-8'))
    checks['six_drift_three_budget_exact'] = new[8] == drift[0] and new[9] == drift[1]
    ledger = tables((ROLES/'verification/maxwell-session004/六记录离散能量账本独审-R008.md').read_text('utf-8'))
    # Compare numeric cells against the reviewed ledger, not author QA.
    def nums(line):
        return [Fraction(x.strip().rstrip('%')) for x in line.strip('|').split('|')[1:] if re.fullmatch(r'[+\-\d.eE]+%?', x.strip())]
    ledger_rows = {line.split('|')[1].strip(): nums(line) for t in ledger if t[0] == new[10][0] for line in t[2:]}
    checks['six_ledger_rows_exact'] = all(line.split('|')[1].strip() in ledger_rows and nums(line) == ledger_rows[line.split('|')[1].strip()] for line in new[10][2:])
    records = rows(ROLES/'experiments/maxwell-session004/R006-device-distribution/device_record_summary_r006.csv')
    groups = defaultdict(list)
    for row in records:
        groups[row['Case'], row['Story']].append(row)
    def select(group, field, descending=True):
        threshold = sorted((Fraction(r[field]) for r in group), reverse=descending)[1]
        return {r['Link'] for r in group if (Fraction(r[field]) >= threshold if descending else Fraction(r[field]) <= threshold)}
    mismatches = {}
    equal_both = True
    for key, group in groups.items():
        peak = select(group, 'max_abs_native_P_kN')
        work = select(group, 'Wtrap_native_kNm')
        port = select(group, 'Dport_conditional_kNm')
        equal_both &= work == port and select(group, 'Wtrap_native_kNm',False) == select(group, 'Dport_conditional_kNm',False)
        if peak != work:
            mismatches[key] = (peak, work, port)
    displayed = {}
    for line in new[5][2:]:
        cells = [x.strip() for x in line.strip('|').split('|')]
        displayed[tuple(cells[:2])] = tuple(set(x.split('、')) for x in cells[2:])
    checks['5_of_24_sets_independent'] = len(records)==192 and len(groups)==24 and len(mismatches)==5 and displayed==mismatches and equal_both
    checks['521472_points'] = sum(int(r['n_points']) for r in records) == 521472
    image_links = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', text)
    checks['three_images_resolve'] = len(image_links)==3 and all((DRAFT.parent/x).resolve().is_file() for x in image_links)
    checks['image03_identity'] = sha((DRAFT.parent/image_links[2]).resolve()) == 'f1a8ff0bba9ead35bfca4a5052333cf6171fcf69a9fa9104bb6459bcfab776c4'
    local_links = [x for x in re.findall(r'\]\(([^)]+)\)',text) if not x.startswith(('https:','http:','#'))]
    checks['local_links_resolve'] = all((DRAFT.parent/x).resolve().is_file() for x in local_links)
    checks['formula_tags_1_to_7'] = re.findall(r'\\tag\{(\d+)\}',text)==[str(i) for i in range(1,8)]
    checks['explicit_scope_and_exceptions'] = all(s in text for s in ['工作标题','阶段稿','K12/Story7/RH4X','0/8','单位尚未认证','不是地震前向预测','不认证布置最优'])
    checks['no_unreviewed_new_candidates'] = all(s not in text for s in ['L_F','44458','2.53052','R012'])
    data = DRAFT.read_bytes()
    checks['utf8_LF_no_trailing'] = not data.startswith(b'\xef\xbb\xbf') and b'\r' not in data and all(x==x.rstrip() for x in text.splitlines())
    result = {'recorded_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'draft_sha256':sha(DRAFT),'reviewer':'root, independent from author','checks':checks,'passed':all(checks.values()),'scope':'Small-artifact identity, integration/transcription and 24-group selection arithmetic; full changed prose read separately by root. No raw Excel/NPZ or author script; no remote rendering/engineering/novelty certification.','ledger_review_keys':list(ledger_rows),'prior_run':'R006-v004-root-review.json retained: audit keyed several distinct ledger tables by same IDs and overwrote earlier rows; corrected to unique matching header. No draft or scientific value changed.'}
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps(result,ensure_ascii=False))
    if not result['passed']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
