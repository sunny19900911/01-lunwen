"""Fixed top-two-with-ties force coverage, from the 192-row summary only."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from fractions import Fraction as Q
from pathlib import Path

SOURCE_SHA = "8d359f9c86b544aaa6c573618a375eef7beb8f02070dc223f2802ce3fe31864d"
PROTOCOL_SHA = "eaa8eac1432e38f889d5112fa28a047d5dd2af81b65da8b18f99f2e43b3c1c87"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def top2(values):
    threshold = sorted(values.values(), reverse=True)[1]
    return {j for j, value in values.items() if value >= threshold}, threshold


def diagnose(peaks, selected):
    maximum = max(peaks.values())
    maximum_ids = {j for j, p in peaks.items() if p == maximum}
    peak_top, _ = top2(peaks)
    selected_maximum = max(peaks[j] for j in selected)
    lf = 1 - selected_maximum / maximum if maximum > 0 else None
    covered = selected & maximum_ids
    state = "all_covered" if covered == maximum_ids else "none_covered" if not covered else "partly_covered"
    return dict(Pmax=maximum, Psel=selected_maximum, LF=lf, maximum_ids=maximum_ids, peak_top=peak_top, missing_max=maximum_ids-selected, missing_top=peak_top-selected, coverage=selected&peak_top, recall=Q(len(selected&peak_top),len(peak_top)), max_coverage_state=state)


def synthetic():
    a = {str(i): Q(p) for i, p in enumerate([10,9,8,1])}
    d = diagnose(a,{"2","3"}); assert d["LF"]==Q(1,5) and d["recall"]==0
    d = diagnose(a,{"0","2"}); assert d["LF"]==0 and d["recall"]==Q(1,2)
    b = {str(i): Q(p) for i,p in enumerate([10,10,9,1])}
    d = diagnose(b,{"0","2"}); assert d["max_coverage_state"]=="partly_covered" and d["LF"]==0
    c = {str(i): Q(p) for i,p in enumerate([10,9,9,1])}
    d = diagnose(c,{"0","1"}); assert len(d["peak_top"])==3 and d["recall"]==Q(2,3)
    selected,_ = top2({"A":Q(2),"B":Q(2),"C":Q(2),"D":Q(1)})
    assert len(selected)==3
    z = diagnose({j:Q(0) for j in a},{"0","1"}); assert z["LF"] is None
    return dict(passed=True,checks=6)


def ids(values): return ";".join(sorted(values))
def dec(value): return "" if value is None else format(float(value),".17g")
def exact(value): return "" if value is None else str(value)


def write_csv(path,rows,fields=None):
    with path.open("x",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields or list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--summary",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    owner=Path(__file__).resolve().parent
    output=args.out.resolve()
    assert output.is_relative_to(owner)
    output.mkdir(parents=True,exist_ok=False)
    assert sha(owner/"protocol.md")==PROTOCOL_SHA
    tests=synthetic()  # Run before this task reads numerical summary values.
    assert sha(args.summary)==SOURCE_SHA
    groups=defaultdict(dict)
    with args.summary.open(encoding="utf-8-sig",newline="") as stream:
        source=list(csv.DictReader(stream))
    assert len(source)==192
    for row in source:
        group=groups[(row["Case"],row["Story"])]
        assert row["Link"] not in group
        assert Q(row["max_abs_native_P_kN"])>=0
        group[row["Link"]]=row
    assert len(groups)==24 and all(len(v)==8 for v in groups.values())
    assert {s for _,s in groups}=={"Story8","Story9","Story10","Story11"}
    assert {c for c,_ in groups}=={"RH4X","RH4Y","SHW4X","SHW4Y","SHW7X","SHW7Y"}
    omissions,global_omissions,methods={},[],{}
    all_missing_top=[]
    omission_fields=["method","Case","Story","Link","native_Ppeak_kN","group_Pmax_kN","selected_Pmax_kN","L_F","L_F_exact","is_global_max_controller","global_max_coverage_state","peak_top2_recall","native_force_peak_controllers_json"]
    for method,column in [("conditional_Dport","Dport_conditional_kNm"),("native_Wtrap","Wtrap_native_kNm")]:
        rows=[]
        for (case,story),items in sorted(groups.items()):
            peaks={j:Q(row["max_abs_native_P_kN"]) for j,row in items.items()}
            scores={j:Q(row[column]) for j,row in items.items()}
            selected,threshold=top2(scores)
            d=diagnose(peaks,selected)
            if d["Pmax"]>0:
                assert (d["LF"]>0)==(d["max_coverage_state"]=="none_covered")
            row=dict(method=method,Case=case,Story=story,n_devices=8,selected_count=len(selected),selected_ids=ids(selected),score_second_threshold=dec(threshold),selected_peak_values_json=json.dumps({j:items[j]["max_abs_native_P_kN"] for j in sorted(selected)},separators=(",",":")),Pmax_kN=dec(d["Pmax"]),Psel_kN=dec(d["Psel"]),L_F=dec(d["LF"]),L_F_exact=exact(d["LF"]),LF_reason="" if d["LF"] is not None else "zero_group_peak_no_force_discrimination",global_max_ids=ids(d["maximum_ids"]),global_max_coverage_state=d["max_coverage_state"],all_global_max_omitted=not bool(selected&d["maximum_ids"]),any_global_max_omitted=bool(d["missing_max"]),omitted_global_max_ids=ids(d["missing_max"]),peak_top2_ids=ids(d["peak_top"]),peak_top2_count=len(d["peak_top"]),covered_peak_top2_ids=ids(d["coverage"]),covered_peak_top2_count=len(d["coverage"]),peak_top2_recall=dec(d["recall"]),peak_top2_recall_exact=exact(d["recall"]),omitted_peak_top2_ids=ids(d["missing_top"]))
            rows.append(row)
            for link in sorted(d["missing_top"]):
                detail=dict(method=method,Case=case,Story=story,Link=link,native_Ppeak_kN=items[link]["max_abs_native_P_kN"],group_Pmax_kN=dec(d["Pmax"]),selected_Pmax_kN=dec(d["Psel"]),L_F=dec(d["LF"]),L_F_exact=exact(d["LF"]),is_global_max_controller=link in d["maximum_ids"],global_max_coverage_state=d["max_coverage_state"],peak_top2_recall=dec(d["recall"]),native_force_peak_controllers_json=items[link]["force_peak_controllers_json"])
                all_missing_top.append(detail)
                if link in d["missing_max"]: global_omissions.append(detail)
        assert len(rows)==24
        write_csv(output/(method+"_groups.csv"),rows)
        methods[method]=dict(rows=24,positive_LF_groups=sum(Q(r["L_F_exact"])>0 for r in rows if r["L_F_exact"]),LF_zero_but_incomplete_recall=sum(r["L_F_exact"]=="0" and Q(r["peak_top2_recall_exact"])<1 for r in rows),full_peak_top2_recall_groups=sum(r["peak_top2_recall_exact"]=="1" for r in rows),zero_peak_groups=sum(not r["L_F_exact"] for r in rows),selected_count_values=sorted({r["selected_count"] for r in rows}))
        omissions[method]=rows
    write_csv(output/"omitted_peak_top2.csv",all_missing_top,omission_fields)
    write_csv(output/"omitted_global_max.csv",global_omissions,omission_fields)
    same=sum(a["selected_ids"]==b["selected_ids"] for a,b in zip(omissions["conditional_Dport"],omissions["native_Wtrap"]))
    assert sha(args.summary)==SOURCE_SHA and sha(owner/"protocol.md")==PROTOCOL_SHA
    record=dict(recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),status="author_derived_candidate_pending_independent_review",source_summary_sha256=SOURCE_SHA,protocol_sha256=PROTOCOL_SHA,script_sha256=sha(Path(__file__).resolve()),synthetic_checks=tests,groups=24,input_rows=192,methods=methods,selection_sets_same_between_W_and_D_groups=same,omitted_peak_top2_detail_rows=len(all_missing_top),omitted_global_max_detail_rows=len(global_omissions),no_NPZ_Excel_fit_or_k_sensitivity=True)
    (output/"run_record.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(record,ensure_ascii=False))


if __name__=="__main__": main()
