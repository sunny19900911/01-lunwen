"""Plot only the three independently audited baseline S tables."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,html,math
P=Path(__file__).resolve().parent
SESSION=P.parents[2]
SPECS=[
 ("SHW3X","R007","author-floor-summary-15.csv","S_percent_per_damping_pp",5,"2.132064","#24779b",""),
 ("SHW4X","R008","independent-S-floors-12.csv","S",1,"4.347595","#c76536","10 6"),
 ("RH4X","R009","independent-S-floors-12.csv","S",7,"8.231270","#398763","3 5")]
INK="#263b48";GRID="#e1e7eb"
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(a,x,y,t,size=24,anchor="middle",weight="normal",color=INK):
    a.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}">{html.escape(str(t))}</text>')
def line(a,x1,y1,x2,y2,color=GRID,width=1):
    a.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{width}"/>')
def marker(a,x,y,i,color,large=False):
    if i==0:
        a.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{10 if large else 5.5}" fill="{color}" stroke="white" stroke-width="{2.5 if large else 1.5}"/>')
    elif i==1:
        r=11 if large else 5.5
        a.append(f'<rect x="{x-r:.3f}" y="{y-r:.3f}" width="{2*r}" height="{2*r}" fill="none" stroke="{color}" stroke-width="{3 if large else 2.2}"/>')
    else:
        r=12 if large else 7
        a.append(f'<polygon points="{x:.3f},{y-r:.3f} {x-r:.3f},{y+r*.75:.3f} {x+r:.3f},{y+r*.75:.3f}" fill="{color}" stroke="white" stroke-width="{2.5 if large else 1.2}"/>')
def main():
    records=[];provenance=[];curves=[]
    for short,role,filename,column,minfloor,label,color,dash in SPECS:
        directory=SESSION/"roles/role2"/role
        src=directory/filename
        manifest=json.loads((directory/"manifest.json").read_text(encoding="utf-8"))
        assert manifest["must_fix"]==0
        expected=next(x["sha256"] for x in manifest["artifacts"] if x["name"]==filename)
        assert digest(src)==expected
        with src.open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
        if short=="SHW3X":rows=[r for r in rows if r["Case"]=="SHW3X_fixed300"]
        rows.sort(key=lambda r:int(r["Story"][5:]))
        assert [r["Story"] for r in rows]==[f"Story{i}" for i in range(1,13)]
        vals=[float(r[column]) for r in rows]
        assert all(math.isfinite(v) for v in vals)
        assert min(range(12),key=lambda k:vals[k])+1==minfloor
        assert f"{vals[minfloor-1]:.6f}"==label
        curve=[]
        for r,value in zip(rows,vals):
            out={"Input":short,"Story":r["Story"],"floor":int(r["Story"][5:]),
                 "S":r[column],"baseline_minimum":int(r["Story"][5:])==minfloor}
            records.append(out);curve.append(out)
        curves.append(curve)
        provenance.append({"Input":short,"source":str(src.relative_to(SESSION)).replace("\\","/"),
                           "sha256":expected,"bytes":src.stat().st_size,
                           "audit_manifest":str((directory/"manifest.json").relative_to(SESSION)).replace("\\","/"),
                           "audit_manifest_sha256":digest(directory/"manifest.json")})
    assert len(records)==36
    with (P/"three-input-S-source-36.csv").open("x",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator="\n");w.writeheader();w.writerows(records)
    a=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1200" viewBox="0 0 1600 1200"><rect width="100%" height="100%" fill="white"/><g font-family="Microsoft YaHei,Arial,sans-serif" fill="'+INK+'">']
    text(a,800,55,"不同输入下的楼层剪力改善敏感度",36,weight="bold")
    text(a,800,105,"5%基准阻尼 · 同一结构的固定300阶线性参照",24)
    for i,(short,role,filename,column,minfloor,label,color,dash) in enumerate(SPECS):
        center=335+i*465
        a.append(f'<line x1="{center-130}" y1="155" x2="{center-58}" y2="155" stroke="{color}" stroke-width="3" stroke-dasharray="{dash}"/>')
        marker(a,center-94,155,i,color)
        text(a,center-35,164,short,27,"start","bold")
        text(a,center,202,f"基准最小：第{minfloor}层 · {label}",23)
    left,right,top,bottom=155,1465,250,970
    X=lambda value:left+value/16*(right-left)
    Y=lambda floor:bottom-(floor-.5)/12*(bottom-top)
    for tick in range(0,17,2):
        line(a,X(tick),top,X(tick),bottom);text(a,X(tick),bottom+42,tick,24)
    for floor in range(1,13):
        line(a,left,Y(floor),right,Y(floor),GRID,1)
        text(a,left-25,Y(floor)+9,floor,25,"end")
    line(a,left,top,left,bottom,INK,1.7);line(a,left,bottom,right,bottom,INK,1.7)
    for i,(spec,curve) in enumerate(zip(SPECS,curves)):
        color,dash=spec[6],spec[7]
        points=" ".join(f'{X(float(r["S"])):.3f},{Y(r["floor"]):.3f}' for r in curve)
        a.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="{dash}"/>')
    # Draw hollow orange markers first so nearly coincident blue floor1 stays visible.
    for i in (1,0,2):
        color=SPECS[i][6]
        for r in curves[i]:marker(a,X(float(r["S"])),Y(r["floor"]),i,color,r["baseline_minimum"])
        r=next(x for x in curves[i] if x["baseline_minimum"])
        x,y=X(float(r["S"])),Y(r["floor"])
        if i==1:text(a,x+18,y+28,"第1层",23,"start","bold",color)
        else:text(a,x-16,y+8,f'第{r["floor"]}层',23,"end","bold",color)
    text(a,810,1060,"S（降幅%/阻尼百分点）",28)
    text(a,72,615,"楼层",28)
    text(a,800,1133,"大标记为各输入的基准最小S所在层；有限阻尼增量仍应结合候选峰值区间判断。",23)
    a.append("</g></svg>")
    with (P/"figure3-three-input-S-profile-v001.svg").open("x",encoding="utf-8",newline="\n") as f:f.write("\n".join(a)+"\n")
    v={"prepared_at":datetime.now(timezone(timedelta(hours=8))).isoformat(),"source_rows":36,"curves":3,"floors_per_curve":12,
       "sources_match_independent_audit_manifests":True,"source_provenance":provenance,
       "minima":[{"Input":r[0],"floor":r[4],"label_S":r[5]} for r in SPECS],
       "only_baseline_S":True,"Senv_read":False,"no_new_response_or_S_computed":True}
    with (P/"source-and-selfcheck.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write("\n")
    print(json.dumps(v,ensure_ascii=False))
if __name__=="__main__":main()
