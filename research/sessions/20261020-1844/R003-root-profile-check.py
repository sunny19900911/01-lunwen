from pathlib import Path
import csv,json,statistics,hashlib,xml.etree.ElementTree as ET,datetime
S=Path(__file__).resolve().parent; D=S/'roles/role4'
def rows(p):return list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
six=rows(D/'R002-common-six-main-axis-72.csv');all14=rows(D/'R002-all14-main-axis-168.csv')
stats=rows(D/'R004-story-axis-statistics-48.csv'); errors=[];checked=0
for r in stats:
 source=six if r['scope']=='common_six' else all14
 vals=[float(x['peak_reduction_percent']) for x in source if x['Story']==r['Story'] and x['Axis']==r['Axis']]
 target=[min(vals),statistics.median(vals),max(vals),max(vals)-min(vals)]
 for key,v in zip(['minimum_reduction_percent','median_reduction_percent','maximum_reduction_percent','range_percentage_points'],target):
  if abs(float(r[key])-v)>1e-10:errors.append([r['scope'],r['Story'],r['Axis'],key])
  checked+=1
 assert int(r['case_count'])==len(vals)
for p in D.glob('R004*.svg'):ET.parse(p)
manifest=json.loads((D/'R004-delivery-manifest.json').read_text('utf-8-sig'))
for item in manifest['files']:
 p=Path(item['path']); assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],p
assert not errors
out={'checked_at':datetime.datetime.now().astimezone().isoformat(),'statistics_rows':len(stats),'independent_numeric_checks':checked,'errors':errors,'svg_xml_valid':True,'role4_R004_manifest_ok':True,'scope':'Independent regrouping of frozen peak CSVs; no new trajectory or modal identification'}
(S/'R003-root-profile-check.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(out,ensure_ascii=False))
