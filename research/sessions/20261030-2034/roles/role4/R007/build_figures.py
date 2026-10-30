from pathlib import Path
from datetime import datetime,timezone
import csv,json,hashlib,html,re
O=Path(__file__).resolve().parent;P=O.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tab=P/'R006/modal-unit-kernel-change-108.csv';oldsvg=P/'R004/figure1-native-peak-reduction-profile.svg';oldcsv=P/'R004/figure1-native-profile-36.csv'
sources=[tab,oldsvg,oldcsv]
bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sources]
m=json.loads((P/'R006/delivery-manifest.json').read_text(encoding='utf-8'));assert sha(tab)==next(d['sha256'] for d in m['outputs'] if d['name']==tab.name)
m4=json.loads((P/'R004/delivery-manifest.json').read_text(encoding='utf-8'))
for p in [oldsvg,oldcsv]:assert sha(p)==next(d['sha256'] for d in m4['outputs'] if d['name']==p.name)
allrows=list(csv.DictReader(tab.open(encoding='utf-8-sig')));cases=['SHW3X','SHW4X','RH4X'];modes=[1,2,3,9];colors=['#2467a1','#d46624','#258271']
rows=[]
for mode in modes:
    for case in cases:
        r=next(d for d in allrows if int(d['Mode'])==mode and d['Case']==case)
        assert abs(float(r['peak_amplitude_decrease_percent'])-100*(1-float(r['A8_over_A5'])))<1e-12
        rows.append({k:r[k] for k in ['Case','Mode','omega_rad_s','period_s','A8_over_A5','peak_amplitude_decrease_percent']})
with (O/'figure-modal-amplitude-reduction-source-12.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
S=['<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="940" viewBox="0 0 1320 940"><title>相同阻尼增量下各阶响应幅值的削弱</title><desc>经典模态阻尼比由5%变为8%，比较第1、2、3、9阶在SHW3X、SHW4X、RH4X输入下，同频率单位参与运动的峰幅削弱率。非楼层贡献；参与因子为零时实际模态不受激。</desc><rect width="100%" height="100%" fill="white"/><g font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" fill="#17242b">']
def text(x,y,t,size=22,anchor='start',color='#17242b',bold=False,extra=''):
    S.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{"bold" if bold else "normal"}" {extra}>{html.escape(str(t))}</text>')
def rect(x,y,w,h,c):S.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>')
def line(x1,y1,x2,y2,c='#e1e6e9',width=1):S.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{width}"/>')
text(80,65,'相同阻尼增量下各阶响应幅值的削弱',32,bold=True)
text(80,110,'经典模态阻尼比 ζ：5% → 8%  |  第1、2、3、9阶',23,color='#475761')
for j,(c,col) in enumerate(zip(cases,colors)):
    x=240+j*340;rect(x,145,25,21,col);text(x+40,165,c,23)
x0,x1,y0,y1=150,1240,220,680
y=lambda v:y1-v/35*(y1-y0)
for v in range(0,36,5):line(x0,y(v),x1,y(v));text(x0-22,y(v)+8,str(v),21,'end')
line(x0,y0,x0,y1,'#57656d',1.5);line(x0,y1,x1,y1,'#57656d',1.5)
text(56,500,'峰幅削弱率（%）',23,extra='transform="rotate(-90 56 500)"')
for j,mode in enumerate(modes):
    center=280+j*280
    for k,(c,col) in enumerate(zip(cases,colors)):
        r=next(d for d in rows if int(d['Mode'])==mode and d['Case']==c);v=float(r['peak_amplitude_decrease_percent']);x=center+(k-1)*70
        rect(x-27.5,y(v),55,y1-y(v),col);text(x,y(v)-14,f'{v:.2f}',20,'middle',color=col)
    text(center,y1+38,f'第{mode}阶',23,'middle')
text((x0+x1)/2,768,'阶次',24,'middle')
text(80,823,'峰幅削弱率 = (1 − A₈% / A₅%) × 100%；A为同频率单位参与运动的绝对峰。',21,color='#475761')
text(80,864,'该幅比与共同的非零参与因子、模态归一化常数无关；不表示楼层剪力贡献。',21,color='#475761')
text(80,905,'参与因子 Γ = 0 时，实际该模态不受激；本图仍表示单位参与运动。',21,color='#475761')
(O/'figure-modal-amplitude-reduction.svg').write_text('\n'.join(S+['</g></svg>']),encoding='utf-8')
old=oldsvg.read_text(encoding='utf-8');new=old.replace('原生','软件计算');assert '原生' not in new
new,count=re.subn(r'<text x="([^"]+)" y="[^"]+" font-size="19" text-anchor="start" fill="#258271"([^>]*)>26.95%</text>',lambda m:f'<text x="{float(m.group(1))-28}" y="197" font-size="19" text-anchor="end" fill="#258271"{m.group(2)}>26.95%</text>',new)
assert count==1
(O/'figure-floor-peak-reduction-calculated.svg').write_text(new,encoding='utf-8')
(O/'figure-floor-peak-reduction-source-36.csv').write_bytes(oldcsv.read_bytes())
assert all(sha(p)==b['sha256'] for p,b in zip(sources,bindings))
(O/'source-and-numeric-QA.json').write_text(json.dumps(dict(created_utc=datetime.now(timezone.utc).isoformat(),sources=bindings,selected_modes=modes,cases=cases,bars=12,chart_values='copied frozen peak_amplitude_decrease_percent; checked 100*(1-A8/A5)',max_display_rounding_absolute_percent=0.005,profile_copy_changes='原生 → 软件计算; all data marks and axes retained; moved RH4X roof text label to avoid legend',profile_source_CSV_byte_identical=True,source_hashes_unchanged=True,no_new_ODE_or_fit_or_arrays=True),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'bar_values':[{k:r[k] for k in ['Case','Mode','peak_amplitude_decrease_percent']} for r in rows],'SVG_bytes':{p.name:p.stat().st_size for p in O.glob('*.svg')}},ensure_ascii=False,indent=2))
