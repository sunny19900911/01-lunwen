from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R004';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rule=json.loads((P/'input-rules-freeze.json').read_text(encoding='utf-8'));actual=Path(next(d['path'] for d in rule['sources'] if d['path'].endswith('controlled_small_tables.json')));meta=json.loads(actual.read_text(encoding='utf-8'));tab=meta['Modal Participating Mass Ratios'];rows={int(d[1][1]):dict(SourceRow=d[0],**dict(zip(tab[1][1],d[1]))) for d in tab[3:] if d[1][0]=='Modal'};mu=np.array([float(rows[i]['UX']) for i in range(1,301)]);cum=np.cumsum(mu);assert np.all(mu>=0)
schemes=[]
for threshold in [.90,.95,.99]:
 ii=np.flatnonzero(cum>=threshold);n=int(ii[0]+1) if len(ii) else None;schemes.append(dict(requested_rule=f'first_native_UX_cumulative_ge_{threshold:.2f}',threshold=threshold,N=n,attained=n is not None,cumulative_native_UX_at_N=float(cum[n-1]) if n else None))
for n in [13,18,300]:schemes.append(dict(requested_rule=f'fixed_N{n}',threshold=None,N=n,attained=True,cumulative_native_UX_at_N=float(cum[n-1])))
Ns=sorted({d['N'] for d in schemes if d['N'] is not None})
with (O/'predefined-N-schemes-6.csv').open('x',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(schemes[0]));w.writeheader();w.writerows(schemes)
with (O/'actual-native-UX-mass-ratio-cumulative-300.csv').open('x',encoding='utf-8-sig',newline='') as f:w=csv.writer(f);w.writerow(['Mode','native_UX_mass_ratio','native_UX_cumulative_no_renormalization','SourceRow']);w.writerows([[i+1,float(mu[i]),float(cum[i]),rows[i+1]['SourceRow']] for i in range(300)])
res=json.loads((P/'results.json').read_text(encoding='utf-8'));sources=[actual]+[Path(d['path']) for d in res['arrays_local_only']];bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sources]
for d in res['arrays_local_only']:assert sha(Path(d['path']))==d['sha256']
out=dict(start_observed_utc='2026-10-31T04:30:33+00:00',deadline_utc='2026-10-31T04:42:33+00:00',frozen_utc=datetime.now(timezone.utc).isoformat(),inputs=bindings,requested_schemes=schemes,deduplicated_Ns=Ns,mass_criterion='native actual UX ratios summed in native Mode order; no normalization to 300 sum; first crossing only, not selected by outputs',reference='actual300 fixed physical-source elastic inertia projection R004; no new ODE, fits or mass identification',state_metrics='VN prefix vs full300 same reference direction signed NRMSE and absolute-peak difference; native only absolute curve and peak',tail='T=sum_r>N max_t abs(v_r); U_retention=U_N/U300; maxabs(V300-VN)<=T within existing reference only',relative_scale='T/(PN-T) only PN>T; otherwise undefined; no fullFE bound claim',peak_ratio_interval='[max(0,PN8-T8)/(PN5+T5),(PN8+T8)/(PN5-T5)] only PN5>T5; check full300 ratio inside',full_truncated_arrays='new generated arrays only local-cache, not uploaded')
(O/'input-rules-freeze.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(Ns=Ns,schemes=schemes),ensure_ascii=False,indent=2))
