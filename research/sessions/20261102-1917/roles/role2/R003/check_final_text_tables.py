from pathlib import Path
from decimal import Decimal as D
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,re
O=Path(__file__).resolve().parent;ROOT=O.parents[5];S=O.parents[2]
M=ROOT/'papers/damping-output-boundaries/manuscript/p06-engineering-session022-v002.md'
A=S/'roles/role5/R002/engineering-data-and-full-tables.md';R=S/'roles/role4/R001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def tables(p):
    out=[];current=[]
    for i,l in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
        if l.startswith('|'):current.append((i,[s.strip() for s in l.strip('|').split('|')]))
        elif current:out.append(current);current=[]
    if current:out.append(current)
    for t in out:assert len({len(r) for _,r in t})==1
    return out
assert sha(R/'engineering-review-by-story-direction-24-v002.csv')=='8d02bcb99ca0bff6134566f34d0f1bd5c4d51054ed79a2f85d9ec099f98c7e81'
assert sha(S/'roles/role2/R002/delivery-manifest.json')=='6282a50630192a178607197ac09c915b468687396d075890d4c32ff8b3647bad'
index={(r['Story'],r['Axis']):r for r in rd(R/'engineering-review-by-story-direction-24-v002.csv')}
checks=[]
def ck(label,actual,want,tol):
    delta=abs(D(actual.replace('−','-'))-D(str(want)));assert delta<=D(tol),(label,actual,want,delta)
    checks.append({'label':label,'display':actual,'reference':str(want),'absolute_difference':str(delta)})
mt=tables(M);at=tables(A);assert len(mt)==5 and len(at)==5
def control_table(t,appendix):
    for line,r in t[2:]:
        axis,st=r[0].split('/');story='Story'+re.search(r'\d+',st)[0];a=index[(story,axis)]
        prefix={'最小减幅':'minimum_r','最大参考剪力':'reference_demand'}[r[1]]
        assert r[2]==a[prefix+'_case'],(line,r,a)
        for col,field,tol in [(3,'PB_kN','.00500001'),(4,'PM_kN','.00500001'),(5,'r_percent','.000050001')]:ck(f'{"A" if appendix else "M"}:{line}/{field}',r[col],a[prefix+'_'+field],tol)
        if appendix:
            ck(f'A:{line}/d',r[6],a[prefix+'_d_pp'],'.000050001')
            for value,field in zip(r[7].split('→'),['tB_s','tM_s']):ck(f'A:{line}/{field}',value,a[prefix+'_'+field],'.00500001')
control_table(mt[1],False);control_table(at[2],True)
assert len(mt[1][2:])==8 and len(at[2][2:])==48
for tab,axis in [(at[3],'X'),(at[4],'Y')]:
    for line,r in tab[2:]:
        a=index[('Story'+r[0],axis)];assert r[4]==a['minimum_r_case']
        for col,field,tol in [(1,'minimum_r_r_percent','.000500001'),(2,'median_r_percent','.000500001'),(3,'maximum_r_percent','.000500001'),(5,'minimum_r_PB_kN','.00500001'),(6,'minimum_r_PM_kN','.00500001')]:ck(f'A:{line}/{field}',r[col],a[field],tol)
meta=rd(R/'paired-input-and-output-metadata-14.csv')
for line,r in at[0][2:]:
    matches=[x for x in meta if x['wave_family_label']==r[0]];assert len(matches)==2
    lo,hi=r[3].split('～')
    for x in matches:
        for actual,field,tol in [(r[2],'saved_n','0'),(lo,'saved_t0_s','.00500001'),(hi,'saved_t1_s','.00500001'),(r[4],'nominal_saved_dt_from_span_s','.00000001'),(r[5],'PGA_mm_per_s2','0')]:ck(f'A:{line}/{x["Case"]}/{field}',actual,x[field],tol)
# Previously audited device/toy/six-case figures are preserved, not recomputed.
old=ROOT/'papers/damping-output-boundaries/manuscript/jgjg-session011-v004.md'
assert sha(old)=='c30cbbccecc21be395ad9cf55de3f842f806cfea8372b72d180d240a3e532b7a'
ot=tables(old)
for newnum,oldnum in [(2,3),(3,5),(4,6)]:assert [r for _,r in mt[newnum]]==[r for _,r in ot[oldnum]]
local=[]
for p in [M,A]:
    text=p.read_text(encoding='utf-8')
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text):
        if not target.startswith(('http://','https://')):assert (p.parent/target).resolve().exists();local.append({'file':str(p),'target':target})
    assert text.count('$$')%2==0
out={'checked_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'main_lines_fully_read':237,'appendix_lines_fully_read':130,
 'representative_control_rows':8,'appendix_control_rows':48,'appendix_original_range_rows':24,'metadata_labels':7,
 'numeric_display_checks':len(checks),'checks':checks,'previous_six_case_device_toy_tables_unchanged':True,
 'local_links_resolve':local,'raw_data_arrays_read':False,'new_scientific_calculations':False,
 'scope':'direct display-to-approved-small-table checks only; no repeat of R002 full source audit'}
with (O/'finite-text-table-checks.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in out.items() if k not in ['checks','local_links_resolve']},ensure_ascii=False))
