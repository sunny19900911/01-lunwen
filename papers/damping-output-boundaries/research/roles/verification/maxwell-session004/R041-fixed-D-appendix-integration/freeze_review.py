"""Close static integration review without altering any source."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
def record(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'validation.json').exists()
sources=read(HERE/'source-freeze.json')['sources']
assert len(sources)==14 and all(record(Path(x['path']))==x for x in sources)
checks=read(HERE/'checks.json')
assert checks['required_changes']==0
assert all(checks['manual_semantic_checks'].values()) and all(checks['automated_static_checks'].values())
assert not checks['in_progress_R025_example_read'] and not checks['new_proof_numerics_trajectories_arrays_or_parameter_sweep']
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n') and not b.startswith(b'\xef\xbb\xbf')
    text=b.decode('utf-8');assert all(line==line.rstrip() for line in text.splitlines())
    if p.suffix=='.json':json.loads(text)
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T04:55:04+08:00'
write('closure_checks.json',{'at':at,'required_changes':0,'sources_unchanged':True,'static_checks_passed':True,'started_at':'2026-10-18T04:47:04.593875+08:00','deadline':'2026-10-18T04:55:04+08:00','within_eight_minutes':True,'new_example_not_read':True,'no_new_mathematics_or_numerics':True,'source_or_shared_writes':False})
outputs=[record(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json']
prior=read(HERE/'prior-preservation.json')
write('validation.json',{'review':'R041','session':'20261017-2109','started_at':'2026-10-18T04:47:04.593875+08:00','frozen_at':at,'deadline':'2026-10-18T04:55:04+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','required_changes':0,'status':'independent static appendix integration audit passed','accepted_scope':'C038/R029/R040 transcription, self-contained definitions, seven equations, six-row domain table, inverse domains and admissibility/scope retained. No new proof/numerics or publication/engineering admission.','source_records_verified':14,'sources_unchanged':True,'frozen_prior_records_verified':40,'frozen_prior_small_outputs_verified':154,'frozen_R001_R040':prior['frozen_R001_R040'],'additional_R040_postcomparison_outputs_verified':3,'additional_R040_postcomparison_freeze':prior['R040_comparison_freeze'],'writer_old_manifests_verified':22,'new_R025_example_read':False,'outputs':outputs,'output_count':len(outputs)})
print(json.dumps({'required_changes':0,'sources':len(sources),'prior_records':40,'prior_main_outputs':154,'additional_R040_comparison_outputs':3,'new_outputs':len(outputs),'report':record(HERE/'report.md'),'checks':record(HERE/'checks.json'),'validation':record(HERE/'validation.json')},ensure_ascii=False))
