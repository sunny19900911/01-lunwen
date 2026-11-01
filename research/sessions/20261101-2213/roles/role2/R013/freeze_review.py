from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((O/'input-freeze.json').read_text(encoding='utf-8'))
for d in freeze['files']:
    p=Path(d['path']); assert p.stat().st_size==d['bytes'] and sha(p)==d['sha256']
check=json.loads((O/'scalar-and-structure-checks.json').read_text(encoding='utf-8'))
assert check['scalar_fields_checked']==149 and check['table_sequence']==list(range(1,14))
report=(O/'final-review-v009-and-S1.md').read_text(encoding='utf-8')
assert '�' not in report and 'must 0项；should 2项；optional 1项' in report
for line in report.splitlines():
    if line.startswith('|'):assert len(line.strip('|').split('|'))==3,line
now=datetime.now(timezone(timedelta(hours=8))); start=datetime.fromisoformat(freeze['actual_start'])
findings={'must':[],
 'should':[{'id':'S-01','file':'v009','lines':[7,440],'issue':'explicitly scope 6/7 reject and 8/10 recompute to maximum-input-peak envelope objective'},
           {'id':'S-02','file':'S1','lines':[215,288,292],'issue':'remove historical pending-values/evaluation-stage wording and label two core versus four total model-input groups'}],
 'optional':[{'id':'O-01','file':'v009','lines':[145],'issue':'explicitly name SHW3X Story5 in modal-own-peak example'}],
 'exact_replacements':'final-review-v009-and-S1.md','author_files_modified':False,'new_scientific_production':False}
with (O/'findings.json').open('x',encoding='utf-8') as f:json.dump(findings,f,ensure_ascii=False,indent=2)
m={'task':'session021-role2-R013','actual_start':start.isoformat(),'actual_freeze':now.isoformat(),
 'elapsed_seconds':(now-start).total_seconds(),'within12min':(now-start).total_seconds()<=720,
 'within15min':(now-start).total_seconds()<=900,'must':0,'should':2,'optional':1,
 'full_read_main_lines':451,'full_read_S1_lines':296,'scalar_fields_checked':149,
 'author_input_hashes_unchanged':True,'author_files_modified':False,
 'new_ODE_fits_models_searches':0,'original_response_arrays_reread':False,
 'scope':'one final review of specified frozen v009/S1; no approval of future changes',
 'files':[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']}
with (O/'delivery-manifest.json').open('x',encoding='utf-8') as f:json.dump(m,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in m.items() if k!='files'},ensure_ascii=False,indent=2));print('manifest_sha256',sha(O/'delivery-manifest.json'))
