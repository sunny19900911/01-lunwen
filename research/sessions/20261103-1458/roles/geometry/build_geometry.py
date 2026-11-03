from pathlib import Path
import csv,json,math,hashlib,datetime,html
from collections import defaultdict,Counter
from PIL import Image,ImageDraw,ImageFont

H=Path(__file__).resolve().parent;R=H.parents[4]
source=R/'research/sessions/20261019-2045/roles/data/R001-link-geometry-88.csv'
summary_source=source.with_name('R001-geometry-summary.json')
for name in ['actual-link-geometry-88.csv','layout-by-story-11.csv','actual-damper-layout.png','actual-damper-layout.svg','geometry-check.json','geometry-report.md','manifest.json']:
    assert not (H/name).exists(),name
rows=list(csv.DictReader(source.open(encoding='utf-8-sig')))
assert len(rows)==88 and len({r['Link'] for r in rows})==88
out=[];max_errors=defaultdict(float)
for row in rows:
    p=[float(row[f'I_{a}_m']) for a in 'XYZ'];q=[float(row[f'J_{a}_m']) for a in 'XYZ']
    d=[q[i]-p[i] for i in range(3)];L=math.sqrt(math.fsum(x*x for x in d));n=[x/L for x in d]
    assert L>0 and row['I_coordinate_found']=='True' and row['J_coordinate_found']=='True'
    theta=math.degrees(math.atan2(abs(d[2]),math.hypot(d[0],d[1])))
    az=math.degrees(math.atan2(d[1],d[0]))
    direction='X' if abs(n[1])<1e-10 and abs(n[0])>1e-10 else 'Y' if abs(n[0])<1e-10 and abs(n[1])>1e-10 else 'XY' if math.hypot(n[0],n[1])>1e-10 else 'vertical'
    max_errors['length_m']=max(max_errors['length_m'],abs(L-float(row['length_m'])))
    max_errors['direction_cosine']=max(max_errors['direction_cosine'],*(abs(n[i]-float(row[k])) for i,k in enumerate(['nx','ny','nz'])))
    max_errors['inclination_deg']=max(max_errors['inclination_deg'],abs(theta-abs(float(row['elevation_from_horizontal_deg']))))
    assert direction==row['horizontal_direction']
    si=0 if row['I_Story']=='Base' else int(row['I_Story'][5:]);sj=int(row['J_Story'][5:])
    assert sj-si==1 and row['Story']==row['J_Story'] and q[2]>p[2]
    out.append({'Story':row['Story'],'Link':row['Link'],'I_Point':row['I_Point'],'J_Point':row['J_Point'],**{f'I_{a}_m':p[i] for i,a in enumerate('XYZ')},**{f'J_{a}_m':q[i] for i,a in enumerate('XYZ')},'I_Story':row['I_Story'],'J_Story':row['J_Story'],'length_m':L,'nx':n[0],'ny':n[1],'nz':n[2],'inclination_deg':theta,'azimuth_I_to_J_deg':az,'exclusive_horizontal_class':direction,'link_source_row':row['link_source_row'],'I_point_source_row':row['I_point_source_row'],'J_point_source_row':row['J_point_source_row']})
out.sort(key=lambda x:(int(x['Story'][5:]),int(x['Link'][1:])))
def write_csv(path,data):
    with path.open('x',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
write_csv(H/'actual-link-geometry-88.csv',out)
by=[]
for story in range(1,12):
    a=[x for x in out if x['Story']==f'Story{story}'];c=Counter(x['exclusive_horizontal_class'] for x in a)
    assert len(a)==8 and c==Counter({'X':4,'Y':4})
    by.append({'Story':f'Story{story}','count_total':len(a),'X_only':c['X'],'Y_only':c['Y'],'XY':c['XY'],'vertical':c['vertical'],'lower_z_m':min(x['I_Z_m'] for x in a),'upper_z_m':max(x['J_Z_m'] for x in a),'length_min_m':min(x['length_m'] for x in a),'length_max_m':max(x['length_m'] for x in a),'inclination_min_deg':min(x['inclination_deg'] for x in a),'inclination_max_deg':max(x['inclination_deg'] for x in a),'abs_nx_nonzero_min':min(abs(x['nx']) for x in a if abs(x['nx'])>1e-10),'abs_nx_nonzero_max':max(abs(x['nx']) for x in a),'abs_ny_nonzero_min':min(abs(x['ny']) for x in a if abs(x['ny'])>1e-10),'abs_ny_nonzero_max':max(abs(x['ny']) for x in a),'links':';'.join(x['Link'] for x in a)})
write_csv(H/'layout-by-story-11.csv',by)
assert sum(x['count_total'] for x in by)==88 and sum(x['X_only'] for x in by)==44 and sum(x['Y_only'] for x in by)==44

# Draw native geometric projections only. No tower identity or structural frame is inferred.
W,HPIX=2280,1690
im=Image.new('RGB',(W,HPIX),'white');draw=ImageDraw.Draw(im)
font_path=Path('C:/Windows/Fonts/msyh.ttc')
if not font_path.is_file():font_path=Path('C:/Windows/Fonts/simsun.ttc')
font=lambda size:ImageFont.truetype(str(font_path),size)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HPIX}" viewBox="0 0 {W} {HPIX}">','<rect width="100%" height="100%" fill="white"/>']
def text(x,y,s,size=28,fill='#17212b',anchor='lm'):
    draw.text((x,y),s,font=font(size),fill=fill,anchor=anchor)
    align={'lm':'start','mm':'middle','rm':'end'}.get(anchor,'start')
    svg.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="Microsoft YaHei, sans-serif" font-size="{size}" fill="{fill}" text-anchor="{align}" dominant-baseline="middle">{html.escape(str(s))}</text>')
def line(x1,y1,x2,y2,fill='#333333',width=2,dash=False):
    if dash:
        d=math.hypot(x2-x1,y2-y1)
        for k in range(0,int(d),12):
            f1=k/d;f2=min((k+6)/d,1);draw.line((x1+(x2-x1)*f1,y1+(y2-y1)*f1,x1+(x2-x1)*f2,y1+(y2-y1)*f2),fill=fill,width=width)
    else:draw.line((x1,y1,x2,y2),fill=fill,width=width)
    svg.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{fill}" stroke-width="{width}"'+(' stroke-dasharray="6 6"' if dash else '')+'/>')
def rect(box,fill):
    draw.rectangle(box,fill=fill);svg.append(f'<rect x="{box[0]:.3f}" y="{box[1]:.3f}" width="{box[2]-box[0]:.3f}" height="{box[3]-box[1]:.3f}" fill="{fill}"/>')
def dot(x,y,color):
    r=3.6;draw.ellipse((x-r,y-r,x+r,y+r),fill=color);svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" fill="{color}"/>')
blue='#1f5a8a';orange='#ad641f';gray='#dbe1e6'
text(1140,54,'实际阻尼器布置的几何投影',44,anchor='mm')
text(1140,109,'88只装置，按实际I/J端点坐标绘制；坐标单位：m',28,fill='#45525f',anchor='mm')
line(410,158,470,158,blue,6);text(485,158,'水平分力沿X：44只',27)
line(1000,158,1060,158,orange,6);text(1075,158,'水平分力沿Y：44只',27)

def panel(box,a,b,limits,ticks,title,shade=False):
    x0,y0,x1,y1=box;loA,hiA,loB,hiB=limits
    scale=min((x1-x0)/(hiA-loA),(y1-y0)/(hiB-loB))
    pw=(hiA-loA)*scale;ph=(hiB-loB)*scale;left=x0+(x1-x0-pw)/2;top=y0+(y1-y0-ph)/2;right=left+pw;bottom=top+ph
    def xy(va,vb):return left+(va-loA)*scale,bottom-(vb-loB)*scale
    if shade:
        p=xy(loA,48.4);q=xy(hiA,31.2);rect((p[0],p[1],q[0],q[1]),'#f0f3f5')
    for va in ticks[0]:
        x,_=xy(va,loB);line(x,top,x,bottom,gray,1);text(x,bottom+24,f'{va:g}',23,anchor='mm')
    for vb in ticks[1]:
        _,y=xy(loA,vb);line(left,y,right,y,gray,1);text(left-16,y,f'{vb:g}',23,anchor='rm')
    for a0,b0,a1,b1 in [(left,top,right,top),(right,top,right,bottom),(right,bottom,left,bottom),(left,bottom,left,top)]:line(a0,b0,a1,b1,'#7d8993',2)
    # Each of the 88 link segments is retained even when projections coincide.
    for r in out:
        color=blue if r['exclusive_horizontal_class']=='X' else orange
        p=xy(r[f'I_{a}_m'],r[f'I_{b}_m']);q=xy(r[f'J_{a}_m'],r[f'J_{b}_m'])
        line(*p,*q,color,4);dot(*p,color);dot(*q,color)
    text((left+right)/2,top-38,title,31,anchor='mm')
    text((left+right)/2,bottom+65,f'{a} / m',26,anchor='mm');text(left-13,top-7,f'{b} / m',24,anchor='rm')
    if shade:
        for z in [31.2,48.4]:
            _,y=xy(loA,z);line(left,y,right,y,'#aeb9c1',1,True)

panel((225,240,2055,735),'X','Y',(25,150,10,85),([40,60,80,100,120,140],[20,40,60,80]),'(a) X-Y平面投影')
panel((175,930,1355,1465),'X','Z',(25,150,0,55),([40,60,80,100,120,140],[0,10,20,30,40,50]),'(b) X-Z立面投影',True)
panel((1540,930,2180,1465),'Y','Z',(10,85,0,55),([20,40,60,80],[0,10,20,30,40,50]),'(c) Y-Z立面投影',True)
text(1140,1570,'灰色区段：第8—11层（31.2～48.4m），供装置出力对照定位',26,fill='#45525f',anchor='mm')
text(1140,1620,'投影重合不代表装置数量；图中线段均为装置，不表示主体梁柱或塔的归属。',25,fill='#45525f',anchor='mm')
im.save(H/'actual-damper-layout.png',dpi=(300,300),optimize=True)
svg.append('</svg>');(H/'actual-damper-layout.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')

check={'at':datetime.datetime.now().astimezone().isoformat(),'source_csv':source.relative_to(R).as_posix(),'source_csv_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_summary_sha256':hashlib.sha256(summary_source.read_bytes()).hexdigest(),'links':88,'unique_link_names':88,'all_endpoints_found':True,'all_span_adjacent_levels':True,'exclusive_horizontal_classes':dict(Counter(x['exclusive_horizontal_class'] for x in out)),'maximum_difference_from_old_csv':dict(max_errors),'overall_length_m':[min(x['length_m'] for x in out),max(x['length_m'] for x in out)],'overall_inclination_deg':[min(x['inclination_deg'] for x in out),max(x['inclination_deg'] for x in out)],'actual_parameters_user_confirmed':{'kappa_kN_per_m':500000,'c_kN_s_per_m_power_alpha':477,'alpha':0.3,'source_type':'human confirmation from earlier main conversation; not silently populated from an empty property export'},'raw_original_excel_reread':False,'new_ODE':False,'drawn_segment_count_each_view':88,'unobserved_tower_assignment_inferred':False}
(H/'geometry-check.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['# 实际88只阻尼器几何与配置','', '结论：88只装置的实际I/J端点坐标完整，均连接相邻楼层。第1—11层每层8只，其中水平投影沿X、沿Y各4只，全楼分别44只；不存在同时按X/Y重复计数的器件。第12层没有本表所列的跨层装置。','', '以下按J端所在上层归类，倾角相对水平面取正，方向单位向量由I指向J。','', '|上端所在层|下端→上端标高/m|总数|X向/Y向/双向|轴线长度/m|相对水平倾角/°|','|---|---|---:|---|---|---|']
for r in by:
    md.append(f"|第{int(r['Story'][5:])}层|{r['lower_z_m']:.1f}→{r['upper_z_m']:.1f}|{r['count_total']}|{r['X_only']}/{r['Y_only']}/{r['XY']}|{r['length_min_m']:.3f}～{r['length_max_m']:.3f}|{r['inclination_min_deg']:.2f}～{r['inclination_max_deg']:.2f}|")
md += ['', '## 可供正文采用', '', '实际模型共设88只阻尼器，跨接第1—11层相邻楼层，每层8只，沿X、Y方向传递水平作用的装置各4只。图示按实际端点坐标绘制，装置轴线长度约6.44～9.40m，安装倾角及分层数值见配置表。相同装置数量并不表示相同水平合力，轴力仍需按各自方向余弦作同刻投影。实际有限Maxwell参数κ=500000kN/m、c=477kN(s/m)^0.3、α=0.3沿用用户确认；几何坐标本身不用于推断真实模态相对运动或附加模态阻尼。', '', '## 来源、检查与限制', '', '- 几何复用20261019小表，源工作簿为用户提供“有控全节点.xlsx”（262062B）；本次未重读工作簿，源SHA及3416节点范围继承原metadata。', '- 独立从XYZ重新求长度、单位向量及倾角，并与旧CSV逐行比对；88个I/J端点齐、全局Link名唯一、11个楼层各8只、相邻楼层连接均通过。精确最大差见geometry-check.json。', '- 原几何Excel的非线性参数行及属性分配表缺失；实际κ/c/α来自用户后续明确确认，不把空属性表补成原生赋值记录。', '- 三视图保留全部88条投影，重合线段可能叠在一起。未推定梁柱布置或塔一/塔二归属。灰色区段仅定位第8—11层供主控与已有装置出力资料对应，力时程完整性另由响应角色核查。', '- 原生轴力P、水平分力、软件Story Forces与主体抗力需保持各自定义，不能仅凭本图相减或给出装置贡献率。', '', '## 本次文件', '', '- actual-link-geometry-88.csv：从XYZ独立重算的88条几何及源行信息。', '- layout-by-story-11.csv：11层配置及方向余弦范围。', '- actual-damper-layout.png / .svg：实际几何三视图。', '- geometry-check.json：源SHA、独立核对和参数身份。', '']
(H/'geometry-report.md').write_text('\n'.join(md),encoding='utf-8')
manifest={'frozen_at':datetime.datetime.now().astimezone().isoformat(),'source_rows':88,'files':[]}
for p in sorted(H.iterdir()):
    if p.is_file() and p.name!='manifest.json':manifest['files'].append({'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(H/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(check,ensure_ascii=False))
