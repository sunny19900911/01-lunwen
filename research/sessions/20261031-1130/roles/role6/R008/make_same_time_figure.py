"""One publication figure from two frozen CSV rows. No response computation."""
from pathlib import Path
import csv,json,hashlib,html
O=Path(__file__).resolve().parent
S=O.parents[2]/"roles/role4/R008"
name="Story5-Story12-two-anchors-symmetric-change-12.csv"
manifest=json.loads((S/"delivery-manifest.json").read_text(encoding="utf-8"))
source=S/name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==next(x["sha256"] for x in manifest["outputs"] if x["name"]==name)
with source.open(encoding="utf-8-sig",newline="") as f:allrows=list(csv.DictReader(f))
selected=[r for r in allrows if r["Case"]=="SHW3X" and r["anchor"]=="native5_abspeak"]
assert len(selected)==2 and {r["Story"] for r in selected}=={"Story5","Story12"}
components=[
("幅值变化项","old_direction_amplitude_weakening_kN","#1D5C88"),
("归一波形变化项","old_direction_waveform_weakening_kN","#C0622A"),
("同刻净削弱","old_direction_total_weakening_kN","#4E5F6C")]
data=[]
for r in selected:
    assert r["old_direction_is_absolute_weakening"]=="True"
    assert float(r["old_direction_unallocated_weakening_kN"])==0
    assert abs(float(r[components[0][1]])+float(r[components[1][1]])-float(r[components[2][1]]))<1e-8
    for label,key,color in components:
        data.append({"Case":r["Case"],"Story":r["Story"],"anchor":r["anchor"],"time_s":r["time_s"],
            "component":label,"value_kN":r[key],"source_column":key,"sigma5_reference":r["sigma5_reference"],
            "source_CSV":name,"source_CSV_line":allrows.index(r)+2,
            "scope":"same-time weakening along old5percent reference direction; not two-ownpeak difference",
            "audit_status":"source SHA verified; independent role2 review pending"})
with (O/"same-time-symmetric-figure-source-6.csv").open("x",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
INK="#202C34";MUTED="#50616B"
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="940" viewBox="0 0 1500 940"><title>SHW3X：同刻削弱量的对称分解</title><desc>Two frozen same-time modal symmetric decomposition sums, along the old5percent reference sign. Independent kN axes. Normalized waveform change is not pure phase; not a difference between two independent response peaks. Scientific independent review pending.</desc><rect width="100%" height="100%" fill="white"/><g font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" fill="{INK}">']
def text(x,y,t,size=22,anchor="start",color=INK,bold=False,extra=""):
    svg.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{700 if bold else 400}" {extra}>{html.escape(str(t))}</text>')
def line(x1,y1,x2,y2,color="#E1E7EB",width=1):
    svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')
def rect(x,y,w,h,color):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>')
text(75,66,"SHW3X：同刻削弱量的对称分解",34,bold=True)
text(75,110,"阻尼比5% → 8% · 逐阶同刻分解后求和 · 两面板采用独立kN纵轴",23,color=MUTED)
for j,story in enumerate(["Story5","Story12"]):
    r=next(x for x in selected if x["Story"]==story)
    x0,x1=(135,690) if j==0 else (875,1430)
    y0,y1=235,670
    ymin,ymax,step=(-200,800,200) if j==0 else (0,300,50)
    yy=lambda value:y1-(value-ymin)/(ymax-ymin)*(y1-y0)
    label="第5层" if j==0 else "第12层（屋顶）"
    text((x0+x1)/2,186,f"({chr(97+j)}) {label} · t = {float(r['time_s']):.2f} s",25,"middle",bold=True)
    for tick in range(ymin,ymax+1,step):
        line(x0,yy(tick),x1,yy(tick),"#77858F" if tick==0 else "#E1E7EB",1.8 if tick==0 else 1)
        text(x0-20,yy(tick)+7,str(tick),21,"end")
    line(x0,y0,x0,y1,"#62727D",1.5)
    line(x0,y1,x1,y1,"#62727D",1.5)
    text(x0-88,460,"同刻削弱量（kN）",23,"middle",extra=f'transform="rotate(-90 {x0-88} 460)"')
    for k,(label,key,color) in enumerate(components):
        center=x0+92+k*185
        value=float(r[key])
        bar_top=min(yy(value),yy(0));height=abs(yy(value)-yy(0))
        rect(center-48,bar_top,96,height,color)
        baseline=yy(value)-14 if value>=0 else yy(value)+23
        rect(center-65,baseline-25,130,31,"white")
        text(center,baseline,f"{value:+.3f}",23,"middle",color,bold=True)
        text(center,742,label,22,"middle")
text(75,833,"同一时刻的对称分解：正值为沿原5%参照方向削弱，负值为抵消削弱。",22,color=MUTED)
text(75,877,"归一波形项不是纯相位；同刻净削弱不能当作两状态各自峰值之差。",22,color=MUTED)
with (O/"figure3-SHW3X-same-time-symmetric-decomposition.svg").open("x",encoding="utf-8") as f:
    f.write("".join(svg)+"</g></svg>\n")
with (O/"numeric-verification.json").open("x",encoding="utf-8") as f:
    json.dump({"source":{"path":str(source),"sha256":sha(source)},"source_rows":len(allrows),"selected_rows":selected,
        "plot_rows":len(data),"value_fields_read_from_CSV":True,"no_manual_numeric_values":True,
        "max_symmetric_sum_error_kN":max(abs(float(r[components[0][1]])+float(r[components[1][1]])-float(r[components[2][1]])) for r in selected),
        "unallocated_term_zero":True,"axes_independent_kN":True,"source_SHA_only_independent_review_pending":True,
        "plot_rounding":"3 decimal places; full precision retained in6row sourceCSV"},f,ensure_ascii=False,indent=2)
print(json.dumps({"SVG":"figure3-SHW3X-same-time-symmetric-decomposition.svg","source_rows":6,"scientific_review":"pending"}))
