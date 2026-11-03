from pathlib import Path
import csv,math,html,json,hashlib
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent
with (H/'three-model-common-six-records-72.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
W,HGT=1800,1110
im=Image.new('RGB',(W,HGT),'white');d=ImageDraw.Draw(im)
fontpath=Path('C:/Windows/Fonts/msyh.ttc');assert fontpath.is_file()
def font(n):return ImageFont.truetype(str(fontpath),n)
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HGT}" viewBox="0 0 {W} {HGT}"><rect width="100%" height="100%" fill="white"/>']
def txt(x,y,s,size=26,color='#243044',anchor='mm'):
 d.text((x,y),s,font=font(size),fill=color,anchor=anchor)
 an={'mm':'middle','lm':'start','rm':'end'}.get(anchor,'start')
 sv.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Microsoft YaHei, sans-serif" font-size="{size}" text-anchor="{an}" dominant-baseline="middle">{html.escape(str(s))}</text>')
def line(xy,color='#d6dde6',width=2):
 d.line(xy,fill=color,width=width);sv.append(f'<polyline points="'+ ' '.join(f'{x:.3f},{y:.3f}'for x,y in xy)+f'" fill="none" stroke="{color}" stroke-width="{width}"/>')
def dot(x,y,color,r=6):
 d.ellipse((x-r,y-r,x+r,y+r),fill=color);sv.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" fill="{color}"/>')
txt(900,62,'共有六工况下三模型楼层剪力峰值包络',40)
txt(900,117,'每个方向取RH4、SHW4、SHW7三输入中的最大绝对峰',27,'#536174')
styles=[('P_B_kN','基准模型','#65758A'),('P_M_kN','附加3个百分点模态阻尼','#245DC1'),('P_D_kN','实际布置阻尼器模型','#C26623')]
XMAX=math.ceil(max(float(r[f])for r in rows for f,_,_ in styles)/3000)*3000
for xx,(_,name,c) in zip([200,650,1260],styles):
 line([(xx-60,177),(xx+10,177)],c,5);dot(xx-25,177,c);txt(xx+25,177,name,27,anchor='lm')
out=[]
for axis,left,right in [('X',125,825),('Y',1010,1710)]:
 top,bottom=255,945
 txt((left+right)/2,222,axis+'向输入／'+axis+'向楼层剪力',31)
 def xp(v):return left+(right-left)*v/XMAX
 def yp(story):return bottom-(story-1)*(bottom-top)/11
 for tick in range(0,XMAX+1,3000):
  x=xp(tick);line([(x,top),(x,bottom)],'#E3E8EF',2);txt(x,bottom+31,str(tick),24)
 for story in range(1,13):
  y=yp(story);line([(left,y),(right,y)],'#ECF0F4',1);txt(left-20,y,str(story),24,anchor='rm')
 line([(left,top),(left,bottom),(right,bottom)],'#718096',3)
 for field,name,color in styles:
  pts=[]
  for story in range(1,13):
   rr=[r for r in rows if r['Axis']==axis and r['Story']==f'Story{story}']
   v=max(float(r[field]) for r in rr);assert v<=XMAX
   pts.append((xp(v),yp(story)))
  line(pts,color,5)
  for x,y in pts:dot(x,y,color,6)
 for story in range(1,13):
  rr=[r for r in rows if r['Axis']==axis and r['Story']==f'Story{story}']
  out.append({'Axis':axis,'Story':f'Story{story}',**{f:max(float(r[f]) for r in rr)for f,_,_ in styles},'actual_governing_input':max(rr,key=lambda r:float(r['P_D_kN']))['Case']})
 txt((left+right)/2,1010,'剪力绝对峰包络 / kN',27)
txt(40,590,'楼层',25,anchor='lm')
txt(900,1066,'各层分别选取控制输入；该包络不表示同一时刻的沿层剪力分布',25,'#536174')
sv.append('</svg>')
for p in [H/'common-six-three-model-peak-envelope.png',H/'common-six-three-model-peak-envelope.svg',H/'common-six-peak-envelope-24.csv']:assert not p.exists()
im.save(H/'common-six-three-model-peak-envelope.png')
(H/'common-six-three-model-peak-envelope.svg').write_text('\n'.join(sv),encoding='utf-8')
with (H/'common-six-peak-envelope-24.csv').open('x',encoding='utf-8',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
print(json.dumps({'png':'common-six-three-model-peak-envelope.png','pixels':[W,HGT],'plot_data_rows':len(out),'physical_inference':'absolute native peaks only, no causal reduction claim'},ensure_ascii=False))
