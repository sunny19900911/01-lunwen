"""Exact rational ordering of fixed-summary affine energy accounts; no histories."""
import argparse
import bisect
import csv
import hashlib
import itertools
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from fractions import Fraction as Q
from pathlib import Path

AHAT = Q("2.0006042528243313e-6")
SOURCE_SHA = "8d359f9c86b544aaa6c573618a375eef7beb8f02070dc223f2802ce3fe31864d"
PROTOCOL_SHA = "04db606fccb9b318414f5a0967f11666137fa180a3fc90414344c1a458a57c8e"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sets(values):
    ordered = sorted(values.values())
    return (tuple(sorted(j for j, s in values.items() if s >= ordered[-2])),
            tuple(sorted(j for j, s in values.items() if s <= ordered[1])))


def pattern(items, a):
    return sets({j: x["W"] - a * x["H"] for j, x in items.items()})


def pair_data(items):
    result, roots = [], set()
    for i, j in itertools.combinations(sorted(items), 2):
        dw, dh = items[i]["W"] - items[j]["W"], items[i]["H"] - items[j]["H"]
        root = dw / dh if dh else None
        kind = ("positive_root" if root > 0 else "zero_root" if root == 0 else "negative_root") if dh else ("identical_all_a" if dw == 0 else "parallel_no_root")
        result.append(dict(Link_i=i, Link_j=j, delta_W=dw, delta_H=dh, root=root, kind=kind))
        if root is not None and root > 0:
            roots.add(root)
    return result, sorted(roots)


def solve(items, ahat):
    pairs, roots = pair_data(items)
    target = pattern(items, ahat)
    bounds = [Q(0), *roots, None]
    cells = []
    for lo, hi in zip(bounds, bounds[1:]):
        sample = (lo + hi) / 2 if hi is not None else 2 * lo if lo else ahat
        cells.append(pattern(items, sample))
    if ahat in roots:
        r = roots.index(ahat)
        if cells[r] != target or cells[r + 1] != target:
            return dict(status="no_open_interval_at_ahat_boundary_tie", lower=None, upper=None, target=target, pairs=pairs, roots=roots)
        left, right = r, r + 1
    else:
        left = right = bisect.bisect_right(roots, ahat)
        assert cells[left] == target
    while left > 0 and cells[left - 1] == target and pattern(items, roots[left - 1]) == target:
        left -= 1
    while right < len(roots) and cells[right + 1] == target and pattern(items, roots[right]) == target:
        right += 1
    return dict(status="maximal_open_interval", lower=bounds[left], upper=bounds[right + 1], target=target, pairs=pairs, roots=roots)


def synthetic_checks():
    def items(rows):
        return {j: dict(W=Q(w), H=Q(h)) for j, w, h in rows}
    x = items([("A", 10, 1), ("B", 9, 0), ("C", 8, -1), ("D", 0, 0)])
    a = solve(x, Q(1, 2)); assert (a["lower"], a["upper"]) == (0, 1)
    b = solve(x, Q(1)); assert b["status"] == "no_open_interval_at_ahat_boundary_tie"
    c = solve(x, Q(2)); assert (c["lower"], c["upper"]) == (1, None)
    y = items([("A", 10, 1), ("B", 9, -1), ("C", 0, 0), ("D", -1, 0)])
    d = solve(y, Q(1, 5)); assert (d["lower"], d["upper"]) == (0, 10)
    e = solve(y, Q(1, 2)); assert (e["lower"], e["upper"]) == (0, 10)
    z = items([("A", 10, 0), ("B", 9, 0), ("C", 9, 0), ("D", 0, 0)])
    f = solve(z, Q(1)); assert (f["lower"], f["upper"]) == (0, None) and len(f["target"][0]) == 3
    return dict(passed=True, cases=["finite_boundary", "nonpersistent_cut_tie_at_baseline", "lower_boundary_unbounded_right", "internal_crossing_merged", "baseline_internal_tie_merged", "parallel_and_identical_lines_with_persistent_ties"])


def exact(x):
    return "" if x is None else str(x)


def dec(x):
    return "" if x is None else format(float(x), ".17g")


def names(x):
    return ";".join(x)


def csv_write(p, rows):
    with p.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    owner = Path(__file__).resolve().parent
    out = args.out.resolve()
    if not out.is_relative_to(owner): raise ValueError("Output outside owned directory")
    out.mkdir(parents=True, exist_ok=False)
    protocol = owner / "R005-protocol.md"
    assert sha(protocol) == PROTOCOL_SHA
    # These tests precede any read of the real numerical summary.
    synthetic = synthetic_checks()
    assert sha(args.summary) == SOURCE_SHA
    with args.summary.open(encoding="utf-8-sig", newline="") as stream:
        source_rows = list(csv.DictReader(stream))
    assert len(source_rows) == 192
    groups = defaultdict(dict)
    max_reconstruction_error = Q(0)
    for row in source_rows:
        key = (row["Case"], row["Story"])
        assert row["Link"] not in groups[key]
        w, du = Q(row["Wtrap_native_kNm"]), Q(row["DeltaUs_conditional_kNm"])
        native_d = Q(row["Dport_conditional_kNm"])
        groups[key][row["Link"]] = dict(W=w, H=du/AHAT, P=Q(row["max_abs_native_P_kN"]), native_D=native_d)
        max_reconstruction_error = max(max_reconstruction_error, abs(w-du-native_d))
    assert len(groups) == 24 and all(len(v) == 8 for v in groups.values())
    assert {s for _, s in groups} == {"Story8", "Story9", "Story10", "Story11"}
    assert {c for c, _ in groups} == {"RH4X", "RH4Y", "SHW4X", "SHW4Y", "SHW7X", "SHW7Y"}
    intervals, pair_rows, events = [], [], []
    for (case, story), items in sorted(groups.items()):
        result = solve(items, AHAT)
        top, bottom = result["target"]
        wt, wb = pattern(items, Q(0))
        pt, _ = sets({j: x["P"] for j, x in items.items()})
        native = sets({j: x["native_D"] for j, x in items.items()})
        baseline_gate = native == result["target"]
        lo, hi = result["lower"], result["upper"]
        valid = baseline_gate and result["status"] == "maximal_open_interval"
        if valid: assert lo < AHAT and (hi is None or AHAT < hi)
        intervals.append(dict(Case=case, Story=story, status=result["status"] if baseline_gate else "summary_Dport_baseline_rank_mismatch", baseline_rank_gate=baseline_gate, a_hat=dec(AHAT), a_lower_open=dec(lo) if valid else "", a_upper_open="inf" if valid and hi is None else dec(hi) if valid else "", a_lower_exact=exact(lo) if valid else "", a_upper_exact="inf" if valid and hi is None else exact(hi) if valid else "", k_lower_open="0" if valid and hi is None else dec(1/hi) if valid else "", k_upper_open="inf" if valid and lo == 0 else dec(1/lo) if valid else "", top_hat=names(top), bottom_hat=names(bottom), unique_top2=len(top)==2, unique_bottom2=len(bottom)==2, top_W=names(wt), bottom_W=names(wb), W_top_same_as_hat=wt==top, W_bottom_same_as_hat=wb==bottom, W_both_sets_same_as_hat=(wt,wb)==(top,bottom), peak_force_top=names(pt), peak_top_differs_W=pt!=wt, peak_top_differs_hat=pt!=top, positive_distinct_roots=len(result["roots"])))
        for pair in result["pairs"]:
            pair_rows.append(dict(Case=case, Story=story, Link_i=pair["Link_i"], Link_j=pair["Link_j"], delta_W_exact=exact(pair["delta_W"]), delta_H_exact=exact(pair["delta_H"]), intersection_kind=pair["kind"], a_cross=dec(pair["root"]), a_cross_exact=exact(pair["root"])))
        if valid:
            for side, a in (("lower", lo), ("upper", hi)):
                if a is None:
                    events.append(dict(Case=case,Story=story,side=side,a_endpoint="inf",a_endpoint_exact="inf",endpoint_type="domain_infinity",top_endpoint="",bottom_endpoint="",sets_same_as_hat="",tied_pairs_json="[]")); continue
                ep = pattern(items, a)
                equal = [[i,j] for i,j in itertools.combinations(sorted(items),2) if items[i]["W"]-a*items[i]["H"] == items[j]["W"]-a*items[j]["H"]]
                events.append(dict(Case=case,Story=story,side=side,a_endpoint=dec(a),a_endpoint_exact=exact(a),endpoint_type="domain_zero_W" if a==0 else "finite_crossing",top_endpoint=names(ep[0]),bottom_endpoint=names(ep[1]),sets_same_as_hat=ep==result["target"],tied_pairs_json=json.dumps(equal,separators=(",",":"))))
    assert len(pair_rows) == 672
    assert sha(args.summary) == SOURCE_SHA and sha(protocol) == PROTOCOL_SHA
    csv_write(out/"intervals.csv",intervals);csv_write(out/"pair_crossings.csv",pair_rows)
    if events: csv_write(out/"endpoint_events.csv",events)
    counts=dict(groups=24,pair_records=672,valid_intervals=sum(x["status"]=="maximal_open_interval" for x in intervals),baseline_rank_gate_failures=sum(not x["baseline_rank_gate"] for x in intervals),W_both_sets_unchanged=sum(x["W_both_sets_same_as_hat"] for x in intervals),peak_top_mismatch_W=sum(x["peak_top_differs_W"] for x in intervals),peak_top_mismatch_hat=sum(x["peak_top_differs_hat"] for x in intervals),upper_unbounded=sum(x["a_upper_open"]=="inf" for x in intervals),lower_zero=sum(x["a_lower_open"]=="0" for x in intervals))
    record=dict(recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),status="candidate_fixed_summary_algebra_pending_R006_R011_and_derivation_audits",protocol_sha256=PROTOCOL_SHA,source_summary_sha256=SOURCE_SHA,script_sha256=sha(Path(__file__).resolve()),a_hat_exact=exact(AHAT),H_recovered_from_conditional_DeltaUs=True,raw_F_endpoints_not_read=True,full_histories_Excel_not_read=True,synthetic_checks=synthetic,summary_Dport_max_decimal_reconstruction_abs_error_kNm=dec(max_reconstruction_error),counts=counts)
    (out/"run_record.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(record,ensure_ascii=False))


if __name__ == "__main__":
    main()
