"""Two standalone scientific SVGs from frozen processed CSVs only."""
from pathlib import Path
import csv,json,hashlib,html

O=Path(__file__).resolve().parent
S=O.parents[2]
rules=json.loads((S/"roles/role4/R004/input-rules-freeze.json").read_text(encoding="utf-8"))
binding=next(x for x in rules["sources"] if x["path"].endswith("CM-signed-all300-5400.csv"))
CM=Path(binding["path"])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(CM)==binding["sha256"]
source=[{"path":str(CM),"sha256":sha(CM)}]
def frozen_csv(folder,name):
    man=json.loads((folder/"delivery-manifest.json").read_text(encoding="utf-8"))
    p=folder/name
    assert sha(p)==next(x["sha256"] for x in man["outputs"] if x["name"]==name)
    source.append({"path":str(p),"sha256":sha(p)})
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
periods={int(x["Mode"]):x for x in frozen_csv(S/"roles/role4/R001","modal-basis-identity-numeric-comparison-18.csv") if x["dataset"]=="actual_controlled"}
env=frozen_csv(S/"roles/role4/R005","mode-envelopes-SHW3X-z0.05-3600.csv")
with CM.open(encoding="utf-8-sig",newline="") as f:
    cm=[r for r in csv.DictReader(f) if int(r["Mode"]) in [2,10,13]]
shapes=[]
for mode in [2,10,13]:
    rr=[r for r in cm if int(r["Mode"])==mode]
    assert len(rr)==18 and all(r["CaseType"]=="LinModRitz" for r in rr)
    assert sorted(int(r["Story"][5:]) for r in rr if r["Diaphragm"]=="D1")==list(range(1,13))
    assert sorted(int(r["Story"][5:]) for r in rr if r["Diaphragm"]=="D2")==list(range(3,9))
    scale=max(abs(float(r["UX_converted_m"])) for r in rr);assert scale>0
    for r in rr:
        shapes.append({"Mode":mode,"Story":r["Story"],"Diaphragm":r["Diaphragm"],"CaseType":r["CaseType"],
            "UX_native_mm":float(r["UX_native_mm"]),"UX_converted_m":float(r["UX_converted_m"]),
            "per_mode_max_abs_UX_m":scale,"normalized_UX":float(r["UX_converted_m"])/scale,
            "same_source_period_s":float(periods[mode]["Period_s"]),"CM_SourceRow":r["SourceRow"],
            "normalization_scope":"all18 existing CM X components within this mode; no cross-mode amplitude comparison"})
weights=[]
for story in ["Story5","Story12"]:
    rr=[r for r in env if r["Story"]==story]
    assert len(rr)==300 and {int(r["Mode"]) for r in rr}==set(range(1,301))
    U=sum(float(r["reference_mode_abs_peak_kN"]) for r in rr)
    total=0.
    for label,mode in [("Mode2",2),("Mode10",10),("Mode13",13),("Mode18",18),("Other296",None)]:
        subset=[r for r in rr if int(r["Mode"])==mode] if mode else [r for r in rr if int(r["Mode"]) not in [2,10,13,18]]
        peak_sum=sum(float(r["reference_mode_abs_peak_kN"]) for r in subset)
        weight=peak_sum/U
        assert abs(weight-sum(float(r["fixed_5pct_weight"]) for r in subset))<1e-12
        weights.append({"Case":"SHW3X","Story":story,"zeta":.05,"category":label,"mode_count":len(subset),
            "sum_independent_mode_peaks_kN":peak_sum,"all300_U5_kN":U,"weight_fraction":weight,"weight_percent":100*weight,
            "scope":"independent full-window modal peak weights, not simultaneous shear or energy shares"})
        total+=weight
    assert abs(total-1)<1e-12
def cs(name,rows):
    with (O/name).open("x",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
cs("figure1-CM-UX-normalized-source-54.csv",shapes)
cs("figure2-SHW3X-weights-source-10.csv",weights)

BLUE="#1D5C88";ORANGE="#C0622A";INK="#202C34";MUTED="#50616B"
class SVG:
    def __init__(self,w,h,title,desc):
        self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><title>{html.escape(title)}</title><desc>{html.escape(desc)}</desc><rect width="100%" height="100%" fill="white"/><g font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" fill="{INK}">']
    def text(self,x,y,t,size=22,anchor="start",color=INK,bold=False,extra=""):
        self.s.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{700 if bold else 400}" {extra}>{html.escape(str(t))}</text>')
    def line(self,x1,y1,x2,y2,color="#DFE5E9",width=1,dash=""):
        self.s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else "")+'/>')
    def rect(self,x,y,w,h,color):
        self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>')
    def marker(self,x,y,color,typ):
        if typ=="circle":self.s.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="white" stroke="{color}" stroke-width="2.5"/>')
        else:self.s.append(f'<rect x="{x-5}" y="{y-5}" width="10" height="10" fill="white" stroke="{color}" stroke-width="2.5"/>')
    def poly(self,points,color,dash=""):
        self.s.append('<polyline points="'+' '.join(f"{x:.4f},{y:.4f}" for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="3"'+(f' stroke-dasharray="{dash}"' if dash else "")+'/>')
    def save(self,name):
        with (O/name).open("x",encoding="utf-8") as f:f.write("".join(self.s)+"</g></svg>\n")

g=SVG(1500,1080,"实际有控模态的隔板质心X向位移分量","Selected actual LinModRitz modes2,10,13; signed diaphragm CM UX normalized by per-mode maximum across18 existing CM samples, D2 only Story3..8. Not full-node deformation or a rigid-story assumption.")
g.text(75,65,"第2、10、13阶：隔板质心X向模态位移分量",34,bold=True)
g.text(75,109,"实际有控模型 · LinModRitz · 每阶按18个现有CM点中的最大 |UX| 归一",23,color=MUTED)
for x,color,d,typ,dash,label in [(90,BLUE,"D1","circle","","D1：第1—12层"),(600,ORANGE,"D2","square","9 6","D2：仅第3—8层")]:
    g.line(x,159,x+58,159,color,3,dash);g.marker(x+29,159,color,typ);g.text(x+75,168,label,23)
for j,mode in enumerate([2,10,13]):
    left=65+j*475;x0=left+65;x1=left+420;y0=245;y1=790
    xx=lambda v:x0+(v+1)/2*(x1-x0)
    yy=lambda floor:y1-(floor-1)/11*(y1-y0)
    g.text((x0+x1)/2,211,f"({chr(97+j)}) 第{mode}阶  T = {float(periods[mode]['Period_s']):.4f} s",24,"middle",bold=True)
    for v in [-1,-.5,0,.5,1]:
        x=xx(v);g.line(x,y0,x,y1,"#89969F" if v==0 else "#E1E7EB",1.5 if v==0 else 1)
        g.text(x,y1+37,f"{v:g}",20,"middle")
    for floor in range(1,13):
        y=yy(floor);g.line(x0,y,x1,y,"#ECF0F2")
        g.text(x0-17,y+7,str(floor),20,"end")
    g.line(x0,y0,x0,y1,"#62727D",1.5);g.line(x0,y1,x1,y1,"#62727D",1.5)
    g.text((x0+x1)/2,866,"归一化 UX（该阶）",23,"middle")
    for d,color,typ,dash in [("D1",BLUE,"circle",""),("D2",ORANGE,"square","9 6")]:
        rr=sorted([r for r in shapes if r["Mode"]==mode and r["Diaphragm"]==d],key=lambda r:int(r["Story"][5:]))
        # Draw only contiguous observed floors; never bridge missing floors.
        segments=[];current=[]
        for r in rr:
            floor=int(r["Story"][5:])
            if current and floor!=current[-1][0]+1:segments.append(current);current=[]
            current.append((floor,(xx(r["normalized_UX"]),yy(floor))))
        if current:segments.append(current)
        for seg in segments:g.poly([pt for _,pt in seg],color,dash)
        for r in rr:g.marker(xx(r["normalized_UX"]),yy(int(r["Story"][5:])),color,typ)
g.text(30,560,"楼层（Story）",23,"middle",extra='transform="rotate(-90 30 560)"')
g.text(75,925,"图示归一化只比较各阶空间分布，不能比较跨阶真实响应振幅；保留原生模态符号。",22,color=MUTED)
g.text(75,966,"点为隔板质心UX样本，连线仅辅助阅读；不是全节点变形，也不据此假定整层刚性。",22,color=MUTED)
g.text(75,1007,"D2只绘制源表实际存在的楼层，不补零、不外推至屋顶或基底。",22,color=MUTED)
g.save("figure1-actual-CM-UX-modes2-10-13.svg")

g=SVG(1500,1080,"SHW3X第5层与屋顶的5%模态独立峰幅权重","Fixed categories Modes2,10,13,18 and all remaining296 modes; actual300 elastic inertia linear reference. Independent modal envelope weights, not same-time shear shares or energy fractions.")
g.text(75,65,"SHW3X：第5层与屋顶的5%模态独立峰幅权重",34,bold=True)
g.text(75,109,"全300阶弹性惯性线性参照 · w = a / Σa · a = 该阶完整时程的 max |v(t)|",23,color=MUTED)
for x,col,label in [(90,BLUE,"第5层"),(380,ORANGE,"第12层（屋顶）")]:
    g.rect(x,148,27,22,col);g.text(x+42,168,label,23)
x0,x1,y0,y1=260,1370,220,790
xx=lambda v:x0+v/70*(x1-x0)
for tick in range(0,71,10):
    g.line(xx(tick),y0,xx(tick),y1,"#DCE3E8");g.text(xx(tick),y1+39,str(tick),21,"middle")
g.line(x0,y0,x0,y1,"#62727D",1.5);g.line(x0,y1,x1,y1,"#62727D",1.5)
for i,(key,label) in enumerate([("Mode2","第2阶"),("Mode10","第10阶"),("Mode13","第13阶"),("Mode18","第18阶"),("Other296","其他296阶")]):
    center=275+i*108
    g.text(x0-27,center+7,label,23,"end")
    for story,color,offset in [("Story5",BLUE,-28),("Story12",ORANGE,9)]:
        w=next(r["weight_percent"] for r in weights if r["Story"]==story and r["category"]==key)
        g.rect(x0,center+offset,xx(w)-x0,24,color)
        g.text(xx(w)+11,center+offset+21,f"{w:.2f}%",22,color=color)
g.text((x0+x1)/2,873,"独立峰幅权重（%）",24,"middle")
g.text(75,925,"“其他”包含除2、10、13、18阶以外的296阶；每层全部五类之和为100%。",22,color=MUTED)
g.text(75,966,"各阶独立峰可能出现在不同时刻；这些权重不是同刻剪力份额，也不是能量比例。",22,color=MUTED)
g.text(75,1007,"取实际模态基的弹性惯性线性参照，尚不等同原生FNA的唯一逐阶内力分解。",22,color=MUTED)
g.save("figure2-SHW3X-Story5-Story12-envelope-weights.svg")

verification={"source_sha_checked":True,"shape_source_rows":len(shapes),"weight_source_rows":len(weights),
    "per_mode_normalized_max_abs":{str(m):max(abs(r["normalized_UX"]) for r in shapes if r["Mode"]==m) for m in [2,10,13]},
    "D1_floors":list(range(1,13)),"D2_floors":list(range(3,9)),"no_missing_floor_zero_fill":True,
    "figure2_categories":"2,10,13,18,all other296 (not top5+295)",
    "figure2_weight_sums":{s:sum(r["weight_fraction"] for r in weights if r["Story"]==s) for s in ["Story5","Story12"]},
    "font":"Microsoft YaHei; installed C:/Windows/Fonts/msyh.ttc",
    "source_fingerprints":source,"raster_visual_QA":"pending view_image"}
with (O/"numeric-verification.json").open("x",encoding="utf-8") as f:json.dump(verification,f,ensure_ascii=False,indent=2)
print(json.dumps({"SVGs":2,"shape_rows":len(shapes),"weight_rows":len(weights),"weights":weights},ensure_ascii=False))
