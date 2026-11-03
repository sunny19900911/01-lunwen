from pathlib import Path
import csv,json,re,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[4]
src=R/'papers/damping-output-boundaries/manuscript/p06-actual-main-session026-v001.md'
sha=hashlib.sha256(src.read_bytes()).hexdigest();assert sha=='a11102490ebe100d8bdf91069bd1460364c4a9c5bfd677c0b8b956c7dec7dcdb'
md=src.read_text(encoding='utf-8')
def blocks(s):return re.findall(r'(?m)^\|[^\n]+\n(?:\|[^\n]+\n)+',s)
def rows(b):return [[x.strip() for x in ln.strip().strip('|').split('|')]for ln in b.strip().splitlines()[2:]]
t=blocks(md);assert len(t)==7
old=blocks((R/'papers/damping-output-boundaries/manuscript/p06-actual-damper-session025-v001.md').read_text(encoding='utf-8'))
assert t[1]==old[4] and t[3]==old[5] and t[4]==old[6] and t[6]==old[3]
d=json.loads((H/'actual-mainline-basis.json').read_text(encoding='utf-8'))
cases={x['Case']:x for x in d['case_minima']};n=0
for row in rows(t[2]):
 q=cases[row[0]];expected=[q['Case'],'第'+q['minimum_story'][5:]+'层',f"{q['minimum_reduction_percent']:.4f}",f"{q['bottom_reduction_percent']:.4f}",f"{q['arithmetic_mean12_percent']:.4f}",f"{q['bottom_minus_min_pp']:.4f}"]
 assert row==expected,(row,expected);n+=len(row)
a={(x['Case'],x['Story']):x for x in csv.DictReader((H/'independent-actual-time-peak-72.csv').open(encoding='utf-8-sig'))}
for row in rows(t[5]):
 case,story=row[0].split('/');q=a[case,'Story'+story.removeprefix('第').removesuffix('层')]
 expected=[row[0],f"{float(q['P_B_kN']):.4f}",f"{float(q['P_D_kN']):.4f}",f"{float(q['r_at_percent']):.4f}",f"{float(q['r_peak_percent']):.4f}",f"{float(q['d_pp']):.4f}",f"{float(q['t_B_s']):.2f}→{float(q['t_D_s']):.2f}"]
 assert row==expected,(row,expected);n+=len(row)
f=re.findall(r'\$\$(.*?)\$\$',md,re.S);assert len(f)==5
assert all('P_{D' in x or 'P_D' in x for x in f[:4]) and all('P_M'not in x for x in f[:4])
assert 'q_r(t)'in f[4] and '\\phi_r'in f[4]
assert md[md.index('## 参考文献'):]==(R/'papers/damping-output-boundaries/manuscript/p06-actual-damper-session025-v001.md').read_text(encoding='utf-8').split('## 参考文献',1)[1].join(['## 参考文献',''])
links=[];pending=[]
for target in re.findall(r'\]\(([^)]+)\)',md):
 if '://'in target:continue
 if (src.parent/target).resolve().is_file():links.append(target)
 else:pending.append(target)
assert all(x.endswith('20261103-1700/工程资料与完整附表.md')for x in pending),pending
report={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'manuscript_sha256':sha,'bytes':src.stat().st_size,'tables':len(t),'displays':len(f),'inherited_geometry_control_timing_reference_tables_exact':True,'new_actual_table_fields_checked':n,'actual_formulas_use_D_not_M':True,'references_unchanged':True,'relative_links_present':links,'pending_supplement_links_not_scientific_missing':pending,'must':0,'scientific_response_reruns':0}
(H/'draft-final-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k]for k in ['manuscript_sha256','tables','displays','new_actual_table_fields_checked','must','pending_supplement_links_not_scientific_missing']},ensure_ascii=False))
