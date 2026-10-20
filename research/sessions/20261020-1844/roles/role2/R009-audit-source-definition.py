from pathlib import Path
from datetime import datetime, timedelta
import ast
import hashlib
import json

OUT = Path(__file__).resolve().parent
SRC = OUT.parent / 'role1'
START = datetime.fromisoformat('2026-10-20T20:42:26.154046+08:00')
DEADLINE = START + timedelta(minutes=8)


def ident(p):
    b = p.read_bytes()
    return {'path': str(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}


def js(name, obj):
    p = OUT / name
    assert not p.exists(), p
    p.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    json.loads(p.read_text(encoding='utf-8'))


assert datetime.now(START.tzinfo) < DEADLINE
assert not (OUT / 'R009-validation.json').exists()
sources = []
for manifest in [SRC / 'R007-manifest.json', OUT / 'R008-manifest.json']:
    sources.append(ident(manifest))
    for r in json.loads(manifest.read_text(encoding='utf-8'))['files']:
        p = Path(r['path']) if 'path' in r else manifest.parent / r['file']
        got = ident(p)
        assert got['bytes'] == r['bytes'] and got['sha256'] == r['sha256']
        sources.append(got)
freeze = json.loads((SRC / 'R007-input-freeze.json').read_text(encoding='utf-8'))
evidence = json.loads((SRC / 'R007-source-evidence.json').read_text(encoding='utf-8'))
runner = Path(next(r['path'] for r in freeze['inputs'] if Path(r['path']).name == 'three_floor_prospective.py'))
prepath = Path(next(r['path'] for r in freeze['inputs'] if Path(r['path']).name == 'pre-run-freeze.json'))
formal = runner.parent / 'H021-delivery-manifest.json'
assert ident(formal)['sha256'] == freeze['H021_manifest_sha256'] == evidence['H021_manifest_sha256']
sources.append(ident(formal))
entries = json.loads(formal.read_text(encoding='utf-8'))['files']
for r in freeze['inputs']:
    p = Path(r['path'])
    got = ident(p)
    assert got['bytes'] == r['bytes'] and got['sha256'] == r['sha256']
    original = next(e for e in entries if Path(e['path']).resolve() == p.resolve())
    assert got['bytes'] == original['bytes'] and got['sha256'] == original['sha256']
    sources.append(got)
text = runner.read_text(encoding='utf-8')
lines = text.splitlines()
# Parse only; never import, compile, execute, or evaluate this runner.
tree = ast.parse(text)
anchors = {}
for key, line in evidence['runner_line_anchors'].items():
    actual = lines[line-1]
    assert actual == evidence['quoted_line_text'][key]
    anchors[key] = {'line_1based': line, 'text': actual}
expected = {
    10: 'MASS=np.array([1.,1.2,.8]);M=np.diag(MASS);STIFF=np.array([1.4,1.,.7]);D=np.array([[1.,0.,0.],[-1.,1.,0.],[0.,-1.,1.]])',
    11: 'K=D.T@np.diag(STIFF)@D;C=.02*K;KAPPA=.5;CD=.02;ALPHA=.3;Q=1/ALPHA',
    12: 'BS={0:np.zeros(3),1:D[0].copy(),2:D[1].copy(),3:D[2].copy()}',
    27: 'def envelope(t,b,e):return np.where((t>b)&(t<e),np.sin(np.pi*(t-b)/(e-b))**2,0.)',
    29: 'w1,w2,w3=FREQUENCIES',
    33: "if case=='H2_envelope':return .1*(envelope(t,0,30)+.75*envelope(t,50,80))*(.75*np.sin(w2*t)+.25*np.sin(1.05*w3*t+math.pi/4))",
    35: 'def g(force):return math.copysign((abs(force)/CD)**Q,force)',
    65: 'u1=u2=u3=v1=v2=v3=F=Win=Db=Dd=Eold=0.;root=mom=kin=const=bal=ident=0.;minimumDb=minimumDd=math.inf',
    68: 'ag=float(forcing[n-1]);p1,p2,p3=-ag,-1.2*ag,-.8*ag',
    73: 'vm1,vm2,vm3=af1-a*w1*Fm,af2-a*w2*Fm,af3-a*w3*Fm',
    74: 'un1,un2,un3=u1+h*vm1,u2+h*vm2,u3+h*vm3;vn1,vn2,vn3=2*vm1-v1,2*vm2-v2,2*vm3-v3;Fn=2*Fm-F if device else 0.',
    81: 'rf=(Fn-F)/KAPPA-h*(b1*vm1+b2*vm2+b3*vm3-g(Fm)) if device else 0.',
    92: 'z[n,1:]=(u1,u2,u3,v1,v2,v3,F,Win,Db,Dd,Eold,balance)',
    169: 'for h in [.01,.005]:',
    172: "z,m=integrate(case,position,h,inputs[case,h]);m['stage']=stage;m['run_number']=RUNS",
    186: 'a=acceleration(case,(np.arange(round(200/h))+.5)*h);assert float(np.max(abs(a)))<=.1*(1+1e-14)',
    187: "inputs[case,h]=a;descriptors.append({'case':case,'h':h,'sha256':hashlib.sha256(a.astype('<f8').tobytes()).hexdigest(),",
}
for line, value in expected.items():
    assert lines[line-1].strip() == value
integrator = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'integrate')
loop = next(n for n in integrator.body if isinstance(n, ast.For))
assert integrator.lineno == 61 and loop.lineno == 66
assert all(not isinstance(n, ast.If) or '50' not in ast.unparse(n.test) for n in ast.walk(loop))
pre = json.loads(prepath.read_text(encoding='utf-8'))
own = json.loads((OUT / 'R008-checks.json').read_text(encoding='utf-8'))
assert pre['M'] == own['M'] and pre['K'] == own['K']
assert all(abs(pre['C'][i][j]-.02*pre['K'][i][j]) < 1e-15 for i in range(3) for j in range(3))
assert pre['B_ports']['1'] == [1., 0., 0.]
assert pre['B_ports']['0'] == [0., 0., 0.]
assert (pre['kappa'], pre['c'], pre['alpha']) == (.5, .02, .3)
meta = next(r for r in pre['input_arrays'] if r['case'] == 'H2_envelope' and r['h'] == .005)
assert meta == evidence['H2_h005_input_metadata']
assert meta['sha256'] == '468bcb0b8f39080b0b50e09d8d188741ae28bff5de3f4dcbe3d683160664058a'
assert meta['midpoint_sample_peak'] == .08480783895471444
for r in sources:
    assert ident(Path(r['path'])) == r
report = '''# R009｜H2输入与数值定义源码独审

**采用：角色1冻结R007的H2表达式、模型参数、初态和离散说明与原H021正式源码一致，无数值或定义必改项。写稿必须补足“有意含较高阶频率的合成输入”这一适用范围限定。** 本项只做文本、AST与JSON核查，未执行、导入runner，也未重建输入数组、读取响应NPZ或求解ODE。

## 源身份与准确行号

原H021清单SHA为971ff81e6af86f179268bc3332e388d8676952d71aab7758cd34de2f45f263e7；runner为4554d99b467b429631fe60d7a70af72107962d1cfd33bd1da088ed5e8a2172b8；pre-run-freeze为506258b0aa9858f9424eae4ba7305e1ebcb18cb743f6fe54a0908705491c8572。均与正式清单逐项匹配。

以下均按原three_floor_prospective.py的UTF-8源码1起算。完整路径、逐行原文与SHA见R009-checks.json，不把过程说明放入论文正文。

|核查项|源码行|
|---|---|
|M、D、层刚度；K与C=.02K；Maxwell参数及B端口|10—12|
|未装置主体特征频率|14、29|
|正弦平方包络、H2完整表达式|27、33|
|逆黏壶g(F)、标量中点求根|35—43|
|步长h/2及隐式中点矩阵、状态网格|61—64|
|u、v及F零初态；单一连续时间循环|65—66|
|输入−M1ag、中点装置抵抗项及节点更新|68—74、80—81|
|保存更新后的整步节点状态|91—92|
|h=.005进入integrate，并保存其状态|169、172—174|
|全窗0—200的中点输入采样，不再归一|185—188|

## 定义核对

H2=0.1[E_(0,30)(t)+0.75E_(50,80)(t)][0.75sin(ω2t)+0.25sin(1.05ω3t+π/4)]，E_(b,e)=sin²[π(t−b)/(e−b)]仅在b<t<e取值，其他时刻为零。两段包络互不重叠，载波一直使用全局t；第二段不把载波替换为t−50，也不重置u、v或F。系数0.1是表达式系数和解析上界，不是强制样本峰归一目标；冻结h=.005中点样本峰为0.08480783895471444，本项仅核旧元数据与SHA，未重新生成样本。

M=diag(1,1.2,.8)，K=[[2.4,−1,0],[−1,1.7,−.7],[0,−.7,.7]]，C=.02K，均与已审固定基模型一致。ω2≈1.2014294628、ω3≈1.7359585286，第二载波实际为1.05ω3。层1端口B=(1,0,0)ᵀ，固定基底下δ=Bᵀu=u1。结构方程抵抗项为+BF，装置对结构的外力为−BF；串联方程Ḟ=κ[Bᵀv−g(F)]，κ=.5、c=.02、α=.3，g(F)=sgn(F)(|F|/c)^(1/α)。无装置F恒为零，但C保留。

源码的a=h/2，中点未知量Fm配合v_m求解，再更新u_(n+1)=u_n+h v_m、v_(n+1)=2v_m−v_n、F_(n+1)=2Fm−F_n，与隐式中点定义一致。h=.005同时为积分步长及每步节点保存步长；0—200共40000步、含零初态40001点。t_(n+1/2)取外力，保存的u/v/F为整步节点状态，不把中点值称为节点值。全窗包含两段间歇和80之后的自由衰减段。

## 写稿必须保留的适用范围

H2按第二阶与近第三阶频率有意构造，用于检验较高阶响应对局部输出的影响。它不是天然地震记录或一般实波抽样。因此无装置QS2后验两阶重构低估43.3215%只属于该模型、该合成输入及所用保存网格；不能写成一般地震输入下的错误率、实际建筑漏模态比例或两阶重解/FNA误差。

可直接写稿：“采用两段包络调制的双频合成输入H2，载波选为未设装置主体的ω2与1.05ω3，以考察较高阶响应对局部层剪力的影响；载波使用全局时间，状态连续积分且不在第二段输入前重置。本文所列43.3215%的第二层剪力峰后验重构差，是该限定算例的结果，不能推广为天然地震输入的一般误差率。”
'''
p = OUT / 'R009-H2-source-definition-review.md'
assert not p.exists()
p.write_bytes(report.encode('utf-8'))
end = datetime.now(START.tzinfo)
assert end <= DEADLINE
js('R009-checks.json', {'source_bindings': sources, 'runner_path': str(runner), 'role1_all_quoted_anchors_verified': anchors, 'independent_line_checks': {str(k): lines[k-1] for k in expected}, 'model_matches_previous_review': True, 'H2_h005_frozen_metadata': meta, 'AST_parse_only': True, 'runner_imports_executions': 0, 'input_regenerations': 0, 'response_state_reads': 0, 'new_ODE': 0})
js('R009-validation.json', {'status': 'adopt source definitions; retain intentional higher-mode synthetic-input scope', 'actual_start': START.isoformat(), 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'within_8_minutes': end <= DEADLINE, 'only_role2_written': True, 'no_runner_execution_new_ODE_ETABS_Git_automation_agents': True, 'qa': {'UTF8_LF': '\r' not in report, 'no_trailing_whitespace': all(x.rstrip() == x for x in report.splitlines()), 'JSON_parse': True}})
js('R009-manifest.json', {'frozen_at': end.isoformat(), 'files': [ident(OUT / n) for n in ['R009-audit-source-definition.py', 'R009-H2-source-definition-review.md', 'R009-checks.json', 'R009-validation.json']]})
print(json.dumps({'status': 'adopt source definition with scope', 'actual_end': end.isoformat(), 'elapsed_seconds': (end-START).total_seconds(), 'role1_anchors_verified': len(anchors), 'independent_line_checks': len(expected), 'runner_executions': 0}, ensure_ascii=False))
