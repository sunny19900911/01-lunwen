from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re,csv,io
ROOT=Path.cwd()/'01-lunwen';S=ROOT/'research/sessions/20261019-2045';O=S/'roles/role5'
p=ROOT/'papers/damping-output-boundaries/manuscript/placement-session007-v001.md'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def write(f,s):f.write_text(s,encoding='utf8',newline='\n')
def js(f,x):write(f,json.dumps(x,ensure_ascii=False,indent=2)+'\n')
s=p.read_text(encoding='utf8')
s=s.replace('装置层数量与节点楼层标签分别说明，不据此把全结构概括为“11层、约49m高”。','装置层数量与节点楼层标签分别描述。')
s=s.replace('全楼位置调整应依据这一实际几何范围组织，不继续沿用旧稿对局部资料的楼层与高度概括。','后续布置比较应覆盖全楼，并区分装置所在层与其他节点层。')
write(p,s)
supp=O/'R003-补充说明.md'
z=supp.read_text(encoding='utf8').replace('本任务从21:34:14实际接手，≤12分钟。','本任务从21:34:14实际接手，原要求≤12分钟；实际超过任务和会话截止，完成时间及经过时长按R003-report.md如实记录。截止后仅收束已有稿件及检查，不继续研究。')
write(supp,z)
checks=[]
def ck(n,v):checks.append({'name':n,'pass':bool(v)})
inputs=json.loads((O/'R003-input-freeze.json').read_text(encoding='utf8'))
for f in inputs['stable_inputs']:
 q=Path(f['path']);ck('input:'+q.name,q.stat().st_size==f['bytes'] and sha(q)==f['sha256'])
ck('seven-chapters',len(re.findall(r'^## [1-7] ',s,re.M))==7)
ck('four-conclusions',len(re.findall(r'^（[1-4]）',s,re.M))==4)
ck('six-tables',len(re.findall(r'^\*\*表[1-6] ',s,re.M))==6)
ck('four-equations',re.findall(r'\\tag\{(\d+)\}',s)==list('1234'))
cn=s.split('## 摘要\n\n')[1].split('\n\n**关键词**')[0]
ck('abstract300-500',300<=len(cn)<=500)
old=(ROOT/'papers/damping-output-boundaries/manuscript/horizontal-paper-session006-v020.md').read_text(encoding='utf8')
oldrefs={int(k):v for k,v in re.findall(r'^\[(\d+)\] (.*)$',old,re.M)}
newrefs={int(k):v for k,v in re.findall(r'^\[(\d+)\] (.*)$',s,re.M)}
for n,k in enumerate([1,2,10,11,12,14],1):ck('reference-body:'+str(n),newrefs[n]==oldrefs[k])
first=[]
for q in re.findall(r'\[(\d+(?:[–,-]\d+)*)\]',s.split('## 2 ')[0]):
 for part in q.split(','):
  r=re.split('[–-]',part)
  for num in range(int(r[0]),int(r[-1])+1):
   if num not in first:first.append(num)
ck('first-citation-order',first==list(range(1,7)))
rows=list(csv.DictReader(io.StringIO((S/'roles/data/R002-native-horizontal/layer-axis-peaks-48.csv').read_text(encoding='utf-8-sig'))))
for story in ['Story8','Story9','Story10','Story11']:
 for case,axis in [('RH4X','X'),('RH4Y','Y')]:
  row=next(x for x in rows if x['Story']==story and x['Case']==case and x['Axis']==axis)
  line='|'+story+'|'+case+'/'+axis+'|'+'|'.join(f"{float(row[k]):.2f}" for k in ['QT_peak_kN','QT_peak_t_s','QD_peak_abs_kN','QD_peak_t_s','QD_at_QT_peak_kN'])+'|'
  ck('native-row:'+story+':'+case,line in s)
ck('candidate-byte-copy',(O/'R003-candidate-geometry.csv').read_bytes()==(S/'roles/design/R002-three-position-drafts.csv').read_bytes())
for token in ['3416','88只','Story12','53.5m','32只','192条','P1和P3','同层平移','未排序','0.8c0','1.2c0','共享Link1','原有控布置记为M0','尚未获得改布置后的响应']:
 ck('scope:'+token,token in s)
for token in ['15.4564','43.321366','约49m','约4.70%','已优选P1','已优选P2','已优选P3']:ck('no-old-result-or-fabrication:'+token,token not in s)
ck('P1-axis-and-movement','Y向装置沿X平移2.717m' in s)
ck('P2-axis-and-movement','X向装置沿Y平移1.350m' in s)
links=0
for q in [p,supp]:
 t=q.read_text(encoding='utf8')
 ck('UTF8-no-BOM:'+q.name,not q.read_bytes().startswith(b'\xef\xbb\xbf'))
 ck('no-controls:'+q.name,not any(ord(c)<32 and c not in '\n\r' for c in t))
 ck('math-pairs:'+q.name,t.count('$$')==2*len(re.findall(r'\$\$.*?\$\$',t,re.S)))
 for target in re.findall(r'\]\(([^)]+)\)',t):
  if target.startswith(('http://','https://')):continue
  ck('local-link:'+target,(q.parent/target).resolve().exists());links+=1
passed=all(x['pass'] for x in checks)
start=datetime.fromisoformat('2026-10-19T21:34:14+08:00')
finished=datetime.now(timezone(timedelta(hours=8)))
rec={'status':'passed' if passed else 'failed','checks':len(checks),'failures':[x for x in checks if not x['pass']],'abstract_chars':len(cn),'local_links_checked':links,'actual_started_at':start.isoformat(),'actual_completed_at':finished.isoformat(),'elapsed_seconds':(finished-start).total_seconds(),'task_deadline':'2026-10-19T21:46:14+08:00','session_deadline':'2026-10-19T22:45:41+08:00','within_task_limit':finished<=datetime.fromisoformat('2026-10-19T21:46:14+08:00'),'within_session_limit':finished<=datetime.fromisoformat('2026-10-19T22:45:41+08:00'),'checks_detail':checks}
js(O/'R003-validation.json',rec)
report=f'''# R003：真实全楼布置阶段稿交接

已形成placement-session007-v001.md及独立补充说明。正文七章、六表、四条阶段结论，中英文摘要对应，中文摘要{len(cn)}字；六条书目复用v020已核来源并按本文首次引用顺序重编号。旧v020原字节保持，未把旧无量纲玩具模型数字迁移为本楼结果。

实质增量：全楼3416节点/88只装置/11个装置层及Story12最高节点53.5m；上部四层32只装置原生P的现状8行示例；物理方向与Bottom包含性条件；三项真实节点草案及坐标；M0有控基线、单项位置比较、0.8c0/1.2c0辅助比较和明日复算表。候选未排序，P1/P3互斥，P1为Y向装置沿X平移、P2为X向装置沿Y平移。改模型尚无响应，不预填改善。

本地核验{len(checks)}项，结果{rec['status']}，本地链接{links}项；没有读取原Excel/NPZ、操作ETABS/API、Git或自动化，没有新建或续派子代理。未读取其他角色在写报告，未自称独立科学审计。补充说明列冻结小结果入口及过程。

实际时间：{start.isoformat()}—{finished.isoformat()}，经过{rec['elapsed_seconds']:.3f}秒。原单项12分钟及会话22:45:41截止均已超过，不能写为按时完成。观察到22:58:35实际时钟后仅作现有稿件必要收束、文字/链接核验及冻结，没有继续方案研究或求解。

下一具体问题：由角色1/2/4判断P1/P2同层平移能否改变实际轴向运动，并说明P3从Story9移出一只装置的响应代价和安装条件，再交主控选定明日先算两组。现稿不替代该裁决。
'''
write(O/'R003-report.md',report)
if not passed:
 print(json.dumps({k:v for k,v in rec.items() if k!='checks_detail'},ensure_ascii=False));raise SystemExit(1)
files=[p]+sorted(x for x in O.glob('R003*') if x.is_file() and x.name!='R003-freeze.json')
payload={'status':'frozen','actual_completed_at':finished.isoformat(),'within_task_limit':rec['within_task_limit'],'within_session_limit':rec['within_session_limit'],'new_solver_runs':0,'files':[{'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f)} for f in files]}
js(O/'R003-freeze.json',payload)
assert all(sha(Path(x['path']))==x['sha256'] for x in payload['files'])
print(json.dumps({'status':'frozen','actual_completed_at':finished.isoformat(),'elapsed_seconds':rec['elapsed_seconds'],'checks':len(checks),'files':len(files),'draft_sha256':sha(p),'within_task_limit':False,'within_session_limit':False},ensure_ascii=False))
