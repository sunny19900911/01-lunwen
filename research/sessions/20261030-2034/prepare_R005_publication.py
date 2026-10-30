from pathlib import Path
import datetime,json,hashlib
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
st=json.loads((S/'status.json').read_text(encoding='utf-8'))
st.update(last_actual=now,phase='final-integration',checkpoint='R006',checkpoint_open=True,no_new_scientific_dispatch=True,primary_task='Scientific calculations frozen; final v005 engineering paper, Word render QA and bounded reviews only',recovery_file='rounds/R005.md')
st['current_tasks'].update(role1='R004 kernel independent review frozen;idle',role2='R007 only v004 new unit-kernel claims/table1 final review5min',role3='R003 ledger review frozen;idle',role4='R007 two existing-data engineering figures6min, no science calculation',role5='R005 finalv005+Word/render20min;deadline22:25,onlyauthor',role6='R006 engineering wording final review5min')
st['scientific_status']['manuscript']='v004 frozen21:46, root full read22:02; v005/Word final formatting in progress; no true high-modal physical attribution'
st['scientific_status']['Story12']='fitted output accurate; high fitted terms not accepted as physical modal shear; native peak change valid'
st['next_checkpoint']='Collect bounded final review and figures, read finalv005/Word QA; do not dispatch new fits/theory/search. Next GitR006 after final artifacts frozen, hard stop22:34:43 and administrative final close.'
st['git']['publication']='R004remoteSHAequal; R005 reviewed v004 and independent kernel metric publication pending'
(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
th=json.loads((S/'threads.json').read_text(encoding='utf-8'))
for q in th['threads']:q['task']=st['current_tasks'][q['role']]
(S/'threads.json').write_text(json.dumps(th,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
txt='''# R005真实22:04成稿检查点
六角色22:01实际快照均idle，未据旧running重派。根完整读v004及补充说明，主线按增ζ→各阶幅值/波形→完整合成/控制峰→楼层差异整合。
新中段已独审：①R004从根N12旧核独核36行，幅比/归一波形/72峰时与④R006一致；③36条软件峰记账已独审；②v003五主张检查0must。v004单位核前3表与第9阶例来自该范围；未夸成108行全独算。
角色交流：上述①②③结果与高项物理限制→⑤，⑤完成v004并停；现②只审v004新增9格表/主张，⑥只改工程叙述，④只画已审数据图，⑤唯一最终v005+Word。无新理论、拟合、ODE、布置或资料索取；进入最后30分钟，scientific_dispatch关闭，成稿/排版QA不扩大科研。
Word使用documents当前skill，必须操作标记+渲染逐页检查，未渲染不得当合格Word。目标22:25前冻结，22:34:43总截止不变。没有实际姓名单位不编。完整图页数组local-cache不发布。
GitR004已推555777073远端核等。R004一次diff-check在冻结数学行发现LaTeX意图空格，仅该行按精确源SHA豁免；源码原字节保留，其他普通行尾检查未放宽，回执和resume脚本随本次留档。R005新稿/小表明确白名单，不收活动角色文件。
'''
(S/'rounds/R005.md').write_text(txt,encoding='utf-8')
with (S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR005: v004 root全文读；role1R00436unitmetrics独核已采用，role2R006v003审通过。Final integration only, no_new_scientific_dispatch=true. role2R007/role6R006 new-content final review,role4R007 data figures,role5R005 v005WordQA;all limits within22:34:43.\n')
with (S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC019-09 reviewed restricted scope：前12阶×3波36核幅比/归一波形经①独立根N12缓存核同；72峰时一致。SHW3第3/9阶峰降6.3546/29.1063%，不依赖固定非零输出/参与乘子；Γ0不可作实际贡献。108生产行范围非全部独核。\n')
paths=[S/n for n in ['status.json','threads.json','claims.md','runs.md','actual-snapshot-R005-start.json','rounds/R005-start.md','rounds/R005.md','prepare_R005_publication.py','resume_R004_publication.py','git-R004-receipt.json']]
for role,rnd in [('role1','R004'),('role2','R006'),('role5','R004')]:
 paths.extend(p for p in (S/'roles'/role/rnd).iterdir()if p.is_file()and p.suffix in ['.md','.json','.csv','.py'])
paths.append(R/'papers/damping-output-boundaries/manuscript/damping-superposition-session019-v004.md')
files=[]
for p in sorted(set(paths),key=str):
 assert p.is_file()and'local-cache'not in p.parts and p.stat().st_size<1048576
 files.append({'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
with (S/'git-R005-publication.json').open('x',encoding='utf-8')as f:json.dump({'checkpoint':'R005','time':now,'message':'research: integrated modal damping mechanism and full-building evidence','files':files},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(files)},ensure_ascii=False))
