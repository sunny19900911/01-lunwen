from pathlib import Path
import csv,json,hashlib,datetime
S=Path(__file__).resolve().parent;R=S.parents[2];old=R/'research/sessions/20261103-1458'
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def mdtable(headers,rows):
    return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(str,row))+'|' for row in rows])
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
lines=['# 实际方案主分析的工程资料与完整附表','',f'整理时间：{now}。对应p06-actual-main-session026新稿。','',
 '## 比较对象与数据身份','',
 '主体为基准B与实际88只阻尼器方案D，在RH4/SHW4/SHW7各X/Y六个方向工况、12层的72条记录。不是14个实际工况，也不是六次独立地震。背景阻尼和完整内部求解设置的缺项沿旧配对裁决保留。原14工况168条只属于基准B与统一增加3个百分点模态阻尼M的扩展对照。','',
 '[原实际方案资料和布置](../20261103-1458/实际方案资料与完整附表.md)；[输入和模型配对裁决](../20261103-1458/roles/pairing/三模型比较条件与裁决.md)；[原14工况完整附表](../20261102-1917/roles/role5/R002/engineering-data-and-full-tables.md)。','',
 '实际方案本轮新算d来自两份旧原生Story Forces缓存的B/D各72组，所有保存时刻逐点一致；峰值与旧已审72表完全一致。并列峰均为1，即本数据无绝对峰并列；方法仍预定取最早保存峰。d恒等式是同保存网格上的评价差，不表示相位份额。','',
 '## 完整24组改善范围与两类控制输入','',
 '减幅与偏差分别用百分数、百分点列示。每条减幅均为同输入P_D/P_B；最大需求一列是该层实际方案跨同方向三输入的最大P_D。两列输入可以不同，不把不同记录拼成一条成对减幅。','']
rows=read(S/'roles/response/actual-layer-direction-ranges-24.csv')
lines.append(mdtable(['方向/层','最小减幅输入','最小/%','中位/%','最大/%','最大需求输入','最大P_D/kN','该输入减幅/%'],[
    [r['Axis']+'/'+r['Story'],r['min_case'],f"{float(r['min_reduction_percent']):.6f}",f"{float(r['median_reduction_percent']):.6f}",f"{float(r['max_reduction_percent']):.6f}",r['demand_control_case'],f"{float(r['P_D_max_kN']):.6f}",f"{float(r['r_at_demand_control_percent']):.6f}"] for r in rows]))
lines+=['','## 完整72条峰值与原峰时读数','',
 '[72条可复算CSV](roles/response/actual-versus-baseline-time-peak-72.csv)，含B/D符号峰、源行、缓存键、保存时窗、并列峰数及D(t_B)。下表d列是d_D，r_at列是r_at,D。','']
rows=read(S/'roles/response/actual-versus-baseline-time-peak-72.csv')
lines.append(mdtable(['输入/层','P_B/kN','P_D/kN','t_B/s','t_D/s','r_D/%','r_at/%','d/百分点'],[
 [r['Case']+'/'+r['Story']]+[f"{float(r[k]):.6f}" for k in ['P_B_kN','P_D_kN','t_B_s','t_D_s','r_peak_percent','r_at_percent','d_pp']] for r in rows]))
lines+=['','## 独立核查与必要范围','',
 '[生产报告](roles/response/actual-response-report.md)；[独立核查](roles/audit/actual-mainline-audit.md)；[方法与CSI原文定位](roles/method/工程方法与主次结构建议.md)。','',
 '几何88只完整；原生轴力完整范围仅第8—11层32只×六工况，不向其余装置补零。QD=sum(nP)为J端内力抵抗项，节点外力相反。软件Bottom截面是否包含装置力尚未完整说明，正文不进行QT−QD物理扣力。','',
 '最大d在RH4Y第12层，基准565.0421kN、实际523.5629kN；比例很大不表示该层绝对需求最大或最危险。完整承载力、配筋和组合检查不在所给数据内。','',
 '固定300阶经典阻尼参考与三层模型解释模态叠加，不能由线性参照拟合或幅值吻合，推出实际FNA逐阶剪力唯一。真实装置方案使用其自身非线性运动与内力恢复才可进一步分解。','',
 '原件只读，本轮无求解器/模型API/新ODE/参数扫描/原Excel重复提取。源缓存散列、键和源行保留于response/input-freeze.json；大数组和第三方原文仅本地。','']
p=S/'工程资料与完整附表.md';assert not p.exists();p.write_text('\n'.join(lines),encoding='utf-8',newline='\n')
W=S/'word';W.mkdir(exist_ok=True)
for n in ['build_word.py','math_omml.py','render_review.py']:
    t=W/n;assert not t.exists();t.write_bytes((old/'word'/n).read_bytes())
p=W/'build_word.py';txt=p.read_text(encoding='utf-8').replace("EXPLICIT_INLINE_MATH = {", "EXPLICIT_INLINE_MATH = {\n 'A_D':r'A_D', 't_D':r't_D', 'd_D':r'd_D', 'r_at,D':r'r_{\\mathrm{at},D}',\n 'V_D(t_B)':r'V_D(t_B)',")
# Wider first column in the actual old-peak comparison; other table dimensions follow existing engineering template.
txt=txt.replace("elif len(header)==6 and header[1].startswith('QT'):","elif len(header)==7 and header[0]=='工况/楼层':widths=[2.6,2.4,2.4,2.3,2.3,2.2,2.8]\n  elif len(header)==6 and header[1].startswith('QT'):")
p.write_text(txt,encoding='utf-8',newline='\n')
gate=(old/'check_final_word.py').read_text(encoding='utf-8')
gate=gate.replace("'M' in x for x in flat)","'D' in x for x in flat)")
gate=gate.replace("'PM' in n", "'PD' in n")
gate=gate.replace("assert doc.findall('.//m:m',NS),'Native K matrix missing'", "if 'bmatrix' in md:assert doc.findall('.//m:m',NS),'Native K matrix missing'")
gate=gate.replace("assert any('engineering-data-and-full-tables'", "assert any('20261103-1700' in x.get('Target','') for x in links),'Current complete engineering supplementary link missing'\n assert any('engineering-data-and-full-tables'")
g=S/'check_final_word.py';assert not g.exists();g.write_text(gate,encoding='utf-8',newline='\n')
(S/'support-preparation.json').write_text(json.dumps({'at':now,'supplement':p.name,'build_helper_source':'20261103-1458','intentional_gate_changes':['main ratio/selector now P_D; d_D numerator P_D-A_D','native matrix required only if actually present in source','current complete engineering supplement required'],'missing_reference_attempt':'documents/references/create_edit.md absent; corrected to tasks/create_edit.md and read tasks/verify_render.md','first_draft_build_failure':'Reference exact-byte assertion saw one appended terminal newline before any output; corrected construction preserves source reference tail exactly'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'supplement':'工程资料与完整附表.md','files_prepared':5,'new_word_authored':False},ensure_ascii=False))
