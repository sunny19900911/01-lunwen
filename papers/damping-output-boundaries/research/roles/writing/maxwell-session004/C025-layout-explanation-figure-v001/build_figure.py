"""C025 topology and certified bounds only. No data histories or ODE. Refuse existing outputs."""
import argparse,hashlib,json,sys,datetime
from pathlib import Path
from fractions import Fraction
from reportlab.graphics.shapes import Drawing,Rect,String,Line,PolyLine
from reportlab.graphics import renderSVG
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import reportlab
p=argparse.ArgumentParser();p.add_argument('--repo',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();R=a.repo.resolve();D=a.out.resolve();D.mkdir(parents=True,exist_ok=True)
for n in ['C025_layout_explanation.svg','run-record.json']:assert not (D/n).exists(),n
def ident(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
rels=['research/sessions/20261017-2109/R011-nonlinear-certificate-adoption.json','research/sessions/20261017-2109/R011-certificate-adoption.md','research/sessions/20261017-2109/layout-nonlinear03-protocol-v001.json','papers/damping-output-boundaries/manuscript/maxwell-paper-compact-v002.md','papers/damping-output-boundaries/manuscript/maxwell-engineering-draft-v010.md','research/sessions/20261017-2109/figures/build_native_energy_coverage.py']
sources=[ident(R/x) for x in rels];ad=json.loads((R/rels[0]).read_text(encoding='utf-8'));sd=ad['safe_decimal_statements'];assert [sd[x] for x in ['A_fulltime_peak_upper','B_at_T_lower','gap_lower']]==['1.325','8.809','7.485']
F=lambda x:Fraction.from_float(float.fromhex(ad['bound_binary64_hex'][x]));assert F('early_upper_candidate')<Fraction('1.325') and F('tail_upper_candidate')<Fraction('1.325') and F('fixed_T_lower_candidate')>Fraction('8.809') and F('gap_lower_candidate')>Fraction('7.485')
font=Path('C:/Windows/Fonts/simhei.ttf');pdfmetrics.registerFont(TTFont('SimHei',str(font)));W,H=1200,840;d=Drawing(W,H);ink='#172c40';muted='#4c5c6a';blue='#375e7a';orange='#bc6b42';red='#a4433d';grid='#dce3e8'
def col(x):return HexColor(x)
def text(x,y,t,size=16,color=ink,anchor='start'):
 d.add(String(x,y,t,fontName='SimHei',fontSize=size,fillColor=col(color),textAnchor=anchor))
def line(x1,y1,x2,y2,color=muted,width=1.8):d.add(Line(x1,y1,x2,y2,strokeColor=col(color),strokeWidth=width))
def spring(x1,y1,x2,y2,color=muted,width=1.8):
 if y1==y2:
  pts=[(x1,y1),(x1+12,y1)]+[(x1+12+(x2-x1-24)*i/12,y1+(6 if i%2 else -6)) for i in range(1,12)]+[(x2-12,y1),(x2,y2)]
 else:
  pts=[(x1,y1),(x1,y1-10)]+[(x1+(6 if i%2 else -6),y1-10+(y2-y1+20)*i/10) for i in range(1,10)]+[(x2,y2+10),(x2,y2)]
 d.add(PolyLine(pts,strokeColor=col(color),strokeWidth=width,fillColor=None))
def dashpot(x,top,bottom):
 line(x,top,x,top-12,orange,2.5);line(x-10,top-12,x+10,top-12,orange,2.5);line(x-10,top-12,x-10,bottom+11,orange,2.5);line(x+10,top-12,x+10,bottom+11,orange,2.5);line(x-7,bottom+17,x+7,bottom+17,orange,2.5);line(x,bottom+17,x,bottom,orange,2.5)
def panel(left,label,port):
 d.add(Rect(left,256,550,365,rx=10,ry=10,strokeColor=col(grid),strokeWidth=1.2,fillColor=col('#fbfcfd')));text(left+22,592,label,21)
 for i,nx in enumerate([left+140,left+420],1):
  is_target=i==1;d.add(Rect(nx-34,500,68,44,rx=6,ry=6,strokeColor=col(red if is_target else blue),strokeWidth=2.7 if is_target else 1.8,fillColor=col('#fff8f5' if is_target else '#f1f5f8')));text(nx,515,'质量'+str(i),17,anchor='middle');text(nx,564,'固定目标 u1' if is_target else 'u2',17,red if is_target else muted,'middle')
  line(nx,500,nx,480);line(nx,480,nx+28,480);spring(nx+28,480,nx+28,365);text(nx+28,340,'对地弹性',14,muted,'middle')
  if i==port:
   x=nx-28;line(nx,480,x,480,orange,2.5);spring(x,480,x,432,orange,2.5);dashpot(x,432,383);line(x,383,x,365,orange,2.5);text(x-17,423,'Maxwell',14,orange,'end')
 spring(left+174,522,left+386,522);text(left+280,544,'正连接 ε=0.001',15,muted,'middle')
 line(left+65,365,left+495,365,muted,1.8)
 for xx in range(int(left+70),int(left+495),13):line(xx,365,xx-6,358,muted,1)
 text(left+280,318,'固定参考端',12,muted,'middle')
 text(left+280,294,'A：真实全时绝对峰' if port==1 else 'B：真实固定T绝对幅值',15,blue if port==1 else orange,'middle');text(left+280,265,'< 1.325' if port==1 else '> 8.809',27,blue if port==1 else orange,'middle')
d.add(Rect(0,0,W,H,strokeColor=None,fillColor=col('#ffffff')))
text(600,793,'同一耗能历史，固定位置的峰值仍可不同',29,ink,'middle');text(600,765,'C025 · 无量纲双质量连接拓扑示意 · 不表示楼层或真实几何',17,muted,'middle')
text(600,724,'同一主体 M/K/C（物理C相同）  ·  同一器件 κ、c，α=0.3',19,ink,'middle');text(600,690,'共同有限输入：0—20π为同向正弦，之后为0；全部初态为0',17,muted,'middle');text(600,650,'固定目标始终是u1，只有Maxwell连接端口改变',18,red,'middle')
panel(25,'布局A：器件接质量1',1);panel(625,'布局B：同一器件接质量2',2)
text(600,225,'两布局的全时绝对峰差：B − A > 7.485',22,ink,'middle');text(600,202,'仅显示认证界，不是实测峰；差额由原有向端点给出，不由显示小数相减',13,muted,'middle')
d.add(Rect(50,122,1100,61,rx=7,ry=7,strokeColor=None,fillColor=col('#f1f5f8')));text(600,159,'相同：所列整体储能、背景/器件耗散、输入功，以及器件F、总δ历史',18,blue,'middle');text(600,136,'同定义能量比仅在分母非零时相同',13,muted,'middle')
text(600,98,'u2交换；两位置全局最大值相同。A并非整体更优。',18,muted,'middle');text(600,59,'整体耗能相同，不能唯一确定某一位置的最大反应。',23,ink,'middle');text(600,24,'经典构造 · 条件数值合同见C025采用记录 · 非真实建筑或布置建议',14,muted,'middle')
svg=D/'C025_layout_explanation.svg';renderSVG.drawToFile(d,str(svg));assert sources==[ident(R/x) for x in rels]
record=dict(generated_at=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),python=sys.version,reportlab=reportlab.Version,renderer='reportlab.graphics.renderSVG',font=dict(name='SimHei',path=str(font)),script=ident(Path(__file__)),sources=sources,svg=ident(svg),figure_kind='topology plus certified inequalities;not timehistory or measuredpeak',no_solver_or_rawarrays=True,actual_C_network_not_drawn=True,decimal_Fraction_directions_verified=True)
(D/'run-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(dict(svg=ident(svg),source_count=len(sources)),ensure_ascii=False))
