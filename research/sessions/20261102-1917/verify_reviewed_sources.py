"""Read-only hash gate for frozen small P06 artifacts and original manuscripts."""
from pathlib import Path
import json,hashlib,ast,csv
S=Path(__file__).resolve().parent;R=S.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
manifests=['roles/role4/R001/delivery-manifest.json','roles/role4/R001/delivery-manifest-v002.json','roles/role2/R002/delivery-manifest.json']
for name in manifests:
 m=S/name;d=json.loads(m.read_text(encoding='utf-8'))
 for q in d.get('files',[])+d.get('additive_files',[]):
  p=Path(q['path']);assert p.is_relative_to(S)
  assert 'local-cache' not in p.parts and p.stat().st_size<1048576
  assert sha(p)==q['sha256'],p
  if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
  elif p.suffix=='.json':json.loads(p.read_text(encoding='utf-8'))
  elif p.suffix=='.csv':
   with p.open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f))
   assert a and all(len(row)==len(a[0]) for row in a)
  records.append({'path':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':q['sha256']})
for name,expected in [('jgjg-session011-v004.md','c30cbbccecc21be395ad9cf55de3f842f806cfea8372b72d180d240a3e532b7a'),('jgjg-session011-论文审阅稿-v004-排版稿.docx','2844e66450e65ec489e33f3e1c1db82f9abab5800aa52c363549bb20cfd0f998'),('p06-engineering-session022-v001.md','70c831f0a01b19476bc090d85f874468ecffcef5d612379e2c56d0a22bf96e24')]:
 p=R/'papers/damping-output-boundaries/manuscript'/name;assert sha(p)==expected
out=S/'root-R002-reviewed-small-source-check.json'
assert not out.exists()
out.write_text(json.dumps({'frozen_files_verified':len(records),'records':records,'original_P06_and_v001_unchanged':True,'no_production_script_executed':True,'no_trajectories_read':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frozen_files_verified':len(records),'original_P06_and_v001_unchanged':True}))
