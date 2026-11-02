from pathlib import Path
from decimal import Decimal as D,getcontext
from datetime import datetime,timezone,timedelta
import csv,hashlib,json,collections
getcontext().prec=40
O=Path(__file__).resolve().parent;ROOT=O.parents[5]
p=ROOT/'research/sessions/20261020-1844/roles/role4/R002-all14-main-axis-168.csv'
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
assert sha(p)=='ff25735eb20b9592323fbaf0640e3e85f86b4610af8a2ebd5be37e870494b081'
with p.open(encoding='utf-8-sig',newline='') as f:old=list(csv.DictReader(f))
records=[];groups=collections.defaultdict(list);cases=collections.defaultdict(list)
for lineno,a in enumerate(old,2):
    B=D(a['P0_kN']);M=D(a['P3_kN']);at=D(a['label3_at_label0_peak_kN']);A=abs(at)
    assert B>0 and M>=A
    r={'Case':a['Case'],'Story':a['Story'],'Axis':a['Axis'],'Location':a['Location'],
      'PB':B,'PM':M,'VM_at_tB':at,'A':A,'r':100*(1-M/B),'rat':100*(1-A/B),'d':100*(M-A)/B,
      'tB':D(a['t_peak0_s']),'tM':D(a['t_peak3_s']),'source_row_B':a['source_row0'],
      'source_row_M':a['source_row3'],'source_CSV_line':lineno,'wave_family':a['wave_family'],
      'n_points':a['n_points'],'t0_s':a['t0_s'],'t1_s':a['t1_s']}
    records.append(r);groups[(r['Story'],r['Axis'])].append(r);cases[r['Case']].append(r)
assert len(records)==168 and len(groups)==24 and len(cases)==14
selectors=[]
for (story,axis),rs in sorted(groups.items(),key=lambda x:(int(x[0][0][5:]),x[0][1])):
    g={'Story':story,'Axis':axis,'rows':len(rs)}
    for name,field,op in [('minr','r',min),('maxPM','PM',max),('maxPB','PB',max),('maxd','d',max)]:
        v=op(r[field] for r in rs);g[name]=[r for r in rs if r[field]==v]
    g['median_r']=sorted(r['r'] for r in rs)[len(rs)//2]
    selectors.append(g)
casechecks=[]
for case,rs in sorted(cases.items()):
    v=min(r['r'] for r in rs);ctrl=[r for r in rs if r['r']==v];bottom=next(r for r in rs if r['Story']=='Story1')
    mean=sum(r['r'] for r in rs)/D(len(rs))
    casechecks.append({'Case':case,'Axis':rs[0]['Axis'],'min_records':ctrl,'bottom':bottom,'mean':mean,
      'bottom_minus_min':bottom['r']-v,'mean_minus_min':mean-v})
diff=lambda g,a,b:{r['Case'] for r in g[a]}!={r['Case'] for r in g[b]}
out={'actual_start':'2026-11-02T19:38:14.336228+08:00','independent_selection_completed_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
 'input':{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size},
 'producer_scientific_tables_read_before_this_snapshot':False,'records':records,'selectors':selectors,'cases':casechecks,
 'minr_vs_maxPM_different_groups':sum(diff(g,'minr','maxPM') for g in selectors),
 'maxPB_vs_maxPM_different_groups':sum(diff(g,'maxPB','maxPM') for g in selectors),
 'strict_tie_groups':{name:sum(len(g[name])>1 for g in selectors) for name in ['minr','maxPM','maxPB','maxd']}}
with (O/'independent-selections-before-comparison.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2,default=str)
print(json.dumps({k:v for k,v in out.items() if k not in ['records','selectors','cases']},ensure_ascii=False,indent=2))
print('Story5X',json.dumps(next(g for g in selectors if g['Story']=='Story5' and g['Axis']=='X'),ensure_ascii=False,default=str))
