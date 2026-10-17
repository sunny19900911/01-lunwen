"""Finite static comparison closure; intentionally no prior-package rescan."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent;PARENT=HERE.parent
AUTHOR=ROOT/'papers/damping-output-boundaries/research/roles/ideation/maxwell-session004/R032-mass-participation-local-corollary'
def rec(p):
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(n,o):(HERE/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert not (HERE/'comparison-freeze.json').exists()
assert rec(AUTHOR/'report.md')['sha256']=='b9bc2371ed2600ff0faece2f1280d8f201362bf2b20e99158ba5b9a52c127d6a'
assert rec(PARENT/'validation.json')['sha256']=='252e903ce853260691973d6d3949098b23861f66d6269d56b114b70baf9ae2f0'
original=read(PARENT/'validation.json');assert len(original['outputs'])==6
assert all(rec(Path(x['path']))==x for x in original['outputs'])
assert all(rec(Path(x['path']))==x for x in read(PARENT/'source-freeze.json')['sources'])
manifest=read(AUTHOR/'artifact-manifest.json');assert len(manifest['artifacts'])==7
for x in manifest['artifacts']:
    actual=rec(AUTHOR/x['file']);assert actual['bytes']==x['bytes'] and actual['sha256']==x['sha256']
at=datetime.now(timezone(timedelta(hours=8))).isoformat();assert at<'2026-10-18T05:21:06+08:00'
write('comparison.json',{'at':at,'first_author_report_read_at':'2026-10-18T05:18:38+08:00','required_changes':0,'mathematically_equivalent':True,'frequencies':'omega_plus=1; omega_minus=sqrt(3)','quantifiers_fixed_witness_relative_output_and_peak_scalar_distinction_passed':True,'author_seven_manifest_outputs_verified':True,'author_identity_records':[rec(AUTHOR/n) for n in ['report.md','artifact-manifest.json','validation.json']],'original_independent_six_outputs_and_six_sources_unchanged':True,'prior_old_packages_rescanned':False,'new_proof_numerics_histories_arrays_NPZ_ODE_data_or_literature':False})
for p in HERE.iterdir():
    if not p.is_file():continue
    b=p.read_bytes();assert b'\r' not in b and b.endswith(b'\n');s=b.decode('utf-8');assert all(x==x.rstrip() for x in s.splitlines())
    if p.suffix=='.json':json.loads(s)
write('comparison-freeze.json',{'at':at,'deadline':'2026-10-18T05:21:06+08:00','required_changes':0,'independent_validation':rec(PARENT/'validation.json'),'outputs':[rec(p) for p in sorted(HERE.iterdir()) if p.is_file()]})
print(json.dumps({'required_changes':0,'report':rec(HERE/'report.md'),'record':rec(HERE/'comparison.json'),'freeze':rec(HERE/'comparison-freeze.json')},ensure_ascii=False))
