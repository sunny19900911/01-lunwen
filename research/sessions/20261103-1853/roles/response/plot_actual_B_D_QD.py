from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,html,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent;R=H.parents[4];O=H/'R003';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
W=R.parent/'W5-重燃双塔连体';B=W/'02-数据/增阻尼多目标研究-20261016/原生0数据缓存';D=W/'research/maxwell-20261017/experiments/R001/core-cache'
mb=json.loads((B/'manifest.json').read_text(encoding='utf-8'));md=json.loads((D/'manifest.json').read_text(encoding='utf-8'));tb=mb['tables']['Story Forces'];td=md['tables']['Story Forces'];cb=tb.get('columns',tb.get('value_columns'));cd=td.get('columns',td.get('value_columns'))
pb=B/tb['cache'];pd=D/td['cache'];pq=R/'research/sessions/20261019-2045/roles/data/local-cache/R002-native-horizontal/paired-layer-histories.npz'
source_summaries=[H/'Story8-mechanism-summary.json',H/'R002/numeric-summary.json']
expected=[next(r for r in json.loads(source_summaries[0].read_text(encoding='utf-8'))['cases']if r['Case']=='RH4X'),json.loads(source_summaries[1].read_text(encoding='utf-8'))['result']]
key=lambda g:tuple(g['keys'][x]for x in ['Output Case','Story','Location']);kb={key(g):k for k,g in tb['groups'].items()};kd={key(g):k for k,g in td['groups'].items()}
saved={}
with np.load(pb,allow_pickle=False)as zb,np.load(pd,allow_pickle=False)as zd,np.load(pq,allow_pickle=False)as zq:
 for x in expected:
  case,story,axis=x['Case'],x['Story'],x['Axis'];k=(case,story,'Bottom');ab=zb[kb[k]];ad=zd[kd[k]];aq=zq[f'{story}__{case}__{axis}'];t=ab[:,cb.index('Time')];b=ab[:,cb.index('V'+axis)];d=ad[:,cd.index('V'+axis)];q=aq[:,2]
  assert np.array_equal(t,ad[:,cd.index('Time')])and np.array_equal(t,aq[:,0])and np.array_equal(d,aq[:,1])
  ib=int(np.argmax(abs(b)));idd=int(np.argmax(abs(d)));iq=int(np.argmax(abs(q)))
  for value,name in [(float(t[ib]),'t_B_s'),(float(t[idd]),'t_D_s'),(float(t[iq]),'t_QD_s'),(float(abs(b[ib])),'P_B_kN'),(float(abs(d[idd])),'P_D_kN'),(float(q[ib]),'QD_signed_at_tB_kN'),(float(q[idd]),'QD_signed_at_tD_kN')]:assert abs(value-x[name])<1e-9
  saved[(story,case)]=(t,b,d,q,ib,idd,iq)
PW,PH=1900,1390;im=Image.new('RGB',(PW,PH),'white');draw=ImageDraw.Draw(im);svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}"><rect width="100%" height="100%" fill="white"/>']
def text(x,y,s,n=27,c='#263449',anchor='mm'):
 draw.text((x,y),str(s),font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n),fill=c,anchor=anchor);a={'mm':'middle','lm':'start','rm':'end'}.get(anchor,'start')
 svg.append(f'<text x="{x}" y="{y}" font-family="Microsoft YaHei, sans-serif" font-size="{n}" fill="{c}" text-anchor="{a}" dominant-baseline="middle">{html.escape(str(s))}</text>')
def line(points,c='#DFE5EE',w=2,dash=False):
 if dash:
  (x1,y1),(x2,y2)=points;l=math.hypot(x2-x1,y2-y1)
  for bb in range(0,int(l),15):
   ee=min(l,bb+9);draw.line([(x1+(x2-x1)*bb/l,y1+(y2-y1)*bb/l),(x1+(x2-x1)*ee/l,y1+(y2-y1)*ee/l)],fill=c,width=w)
 else:draw.line(points,fill=c,width=w)
 da=' stroke-dasharray="9 6"'if dash else''
 svg.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}'for x,y in points)+f'" fill="none" stroke="{c}" stroke-width="{w}"{da}/>')
def dot(x,y,c,r=7,fill=True):
 draw.ellipse((x-r,y-r,x+r,y+r),fill=c if fill else'white',outline=c,width=3);svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" fill="{c if fill else "white"}" stroke="{c}" stroke-width="3"/>')
GRAY='#6D7A8C';BLUE='#245FB2';GREEN='#24856D';ORANGE='#C68027'
text(950,51,'实际阻尼器方案的原峰降低与控制时刻变化',42)
text(950,107,'上行：基准B与实际方案D的楼层剪力；下行：实际装置水平合力QD',29,'#526175')
for xx,name,col in [(270,'基准B',GRAY),(640,'实际方案D',BLUE),(1125,'装置合力QD',GREEN)]:
 line([(xx-70,166),(xx,166)],col,4);text(xx+20,166,name,28,anchor='lm')
text(950,217,'虚线：基准峰时tB（灰）／实际峰时tD（蓝）／装置合力峰时tQD（橙）',27,'#526175')
for x,left,right in zip(expected,[160,1100],[835,1775]):
 story,case=x['Story'],x['Case'];t,b,d,q,ib,idd,iq=saved[(story,case)];xmax=float(t[-1]);xp=lambda v:left+(right-left)*v/xmax
 text((left+right)/2,266,f"第{story[5:]}层  {case}",32)
 text((left+right)/2,314,f"tB={t[ib]:.2f}s，tD={t[idd]:.2f}s，tQD={t[iq]:.2f}s",26)
 for which,top,bottom,limit,ticks in [('QT',370,690,8000,[-8000,-4000,0,4000,8000]),('QD',950,1225,500,[-500,-250,0,250,500])]:
  yp=lambda val:bottom-(bottom-top)*(val+limit)/(2*limit)
  for v in ticks:
   yy=yp(v);line([(left,yy),(right,yy)],'#E1E8F0',1);text(left-18,yy,str(v),24,anchor='rm')
  for v in range(0,int(xmax)+1,10):
   xx=xp(v);line([(xx,top),(xx,bottom)],'#E1E8F0',1);text(xx,bottom+27,str(v),24)
  line([(left,top),(left,bottom),(right,bottom)],'#7B889B',2)
  data=[(b,GRAY),(d,BLUE)]if which=='QT'else[(q,GREEN)]
  for ar,c in data:line([(xp(float(tt)),yp(float(yy)))for tt,yy in zip(t,ar)],c,3)
  for ii,col in [(ib,GRAY),(idd,BLUE),(iq,ORANGE)]:line([(xp(float(t[ii])),top),(xp(float(t[ii])),bottom)],col,2,True)
  if which=='QT':
   dot(xp(float(t[ib])),yp(float(b[ib])),GRAY);dot(xp(float(t[idd])),yp(float(d[idd])),BLUE);dot(xp(float(t[ib])),yp(float(d[ib])),BLUE,7,False)
  else:
   dot(xp(float(t[iq])),yp(float(q[iq])),GREEN);dot(xp(float(t[ib])),yp(float(q[ib])),GRAY,7,False);dot(xp(float(t[idd])),yp(float(q[idd])),BLUE,7,False)
  text(left-91,(top+bottom)/2,which+'/kN',26)
  text((left+right)/2,bottom+78,'时间 / s',27)
 text((left+right)/2,824,f"D(tB)={x['D_signed_at_tB_kN']:+.2f} kN；D峰={x['D_signed_at_tD_kN']:+.2f} kN",25)
 text((left+right)/2,877,f"QD(tB)={x['QD_signed_at_tB_kN']:+.2f} kN；QD(tD)={x['QD_signed_at_tD_kN']:+.2f} kN",25,GREEN)
text(950,1352,'均为原始保存点，未平滑；QD按该层8只装置实际方向合成，不由QT扣除生成主体剪力。',26,'#526175')
svg.append('</svg>')
png=O/'actual-B-D-QD-two-records.png';sv=png.with_suffix('.svg');assert not png.exists()and not sv.exists();im.save(png);sv.write_text('\n'.join(svg),encoding='utf-8')
record={'at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'sources':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}for p in [pb,pd,pq]+source_summaries],
 'displayed_cases':[{'Story':x['Story'],'Case':x['Case']}for x in expected],'selection':'Root retains Story8 RH4X small-shift case and chooses RH4Y Story10 as max absolute peak-time shift among complete native-device-P Story8-11 × six cases; all Story8 six are kept in numerical supplement',
 'source_numeric_checks_passed':True,'full_original_saved_time_axis_in_both_rows':True,'no_smoothing_or_interpolation':True,'no_new_ODE_or_fit':True,'visual_review_pending':True,'pixels':[PW,PH]}
(O/'plot-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'png':str(png),'bytes':png.stat().st_size,'sha256':sha(png),'cases':record['displayed_cases']},ensure_ascii=False))
