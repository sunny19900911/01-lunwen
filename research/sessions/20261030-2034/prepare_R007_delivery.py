from pathlib import Path
import json,datetime,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2];A=S/'roles/role5/R005'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
mf=json.loads((A/'manifest.json').read_text(encoding='utf-8'));qa=json.loads((S/'root-final-document-QA.json').read_text(encoding='utf-8'))
assert mf['all_checks_passed'] and mf['latest_visual_QA']=='passed' and qa['page_count']==7
st=json.loads((S/'status.json').read_text(encoding='utf-8'))
st.update(last_actual=now,phase='delivery-frozen-await-budget-close',checkpoint='R008-close',checkpoint_open=True,no_new_scientific_dispatch=True,recovery_file='rounds/R007.md')
st['current_tasks']={f'role{i}':'completed and actual idle; no new task'for i in range(1,7)}
st['scientific_status']['manuscript']='finalv005 root full read +7page Word root/author visual QA; frozen22:16:35; no further science'
st['final_manuscript']={'relative':'papers/damping-output-boundaries/manuscript/damping-superposition-session019-v005.md','sha256':qa['MD_sha256']}
st['final_word']={'relative':'papers/damping-output-boundaries/manuscript/damping-superposition-session019-v005.docx','sha256':qa['Word_sha256'],'pages':7,'OMML':25,'editable_tables':4,'figures':2,'root_visual_QA':True}
st['git'].update(last_success_HEAD='30bdc6f2b63723eae7dd44bf854734735e7ee293',last_success_receipt='git-R006-receipt.json',publication='R007 final frozen Word and QA publication pending')
st['next_checkpoint']='Administrative close at22:34:43, final-summary with actual time, final scoped Git, pause/view/config receipt then delete completed automation per heartbeat instruction. No repeat research/review.'
(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
th=json.loads((S/'threads.json').read_text(encoding='utf-8'))
for q in th['threads']:q['task']=st['current_tasks'][q['role']];q['actual_status']={'type':'idle'}
(S/'threads.json').write_text(json.dumps(th,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(S/'rounds/R007.md').write_text('''# R007最终审阅稿与Word交付冻结
作者22:16:35完成v005及7页Word，实际idle。主控完整读v005，三处终审建议均已采用；25处原生可编辑公式、4张可编辑表、2图经结构核验。根使用view_image original实际逐页看完全部7页，图/表/公式清晰无裁切重叠，最终Word hash638e0f5d152c0e216f138250abd0f402c55e1f157229461842fb6da9de62658a。
标准render_docx曾因soffice缺失失败；隐藏Word原生PDF导出+bundled pypdfium2生成图页，初轮图片行距裁切已修复并全页重渲染。没有将失败首轮作为交付，也未复制QA完整图页到Git。
科学内容仍是已明确模态单位运动的变化、软件全楼峰降与控制峰核算；真实每层逐阶物理分担未闭合，未把高拟合巨项认物理相消，未新增Maxwell定量。目标是审阅稿，不冒称已经符合投稿全部格式或主线完全完成。
R006 Git正常push30bdc6f2远端SHA等；其publisher首次把中文文件名的Git引号输出误判为越界，NUL分隔核对恢复，逐blob再核、无reset/unstage，已经修复通用publisher。R007仅最终稿/Word/小构建脚本与QA；所有原Excel/模型、local-cache、旧脏文件保持。
至截止前不派新科研、不反复审稿或新计算填预算，只保留必要交付与行政收束。固定截止22:34:43，关闭时间据真实时钟写，不预报已结束。
''',encoding='utf-8')
with (S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR007: finalv005MD/Word frozen22:16:35;root fullread and all7page actual view;25OMML/4tables/2figures pass. Sixroles idle. No new science until budget close22:34:43; only administrative remaining.\n')
paths=[S/n for n in ['status.json','threads.json','runs.md','rounds/R007.md','prepare_R007_delivery.py','root_final_document_audit.py','root-final-document-QA.json','resume_staged_checkpoint.py','publish_checkpoint.py','git-R006-receipt.json']]
paths.extend(p for p in A.iterdir()if p.is_file()and p.suffix in ['.md','.json','.csv','.py','.ps1'])
paths.extend(Path(q['path'])for q in mf['final_outputs'])
files=[]
for p in sorted(set(paths),key=str):
 assert p.is_file()and'local-cache'not in p.parts and p.stat().st_size<1048576
 files.append({'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
with (S/'git-R007-publication.json').open('x',encoding='utf-8')as f:json.dump({'checkpoint':'R007','time':now,'message':'research: final modal damping paper and verified editable Word','files':files},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(files),'Word_ready':True},ensure_ascii=False))
