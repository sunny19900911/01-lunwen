"""Exact algebra checks for the frozen L1 family; no ODE or arrays."""
from pathlib import Path
from fractions import Fraction as Q
import json
import hashlib

HERE=Path(__file__).resolve().parent
freeze=json.loads((HERE/'input-freeze.json').read_text(encoding='utf-8'))
for item in freeze['inputs']:
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['sha256']
adoption=json.loads(Path(freeze['inputs'][3]['path']).read_text(encoding='utf-8'))
binary=adoption['bound_binary64_hex']
av=Q(float.fromhex(binary['early_upper_candidate']))
at=Q(float.fromhex(binary['tail_upper_candidate']))
bv=Q(float.fromhex(binary['fixed_T_lower_candidate']))
assert max(av,at)<Q('1.325') and bv>Q('8.809')
S=Q(1001,1002); radius_squared=8*S; cap=Q('2.83')
assert radius_squared<8<cap*cap
upper=Q('1.325')+cap; lower=Q('8.809')-cap; gap=lower-upper
assert upper==Q('4.155') and lower==Q('5.979') and gap==Q('1.824')
assert Q(2,40)==Q(5,100)
result={'scope':'Exact Fraction/hex and scalar algebra only, not new numerical dynamics.',
        'nominal_upper_direction':True,'nominal_fixed_T_lower_direction':True,
        'S_K':str(S),'perturbation_radius_squared_at_area2':str(radius_squared),
        'sqrt8_lt_2.83_verified_by_squares':True,'safe_error_cap':str(cap),
        'A_fulltime_upper':str(upper),'B_fixed_T_lower':str(lower),'fulltime_gap_lower':str(gap),
        'thresholds_are_strict':True,'base_abs_area':40,'disturbance_abs_area_budget':2,
        'ratio_is_L1_area_only':str(Q(2,40)),
        'nominal_machine_contract':adoption['machine_contract'],
        'all_frozen_source_sha_unchanged':True}
(HERE/'checks.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(result,ensure_ascii=False,indent=2))
