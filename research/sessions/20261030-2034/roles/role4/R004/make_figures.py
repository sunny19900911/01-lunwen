from pathlib import Path
from datetime import datetime, timezone
import csv, json, hashlib, math, html
import numpy as np

O=Path(__file__).resolve().parent
P=O.parent/'R003'
sources=[P/'native-all12-peak-change-36.csv',P/'local-cache/all12-low-high-reference-traces.npz',P/'all12-same-time-low-high-residual-288.csv']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sources]
def savejson(n,v): (O/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def csvwrite(n,rows):
    with (O/n).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
rows=list(csv.DictReader(sources[0].open(encoding='utf-8-sig')))
assert len(rows)==36 and len({(r['Case'],r['Story']) for r in rows})==36
for r in rows:
    assert abs(float(r['native_peak_decrease_percent'])-100*(1-float(r['peak8_kN'])/float(r['peak5_kN'])))<1e-10
pair=next(r for r in rows if r['Story']=='Story12' and r['Case']=='SHW4X')
points=[]
with np.load(sources[1],allow_pickle=False) as a:
    for t in [28.34,20.58]:
        for z in [.05,.08]:
            k=f'N36__SHW4X__Story12__z{z:g}__';tt=a[k+'t'];ii=np.flatnonzero(np.isclose(tt,t,rtol=0,atol=1e-9));assert len(ii)==1;i=int(ii[0])
            d=dict(N=36,Story='Story12',Case='SHW4X',zeta=z,anchor_s=t)
            for out,key in [('native_kN','native'),('low1to12_kN','low1to12'),('high13to36_kN','represented_high13plus'),('residual_kN','residual')]: d[out]=float(a[k+key][i])
            d['closure_error_kN']=d['native_kN']-sum(d[q] for q in ['low1to12_kN','high13to36_kN','residual_kN'])
            assert abs(d['closure_error_kN'])<1e-6
            points.append(d)
expected=[float(pair['peak5_kN']),float(pair['V8_at_5peak_kN']),float(pair['V5_at_8peak_kN']),float(pair['peak8_kN'])]
assert max(abs(d['native_kN']-v) for d,v in zip(points,expected))<1e-9
csvwrite('figure1-native-profile-36.csv',rows)
csvwrite('figure2-same-time-points-4.csv',points)

class SVG:
    def __init__(self,w,h,title,desc):
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc><rect width="100%" height="100%" fill="white"/><g font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" fill="#17242b">']
    def text(self,x,y,s,size=22,anchor='start',color='#17242b',weight='normal',extra=''):
        self.s.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}" {extra}>{html.escape(str(s))}</text>')
    def line(self,x1,y1,x2,y2,color='#cbd3d8',width=1,extra=''):
        self.s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {extra}/>')
    def rect(self,x,y,w,h,color,extra=''):
        self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" {extra}/>')
    def marker(self,x,y,c,typ='circle',size=7):
        if typ=='square':self.rect(x-size,y-size,size*2,size*2,c)
        elif typ=='triangle':self.s.append(f'<path d="M{x},{y-size-1} L{x+size+1},{y+size} L{x-size-1},{y+size}Z" fill="{c}"/>')
        else:self.s.append(f'<circle cx="{x}" cy="{y}" r="{size}" fill="{c}"/>')
    def poly(self,p,c): self.s.append('<polyline points="'+' '.join(f'{x:.3f},{y:.3f}' for x,y in p)+f'" fill="none" stroke="{c}" stroke-width="3"/>')
    def save(self,n): (O/n).write_text('\n'.join(self.s+['</g></svg>']),encoding='utf-8')

colors=['#2467a1','#d46624','#258271'];cases=['SHW3X','SHW4X','RH4X'];marks=['circle','square','triangle']
s=SVG(1240,980,'原生楼层剪力峰值降幅沿高度分布','同一输入记录下经典模态阻尼比由5%变为8%；Bottom截面X向原生楼层剪力，采用各自全时程绝对峰，12层、3条记录。')
s.text(80,65,'原生楼层剪力峰值降幅沿高度分布',32,weight='bold')
s.text(80,108,'经典模态阻尼比 ζ：5% → 8%  |  Bottom截面 · X向',23,color='#475761')
for j,(c,col,m) in enumerate(zip(cases,colors,marks)):
    x=230+j*325;s.line(x-60,155,x-12,155,col,3);s.marker(x-35,155,col,m);s.text(x,163,'原生 '+c,23)
x0,x1,y0,y1=145,1140,220,760
xx=lambda v:x0+v/35*(x1-x0)
yy=lambda f:y1-(f-1)/11*(y1-y0)
for val in range(0,36,5):
    x=xx(val);s.line(x,y0,x,y1,'#e1e6e9');s.text(x,y1+38,str(val),21,'middle')
for f in range(1,13):
    y=yy(f);s.line(x0,y,x1,y,'#edf0f2');s.text(x0-22,y+8,f'{f}层',21,'end')
s.line(x0,y0,x0,y1,'#57656d',1.5);s.line(x0,y1,x1,y1,'#57656d',1.5)
s.text((x0+x1)/2,840,'原生峰值降幅 r（%）',24,'middle')
s.text(48,490,'楼层',23,extra='transform="rotate(-90 48 490)"')
for c,col,m in zip(cases,colors,marks):
    rr=sorted([r for r in rows if r['Case']==c],key=lambda r:int(r['Story'][5:]));pp=[(xx(float(r['native_peak_decrease_percent'])),yy(int(r['Story'][5:]))) for r in rr]
    s.poly(pp,col)
    for x,y in pp:s.marker(x,y,col,m,5.5)
    s.text(pp[-1][0]+12,pp[-1][1]+{'SHW3X':-15,'SHW4X':22,'RH4X':-42}[c],f"{float(rr[-1]['native_peak_decrease_percent']):.2f}%",19,color=col)
s.text(80,901,'r = (1 − P₈% / P₅%) × 100%；P = max |Vₓ(t)|，剪力单位kN。',21,color='#475761')
s.text(80,940,'5%与8%分别取各自全时程绝对峰；保留12层、3条原始记录的全部36对结果。',20,color='#475761')
s.save('figure1-native-peak-reduction-profile.svg')

s=SVG(1450,1100,'Story12 SHW4X 两锚点同刻参照组','四柱分别为28.34s与20.58s的5%和8%状态，N36弹性固定映射低1—12组、高13—36组和原生减参照的残差；有符号量，非能量或分力百分比。')
s.text(80,62,'Story12 · SHW4X：两个锚点的同刻参照组',32,weight='bold')
s.text(80,105,'N36弹性固定映射，rcond = 10⁻¹⁰；8%沿用5%系数  |  Bottom截面 · X向',22,color='#475761')
cols=['#2467a1','#d46624','#a8b0b5'];keys=['low1to12_kN','high13to36_kN','residual_kN']
for j,(lab,col) in enumerate(zip(['低组1—12（参照）','高组13—36（参照）','残差：原生 − 参照'],cols)):
    x=85+j*350;s.rect(x,140,24,19,col);s.text(x+36,159,lab,21)
s.marker(1180,150,'#111111',size=6);s.text(1196,159,'原生总剪力',21)
x0,x1,y0,y1=140,1360,245,625
mx=max(sum(max(0,d[k]) for k in keys) for d in points);mn=min(0,min(sum(min(0,d[k]) for k in keys) for d in points))
step=100;vmin=math.floor((mn-25)/step)*step;vmax=math.ceil((mx+60)/step)*step
y=lambda v:y1-(v-vmin)/(vmax-vmin)*(y1-y0)
for val in range(vmin,vmax+1,step):
    s.line(x0,y(val),x1,y(val),'#aebbc3' if val==0 else '#e1e6e9',1.6 if val==0 else 1);s.text(x0-20,y(val)+7,str(val),20,'end')
s.line(x0,y0,x0,y1,'#57656d',1.5);s.text(54,450,'同刻剪力（kN）',22,extra='transform="rotate(-90 54 450)"')
centers=[335,535,965,1165]
for j,d in enumerate(points):
    x=centers[j];pos=neg=0
    for k,col in zip(keys,cols):
        v=d[k];base=pos if v>=0 else neg;end=base+v;s.rect(x-48,min(y(base),y(end)),96,abs(y(end)-y(base)),col)
        if v>=0:pos=end
        else:neg=end
    s.marker(x,y(d['native_kN']),'#111111',size=6)
    s.text(x+62,y(d['native_kN'])+6,f"{d['native_kN']:.2f}",19,color='#111111')
    s.text(x,y1+37,f"ζ = {d['zeta']:.0%}",23,'middle')
for cx,t,label in [(435,28.34,'5%原生峰时刻'),(1065,20.58,'8%原生峰时刻')]:
    s.text(cx,202,f't = {t:.2f} s',25,'middle',weight='bold');s.text(cx,231,label,19,'middle',color='#475761')
s.line(750,193,750,670,'#b6c1c7',1,extra='stroke-dasharray="6 6"')
s.text(80,716,'正、负分量分别从零线堆叠；黑点是原生总剪力，分量代数和与黑点闭合。',21,color='#475761')
tablex=[95,245,435,680,925,1190]
for x,lab in zip(tablex,['锚点 / s','阻尼比','原生 / kN','低组 / kN','高组 / kN','残差 / kN']):s.text(x,766,lab,21,weight='bold')
s.line(80,780,1370,780,'#aab8c0')
for j,d in enumerate(points):
    yy=813+j*40
    vals=[f"{d['anchor_s']:.2f}",f"{d['zeta']:.0%}"]+[f"{d[k]:+.2f}" for k in ['native_kN']+keys]
    for x,v in zip(tablex,vals):s.text(x,yy,v,21)
s.line(80,950,1370,950,'#aab8c0')
s.text(80,988,'参照组来自冻结拟合输出，高组仅含13—36阶；残差保留原生与参照之差。',21,color='#475761')
s.text(80,1027,'两锚点分别独立比较同刻有符号值；不得拼成跨时刻分力百分比或解释为能量占比。',21,color='#475761')
s.text(80,1066,'组系数不具有唯一物理分解含义；图中比较的是同一锚点的两种阻尼状态。',21,color='#475761')
s.save('figure2-Story12-SHW4X-two-anchors.svg')
assert all(sha(p)==b['sha256'] for p,b in zip(sources,bindings))
savejson('numeric-verification.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),sources=bindings,profile_pairs=36,same_time_points=4,N=36,max_closure_error_kN=max(abs(d['closure_error_kN']) for d in points),native_cross_values_match_R003=True,no_fit=True,no_order_extension=True,complete_trace_outputs=False,source_hashes_unchanged=True))
print(json.dumps(dict(points=points,range=[vmin,vmax],svgs=[dict(name=p.name,bytes=p.stat().st_size) for p in O.glob('*.svg')]),ensure_ascii=False,indent=2))
