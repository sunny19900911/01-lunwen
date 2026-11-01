"""Aggregate frozen small tables only; no structural response calculations."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone, timedelta
import csv, hashlib, json, math

HERE = Path(__file__).resolve().parent
SESSION = HERE.parents[2]
UP = SESSION/"roles/role4/R002"
FLOORS = tuple(f"Story{k}" for k in range(1,13))
THRESHOLD, WIDTH = .10,.05
TZ = timezone(timedelta(hours=8))


def read_csv(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))


def write_csv(name, rows):
    with (HERE/name).open("x",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    policy_path=SESSION/"candidate-level-policy-v002-freeze.json"
    policy=json.loads(policy_path.read_text(encoding="utf-8"))
    previous=json.loads((SESSION/"engineering-policy-freeze-v001.json").read_text(encoding="utf-8"))
    assert previous["demonstration_Dreq"]==THRESHOLD and previous["width_limit_D_fraction"]==WIDTH
    manifest_path=UP/"delivery-manifest.json"
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    audit=json.loads((SESSION/"roles/role2/R003/manifest.json").read_text(encoding="utf-8"))
    assert audit["must_fix"]==0
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest()==audit["upstream_manifest_sha256"]
    expected={r["name"]:r["sha256"] for r in manifest["outputs"]}
    names=["baseline-only-coth-bound-prediction-intervals-96.csv","candidate-level-recompute-accounting-8.csv","exact-reference-truth-peaks-48.csv","workload-and-measured-cost-ledger-8.csv"]
    hashes={}
    for name in names:
        actual=hashlib.sha256((UP/name).read_bytes()).hexdigest()
        assert actual==expected[name],name
        hashes[name]=actual
    predictions=read_csv(UP/names[0])
    old={(float(r["target_zeta"]),int(r["Taylor_order"])):r for r in read_csv(UP/names[1])}
    # Decisions use interval-only source. Reference truth is joined only after these decisions.
    decisions=[]
    for zeta in (.06,.07,.08,.10):
        for order in (1,2):
            rows={r["Story"]:r for r in predictions if float(r["target_zeta"])==zeta and int(r["Taylor_order"])==order}
            assert set(rows)==set(FLOORS)
            def valid(r):
                v=[float(r[k]) for k in ("P0_kN","D_lower","D_upper","D_interval_width")]
                return all(math.isfinite(x) for x in v) and v[0]>0 and v[1]<=v[2] and v[3]>=0
            rejected=[s for s in FLOORS if valid(rows[s]) and float(rows[s]["D_upper"])<THRESHOLD]
            passed=all(valid(rows[s]) and float(rows[s]["D_lower"])>=THRESHOLD and float(rows[s]["D_interval_width"])<=WIDTH for s in FLOORS)
            outcome="reject" if rejected else "pass" if passed else "recompute"
            witness=min(rejected,key=lambda s:float(rows[s]["D_upper"])) if rejected else ""
            flag_count=sum(r["operational_full_recompute"]=="True" for r in rows.values())
            old_count=int(old[zeta,order]["unique_full_building_recompute_count_if_all_flagged_layers_checked"])
            assert flag_count==int(old[zeta,order]["operational_flagged_layers"])
            assert old_count==int(flag_count>0)
            assert bool(rejected)==(old[zeta,order]["mathematical_whole_building_decision"]=="insufficient")
            decisions.append({
                "record":"SHW3X","scope":"development_set_retrospective",
                "target_zeta":zeta,"Taylor_order":order,"target_floor_count":12,
                "target_floors":";".join(FLOORS),"v002_decision":outcome,
                "insufficient_interval_floor_count":len(rejected),
                "insufficient_interval_floors":";".join(rejected),
                "rejection_witness":witness,
                "witness_D_upper":float(rows[witness]["D_upper"]) if witness else "",
                "too_wide_floor_count":sum(float(r["D_interval_width"])>WIDTH for r in rows.values()),
                "v001_flagged_floor_count":flag_count,"v001_full_recompute_per_candidate":old_count,
                "v002_full_recompute_per_candidate":int(outcome=="recompute"),
            })
    write_csv("candidate-decisions-from-intervals-8.csv",decisions)
    truth=read_csv(UP/names[2])
    actuals={}
    for zeta in (.06,.07,.08,.10):
        t={r["Story"]:r for r in truth if float(r["target_zeta"])==zeta}
        assert set(t)==set(FLOORS)
        decrease={s:float(t[s]["exact_reference_decrease_percent"])/100 for s in FLOORS}
        actuals[zeta]={"truth_meets":all(x>=THRESHOLD for x in decrease.values()),
                       "truth_adverse":any(x<0 for x in decrease.values()),
                       "truth_min_D":min(decrease.values()),
                       "truth_min_floor":min(decrease,key=decrease.get)}
    evaluation=[]
    for d in decisions:
        a=actuals[d["target_zeta"]]
        outcome=d["v002_decision"]
        evaluation.append(dict(d,**a,
            false_pass=(outcome=="pass" and not a["truth_meets"]),
            false_reject=(outcome=="reject" and a["truth_meets"]),
            adverse_missed_pass=(outcome=="pass" and a["truth_adverse"])))
    write_csv("candidate-retrospective-truth-check-8.csv",evaluation)
    summaries=[]
    for order in (1,2):
        d=[r for r in evaluation if r["Taylor_order"]==order]
        counts=Counter(r["v002_decision"] for r in d)
        summaries.append({
            "Taylor_order":order,"candidate_count":len(d),
            "reject":counts["reject"],"pass":counts["pass"],"recompute":counts["recompute"],
            "v001_recompute":sum(r["v001_full_recompute_per_candidate"] for r in d),
            "truth_meeting_candidates":sum(r["truth_meets"] for r in d),
            "truth_insufficient_candidates":sum(not r["truth_meets"] for r in d),
            "false_pass":sum(r["false_pass"] for r in d),
            "false_reject":sum(r["false_reject"] for r in d),
            "true_adverse_candidates":sum(r["truth_adverse"] for r in d),
            "unsafe_pass_rate_given_pass":"NA: no pass",
            "adverse_missed_pass_rate":"NA: no adverse candidate",
        })
    write_csv("candidate-policy-summary-2.csv",summaries)
    table=[]
    for zeta in (.06,.07,.08,.10):
        first=next(d for d in evaluation if d["target_zeta"]==zeta and d["Taylor_order"]==1)
        second=next(d for d in evaluation if d["target_zeta"]==zeta and d["Taylor_order"]==2)
        translate={"reject":"拒绝","pass":"通过","recompute":"复算"}
        table.append(f"|{zeta:.0%}|{translate[first['v002_decision']]}|{translate[second['v002_decision']]}|{100*first['truth_min_D']:.6f}%（{first['truth_min_floor']}）|")
    report="""# 候选阻尼方案的提前判断：SHW3X开发集回顾

在冻结v002规则下，一阶外推对4个候选拒绝1个、通过0个、需复算3个；二阶拒绝2个、通过0个、需复算2个。旧v001规则在两种阶次下均为4/4候选需完整分析。这是已看过SHW3X结果后的开发集回顾，体现规则对分析次数的影响，不是独立验证或实测省时。

## 工程目标与候选计数

目标集合固定为Story1至Story12全部12层，要求每层剪力峰值相对5%基准降低至少10%。Dreq=10%、允许改善区间宽度5个百分点均为本项目演示输入。12层全部保留，不按结果删除楼层。

任一目标层有有效区间且DU<10%，便可拒绝“全楼各目标层均达标”的候选，即使其他层区间不确定或过宽。通过要求所有目标层DL≥10%、区间宽≤5个百分点且数据有效。其余候选完整复算一次。拒绝只表示该候选不能满足当前全层目标，不等于其毫无减震效果。

|候选ζ|v002一阶|v002二阶|参考最小改善率|
|---:|---|---|---:|
"""+ "\n".join(table)+"""

v001对表中每个候选、每种阶次均要求复算；其原8/8结果不改写。v002合计8个“候选—方法”评价中拒绝3、通过0、复算5，分别为37.5%、0%、62.5%。这些是4个物理阻尼候选的两种方法评价，不是8个独立方案或事件。实际部署应事先选定方法；一阶需复算7%、8%、10%三个候选，二阶需复算8%、10%两个候选，不能事后按各候选较有利的方法拼接。

## 区间宽度、误判与适用性

6%一阶可据不足层拒绝，但11/12层仍过宽；7%二阶拒绝时9/12层过宽。单侧不足区间有助于排除全层目标，但不代表峰值预测已达到5个百分点精度。逐层宽度、不确定性和失败样本均保留。

参考结果中6%、7%、8%均有未达10%的层，10%各层均达到目标。3项拒绝均与参考一致，误拒绝0；两种方法各有1个真实达标候选，均转复算。没有任何提前通过，因此无法评价通过后出错的条件概率；也不能把没有通过造成的零假通过当作通过可靠性证据。参考不利候选为0，不利漏放率为不适用。

区间采用既有采样残差尺度和精确核L1构造，本次只核对既有数值网格，未给连续时间极值或积分误差保证。旧8%还是历史已知案例。新公开模型及其他输入的前瞻评价另行进行。

## 计算代价和设计步骤

每个候选完整分析产生全部目标层结果，同一候选的多个标记层只计一次求解。开发集已生成的参考真值保留为验证成本；本回顾没有撤销已发生的求解，也没有测得实际减少的运行时间。

完整成本应为：一次基准及导数准备，加上每候选预测合成和区间计算，再加需要复算候选的完整分析及全部I/O。现有准备包含一/二阶导数系统、4个微扰校验和8组输出预测；导数准备与I/O尚无完整分项计时。已知区间合计约0.0654 s、6/7/10%参考各约0.06 s的局部计时不能替代端到端比较。即使完整分析触发次数较少，准备开销仍可能使总成本增加。

工程使用依次为：固定目标层、改善率和区间宽度要求；选定预测方法并计算基准/导数；逐候选形成全部目标层区间；先检查是否存在确定不足层，再检查是否全部达标且宽度合格；其余候选完整复算一次，并记录拒绝、通过、复算、误判及总成本。需要优化某些关键层时，应事先另定目标集合，不能沿用本表的全层结论。

本项只汇总已独审的小表，没有新增地震响应、灵敏度、布局或目标真值。候选判据来自根candidate-level-policy-v002-freeze.json；输入与审核散列见freeze.json。
"""
    with (HERE/"one-page.md").open("x",encoding="utf-8",newline="\n") as f:
        f.write(report)
    metrics={"per_order":summaries,"evaluation_rows":8,"physical_candidates":4,"rejected_method_candidate_rows":3,"passed_rows":0,"recompute_rows":5,"previous_recompute_rows":8,"independent_validation":False,"measured_speedup_claim":False,"source_hashes":hashes,"policy_sha256":hashlib.sha256(policy_path.read_bytes()).hexdigest()}
    with (HERE/"results.json").open("x",encoding="utf-8",newline="\n") as f:
        json.dump(metrics,f,ensure_ascii=False,indent=2);f.write("\n")
    assert [(s["reject"],s["pass"],s["recompute"]) for s in summaries]==[(1,0,3),(2,0,2)]
    print(json.dumps(metrics,ensure_ascii=False))


if __name__=="__main__":
    main()
