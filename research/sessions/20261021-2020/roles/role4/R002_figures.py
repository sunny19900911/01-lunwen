from pathlib import Path
import csv,html,hashlib,json,math
from datetime import datetime,timezone
O=Path(__file__).resolve().parent;R=O.parents[4];S=R/'research/sessions/20261021-0737/roles/role4/R002-story-axis-summary-24.csv';D=O/'R001-d-168.csv'
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def tx(x,y,t,size=13,anchor='start',extra=''):return f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" {extra}>{html.escape(str(t))}</text>'
def ln(x1,y1,x2,y2,c='#dce3e8',w=1,extra=''):return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{c}" stroke-width="{w}" {extra}/>'
def head(w,h,title):return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><title>{html.escape(title)}</title><rect width="100%" height="100%" fill="white"/><g font-family="Microsoft YaHei,Segoe UI,Arial,sans-serif" fill="#243642">']
def put(n,p):
 f=O/n;assert not f.exists();f.write_text('\n'.join(p+['</g></svg>']),encoding='utf-8')
stats=read(S);rows=read(D);assert len(stats)==24 and len(rows)==168
p=head(1080,740,'各楼层水平剪力峰值降幅的多输入分布');p += [tx(540,35,'各楼层水平剪力峰值降幅的多输入分布',21,'middle'),tx(540,64,'基准模型与增加3个百分点模态阻尼模型；每方向7个工况',14,'middle'),tx(540,94,'横线：最小—最大值；圆点：中位数',13,'middle')]
for axis,left,col in [('X',115,'#216d9d'),('Y',655,'#b66a23')]:
 x=lambda v:left+v/35*340;y=lambda s:610-(s-1)/11*475
 p.append(tx(left+170,119,axis+'向输入 / '+axis+'向响应',16,'middle'))
 for s in range(1,13):p += [ln(left,y(s),left+340,y(s)),tx(left-12,y(s)+4,'第'+str(s)+'层',12,'end')]
 for v in range(0,36,5):p += [ln(x(v),135,x(v),610),tx(x(v),637,v,12,'middle')]
 p += [ln(left,135,left,610,'#4a5a65',1.3),ln(left,610,left+340,610,'#4a5a65',1.3),tx(left+170,674,'剪力峰值降幅 / %',15,'middle')]
 for r in stats:
  if r['Axis']!=axis:continue
  yy=y(int(r['Story'][5:]));lo=x(float(r['minimum_reduction_percent']));hi=x(float(r['maximum_reduction_percent']));md=x(float(r['median_reduction_percent']))
  p += [ln(lo,yy,hi,yy,col,3),ln(lo,yy-4,lo,yy+4,col,1.5),ln(hi,yy-4,hi,yy+4,col,1.5),f'<circle cx="{md:.3f}" cy="{yy:.3f}" r="4.5" fill="{col}"/>']
p.append(tx(540,717,'输入：R1、RH4、SHW3、SHW4、SHW5、SHW6、SHW7；X、Y向分别统计',12,'middle'));put('R002-story-range-median.svg',p)
mx=5*math.ceil(max(max(float(r['r_at_percent']),float(r['r_peak_percent'])) for r in rows)/5);left=110;top=115;size=540
x=lambda v:left+v/mx*size;y=lambda v:top+size-v/mx*size
p=head(1040,790,'原峰时评价与完整时程峰值减幅对照');p += [tx(520,35,'原峰时评价与完整时程峰值减幅对照',21,'middle'),tx(520,65,'14个方向工况 × 12层；基准模型与增加模态阻尼模型',14,'middle')]
for v in range(0,int(mx)+1,5):p += [ln(x(v),top,x(v),top+size),ln(left,y(v),left+size,y(v)),tx(x(v),top+size+25,v,12,'middle'),tx(left-12,y(v)+4,v,12,'end')]
p += [ln(left,top,left,top+size,'#4a5a65',1.3),ln(left,top+size,left+size,top+size,'#4a5a65',1.3),ln(x(0),y(0),x(mx),y(mx),'#79838b',1.5,'stroke-dasharray="6 4"')]
for r in rows:
 xx=x(float(r['r_at_percent']));yy=y(float(r['r_peak_percent']));col='#216d9d' if r['Axis']=='X' else '#a15983'
 if r['Axis']=='X':p.append(f'<circle cx="{xx:.3f}" cy="{yy:.3f}" r="3.2" fill="{col}" fill-opacity=".68"/>')
 else:p.append(f'<rect x="{xx-2.8:.3f}" y="{yy-2.8:.3f}" width="5.6" height="5.6" fill="{col}" fill-opacity=".68"/>')
e=next(r for r in rows if r['Case']=='SHW7Y' and r['Story']=='Story6');a=float(e['r_at_percent']);b=float(e['r_peak_percent'])
p += [ln(x(a),y(a),x(a),y(b),'#c4771e',2.3),f'<circle cx="{x(a):.3f}" cy="{y(b):.3f}" r="6" fill="none" stroke="#c4771e" stroke-width="2.2"/>',ln(x(a)+7,y(b),690,440,'#c4771e',1.2),tx(700,185,'● X向工况',14),tx(700,217,'■ Y向工况',14),ln(700,253,735,253,'#79838b',1.5,'stroke-dasharray="6 4"'),tx(745,258,'y = x',14),tx(700,370,'SHW7Y，第6层',15),tx(700,400,f'({a:.4f}%, {b:.4f}%)',14),tx(700,430,f'两种评价相差{float(e["d_pp"]):.4f}个百分点',14),tx(380,714,'原峰时评价减幅 r_at / %',15,'middle'),tx(30,385,'完整保存时程减幅 r_peak / %',15,'middle','transform="rotate(-90 30 385)"'),tx(520,760,'r_at − r_peak = d；差值为原峰时评价相对完整时程评价的偏差，不表示相位损失。',12,'middle')]
put('R002-peak-evaluation-scatter.svg',p)
print('SVGs saved '+datetime.now(timezone.utc).isoformat())
