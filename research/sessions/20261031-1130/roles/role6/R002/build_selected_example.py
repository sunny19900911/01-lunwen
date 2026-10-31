"""Six-row conditional selected-mode illustration; no response analysis or fit."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime,timezone,timedelta
import csv,json,hashlib
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[2]/"roles/role4/R001"
START="2026-10-31T11:55:46+08:00"
manifest=json.loads((SOURCE/"delivery-manifest.json").read_text(encoding="utf-8"))
names=["conditional-mass-projection-examples-18.csv","modal-basis-identity-numeric-comparison-18.csv"]
tables={};sources=[]
for name in names:
    p=SOURCE/name
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    assert h==next(x["sha256"] for x in manifest["outputs"] if x["name"]==name)
    sources.append({"path":str(p),"sha256":h})
    with p.open(encoding="utf-8-sig",newline="") as f:tables[name]=list(csv.DictReader(f))
actual={int(x["Mode"]):x for x in tables[names[1]] if x["dataset"]=="actual_controlled"}
out=[]
for story in ["Story5","Story12"]:
    selected=[(i,r) for i,r in enumerate(tables[names[0]],2) if r["Axis"]=="X" and r["cut_story"]==story]
    assert sorted(int(r["Mode"]) for _,r in selected)==[2,10,13]
    den=sum((abs(F(r["B_candidate_kg"])) for _,r in selected),F(0))
    weights=[]
    for line,r in selected:
        mode=int(r["Mode"]);a=actual[mode]
        assert F(a["Period_s"])==F(r["actual_period_s"])
        assert r["actual_CaseType"]=="LinModRitz"
        w=abs(F(r["B_candidate_kg"]))/den;weights.append(w)
        out.append({"Story":story,"Axis":"X","Mode":mode,"actual_CaseType":"LinModRitz",
            "same_source_period_s":r["actual_period_s"],
            "actual_global_X_participating_mass_ratio_percent":float(100*F(a["mass_ratio_UX"])),
            "conditional_B_signed_kg":r["B_candidate_kg"],
            "conditional_B_signed_kN_per_m_s2":r["B_candidate_kN_per_m_s2"],
            "selected3_absB_weight_percent":float(100*w),"selected3_absB_weight_exact":str(w),
            "S_above_over_S_all":float(F(r["S_above_oldmass_CM_kg_m"])/F(r["S_all_oldmass_CM_kg_m"])),
            "same_source_mass_confirmed":r["same_source_mass_confirmed"],
            "selected_modes":"2;10;13","other_modes":"not evaluated, not zero-filled",
            "input_spectrum_or_wave_amplitude":"not supplied for this example",
            "source_projection_CSV_line":line,"actual_period_table_source_row":a["period_SourceRow"],
            "actual_mass_ratio_table_source_row":a["ratio_SourceRow"],
            "classification":"conditional mass/inertia projection only; selected3 coefficient normalization, not all-mode elastic shear or response share"})
    assert sum(weights,F(0))==1
with (HERE/"selected3-conditional-cut-comparison-6.csv").open("x",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
lines=["# R002：两个切口的三阶条件质量投影示例","",
"**本例仅比较实际有控LinModRitz的第2、10、13阶条件质量投影；不是已核主体弹性剪力分担。** 周期和参与表与实际有控CM模态同源，但候选投影暂用旧D质量分布，源表same_source_mass_confirmed=False；Ritz的切口恢复关系仍在独审。",
"","权重定义为 |B_r|/Σ_{j∈{2,10,13}}|B_j|，仅在三个选定阶内归一，没有输入谱/波幅值。表中B单位kN/(m/s²)，符号原样保留。",
"","|阶次|同源周期s|全楼X参与率%|第5层B|第5层三阶权重%|第12层B|第12层三阶权重%|",
"|---:|---:|---:|---:|---:|---:|---:|"]
for mode in [2,10,13]:
    a,b=[next(r for r in out if r["Mode"]==mode and r["Story"]==s) for s in ["Story5","Story12"]]
    lines.append(f"|{mode}|{float(a['same_source_period_s']):.6f}|{a['actual_global_X_participating_mass_ratio_percent']:.4f}|{float(a['conditional_B_signed_kN_per_m_s2']):+.3f}|{a['selected3_absB_weight_percent']:.2f}|{float(b['conditional_B_signed_kN_per_m_s2']):+.3f}|{b['selected3_absB_weight_percent']:.2f}|")
lines+=["",
"第5层三阶中第2阶投影较大；到第12层，三者的条件相对量级接近，第10阶还由负变正。第13阶全楼X参与率约1.02%，但其屋顶候选|B|约440.68kN/(m/s²)，与第2阶747.06处于可比较量级。原因是全楼参与率度量全楼质量投影，而切口以上的带符号振型质量投影不同；全楼正负相消较多的模态，在局部切口不一定同样抵消。小参与率仍限制绝对响应，不会因投影比值变大自动产生任意大剪力。",
"",
"因此，全楼参与率较小的高阶仍可能影响局部层，但必须将该切口的带符号输出系数与同一输入下的该阶响应相乘，再看完整合成曲线。表中25.91%只表示屋顶三个|B|候选值的归一结果，不能读成第13阶承担25.91%的实际剪力；未选模态没有评价，不能补零，也不能仅凭B的正负认定有利或不利。",
"",
"判断实际局部峰尚需三步：①核实际同源质量、所用切口及Ritz弹性剪力恢复关系，明确最终系数对应惯性量还是弹性剪力；②取得同一有控模态基和给定输入下的模态时程或适用的前向响应，实际Maxwell非线性响应不能直接换成独立SDOF统一增ζ；③计入其余模态及恢复残差，按同刻符号合成，并核原生峰幅、峰时及旧/新控制点。",
"",
"019的单位参与响应方法说明同一固定阶的非零参与/输出乘子可在两态幅比中消去，但其逐阶数值依赖具体频率、输入和模态基。本例只引用该方法，不按阶号移入019的峰幅比；配用的周期均取本有控源。源SHA、源行、六行小表与真实时段见freeze.json；未拟合、解ODE、设谱参数或新阈值，待②方法审核。"]
with (HERE/"one-page.md").open("x",encoding="utf-8") as f:f.write("\n".join(lines)+"\n")
start=datetime.fromisoformat(START);end=datetime.now(timezone(timedelta(hours=8)))
record={"status":"candidate conditional engineering example; method audit pending",
    "actual_start_local":START,"freeze_local":end.isoformat(timespec="seconds"),
    "elapsed_seconds":(end-start).total_seconds(),"limit_seconds":480,"within_limit":(end-start).total_seconds()<=480,
    "sources":sources,"source_SHA_checked":True,"row_count":6,"exact_selected3_weights_sum1":True,
    "conditional_mass_identity":False,"Ritz_elastic_output_certified":False,"other_modes_zero_filled":False,
    "new_fit_ODE_raw_extraction_or_spectrum":False,
    "files":{p.name:{"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(HERE.iterdir()) if p.is_file() and p.name!="freeze.json"}}
with (HERE/"freeze.json").open("x",encoding="utf-8") as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in record.items() if k not in ["sources","files"]},ensure_ascii=False,indent=2))
