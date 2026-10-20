from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,statistics as st,math,html,xml.etree.ElementTree as ET
O=Path(__file__).resolve().parent;START=datetime.fromisoformat('2026-10-20T11:46:04+00:00')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc)
def rc(n):
 with (O/n).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def save(n,x):
 p=O/n;assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sources=['R002-common-six-main-axis-72.csv','R002-all14-main-axis-168.csv'];bindings=[{'path':str(O/n),'sha256':sha(O/n)} for n in sources]
save('R004-input-freeze.json',{'utc':now().isoformat(),'code_sha256':sha(Path(__file__)),'inputs':bindings,'scope':'SVG and distribution summaries from frozen reductions only; no arrays/no new response/no causal modal or QS attribution'})
six=rc(sources[0]);all14=rc(sources[1])
for rows in [six,all14]:
 for r in rows:r['v']=float(r['peak_reduction_percent']);r['s']=int(r['Story'][5:]);assert r['denominator_resolved']=='True' and r['input_main_axis']=='True' and r['Location']=='Bottom'
assert len(six)==72 and len(all14)==168
stats=[]
for scope,rows in [('common_six',six),('all_14',all14)]:
 for s in range(1,13):
  for axis in ['X','Y']:
   rr=[r for r in rows if r['s']==s and r['Axis']==axis];lo=min(rr,key=lambda r:r['v']);hi=max(rr,key=lambda r:r['v'])
   stats.append({'scope':scope,'Story':'Story'+str(s),'Axis':axis,'case_count':len(rr),'minimum_reduction_percent':lo['v'],'median_reduction_percent':st.median(r['v'] for r in rr),'maximum_reduction_percent':hi['v'],'range_percentage_points':hi['v']-lo['v'],'minimum_Case':lo['Case'],'maximum_Case':hi['Case'],'identity':'native Bottom QT; label0 baseline versus label3; not isolated QS'})
with (O/'R004-story-axis-statistics-48.csv').open('x',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(stats[0]));w.writeheader();w.writerows(stats)
def text(x,y,t,size=13,anchor='start',fill='#243642'):
 return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}">{html.escape(str(t))}</text>'
def line(x1,y1,x2,y2,color='#d8e0e5',width=1,extra=''):
 return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}" {extra}/>'
def head(w,h,title):return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{html.escape(title)}</title><desc>Native Bottom Story Forces label0 versus label3 saved absolute peak reduction; no modal contribution attribution.</desc><rect width="100%" height="100%" fill="white"/><g font-family="Microsoft YaHei,Segoe UI,Arial,sans-serif">']
maxx=5*math.ceil(max(r['v'] for r in all14)/5);colors={'RH4':'#216d9d','SHW4':'#c4771d','SHW7':'#8e4d83'}
def frame(parts,left,top,width,height,xmax):
 xx=lambda v:left+v/xmax*width;yy=lambda s:top+height-(s-1)/11*height
 for s in range(1,13):parts.extend([line(left,yy(s),left+width,yy(s)),text(left-12,yy(s)+4,'Story'+str(s),12,'end')])
 for tick in range(0,int(xmax)+1,5):parts.extend([line(xx(tick),top,xx(tick),top+height),text(xx(tick),top+height+24,tick,12,'middle')])
 parts.extend([line(left,top,left,top+height,'#435462',1.3),line(left,top+height,left+width,top+height,'#435462',1.3)])
 return xx,yy
p=head(900,720,'共同六工况：各层原生剪力峰值降幅');p+=[text(450,34,'共同六工况：各层原生剪力峰值降幅',21,'middle'),text(450,61,'标签0基准 → 标签3模型；Bottom输出；三波族各X/Y',14,'middle')]
x,y=frame(p,110,100,550,510,maxx)
for k,case in enumerate(sorted({r['Case'] for r in six})):
 rr=sorted([r for r in six if r['Case']==case],key=lambda r:r['s']);color=colors[case[:-1]];dash='' if case[-1]=='X' else 'stroke-dasharray="7 4"'
 p.append(f'<polyline points="'+ ' '.join(f"{x(r['v']):.2f},{y(r['s']):.2f}" for r in rr)+f'" fill="none" stroke="{color}" stroke-width="2.2" {dash}/>')
 for r in rr:p.append(f'<circle cx="{x(r["v"]):.2f}" cy="{y(r["s"]):.2f}" r="3" fill="{color}"><title>{case} Story{r["s"]}: {r["v"]:.6f}%</title></circle>')
 ly=150+36*k;p.extend([line(700,ly,740,ly,color,2.2,dash),text(750,ly+5,case,14)])
p.extend([text(710,410,'实线：X向输入/响应',12),text(710,434,'虚线：Y向输入/响应',12),text(385,664,'相对标签0的原生剪力峰值降幅 / %',15,'middle'),text(450,700,'降幅 = 100 × (1 − P3/P0)；各层峰分别取自各自完整时程',12,'middle'),'</g></svg>'])
(O/'R004-six-case-reduction-profiles.svg').write_text('\n'.join(p),encoding='utf-8');ET.parse(O/'R004-six-case-reduction-profiles.svg');print('FIRST_SVG_SAVED '+now().isoformat(),flush=True)
p=head(1060,710,'14工况按方向的逐层剪力降幅包络');p.extend([text(530,34,'14工况：各方向逐层剪力降幅分布',21,'middle'),text(530,62,'标签0基准 → 标签3模型；每方向7工况；阴影为最小—最大，实线为中位数',14,'middle')])
for axis,left,color in [('X',105,'#216d9d'),('Y',635,'#a35a22')]:
 rr=[r for r in stats if r['scope']=='all_14' and r['Axis']==axis];x,y=frame(p,left,115,350,480,maxx);p.append(text(left+175,95,axis+'向输入 / '+axis+'向响应',16,'middle'))
 points=[(x(r['minimum_reduction_percent']),y(int(r['Story'][5:]))) for r in rr]+[(x(r['maximum_reduction_percent']),y(int(r['Story'][5:]))) for r in reversed(rr)]
 p.append('<polygon points="'+' '.join(f'{a:.2f},{b:.2f}' for a,b in points)+f'" fill="{color}" fill-opacity=".15"/>')
 p.append('<polyline points="'+' '.join(f"{x(r['median_reduction_percent']):.2f},{y(int(r['Story'][5:])):.2f}" for r in rr)+f'" fill="none" stroke="{color}" stroke-width="2.3"/>')
 p.append(text(left+175,645,'相对标签0的峰值降幅 / %',15,'middle'))
p.extend([text(530,690,'统计单位为工况；X/Y分量不视为独立地震事件。原生QT不自动等于剔除装置后的主体QS。',12,'middle'),'</g></svg>']);(O/'R004-all14-directional-envelope.svg').write_text('\n'.join(p),encoding='utf-8');ET.parse(O/'R004-all14-directional-envelope.svg')
minimum=[]
for case in sorted({r['Case'] for r in six}):minimum.append(min((r for r in six if r['Case']==case),key=lambda r:r['v']))
sx={r['Story']:r for r in stats if r['scope']=='common_six' and r['Axis']=='X'};sy={r['Story']:r for r in stats if r['scope']=='common_six' and r['Axis']=='Y'};greater=sum(sx[s]['median_reduction_percent']>sy[s]['median_reduction_percent'] for s in sx);wide=max((r for r in stats if r['scope']=='all_14'),key=lambda r:r['range_percentage_points'])
caption='图：标签0基准与标签3模型在三波族各X/Y输入下，各层原生Bottom水平剪力绝对峰的降幅。P0、P3分别为对应模型完整保存时程的绝对峰；降幅为100(1−P3/P0)。各层峰时可不同，曲线不表示同刻受力剖面。该图描述原生QT输出，未将其归为剔除Link后的主体QS，也不表示单阶模态贡献。'
observations=[f"共同六工况最小降幅位于Story1的有{sum(r['s']==1 for r in minimum)}/6，最小降幅层并非总为底层。",'逐工况最小降幅为：'+'；'.join(f"{r['Case']} Story{r['s']} {r['v']:.4f}%" for r in minimum)+'。',f"共同六工况72条记录减幅为{min(r['v'] for r in six):.4f}%—{max(r['v'] for r in six):.4f}%，均为正值。",f"按三个波族取逐层中位数，X向高于Y向有{greater}/12层；这是本组输入响应的方向差异，不构成方向优劣或模态因果结论。",f"14工况分方向统计中，离散范围最宽为{wide['Story']}/{wide['Axis']}向，最小{wide['minimum_reduction_percent']:.4f}%、最大{wide['maximum_reduction_percent']:.4f}%，跨度{wide['range_percentage_points']:.4f}个百分点。"]
(O/'R004-caption-and-observations.md').write_text('# 图注与真实工程观察\n\n'+caption+'\n\n'+'\n\n'.join(f'{i+1}. {s}' for i,s in enumerate(observations))+'\n\n第二图为全部14工况按X/Y各7工况的最小/中位/最大分布，阴影不是置信区间。统计CSV同时保留共同六工况与全部14工况两种范围，共48行。\n',encoding='utf-8')
assert len(stats)==48 and all(sha(O/n)==b['sha256'] for n,b in zip(sources,bindings))
save('R004-result.json',{'observations':observations,'statistics_rows':48,'six_curve_points':72,'input_rows':{'common_six':72,'all14':168},'SVG_XML_valid':True,'new_time_histories_or_modal_decompositions':0})
end=now();save('R004-delivery-manifest.json',{'status':'frozen','start_utc':START.isoformat(),'frozen_utc':end.isoformat(),'elapsed_seconds':(end-START).total_seconds(),'within_8min':end<=START+timedelta(minutes=8),'files':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(O.glob('R004*')) if p.is_file()]})
print(json.dumps({'frozen':end.isoformat(),'seconds':(end-START).total_seconds(),'observations':observations},ensure_ascii=False))
