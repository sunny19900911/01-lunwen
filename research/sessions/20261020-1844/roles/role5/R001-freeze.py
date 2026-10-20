from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,re
ROOT=Path.cwd()/'01-lunwen';O=ROOT/'research/sessions/20261020-1844/roles/role5'
M=ROOT/'papers/damping-output-boundaries/manuscript';p=M/'modal-shear-session009-v001.md'
s=p.read_text(encoding='utf8');checks={}
checks['five_sections']=len(re.findall(r'^## [1-5] ',s,re.M))==5
checks['Chinese_and_English_abstract']='## 摘要（候选）' in s and '## Abstract (candidate)' in s
checks['three_state_labels']=all(x in s for x in ['既有基准结构','模态阻尼增加3个百分点','设置实体阻尼器'])
checks['comparison_identity_pending']='不预设为零阻尼' in s and '不预设与前一状态等效' in s
checks['higher_modes_and_remaining_response']='第四阶及以上' in s and '重构剩余量' in s
checks['signed_sum_and_peak']='各阶独立峰不能直接相加' in s
checks['toy_model_identity']='简化模型数值结果' in s and '不是本栋工程的模态贡献或闭式解' in s
checks['no_layout_candidates']=not any(x in s for x in ['P1','P2','P3','2281','2421','0.8c0'])
checks['no_invented_engineering_percent']='工程单阶贡献比例留待计算' in s
checks['no_control_characters']=not any(ord(c)<32 and c not in '\n\r' for c in s)
checks['literal_TeX']=r'\sum_r(\ell_s^T\phi_r)q_r(t)' in s and s.count('$$')==2
for target in re.findall(r'\]\(([^)]+)\)',s):checks['local_link:'+target]=(p.parent/target).resolve().exists()
assert all(checks.values()),checks
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def js(f,x):f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
now=datetime.now(timezone(timedelta(hours=8)))
start=datetime.fromisoformat('2026-10-20T18:46:40+08:00')
inputs=[M/'horizontal-paper-session006-v020.md',M/'horizontal-paper-session006-v020-notes.md',ROOT/'research/sessions/20261020-1844/plan.md']
js(O/'R001-validation.json',{'status':'passed','checks':checks,'count':len(checks),'CJK_characters':len(re.findall('[\u3400-\u9fff]',s)),'actual_start':start.isoformat(),'actual_end':now.isoformat(),'elapsed_seconds':(now-start).total_seconds(),'within_8_minutes':(now-start).total_seconds()<=480,'scientific_runs':0,'input_identities':[{'path':str(f),'sha256':sha(f)} for f in inputs]})
files=[p,O/'R001-handoff.md',O/'R001-freeze.py',O/'R001-validation.json']
js(O/'R001-freeze.json',{'status':'frozen_first_increment','actual_completed_at':now.isoformat(),'within_8_minutes':(now-start).total_seconds()<=480,'files':[{'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f)} for f in files]})
print(json.dumps({'at':now.isoformat(),'checks':len(checks),'CJK_characters':len(re.findall('[\u3400-\u9fff]',s)),'elapsed_seconds':(now-start).total_seconds(),'within_8_minutes':False,'draft_sha256':sha(p)},ensure_ascii=False))
