from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
assert not(S/'git-FINAL-publication.json').exists()
now=datetime.now(timezone(timedelta(hours=8))).isoformat()
def js(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
check=json.loads((S/'root-final-document-check.json').read_text());assert check['status']=='accepted final document'
plain=(S/'普通中文研究说明-成稿准备-v001.md').read_text(encoding='utf-8').replace('本说明随最终稿核对后交付。当前为成稿准备版本，不代表四小时窗口已经结束。','最终论文v007和Word已经完成独立审阅、内容核对与11页实际排版检查。结果范围保持上述区别；完成后提前关闭本轮，不延长研究或用重复计算填满预算。')
(S/'普通中文研究说明.md').write_text(plain,encoding='utf-8')
js(S/'root-final-check-script-note.json',dict(actual=now,initial_check_failure='Markdown parser counted an absolute-value equation as a table because it only checked the starting pipe',fix='require both leading and trailing table pipe',source_or_docx_changed=False,subsequent_result='all208 tablecells identical; allartifactchecks pass'))
d=json.loads((S/'status.json').read_text());d.update(last_actual=now,phase='closed-completed-early',checkpoint='FINAL-publication',checkpoint_open=True,closed_scientific_at='2026-10-31T13:40:20+08:00',closed_actual=now,no_new_scientific_dispatch=True,no_new_numeric_experiments=True,recovery_file='final-summary.md',automation='git-2 formallyPAUSED/viewed/actualconfigchecked then deleted, stopwakeups; oldthreePAUSED')
d['scientific_status']['manuscript']='v00727232B SHA9b295a0aa81f2d493bc5945b0e6f907b0f00f096f5949d507a3d36798d262a13;onlytwooptionalclarifications/S1link fromreviewedv006; rootexactdiffpassed'
d['scientific_status']['Word']='503094B SHA216d5437605a0d08c5676a586efdcabdbd7a309f95d374ee768cf6b7f6762add;11pages author+root actualviewall;77OMML/6tables/3approvedembeddedPNG/208cells independentlychecked'
d['current_tasks']={k:('closed own90min13:11:38, no restart' if k=='role3' else 'frozen idle, no further dispatch') for k in d['current_tasks']}
d['next_checkpoint']='No further science orroutinewakeups; git-2 deleted. Finishthis final normalwhite-listGit then handoverWord/summary. Actual windowcompletedearly, not4hcontinuousclaim. Closed session notto restart.'
js(S/'status.json',d)
t=json.loads((S/'threads.json').read_text())
for x in t['threads']:
 x['task']=d['current_tasks'][x['role']]
 if x['role']=='role5':x.update(cursor='824ab043-4970-4d4a-8fa8-7ed81ac611bc:58',actual_status={'type':'idle'},last_actual=now)
js(S/'threads.json',t)
with(S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nFINAL '+now+': authorWord frozen13:57:55; root all11 actualpages view+18manifestfiles+208cells+77OMML+3embeddedfigure andexact2textclarifications passed14:01:50. Canonicalsoffice unavailable, actualWordCOM/pypdfium2 fallback; failurelogs preserved. Closeearly afterdeliverables, notfake4hcontinuous. git-2 formalpause/view/configcheck/delete succeeded; oldthreepaused. Lastnormalwhitelistpublicationpendingreceipt.\n')
js(S/'final-closeout-prepublication.json',dict(actual=now,authorization_start='2026-10-31T11:30:11+08:00',hard_deadline='2026-10-31T15:30:11+08:00',closed_early_reason='scientific outputs and complete reviewed Word finished; no new scientific dispatch or filler',final_MD=check['markdown_sha256'],final_Word=check['docx_sha256'],all_pages_viewed=11,automation='formal pause then delete succeeded',oldthree='actualconfigverifiedPAUSED',Git='finalpublication pending receipt'))
files=[];base=S/'roles/role5/R007'
for p in base.iterdir():
 if p.is_file() and p.suffix in ['.md','.json','.py','.ps1','.csv'] and p.stat().st_size<1048576:files.append(p)
for n in ['prepare_final_publication.py','status.json','threads.json','runs.md','claims.md','final-summary.md','普通中文研究说明.md','root-final-document-check.py','root-final-document-check.json','root-final-check-script-note.json','final-closeout-prepublication.json','final-automation-paused-config-check.json','final-automation-tool-receipts.json','automation-R009-update-receipt.json','git-R009-receipt.json','R009-word-progress-1344.json']:files.append(S/n)
for n in ['physical-modal-shear-session020-v007.md','physical-modal-shear-session020-论文审阅稿-v007.docx']:files.append(R/'papers/damping-output-boundaries/manuscript'/n)
js(S/'git-FINAL-publication.json',dict(checkpoint='FINAL',time=now,message='paper: deliver reviewed modal shear manuscript and editable Word with engineering workflow',files=[dict(relative=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(set(files))]))
print(json.dumps(dict(actual=now,files=len(set(files)),bytes=sum(p.stat().st_size for p in set(files))),ensure_ascii=False))
