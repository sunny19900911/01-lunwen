"""Two tiny fixed exact BE algebra cases, not a time integrator or root solver."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
BASE=ROOT/'papers/damping-output-boundaries/research/roles'
AUTHOR=BASE/'ideation/maxwell-session004/R026-forward-BE-contract'
LIT=BASE/'literature/maxwell-session004/R022-BE-source-boundary'
EXP=BASE/'experiments/maxwell-session004/R022-forward-BE-synthetic'
PROTOCOL=ROOT/'research/sessions/20261017-2109/forward-BE-synthetic-protocol-v001.md'
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for x in read(AUTHOR/'artifact-manifest.json')['artifacts']:
    r=record(AUTHOR/x['file']);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
assert record(AUTHOR/'report.md')['sha256']=='7ef3ba03dd24edd6a23ea4dfac8332f21398019e80826821b4999d6c0ad28c78'
assert record(PROTOCOL)['sha256']=='b893b191d9915d5bb7d7c8aaf75f646275c79ace845a6633838c48d0cf729140'
files=list(AUTHOR.iterdir())+list(LIT.iterdir())+[PROTOCOL,EXP/'report.md',EXP/'summary.json']
sources=[record(p) for p in sorted(set(files)) if p.is_file()]
def tr(A):return list(map(list,zip(*A)))
def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def mv(A,x):return [dot(r,x) for r in A]
def mm(A,B):return [[dot(r,c) for c in tr(B)] for r in A]
def ma(A,B,c=F(1)):return [[x+c*y for x,y in zip(r,s)] for r,s in zip(A,B)]
def ms(A,c):return [[c*x for x in r] for r in A]
def va(a,b,c=F(1)):return [x+c*y for x,y in zip(a,b)]
def inv(A):
    n=len(A);W=[list(r)+[F(int(i==j)) for j in range(n)] for i,r in enumerate(A)]
    for j in range(n):
        k=next(k for k in range(j,n) if W[k][j]);W[j],W[k]=W[k],W[j]
        q=W[j][j];W[j]=[x/q for x in W[j]]
        for i in range(n):
            if i!=j:
                q=W[i][j];W[i]=[x-q*y for x,y in zip(W[i],W[j])]
    return [r[n:] for r in W]
def quad(A,x):return dot(x,mv(A,x))
def det(A):return A[0][0]*A[1][1]-A[0][1]*A[1][0]
M=[[F(2),F(1,3)],[F(1,3),F(3)]];K=[[F(4),F(-1)],[F(-1),F(2)]]
C=[[F(1,5),F(-1,5)],[F(-1,5),F(1,5)]]
J=[[F(1,3),F(0)],[F(0),F(1,5)]];G=[[F(1,2),F(0)],[F(0),F(1,7)]]
h=F(1,6);u0=[F(1,2),F(-2,3)];v0=[F(2,5),F(3,7)];F0=[F(1,3),F(-4,5)];f=[F(5,4),F(-7,6)]
assert det(M)>0 and det(K)>0 and det(C)==0 and C[0][0]>0
A=ma(ma(M,ms(C,h)),ms(K,h*h));Ai=inv(A)
assert A[0][0]>0 and det(A)>0
def energy(u,v,force):return (quad(K,u)+quad(M,v)+quad(J,force))/2
E0=energy(u0,v0,F0);assert E0>0
results=[]
for name,B in [('full_rank',[[F(1),F(-2)],[F(1),F(1)]]),('rank_deficient',[[F(1),F(-2)],[F(-2),F(4)]])]:
    S=mm(mm(B,Ai),tr(B));Q=ma(J,ms(S,h*h));assert S[0][1]!=0
    assert S[0][0]>=0 and det(S)>=0 and Q[0][0]>0 and det(Q)>0
    rhs=va(mv(M,v0),va(f,mv(K,u0),-1),h);z=mv(Ai,rhs)
    bn=va(mv(J,F0),mv(B,z),h)
    force=mv(inv(ma(Q,ms(G,h))),bn)
    v=va(z,mv(mm(Ai,tr(B)),force),-h);u=va(u0,v,h)
    block=[A[i]+[h*x for x in tr(B)[i]] for i in range(2)]+[[-h*x for x in B[i]]+ma(J,ms(G,h))[i] for i in range(2)]
    assert mv(inv(block),rhs+mv(J,F0))==v+force
    du=va(u,u0,-1);dv=va(v,v0,-1);df=va(force,F0,-1)
    physical=h*(quad(C,v)+dot(force,mv(G,force)))
    numeric=(quad(K,du)+quad(M,dv)+quad(J,df))/2
    assert energy(u,v,force)-E0+physical+numeric==h*dot(v,f)
    # Perturb all stored end states to exercise all residual work contributions.
    ur=va(u,[F(1,11),F(-2,13)]);vr=va(v,[F(-1,17),F(3,19)]);fr=va(force,[F(2,23),F(-1,29)])
    dur=va(ur,u0,-1);dvr=va(vr,v0,-1);dfr=va(fr,F0,-1)
    ru=va([x/h for x in dur],vr,-1)
    rv=va(va(va(va([x/h for x in mv(M,dvr)],mv(C,vr)),mv(K,ur)),mv(tr(B),fr)),f,-1)
    rf=va(va([x/h for x in mv(J,dfr)],mv(B,vr),-1),mv(G,fr))
    terms=[h*dot(ur,mv(K,ru)),h*dot(vr,rv),h*dot(fr,rf)]
    assert all(x!=0 for x in terms)
    balance=energy(ur,vr,fr)-E0+h*(quad(C,vr)+dot(fr,mv(G,fr)))+(quad(K,dur)+quad(M,dvr)+quad(J,dfr))/2-h*dot(vr,f)
    assert balance==sum(terms,F(0))
    for term in terms:assert balance!=sum(terms,F(0))-2*term
    if name=='rank_deficient':assert det(S)==0
    results.append({'case':name,'C_PSD_singular':True,'Q_SPD_with_full_cross_terms':True,'exact_block_equals_elimination':True,'nonzero_E0_energy_identity':True,'all_three_nonzero_residual_work_plus_signs':True})
# Coupled-port roots need not share the componentwise RHS sign.
Q=[[F(2),F(1)],[F(1),F(2)]];identity=[[F(1),F(0)],[F(0),F(1)]]
multi=mv(inv(ma(Q,identity)),[F(1),F(4)])
assert multi==[F(-1,8),F(11,8)]
summary=read(EXP/'summary.json')
assert summary['fine_u1_u2_maxerror_below_point1']=={'u1':False,'u2':True}
assert summary['comparison']['fine_vs_reference_on_98305_all_nodes']['u1']['max_abs_error']>.1
for x in sources:assert record(Path(x['path']))==x
write(HERE/'source-freeze.json',sources)
out={'required_changes':0,'scope':'Two fixed exact alpha=1 BE algebra substitutions with non-diagonal M, singular PSD C and two ports; no time integration/root iteration or source program executed.',
 'cases':results,'coupled_scalar_sign_bound_counterexample':{'b':['1','4'],'F':['-1/8','11/8'],'Q':'I+positive-semidefinite all-ones matrix','g':'identity','h':'1'},
 'exact_initial_energy':str(E0),'reported_fine_u1_failure_preserved':True,'reported_gate_not_independently_recomputed':True,
 'source_count':len(sources),'sources_unchanged':True,'NPZ_arrays_ODE_source_execution_PDF_or_full_statistics_audit':False,
 'not_established':['general theorem by finite cases','floating bisection success','time-continuous convergence/order/accuracy','engineering or independent physical validation']}
write(HERE/'checks.json',out);print(json.dumps(out,indent=2))
