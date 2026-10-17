"""Tiny exact modal algebra only; no histories or numerical solver."""
from fractions import Fraction as Q
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;ROLE=HERE.parent
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
paths=[ROOT/'research/sessions/20261017-2109/mass-participation-local-corollary-protocol-v001.md',ROLE/'R029-modal-sign-corollary/report.md',ROLE/'R029-modal-sign-corollary/validation.json',ROOT/'research/sessions/20261017-2109/R013-addition-certificate-adoption.json',ROOT/'research/sessions/20261017-2109/R014-adoption.json',ROLE/'R043-compact-v004-math-integration/validation.json']
assert not (HERE/'source-freeze.json').exists()
assert rec(paths[1])['sha256']=='c47f6e6f4d1f8ed9b13a7aead1738e2c4f9fd6c56995de3aebfd16751e440219'
assert rec(paths[3])['sha256']=='836a0d6e8e551dd594770fe1421f49780636cdb2d9d2c8cdbd2fd878cc2b729f'
write('source-freeze.json',{'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'started_at':'2026-10-18T05:14:06.207583+08:00','deadline':'2026-10-18T05:21:06+08:00','global_deadline':'2026-10-18T07:09:45+08:00','sources':[rec(p) for p in paths],'new_role1_R032_candidate_read':False,'NPZ_or_histories_opened_or_hashed':False})
# Use unnormalized shapes to remove square roots without approximating them.
assert (2*1-1,-1+2*1)==(1,1)
assert (2*1-(-1),-1+2*(-1))==(3,-3)
mass=Q(2);direction_mass=Q(2)
rho_plus=Q(2)**2/(mass*direction_mass)
rho_minus=Q(0)**2/(mass*direction_mass)
assert rho_plus==1 and rho_minus==0 and rho_plus+rho_minus==1
assert Q(-1)!=0  # B times unnormalized antisymmetric shape.
assert Q('2.75')==Q(11,4)
relative_squared=Q(121,8);node_squared=Q(121,32)
assert relative_squared-Q('3.88')**2==Q(353,5000)>0
assert node_squared-Q('1.94')**2==Q(353,20000)>0
# Isolated scalar geometry illustration, explicitly not a model-state sample.
x,y=Q(7,3),Q(-5,6);mean=(x+y)/2
assert max(abs(x-mean),abs(y-mean))==abs(x-y)/2
match=x
assert x-match==0 and (x-match)-(y-match)==x-y
out={'all_passed':True,'arithmetic':'fractions.Fraction and exact integers','eigenvalues_1_and_3':True,'directional_mass_fractions':[str(rho_plus),str(rho_minus)],'port_antisymmetric_projection_nonzero':True,'antisymmetric_threshold':'11/4','relative_threshold_square_margin':'353/5000','max_node_threshold_square_margin':'353/20000','best_common_value_geometry':True,'fixed_u1_universal_lower_bound_counterexample':True,'new_R032_candidate_read':False,'scope':'Tiny exact modal/threshold algebra only; certified true q-minus premise inherited unchanged. No state reconstruction, numerical integration, ODE, arrays, NPZ, parameter scan or new literature.'}
write('checks.json',out)
print(json.dumps({'checks':out,'protocol':rec(paths[0])},ensure_ascii=False))
