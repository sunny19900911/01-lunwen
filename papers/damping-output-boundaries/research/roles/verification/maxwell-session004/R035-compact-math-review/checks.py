"""Static compact integration/decimal checks only, no source code or data replay."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,re
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
DRAFT=ROOT/'papers/damping-output-boundaries/manuscript/maxwell-paper-compact-v001.md'
AUTHOR=ROOT/'papers/damping-output-boundaries/research/roles/writing/maxwell-session004/compact-paper-v001'
def record(p):
    assert p.suffix.lower() not in ['.npz','.npy','.pdf'],p
    b=p.read_bytes();return {'path':str(p.resolve()),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
assert record(DRAFT)['sha256']=='560d950d3ede543a3ddb78b937803ad750dec1d685a9d16d62ea8a8c90be6d78'
for x in read(AUTHOR/'freeze.json')['files']:assert record(Path(x['path']))==x
refs=read(AUTHOR/'input-freeze.json')['sources']
for x in refs:
    r=record(Path(x['path']));assert r['bytes']==x['bytes'] and r['sha256']==x['sha256']
sources=[record(p) for p in sorted(set([DRAFT]+list(AUTHOR.iterdir())+[Path(x['path']) for x in refs])) if p.is_file()]
text=DRAFT.read_text(encoding='utf-8');lines=text.splitlines()
assert 'C026令外力(1,1)ᵀ[sin(t)+d(t)]' in lines[57]
long=ROOT/'papers/damping-output-boundaries/manuscript/maxwell-engineering-draft-v010.md'
longlines=long.read_text(encoding='utf-8').splitlines()
assert '名义正弦在[0,T]外取零' in longlines[284]
assert '位移增量RMS为分母' in lines[40] and '各条原始Δd的RMS为分母' in longlines[158]
assert '对标准单轴串联模型' in text and '这不是属性真值' in text
assert '末动能加势能仍为0.038525' in longlines[115]
adopt25=read(ROOT/'research/sessions/20261017-2109/R011-nonlinear-certificate-adoption.json')
for key,bound in [('early_upper_candidate','1.325'),('tail_upper_candidate','1.325')]:assert F(float.fromhex(adopt25['bound_binary64_hex'][key]))<F(bound)
assert F(float.fromhex(adopt25['bound_binary64_hex']['fixed_T_lower_candidate']))>F('8.809')
assert F(float.fromhex(adopt25['bound_binary64_hex']['gap_lower_candidate']))>F('7.485')
adopt27=read(ROOT/'research/sessions/20261017-2109/R013-addition-certificate-adoption.json')
assert F(float.fromhex(adopt27['bound_hex']['D_witness_lower']))>F('4.349')
assert F(float.fromhex(adopt27['bound_hex']['gap_lower']))>F('1.939')
assert F('1.325')+F('2.83')==F('4.155') and F('8.809')-F('2.83')==F('5.979')
assert F('5.979')-F('4.155')==F('1.824')
adopt31=read(ROOT/'research/sessions/20261017-2109/R015-adoption.json')['accepted']['M-C031']
assert adopt31['comparison_scope'].startswith('4 max/RMS stats plus8 fixed-point values')
assert not adopt31['strict_true_solution_or_engineering_prediction']
assert '4项max/RMS统计及四点8个预测值' in text and '非整条预测逐点比较' in text
assert '绝对q也不是装置引起的差模态' in text
assert 'ε_tot=η_U+η_c+ε' in text and '未知56只的ε不能设零' in text
links=[]
for target in re.findall(r'\]\(([^)]+)\)',text):
    if '://' not in target:
        p=(DRAFT.parent/target).resolve();assert p.is_file();links.append(str(p))
findings={'required_changes':1,'recommendations':2,'mustfixes':[{'id':'M1','file':str(DRAFT.resolve()),'line':58,'category':'mathematical input/quantifier transcription',
 'original':lines[57],'problem':'Only d is time-supported; sin(t) is left running after T, so displayed input differs from adopted C026 and its stop-tail/area40 premise.',
 'minimal_replacement':'令s0(t)=sin(t)·1_[0,20π](t)。C026的外力为(1,1)ᵀ[s0(t)+d(t)]，其中d连续、支撑于[0,20π]且∫_0^{20π}|d(t)|dt≤2；A/B及两个输入分量共享同一d。',
 'source':str(long.resolve()),'source_line':285}],
 'clarifications':[{'id':'C1','line':51,'scope':'Table2 lines54-56','kind':'quantity-definition clarification; caption already supports amplitude interpretation, not counted as certain scientific error',
 'minimal_replacement':'表头改为“固定u1的绝对峰/固定点绝对幅值界”，并把B固定T/D固定真点写为|u1,B(T)|/|u1,D(t*)|的下界。'},
 {'id':'C2','line':43,'kind':'native-source terminology clarification, not counted as measured device-energy claim',
 'minimal_replacement':'能量账目保留206个微小负Link增量及非零的导出末动能与势能之和；……',
 'reason':'Source is native end kinetic+potential, not authenticated actual Maxwell F_T²/(2κ) with unknown κ.'}],
 'unchanged_frozen_v001':True}
for x in sources:assert record(Path(x['path']))==x
write(HERE/'findings.json',findings);write(HERE/'source-freeze.json',sources)
print(json.dumps({'required_changes':1,'clarifications':2,'source_count':len(sources),'links_verified':len(links),'safe_decimal_transcriptions_passed':True,'no_source_or_draft_modified':True}))
