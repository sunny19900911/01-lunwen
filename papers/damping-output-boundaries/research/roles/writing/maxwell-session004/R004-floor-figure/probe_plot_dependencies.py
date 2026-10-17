"""Record local scientific-plot dependencies; never install or overwrite outputs."""
import argparse,datetime,hashlib,importlib.util,json,platform,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
if a.out.exists(): raise SystemExit('Refusing existing --out directory')
repo=a.repo.resolve(); sources=[(repo/'papers/damping-output-boundaries/research/roles/experiments/maxwell-session004/R005-floor-results/floor_three_metric_table_r005.csv','fc4ea0e6291be246e2c3c167176d09d2c06728cb51c34ccfd8a04c3ebee6cb2c'),(repo/'papers/damping-output-boundaries/research/roles/verification/maxwell-session004/楼层输出与控制位置独审-R009.md','eb8b86079c8fc0ff05d466c2889db08f3456f29313540ec14ac7c50ac441af1e')]
source_records=[]
for path,expected in sources:
 data=path.read_bytes();actual=hashlib.sha256(data).hexdigest()
 if actual!=expected:raise SystemExit('Source SHA mismatch: '+str(path))
 source_records.append({'repo_relative':path.relative_to(repo).as_posix(),'bytes':len(data),'sha256':actual})
packages={n:bool(importlib.util.find_spec(n)) for n in ['matplotlib','plotly','kaleido','numpy','PIL']}
a.out.mkdir(parents=True,exist_ok=False)
record={'recorded_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'status':'dependency_missing_limited_stop','python':sys.version,'executable':sys.executable,'packages':packages,'sources':source_records,'source_hashes_match':True,'plot_executed':False,'PNG_SVG_created':False,'numeric_normalization_QA_run':False,'no_install_or_download':True,'no_manuscript_or_source_changes':True,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'arguments':sys.argv[1:]}
(a.out/'dependency_record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(record,ensure_ascii=False))
