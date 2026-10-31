from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,ast
import numpy as np
O=Path(__file__).parent;R=O.parents[5]
now=lambda:datetime.now(timezone(timedelta(hours=8)))
assert now()<datetime.fromisoformat('2026-10-31T12:57:37+08:00')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
failed=O/'all-table-algebra-checks.failed-json.txt'
text=failed.read_text(encoding='utf-8')
prefix=text.rsplit('"opposite_sum_sign_anchors"',1)[0].rstrip().rstrip(',')+'\n}'
done=json.loads(prefix)
assert done['mode_points']==21600 and done['scalar_formula_checks']==156024
anchors=rows(O/'all72-anchor-formula-audit.csv');components=rows(O/'all432-component-group-audit.csv')
assert len(anchors)==72 and len(components)==432
assert all(x['same_time_and_peak_loss_formula_pass']=='True' for x in anchors)
assert all(x['formula_group_sum_pass']=='True' for x in components)
source=rows(R/'research/sessions/20261031-1130/roles/role4/R008/all12-threewaves-two-native-anchors-symmetric-change-72.csv')
done.update({'metadata_recovered_at':now().isoformat(),'opposite_sum_sign_anchors':int(sum(float(x['sign_reversal_correction_kN'])>0 for x in anchors)),'zero_old_sign_anchors':int(sum(int(x['sigma5'])==0 for x in anchors)),'negative_projected_waveform_anchors':int(sum(float(x['old_direction_waveform_weakening_kN'])<0 for x in source)),'fixed_scalar_zero_and_flip_policy_checks':True,'must_count':0,'scope':'all scientific assertions completed before final JSON failure; recovery uses preserved prefix and already completed audit CSVs, no state recomputation','foreign_code_imported':False,'new_ODE_or_physical_counterexample_scan':False})
assert json.loads(json.dumps({'counter':int(np.int64(0))}))=={'counter':0}
ast.parse((O/'check_same_time_symmetric.py').read_text(encoding='utf-8'))
with (O/'all-table-algebra-checks-v002.json').open('x',encoding='utf-8') as f:json.dump(done,f,ensure_ascii=False,indent=2)
note={'failure':'TypeError: Object of type int64 is not JSON serializable in final metadata only','scientific_checks_completed_before_failure':True,'failed_metadata_preserved_as':failed.name,'failed_metadata_sha256':sha(failed),'executed_v001_script_sha256':sha(O/'check_same_time_symmetric-executed-v001.py'),'fixed_primary_script_sha256':sha(O/'check_same_time_symmetric.py'),'fix':'cast NumPy boolean counters to Python int','counter_serialization_test_pass':True,'source_parse_pass':True,'large_state_recomputation':False,'recovered_summary':'all-table-algebra-checks-v002.json','completed':now().isoformat()}
with (O/'execution-note.json').open('x',encoding='utf-8') as f:json.dump(note,f,ensure_ascii=False,indent=2)
print(json.dumps(done,ensure_ascii=False))
