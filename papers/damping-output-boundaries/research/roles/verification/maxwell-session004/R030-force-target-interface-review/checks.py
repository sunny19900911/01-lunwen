"""Independent exact rational/polynomial interface identities; no ODE or arrays."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
BASE=ROOT/'papers/damping-output-boundaries/research/roles'
AUTHOR=BASE/'ideation/maxwell-session004/R022-force-target-interface'
LIT=BASE/'literature/maxwell-session004/R017-FNA-reference-force-scope'
HISTORY=LIT.parent/'R017-history-repair'
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert record(AUTHOR/'report.md')['sha256']=='2e00ac175aac7beff172b2ac1a40b88d35023d3d7dcd0eeb7a71194254c4e203'
assert record(LIT/'R017-FNA-reference-force-scope.md')['sha256']=='a33c2080171356a5bc6255b3b2a2a443d42b478531be035814c7c5c3f43a3994'
inputs=read(AUTHOR/'input-freeze.json')['inputs']
for x in inputs:assert record(Path(x['path']))==x
files=[p for d in [AUTHOR,LIT,HISTORY] for p in d.iterdir() if p.is_file()]
files += [Path(x['path']) for x in inputs]
sources=[record(p) for p in sorted(set(files))]
history=read(HISTORY/'version-provenance.json')
for version in history['versions']:
    for key in ['report_copy','validation_copy']:assert record(Path(version[key]['path']))==version[key]
assert (HISTORY/'current-report-a33c2080.md').read_bytes()==(LIT/'R017-FNA-reference-force-scope.md').read_bytes()
assert (HISTORY/'current-validation-d54c3aa9.json').read_bytes()==(LIT/'validation-R017.json').read_bytes()
assert record(HISTORY/'recovered-first-report-f4f3e4b0.md')['sha256']=='f4f3e4b0ec0d2b3a2bb61683292778fe0a8fe23285e95916e8b090ed74b457d4'
assert record(HISTORY/'recovered-first-validation-0e3de71a.json')['sha256']=='0e3de71a6ddf099f39d468d253f5112d4e28aa966edc33f252548397488fcb64'
def dot(x,y):return sum((a*b for a,b in zip(x,y)),F(0))
def mv(A,x):return [dot(r,x) for r in A]
def transpose(A):return list(map(list,zip(*A)))
def mm(A,B):return [[dot(r,c) for c in transpose(B)] for r in A]
def msub(A,B):return [[x-y for x,y in zip(r,s)] for r,s in zip(A,B)]
def spectral(M,psi,masses,values):
    return [[sum((v*mv(M,p)[i]*mv(M,p)[j]/m for p,m,v in zip(psi,masses,values)),F(0)) for j in range(2)] for i in range(2)]
def trim(p):
    p=list(p)
    while len(p)>1 and p[-1]==0:p.pop()
    return p
def pa(a,b):return trim([(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))])
def ps(a,c):return trim([x*c for x in a])
def pm(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return trim(c)
M=[[F(2),F(0)],[F(0),F(3)]]
psi=[[F(1),F(1)],[F(3),F(-2)]];mass=[dot(p,mv(M,p)) for p in psi]
assert mass==[5,30] and dot(psi[0],mv(M,psi[1]))==0
lam=[F(1),F(4)];damp=[F(1,10),F(1,5)]
K=spectral(M,psi,mass,lam);C=spectral(M,psi,mass,damp)
ell=[F(2),F(-1)];ports=[[F(1),F(-2)],[F(-1),F(0)],[F(2),F(1)]];forces=[F(2),F(-3),F(7,5)]
for p,l,c in zip(psi,lam,damp):
    assert mv(K,p)==[l*x for x in mv(M,p)]
    assert mv(C,p)==[c*x for x in mv(M,p)]
coeff=[[dot(ell,p)*dot(B,p)/m for B in ports] for p,m in zip(psi,mass)]
for p,m,row in zip(psi,mass,coeff):
    for scale in [F(-5,3),F(7,2),F(-1)]:
        q=[scale*x for x in p];mq=dot(q,mv(M,q))
        assert [dot(ell,q)*dot(B,q)/mq for B in ports]==row
load=[-sum((B[i]*f for B,f in zip(ports,forces)),F(0)) for i in range(2)]
for d in range(3):
    bp=[list(x) for x in ports];fp=list(forces)
    bp[d]=[-x for x in bp[d]];fp[d]=-fp[d]
    assert [-sum((B[i]*f for B,f in zip(bp,fp)),F(0)) for i in range(2)]==load
# Prove transfer identity for every Laplace variable by exact polynomial equality.
A=[[[K[i][j],C[i][j],M[i][j]] for j in range(2)] for i in range(2)]
det=pa(pm(A[0][0],A[1][1]),ps(pm(A[0][1],A[1][0]),-1))
adjload=[pa(ps(A[1][1],load[0]),ps(A[0][1],-load[1])),pa(ps(A[1][0],-load[0]),ps(A[0][0],load[1]))]
direct=pa(ps(adjload[0],ell[0]),ps(adjload[1],ell[1]))
den=[[lam[j],damp[j],F(1)] for j in range(2)]
modal=pa(ps(den[1],-dot(coeff[0],forces)),ps(den[0],-dot(coeff[1],forces)))
assert pm(direct,pm(den[0],den[1]))==pm(modal,det)
# Effective-reference residual and compensation for comparison with U0.
B=ports[0];ke=F(1,10);KN=[[ke*B[i]*B[j] for j in range(2)] for i in range(2)]
uD=[F(7,3),F(-4,5)];u0=[F(-1,4),F(2,7)];fd=F(5)
rd=fd-ke*dot(B,uD)
lhs=[-B[i]*rd-mv(KN,u0)[i] for i in range(2)]
rhs=[-B[i]*fd+mv(KN,[uD[j]-u0[j] for j in range(2)])[i] for i in range(2)]
assert lhs==rhs and mv(KN,u0)!=[0,0]
# Actual C diagonal in Keff basis need not be classical in physical K0 basis.
K0=msub(K,KN);assert K0[0][0]>0 and K0[0][0]*K0[1][1]-K0[0][1]*K0[1][0]>0
invM=[[F(1,2),F(0)],[F(0),F(1,3)]]
def comm(A,B):return msub(mm(A,B),mm(B,A))
assert comm(mm(invM,K),mm(invM,C))==[[0,0],[0,0]]
assert comm(mm(invM,K0),mm(invM,C))!=[[0,0],[0,0]]
zeta=F(1,20);assert 2*zeta*1!=2*zeta*2  # same 5%, M=1, K=1 versus K=4
allpairs={(j,d) for j in range(5) for d in range(7)};I={0,2,4};S={1,5}
part={(j,d) for j,d in allpairs if j in I and d in S}
rmode={(j,d) for j,d in allpairs if j not in I}
rdev={(j,d) for j,d in allpairs if j in I and d not in S}
assert not(part&rmode or part&rdev or rmode&rdev) and part|rmode|rdev==allpairs
assert 2-3<2<2+3  # partial signed contribution alone supplies no order bound
for x in sources:assert record(Path(x['path']))==x
write(HERE/'source-freeze.json',sources)
out={'required_changes':0,'scope':'Independent synthetic exact algebra only; no real arrays, ODE, force reconstruction, PDF or source-script execution.',
 'complete_modal_transfer_identity_polynomial_all_s':True,'arbitrary_consistent_modal_masses':['5','30'],'same_C_common_basis_verified':True,
 'mass_scaling_and_mode_sign_invariance':True,'paired_port_force_flip_invariance':True,
 'FNA_U0_extra_compensation_matrix_identity':True,'residual_only_baseline_is_Ueff_not_U0':True,
 'Keff_C_common_basis_does_not_imply_K0_C_common_basis_counterexample':True,'same_5percent_does_not_imply_same_C_counterexample':True,
 'missing_pairs_disjoint_complete':True,'pair_counts':{'partial':len(part),'missing_modes_all_devices':len(rmode),'retained_modes_missing_devices':len(rdev)},
 'partial_signed_sum_not_total_bound':True,'history_first_SHA_and_current_copies_verified':True,'source_records_unchanged':True,'source_count':len(sources),
 'actual_engineering_interface_certified':False,'time_domain_theorem_and_kernel_initial_jump_reviewed_analytically':True}
write(HERE/'checks.json',out)
print(json.dumps(out,indent=2))
