from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,html,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[4];O=H/'R002';O.mkdir(exist_ok=True)
cache=R/'research/sessions/20261019-2045/roles/data/local-cache/R002-native-horizontal/paired-layer-histories.npz'
source_table=R/'research/sessions/20261019-2045/roles/data/R002-native-horizontal/layer-axis-peaks-48.csv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(cache)
with source_table.open(encoding='utf-8-sig')as f:meta=list(csv.DictReader(f))
arrays={};checks=[]
with np.load(cache,allow_pickle=False)as z:
 for case in ['RH4X','SHW7X']:
  key=f'Story8__{case}__X';a=z[key];assert a.shape[1]==6 and np.isfinite(a).all()
  t,qt,qd=a[:,0],a[:,1],a[:,2]
  r=next(r for r in meta if r['Story']=='Story8'and r['Case']==case and r['Axis']=='X')
  assert len(t)==int(r['n_points'])and np.all(np.diff(t)>0)
  it=int(np.argmax(abs(qt)));idd=int(np.argmax(abs(qd)))
  assert abs(abs(qt[it])-float(r['QT_peak_kN']))<1e-9
  assert t[it]==float(r['QT_peak_t_s']) and abs(qt[it]-float(r['QT_signed_at_peak_kN']))<1e-9
  assert abs(abs(qd[idd])-float(r['QD_peak_abs_kN']))<1e-9 and t[idd]==float(r['QD_peak_t_s'])
  assert abs(qd[it]-float(r['QD_at_QT_peak_kN']))<1e-9
  assert int(a[it,5])==int(r['QT_source_row_at_QT_peak'])
  arrays[case]=(t,qt,qd,it,idd)
  checks.append({'Case':case,'array_key':key,'n_points':len(t),'t_start_s':float(t[0]),'t_end_s':float(t[-1]),
   'QT_abs_peak_kN':float(abs(qt[it])),'QT_peak_time_s':float(t[it]),'QT_signed_at_peak_kN':float(qt[it]),
   'QD_abs_peak_kN':float(abs(qd[idd])),'QD_peak_time_s':float(t[idd]),'QD_signed_at_QT_peak_kN':float(qd[it]),
   'QT_source_row':int(a[it,5]),'all_frozen_peak_checks_passed':True})
W,HT=1800,1220;im=Image.new('RGB',(W,HT),'white');d=ImageDraw.Draw(im)
fp='C:/Windows/Fonts/msyh.ttc'
sv=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HT}" viewBox="0 0 {W} {HT}"><rect width="100%" height="100%" fill="white"/>']
def tx(x,y,text,size=25,color='#243044',anchor='mm'):
 d.text((x,y),text,font=ImageFont.truetype(fp,size),fill=color,anchor=anchor)
 an={'mm':'middle','lm':'start','rm':'end'}.get(anchor,'start')
 sv.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="Microsoft YaHei, sans-serif" font-size="{size}" text-anchor="{an}" dominant-baseline="middle">{html.escape(str(text))}</text>')
def ln(points,color='#dbe2eb',width=2,dash=False):
 if dash:
  (x1,y1),(x2,y2)=points
  length=math.hypot(x2-x1,y2-y1)
  for b in range(0,int(length),12):
   end=min(length,b+7);d.line([(x1+(x2-x1)*b/length,y1+(y2-y1)*b/length),(x1+(x2-x1)*end/length,y1+(y2-y1)*end/length)],fill=color,width=width)
 else:d.line(points,fill=color,width=width)
 da=' stroke-dasharray="7 5"'if dash else''
 sv.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}'for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}"{da}/>')
def dot(x,y,color,r=6):
 d.ellipse((x-r,y-r,x+r,y+r),fill=color);sv.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" fill="{color}"/>')
tx(900,48,'第8层实际阻尼器模型的剪力与装置水平合力',40)
tx(900,102,'RH4X与SHW7X：原生保存时程，QD按该层8只装置真实方向投影',27,'#536174')
for case,left,right in [('RH4X',145,830),('SHW7X',1040,1725)]:
 t,qt,qd,it,idd=arrays[case];xmax=float(t[-1]);xp=lambda v:left+(right-left)*v/xmax
 tx((left+right)/2,151,case,32)
 for which,arr,top,bottom,limit,color,ticks in [
  ('QT',qt,245,555,8000,'#2868B7',[-8000,-4000,0,4000,8000]),
  ('QD',qd,755,1065,500,'#25856E',[-500,-250,0,250,500])]:
  yp=lambda v:bottom-(bottom-top)*(v+limit)/(2*limit)
  for tick in ticks:
   y=yp(tick);ln([(left,y),(right,y)],'#E4EAF0',1);tx(left-16,y,str(tick),23,anchor='rm')
  for xx in range(0,int(xmax)+1,10):
   x=xp(xx);ln([(x,top),(x,bottom)],'#E4EAF0',1);tx(x,bottom+27,str(xx),23)
  ln([(left,top),(left,bottom),(right,bottom)],'#718096',2)
  pts=[(xp(float(tt)),yp(float(yy)))for tt,yy in zip(t,arr)];ln(pts,color,3)
  ln([(xp(float(t[it])),top),(xp(float(t[it])),bottom)],'#7C8794',2,True)
  ln([(xp(float(t[idd])),top),(xp(float(t[idd])),bottom)],'#D08B39',2,True)
  idx=it if which=='QT'else idd
  dot(xp(float(t[idx])),yp(float(arr[idx])),color)
  title=(f'层剪力QT：绝对峰{abs(arr[idx]):.2f} kN，{t[idx]:.2f} s'if which=='QT'else f'装置合力QD：绝对峰{abs(arr[idx]):.2f} kN，{t[idx]:.2f} s')
  tx((left+right)/2,top-48,title,25)
  tx(left-86,(top+bottom)/2,which+'/kN',24)
  tx((left+right)/2,bottom+72,'时间 / s',25)
 tx((left+right)/2,665,f'QT峰时QD = {qd[it]:+.2f} kN',26,'#245A4B')
tx(900,1173,'QD为上端J的结构内力抵抗项；装置对节点外力为−QD。灰／橙虚线分别标QT／QD自身峰时。',25,'#536174')
sv.append('</svg>')
png=O/'Story8-RH4X-SHW7X-native-QT-QD-v003.png';svg=png.with_suffix('.svg');assert not png.exists()and not svg.exists()
im.save(png);svg.write_text('\n'.join(sv),encoding='utf-8')
with(O/'native-peak-anchors-2-v003.csv').open('x',encoding='utf-8',newline='')as f:
 w=csv.DictWriter(f,fieldnames=list(checks[0]));w.writeheader();w.writerows(checks)
assert sha(cache)==before
record={'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'source_cache':cache.relative_to(R).as_posix(),'source_cache_bytes':cache.stat().st_size,'source_cache_sha256':before,
 'source_table':source_table.relative_to(R).as_posix(),'source_table_sha256':sha(source_table),'only_arrays_read':[r['array_key']for r in checks],
 'columns_read':['t_s','QT_kN','QD_kN','native_story_source_row'],'columns_not_used':['QT-QD algebraic remainder','QT+QD algebraic remainder'],
 'checks':checks,'no_new_P_or_ODE_or_original_workbook_read':True,'all_samples_rendered_without_smoothing':True,'visual_QA_pending':True,'source_unchanged':True}
(O/'run-record-v003.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'png':str(png),'source_bytes':cache.stat().st_size,'read_arrays':2,'records':checks},ensure_ascii=False))
