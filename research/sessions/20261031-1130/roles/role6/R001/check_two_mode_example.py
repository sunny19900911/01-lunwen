"""One fixed two-story harmonic example. No fitting, ODE or frequency scan."""
from pathlib import Path
import json
import numpy as np
K=np.array([[2.,-1.],[-1.,1.]])
lam,phi=np.linalg.eigh(K);w=np.sqrt(lam)
gamma=phi.T@np.ones(2);B=gamma**2;Omega=np.sqrt(2.)
rows=[]
for zeta in [.05,.08]:
    modal=-B*lam/(lam-Omega**2+2j*zeta*w*Omega)
    U=float(np.sum(abs(modal)));P=float(abs(np.sum(modal)))
    damping=phi@np.diag(2*zeta*w)@phi.T
    direct=np.linalg.solve(K-Omega**2*np.eye(2)+1j*Omega*damping,-np.ones(2))[0]
    exact_P2=(72/5)*zeta**2/(1+56*zeta**2+64*zeta**4)
    assert abs(direct-sum(modal))<1e-12 and abs(P*P-exact_P2)<1e-14
    rows.append({"zeta":zeta,"modal_abs_peak_N":abs(modal).tolist(),
        "modal_complex_N":[[float(x.real),float(x.imag)] for x in modal],
        "U_N":U,"P_N":P,"C":P/U,
        "direct_matrix_error_N":float(abs(direct-sum(modal))),
        "closed_form_P_squared":exact_P2})
assert all(b<a for a,b in zip(rows[0]["modal_abs_peak_N"],rows[1]["modal_abs_peak_N"]))
assert rows[1]["U_N"]<rows[0]["U_N"] and rows[1]["P_N"]>rows[0]["P_N"]
result={"scope":"minimal two-modal steady harmonic counterexample, physical first-story elastic shear; not finite-zero-initial earthquake claim",
    "M_kg":np.eye(2).tolist(),"K_N_per_m":K.tolist(),"story_stiffness_N_per_m":[1.,1.],
    "omega_rad_s":w.tolist(),"input":"ag=sin(sqrt(2)*t) m/s2, steady state","Omega_rad_s":Omega,
    "B_base_kg":B.tolist(),"rows":rows,
    "U8_over_U5":rows[1]["U_N"]/rows[0]["U_N"],
    "C8_over_C5":rows[1]["C"]/rows[0]["C"],
    "P8_over_P5":rows[1]["P_N"]/rows[0]["P_N"],
    "checks":"two independent algebraic routes; closed form; both modal peaks decrease; no fitting or ODE"}
with Path(__file__).with_name("two-mode-counterexample.json").open("x",encoding="utf-8") as f:
    json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({k:result[k] for k in ["U8_over_U5","C8_over_C5","P8_over_P5"]}))
