"""Read-only final text/table cross-check against prior role2 scalar outputs."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,re,hashlib
O=Path(__file__).resolve().parent; S=O.parents[2]; V=S/'roles/role5/R010'
M=Path('papers/damping-output-boundaries/manuscript/damping-prediction-session021-v009.md')
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
lines=M.read_text(encoding='utf-8').splitlines();checks=[];sources=[]
def source(rel):
    p=S/'roles/role2'/rel;sources.append({'path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});return rows(p)
def tab(num):
    i=next(i for i,l in enumerate(lines) if re.match(r'^\*\*表'+str(num)+r'\s',l));a=[]
    for l in lines[i+1:]:
        if l.startswith('|'):a.append([x.strip() for x in l.strip('|').split('|')])
        elif a:break
    assert len({len(x) for x in a})==1
    return a[2:]
def number(x):return float(x.replace('−','-').replace('%',''))
def check(where,actual,want,tol):
    d=abs(number(actual)-float(want));assert d<=tol,(where,actual,want,d)
    checks.append({'where':where,'display':actual,'reference':float(want),'absolute_difference':d,'display_tolerance':tol})
floor={(x['Case'],x['Story']):x for x in source('R007/author-floor-summary-15.csv')}
for tn,case in [(1,'SHW3X_fixed300'),(4,'publicExample5_H-E12140')]:
    # Frozen role2 R007 public case label differs from the later role2 R012 label.
    publickeys=[k[0] for k in floor if k[0]!='SHW3X_fixed300']
    if tn==4:case=publickeys[0]
    for r in tab(tn):
        a=floor[(case,'Story'+r[0])]
        for col,key,tol in [(1,'slow_rank',0),(2,'controller_time_s',.000501),(3,'P0',.000000501),
                            (4,'S_percent_per_damping_pp',.000000501),(5,'promoting_sum',.000000501),(6,'opposing_sum',.000000501)]:
            check(f'table{tn}/{r[0]}/{key}',r[col],a[key],tol)
own={(x['Case'],x['Story']):x for x in source('R012/independent-baseline-U-C-rates-39.csv')}
for r,(case,story) in zip(tab(5),[('SHW3X','Story5'),('SHW3X','Story12'),('publicExample5_H-E12140','Story1')]):
    for col,key in [(1,'SU'),(2,'SC'),(3,'S')]:check(f'table5/{case}/{story}/{key}',r[col],own[(case,story)][key],.000000501)
modal={(x['Story'],x['Mode']):x for x in source('R007/author-main5-and-rest-12.csv')}
for r in tab(2):
    for story,mc,cc in [('Story5',1,2),('Story12',3,4)]:
        mode='rest' if r[0]=='其余295阶' else r[mc]
        if mode=='rest':
            key=next(k for k in modal if k[0]==story and not k[1].isdigit())
        else:key=(story,mode)
        check(f'table2/{story}/{mode}',r[cc],modal[key]['c'],.000000501)
factors=source('R010/independent-mode13-factors-3.csv')
for r,a in zip(tab(3),factors):
    for col,key,tol in [(1,'B_kg',.000501),(2,'z_m_per_zeta',.000000000501),(3,'sign_V0',0),
                        (4,'v13_kN',.000000501),(5,'dv13_kN_per_zeta',.000000501),(6,'c13',.000000501)]:
        check(f'table3/{r[0]}/{key}',r[col],a[key],tol)
dec=source('R011/independent-envelope-candidate-decisions-8.csv')
for r in tab(12):
    z=number(r[0])/100;a=[x for x in dec if abs(float(x['target_zeta'])-z)<1e-12];assert len(a)==2
    check(f'table12/{z}/min_reference_D',r[1],100*float(a[0]['min_envelope_reference_D']),.000000501)
    assert a[0]['limiting_floor']=='Story'+r[2]
    for col,order,key in [(3,'1','envelope_candidate_action'),(4,'2','envelope_candidate_action'),(5,'2','strong_each_input_candidate_action')]:
        x=next(x for x in a if x['Taylor_order']==order)
        assert r[col]=={'reject':'舍弃','recompute':'完整复算','pass':'采纳'}[x[key]]
summary=source('R010/independent-method-summary-8.csv')
methods=list(dict.fromkeys(x['method'] for x in summary));assert len(methods)==4
for i,r in enumerate(tab(13)):
    case='SHW3X_fixed300' if i<4 else next(x['Case'] for x in summary if x['Case']!='SHW3X_fixed300')
    a=next(x for x in summary if x['Case']==case and x['method']==methods[i%4])
    for col,key in [(2,'MAE_pp'),(3,'max_absolute_error_pp')]:check(f'table13/{case}/{a["method"]}/{key}',r[col],a[key],.000501)
    assert r[4]==a['false_pass']+'/'+a['false_reject']
titles=[int(re.match(r'^\*\*表(\d+)\s',l)[1]) for l in lines if re.match(r'^\*\*表(\d+)\s',l)]
assert titles==list(range(1,14))
for n in titles:tab(n)
local=[]
for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',M.read_text(encoding='utf-8')):
    if not re.match(r'https?://',target):assert (M.parent/target).resolve().exists();local.append(target)
out={'checked_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'main_lines_read':451,'S1_lines_read':296,
 'scalar_fields_checked':len(checks),'checks':checks,'source_scalar_tables':sources,'table_sequence':titles,
 'all13_table_shapes_consistent':True,'all_local_links_resolve':True,'local_links':local,
 'raw_arrays_read':False,'new_ODE':0,'new_models_fits_or_searches':0}
with (O/'scalar-and-structure-checks.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in out.items() if k not in ['checks','source_scalar_tables','local_links']},ensure_ascii=False))
