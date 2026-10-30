from pathlib import Path
import json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
st=json.loads((S/'status.json').read_text(encoding='utf-8'))
st.update(last_actual=now,checkpoint='R005',checkpoint_open=True)
st['current_tasks'].update(role1='R004 independent first12 x3 kernel ratio metrics from root cache;active',role2='R006 v003 scientific claim review5min;active or collect actual',role3='R00336native peak scalar audit frozen0must;idle',role4='R006 unit kernel108 metrics frozen;idle',role5='R004 v004 mainline rewrite integrating reviewed native ledger and unit kernel;12min active',role6='R005 native vs fitted interpretations frozen;idle')
st['scientific_status']['native_peak_ledger']='role3R00336rows scalar/arithmetic independently passed,20timechanges16M0;not causal phase'
st['scientific_status']['unit_modal_kernels']='108existing kernel peak ratios0.70894..0.93645,first3 both amplitude and shape differences;role1 independent36row audit in progress'
st['next_checkpoint']='Collect role1R00436kernel review and role2R006 manuscript review; root read v004 after freeze; then final writing after22:04:43 and final cutoff22:34:43. No new fits or layout tasks.'
st['git']['publication']='R004 explicit frozen mainline evidence publication pending'
(S/'status.json').write_text(json.dumps(st,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
th=json.loads((S/'threads.json').read_text(encoding='utf-8'))
for q in th['threads']:q['task']=st['current_tasks'][q['role']]
(S/'threads.json').write_text(json.dumps(th,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
t='''# R004主线交叉核验与稿件增量
实际约21:43汇总，R003于21:32:22正常推送d62fb764并核远端等同；本R004只冻结小件新证据。
①R003物理系数必要界→②R005交叉→⑤。原始系数单位tonnes，高逆拟合项最大约质量表14833倍，不把拟合相消当真实高阶贡献；条件参考并非已证实际有限元VX上界。②还核⑥R004612项小表算术，和原生物理身份区分。
④R005全楼36对原生D/M→③R003独审，代数/小表/统计通过0must→⑤。峰时改变20对、未变16对；并列峰一般情形不将M0与时刻相同视等价。RH4第1层控制峰换号，旧点削弱与最终峰降有3.6748个百分点差。
新中段证据：④R006现存单位参与模态运动108行，ζ增量相同，峰降6.355—29.106%，前3阶随输入的削弱顺序不同。固定非零常数Γ或输出系数在比值中消去，故不受高阶拟合系数不可辨识影响；实际Γ0无激励，结果不是楼层贡献比例。①R004正在从根N12独立核前12×3波36行；此时只标生产计算完成，未冒称108行全独审。
⑤v003完整稿已根全文读过，未把高拟合堆叠图放正文。新v004重排为阻尼增量→各阶运动→叠加/峰时→各层差异，工程数据主导；物理逐阶楼层分担缺口保留一次，程序式词语整体润色。②R006仅新稿主张科学审查，未重复旧数值。
当前预算不延长，22:04:43进入最后30分钟，22:34:43停止新科研。无重新布置、CM修补、索数据或新拟合。
'''
(S/'rounds/R004.md').write_text(t,encoding='utf-8')
with (S/'runs.md').open('a',encoding='utf-8')as f:f.write('\nR004 completed: role1R003 conditional bound + role2R005432coeff/612arithmetic; role4R00536native ledger + role3R003 independent scalar audit; role4R006108unit modal metrics no newODE/fit; role5v003 read. Pending role1R004 independent36kernel, role2R006 v003 review, authorv004.\n')
with (S/'claims.md').open('a',encoding='utf-8')as f:f.write('\nC019-10 supported/reviewed scalar native accounting：36对D-M及20峰时变/16未变由③独核；不是相位或因果份额。C019-09 production108rows completed，independent first36 audit pending；单位参与核不代表各层真实贡献。\n')
paths=[S/n for n in ['status.json','threads.json','claims.md','runs.md','save_R004_progress.py','prepare_R004_publication.py','rounds/R004-progress.md','rounds/R004.md','automation-R004-receipt.json','git-R003-receipt.json']]
for role,rnd in [('role1','R003'),('role2','R005'),('role3','R003'),('role4','R005'),('role4','R006'),('role5','R003'),('role6','R005')]:
 paths.extend(p for p in (S/'roles'/role/rnd).iterdir()if p.is_file()and p.suffix in ['.md','.json','.csv','.py','.svg','.png'])
paths.append(R/'papers/damping-output-boundaries/manuscript/damping-superposition-session019-v003.md')
files=[]
for p in sorted(set(paths),key=str):
 assert p.is_file()and'local-cache'not in p.parts and p.stat().st_size<1048576
 files.append({'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
with (S/'git-R004-publication.json').open('x',encoding='utf-8')as f:json.dump({'checkpoint':'R004','time':now,'message':'research: modal damping response differences and native peak accounting','files':files},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'files':len(files)},ensure_ascii=False))
