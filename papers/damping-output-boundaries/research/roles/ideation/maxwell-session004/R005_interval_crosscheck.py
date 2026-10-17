"""Independent inequality-intersection check of the unique-cut real groups."""
import argparse
import csv
import hashlib
import json
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path

AHAT = Q("2.0006042528243313e-6")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--intervals", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    assert hashlib.sha256(args.summary.read_bytes()).hexdigest() == "8d359f9c86b544aaa6c573618a375eef7beb8f02070dc223f2802ce3fe31864d"
    groups = defaultdict(dict)
    with args.summary.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            groups[(row["Case"], row["Story"])][row["Link"]] = (Q(row["Wtrap_native_kNm"]), Q(row["DeltaUs_conditional_kNm"]) / AHAT)
    with args.intervals.open(encoding="utf-8", newline="") as stream:
        intervals = list(csv.DictReader(stream))
    checked = []
    for row in intervals:
        items = groups[(row["Case"], row["Story"])]
        top, bottom = set(row["top_hat"].split(";")), set(row["bottom_hat"].split(";"))
        assert len(top) == len(bottom) == 2
        constraints = []
        for selected, is_top in [(top, True), (bottom, False)]:
            for i in selected:
                for j in set(items) - selected:
                    w = items[i][0] - items[j][0]
                    h = items[i][1] - items[j][1]
                    if not is_top: w, h = -w, -h
                    assert w - AHAT * h > 0
                    constraints.append((w, h))
        lower, upper = Q(0), None
        for w, h in constraints:
            if h > 0: upper = w / h if upper is None else min(upper, w / h)
            elif h < 0: lower = max(lower, w / h)
            else: assert w > 0
        assert lower == Q(row["a_lower_exact"])
        assert (upper is None and row["a_upper_exact"] == "inf") or upper == Q(row["a_upper_exact"])
        def weak_order(a):
            scores = {j: w - a * h for j, (w, h) in items.items()}
            return [sorted(j for j, score in scores.items() if score == level)
                    for level in sorted(set(scores.values()), reverse=True)]
        w_order, hat_order = weak_order(Q(0)), weak_order(AHAT)
        checked.append(dict(Case=row["Case"], Story=row["Story"], matched_exact_bounds=True, strict_constraints=len(constraints), W_full_weak_order=w_order, hat_full_weak_order=hat_order, full_order_same=w_order==hat_order))
    assert len(checked) == 24
    output = args.out.resolve()
    assert output.is_relative_to(Path(__file__).resolve().parent)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(dict(passed=True, method="strict cross-boundary affine inequalities, independent of root-cell merging", full_W_vs_hat_order_same_count=sum(x["full_order_same"] for x in checked), groups=checked), stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(dict(passed=True, groups=len(checked))))


if __name__ == "__main__":
    main()
