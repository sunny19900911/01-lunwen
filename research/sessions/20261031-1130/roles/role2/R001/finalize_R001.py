from pathlib import Path
from datetime import datetime,timezone,timedelta
from fractions import Fraction as F
import hashlib,json
O=Path(__file__).parent
now=lambda:datetime.now(timezone(timedelta(hours=8)))
start=datetime.fromisoformat('2026-10-31T11:39:14+08:00');deadline=start+timedelta(minutes=12)
assert now()<deadline
def save(name,obj):
    with (O/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
dot=lambda x,y:sum((a*b for a,b in zip(x,y)),F(0))
v=(F(2),F(3));Kv=(2*v[0]-v[1],-v[0]+v[1]);r=(F(1),F(1))
mr=dot(v,v);lam=dot(v,Kv)/mr;S=dot(r,v);Gamma=S/mr;meff=S*S/mr
e=tuple(a-lam*b for a,b in zip(Kv,v))
assert lam==F(5,13) and e==(F(3,13),F(-2,13)) and dot(v,e)==0
checks=[]
for cut in (r,(F(0),F(1))):
    bi=meff*dot(cut,v)/S;be=dot(cut,Kv)*Gamma/lam;cor=dot(cut,e)*Gamma/lam
    assert be-bi==cor and be!=bi
    checks.append({'cut':[str(x) for x in cut],'B_inertia':str(bi),'B_elastic':str(be),'exact_difference':str(be-bi),'exact_residual_correction':str(cor)})
save('exact-rational-Ritz-certificate.json',{'completed':now().isoformat(),'lambda':str(lam),'modal_mass':str(mr),'S':str(S),'Gamma':str(Gamma),'m_eff':str(meff),'residual':[str(x) for x in e],'Galerkin_residual':str(dot(v,e)),'participating_mass_fraction':str(meff/F(2)),'cuts':checks,'meaning':'exact rational arithmetic for this 2-coordinate, one-dimensional static Ritz subspace; not a numerical near-zero argument'})
scientific=json.loads((O/'checks.json').read_text(encoding='utf-8'))
assert scientific['eigen_coefficient_checks']==9 and scientific['normalization_cases']==36 and scientific['Ritz_cut_counterexamples']==2
entries=[]
for p in sorted(O.iterdir()):
    if p.is_file() and p.name!='manifest.json':
        b=p.read_bytes();entries.append({'name':p.name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
t=now();manifest={'task':'session020-role2-R001','status':'complete conditional algebraic audit, physical Eigen test and exact Ritz counterexample','first_tool_observed_start':start.isoformat(),'numerical_completed':scientific['completed'],'frozen':t.isoformat(),'deadline_from_observed_start':deadline.isoformat(),'elapsed_since_observed_start_seconds':(t-start).total_seconds(),'within12_minutes_since_observed_start':t<=deadline,'dispatch_time_not_assumed':True,'formula_verdict':'mass-projection identity for S nonzero; elastic cut identity additionally needs full eigen residual or explicit recovery correction','eigen_coefficient_checks':9,'normalization_cases':36,'degenerate_cases':2,'exact_Ritz_counterexample_cuts':2,'implementation_must_count':0,'new_fit_or_ODE':False,'engineering_data_read':False,'role1_code_or_conclusions_read':False,'source_scope':'new small physical matrices only','files':entries}
save('manifest.json',manifest)
for e in entries:
    b=(O/e['name']).read_bytes();assert len(b)==e['bytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
print(json.dumps({k:v for k,v in manifest.items() if k!='files'},ensure_ascii=False))
