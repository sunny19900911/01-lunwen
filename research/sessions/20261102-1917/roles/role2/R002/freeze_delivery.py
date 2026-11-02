from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[2]/'roles/role4/R001';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ind=json.loads((O/'independent-selections-before-comparison.json').read_text(encoding='utf-8'))
assert sha(Path(ind['input']['path']))==ind['input']['sha256']
c=json.loads((O/'frozen-table-comparison.json').read_text(encoding='utf-8'))
assert c['minr_vs_maxPM_different_groups']==19 and c['maxPB_vs_maxPM_different_groups']==3
assert c['must_numeric_or_pairing_items']==0 and c['all_four_control_groups_match_independent_selection']
assert sum(c['check_counts'].values())==6415 and sum(v for k,v in c['check_counts'].items() if k!='text')==3625
for item in c['producer_manifests']:
    p=Path(item['path']);assert sha(p)==item['sha256']
    m=json.loads(p.read_text(encoding='utf-8'))
    for f in m.get('files',m.get('additive_files',[])):
        q=Path(f['path']);assert sha(q)==f['sha256'] and q.stat().st_size==f['bytes']
report=(O/'one-page-engineering-table-audit.md').read_text(encoding='utf-8');assert '�' not in report
w=None
for l in report.splitlines():
    if l.startswith('|'):
        n=len(l.strip('|').split('|'))
        if w is None:w=n
        assert w==n
    else:w=None
now=datetime.now(timezone(timedelta(hours=8)));start=datetime.fromisoformat(ind['actual_start'])
out={'task':'session022-role2-R002','actual_start':start.isoformat(),'actual_freeze':now.isoformat(),
 'elapsed_seconds':(now-start).total_seconds(),'within12min':(now-start).total_seconds()<=720,
 'within15min':(now-start).total_seconds()<=900,'must':0,'reviewed_main_rows':24,'reviewed_screening_rows':14,
 'reviewed_trace_rows':168,'reviewed_Markdown_rows':24,'minr_vs_maxPM_differences':19,'maxPB_vs_maxPM_differences':3,
 'field_checks':6415,'number_checks_including_display':3625,'source_pairing_errors':0,
 'version':'original and additive v002, original columns unchanged','envelope_ratio':'backend/optional appendix diagnostic only, excluded from main objective',
 'new_ODE':0,'raw_trajectories_or_Excel_read':False,'producer_scripts_executed':False,
 'producer_or_author_files_modified':False,'status_after_delivery':'idle',
 'unresolved':['all tied time-peak anchors','complete model identity/damping tables','independent event provenance','physical-device causal pairing'],
 'files':[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.iterdir()) if p.is_file() and p.name!='delivery-manifest.json']}
with (O/'delivery-manifest.json').open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in out.items() if k!='files'},ensure_ascii=False,indent=2));print('manifest_sha256',sha(O/'delivery-manifest.json'))
