from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
O=Path(__file__).resolve().parent;P=O.parent/'R003'
cache=P/'local-cache/all12-low-high-reference-traces.npz'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cases=['SHW3X','SHW4X','RH4X'];stories=['Story'+str(i) for i in range(1,13)]
manifest=json.loads((P/'delivery-manifest.json').read_text(encoding='utf-8'))
assert sha(cache)==manifest['local_only_array']['sha256']
checks=[]
with np.load(cache,allow_pickle=False) as a:
    expected={f'N{n}__{c}__{s}__z{z:g}__{q}' for n in [24,36] for c in cases for s in stories for z in [.05,.08] for q in ['t','native','prediction','low1to12','represented_high13plus','residual']}
    assert set(a.files)==expected
    for c in cases:
        for s in stories:
            oldtime=None
            for z in [.05,.08]:
                p=f'N36__{c}__{s}__z{z:g}__';p24=f'N24__{c}__{s}__z{z:g}__';t=a[p+'t'];v=a[p+'native']
                assert t.ndim==v.ndim==1 and len(t)==len(v) and np.isfinite(t).all() and np.isfinite(v).all()
                assert (np.diff(t)>0).all() and np.allclose(np.diff(t),.02,atol=1e-9,rtol=0)
                assert np.array_equal(v,a[p24+'native']) and np.array_equal(t,a[p24+'t'])
                if oldtime is not None:assert np.array_equal(t,oldtime)
                oldtime=t.copy()
                checks.append(dict(Case=c,Story=s,zeta=z,key_native=p+'native',key_time=p+'t',samples=len(t),start_s=float(t[0]),end_s=float(t[-1]),N24_N36_native_identical=True,pair_times_exact=True))
result=dict(inspected_utc=datetime.now(timezone.utc).isoformat(),start_observed_utc='2026-10-30T13:30:25+00:00',deadline_utc='2026-10-30T13:38:25+00:00',cache_path=str(cache),cache_sha256=sha(cache),all_cache_keys_exact=True,total_cache_keys=len(expected),actual_native_pairs=36,native_vectors=72,N24_N36_duplicates_verified=True,native_selector='N36 is only a cache namespace; native output is identical to N24 and independent of fitted groups',cases=cases,stories=stories,zeta=[.05,.08],Location='Bottom',Axis='X',force_unit='kN',checks=checks)
(O/'cache-key-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False,indent=2))
