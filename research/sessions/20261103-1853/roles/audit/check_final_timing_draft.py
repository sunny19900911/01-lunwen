from pathlib import Path
import re,json,hashlib,datetime
H=Path(__file__).resolve().parent;R=H.parents[4]
p=R/'papers/damping-output-boundaries/manuscript/p06-actual-timing-session027-v001.md'
md=p.read_text(encoding='utf-8');sha=hashlib.sha256(p.read_bytes()).hexdigest()
assert sha=='2a703d4b763b720f9f6bb5c44eadb442bafae66b5d134b3904ffcbdd07647938'
def tb(s):return re.findall(r'(?m)^\|[^\n]+\n(?:\|[^\n]+\n)+',s)
def rows(s):return [[x.strip()for x in ln.strip().strip('|').split('|')]for ln in s.strip().splitlines()[2:]]
old=(R/'papers/damping-output-boundaries/manuscript/p06-actual-main-session026-v001.md').read_text(encoding='utf-8')
t=tb(md);o=tb(old);assert len(t)==7
for ni,oi in [(0,0),(1,1),(2,2),(3,3),(4,5)]:assert t[ni]==o[oi]
f=re.findall(r'\$\$(.*?)\$\$',md,re.S);of=re.findall(r'\$\$(.*?)\$\$',old,re.S)
assert len(f)==5 and f[:4]==of[:4] and f[4].strip()==r'd_2-d_1=(\delta_1-\delta_2)-(b_1-b_2).'
d=json.loads((H/'actual-sametime-audit.json').read_text(encoding='utf-8'))
q1=next(x for x in d['Story8_cases']if x['Case']=='RH4X');q2=d['Story10_RH4Y']
mapping=[('基准峰时t_B/s','t_B_s',2),('实际方案峰时t_D/s','t_D_s',2),('基准原峰/kN','P_B_kN',4),('实际方案原峰时读数/kN','D_signed_at_tB_kN',4),('基准在实际方案峰时读数/kN','B_signed_at_tD_kN',4),('实际方案自身峰/kN','P_D_kN',4),('原峰时降低/kN','old_direction_signed_weakening_S_kN',4),('重新取峰比原峰时读数高/kN','own_peak_selection_recovery_M_kN',4),('最终峰降低/kN','P_B_minus_P_D_kN',4),('原峰时评价/%','r_at_percent',4),('完整时程峰减幅/%','r_D_peak_percent',4)]
rr=rows(t[5]);assert len(rr)==len(mapping)
for row,(label,key,n)in zip(rr,mapping):assert row==[label,f'{q1[key]:.{n}f}',f'{q2[key]:.{n}f}'],(row,key)
expected=[]
for label,q in [('第8层/RH4X',q1),('第10层/RH4Y',q2)]:expected.append([label,f"{q['QD_signed_at_tB_kN']:.4f}",f"{q['QD_signed_at_tD_kN']:.4f}",f"{q['P_QD_abs_kN']:.4f}",f"{q['t_QD_s']:.2f}",f"{q['QD_abs_at_tD_over_own_peak_percent']:.4f}"])
assert rows(t[6])==expected
assert md[md.index('## 参考文献'):]==old[old.index('## 参考文献'):]
links=[]
for target in re.findall(r'\]\(([^)]+)\)',md):
 if '://'in target:continue
 assert (p.parent/target).resolve().is_file(),target;links.append(target)
r={'at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'manuscript_sha256':sha,'bytes':p.stat().st_size,'tables':7,'display_formulae':5,'figures':len(re.findall(r'!\[[^\]]*\]\(',md)),'inherited_main_tables1to5_exact':True,'inherited_first4_equations_exact':True,'new_two_time_equation_exact':True,'new_table6_7_fields_checked':len(mapping)*3+12,'all_links_exist':links,'references_unchanged':True,'actual_same_time_review_fields_reused':d['producer_fields_checked'],'must':0,'numeric_or_array_reruns':0}
(H/'final-timing-draft-checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:r[k]for k in ['manuscript_sha256','tables','display_formulae','figures','new_table6_7_fields_checked','must']},ensure_ascii=False))
