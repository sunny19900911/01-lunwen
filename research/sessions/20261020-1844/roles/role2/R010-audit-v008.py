from pathlib import Path
from datetime import datetime, timedelta
import csv, hashlib, json, re
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
ROLES = OUT.parent
PAPER = ROOT/'papers/damping-output-boundaries/manuscript/modal-shear-session009-v008.md'
START = datetime.fromisoformat('2026-10-20T20:48:28.552280+08:00')
DEADLINE = START+timedelta(minutes=8)
def ident(p):
    b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def rc(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def js(name,obj):
    p=OUT/name;assert not p.exists();p.write_bytes((json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8'));json.loads(p.read_text(encoding='utf-8'))
assert datetime.now(START.tzinfo)<DEADLINE and not (OUT/'R010-validation.json').exists()
sources=[];known={}
for n in range(3,10):
    p=OUT/f'R{n:03d}-manifest.json';sources.append(ident(p))
    for r in json.loads(p.read_text(encoding='utf-8'))['files']:
        got=ident(Path(r['path']));assert got['sha256']==r['sha256'] and got['bytes']==r['bytes']
    c=json.loads((OUT/f'R{n:03d}-checks.json').read_text(encoding='utf-8'))
    known.update({r['path']:r for r in c['source_bindings']})
writer=json.loads((ROLES/'role5/R008-freeze.json').read_text(encoding='utf-8'))
for r in writer['files']:
    got=ident(Path(r['path']));assert got['sha256']==r['sha256'] and got['bytes']==r['bytes'];sources.append(got)
assert ident(PAPER)['sha256']=='d4c5f90155943ecd96663873dc42fed9f59e76509c0acb558f437e31baa91aec'
text=PAPER.read_text(encoding='utf-8');lines=text.splitlines();tables=[];block=[]
for line in lines+['']:
    if line.startswith('|'):block.append([x.strip() for x in line.strip('|').split('|')])
    elif block:tables.append(block[2:]);block=[]
assert [len(t) for t in tables]==[6,2,2,3,4,3,4,3]
count=0
def num(cell,value):
    global count
    cell=cell.replace('−','-');assert re.fullmatch(r'[+-]?\d*\.?\d+',cell),cell
    digits=len(cell.split('.')[1]) if '.' in cell else 0
    assert abs(float(cell)-float(value))<=.50001*10**(-digits)+1e-10,(cell,value)
    count+=1
def pairs(cell):return re.findall(r'[+-]?\d+(?:\.\d+)?',cell.replace('−','-'))
def source(role,name):
    p=ROLES/role/name;got=ident(p);assert got==known[str(p)],p;sources.append(got);return rc(p)
main=source('role4','R002-all14-main-axis-168.csv')
three=source('role4','R003-three-model-peaks-72.csv')
device=source('role4','R005-Story8-six-layer-summary.csv')
shape=source('role1','R006-shape-mass-local-shear.csv')
anchors=source('role1','R003-mechanism-table.csv')
peaks=source('role1','R004-whole-window-mode-peaks.csv')
common=source('role1','R004-common-time-terms.csv')
reference=source('role1','R005-three-output-peaks.csv')
for r in tables[0]:
    src=min((x for x in main if x['Case']==r[0]),key=lambda x:float(x['peak_reduction_percent']))
    assert r[1]==src['Story']
    for cell,key in zip(r[2:5],['P0_kN','P3_kN','peak_reduction_percent']):num(cell,src[key])
    for cell,key in zip(pairs(r[5]),['t_peak0_s','t_peak3_s']):num(cell,src[key])
for r in tables[1]:
    case,story=r[0].split('／');src=next(x for x in three if x['Case']==case and x['Story']==story)
    for cell,key in zip(r[1:4],['P0_kN','P3_kN','Pphysical_kN']):num(cell,src[key])
    for cell,key in zip(pairs(r[4]),['t_peak0_s','t_peak3_s','t_peakphysical_s']):num(cell,src[key])
    num(r[5],src['physical_over_label3_peak'])
for r in tables[2]:
    src=next(x for x in device if x['Case']==r[0])
    for cell,key in zip(pairs(r[1]),['QT_peak_abs_kN','t_QT_peak_s']):num(cell,src[key])
    for cell,key in zip(pairs(r[2]),['QD_J_resisting_peak_abs_kN','t_QD_abs_peak_s']):num(cell,src[key])
    for cell,key in zip(r[3:],['QD_J_resisting_at_QT_peak_kN','QD_at_QT_abs_percent_own_abs_peak','t_QD_minus_t_QT_s']):num(cell,src[key])
for r,src in zip(tables[3],shape):
    for cell,key in zip(r,['mode','directional_effective_mass_percent','phi_floor1_massnorm','phi_floor2_massnorm','QS2_coefficient_k2_times_phi2_minus_phi1']):num(cell,src[key])
for r in tables[4]:
    pos='0' if r[0].startswith('无装置') else '1';quantity='QS2' if '剪力' in r[0] else 'roof'
    src=next(x for x in anchors if x['position']==pos and x['quantity']==quantity and x['anchor']=='full_output_own_peak')
    for cell,key in zip(r[1:],['time_nondimensional','mode1_signed','mode2_signed','mode3_signed','three_mode_signed_sum']):num(cell,src[key])
for r,src in zip(tables[5],peaks):
    for cell,key in zip(r[:3],['mode','none_absolute_peak','story1_absolute_peak']):num(cell,src[key])
    num(r[3],-float(src['signed_peak_change_percent']))
for r in tables[6]:
    src=next(x for x in common if x['position']==('0' if r[1]=='无装置' else '1') and abs(float(x['time_nondimensional'])-float(r[0]))<1e-12)
    for cell,key in zip(r[2:],['mode1_signed','mode2_signed','mode3_signed','QS2_direct']):num(cell,src[key])
for r,src in zip(tables[7],reference):
    num(r[1],src['QS2_absolute_peak']);num(r[2],src['peak_time_nondimensional']);num(r[3],-float(src['peak_change_from_none_percent']))
formulas=re.findall(r'^\$\$(.+)\$\$$',text,re.M)
assert len(formulas)==3
assert r'q=\Phi^TMu' in formulas[0] and r'\sum_r(\ell_s^T\phi_r)q_r(t)' in formulas[0]
assert r'0.75E_{50,80}' in formulas[1] and r'1.05\omega_3t+\pi/4' in formulas[1]
assert r'\sin^2[\pi(t-b)/(e-b)]' in formulas[2] and 'b<t<e' in formulas[2]
assert len(main)==168 and len(three)==72
assert sum(float(r['Pphysical_kN'])>float(r['P3_kN']) for r in three)==34
assert sum(float(r['Pphysical_kN'])<float(r['P3_kN']) for r in three)==38
assert all(float(r['peak_reduction_percent'])>0 for r in main)
images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text);assert len(images)==3
bindings=json.loads((ROLES/'role5/R008-input-freeze.json').read_text(encoding='utf-8'))['sources']
pngknown={x['path']:x for x in bindings}
mapping=json.loads((ROLES/'role4/R008-render-map.json').read_text(encoding='utf-8'))['records']
figures=[]
for image in images:
    p=(PAPER.parent/image).resolve();got=ident(p);assert got==pngknown[str(p)];sources.append(got)
    record=next(x for x in mapping if x['approved_png_pending_visual_QA']==str(p))
    original=Path(record['source_svg']);revised=Path(record['revised_svg'])
    assert ident(original)['sha256']==record['source_sha256'] and ident(revised)['sha256']==record['revised_svg_sha256']
    def geometry(path):
        return [(x.tag,dict(x.attrib)) for x in ET.parse(path).getroot().iter() if x.tag.split('}')[-1] in ['polyline','circle','line','path','polygon']]
    assert geometry(original)==geometry(revised)
    figures.append({'png':got,'geometry_unchanged_from_frozen_source':True,'visually_inspected':True})
for x in sources:assert ident(Path(x['path']))==x
must=[{'id':'M1','line':109,'paragraph':'第4节，H2输入公式前的引入句','old':'H2采用两段包络调制的双频合成输入：','replacement':'H2有意包含第二阶及近第三阶频率，以检验高阶响应对局部输出的影响；下述重构差仅针对该合成输入，不作为天然地震输入的一般误差率。其表达式为：','reason':'公式及选频准确，但尚未直接说明选频目的与43%局部重构差的输入范围，需补一处简短正文条件。'}]
report='''# R010｜v008最后一次科学内容审核

**结论：数值、图表和机制解释通过；1项范围条件必须补入正文后可科学内容放行。无数值必改，无其他should项。** 本项仅审冻结v008，SHA256为d4c5f90155943ecd96663873dc42fed9f59e76509c0acb558f437e31baa91aec；不改共享稿，引用和语言由③⑥负责。

## 必改1：明确H2选频范围

位置：v008第109行，第4节H2公式前的引入句。

原句：“H2采用两段包络调制的双频合成输入：”

替换为：“H2有意包含第二阶及近第三阶频率，以检验高阶响应对局部输出的影响；下述重构差仅针对该合成输入，不作为天然地震输入的一般误差率。其表达式为：”

理由：载波ω2与1.05ω3、全局时间及包络均正确，但正文还应直接说明有意含较高阶频率，避免把43.3215%解释为一般实波误差率。这一处简短范围条件足够，无需增写大段免责声明；不要求改动8表或已有结论数值。

## 已通过的科学内容

- 8张表逐项对照已独审冻结小表，显示精度内一致；表1确为共同六工况各自最小层，全14工况最小记录另有明确区分。
- 表2的72项34高/38低和两示例比值正确，正文保留实体模型输入及完整主体身份未全部配对的范围；不裁决阻尼策略。
- 表3的负QD、J端抵抗项与装置对J外力−QD一致，分母为QD自身峰，58.6736%/62.5278%非贡献率；未扣算主体QS，32只记录未补作全88只力。
- 表4质量归一分量、87.0289%/8.1819%/4.7892%、第二层系数及roof第三系数准确；q配套与系数非占比的说明保留。
- 表5完整峰时项、43.3215%/41.6360%剪力低估和1.8839%/3.1416%roof高估准确，已区分同状态后验重构与重新减模态求解。
- 表6—7保留各阶全程峰与共同时间的区别；两时刻三项同向，未称反向抵消损失或各阶独立因果。
- 表8人工峰幅参照的三峰及三峰时准确，明确结果已知后构造、非可实现结构；合成峰时迁移不单独证明相位改变，差额未命名相位损失。
- 3个显示式与已审输出及H2定义一致；M/K/C、B、串联力方向、零初态、隐式中点、h=.005及40001节点准确采用。
- 3幅实际嵌入PNG均已看图：图1以各自绝对峰计算沿层减幅；图2保留上下不同纵轴、5—25s局部窗及QD方向；图3为同尺度19.7—20.5局部项。PNG身份与作者冻结输入一致，SVG曲线几何与冻结原图相同。
- 中英摘要与四条结论采用相同的168/72范围、质量和幅值比例，未引入额外因果结论。H2范围按上面M1在正文补足即可，摘要不必堆叠限制句。

无新数据重跑、响应数组读取、证明或参数扫描。作者实施M1后请冻结新版本及SHA；本审不将尚未实施的修改记作完成。
'''
p=OUT/'R010-v008-science-review.md';assert not p.exists();p.write_bytes(report.encode('utf-8'))
end=datetime.now(START.tzinfo);assert end<=DEADLINE
js('R010-checks.json',{'manuscript':ident(PAPER),'source_bindings':sources,'tables_checked':8,'display_numeric_cells_checked':count,'display_equations_checked':3,'figures':figures,'abstract_and_conclusions_read':True,'must':must,'should':[],'new_response_reads_ODE_proofs_scans':0})
js('R010-validation.json',{'status':'science data passed; one mandatory H2 input-scope sentence pending author','actual_start':START.isoformat(),'actual_end':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'within_8_minutes':end<=DEADLINE,'only_role2_written':True,'no_shared_manuscript_modification':True,'qa':{'UTF8_LF':'\r' not in report,'no_trailing_whitespace':all(x.rstrip()==x for x in report.splitlines()),'JSON_parse':True}})
js('R010-manifest.json',{'frozen_at':end.isoformat(),'files':[ident(OUT/n) for n in ['R010-audit-v008.py','R010-v008-science-review.md','R010-checks.json','R010-validation.json']]})
print(json.dumps({'status':'one scope must; numeric content passed','end':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'tables':8,'numeric_cells':count,'figures':3,'equations':3,'must':1,'should':0},ensure_ascii=False))
