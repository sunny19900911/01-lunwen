"""Tiny independent exact linear Schur/initial-affine checks, never a solver."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
AUTHOR=ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R024-force-feedback-closure'
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
for x in read(AUTHOR/'artifact-manifest.json')['artifacts']:
    r=record(AUTHOR/x['file']);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
assert record(AUTHOR/'report.md')['sha256']=='b42de843e3291e959c395701d29f3ebafff71e8e407ff33d12c02164ed55c298'
refs=[ROOT/x['path'] for x in read(AUTHOR/'input-freeze.json')['sources']]
for p,x in zip(refs,read(AUTHOR/'input-freeze.json')['sources']):
    r=record(p);assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
adopt=ROOT/'research/sessions/20261017-2109/R014-adoption.json';authority=read(adopt)
assert authority['accepted']['M-C029']['review']=='reviewed'
assert authority['accepted']['M-C029']['authority'].endswith('R030-force-target-interface-review/report.md')
sources=[record(p) for p in sorted(set(list(AUTHOR.iterdir())+refs+[adopt])) if p.is_file()]
def tr(A):return list(map(list,zip(*A)))
def dot(a,b):return sum((x*y for x,y in zip(a,b)),F(0))
def mv(A,x):return [dot(r,x) for r in A]
def mm(A,B):return [[dot(r,c) for c in tr(B)] for r in A]
def plus(A,B):return [[x+y for x,y in zip(r,s)] for r,s in zip(A,B)]
def inv(A):
    n=len(A);W=[list(r)+[F(int(i==j)) for j in range(n)] for i,r in enumerate(A)]
    for j in range(n):
        k=next(k for k in range(j,n) if W[k][j])
        W[j],W[k]=W[k],W[j];pivot=W[j][j];W[j]=[x/pivot for x in W[j]]
        for i in range(n):
            if i!=j:
                q=W[i][j];W[i]=[x-q*y for x,y in zip(W[i],W[j])]
    return [r[n:] for r in W]
def diag(a,b):return [[a,F(0)],[F(0),b]]
M=diag(F(2),F(3));psi=[[F(1),F(1)],[F(3),F(-2)]];mass=[dot(p,mv(M,p)) for p in psi]
assert mass==[5,30]
lam=[F(2),F(5)];damp=[F(1,5),F(1,2)];s=F(2,3)
def spectral(values):return [[sum((v*mv(M,p)[i]*mv(M,p)[j]/m for v,p,m in zip(values,psi,mass)),F(0)) for j in range(2)] for i in range(2)]
K=spectral(lam);C=spectral(damp)
A=[[M[i][j]*s*s+C[i][j]*s+K[i][j] for j in range(2)] for i in range(2)];S=inv(A)
Smodal=[[sum((p[i]*p[j]/(m*(s*s+d*s+l)) for p,m,d,l in zip(psi,mass,damp,lam)),F(0)) for j in range(2)] for i in range(2)]
assert S==Smodal
scaled=[[F(-3)*x for x in psi[0]],[F(5,2)*x for x in psi[1]]]
scaledmass=[dot(p,mv(M,p)) for p in scaled]
assert [[sum((p[i]*p[j]/(m*(s*s+d*s+l)) for p,m,d,l in zip(scaled,scaledmass,damp,lam)),F(0)) for j in range(2)] for i in range(2)]==S
f=[F(1),F(-2)];ks=[F(3),F(5)];cd=[F(7),F(11)]
V=diag(1/ks[0]+1/(cd[0]*s),1/ks[1]+1/(cd[1]*s));Z=inv(V);results=[]
for name,B in [('full_rank',[[F(1),F(-2)],[F(0),F(1)]]),('rank_deficient',[[F(1),F(-2)],[F(-2),F(4)]])]:
    H=mm(mm(B,S),tr(B));assert H[0][1]!=0 and H[1][0]!=0
    uU=mv(S,f);dU=mv(B,uU);force=mv(inv(plus(V,H)),dU)
    uD=[x-y for x,y in zip(uU,mv(mm(S,tr(B)),force))]
    direct=mv(inv(plus(A,mm(mm(tr(B),Z),B))),f);assert uD==direct
    assert mv(B,uD)==mv(V,force)
    block=[A[i]+tr(B)[i] for i in range(2)]+[[-x for x in B[i]]+V[i] for i in range(2)]
    assert mv(inv(block),f+[F(0),F(0)])==uD+force
    if name=='rank_deficient':assert H[0][0]*H[1][1]-H[0][1]*H[1][0]==0
    flip=diag(F(-1),F(1));BF=mm(flip,B)
    assert mm(mm(BF,S),tr(BF))==mm(mm(flip,H),flip)
    assert mv(inv(plus(V,mm(mm(BF,S),tr(BF)))),mv(BF,uU))==mv(flip,force)
    results.append({'case':name,'full_block_direct_body_and_port_Schur_equal':True,'cross_kernel_nonzero':True,'H_may_be_singular':name=='rank_deficient'})
# Nonzero initial states and D-minus-U homogeneous correction at t=0.
B=[[F(1),F(-2)],[F(0),F(1)]];uU0=[F(1,2),F(-1,3)];h0=[F(2,5),F(3,7)]
deltaU0=mv(B,uU0);Bh0=mv(B,h0);deltaD0=mv(B,[x+y for x,y in zip(uU0,h0)])
F0=[F(1),F(-2)];initialdashpot=[d-v/k for d,v,k in zip(deltaD0,F0,ks)]
assert [d+k0-d0+v/k for d,k0,d0,v,k in zip(deltaU0,Bh0,deltaD0,F0,ks)]==[v/k for v,k in zip(F0,ks)]
assert [v/k+q for v,k,q in zip(F0,ks,initialdashpot)]==deltaD0
Ft=[F(7,3),F(-2,5)];Ig=[F(1,11),F(-3,13)];HF=[F(2,17),F(5,19)];Bh=[F(3,23),F(-2,29)]
deltaU=[d+(v-v0)/k+g+hf-bh for d,v,v0,k,g,hf,bh in zip(deltaD0,Ft,F0,ks,Ig,HF,Bh)]
lhs=[v/k+hf+g for v,k,hf,g in zip(Ft,ks,HF,Ig)]
rhs=[du+bh-d0+v0/k for du,bh,d0,v0,k in zip(deltaU,Bh,deltaD0,F0,ks)]
assert lhs==rhs
assert lhs!=[du-bh-d0+v0/k for du,bh,d0,v0,k in zip(deltaU,Bh,deltaD0,F0,ks)]
for x in sources:assert record(Path(x['path']))==x
write(HERE/'source-freeze.json',sources)
out={'required_changes':0,'scope':'Two exact 2-body/2-port alpha=1 Laplace algebra cases at s=2/3, mass/port transformations and initial affine checks only; no time solver.',
 'independent_Schur_cases':results,'complete_common_modal_resolvent_with_masses_5_30':True,'raw_shape_rescaling_invariance':True,'paired_port_force_flip_invariance':True,
 'nonzero_F0_deltaD0_and_D_minus_U_Bh_signs_passed':True,'initial_dashpot_displacement_consistency_passed':True,
 'not_established_by_computations':['general nonlinear equivalence','existence/uniqueness','discretization convergence','time-domain force solution','engineering interface executability'],
 'source_count':len(sources),'sources_unchanged':True,'author_script_ODE_arrays_PDF_or_NPZ_access':False,'new_solver_implemented':False}
write(HERE/'checks.json',out)
print(json.dumps(out,indent=2))
