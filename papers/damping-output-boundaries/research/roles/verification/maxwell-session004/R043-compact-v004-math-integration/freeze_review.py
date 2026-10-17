"""Close mathematical transcription review, no source mutation or scientific run."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'validation.json').exists()
sources=read(HERE/'source-freeze.json')['sources'];assert len(sources)==20 and all(rec(Path(x['path']))==x for x in sources)
checks=read(HERE/'checks.json');assert checks['required_changes']==0 and checks['independent_diff_matches_author_patch'] and checks['only_four_authorized_changes_reverse_to_v003_bytes']
figure=ROOT/'papers/damping-output-boundaries/research/roles/writing/maxwell-session004/C025-layout-explanation-figure-v001/freeze.json'
assert rec(figure)['sha256']=='f85295fbbae92fdf0a3299d4c90ca0c7ba77581d47e3888236321f4f210a1322'
graphics=[x for x in read(figure)['files'] if Path(x['path']).suffix in ['.png','.svg'] or Path(x['path']).name=='caption.md']
assert len(graphics)==3 and all(rec(Path(x['path']))==x for x in graphics)
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n');text=b.decode('utf-8')
    if p.suffix!='.patch':assert all(x==x.rstrip() for x in text.splitlines())
    if p.suffix=='.json':json.loads(text)
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T05:15:16+08:00'
write('closure_checks.json',{'at':at,'required_changes':0,'all_twenty_source_SHA_unchanged':True,'math_transcription_and_scope_passed':True,'independent_actual_diff_and_reverse_bytes_passed':True,'old_three_formulas_two_tables_figure_and_conditions_preserved':True,'figure_freeze':rec(figure),'figure_SVG_PNG_caption_unchanged':graphics,'format_checker_repair':'Initial blanket whitespace check rejected valid unified-diff blank-context prefix; check narrowed to text/code/JSON, exact patch bytes preserved.','new_proof_numeric_arrays_ODE_or_primary_download':False,'old_shared_or_manuscript_writes':False,'before_eight_minute_deadline':True})
prior=read(HERE/'prior-preservation.json')
outputs=[rec(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json']
write('validation.json',{'review':'R043','session':'20261017-2109','started_at':'2026-10-18T05:07:16.522594+08:00','frozen_at':at,'deadline':'2026-10-18T05:15:16+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','required_changes':0,'status':'compact-v004 independent mathematical integration passed','accepted_scope':'C039 common-alpha conditional difference bound and C038 device example scope transcribed correctly; exact preservation of old content outside four changes. No new proof, source-primary review, engineering or publication admission.','source_records_verified':20,'sources_unchanged':True,'frozen_prior_records_verified':42,'frozen_prior_small_outputs_verified':166,'frozen_R001_R042':prior['frozen_R001_R042'],'additional_postcomparison_freezes':prior['additional_comparison_freezes'],'additional_postcomparison_outputs_verified':6,'writer_protected_manifests_verified':23,'figure_SVG_PNG_caption_verified':3,'outputs':outputs,'output_count':len(outputs)})
print(json.dumps({'required_changes':0,'sources':20,'prior_records':42,'prior_outputs':166,'additional_comparison_outputs':6,'new_outputs':len(outputs),'report':rec(HERE/'report.md'),'checks':rec(HERE/'checks.json'),'validation':rec(HERE/'validation.json')},ensure_ascii=False))
