from pathlib import Path
from datetime import datetime, timedelta
from fractions import Fraction as F
import hashlib, json
B=Path(__file__).resolve().parent; R=B.parents[1]; S=datetime.fromisoformat('2026-10-21T07:55:25.927640+08:00')
def now(): return datetime.now(S.tzinfo)
def ident(p):
    b=p.read_bytes(); return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def save(name,x):
    p=B/name; assert not p.exists(); p.write_bytes((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode()); json.loads(p.read_text(encoding='utf-8'))
examples=[('E1',[100,50,0],[-80,-120,-40]),('E2',[100,-100,0],[40,80,-80])]
inputs=[ident(R/'candidate-peak-time-correction-v001.md'),ident(B/'R001-validation-standards-partial.md')]
save('R002-input-freeze.json',{'actual_start':S.isoformat(),'frozen_at':now().isoformat(),'inputs':inputs,'examples':examples,'definition':'A=abs(M(tB)); r_at=1-A/PB; d=(PM-A)/PB; r_peak=1-PM/PB','grid':'three saved times 0,1,2 s; first/last tie rules both explicit'})
def calc(b,m,last=False):
    pb=max(map(abs,b)); pm=max(map(abs,m)); ib=[i for i,v in enumerate(b) if abs(v)==pb][-1 if last else 0]; im=[i for i,v in enumerate(m) if abs(v)==pm][-1 if last else 0]
    if pb==0: return {'status':'zero baseline; normalized metrics undefined','PB':pb,'PM':pm}
    a=abs(m[ib]); rat=1-F(a,pb); d=F(pm-a,pb); rp=1-F(pm,pb); assert d>=0 and rp==rat-d
    return {'PB':pb,'PM':pm,'tB':ib,'tM':im,'A':a,'r_at':str(rat),'d':str(d),'r_peak':str(rp),'r_at_percent':str(100*rat),'d_percentage_points':str(100*d),'r_peak_percent':str(100*rp)}
result=[{'example':name,'tie_rule':'last' if last else 'first',**calc(b,m,last)} for name,b,m in examples for last in ([False] if name=='E1' else [False,True])]
assert [(x['r_at'],x['d'],x['r_peak']) for x in result]==[('1/5','2/5','-1/5'),('3/5','2/5','1/5'),('1/5','0','1/5')]
assert 1-F(-80,100)==F(9,5) and result[2]['tM']!=result[2]['tB']
zeros=[calc([0,0],[0,0]),calc([0,0],[1,0]),calc([100,0],[0,0])]; assert zeros[2]['r_at']==zeros[2]['r_peak']=='1' and zeros[2]['d']=='0'
save('R002-checks.json',{'exact_fraction_results':result,'zero_boundary_checks':zeros,'wrong_signed_E1_percent':'180','new_ODE_or_large_data':0})
end=now(); assert end<=S+timedelta(minutes=8)
save('R002-validation.json',{'status':'adopt for formal paired-data calculation and scoped methods text','actual_start':S.isoformat(),'actual_end':end.isoformat(),'elapsed_seconds':(end-S).total_seconds(),'within_8_minutes':True,'only_role2_written':True,'source_bindings':inputs,'new_ODE_arrays_Git_automation_agents':False})
files=[B/n for n in ['R002-check.py','R002-peak-time-correction-review.md','R002-input-freeze.json','R002-checks.json','R002-validation.json']]
for p in files:
    s=p.read_text(encoding='utf-8'); assert '\r' not in p.read_bytes().decode() and all(x.rstrip()==x for x in s.splitlines())
for x in inputs: assert ident(Path(x['path']))==x
save('R002-manifest.json',{'frozen_at':end.isoformat(),'files':[ident(p) for p in files]})
print(json.dumps({'status':'passed','actual_end':end.isoformat(),'elapsed_seconds':(end-S).total_seconds(),'examples':result},ensure_ascii=False))
