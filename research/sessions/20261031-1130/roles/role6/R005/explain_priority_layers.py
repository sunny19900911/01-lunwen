"""Read frozen small CSVs only; summarize actual300 reference envelopes."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import json,csv,hashlib
HERE=Path(__file__).resolve().parent
SESSION=HERE.parents[2]
SOURCE=SESSION/"roles/role4/R005"
AUDIT=SESSION/"root-R004-term-audit"
START="2026-10-31T12:27:12+08:00"
manifest=json.loads((SOURCE/"delivery-manifest.json").read_text(encoding="utf-8"))
sources=[]
def readcsv(name):
    p=SOURCE/name;h=hashlib.sha256(p.read_bytes()).hexdigest()
    assert h==next(x["sha256"] for x in manifest["outputs"] if x["name"]==name)
    sources.append({"path":str(p),"sha256":h})
    with p.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
auditmanifest=json.loads((AUDIT/"manifest.json").read_text(encoding="utf-8"))
auditpath=AUDIT/"checks.json"
assert hashlib.sha256(auditpath.read_bytes()).hexdigest()==next(x["sha256"] for x in auditmanifest["files"] if x["name"]=="checks.json")
audit=json.loads(auditpath.read_text(encoding="utf-8"))
assert audit["must_changes"]==0
sources.append({"path":str(auditpath),"sha256":hashlib.sha256(auditpath.read_bytes()).hexdigest()})
pairs=readcsv("Story5-Story12-UPC-priority-6.csv")
anchors=readcsv("Story5-Story12-signed-reference-priority-48.csv")
coverage=readcsv("all12-fixed5-top5-envelope-summary-36.csv")
details=[];selected={}
for case in ["SHW3X","SHW4X","RH4X"]:
    env=readcsv(f"mode-envelopes-{case}-z0.05-3600.csv")
    for story in ["Story5","Story12"]:
        picked=sorted([x for x in env if x["Story"]==story and x["top5_fixed_from_5pct"]=="True"],key=lambda x:int(x["fixed_5pct_rank"]))
        assert len(picked)==5
        row=next(x for x in pairs if x["Case"]==case and x["Story"]==story)
        assert ";".join(x["Mode"] for x in picked)==row["top5_modes_fixed5"]
        for x in picked:
            details.append({"Case":case,"Story":story,"baseline_zeta":.05,"rank5":int(x["fixed_5pct_rank"]),
                "Mode":int(x["Mode"]),"independent_peak5_kN":float(x["reference_mode_abs_peak_kN"]),
                "weight5_percent":100*float(x["fixed_5pct_weight"]),
                "single_peak_time5_s":float(x["single_peak_time_s"]),
                "identity":"single-mode envelope weight; not simultaneous force share"})
        cap=next(x for x in coverage if x["Case"]==case and x["Story"]==story)
        assert abs(sum(float(x["fixed_5pct_weight"]) for x in picked)-float(cap["top5_sum_5pct_envelope_weights"]))<1e-12
        selected[case,story]=picked
with (HERE/"top5-baseline-envelope-weights-30.csv").open("x",encoding="utf-8-sig",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(details[0]));w.writeheader();w.writerows(details)
lines=["# R005：第5层与屋顶的三波工程解释","",
"**同样由5%增至8%，第5层以第2阶幅值为主，屋顶由多个模态共同决定，增阻尼后的组合变化因输入而异。** 以下为固定物理来源、无输出拟合的300阶弹性惯性线性参照；方向沿用参照定义，未试选软件反号。全部300阶用于U/P/C，top5只按5%排序展示，其余295阶保留。",
"","5%权重w_r=a_r,5/Σa_r,5，其中a=max|v_r|。括号内为独立峰幅权重%，不是同刻力份额；峰降幅列为参照/软件。",
"","|输入/层|5% top5：阶次(权重%)|U8/U5|C8/C5|峰降幅%：参照/软件|",
"|---|---|---:|---:|---:|"]
for case in ["SHW3X","SHW4X","RH4X"]:
    for story in ["Story5","Story12"]:
        row=next(x for x in pairs if x["Case"]==case and x["Story"]==story)
        desc="，".join(f"{x['Mode']}({100*float(x['fixed_5pct_weight']):.2f})" for x in selected[case,story])
        lines.append(f"|{case}/{story[5:]}|{desc}|{float(row['U8_over_U5']):.6f}|{float(row['C8_over_C5']):.6f}|{float(row['reference_peak_decrease_percent']):.4f}/{float(row['native_peak_decrease_percent']):.4f}|")
lines+=["",
"三波均保持两点：第5层第2阶权重为66.55%—71.81%，top5合计93.45%—94.52%；屋顶top5集合都是10、13、4、2、18，合计89.33%—91.81%，其余幅值预算仍为8.19%—10.67%。屋顶第10阶为25.05%—26.75%、第13阶20.82%—29.63%、第18阶6.21%—11.24%，说明这些阶次在局部切口具有不可忽略的响应量级，而非全楼参与率的简单排序。",
"",
"峰值关系P=UC给出两层差别。SHW3X第5层U下降9.65%，但C从0.78451升至0.80882，故0.903493×1.030990=0.931492，最终参照峰只降6.8508%；屋顶U与C同时降低，0.846186×0.847092=0.716798，峰降28.3202%。屋顶三波C8/C5都小于1，均使峰降大于U的降幅；第5层仅SHW4X的C略降，另两波C上升。C包含峰时不一致、符号和波形的共同效果，不单独称相位或瞬时抵消。",
"",
"有符号同刻项进一步区分幅值权重与受力组合。SHW3X屋顶21.18s的5%参照中，第10/13/18阶分别为−390.74/−369.31/−53.72kN，第4阶为+37.48kN，其余295阶合计−4.05kN，全部为−850.30kN；8%在同一时刻上述10/13/18阶变为−282.07/−229.18/−40.30kN。RH4X屋顶20.24s则不同：5%第10阶+284.52、第13阶−14.74、第18阶+64.78kN，全阶合成为+510.50kN；第13阶虽有21.86%的独立峰幅权重，此刻却是反向小项，不能据权重称它承担21.86%的剪力。",
"",
"峰时也随波变化：SHW3X、RH4X屋顶两态控制峰时分别保持21.18s、20.24s，SHW4X屋顶则由28.34s移至20.58s；第5层SHW3X/SHW4X各变化0.02s，RH4X不变。因而本三波稳定的是主模态集合与屋顶U/C共同下降，随波变化的是主项排序、峰时与同刻正负组合。工程判断应先看5%幅值预算确定主项，再沿完整曲线核新旧控制时刻，不能把独立峰值或不同时间的分项直接相加。",
"",
"边界：这些是已审数字支持的300阶线性物理参照解释，不等同完整FE的Ritz弹性恢复或实际FNA唯一逐阶分解。软件符号对应未独立确认，signed项不称原生同刻分力。原始48行重点层表保留四类锚点及两态，30项权重另存小CSV；来源与计时见freeze.json。"]
with (HERE/"one-page.md").open("x",encoding="utf-8") as f:f.write("\n".join(lines)+"\n")
start=datetime.fromisoformat(START);end=datetime.now(timezone(timedelta(hours=8)))
record={"status":"engineering interpretation of frozen audited reference terms; no new trajectories",
    "start_local":START,"freeze_local":end.isoformat(timespec="seconds"),
    "elapsed_seconds":(end-start).total_seconds(),"limit_seconds":480,"within_limit":(end-start).total_seconds()<=480,
    "only_small_csv_reads":True,"new_ODE_fit_or_selection_rule":False,"canonical_top5_preserved":True,
    "remaining295_retained":True,"source_fingerprints":sources,"root_audit_must_changes":audit["must_changes"],
    "weight_rows":len(details),"files":{p.name:{"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(HERE.iterdir()) if p.is_file() and p.name!="freeze.json"}}
with (HERE/"freeze.json").open("x",encoding="utf-8") as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps({k:v for k,v in record.items() if k not in ["source_fingerprints","files"]},ensure_ascii=False,indent=2))
