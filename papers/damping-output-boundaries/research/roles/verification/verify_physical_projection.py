"""Small full-basis physical projection checks; synthetic shear models only."""
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent


def main():
    cases = [([1.,2.],[2.,5.]),([1.,2.,3.],[2.,5.,7.]),([2.,1.,4.,3.],[3.,5.,2.,7.])]
    rows = []
    max_error = 0.0
    for masses, stiffnesses in cases:
        m,k = np.array(masses),np.array(stiffnesses)
        n=len(m); b=np.ones(n); B=np.eye(n)-np.eye(n,k=-1)
        M=np.diag(m); K=B.T@np.diag(k)@B
        rootinv=np.diag(1/np.sqrt(m))
        lam,U=np.linalg.eigh(rootinv@K@rootinv)
        phi=rootinv@U
        Gamma=phi.T@M@b
        A=np.linalg.solve(M,K)
        case_rows=[]
        for kind in ("cut","net","global"):
            indices=range(n) if kind!="global" else [0]
            for j in indices:
                ell=k[j]*B[j] if kind=="cut" else K[:,j] if kind=="net" else K@b
                rho=(ell@phi)*Gamma
                moment_rows=[]
                for p in (-1,0,1,2):
                    modal=float(np.dot(lam**p,rho))
                    direct=float(ell@(np.linalg.matrix_power(A,p)@b))
                    error=abs(modal-direct)/max(1.,abs(direct))
                    max_error=max(max_error,error)
                    assert error<1e-10
                    moment_rows.append({"p":p,"modal":modal,"physical":direct,"relative_error":error})
                if kind=="cut":
                    assert abs(moment_rows[0]["physical"]-sum(m[j:]))<1e-10
                elif kind=="net":
                    assert abs(moment_rows[0]["physical"]-m[j])<1e-10
                else:
                    assert np.all(rho>=-1e-12)
                    assert np.max(abs(rho-lam*Gamma**2))<1e-10
                case_rows.append({"output":kind,"floor_1_based":j+1 if kind!="global" else None,"rho":rho.tolist(),"moments":moment_rows})
        rows.append({"mass":masses,"story_stiffness":stiffnesses,"lambda":lam.tolist(),"outputs":case_rows})
    def exact_moments(lambdas,residues):
        return {str(p):str(sum(F(r)*F(l)**p for l,r in zip(lambdas,residues))) for p in (-1,0,1)}
    c008=exact_moments([1,4,9],[1,-2,1])
    e004=exact_moments([1,9],[1,F(-89,10)])
    assert c008=={"-1":"11/18","0":"0","1":"2"}
    assert e004=={"-1":"1/90","0":"-79/10","1":"-791/10"}
    out={
        "run_time_utc":datetime.now(timezone.utc).isoformat(),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "numpy":np.__version__,"input_convention":"M u_ddot+C u_dot+K u=M b f, b=ones, f=-ground_acceleration",
        "cases":rows,"max_normalized_moment_discrepancy":max_error,
        "C008_exact_moments_at_scale_1":c008,"EEXP004_exact_moments_at_scale_1":e004,
        "scope":"Three synthetic full-basis checks supplement exact projection/sign derivations. No ETABS, raw data, large search, or approximate modal-fit interpretation."
    }
    (HERE/"physical-projection-audit.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(rows),"max_moment_error":max_error,"C008":c008,"E004":e004}))


if __name__=="__main__":main()
