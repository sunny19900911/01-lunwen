from pathlib import Path
import numpy as np,json,hashlib
from PIL import Image,ImageDraw,ImageFont
S=Path(__file__).resolve().parent;R=S.parents[2];O=S/'figures';O.mkdir(exist_ok=True)
out=O/'four-record-QT-QD-difference-v002.png';assert not out.exists()
cache=R/'research/sessions/20261019-2045/roles/data/local-cache/R002-native-horizontal/paired-layer-histories.npz'
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
im=Image.new('RGB',(1900,1390),'white');d=ImageDraw.Draw(im)
d.text((950,25),'实际方案软件剪力与装置水平分力的同刻对照',font=font(40),fill='#111111',anchor='mt')
colors=['#1f5b9a','#b6392e','#218a55'];labels=['QT：软件Bottom剪力','QT−QD：代数差','QD：J端结构内力抵抗项']
for i,(c,l)in enumerate(zip(colors,labels)):
 x=90+i*600;d.line((x,115,x+66,115),fill=c,width=5);d.text((x+80,115),l,font=font(28),fill='#111111',anchor='lm')
meta=[]
with np.load(cache,allow_pickle=False)as z:
 for k,(story,case)in enumerate([(8,'RH4X'),(8,'RH4Y'),(10,'RH4X'),(10,'RH4Y')]):
  a=z[f'Story{story}__{case}__{case[-1]}'];t,qt,qd=a[:,0],a[:,1],a[:,2];minus=qt-qd
  col=k%2;row=k//2;x0=135+col*920;y0=235+row*535;w=765;h=370;lim=8000 if story==8 else 5000
  sx=lambda x:x0+x/50*w;sy=lambda y:y0+h/2-y/(2*lim)*h
  d.text((x0+w/2,y0-58),f'第{story}层 {case}',font=font(34),fill='#111111',anchor='mm')
  d.text((x0+4,y0-22),'kN',font=font(28),fill='#222222',anchor='lb')
  for y in [-lim,-lim/2,0,lim/2,lim]:
   yy=sy(y);d.line((x0,yy,x0+w,yy),fill='#dddddd'if y else '#999999',width=1)
   d.text((x0-14,yy),f'{int(y)}',font=font(25),fill='#333333',anchor='rm')
  for x in [0,10,20,30,40,50]:
   xx=sx(x);d.line((xx,y0,xx,y0+h),fill='#eeeeee',width=1);d.text((xx,y0+h+13),str(x),font=font(26),fill='#333333',anchor='mt')
  d.rectangle((x0,y0,x0+w,y0+h),outline='#444444',width=2)
  # Every saved point is plotted, with no time shift or filtering.
  for yy,color,width in [(minus,colors[1],4),(qt,colors[0],3),(qd,colors[2],3)]:
   d.line([(sx(float(x)),sy(float(y)))for x,y in zip(t,yy)],fill=color,width=width)
  ip=int(np.argmax(abs(qt)));xp=sx(float(t[ip]))
  for y in range(y0,y0+h,15):d.line((xp,y,xp,min(y+8,y0+h)),fill='#444444',width=2)
  d.text((x0+w/2,y0+h+62),f'时间/s；虚线为QT自身峰时 {t[ip]:.2f}s',font=font(27),fill='#222222',anchor='mt')
  meta.append({'Story':story,'Case':case,'saved_points':len(t),'y_axis_symmetric_limit_kN':lim,'QT_peak_time_s':float(t[ip])})
d.text((950,1330),'QD=ΣnP；装置对J节点外力为−QD。差值仅作代数对照，不据曲线形状认定主体剪力。',font=font(27),fill='#333333',anchor='mm')
im.save(out)
(O/'figure-manifest-v002.json').write_text(json.dumps({'source_sha256':hashlib.sha256(cache.read_bytes()).hexdigest(),'png_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'png_bytes':out.stat().st_size,'size':[1900,1390],'panels':meta,'all_saved_points_no_smoothing':True,'root_visual_review_required':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(out)
