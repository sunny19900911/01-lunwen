"""One fixed unit shear chain: numerical checks of an exactly defined algebraic zero."""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import json
import platform
import time

HERE=Path(__file__).resolve().parent


def main():
    started=time.perf_counter()
    with localcontext() as context:
        context.prec=80
        z,o=D(0),D(1)
        K=[[D(2),D(-1),z],[D(-1),D(2),D(-1)],[z,D(-1),o]]
        A=[row[:] for row in K]
        Q=[[o if i==j else z for j in range(3)] for i in range(3)]
        for count in range(200):
            p,q=max(((i,j) for i in range(3) for j in range(i+1,3)),key=lambda ij:abs(A[ij[0]][ij[1]]))
            if abs(A[p][q])<D('1e-72'):
                break
            tau=(A[q][q]-A[p][p])/(2*A[p][q])
            tt=(o if tau>=0 else -o)/(abs(tau)+(o+tau*tau).sqrt())
            cc=o/(o+tt*tt).sqrt();ss=tt*cc;apq=A[p][q]
            A[p][p]-=tt*apq;A[q][q]+=tt*apq;A[p][q]=A[q][p]=z
            for i in range(3):
                if i not in [p,q]:
                    x,y=A[i][p],A[i][q]
                    A[i][p]=A[p][i]=cc*x-ss*y;A[i][q]=A[q][i]=ss*x+cc*y
                x,y=Q[i][p],Q[i][q]
                Q[i][p]=cc*x-ss*y;Q[i][q]=ss*x+cc*y
        order=sorted(range(3),key=lambda i:A[i][i])
        lam=[A[i][i] for i in order]
        omega=[x.sqrt() for x in lam]
        phi=[[Q[j][i] for j in range(3)] for i in order]
        gamma=[sum(v) for v in phi]
        rho=[(v[2]-v[1])*g for v,g in zip(phi,gamma)]
        S=sum(omega);P=omega[0]*omega[1]*omega[2]
        pair=(omega[0]+omega[1])*(omega[0]+omega[2])*(omega[1]+omega[2])
        zz=(pair/(4*S**3)).sqrt();kappa=D('1.6');zz1=kappa*zz
        c=o
        coeff=[c,2*c*S*S/pair,4*c*S/pair,2*c/pair]  # A0,A1,A2,A3.
        direct=[z,z,z,z]
        for i,r in enumerate(rho):
            j,l=(i+1)%3,(i+2)%3
            direct[0]+=r*lam[j]*lam[l]
            direct[1]+=2*r*omega[j]*omega[l]*(omega[j]+omega[l])
            direct[2]+=4*r*omega[j]*omega[l]
            direct[3]+=2*r*(omega[j]+omega[l])
        coefficient_error=max(abs(v-w) for v,w in zip(direct,coeff))
        assert coefficient_error<D('1e-65')
        vandermonde=max(abs(r-c/((lam[i]-lam[(i+1)%3])*(lam[i]-lam[(i+2)%3]))) for i,r in enumerate(rho))
        moments=[sum(r*x**p for r,x in zip(rho,lam)) for p in range(3)]
        assert max(abs(moments[0]),abs(moments[1]),abs(moments[2]-1),vandermonde)<D('1e-65')
        def transfer(damping):
            values=[]
            for w,r in zip(omega,rho):
                aa=w*w-S*S;bb=2*damping*w*S;den=aa*aa+bb*bb
                values.append((r*aa/den,-r*bb/den))
            return sum(v[0] for v in values),sum(v[1] for v in values)
        h0=transfer(zz);h1=transfer(zz1)
        abs0=(h0[0]*h0[0]+h0[1]*h0[1]).sqrt()
        abs1=(h1[0]*h1[0]+h1[1]*h1[1]).sqrt()
        assert abs0<D('1e-65') and abs1>0 and 0<zz<zz1<1
        M=[sum(abs(r)/(d*d*w**3*(1-d*d).sqrt()) for w,r in zip(omega,rho)) for d in [zz,zz1]]
        pi=D('3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628')
        # This lower formula assumes the exact algebraic zero proved in round-008.
        bounds=[{"T_s":t,"support_s":2*t,"ratio_lower_formula_evaluated":str((2*D(t)*abs1/pi-M[1])/M[0])} for t in [1000,10000,100000,200000,1000000]]
        C=[[sum(2*zz*omega[s]*phi[s][i]*phi[s][j] for s in range(3)) for j in range(3)] for i in range(3)]
        exact_new_numerator=F(1)-F(8,5)**2
        assert exact_new_numerator==F(-39,25)
        residual=max(abs(sum(K[i][j]*phi[s][j] for j in range(3))-lam[s]*phi[s][i]) for s in range(3) for i in range(3))
        out={"time_Asia_Shanghai":datetime.now(timezone(timedelta(hours=8))).isoformat(),
             "python_version":platform.python_version(),"precision_digits":context.prec,
             "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "fixed_model":{"M":"I3","K":[[str(v) for v in row] for row in K],"b":[1,1,1],"ell":[0,-1,1],"input":"f=-base_acceleration"},
             "exact_frequency_definition":"omega_i=2*sin((2*i-1)*pi/14), i=1,2,3; lambda roots of lambda^3-5lambda^2+6lambda-1",
             "exact_zero_definition":"Omega*=S=sum(omega); zeta*=sqrt(D/(4*S^3)), D=product_{i<j}(omega_i+omega_j)",
             "omega":list(map(str,omega)),"rho_from_physical_modes":list(map(str,rho)),
             "S":str(S),"P":str(P),"D_pair_sum_product":str(pair),
             "A0_A1_A2_A3":list(map(str,coeff)),"zeta_star":str(zz),"zeta_new":str(zz1),
             "direct_modal_numerator_coefficient_max_difference":str(coefficient_error),
             "moments_p0_p1_p2":list(map(str,moments)),"vandermonde_residue_max_difference":str(vandermonde),
             "eigen_equation_max_residual":str(residual),"H0_numeric_abs_residual":str(abs0),
             "H1_numeric_complex":[str(v) for v in h1],"H1_numeric_abs":str(abs1),
             "new_numerator_exact":str(exact_new_numerator),
             "delta_C_modal_eigenvalues":[str(2*(zz1-zz)*w) for w in omega],
             "C0_13":str(C[0][2]),"moment_upper_formula_evaluated":list(map(str,M)),
             "finite_envelope_lower_formula_evaluations":bounds,
             "elapsed_seconds":time.perf_counter()-started,
             "scope":"Exactly defined physical-model zero is proved algebraically in round-008; finite decimal residuals are checks only. One model, no parameter search or time integration; no local-dashpot or engineering-record claim."}
    (HERE/"physical-topcut-zero.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({key:out[key] for key in ['zeta_star','zeta_new','H0_numeric_abs_residual','H1_numeric_abs','moment_upper_formula_evaluated','finite_envelope_lower_formula_evaluations','C0_13','elapsed_seconds']},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
