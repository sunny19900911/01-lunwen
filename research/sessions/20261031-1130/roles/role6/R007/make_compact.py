"""Publication variant: change text/canvas only; preserve R006 and all data geometry."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,hashlib
O=Path(__file__).resolve().parent
P=O.parent/"R006"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((P/"delivery-manifest.json").read_text(encoding="utf-8"))
before={p.name:sha(p) for p in P.iterdir() if p.is_file()}
ns="http://www.w3.org/2000/svg";ET.register_namespace("",ns)
def tag(name):return "{"+ns+"}"+name
def geometry(root):
    return [(e.tag,sorted(e.attrib.items())) for e in root.iter() if e.tag in [tag(t) for t in ["rect","line","polyline","circle","path","polygon"]]]
def core_text(root):
    excluded={"65","109","920","925","966","1007"}
    return [(sorted(e.attrib.items()),e.text) for e in root.iter(tag("text")) if e.attrib.get("y") not in excluded]
records=[]
configs=[
("figure1-actual-CM-UX-modes2-10-13.svg","figure1-compact-CM-UX-modes2-10-13.svg",
 "第2、10、13阶X向模态位移分量（隔板质心）",
 "各阶按 max|UX| 归一化；D2仅表示第3—8层已有质心数据。",
 "实际有控模型 · LinModRitz"),
("figure2-SHW3X-Story5-Story12-envelope-weights.svg","figure2-compact-SHW3X-modal-weights.svg",
 "SHW3X下第5层与屋顶的模态峰幅权重（阻尼比5%）",
 "权重取各阶独立峰幅，非同刻剪力份额；“其他”为余下296阶。",
 None)]
for old,new,title,foot,subtitle in configs:
    p=P/old
    assert sha(p)==next(x["sha256"] for x in m["files"] if x["name"]==old)
    tree=ET.parse(p);root=tree.getroot()
    oldgeom=geometry(root);oldtext=core_text(root)
    root.set("height","950");root.set("viewBox","0 0 1500 950")
    root.find(tag("title")).text=title
    g=root.find(tag("g"))
    for e in list(g):
        if e.tag!=tag("text"):continue
        y=e.attrib.get("y")
        if y=="65":e.text=title
        if y=="109" and subtitle:e.text=subtitle
        if y in ["925","966","1007"]:g.remove(e)
    e=ET.SubElement(g,tag("text"),{"x":"75","y":"920","font-size":"22","text-anchor":"start","fill":"#50616B","font-weight":"400"})
    e.text=foot
    assert geometry(root)==oldgeom
    assert core_text(root)==oldtext
    out=O/new
    with out.open("xb") as f:tree.write(f,encoding="utf-8",xml_declaration=False)
    records.append({"old_svg":old,"new_svg":new,"original_sha256":sha(p),
        "geometry_unchanged":True,"plot_numeric_and_legend_text_unchanged":True,
        "geometry_signature_sha256":hashlib.sha256(json.dumps(oldgeom,ensure_ascii=False).encode("utf-8")).hexdigest(),
        "canvas_before":[1500,1080],"canvas_after":[1500,950],"font_sizes_unchanged":True})
csvs=["figure1-CM-UX-normalized-source-54.csv","figure2-SHW3X-weights-source-10.csv"]
copied=[]
for name in csvs:
    assert sha(P/name)==next(x["sha256"] for x in m["files"] if x["name"]==name)
    with (O/name).open("xb") as f:f.write((P/name).read_bytes())
    assert sha(O/name)==sha(P/name)
    copied.append({"name":name,"sha256":sha(O/name),"same_bytes_as_R006":True})
assert before=={p.name:sha(p) for p in P.iterdir() if p.is_file()}
with (O/"variant-verification.json").open("x",encoding="utf-8") as f:
    json.dump({"records":records,"source_csvs":copied,"all_R006_file_hashes_unchanged":True,
        "R006_files_before":before,"new_response_calculation":False,"png_visual_QA":"pending"},f,ensure_ascii=False,indent=2)
print(json.dumps({"SVGs":2,"canvas":[1500,950],"source_CSVs_byte_identical":True,"all_R006_unchanged":True}))
