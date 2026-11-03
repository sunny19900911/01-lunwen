from pathlib import Path
import csv,json,html,math,hashlib
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent
def read(name):
 with (H/name).open(encoding='utf-8-sig')as f:return list(csv.DictReader(f))
rows=read('actual-versus-baseline-time-peak-72.csv');ranges=read('actual-layer-direction-ranges-24.csv')
class Plot:
 def __init__(self,w,h):
  self.w=w;self.h=h;self.im=Image.new('RGB',(w,h),'white');self.d=ImageDraw.Draw(self.im)
  self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/>']
 def text(self,x,y,t,size=28,color='#263449',anchor='mm',rotate=0):
  font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
  if rotate:
   box=font.getbbox(t);ww=box[2]-box[0]+8;hh=box[3]-box[1]+8
   img=Image.new('RGBA',(ww,hh),(255,255,255,0));dr=ImageDraw.Draw(img);dr.text((4-box[0],4-box[1]),t,font=font,fill=color)
   img=img.rotate(rotate,expand=True);self.im.paste(img,(int(x-img.width/2),int(y-img.height/2)),img)
  else:self.d.text((x,y),str(t),font=font,fill=color,anchor=anchor)
  an={'mm':'middle','lm':'start','rm':'end'}.get(anchor,'start');rt=f' transform="rotate({-rotate} {x} {y})"'if rotate else''
  self.s.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Microsoft YaHei, sans-serif" font-size="{size}" text-anchor="{an}" dominant-baseline="middle"{rt}>{html.escape(str(t))}</text>')
 def line(self,points,c='#dbe2eb',w=2,dash=False):
  if dash:
   (x1,y1),(x2,y2)=points;l=math.hypot(x2-x1,y2-y1)
   for b in range(0,int(l),15):
    e=min(l,b+9);self.d.line([(x1+(x2-x1)*b/l,y1+(y2-y1)*b/l),(x1+(x2-x1)*e/l,y1+(y2-y1)*e/l)],fill=c,width=w)
  else:self.d.line(points,fill=c,width=w)
  ds=' stroke-dasharray="9 6"'if dash else''
  self.s.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}'for x,y in points)+f'" fill="none" stroke="{c}" stroke-width="{w}"{ds}/>')
 def dot(self,x,y,c,r=7,fill=True,square=False):
  if square:self.d.rectangle((x-r,y-r,x+r,y+r),fill=c if fill else'white',outline=c,width=3);self.s.append(f'<rect x="{x-r}" y="{y-r}" width="{2*r}" height="{2*r}" fill="{c if fill else "white"}" stroke="{c}" stroke-width="3"/>')
  else:self.d.ellipse((x-r,y-r,x+r,y+r),fill=c if fill else'white',outline=c,width=3);self.s.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" fill="{c if fill else "white"}" stroke="{c}" stroke-width="3"/>')
 def save(self,name):
  png=H/(name+'.png');svg=H/(name+'.svg');assert not png.exists()and not svg.exists()
  self.im.save(png);svg.write_text('\n'.join(self.s+['</svg>']),encoding='utf-8')
P=Plot(1800,1120)
P.text(900,60,'实际阻尼器方案的分层剪力峰减幅',42)
P.text(900,115,'基准模型B与实际布置模型D；每方向RH4、SHW4、SHW7三输入',28,'#526175')
P.text(900,165,'横线：最小至最大值    圆点：中位值',27,'#526175')
for axis,left,right,color in [('X',140,835,'#235FB2'),('Y',1020,1715,'#BD641F')]:
 top,bottom=255,900
 xp=lambda v:left+(right-left)*v/50
 yp=lambda story:bottom-(story-1)*(bottom-top)/11
 P.text((left+right)/2,213,axis+'向输入／'+axis+'向响应',32)
 for v in [0,10,20,30,40,50]:
  x=xp(v);P.line([(x,top),(x,bottom)],'#E0E7EF',2);P.text(x,bottom+31,str(v),26)
 for st in range(1,13):
  y=yp(st);P.line([(left,y),(right,y)],'#EDF1F5',1);P.text(left-22,y,str(st),26,anchor='rm')
  q=next(r for r in ranges if r['Axis']==axis and r['Story']==f'Story{st}')
  lo,med,hi=[float(q[k])for k in ['min_reduction_percent','median_reduction_percent','max_reduction_percent']]
  assert 0<=lo<=med<=hi<=50
  P.line([(xp(lo),y),(xp(hi),y)],color,5);P.line([(xp(lo),y-7),(xp(lo),y+7)],color,3);P.line([(xp(hi),y-7),(xp(hi),y+7)],color,3);P.dot(xp(med),y,color,7)
 P.line([(left,top),(left,bottom),(right,bottom)],'#78879A',3)
 P.text(left-65,(top+bottom)/2,'楼层',28,rotate=90)
 P.text((left+right)/2,982,'剪力绝对峰减幅 / %',29)
 q=min([r for r in ranges if r['Axis']==axis],key=lambda r:float(r['min_reduction_percent']))
 P.text((left+right)/2,1036,f"最小：{q['min_case']}，第{q['Story'][5:]}层，{float(q['min_reduction_percent']):.4f}%",26,color)
P.text(900,1090,'每条减幅均由同一输入的两模型各自完整保存时程峰值计算',26,'#526175')
P.save('actual-device-story-reduction-range')

S=Plot(1800,1280)
S.text(900,58,'实际阻尼器方案的原峰时评价与自身控制峰对照',40)
S.text(900,115,'72条楼层成对记录；基准模型B与实际布置模型D',28,'#526175')
left,right,top,bottom=220,1210,210,1100
mx=max(max(float(r['r_at_percent']),float(r['r_peak_percent']))for r in rows);limit=math.ceil(mx/10)*10
xp=lambda x:left+(right-left)*x/limit;yp=lambda y:bottom-(bottom-top)*y/limit
for v in range(0,limit+1,10):
 x,y=xp(v),yp(v);S.line([(x,top),(x,bottom)],'#E0E7EF',2);S.line([(left,y),(right,y)],'#E0E7EF',2);S.text(x,bottom+36,str(v),26);S.text(left-26,y,str(v),26,anchor='rm')
S.line([(left,top),(left,bottom),(right,bottom)],'#748398',3)
S.line([(xp(0),yp(0)),(xp(limit),yp(limit))],'#8392A3',3,True)
for r in rows:
 x,y=float(r['r_at_percent']),float(r['r_peak_percent']);assert y<=x+1e-10
 c='#2866B7'if r['Axis']=='X'else'#BF6B86'
 S.dot(xp(x),yp(y),c,6,square=r['Axis']=='Y')
S.text((left+right)/2,1182,'仅按基准峰时评价的减幅 r_at / %',30)
S.text(70,(top+bottom)/2,'完整保存时程峰值减幅 r_D / %',30,rotate=90)
S.dot(1320,270,'#2866B7',8);S.text(1350,270,'X向记录',29,anchor='lm')
S.dot(1320,325,'#BF6B86',8,square=True);S.text(1350,325,'Y向记录',29,anchor='lm')
S.line([(1298,385),(1342,385)],'#8392A3',3,True);S.text(1362,385,'r_D = r_at',28,anchor='lm')
q=max(rows,key=lambda r:float(r['d_pp']));x=float(q['r_at_percent']);y=float(q['r_peak_percent'])
S.line([(xp(x),yp(x)),(xp(x),yp(y))],'#CB7D23',4)
S.dot(xp(x),yp(y),'#CB7D23',12,False)
S.line([(xp(x)+10,yp(y)),(1288,770)],'#CB7D23',2)
S.text(1300,695,f"{q['Case']}，第{q['Story'][5:]}层",29,anchor='lm')
S.text(1300,745,f"r_at = {x:.4f}%",27,anchor='lm')
S.text(1300,795,f"r_D = {y:.4f}%",27,anchor='lm')
S.text(1300,845,f"d = {float(q['d_pp']):.4f} 个百分点",27,'#AB5F0E',anchor='lm')
S.text(900,1240,'点到等值线的竖向差为d≥0，表示评价时刻造成的减幅读数差',27,'#526175')
S.save('actual-device-old-peak-vs-complete-peak')
record={'plots':['actual-device-story-reduction-range','actual-device-old-peak-vs-complete-peak'],'source72_sha256':hashlib.sha256((H/'actual-versus-baseline-time-peak-72.csv').read_bytes()).hexdigest(),'source24_sha256':hashlib.sha256((H/'actual-layer-direction-ranges-24.csv').read_bytes()).hexdigest(),'scatter_limit_percent':limit,'points':72,'range_rows':24,'model_identity':'B baseline versus D actual88 configuration; not M uniform modal reference','all_numbers_from_frozen_CSV':True,'new_response_calculations':False,'visual_review_pending':True}
(H/'plot-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
