"""Exact-Fraction fixed-node modal corollary; no helper, residual replay or ODE."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime,timezone,timedelta
import hashlib,json
import numpy as np
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
SESSION=ROOT/'research/sessions/20261017-2109'
ROLE=HERE.parent
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def root2(q):
    lo=F(0);hi=max(F(1),q)
    for _ in range(200):
        m=(lo+hi)/2
        if m*m<=q:lo=m
        else:hi=m
    assert lo*lo<=q<=hi*hi
    return lo,hi
def add(a,b):return a[0]+b[0],a[1]+b[1]
def div(a,b):
    assert b[0]>0
    r=[x/y for x in a for y in b];return min(r),max(r)
def scale(a,c):
    r=[x*c for x in a];return min(r),max(r)
def exact(q):return str(q.numerator)+'/'+str(q.denominator)
def outward_decimal(a,digits=12):
    d=10**digits;lo=(a[0]*d)//1;hi=-((-a[1]*d)//1)
    def fmt(n):
        sign='-' if n<0 else '';n=abs(n)
        return sign+str(n//d)+'.'+str(n%d).zfill(digits)
    return [fmt(lo),fmt(hi)]
adopt=SESSION/'R013-addition-certificate-adoption.json'
assert record(adopt)['sha256']=='836a0d6e8e551dd594770fe1421f49780636cdb2d9d2c8cdbd2fd878cc2b729f'
a=read(adopt);assert a['claim']=='M-C027' and a['witness']['J']==16529
protocol=SESSION/'addition-modal-sign-corollary-protocol-v001.md'
model=SESSION/'addition-local-peak-protocol-v001.json'
summary=ROOT/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R017-addition-witness-certificate/summary_r017.json'
s=read(summary);cache=Path(s['source_refs']['local_cache']['path'])
files=[protocol,adopt,model,summary,cache,ROLE/'R028/R028-review-validation.json',ROLE/'R028/R028-proof-evidence.json',ROLE/'R028/R028-review-report.md']
sources=[record(p) for p in files]
assert record(summary)['sha256']==a['checked_sources'][str(summary.relative_to(ROOT)).replace('\\','/')]
assert record(cache)['sha256']==s['source_refs']['local_cache']['sha256']
for p in files[5:]:assert record(p)['sha256']==a['checked_sources'][str(p.relative_to(ROOT)).replace('\\','/')]
assert record(model)['sha256']==s['source_refs']['addition_model']['sha256']
with np.load(cache,allow_pickle=False) as z:
    ar=z['D_N16384'];assert ar.shape==(98305,9) and ar.dtype==np.float64
    node=ar[16529,1:6].copy()
assert np.isfinite(node).all()
u1,u2,v1,v2,force=[F(float(x)) for x in node]
assert float(node[0])==s['identity_gate']['signed_stored_u1_at_J']
i=F(a['bound_values_binary64']['I_J_upper'])
assert float(i).hex()==a['bound_hex']['I_J_upper']
assert i==F(s['candidate_witness_bounds']['I_J_upper_candidate'])
r2=root2(F(2));r3=root2(F(3));sk=root2(F(2,3))
nomp=div((u1+u2,u1+u2),r2);nomm=div((u1-u2,u1-u2),r2)
ep=i;em=div((i,i),r3)[1];eu2=scale(sk,i)[1]
truep=(nomp[0]-ep,nomp[1]+ep);truem=(nomm[0]-em,nomm[1]+em)
u2interval=(u2-eu2,u2+eu2);absu2=max(abs(x) for x in u2interval)
conservative_absu2=abs(u2)+i
flags={'qplus_upper_lt_minus_3_27':truep[1]<F('-3.27'),'qminus_upper_lt_minus_2_75':truem[1]<F('-2.75'),'abs_u2_upper_lt_1_302':absu2<F('1.302'),'conservative_abs_u2_plus_I_lt_1_302':conservative_absu2<F('1.302')}
threshold=F(3,2)*F('2.75')**2
assert threshold==F('11.34375')
for rec in sources:assert record(Path(rec['path']))==rec
out={'review':'R029','claim':'C027 fixed-node modal/passivity corollary','N':16384,'J':16529,'sources':sources,'source_records_unchanged':True,
 'exact_binary64_node':{name:{'fraction':exact(q),'hex':float(q).hex()} for name,q in zip(['u1','u2','v1','v2','F'],[u1,u2,v1,v2,force])},
 'I_J_full_state_error_radius':{'fraction':exact(i),'hex':float(i).hex(),'is_error_energy':False},
 'independent_method':'Fraction exact arithmetic and 200 rational bisections with exact square containment; no outward helper imported, no residual loop or ODE.',
 'nominal_modal_intervals_decimal':{'qplus':outward_decimal(nomp),'qminus':outward_decimal(nomm)},
 'certified_true_intervals_decimal':{'qplus':outward_decimal(truep),'qminus':outward_decimal(truem),'u2':outward_decimal(u2interval),'abs_u2_upper':outward_decimal((absu2,absu2))[1],'conservative_abs_u2_plus_I_upper':outward_decimal((conservative_absu2,conservative_absu2))[1]},
 'exact_rational_true_intervals':{'qplus':[exact(x) for x in truep],'qminus':[exact(x) for x in truem],'u2':[exact(x) for x in u2interval]},
 'threshold_checks':flags,'all_candidate_thresholds_passed':all(flags.values()),
 'power_threshold_exact':exact(threshold),'power_threshold_decimal':'11.34375','no_trapezoidal_work_values_used':True,
 'error_coefficients':{'qplus':'1','qminus':'1/sqrt(3)','u2':'sqrt(2/3); conservative 1 also checked'},
 'decoded_array_scope':'D_N16384 entire member decoded; only fixed J five-state node retained; no full trajectory output',
 'finished_at':datetime.now(timezone(timedelta(hours=8))).isoformat()}
write(HERE/'checks.json',out)
write(HERE/'source-freeze.json',sources)
print(json.dumps({'threshold_checks':flags,'true_intervals':out['certified_true_intervals_decimal'],'nominal':out['nominal_modal_intervals_decimal']},indent=2))
