"""Small exact linear-algebra identities only; no ODE or engineering data."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib

HERE=Path(__file__).resolve().parent
freeze=json.loads((HERE/'input-freeze.json').read_text(encoding='utf-8'))
for item in freeze['inputs']:
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256']
def dot(a,b):return sum((x*y for x,y in zip(a,b)),Q(0))
def mv(A,x):return [dot(row,x) for row in A]
M=[[Q(2),Q(0)],[Q(0),Q(2)]];K=[[Q(5),-Q(3)],[-Q(3),Q(5)]]
C=[[Q(9,20),-Q(3,20)],[-Q(3,20),Q(9,20)]]
shapes=[[Q(1),Q(1)],[Q(2),-Q(2)]];omega2=[Q(1),Q(4)]
ell=[Q(1),-Q(2)];ports=[[-Q(1),Q(1)],[Q(1),Q(0)]];forces=[Q(2),-Q(3)]
coefficients=[];masses=[];damping=[]
for psi,w2 in zip(shapes,omega2):
    mass=dot(psi,mv(M,psi));masses.append(mass)
    assert mv(K,psi)==[w2*x for x in mv(M,psi)]
    damping.append(dot(psi,mv(C,psi))/mass)
    row=[dot(ell,psi)*dot(B,psi)/mass for B in ports];coefficients.append(row)
    for scale in [-Q(5,2),Q(7,3),-Q(1)]:
        scaled=[scale*x for x in psi];scaled_mass=dot(scaled,mv(M,scaled))
        assert [dot(ell,scaled)*dot(B,scaled)/scaled_mass for B in ports]==row
for s in [Q(1,2),Q(1),Q(3)]:
    A=[[M[i][j]*s*s+C[i][j]*s+K[i][j] for j in range(2)] for i in range(2)]
    load=[-sum(ports[d][i]*forces[d] for d in range(2)) for i in range(2)]
    determinant=A[0][0]*A[1][1]-A[0][1]*A[1][0]
    response=[(A[1][1]*load[0]-A[0][1]*load[1])/determinant,
              (-A[1][0]*load[0]+A[0][0]*load[1])/determinant]
    modal=-sum(coefficients[j][d]*forces[d]/(s*s+damping[j]*s+omega2[j]) for j in range(2) for d in range(2))
    assert dot(ell,response)==modal
for B,F in zip(ports,forces):
    assert [x*F for x in B]==[(-x)*(-F) for x in B]
uD,u0,ke,force=Q(7,3),-Q(1,4),Q(2),Q(5)
residual=force-ke*uD
assert -residual-ke*u0==-force+ke*(uD-u0)
assert ke*uD!=0  # Missing this correction would not be the same equation.
all_pairs={(j,d) for j in range(3) for d in range(4)};ret={0,2};known={0,1}
partial={(j,d) for j in ret for d in known}
tail_modes={(j,d) for j,d in all_pairs if j not in ret}
missing_devices={(j,d) for j,d in all_pairs if j in ret and d not in known}
assert not (partial&tail_modes or partial&missing_devices or tail_modes&missing_devices)
assert partial|tail_modes|missing_devices==all_pairs
result={'scope':'Exact synthetic algebra only; no ODE, real modal constants or force histories.',
 'direct_vs_complete_modal_resolvent_rational_s_cases':3,'raw_modal_masses':[str(x) for x in masses],
 'rescaling_and_sign_invariance':True,'paired_port_force_sign_invariance':True,
 'FNA_reference_correction_identity':True,'missing_pair_partition_disjoint_complete':True,
 'current_complete_force_subset':32,'protocol_total_devices':88,'missing_device_count':88-32,
 'engineering_reconstruction_or_response_certified':False,'frozen_source_sha_unchanged':True}
(HERE/'checks.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(result,ensure_ascii=False,indent=2))
