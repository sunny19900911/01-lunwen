"""Audit existing CSI energy caches; never run the solver or overwrite results."""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import numpy as np


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cache, out):
    out.mkdir(parents=True, exist_ok=False)
    manifest_path = cache / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["complete"] and manifest["source_unchanged"]
    total = manifest["tables"]["Total Energy Components"]
    grouped = manifest["tables"]["Element NL Energy By Group"]
    columns = {name: i for i, name in enumerate(total["columns"])}
    group_columns = {name: i for i, name in enumerate(grouped["columns"])}
    groups_by_case = {}
    for key, meta in grouped["groups"].items():
        case = meta["keys"]["Output Case"]
        assert meta["keys"]["Group"] == "All" and case not in groups_by_case
        groups_by_case[case] = key
    rows, details = [], []
    total_path, group_path = cache / total["cache"], cache / grouped["cache"]
    with np.load(total_path, allow_pickle=False) as energies, np.load(group_path, allow_pickle=False) as device_energies:
        for key, meta in total["groups"].items():
            case = meta["keys"]["Output Case"]
            a = energies[key]
            b = device_energies[groups_by_case[case]]
            assert np.isfinite(a).all() and np.isfinite(b).all()
            t = a[:, columns["Time"]]
            assert np.all(np.diff(t) > 0) and len(t) == meta["n"]
            assert np.array_equal(t, b[:, group_columns["Time"]])
            values = {name: a[:, columns[name]] for name in columns}
            ein = values["Input Energy"]
            kinetic, potential = values["Kinetic Energy"], values["Potential Energy"]
            global_damping, link = values["Global Damping Energy"], values["Link Damper Energy"]
            hysteresis, error = values["Link Hysteresis Energy"], values["Energy Error"]
            residual = ein - kinetic - potential - global_damping - link - hysteresis
            scale = max(float(np.max(np.abs(ein))), np.finfo(float).tiny)
            all_link = b[:, group_columns["Internal Viscous Damping"]] + b[:, group_columns["Support Viscous Damping"]]
            eg, ed = float(global_damping[-1] - global_damping[0]), float(link[-1] - link[0])
            assert eg > 0
            row = {"case": case, "T_s": float(t[-1]), "Eglobal_increment_kNm": eg,
                   "Elink_increment_kNm": ed, "ratio_Elink_over_Eglobal": ed / eg,
                   "conditional_added_damping_at_5pct": .05 * ed / eg,
                   "background_setting_verified": False,
                   "max_balance_residual_over_max_input": float(np.max(np.abs(residual))) / scale,
                   "residual_minus_reported_error_over_input": float(np.max(np.abs(residual - error))) / scale,
                   "residual_plus_reported_error_over_input": float(np.max(np.abs(residual + error))) / scale,
                   "max_All_vs_total_link_diff_kNm": float(np.max(np.abs(all_link - link))),
                   "end_kinetic_plus_potential_over_input_scale": float(kinetic[-1] + potential[-1]) / scale,
                   "source_row_final": int(a[-1, columns["SourceRow"]])}
            rows.append(row)
            windows = []
            for fraction in [.25, .5, .75, 1.0]:
                i = int(np.searchsorted(t, t[0] + fraction * (t[-1] - t[0])))
                denominator = float(global_damping[i] - global_damping[0])
                windows.append({"fraction": fraction, "actual_T_s": float(t[i]),
                                "ratio": float((link[i] - link[0]) / denominator) if denominator > 0 else None})
            details.append({"case": case, "time_grid": {"n": len(t), "t0": float(t[0]), "t1": float(t[-1])},
                            "quarter_windows": windows,
                            "min_energy_increments": {"global": float(np.min(np.diff(global_damping))), "link": float(np.min(np.diff(link)))},
                            "initial_energies_kNm": {name: float(values[name][0]) for name in total["columns"] if name.endswith("Energy")}})
    with (out / "energy_summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report = {"recorded_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
              "source_sha256": manifest["sha256"], "source_bytes": manifest["bytes"],
              "input_files": [{"path": str(p.resolve()), "sha256": digest(p)} for p in [manifest_path, total_path, group_path]],
              "script_sha256": digest(Path(__file__)), "cases": details,
              "limitations": ["5% is an explicit reference, not verified actual background damping", "energy windows stop at exported end; not certified full free tail", "single controlled state; no claimed reduction against another model", "group All is total energy; incomplete individual devices must not replace it"]}
    (out / "run_record.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cache", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    run(args.cache, args.out)
