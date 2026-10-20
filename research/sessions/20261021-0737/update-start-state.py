from pathlib import Path
import json,datetime
S=Path(__file__).resolve().parent
v=json.loads((S/'status.json').read_text('utf-8'))
r=json.loads((S/'R000-tool-receipts.json').read_text('utf-8'))
by={p['role']:p for p in r['actual_six_role_start']}
for role in v['roles']:
 p=by[role['role']];role.update(cursor=p['cursor'],actual_status=p['status'],turn_status=p['turn']['status'],task='R001')
v.update(phase='research',last_actual_snapshot=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),automation_actual_config=json.loads((S/'automation-actual-readback.json').read_text('utf-8')),last_scientific_progress='Six existing role chats actually active on new R001 tasks; no duplicate chat/solver started.')
(S/'status.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
(S/'threads.json').write_text(json.dumps({'session':v['session'],'roles':v['roles']},ensure_ascii=False,indent=2)+'\n','utf-8')
