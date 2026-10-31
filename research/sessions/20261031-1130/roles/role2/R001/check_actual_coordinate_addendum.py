from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
import numpy as np
O=Path(__file__).parent;R=O.parents[5]
now=lambda:datetime.now(timezone(timedelta(hours=8)))
DEADLINE=datetime.fromisoformat('2026-10-31T11:51:14+08:00')
assert now()<DEADLINE
Phi=np.array([[1.,1.],[1.,-1.]])/np.sqrt(2)
M=np.eye(2);K=np.array([[3.,-1.],[-1.,3.]])
Cmodal=np.array([[.6,.1],[.1,.7]]);C=Phi@Cmodal@Phi.T
r=np.ones(2);lam=np.array([2.,4.]);Gamma=Phi.T@M@r
assert np.allclose(Phi.T@M@Phi,np.eye(2))
assert np.linalg.norm(K@Phi-M@Phi@np.diag(lam))<2e-15
assert Gamma[1]==0 and np.min(np.linalg.eigvalsh(C))>0
# Instantaneous algebra only: no ODE/time-history integration.
q=np.zeros(2);velocity=np.array([1.,0.]);ag=0.
acceleration=-Cmodal@velocity-lam*q-Gamma*ag
assert np.isclose(acceleration[1],-.1)
# For zero initial q, qdot and constant ag=1 locally, differentiate the modal equations once.
initial_acceleration=-Gamma
initial_jerk=-Cmodal@initial_acceleration
assert np.isclose(initial_jerk[1],.1*np.sqrt(2))
# A separate admissible modal-coordinate snapshot shows that B=0 does not annul the actual elastic output.
a=np.array([1.,0.]);L=float(a@M@Phi[:,1]);B=float(Gamma[1]*L);qr=1.
actual=float(a@K@Phi[:,1]*qr);by_L=float(lam[1]*L*qr)
assert B==0 and np.isclose(actual,by_L) and actual>2.8
rows=[{'mode':'antisymmetric','Gamma':float(Gamma[1]),'L_output':L,'B_GammaL':B,'actual_q_snapshot':qr,'actual_elastic_output':actual,'omega2_L_q':by_L,'coupled_acceleration_at_qdot_symmetric_1':float(acceleration[1]),'zero_initial_constant_input_initial_jerk':float(initial_jerk[1])}]
with (O/'actual-coordinate-coupling-1.csv').open('x',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
source=R/'research/sessions/20261031-1130/plan-theory-addendum-v002.md'
result={'completed':now().isoformat(),'same_original_deadline':DEADLINE.isoformat(),'within_original_observed_budget':now()<DEADLINE,'M':M.tolist(),'K':K.tolist(),'C_physical':C.tolist(),'C_modal':Cmodal.tolist(),'Phi_columns':Phi.tolist(),'Gamma':Gamma.tolist(),'lambda':lam.tolist(),'initial_acceleration_constant_ag1':initial_acceleration.tolist(),'initial_jerk_constant_ag1':initial_jerk.tolist(),'operator':'a=(1,0), output=a^T K u includes intertower connector; not labelled single-tower ground-spring shear','source_addendum_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'actual_FNA_coordinates_recovered':False,'time_integration':False,'new_fit':False,'original_frozen_files_modified':False}
with (O/'actual-coordinate-addendum-checks.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False))
