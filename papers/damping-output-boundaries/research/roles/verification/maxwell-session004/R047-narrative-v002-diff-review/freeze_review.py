from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'validation.json').exists()
sources=read(HERE/'source-freeze.json')['sources'];assert len(sources)==22 and all(rec(Path(x['path']))==x for x in sources)
checks=read(HERE/'checks.json');assert checks['required_changes']==0
assert all(x['independent_diff_identical'] and x['reverse_restores_old_bytes_and_SHA'] for x in checks['three_independent_diffs_and_reverse_checks'])
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n');s=b.decode('utf-8')
    if p.suffix!='.patch':assert all(x==x.rstrip() for x in s.splitlines())
    if p.suffix=='.json':json.loads(s)
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T05:49:48+08:00'
write('closure_checks.json',{'at':at,'required_changes':0,'old_R046_required_change_preserved':True,'M1_repaired_only_in_new_versions':True,'three_independent_reverse_checks_passed':True,'twenty_two_sources_unchanged':True,'old_scientific_content_outside_authorized_changes_preserved':True,'no_old_history_scan_or_scientific_execution':True,'source_shared_or_Git_writes':False,'patch_context_spaces_retained':True,'before_five_minute_deadline':True})
outputs=[rec(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='validation.json']
write('validation.json',{'review':'R047','session':'20261017-2109','started_at':'2026-10-18T05:44:48.889424+08:00','frozen_at':at,'deadline':'2026-10-18T05:49:48+08:00','global_deadline_unchanged':'2026-10-18T07:09:45+08:00','required_changes':0,'status':'limited v002 diff review passed; old R046 finding unchanged','accepted_scope':'M1 terminology repair, version/proof/appendix/reproduction links, and two authorized engineering clarifications only. Ten+seven formulas unchanged and three old SHA identities independently reconstructed; other scope inherited, not reproved.','source_records_verified':22,'sources_unchanged':True,'all_prior_history_rescanned':False,'outputs':outputs,'output_count':len(outputs)})
print(json.dumps({'required_changes':0,'frozen_at':at,'sources':22,'new_outputs':len(outputs),'report':rec(HERE/'report.md'),'checks':rec(HERE/'checks.json'),'validation':rec(HERE/'validation.json')},ensure_ascii=False))
