"""Author first calculation of frozen I-M001; no Y/I-M002/solver calls."""
import argparse
import csv
import hashlib
import itertools
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

CASES = ("RH4X", "SHW4X", "SHW7X")
WINDOWS = ((10, 20), (20, 30), (30, 40), (40, 50))
PROTOCOL_SHA = "cfe32266bf3bdaef16709594fda40acef8024af26c179ec189bc5512303d1833"
MANIFEST_SHA = "03cae034bd5409c6dc6bed06727a58fd85391a6f583a2b38776cf03bf45f26f4"
ENERGY_SHA = "3614b98aa57bb52ba7e18ceaac98f221ebcf6f15d13777b0ead7be268d857b4e"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def write_csv(path, rows):
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    owner = Path(__file__).resolve().parent
    output = args.out.resolve()
    if not output.is_relative_to(owner):
        raise ValueError("Output must stay in role1 owned directory")
    output.mkdir(parents=True, exist_ok=False)
    protocol = owner / "R001-energy-force-candidates.md"
    cache = args.cache.resolve()
    inputs = [protocol, cache / "manifest.json", cache / "Total_Energy_Components.npz", cache / "Story_Forces.npz"]
    initial_hashes = {str(p): sha(p) for p in inputs}
    assert initial_hashes[str(protocol)] == PROTOCOL_SHA, "Frozen protocol changed"
    assert initial_hashes[str(inputs[1])] == MANIFEST_SHA, "Cache manifest changed"
    assert initial_hashes[str(inputs[2])] == ENERGY_SHA, "Energy input changed"
    manifest = json.loads(inputs[1].read_text(encoding="utf-8-sig"))
    assert manifest["complete"] is True and manifest["source_unchanged"] is True
    tables = manifest["tables"]
    force_meta, energy_meta = tables["Story Forces"], tables["Total Energy Components"]
    assert set(force_meta["step_types"]) == {"Step By Step"}
    assert set(energy_meta["step_types"]) == {"Step By Step"}
    for meta, field, unit in ((force_meta, "VX", "kN"), (energy_meta, "Global Damping Energy", "kN-m"), (energy_meta, "Link Damper Energy", "kN-m")):
        assert meta["units"][meta["headers"].index(field)] == unit
    force_npz = np.load(inputs[3], allow_pickle=False)
    energy_npz = np.load(inputs[2], allow_pickle=False)

    def group(meta, archive, keys):
        matches = [(name, data) for name, data in meta["groups"].items() if data["keys"] == keys]
        assert len(matches) == 1, f"Nonunique group: {keys}"
        name, description = matches[0]
        array = archive[name]
        assert array.ndim == 2 and array.shape == (description["n"], len(meta["columns"]))
        assert np.isfinite(array).all(), "Nonfinite values"
        time = array[:, meta["columns"].index("Time")]
        assert np.all(np.diff(time) > 0), "Duplicate/nonincreasing time"
        assert time[0] == 0 and time[-1] >= 50, "Coverage missing"
        array = array[time <= 50]
        time = array[:, meta["columns"].index("Time")]
        assert len(time) == 2501 and time[-1] == 50, "Common window coverage"
        grid_error = float(np.max(np.abs(time - np.arange(2501) * 0.02)))
        assert grid_error <= 1e-12, "Irregular 0.02-second grid"
        source_rows = array[:, meta["columns"].index("SourceRow")]
        assert np.all(source_rows == np.floor(source_rows)) and np.all(source_rows >= 4)
        return array, time, name, grid_error

    def col(array, meta, name):
        return array[:, meta["columns"].index(name)]

    window_rows, pair_rows, case_checks = [], [], []
    for case in CASES:
        gate_errors, case_windows = [], []
        diagnostic = {"case": case, "semantic_scope": "exported signed VX difference of adjacent Bottom cuts; physical composition/sign convention not independently certified"}
        try:
            base_key = {"Output Case": case, "Case Type": "NonModHist"}
            e, te, ge, ee = group(energy_meta, energy_npz, base_key)
            s1a, t1, g1, e1 = group(force_meta, force_npz, {"Story": "Story1", "Location": "Bottom", **base_key})
            s2a, t2, g2, e2 = group(force_meta, force_npz, {"Story": "Story2", "Location": "Bottom", **base_key})
            assert np.array_equal(te, t1) and np.array_equal(te, t2), "Exact time alignment failed"
            s1, s2 = col(s1a, force_meta, "VX"), col(s2a, force_meta, "VX")
            eg, el = col(e, energy_meta, "Global Damping Energy"), col(e, energy_meta, "Link Damper Energy")
            net, force_activity = s1 - s2, np.abs(s1) + np.abs(s2)
            total_eg, total_el = float(eg[-1] - eg[0]), float(el[-1] - el[0])
            max_activity = float(np.max(force_activity))
            if total_eg <= 0 or total_el <= 0:
                gate_errors.append("nonpositive_full_window_energy_increment")
            diagnostic.update(groups={"energy": ge, "Story1": g1, "Story2": g2}, n=2501, exact_cross_table_time_match=True, max_grid_float_error=max(ee, e1, e2), total_delta_EG_kNm=total_eg, total_delta_EL_kNm=total_el, max_force_activity_kN=max_activity, min_sample_delta_EG_kNm=float(np.min(np.diff(eg))), min_sample_delta_EL_kNm=float(np.min(np.diff(el))), negative_EG_increment_count=int(np.count_nonzero(np.diff(eg) < 0)), negative_EL_increment_count=int(np.count_nonzero(np.diff(el) < 0)), negative_increments_clipped=False)
        except (AssertionError, ValueError, KeyError) as exc:
            gate_errors.append("data_gate: " + str(exc))
        diagnostic["case_gate_errors"] = gate_errors.copy()
        case_checks.append(diagnostic)
        for start, end in WINDOWS:
            row = dict(case=case, window=f"{start}-{end}", start_s=start, end_s=end, delta_EG_kNm=None, delta_EL_kNm=None, R=None, EG_fraction_of_0_50=None, EL_fraction_of_0_50=None, tN_s=None, S1_VX_kN=None, S2_VX_kN=None, N_kN=None, D_kN=None, max_D_0_50_kN=None, D_fraction=None, eta=None, EL_at_tN_kNm=None, EG_at_tN_kNm=None, S1_VX_cell=None, S2_VX_cell=None, energy_at_tN_cells=None, EG_endpoint_cells=None, EL_endpoint_cells=None, energy_gate=False, force_gate=False, eligible=False, exclusion_reasons="")
            reasons = gate_errors.copy()
            if not gate_errors:
                a, b = np.flatnonzero(te == start), np.flatnonzero(te == end)
                assert len(a) == len(b) == 1
                ia, ib = int(a[0]), int(b[0])
                # Closed intervals, first exact maximum, no independent-peak subtraction.
                ip = ia + int(np.argmax(np.abs(net[ia:ib + 1])))
                dg, dl = float(eg[ib] - eg[ia]), float(el[ib] - el[ia])
                d = float(force_activity[ip])
                eg_gate = dg > 0 and dg >= 0.01 * total_eg
                el_gate = dl > 0 and dl >= 0.01 * total_el
                f_gate = d > 0 and d >= 0.05 * max_activity
                if not eg_gate: reasons.append("EG_increment_nonpositive_or_below_1pct")
                if not el_gate: reasons.append("EL_increment_nonpositive_or_below_1pct")
                if not f_gate: reasons.append("force_activity_nonpositive_or_below_5pct")
                erows = col(e, energy_meta, "SourceRow").astype(int)
                r1, r2 = int(col(s1a, force_meta, "SourceRow")[ip]), int(col(s2a, force_meta, "SourceRow")[ip])
                eta = float(abs(net[ip]) / d) if d > 0 else None
                if eta is not None: assert 0 <= eta <= 1 + 1e-15
                row.update(delta_EG_kNm=dg, delta_EL_kNm=dl, R=dl/dg if dg > 0 else None, EG_fraction_of_0_50=dg/total_eg, EL_fraction_of_0_50=dl/total_el, tN_s=float(te[ip]), S1_VX_kN=float(s1[ip]), S2_VX_kN=float(s2[ip]), N_kN=float(net[ip]), D_kN=d, max_D_0_50_kN=max_activity, D_fraction=d/max_activity if max_activity > 0 else None, eta=eta, EL_at_tN_kNm=float(el[ip]), EG_at_tN_kNm=float(eg[ip]), S1_VX_cell=f"Story Forces!H{r1}", S2_VX_cell=f"Story Forces!H{r2}", energy_at_tN_cells=f"Total Energy Components!H{erows[ip]}:I{erows[ip]}", EG_endpoint_cells=f"H{erows[ia]},H{erows[ib]}", EL_endpoint_cells=f"I{erows[ia]},I{erows[ib]}", energy_gate=eg_gate and el_gate, force_gate=f_gate, eligible=eg_gate and el_gate and f_gate)
            row["exclusion_reasons"] = ";".join(reasons)
            case_windows.append(row)
            window_rows.append(row)
        for u, v in itertools.combinations(case_windows, 2):
            eligible = u["eligible"] and v["eligible"]
            delta_r = 2 * abs(u["R"] - v["R"]) / (u["R"] + v["R"]) if eligible else None
            delta_eta = abs(u["eta"] - v["eta"]) if eligible else None
            matched = eligible and delta_r <= 0.05
            witness = matched and delta_eta >= 0.20
            reason = "" if witness else ("ineligible_window: " + ";".join(filter(None, [u["exclusion_reasons"], v["exclusion_reasons"]])) if not eligible else "R_not_matched_5pct" if not matched else "eta_gap_below_0.20")
            pair_rows.append(dict(case=case, window_u=u["window"], window_v=v["window"], eligible=eligible, R_u=u["R"], R_v=v["R"], eta_u=u["eta"], eta_v=v["eta"], delta_R_relative=delta_r, delta_eta=delta_eta, energy_matched=matched, witness=witness, failure_reason=reason))
    assert len(window_rows) == 12 and len(pair_rows) == 18
    assert all(sha(p) == initial_hashes[str(p)] for p in inputs), "Inputs changed during calculation"
    matches = sum(p["energy_matched"] for p in pair_rows)
    witnesses = sum(p["witness"] for p in pair_rows)
    verdict = "supported_candidate" if witnesses else "not_supported_under_frozen_protocol" if matches else "not_testable_no_eligible_match"
    write_csv(output / "windows.csv", window_rows)
    write_csv(output / "pairs.csv", pair_rows)
    write_json(output / "run_record.json", dict(recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"), status="author_first_calculation_candidate_pending_role2_review", verdict=verdict, window_count=12, pair_count=18, eligible_window_count=sum(w["eligible"] for w in window_rows), eligible_pair_count=sum(p["eligible"] for p in pair_rows), energy_matched_pair_count=matches, witness_count=witnesses, cases=case_checks, protocol_sha256=PROTOCOL_SHA, script_sha256=sha(Path(__file__).resolve()), input_files=[dict(path=str(p), sha256=initial_hashes[str(p)], bytes=p.stat().st_size) for p in inputs], source_workbook_sha256_from_manifest=manifest["sha256"], original_workbook_rehashed_this_run=False, source_unchanged_during_calculation=True, package_numpy=np.__version__, fixed_parameters=dict(cases=CASES, common_window=[0,50], windows=WINDOWS, energy_fraction_gate=0.01, force_activity_gate=0.05, relative_R_tolerance=0.05, absolute_eta_gap=0.20), no_Y_or_IM002=True, physical_force_budget_certified=False))
    print(json.dumps(dict(out=str(output), verdict=verdict, eligible_windows=sum(w["eligible"] for w in window_rows), matched_pairs=matches, witnesses=witnesses), ensure_ascii=False))


if __name__ == "__main__":
    main()
