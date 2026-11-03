from pathlib import Path
import re,csv,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];M=R/'papers/damping-output-boundaries/manuscript'
old=M/'p06-mechanism-classification-v003.md';new=M/'p06-actual-damper-session025-v001.md'
s=new.read_text(encoding='utf-8');t=old.read_text(encoding='utf-8')
tabs=lambda x:re.findall(r'(?:^\|.*\n)+',x,re.M)
assert tabs(s)[1:4]==tabs(t)[1:4]
assert re.findall(r'\$\$.*?\$\$',s,re.S)==re.findall(r'\$\$.*?\$\$',t,re.S)
assert s[s.index('## 参考文献'):]==t[t.index('## 参考文献'):]
rr=list(csv.DictReader((H/'roles/response/common-six-control-records-24.csv').open(encoding='utf-8-sig')))
lines=['# 实际阻尼器方案资料与完整附表','','## 比较范围与输入依据','',
'共有RH4、SHW4、SHW7各X/Y六方向工况，共72条楼层记录。基准与模态参考在此范围的峰值/峰时与原168表相同；实体与基准的16296个导出基底时刻、六分量共97776个值逐点一致。实体18个质心方向质量与基准/参考汇总逐项对应，最大相对差3.60077e-14。实体背景阻尼、完整内部求解设置未导出，因此本文r_D为所提供方案相对基准的软件峰值减幅，不解释为所有其他状态严格相同下的单一阻尼因果收益。','',
'实际导出没有函数、时程工况设置、质心质量刚度表，重读原件不能补齐不存在的导出表；有效基底输入已有独立数值复核。B/M共有六工况的倍率3.5、时间倍率1、起始到达0、Angle0等字段对应。','',
'原14方向工况的参考19/24、共有六工况参考7/24和实体方案12/24属于不同模型/输入集合，分别报告。X/Y不能计为六独立事件。第5层X向方案减幅前两输入仅差0.0181063个百分点，保留相邻记录而非扩大排序稳定性。','',
'## 24组实体方案控制记录','',
'|方向/层|最小减幅输入|最小r_D/%|该输入P_D/kN|最大需求输入|最大P_D/kN|该输入r_D/%|','|---|---|---:|---:|---|---:|---:|']
for r in rr:
    lines.append(f"|{r['Axis']}/{r['Story']}|{r['conditional_min_D_reduction_case']}|{float(r['conditional_min_D_reduction_percent']):.6f}|{float(r['P_D_at_conditional_min_D_reduction_kN']):.6f}|{r['actual_max_demand_case']}|{float(r['actual_max_demand_kN']):.6f}|{float(r['conditional_r_D_at_actual_max_demand_percent']):.6f}|")
lines+=['','## 资料与可复查表','',
'- [88只真实几何重算与源行](roles/geometry/actual-link-geometry-88.csv)','- [11层实际配置](roles/geometry/layout-by-story-11.csv)','- [三模型72条成对输出](roles/response/three-model-common-six-records-72.csv)','- [24组两类控制输入及参考对照](roles/response/common-six-control-records-24.csv)','- [第8层六工况同刻出力](roles/response/Story8-native-device-timing-6.csv)','- [三模型比较条件与裁决](roles/pairing/三模型比较条件与裁决.md)','- [输入与设置数值核查](roles/pairing/pairing-results.json)','- [独立数字审核](roles/audit/audit.md)','',
'几何来自已有3416节点/88Link的实际导出。每层8只分为X4/Y4，全楼44/44；第8—11层32只装置在六工况下有192条完整原生轴力记录。QD=ΣnP按真实I/J方向合成上端J结构内力抵抗项，节点外力反号；不把局部子集补成全88出力，不根据未知软件切口包含口径物理扣QT求主体抗力。','',
'旧响应表的conditional列名保留生成时状态；本轮配对核查补齐了保存基底输入的一致性，正文按上述裁决使用，不改写旧冻结CSV。实际参数来自用户确认κ500000kN/m、c477kN(s/m)^0.3、α0.3；原属性赋值空表不补造。实际方案属于工程模型的数值应用，不是现场实测或装置物理试验。','']
out=H/'实际方案资料与完整附表.md';assert not out.exists();out.write_text('\n'.join(lines),encoding='utf-8',newline='\n')
links=[]
for target in re.findall(r'\]\(([^)]+)\)',s):
    if '://' in target:continue
    assert (new.parent/target).resolve().is_file(),target;links.append(target)
report={'source_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'manuscript':new.relative_to(R).as_posix(),'bytes':new.stat().st_size,'sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'original_tables2_to4_exact':True,'table1_scope_expanded_intentionally':True,'original_display_equations_exact':True,'references_exact':True,'tables':len(tabs(s)),'figures':len(re.findall(r'!\[',s)),'all_source_links_exist':links,'initial_validation_note':'Initial generator expected data-scope table1 unchanged, although that table was intentionally expanded. That check stopped after writing draft; corrected scoped verification above passes. No scientific data were changed to pass a check.'}
(H/'manuscript-v001-change-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['manuscript','bytes','sha256','tables','figures']},ensure_ascii=False))
