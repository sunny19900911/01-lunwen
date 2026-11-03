from pathlib import Path
import re,json,hashlib,datetime
HERE=Path(__file__).resolve().parent;R=HERE.parents[4];O=HERE/'R002';O.mkdir(exist_ok=False)
P=R/'papers/damping-output-boundaries/manuscript/p06-sh3-sh4-session023-v002.md'
Q=R/'research/sessions/20261103-0845/roles/writing/SHW3X-SHW4X-辅助分析资料.md'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)=='8906450fd3ad926e13f3a05de332d692944a6a6e50d43e36a127628b49f9d7c0'
assert sha(Q)=='b41d6563d5daa991d77644531ca14c3038036cd8e65f6979dcb7a5a011c14268'
new=P.read_text(encoding='utf-8');supp=Q.read_text(encoding='utf-8')
old=(R/'papers/damping-output-boundaries/manuscript/p06-engineering-session022-v003.md').read_text(encoding='utf-8')
def tables(s):return re.findall(r'(?m)^\|.*(?:\n\|.*)*',s)
oldtables=tables(old);newtables=tables(new);assert len(oldtables)==5 and len(newtables)==6
assert all(t in newtables for t in oldtables)
displays=lambda s:re.findall(r'\$\$(.*?)\$\$',s,re.S)
assert displays(old)==displays(new) and len(displays(new))==5
assert old.split('## 参考文献\n',1)[1]==new.split('## 参考文献\n',1)[1]
fig=lambda s:re.findall(r'!\[[^\]]*\]\([^)]*\)',s)
assert fig(old)==fig(new) and len(fig(new))==3
assert old.split('## 1 引言',1)[0]==new.split('## 1 引言',1)[0]
data=json.loads((HERE/'R001/results.json').read_text(encoding='utf-8'))['states'];r8=[x for x in data if x['zeta']==.08]
table=next(t for t in newtables if '|量|SHW3X|SHW4X|' in t)
mapping={'软件剪力绝对峰/kN':'native_peak_abs_kN','软件峰时/s':'native_peak_time_s','参照合成/kN':'reference_at_native_peak_signed_kN','参照第2阶项/kN':'reference_mode2_kN','参照第10阶项/kN':'reference_mode10_kN','参照第13阶项/kN':'reference_mode13_kN'}
checks=[]
for line in table.splitlines():
    cells=line.strip('|').split('|')
    if cells[0] in mapping:
        for case,shown in zip(('SHW3X','SHW4X'),cells[1:]):
            native=next(x[mapping[cells[0]]] for x in r8 if x['Case']==case)
            value=float(shown.replace('−','-'));assert abs(value-native)<.00500001
            checks.append({'location':'main-table4','label':cells[0],'case':case,'shown':shown,'source':native})
assert len(checks)==12
st=tables(supp)[0]
keys=['zeta','native_peak_time_s','native_peak_abs_kN','reference_at_native_peak_signed_kN','reference_mode2_kN','reference_mode10_kN','reference_mode13_kN']
for line in st.splitlines():
    c=line.strip('|').split('|')
    if c[0] not in ('SHW3X','SHW4X'):continue
    own=next(x for x in data if x['Case']==c[0] and abs(x['zeta']*100-float(c[1]))<1e-8)
    for i,key in enumerate(keys,1):
        value=float(c[i].replace('−','-'));native=own[key]*(100 if key=='zeta' else 1);tol=.000050001 if i>=3 else 1e-8
        assert abs(value-native)<tol
        checks.append({'location':'supplement-four-states','label':key,'case':c[0],'shown':c[i],'source':native})
for m in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',new+'\n'):
    target=m.group(1)
    if '://' not in target and not target.startswith('#'):assert (P.parent/target).resolve().exists(),target
for m in re.finditer(r'\[[^\]]*\]\(([^)]+)\)',supp+'\n'):
    target=m.group(1)
    if '://' not in target and not target.startswith('#'):assert (Q.parent/target).resolve().exists(),target
out={'at':datetime.datetime.now().astimezone().isoformat(),'main_sha256':sha(P),'supplement_sha256':sha(Q),'old_tables_retained':len(oldtables),'new_tables':len(newtables),'old_display_equations_unchanged':5,'old_figures_unchanged':3,'abstracts_unchanged':True,'references_unchanged':True,'new_table_numeric_cells_checked':len(checks),'checks':checks,'all_local_links_exist':True,'no_arrays_loaded':True,'must_numeric':0}
(O/'text-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='checks'},ensure_ascii=False))
