"""Independent scalar-table audit only. Never opens trace arrays or runs fitting."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import csv
import json
import math
import hashlib

OUT = Path(__file__).resolve().parent
SESSION = OUT.parents[2]

def fp(path):
    data = path.read_bytes()
    return dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())

def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def main():
    accounting = SESSION / "roles/role4/R005/native-peak-accounting-all12-36.csv"
    native = SESSION / "roles/role4/R003/native-all12-peak-change-36.csv"
    roof = SESSION / "roles/role1/R002/native-peak-ledger-3.csv"
    result_source = SESSION / "roles/role4/R005/results.json"
    src = [fp(x) for x in (accounting, native, roof, result_source)]
    a, b, c = rows(accounting), rows(native), rows(roof)
    key = lambda x: (x["Case"], x["Story"])
    table = {key(x): x for x in a}
    originals = {key(x): x for x in b}
    expected = {(case, f"Story{i}") for case in ("SHW3X", "SHW4X", "RH4X") for i in range(1, 13)}
    assert len(a) == len(b) == 36 and set(table) == set(originals) == expected
    maxima = {}
    def check(name, actual, wanted, tol=1e-9):
        assert math.isfinite(actual) and math.isfinite(wanted)
        delta = abs(actual - wanted)
        maxima[name] = max(maxima.get(name, 0.0), delta)
        assert delta <= tol, (name, actual, wanted, delta)
    def boolean(value):
        assert value in ("True", "False")
        return value == "True"
    totals = dict(M_zero=0, time_unchanged=0, old_anchor_abspeak=0,
                  old_anchor_signed_peak=0, sign_changed=0, positive_M=0)
    sign_changes = []
    computed = {}
    min_m = math.inf
    all_unique_ties = True
    for item in a:
        k = key(item); ref = originals[k]
        get = lambda n: float(item[n])
        p5, p8 = get("P5_kN"), get("P8_kN")
        t0, t8 = get("t0_5pct_abspeak_s"), get("t8_8pct_abspeak_s")
        old, cross, new = get("V5_t0_kN"), get("V8_t0_kN"), get("V8_t8_kN")
        s0, s8 = (1 if old > 0 else -1), (1 if new > 0 else -1)
        assert p5 > 0 and p8 > 0 and old != 0 and new != 0
        check("s0", get("s0"), s0, 0); check("s8", get("s8"), s8, 0)
        check("old_anchor_abs", abs(old), p5); check("new_anchor_abs", abs(new), p8)
        assert abs(cross) <= p8 + 1e-9 and abs(get("V5_t8_kN")) <= p5 + 1e-9
        # Different arrangement from producer: P5 - s0*cross, not s0*(old-cross).
        d = p5 - s0 * cross
        m = abs(new) - s0 * cross
        net = abs(old) - abs(new)
        assert m >= 0
        min_m = min(min_m, m)
        check("D_kN", get("D_same_time_signed_decrease_kN"), d)
        check("M_kN", get("M_peak_reselection_correction_kN"), m)
        check("net_kN", get("net_peak_decrease_kN"), net)
        check("identity_kN", d - m, net)
        check("stored_identity_error", get("identity_error_kN"), net - (d - m))
        check("time_shift_s", get("peak_time_shift_s"), t8 - t0, 1e-12)
        for name, value in (("D", d), ("M", m), ("net_decrease", net)):
            fraction_name = "net_decrease_over_P5" if name == "net_decrease" else name + "_over_P5"
            percent_name = "net_peak_decrease_percent" if name == "net_decrease" else name + "_percent_P5"
            check(fraction_name, get(fraction_name), value / p5, 1e-12)
            check(percent_name, get(percent_name), 100 * value / p5, 1e-10)
        mappings = {"peak5_kN": p5, "peak8_kN": p8, "peak5_time_s": t0,
                    "peak8_time_s": t8, "V8_at_5peak_kN": cross,
                    "V5_at_8peak_kN": get("V5_t8_kN"),
                    "native_peak_decrease_percent": 100 * net / p5}
        for field, value in mappings.items():
            check("R003_" + field, value, float(ref[field]), 1e-9)
        for left, right in (("native_SourceRow5", "source_row5"), ("native_SourceRow8", "source_row8")):
            assert int(item[left]) == int(ref[right])
        tol = 1e-9 * max(1.0, p8)  # Reported producer classification tolerance.
        zero = m <= tol
        same_time = abs(t8 - t0) <= 1e-12
        abs_peak = abs(abs(cross) - p8) <= tol
        signed_peak = abs(s0 * cross - p8) <= tol
        flip = s0 != s8
        expected_flags = {"time_argmax_changed": not same_time,
                          "old_anchor_still_8pct_abspeak": abs_peak,
                          "old_anchor_still_8pct_signed_control": signed_peak,
                          "M_zero_within_tolerance": zero, "control_sign_changed": flip}
        for name, flag in expected_flags.items(): assert boolean(item[name]) == flag, (k, name)
        totals["M_zero"] += zero; totals["positive_M"] += not zero
        totals["time_unchanged"] += same_time
        totals["old_anchor_abspeak"] += abs_peak; totals["old_anchor_signed_peak"] += signed_peak
        totals["sign_changed"] += flip
        if flip: sign_changes.append(dict(Case=k[0], Story=k[1], s0=s0, s8=s8))
        all_unique_ties &= int(item["abspeak5_exact_tie_count"]) == int(item["abspeak8_exact_tie_count"]) == 1
        computed[k] = dict(Case=k[0], Story=k[1], P5_kN=p5, P8_kN=p8, t0_s=t0, t8_s=t8,
                           s0=s0, s8=s8, V8_t0_kN=cross, D_kN=d, M_kN=m, net_kN=net,
                           D_percent=100*d/p5, M_percent=100*m/p5, net_percent=100*net/p5)
    assert totals == dict(M_zero=16, time_unchanged=16, old_anchor_abspeak=16,
                          old_anchor_signed_peak=16, sign_changed=3, positive_M=20)
    # Cross-check all three roof rows from role1's independently frozen ledger.
    roof_fields = {"P5_native_kN": "P5_kN", "P8_native_kN": "P8_kN",
                   "D_old_peak_suppression_kN": "D_kN", "M_controlling_peak_transfer_gap_kN": "M_kN",
                   "P5_minus_P8_kN": "net_kN", "D_minus_M_kN": "net_kN",
                   "D_over_P5_percent": "D_percent", "M_over_P5_percent": "M_percent",
                   "native_peak_reduction_percent": "net_percent"}
    assert len(c) == 3
    for row in c:
        calc = computed[key(row)]
        for field, target in roof_fields.items(): check("role1_" + field, float(row[field]), calc[target], 1e-9)
        check("role1_signed_cross", float(row["s0_V8_at_t0_kN"]), calc["s0"]*calc["V8_t0_kN"])
    original_result = json.loads(result_source.read_text(encoding="utf-8"))
    assert original_result["source_native_table"]["sha256"] == fp(native)["sha256"]
    selected = [computed[k] for k in (("RH4X", "Story1"), ("RH4X", "Story2"), ("SHW4X", "Story12"))]
    for item in selected:
        if item["s0"] != item["s8"]:
            item["wrong_M_if_s8_used_kN"] = item["P8_kN"] - item["s8"]*item["V8_t0_kN"]
    assert [fp(Path(x["path"])) for x in src] == src
    result = dict(task="20261030-2034 role3 R003", completed_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
                  verdict="PASS scalar-table and algebraic audit; raw extrema not re-extracted",
                  rows_checked=36, roof_ledger_rows_checked=3, counts=totals,
                  minimum_M_kN=min_m, all_tie_counts_in_supplied_table_equal_one=all_unique_ties,
                  sign_changed_records=sign_changes, maximum_absolute_differences=maxima,
                  selected_examples=selected, sources=src,
                  arrays_or_fits_read_or_run=False,
                  unverified_scope="No raw-array rerun of global max, tie multiplicity, grid identity or signed-anchor extraction")
    with (OUT / "scalar-checks.json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2); handle.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__": main()
