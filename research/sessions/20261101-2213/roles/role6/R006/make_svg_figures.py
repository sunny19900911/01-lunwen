from pathlib import Path
import json,html
P=Path(__file__).resolve().parent
D=json.loads((P/"plot-data.json").read_text(encoding="utf-8"))
INK="#263b48";BLUE="#24779b";ORANGE="#c76536";GRID="#e1e7eb"
def start(w,h):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/><g font-family="Microsoft YaHei,Arial,sans-serif" fill="{INK}">']
def text(a,x,y,s,size=24,anchor="middle",weight="normal",color=INK):
    a.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}">{html.escape(str(s))}</text>')
def line(a,x1,y1,x2,y2,color=GRID,width=1):
    a.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{width}"/>')
def save(a,name):
    a.append("</g></svg>")
    with (P/name).open("x",encoding="utf-8",newline="\n") as f:f.write("\n".join(a)+"\n")

a=start(1400,1000)
text(a,700,52,"基准阻尼5%时的楼层剪力改善速度",34,weight="bold")
text(a,700,100,"SHW3X · 固定300阶线性参照",23)
left,right,top,bottom=150,1270,150,830
X=lambda v:left+v/13*(right-left)
Y=lambda f:bottom-(f-.5)/12*(bottom-top)
for x in range(0,13,2):
    line(a,X(x),top,X(x),bottom);text(a,X(x),bottom+43,x)
for f in range(1,13):
    line(a,left-7,Y(f),left,Y(f),INK);text(a,left-24,Y(f)+9,f,24,"end")
line(a,left,top,left,bottom,INK,1.7);line(a,left,bottom,right,bottom,INK,1.7)
points=" ".join(f'{X(float(r["S"])):.3f},{Y(int(r["floor"])):.3f}' for r in D["profile"])
a.append(f'<polyline points="{points}" fill="none" stroke="{BLUE}" stroke-width="3"/>')
for r in D["profile"]:
    x,y=X(float(r["S"])),Y(int(r["floor"]))
    highlight=int(r["floor"]) in (5,12)
    a.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{8 if highlight else 6}" fill="{ORANGE if highlight else BLUE}" stroke="white" stroke-width="2"/>')
    if highlight:
        label="第5层  S = 2.132" if int(r["floor"])==5 else "屋顶  S = 11.724"
        text(a,x+(24 if int(r["floor"])==5 else -24),y+10,label,27,"start" if int(r["floor"])==5 else "end","bold")
text(a,710,920,"S（降幅%/阻尼百分点）",27)
text(a,73,485,"楼层",27)
text(a,700,977,"S越小，基准附近改善越慢；每层按本层基准剪力峰值归一。",22)
save(a,"figure1-S-along-height-v001.svg")

a=start(1600,1100)
text(a,800,52,"同一基准控制峰的模态改善贡献",36,weight="bold")
for x,label,color in ((525,"促进下降（c > 0）",BLUE),(920,"抵消下降（c < 0）",ORANGE)):
    a.append(f'<rect x="{x-145}" y="89" width="27" height="20" fill="{color}"/>')
    text(a,x-105,108,label,24,"start")
line(a,800,155,800,930,GRID,1)
for story,offset,title in (("Story5",0,"第5层  S = 2.132"),("Story12",800,"屋顶（第12层）  S = 11.724")):
    l,r=200+offset,740+offset
    xx=lambda v:l+(v+4)/14*(r-l)
    text(a,400+offset,170,title,28,weight="bold")
    for x in range(-4,11,2):
        line(a,xx(x),215,xx(x),840,INK if x==0 else GRID,2 if x==0 else 1)
        text(a,xx(x),884,x,23)
    bars=[d for d in D["bars"] if d["Story"]==story]
    for j,d in enumerate(bars):
        y=250+j*80;v=float(d["c"]);x0,xv=xx(0),xx(v)
        text(a,l-20,y+9,d["group"],25,"end")
        a.append(f'<rect x="{min(x0,xv):.4f}" y="{y-17}" width="{abs(xv-x0):.4f}" height="34" fill="{BLUE if v>=0 else ORANGE}"/>')
        text(a,xv+(9 if v>=0 else -9),y+8,f"{v:+.3f}",22,"start" if v>=0 else "end")
    line(a,l,840,r,840,INK,1.3)
    text(a,470+offset,939,"c（降幅%/阻尼百分点）",25)
text(a,800,1010,"控制峰：第5层22.92 s，屋顶21.18 s。7阶并集＋其余293阶，各层有符号和为S。",23)
text(a,800,1060,"c为基准峰值导数贡献，不是候选阻尼下实际剪力的模态分担。",23)
save(a,"figure2-signed-modal-improvement-v001.svg")
print("Wrote two editable SVG figures from frozen numeric sources.")
