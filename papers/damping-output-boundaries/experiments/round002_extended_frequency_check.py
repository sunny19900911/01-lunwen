"""One-model tail-frequency check, including independent 70-digit physical solve.

No external solver, SciPy or mpmath. Decimal Jacobi eigensolver forms classical C.
"""
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal, localcontext
import hashlib
import json
import sys
import time
import numpy as np

from round002_frequency_refinement import golden_max

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'round002'
SRC = ROOT.parent / 'W5-重燃双塔连体/02-数据/理论解析突破-20261016/physical_three_story_search.json'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def decimal_physical(mass, stiffness, frequency):
    """Physical matrices formed independently from decimal m/k and Jacobi modes."""
    D=Decimal
    with localcontext() as context:
        context.prec=70
        zero,one=D(0),D(1)
        m=[D(str(x)) for x in mass];k=[D(str(x)) for x in stiffness]
        B=[[one,zero,zero],[-one,one,zero],[zero,-one,one]]
        K=[[sum(B[s][i]*k[s]*B[s][j] for s in range(3)) for j in range(3)] for i in range(3)]
        sm=[x.sqrt() for x in m]
        A=[[K[i][j]/sm[i]/sm[j] for j in range(3)] for i in range(3)]
        Q=[[one if i==j else zero for j in range(3)] for i in range(3)]
        iterations=0
        for iterations in range(200):
            p,q=max(((i,j) for i in range(3) for j in range(i+1,3)),key=lambda ij:abs(A[ij[0]][ij[1]]))
            if abs(A[p][q])<D('1e-64'):
                break
            tau=(A[q][q]-A[p][p])/(2*A[p][q])
            tangent=(one if tau>=0 else -one)/(abs(tau)+(one+tau*tau).sqrt())
            cosine=one/(one+tangent*tangent).sqrt();sine=tangent*cosine
            apq=A[p][q]
            A[p][p]-=tangent*apq;A[q][q]+=tangent*apq
            A[p][q]=A[q][p]=zero
            for i in range(3):
                if i not in [p,q]:
                    x,y=A[i][p],A[i][q]
                    A[i][p]=A[p][i]=cosine*x-sine*y
                    A[i][q]=A[q][i]=sine*x+cosine*y
                x,y=Q[i][p],Q[i][q]
                Q[i][p]=cosine*x-sine*y;Q[i][q]=sine*x+cosine*y
        lam=[A[i][i] for i in range(3)]
        assert all(x>0 for x in lam)
        omega=[x.sqrt() for x in lam]
        C=[[sm[i]*sm[j]*sum(Q[i][s]*(D('.1')*omega[s])*Q[j][s] for s in range(3))
            for j in range(3)] for i in range(3)]
        def plus(a,b):return (a[0]+b[0],a[1]+b[1])
        def minus(a,b):return (a[0]-b[0],a[1]-b[1])
        def mul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
        def div(a,b):
            denominator=b[0]*b[0]+b[1]*b[1]
            return ((a[0]*b[0]+a[1]*b[1])/denominator,(a[1]*b[0]-a[0]*b[1])/denominator)
        def abs2(a):return a[0]*a[0]+a[1]*a[1]
        f=D(str(frequency));values=[];residuals=[]
        for factor in [one,D('1.6')]:
            matrix=[[(K[i][j]-(f*f*m[i] if i==j else zero),f*C[i][j]*factor) for j in range(3)] for i in range(3)]
            rhs=[(-x,zero) for x in m]
            original=[row[:] for row in matrix];rhs_original=rhs[:]
            for p in range(3):
                pivot=max(range(p,3),key=lambda i:abs2(matrix[i][p]))
                matrix[p],matrix[pivot]=matrix[pivot],matrix[p]
                rhs[p],rhs[pivot]=rhs[pivot],rhs[p]
                for i in range(p+1,3):
                    factor_i=div(matrix[i][p],matrix[p][p])
                    for j in range(p,3):matrix[i][j]=minus(matrix[i][j],mul(factor_i,matrix[p][j]))
                    rhs[i]=minus(rhs[i],mul(factor_i,rhs[p]))
            u=[(zero,zero)]*3
            for i in range(2,-1,-1):
                remainder=rhs[i]
                for j in range(i+1,3):remainder=minus(remainder,mul(matrix[i][j],u[j]))
                u[i]=div(remainder,matrix[i][i])
            value=mul((k[2],zero),minus(u[2],u[1]));values.append(value)
            rr=[]
            for i in range(3):
                recovered=(zero,zero)
                for j in range(3):recovered=plus(recovered,mul(original[i][j],u[j]))
                rr.append(abs2(minus(recovered,rhs_original[i])).sqrt())
            residuals.append(max(rr))
        ratio=(abs2(values[1])/abs2(values[0])).sqrt()
        return {'precision_digits':context.prec,'frequency_rad_s':str(f),
                'ratio':str(ratio),'ratio_minus_1p6':str(ratio-D('1.6')),
                'H0_real':str(values[0][0]),'H0_imag':str(values[0][1]),
                'H1_real':str(values[1][0]),'H1_imag':str(values[1][1]),
                'H0_abs':str(abs2(values[0]).sqrt()),'H1_abs':str(abs2(values[1]).sqrt()),
                'omega_rad_s':sorted(str(x) for x in omega),
                'jacobi_rotations':iterations,'jacobi_remaining_offdiag':str(max(abs(A[i][j]) for i in range(3) for j in range(3) if i!=j)),
                'physical_equation_max_absolute_residual':str(max(residuals))}


def main():
    start=time.perf_counter()
    archived=json.loads(SRC.read_text(encoding='utf-8'))
    m=np.array(archived['mass']);k=np.array(archived['stiffness'])
    B=np.array([[1.,0,0],[-1,1,0],[0,-1,1.]])
    M=np.diag(m);K=B.T@np.diag(k)@B
    massscale=np.diag(1/np.sqrt(m));eigen,Q=np.linalg.eigh(massscale@K@massscale)
    omega=np.sqrt(eigen);Phi=massscale@Q;Gamma=Phi.T@M@np.ones(3)
    output=np.diag(k)@B
    residues=-(output@Phi)*Gamma[None,:]
    def H(f,z):
        f=np.asarray(f)
        return (1/(eigen-f[...,None]**2+2j*z*f[...,None]*omega))@residues.T
    def R(f):return abs(H(f,.08))/abs(H(f,.05))
    def physical(f,z):
        C=M@Phi@np.diag(2*z*omega)@Phi.T@M
        return output@np.linalg.solve(K-f*f*M+1j*f*C,-m)
    lo,hi=omega[0]*.01,omega[-1]*100
    freq=np.exp(np.linspace(np.log(lo),np.log(hi),300001));ratios=R(freq)
    rows=[]
    for j in range(3):
        y=ratios[:,j]
        peaks=np.flatnonzero((y[1:-1]>=y[:-2])&(y[1:-1]>=y[2:]))+1
        candidates=[(float(freq[0]),float(y[0])),(float(freq[-1]),float(y[-1]))]
        for index in peaks:
            candidates.append(golden_max(lambda f:float(R(f)[j]),freq[index-1],freq[index+1]))
        f,r=max(candidates,key=lambda item:item[1]);d0,d1=physical(f,.05)[j],physical(f,.08)[j]
        rows.append({'output':f'cut{j+1}','omega_rad_s':float(f),'modal_ratio':float(r),
                     'physical_ratio':float(abs(d1)/abs(d0)),'H0_abs':float(abs(d0)),'H1_abs':float(abs(d1)),
                     'ratio_minus_1p6':float(abs(d1)/abs(d0)-1.6),'local_maxima_detected':len(peaks)})
    selected=max(rows,key=lambda row:row['physical_ratio'])
    highprecision=[decimal_physical(m,k,50),decimal_physical(m,k,selected['omega_rad_s'])]
    Cdelta=M@Phi@np.diag(2*.03*omega)@Phi.T@M
    checks={'fixed_M_K_positive_definite':bool(np.min(np.linalg.eigvalsh(M))>0 and np.min(np.linalg.eigvalsh(K))>0),
            'added_C_positive_definite':bool(np.min(np.linalg.eigvalsh(Cdelta))>0),
            'all_modal_physical_ratios_match_below_1e-8':all(abs(row['modal_ratio']/row['physical_ratio']-1)<1e-8 for row in rows),
            'decimal_ratios_above_1p6_by_more_than_5e-5':all(Decimal(row['ratio_minus_1p6'])>Decimal('5e-5') for row in highprecision),
            'decimal_jacobi_residual_below_1e-60':all(Decimal(row['jacobi_remaining_offdiag'])<Decimal('1e-60') for row in highprecision),
            'decimal_physical_residual_below_1e-60':all(Decimal(row['physical_equation_max_absolute_residual'])<Decimal('1e-60') for row in highprecision),
            'elapsed_below_300_seconds':time.perf_counter()-start<300}
    result={'evidence_id':'E-EXP-002b','finished_utc':datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds':time.perf_counter()-start,'code_sha256':sha(__file__),
            'helper_sha256':sha(Path(__file__).with_name('round002_frequency_refinement.py')),
            'source_model_sha256':sha(SRC),'mass':m.tolist(),'stiffness':k.tolist(),
            'frequency_interval_rad_s':[float(lo),float(hi)],'n_grid':len(freq),'zeta':[.05,.08],
            'added_C_eigenvalues':np.linalg.eigvalsh(Cdelta).tolist(),'cut_maxima':rows,
            'selected_cut':selected,'decimal_independent_physical_checks':highprecision,'checks':checks,
            'boundary':'Small but robust harmonic counterexample to a proposed 1.6 bound for all physical three-storey cuts. This was not an established theorem. No finite-input peak ratio or unboundedness result is inferred. Absolute H amplitudes are small; finite grid plus local search does not certify the global maximum.'}
    (OUT/'extended_frequency_check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'selected_cut':selected,'decimal_checks':highprecision,'checks':checks,'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2))
    assert all(checks.values())


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
