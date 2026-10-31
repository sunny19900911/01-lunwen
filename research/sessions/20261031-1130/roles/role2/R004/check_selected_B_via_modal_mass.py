from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
O=Path(__file__).parent;R=O.parents[5];SRC=R/'research/sessions/20261031-1130/roles/role4/R003'
now=lambda:datetime.now(timezone(timedelta(hours=8)))
assert now()<datetime.fromisoformat('2026-10-31T12:20:27+08:00')
manifest=json.loads((SRC/'delivery-manifest.json').read_text(encoding='utf-8'))
e=next(e for e in manifest['inputs'] if e['path'].endswith('controlled_small_tables.json'));p=Path(e['path'])
assert hashlib.sha256(p.read_bytes()).hexdigest()==e['sha256']
data=json.loads(p.read_text(encoding='utf-8'))['Modal Participation Factors'];h=data[1][1]
assert data[2][1][h.index('ModalMass')]=='kN-m-s²'
modalmass={int(x[h.index('Mode')]):float(x[h.index('ModalMass')])*1000 for _,x in data[3:] if x[h.index('Case')]=='Modal'}
with (O/'independent-inertia-B-selected-72.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
out=[]
for x in rows:
    mr=modalmass[int(x['Mode'])];st=float(x['S_all_kg_m']);ss=float(x['S_above_kg_m']);bi=st*ss/mr;bmu=float(x['B_inertia_projection_kg']);err=abs(bi-bmu)
    assert err<1e-10*max(1.,abs(bmu))
    out.append({'Axis':x['Axis'],'cut_story':x['cut_story'],'Mode':x['Mode'],'B_GammaCM_L_kg':bi,'B_mu_mass_Scut_over_S_kg':bmu,'abs_difference_kg':err,'Gamma_CM_per_m':st/mr})
with (O/'selected-B-two-inertia-routes-72.csv').open('x',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');w.writeheader();w.writerows(out)
result={'completed':now().isoformat(),'rows':len(out),'max_abs_two_route_difference_kg':max(x['abs_difference_kg'] for x in out),'Gamma_source':'CM mass projection S divided by native ModalMass converted to kg*m^2; never native UX/UY PF relabelled Gamma','scope':'18-CM input-weighted inertia projection; not Ritz elastic recovery','must_count':0}
with (O/'two-inertia-route-checks.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False))
