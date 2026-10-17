"""Close the failed single run without replay, parser repair, or new comparisons."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib, json

ROOT=Path.cwd()
ROLE=ROOT/'papers/damping-output-boundaries/research/roles/verification/maxwell-session004'
HERE=Path(__file__).resolve().parent
def record(p):
    b=p.read_bytes()
    return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(name,obj):(HERE/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

assert not (HERE/'validation.json').exists()
prior_path=ROLE/'R037-forward-midpoint-contract-review/validation.json'
assert record(prior_path)['sha256']=='47ef691b257a67137bee45ead48a78169540f284f2c9363759c435b544af3013'
prior=read(prior_path)
old=prior['frozen_R001_R036']+[{'run_file':str(prior_path.relative_to(ROLE)).replace('\\','/'),'sha256':record(prior_path)['sha256'],'outputs_verified':len(prior['outputs'])}]
total=0
for item in old:
    p=ROLE/item['run_file'];assert record(p)['sha256']==item['sha256']
    d=read(p);outputs=d.get('outputs',[d['report']] if 'report' in d else [])
    assert len(outputs)==item['outputs_verified']
    for out in outputs:assert record(Path(out['path']))==out
    total+=len(outputs)
assert len(old)==37 and total==127
pre=read(HERE/'pre_run_freeze.json')
assert all(record(Path(x['path']))==x for x in pre['sources'])
prediction=read(HERE/'prediction_freeze.json')
assert all(record(Path(x['path']))==x for x in prediction['small_outputs'])
assert prediction['code_sha256']==record(HERE/'independent_modal_newton.py')['sha256']
schema=read(HERE/'author_small_schema.json')
assert all(record(Path(x['path']))==x for x in schema['sources'])
failure=read(HERE/'failure.json');assert failure['context']['phase']=='author_small_comparison'
assert not (HERE/'author_comparison.json').exists() and not (HERE/'run_record.json').exists()
metric=read(HERE/'reference_metrics.json')
assert metric['nodes']==98305 and all(metric['u1_u2_maxerror_below_point1'].values())
events=read(HERE/'read_order.json')
assert [x['event'] for x in events]==['code_protocol_frozen_before_prediction','all98305_predictions_and_SHA_frozen','reference_hash_start','reference_D_N16384_only_decoded','independent_full_reference_statistics_saved']
assert all(events[i]['at']<=events[i+1]['at'] for i in range(len(events)-1))
at=datetime.now(timezone(timedelta(hours=8))).isoformat()
assert at<'2026-10-18T04:05:02+08:00'
checks={'at':at,'prior_records':37,'prior_small_outputs':127,'prior_records_and_outputs_unchanged':True,'four_pre_run_source_records_unchanged':True,'two_prediction_outputs_unchanged':True,'two_author_small_source_records_unchanged':True,'source_and_prediction_SHA_unchanged':True,'saved_event_order_passed':True,'full_98305_node_reference_metrics_saved':True,'u1_u2_original_point1_gates_passed':True,'failure_preserved':True,'solver_replayed_or_retuned':False,'post_failure_new_author_comparisons':False,'all_six_author_statistic_gates':'not_completed_not_accepted','all_twenty_author_snapshot_gates':'not_completed_not_accepted','overall_protocol':'STOPPED_INCOMPLETE','reference_NPZ_reopened_by_this_closure_script':False,'before_task_deadline':True}
write('closure_checks.json',checks)
outputs=[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json']
assert all(x['bytes']<100000 for x in outputs)
write('validation.json',{'review':'R038','session':'20261017-2109','started_at':'2026-10-18T03:53:02.390+08:00','frozen_at':at,'deadline':'2026-10-18T04:05:02+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','status':'STOPPED_INCOMPLETE','solver_exit_code':1,'mathematical_required_changes_in_completed_phase':0,'blocking_completion_issue':'UTF-8 BOM in author snapshot first header; failure preserved; no retry or further comparisons','full_protocol_accepted':False,'accepted_scope':'Only independently generated fine predictions, saved full reference metrics and discrete diagnostics; original .1 finite gates passed. Author consistency gates unaccepted.','frozen_prior_records_verified':len(old),'frozen_prior_small_outputs_verified':total,'frozen_R001_R037':old,'outputs':outputs,'output_count':len(outputs)})
print(json.dumps({'status':checks['overall_protocol'],'prior_records':len(old),'prior_outputs':total,'new_outputs':len(outputs),'validation':record(HERE/'validation.json'),'report':record(HERE/'report.md'),'checks':record(HERE/'closure_checks.json')},ensure_ascii=False))
