from pathlib import Path
import json,datetime,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
st=json.loads((S/'status.json').read_text(encoding='utf-8'))
st.update(last_actual=now,phase='final-integration',checkpoint='R007-final',checkpoint_open=True,no_new_scientific_dispatch=True,recovery_file='rounds/R006.md')
st['git'].update(last_success_HEAD='a35d6665246aa346653ac1fcc6acb8129b6598ff',last_success_receipt='git-R005-receipt.json',publication='R006 frozen final-review and figures publication pending')
st['current_tasks'].update(role2='R007 v004 new-content review0must frozen;idle',role4='R007 two reviewed-data figures frozen22:05:47;idle',role5='R005 v005Word render and QA in progress; only collect after actual freeze',role6='R0063 precise wording suggestions frozen adopted by author;idle')
st['next_checkpoint']='No new science. Collect role5 final manifest, root read finalv005 and all rendered page PNGs; final close at22:34:43, scoped normal Git and stop current automation.'
(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
th=json.loads((S/'threads.json').read_text(encoding='utf-8'))
for q in th['threads']:q['task']=st['current_tasks'][q['role']]
(S/'threads.json').write_text(json.dumps(th,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note='''# R006最后成稿交流与可审图件
本检查点约22:20执行，实际时间以manifest/Git receipt为准。根全文核v004，②R007仅新增内容审查通过：九格18个数值与前36核独审一致、36峰D/M统计无误。⑥工程文字3条建议根采用→⑤，明确Maxwell只讨论区别，低阶组合只是数值参照，避免暗示物理分担已闭合。
④R007以已审数据作1/2/3/9阶三波幅值削弱图及全楼降幅图修订副本，22:05:47冻结、根两图实际查看→⑤。没有新拟合、积分或模型。
⑤唯一v005科学稿和Word，编辑公式/表格/两图。packaged render_docx.py已实际尝试，因未装soffice失败；改用隐藏Word原生导出PDF+bundled pypdfium2逐页PNG。首轮图片段落固定行高裁切已发现，作者修复后重渲染；最终稿只有实际冻结和逐页QA后才允许交付。不能把初轮Word称合格，不上传QA完整图页。此检查点不收活动作者文件。
普通中文说明与预备总结已留本地；正式final-summary待真实关闭时生成。当前自动化指向最后成稿，不延长固定22:34:43。旧git/automation3/4只读核仍PAUSED。
'''
(S/'rounds/R006.md').write_text(note,encoding='utf-8')
with (S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR006 final integration only: role2R007 new-content0must;role6R0063phrases→author;role4R007 two data figures rendered/root viewed→author; no new scientific dispatch. Packaged doc renderer unavailable, native Word fallback and image-paragraph fix tracked by author; final QA not presumed.\n')
paths=[S/n for n in ['status.json','threads.json','runs.md','rounds/R006.md','prepare_R006_publication.py','publish_checkpoint.py','git-R005-receipt.json','automation-R006-writing-receipt.json','old-automation-paused-check.json','普通中文研究说明.md','final-summary-prepared-v001.md']]
for role,rnd in [('role2','R007'),('role4','R007'),('role6','R006')]:
 paths.extend(p for p in (S/'roles'/role/rnd).iterdir()if p.is_file()and p.suffix in ['.md','.json','.csv','.py','.cjs','.svg','.png'])
paths.append(S/'roles/role4/R004/render_figures.cjs')
files=[]
for p in sorted(set(paths),key=str):
 assert p.is_file()and'local-cache'not in p.parts and p.stat().st_size<1048576
 files.append({'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
with (S/'git-R006-publication.json').open('x',encoding='utf-8')as f:json.dump({'checkpoint':'R006','time':now,'message':'research: reviewed final engineering figures and manuscript checks','files':files},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(files)},ensure_ascii=False))
