import csv, json, math, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DATA=ROOT.parent/'data'
geometry_path=DATA/'R001-link-geometry-88.csv'
points_path=DATA/'local-cache/new-full-geometry/point_coordinates.csv'
links=list(csv.DictReader(geometry_path.open(encoding='utf-8-sig')))
points=list(csv.DictReader(points_path.open(encoding='utf-8-sig')))
for p in points:
    for key in ['X_m','Y_m','Z_m']: p[key]=float(p[key])
idx={(round(p['X_m'],6),round(p['Y_m'],6),round(p['Z_m'],6)):p for p in points}
occupied={frozenset([r['I_Point'],r['J_Point']]) for r in links}
rows=[]
for r in links:
    if r['Story'] not in ['Story8','Story9','Story10','Story11']: continue
    i=[float(r['I_'+a+'_m']) for a in ['X','Y','Z']]
    j=[float(r['J_'+a+'_m']) for a in ['X','Y','Z']]
    d=[j[k]-i[k] for k in range(3)]
    choices=[]
    for pi in points:
        if abs(pi['Z_m']-i[2])>1e-6:continue
        delta=[pi[a+'_m']-i[k] for k,a in enumerate(['X','Y','Z'])]
        shift=math.sqrt(sum(x*x for x in delta))
        if not 0.01<shift<=12.0:continue
        pj=idx.get(tuple(round(pi[a+'_m']+d[k],6) for k,a in enumerate(['X','Y','Z'])))
        if not pj:continue
        if frozenset([pi['point'],pj['point']]) in occupied:continue
        choices.append((shift,pi,pj))
    for rank,(shift,pi,pj) in enumerate(sorted(choices,key=lambda t:(t[0],t[1]['point']))[:3],1):
        row={'candidate_id':f"{r['Story']}-{r['Link']}-T{rank}",'Story':r['Story'],'Link':r['Link'],'direction':r['horizontal_direction'],'I_original':r['I_Point'],'J_original':r['J_Point'],'I_candidate':pi['point'],'J_candidate':pj['point'],'translation_m':shift,'length_m':float(r['length_m']),'angle_deg':float(r['elevation_from_horizontal_deg']),'nx':float(r['nx']),'ny':float(r['ny']),'nz':float(r['nz']),'installation_status':'existing coordinates only; framing and installation require review'}
        for kind,vals in [('I_original',i),('J_original',j),('I_candidate',[pi[a+'_m'] for a in ['X','Y','Z']]),('J_candidate',[pj[a+'_m'] for a in ['X','Y','Z']])]:
            for k,a in enumerate(['X','Y','Z']):row[kind+'_'+a+'_m']=vals[k]
        row['candidate_I_source_row']=pi['point_source_row']; row['candidate_J_source_row']=pj['point_source_row']
        rows.append(row)
out=ROOT/'R002-same-floor-translation-pool.csv'
with out.open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
meta={'source_geometry_sha256':hashlib.sha256(geometry_path.read_bytes()).hexdigest(),'source_points_sha256':hashlib.sha256(points_path.read_bytes()).hexdigest(),'rows':len(rows),'distinct_donors':len({r['Link'] for r in rows}),'method':'whole I/J translation <=12 m; exact original axis vector; unoccupied candidate pair; 3 nearest per donor','not_claimed':'framing connectivity, motion improvement, force reduction, or installed-device feasibility'}
(ROOT/'R002-candidate-generation.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
selected=[]
for plan,candidate_id,donor in [('P1','Story8-K83-T1','K83'),('P2','Story8-K10-T1','K10'),('P3','Story8-K83-T1','K82')]:
    target=next(r for r in rows if r['candidate_id']==candidate_id)
    source=next(r for r in links if r['Link']==donor)
    row={'plan':plan,'donor_link':donor,'donor_story':source['Story'],'target_story':target['Story'],'original_I':source['I_Point'],'original_J':source['J_Point'],'candidate_I':target['I_candidate'],'candidate_J':target['J_candidate'],'direction':source['horizontal_direction'],'original_length_m':float(source['length_m']),'candidate_length_m':target['length_m'],'original_angle_deg':float(source['elevation_from_horizontal_deg']),'candidate_angle_deg':target['angle_deg']}
    for a in ['X','Y','Z']:
        for end in ['I','J']:
            row[f'original_{end}_{a}_m']=float(source[f'{end}_{a}_m'])
            row[f'candidate_{end}_{a}_m']=target[f'{end}_candidate_{a}_m']
    row['I_movement_m']=math.sqrt(sum((row[f'candidate_I_{a}_m']-row[f'original_I_{a}_m'])**2 for a in ['X','Y','Z']))
    row['J_movement_m']=math.sqrt(sum((row[f'candidate_J_{a}_m']-row[f'original_J_{a}_m'])**2 for a in ['X','Y','Z']))
    row['status']='unranked alternative; do not combine P1 with P3; check framing and rerun'
    selected.append(row)
with (ROOT/'R002-three-position-drafts.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(selected[0]));w.writeheader();w.writerows(selected)
print(json.dumps(meta,ensure_ascii=False))
for r in rows:
    if r['Story']=='Story8':print(json.dumps(r,ensure_ascii=False))
