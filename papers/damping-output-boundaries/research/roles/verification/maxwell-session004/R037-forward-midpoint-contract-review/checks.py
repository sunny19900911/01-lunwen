"""Independent tiny exact midpoint identities, no temporal integration or source import."""
from pathlib import Path
from fractions import Fraction as F
import ast,hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
AUTHOR=ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R027-forward-midpoint-contract'
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for x in read(AUTHOR/'artifact-manifest.json')['artifacts']:
    r=record(AUTHOR/x['file']);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
assert record(AUTHOR/'report.md')['sha256']=='5ffe4793d5f92e14d46c3e8c31e9cde8e8a3d237dc87b76d0e12153270c7e6f0'
refs=read(AUTHOR/'source-freeze.json')['sources']
for x in refs:
    r=record(ROOT/x['path']);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
old=HERE.parent/'R036-forward-BE-contract-review/checks.py'
sources=[record(p) for p in sorted(set(list(AUTHOR.iterdir())+[ROOT/x['path'] for x in refs]+[old])) if p.is_file()]
# Reuse own frozen pure rational matrix functions only, never its executable run.
names={'tr','dot','mv','mm','ma','ms','va','inv','quad','det'}
tree=ast.parse(old.read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(old),'exec'))
M=[[F(3),F(1,4)],[F(1,4),F(2)]];K=[[F(2),F(-1,2)],[F(-1,2),F(3)]]
C=[[F(1,7),F(-1,7)],[F(-1,7),F(1,7)]];J=[[F(1,4),F(0)],[F(0),F(1,6)]]
G=[[F(1,3),F(0)],[F(0),F(1,5)]];h=F(2,9);a=h/2
un=[F(1,3),F(-3,5)];vn=[F(2,7),F(1,4)];Fn=[F(-2,3),F(4,5)];f=[F(5,6),F(-7,8)]
assert det(M)>0 and det(K)>0 and det(C)==0
A=ma(ma(M,ms(C,a)),ms(K,a*a));Ai=inv(A)
def energy(u,v,force):return (quad(K,u)+quad(M,v)+quad(J,force))/2
def half(x,y):return [(t+s)/2 for t,s in zip(x,y)]
results=[]
for name,B in [('full_rank',[[F(1),F(-1)],[F(2),F(1)]]),('rank_deficient',[[F(1),F(-1)],[F(-2),F(2)]])]:
    S=mm(mm(B,Ai),tr(B));Q=ma(J,ms(S,a*a));assert Q[0][0]>0 and det(Q)>0 and S[0][1]!=0
    rhs=va(mv(M,vn),va(f,mv(K,un),-1),a);z=mv(Ai,rhs);b=va(mv(J,Fn),mv(B,z),a)
    Fm=mv(inv(ma(Q,ms(G,a))),b);vm=va(z,mv(mm(Ai,tr(B)),Fm),-a)
    up=va(un,vm,h);vp=va([2*x for x in vm],vn,-1);Fp=va([2*x for x in Fm],Fn,-1)
    assert half(un,up)==va(un,vm,a) and half(vn,vp)==vm and half(Fn,Fp)==Fm
    block=[A[i]+[a*x for x in tr(B)[i]] for i in range(2)]+[[-a*x for x in B[i]]+ma(J,ms(G,a))[i] for i in range(2)]
    assert mv(inv(block),rhs+mv(J,Fn))==vm+Fm
    du=va(up,un,-1);dv=va(vp,vn,-1);dF=va(Fp,Fn,-1)
    balance=energy(up,vp,Fp)-energy(un,vn,Fn)+h*(quad(C,vm)+dot(Fm,mv(G,Fm))-dot(vm,f))
    assert balance==0 and energy(un,vn,Fn)>0
    BEextra=(quad(K,du)+quad(M,dv)+quad(J,dF))/2;assert BEextra>0
    if name=='rank_deficient':assert det(S)==0
    results.append({'case':name,'halfstep_full_cross_elimination_and_block_equal':True,'nonzero_E0_midpoint_balance':True,'adding_BE_increment_losses_would_break_identity':True})
# Nonlinear endpoint/work-midpoint mismatch, including FORCE mismatch.
un=[F(1,3),F(-2,5)];up=[F(5,4),F(1,7)];vn=[F(-1,5),F(3,8)];vp=[F(4,9),F(-2,7)]
Fn=[F(1),F(-2)];Fp=[F(3),F(4)];um=half(un,up);vm=half(vn,vp);Fm=half(Fn,Fp)
du=va(up,un,-1);dv=va(vp,vn,-1);dF=va(Fp,Fn,-1);B=[[F(1),F(-1)],[F(2),F(1)]]
def g(x):return [t**3 for t in x]  # alpha=1/3,c=1, continuous monotone nonlinear law.
def residual_work(u,v,force):
    Ru=va(du,v,-h)
    Rv=va(mv(M,dv),va(va(va(f,mv(C,v),-1),mv(K,u),-1),mv(tr(B),force),-1),-h)
    RF=va(mv(J,dF),va(mv(B,v),g(force),-1),-h)
    terms=[dot(u,mv(K,Ru)),dot(v,Rv),dot(force,RF)]
    balance=energy(up,vp,Fp)-energy(un,vn,Fn)+h*(quad(C,v)+dot(force,g(force))-dot(v,f))
    return terms,balance
terms,balance=residual_work(um,vm,Fm);assert all(t!=0 for t in terms) and balance==sum(terms,F(0))
ut=va(um,[F(3,23),F(-1,29)]);vt=va(vm,[F(-1,17),F(2,19)]);Ft=va(Fm,[F(1,11),F(-2,13)])
workterms,workbalance=residual_work(ut,vt,Ft)
corrections=[dot(va(um,ut,-1),mv(K,du)),dot(va(vm,vt,-1),mv(M,dv)),dot(va(Fm,Ft,-1),mv(J,dF))]
assert all(t!=0 for t in corrections) and sum(corrections,F(0))!=0
assert workbalance==sum(workterms,F(0))+sum(corrections,F(0))
assert workbalance!=sum(workterms,F(0)) and g(Ft)!=g(Fm)
assert g(Fm)!=half(g(Fn),g(Fp))
# Single-port midpoint root has a valid positive bracket, while F_next is negative.
Fmid=F(1,3);Fprevious=F(1);af=F(2);aa=F(1);bscalar=F(1)
assert af*Fmid+aa*Fmid==bscalar and 0<Fmid<bscalar/af
assert 2*Fmid-Fprevious==F(-1,3)
for x in sources:assert record(Path(x['path']))==x
write(HERE/'source-freeze.json',sources)
out={'required_changes':0,'scope':'Two exact fixed alpha1 halfstep algebra cases and one arbitrary nonlinear stored/work-midpoint identity; no temporal loop or root iteration.',
 'linear_cases':results,'three_nonzero_increment_residual_work_signs':True,'nonlinear_g_of_midpoint_not_endpoint_average':True,
 'all_three_work_midpoint_corrections_nonzero':True,'force_work_midpoint_different_and_nonlinear_g_evaluation_changed':True,'work_midpoint_correction_plus_sign':True,
 'Fmid_bracket_not_Fnext_bracket_counterexample':{'Fmid':'1/3','Fm_bracket':['0','1/2'],'Fprevious':'1','Fnext':'-1/3'},
 'pure_algebra_reuse':'Only selected frozen own R036 Fraction function definitions; its executable run and all author scripts not executed.',
 'source_count':len(sources),'sources_unchanged':True,'NPZ_arrays_ODE_time_integration_author_execution_or_new_statistics_certified':False,
 'not_claimed':['floating roots successful','continuous solution error/order','all-time numerical comparison','BE failure reversed','unique error mechanism','FNA/engineering/physical validation or novelty']}
write(HERE/'checks.json',out);print(json.dumps(out,indent=2))
