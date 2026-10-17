"""Exact functional boundary challenges, not ODE/mechanical realizations."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib

HERE=Path(__file__).resolve().parent
freeze=json.loads((HERE/'input-freeze.json').read_text(encoding='utf-8'))
for item in freeze['inputs']:
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256']
def peak(nodes):return max(abs(x) for x in nodes)
def decision(Uminus,Uplus,Zminus,Zplus,etaU=Q(0),etaC=Q(0),eps=Q(0)):
    assert 0<=Uminus<=Uplus and 0<=Zminus<=Zplus and min(etaU,etaC,eps)>=0
    delta=etaU+etaC+eps
    LU,HU=max(Q(0),Uminus-etaU),Uplus+etaU
    LD,HD=max(Q(0),Zminus-delta),Zplus+delta
    result='decrease' if HD<LU else 'increase' if LD>HU else 'inconclusive'
    return {'U':[str(LU),str(HU)],'D':[str(LD),str(HD)],'decision':result}
U=[Q(0),Q(1),Q(0)]  # Exact continuous PL functions on the common three-node grid.
cases=[]
for name,scale,eps,expected in [
    ('strict_decrease',Q(1,2),Q(1,4),'decrease'),
    ('strict_increase',Q(3,2),Q(1,4),'increase'),
    ('same_information_both_directions',Q(1),Q(1,4),'inconclusive'),
    ('upper_touches_reference',Q(3,4),Q(1,4),'inconclusive'),
    ('lower_touches_reference',Q(5,4),Q(1,4),'inconclusive')]:
    Z=[scale*x for x in U];out=decision(peak(U),peak(U),peak(Z),peak(Z),eps=eps)
    assert out['decision']==expected;cases.append({'name':name,**out})
eps=Q(1,4)
assert peak([(1-eps)*x for x in U])<peak(U)<peak([(1+eps)*x for x in U])
assert decision(Q(0),Q(0),Q(0),Q(0))['decision']=='inconclusive'
assert decision(Q(0),Q(0),Q(1),Q(1))['decision']=='increase'
assert decision(Q(1),Q(1),Q(1,2),Q(1,2),Q(1,10),Q(1,20),Q(1,20))['decision']=='decrease'
uh=[Q(0),Q(1),Q(1),Q(0)];ch=[Q(0),-Q(2,5),Q(3,20),Q(0)]
error=[Q(0),Q(1,10),-Q(1,10),Q(0)]
trueU=[a+e for a,e in zip(uh,error)];trueD=[a+c for a,c in zip(trueU,ch)]
zh=[a+c for a,c in zip(uh,ch)]
assert peak(trueD)<peak(trueU)
correct=decision(peak(uh),peak(uh),peak(zh),peak(zh),etaU=Q(1,10))
assert correct['decision']=='inconclusive'
assert peak(zh)>peak(uh)+Q(1,10)  # Omitting etaU from D would falsely label increase here.
phaseU=[Q(0),Q(1),Q(0),Q(0)];phaseD=[Q(0),Q(0),Q(1),Q(0)]
assert peak(phaseD)-peak(phaseU)==0 and peak([d-u for d,u in zip(phaseD,phaseU)])==1
M=Q(0);L=Q(2);h=Q(1);true_triangle_peak=Q(1)
assert M+L*h/2==true_triangle_peak and M<true_triangle_peak
result={'scope':'Exact functional/PL information-contract tests only; no physical realizability, ODE or engineering data claim.',
        'case_table':cases,'same_center_same_eps_admits_both_orders':True,
        'zero_reference_peak_cases':'passed','approximate_reference_and_contribution_errors':'passed',
        'shared_reference_error_false_increase_challenge':{'actual_U_peak':str(peak(trueU)),'actual_D_peak':str(peak(trueD)),'correct_interval_decision':correct},
        'different_peak_times_not_peak_of_difference':True,
        'hidden_between_node_triangle':{'node_peak':'0','true_peak':'1','certified_L':'2','gap':'1','upper_with_L_gap_half':'1'},
        'missing_56_remainder_bound':'unknown must not be replaced by zero; no numerical engineering verdict',
        'all_frozen_source_sha_unchanged':True}
(HERE/'checks.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(result,ensure_ascii=False,indent=2))
