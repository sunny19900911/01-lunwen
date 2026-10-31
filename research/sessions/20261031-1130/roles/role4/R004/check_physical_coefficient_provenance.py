from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,math
import numpy as np
O=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rules=json.loads((O/'input-rules-freeze.json').read_text(encoding='utf-8'))
def pathfor(t):return Path(next(d['path'] for d in rules['sources'] if t in d['path']))
def read(p):return list(csv.DictReader(p.open(encoding='utf-8-sig')))
mass=read(pathfor('identified-masses-before'));cm=read(pathfor('CM-signed-all300'));phys=json.loads(pathfor('controlled_small_tables.json').read_text(encoding='utf-8'));pr={int(d[1][1]):dict(zip(phys['Modal Participation Factors'][1][1],d[1])) for d in phys['Modal Participation Factors'][3:]};fr={int(d[1][1]):dict(zip(phys['Modal Periods And Frequencies'][1][1],d[1])) for d in phys['Modal Periods And Frequencies'][3:]}
mm={(d['Story'],d['Diaphragm']):float(d['identified_mass_kg']) for d in mass if d['Axis']=='X'};cc={(int(d['Mode']),d['Story'],d['Diaphragm']):d for d in cm};coef=read(O/'actual300-frozen-forward-coefficients-300.csv');G=[];B=[]
for i in range(1,301):
 s=math.fsum(m*float(cc[i,*k]['UX_converted_m']) for k,m in mm.items());g=s/(1000*float(pr[i]['ModalMass']));G.append(g)
for cut in range(1,13):B.append([math.fsum(m*float(cc[i,*k]['UX_converted_m']) for k,m in mm.items() if int(k[0][5:])>=cut)*G[i-1] for i in range(1,301)])
saved=np.array([float(d['Gamma_per_m']) for d in coef]);G=np.array(G);B=np.array(B)
res=json.loads((O/'results.json').read_text(encoding='utf-8'))
with np.load(res['arrays_local_only'][0]['path'],allow_pickle=False) as a:
 oldB=a['B_direct'];oldG=a['Gamma_X'];om=a['omega'];maxBabs=float(np.max(abs(B-oldB)));maxBrel=float(np.max(abs(B-oldB)/np.maximum(abs(oldB),1e-300)));maxGrel=float(np.max(abs(G-saved)/np.maximum(abs(saved),1e-300)));assert np.array_equal(saved,oldG);assert np.array_equal(om,np.array([float(fr[i]['CircFreq']) for i in range(1,301)]))
assert maxGrel<1e-10 and maxBrel<1e-10
for d in rules['sources']:assert sha(Path(d['path']))==d['sha256']
now=datetime.now(timezone.utc);elapsed=(now-datetime.fromisoformat('2026-10-31T04:11:33+00:00')).total_seconds();assert elapsed<720
v=dict(frozen_utc=now.isoformat(),elapsed_seconds=elapsed,scope='coefficient provenance only; no new ODE or prediction',independent_math_fsum_Gamma_vs_saved_max_relative_difference=maxGrel,independent_math_fsum_B_vs_saved_max_abs_difference_kg=maxBabs,independent_math_fsum_B_vs_saved_max_relative_difference=maxBrel,all_actual300_omega_exactly_match_source=True,all_csv_Gamma_exactly_match_local_array=True,previous_placeholder_note='verification.json rechecks.Gamma_relative_recheck was an unused initialized placeholder; do not treat it as a checked zero. This file supplies the actual independent source-based coefficient check.',prediction_outputs_unchanged=True,sources_unchanged=True)
(O/'verification-coefficient-addendum-v002.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest-v002.json']
(O/'delivery-manifest-v002.json').write_text(json.dumps(dict(frozen_utc=now.isoformat(),outputs=files,inputs=rules['sources'],local_only_arrays=res['arrays_local_only'],array_upload_allowed=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(v,ensure_ascii=False,indent=2))
