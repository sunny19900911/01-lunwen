"""Frozen-rule comparison; small CSV only; no response calculation."""
from pathlib import Path
from collections import defaultdict
from statistics import median, mean
from datetime import datetime,timezone,timedelta
import csv,json,hashlib,math

P=Path(__file__).resolve().parent
SESSION=P.parents[2]
R4=SESSION/"roles/role4"
Z=(.06,.07,.08,.10)
PRIVATE="SHW3X_fixed300"
PUBLIC="publicExample5_H-E12140"
SOURCES={}
def read(rel):
    q=R4/rel
    SOURCES[str(rel)]=hashlib.sha256(q.read_bytes()).hexdigest()
    with q.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def save(name,rows):
    with (P/name).open("x",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        w.writeheader();w.writerows(rows)
def flags(pred,true):
    return {"false_pass":pred>=10 and true<10,"false_reject":pred<10 and true>=10,
            "false_adverse":pred<0 and true>=0,"missed_adverse":pred>=0 and true<0}

def main():
    rule=json.loads((P/"rules-freeze.json").read_text(encoding="utf-8"))
    S=read(Path("R006/baseline-sensitivity-ranked-floors-15.csv"))
    assert SOURCES["R006\\baseline-sensitivity-ranked-floors-15.csv"]=="37362b600ba419b383e6538e8fa6837a46fe5635b76db6e4f9271793e6c9388d"
    groups={c:{r["Story"]:r for r in S if r["Case"]==c} for c in (PRIVATE,PUBLIC)}
    assert [len(groups[c]) for c in (PRIVATE,PUBLIC)]==[12,3]
    med={c:median(float(r["S_percent_per_damping_pp"]) for r in d.values()) for c,d in groups.items()}
    # First form both simple predictions from S only, before joining the reference values.
    simple={}
    for c,d in groups.items():
        for story,r in d.items():
            s=float(r["S_percent_per_damping_pp"])
            assert math.isfinite(s)
            for z in Z:
                for method,rate in (("local_S",s),("uniform_median_S",med[c])):
                    simple[c,story,z,method]=rate*(100*(z-.05))
    truth={}
    for r in read(Path("R002/exact-reference-truth-peaks-48.csv")):
        truth[PRIVATE,r["Story"],float(r["target_zeta"])]=float(r["exact_reference_decrease_percent"])
    for r in read(Path("R005/exact-reference-floor-peaks-12.csv")):
        truth[PUBLIC,r["Story"],float(r["target_zeta"])]=float(r["reference_decrease_percent"])
    assert len(truth)==60
    def row(c,story,z,method,pred):
        t=truth[c,story,z]
        return dict(Case=c,Story=story,target_zeta=z,method=method,
                    S_floor=float(groups[c][story]["S_percent_per_damping_pp"]),
                    fixed_input_median_S=med[c],b_damping_pp=100*(z-.05),
                    predicted_D_percent=pred,reference_D_percent=t,
                    signed_error_pp=pred-t,absolute_error_pp=abs(pred-t),
                    point_decision="provisional_meets" if pred>=10 else "provisional_insufficient",
                    true_insufficient=t<10,true_adverse=t<0,**flags(pred,t))
    new=[row(c,s,z,m,v) for (c,s,z,m),v in simple.items()]
    old=[]
    for c,file in ((PRIVATE,"R002/frozen-prediction-vs-exact-reference-96.csv"),(PUBLIC,"R005/frozen-prediction-vs-reference-24.csv")):
        for r in read(Path(file)):
            pred=float(r["predicted_decrease_percent"]) if c==PRIVATE else 100*float(r["predicted_D"])
            old.append(row(c,r["Story"],float(r["target_zeta"]),"whole_window_order"+r["Taylor_order"],pred))
    assert len(new)==len(old)==120
    save("simple-point-baselines-120.csv",new)
    save("frozen-whole-window-point-comparators-120.csv",old)
    allrows=new+old
    summary=[]
    for c in (PRIVATE,PUBLIC):
        for method in ("local_S","uniform_median_S","whole_window_order1","whole_window_order2"):
            d=[r for r in allrows if r["Case"]==c and r["method"]==method]
            worst=max(d,key=lambda r:r["absolute_error_pp"])
            summary.append(dict(Case=c,method=method,n=len(d),bias_pp=mean(r["signed_error_pp"] for r in d),
                MAE_pp=mean(r["absolute_error_pp"] for r in d),max_absolute_error_pp=worst["absolute_error_pp"],
                worst_zeta=worst["target_zeta"],worst_story=worst["Story"],
                **{f:sum(r[f] for r in d) for f in ("false_pass","false_reject","false_adverse","missed_adverse","true_insufficient","true_adverse")},
                predicted_meets=sum(r["predicted_D_percent"]>=10 for r in d),
                predicted_adverse=sum(r["predicted_D_percent"]<0 for r in d)))
    save("method-summary-by-input-8.csv",summary)
    detailed=[]
    candidates=[]
    for base in summary:
        for z in Z:
            d=[r for r in allrows if r["Case"]==base["Case"] and r["method"]==base["method"] and r["target_zeta"]==z]
            detailed.append(dict(Case=base["Case"],method=base["method"],target_zeta=z,n=len(d),
                MAE_pp=mean(r["absolute_error_pp"] for r in d),max_absolute_error_pp=max(r["absolute_error_pp"] for r in d),
                **{f:sum(r[f] for r in d) for f in ("false_pass","false_reject","false_adverse","missed_adverse")}))
            pred=all(r["predicted_D_percent"]>=10 for r in d)
            actual=all(r["reference_D_percent"]>=10 for r in d)
            candidates.append(dict(Case=base["Case"],method=base["method"],target_zeta=z,
                target_floor_count=len(d),point_all_floor_meets=pred,reference_all_floor_meets=actual,
                candidate_false_pass=pred and not actual,candidate_false_reject=not pred and actual))
    save("method-candidate-errors-32.csv",detailed)
    save("whole-candidate-point-decisions-32.csv",candidates)
    misses=[r for r in allrows if any(r[f] for f in ("false_pass","false_reject","false_adverse","missed_adverse"))]
    save("all-point-misclassification-cases.csv",misses)
    interval=[]
    for c,file in ((PRIVATE,"R002/coth-interval-coverage-width-decisions-96.csv"),(PUBLIC,"R005/interval-coverage-width-decisions-24.csv")):
        data=read(Path(file))
        for order in (1,2):
            for z in Z:
                d=[r for r in data if int(r["Taylor_order"])==order and float(r["target_zeta"])==z]
                states=[r.get("interval_decision",r.get("decision_status")) for r in d]
                recompute=[r.get("operational_full_recompute",r.get("v001_operational_recompute"))=="True" for r in d]
                interval.append(dict(Case=c,Taylor_order=order,target_zeta=z,n=len(d),
                    meets=states.count("sufficient")+states.count("meets"),
                    insufficient=states.count("insufficient"),uncertain=states.count("uncertain"),
                    v001_operational_flagged_floors=sum(recompute),
                    interval_method="private sampled-coth" if c==PRIVATE else "public guarded-discrete",
                    scope="existing interval states only, not assigned to simple point baselines"))
    save("frozen-whole-window-interval-states-16.csv",interval)
    table=[]
    for r in summary:
        label={PRIVATE:"SHW3X（48项）",PUBLIC:"公开例（12项）"}[r["Case"]]
        table.append(f"|{label}|{r['method']}|{r['MAE_pp']:.3f}|{r['max_absolute_error_pp']:.3f}|{r['false_pass']} / {r['false_reject']}|{r['false_adverse']}|")
    candidate_lines=[]
    for c in (PRIVATE,PUBLIC):
        for m in ("local_S","uniform_median_S","whole_window_order1","whole_window_order2"):
            d=[r for r in candidates if r["Case"]==c and r["method"]==m]
            candidate_lines.append(f"- {c}，{m}：全层点预测通过{sum(r['point_all_floor_meets'] for r in d)}/4；误通过{sum(r['candidate_false_pass'] for r in d)}，误拒绝{sum(r['candidate_false_reject'] for r in d)}。")
    text="""# 两条简便基线与整时程预测的既有案例对照

比较两条仅用5%基准信息的点预测：各层局部外推D̂%=S层×b；全楼统一外推D̂%=该输入全部目标层S的固定中位数×b。b为5%基准后的阻尼增量百分点，6/7/8/10%分别对应1/2/3/5个百分点。统一基线的中位数不随候选或目标真值改变；所有负预测原样保留。

每个方法都覆盖SHW3X的12层×4候选及公开Example5/H-E12140的3层×4候选。输入与结果在本轮前已见，以下为既有案例方法对照，不称独立盲测。均比较同一数值参照的降幅，误差单位为百分点。

|输入|方法|降幅MAE|最大绝对误差|10%目标误通过 / 误拒绝（层—候选项）|不利误报|
|---|---|---:|---:|---:|---:|
"""+ "\n".join(table)+f"""

固定中位数S：SHW3X为{med[PRIVATE]:.9g}，公开例为{med[PUBLIC]:.9g}，单位均为降幅百分数/阻尼百分点。误通过指真降幅<10%却点预测≥10%；误拒绝为相反情况；不利误报指点预测<0而真降幅≥0。完整逐候选误差、最差层和全部误判身份均保留，没有仅挑误差较小的目标。

统一系数使同一输入各层获得相同降幅，因而丢掉S表已有的楼层差异。逐层S保留局部差异，但只延伸基准控制峰的一阶趋势，不能随有限增量重新选择竞争峰。整时程预测允许更新预测峰，却仍有有限Taylor误差；上表与逐项小表共同用于评价，不预设复杂方法逐项胜出。

## 全楼点判断与区间判断分开

以下每行只有4个物理候选，均要求全部目标层达到10%；不是按每个标记层各求解一次。
"""+ "\n".join(candidate_lines)+"""

这些均为点预测暂判，不附区间保证。既有一/二阶区间的达到、不足、不确定和v001复算标记另存frozen-whole-window-interval-states-16.csv；两条新基线没有区间，不套用这些区间，也不把点预测误拒绝与v002的区间拒绝混为一项。本次两输入的真实不利样本均为0，漏判不利响应的比率为不适用；层和候选也不是独立地震事件。

两种简便基线也需要先计算基准导数；统一中位数需要全部目标层S。最后一步乘法的工作量不能代表完整成本，目前没有端到端提速结论。本表说明整体折减会忽略层差、局部外推不能处理有限增量换峰，同时保留了整时程方法的失败案例。
"""
    with (P/"one-page.md").open("x",encoding="utf-8",newline="\n") as f:f.write(text)
    result={"fixed_median_S":med,"summary":summary,"candidate_summary":candidate_lines,
            "simple_prediction_rows":120,"whole_window_point_rows":120,"source_sha256":SOURCES,
            "rules_sha256":hashlib.sha256((P/"rules-freeze.json").read_bytes()).hexdigest(),
            "join_completed":datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "new_truth_calculated":False,"SHW4_read":False,"independent_blind_test":False}
    with (P/"results.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write("\n")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":main()
