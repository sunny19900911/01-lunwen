"""One synthetic layout example; no model files or full-building node data."""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(a):
    return math.sqrt(dot(a, a))


def floor_motion(point, origin, translation, theta_z):
    r = sub(point, origin)
    return (translation[0] - theta_z * r[1], translation[1] + theta_z * r[0], translation[2])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    owner = Path(__file__).resolve().parent
    out = args.out.resolve()
    if not out.is_relative_to(owner):
        raise ValueError("Output must stay in owned role1 directory")
    out.mkdir(parents=True, exist_ok=False)
    z = (0.0, 0.0, 0.0)
    # I, J, floor origins, translations and rotations are explicit synthetic inputs.
    cases = [
        ("A_common_X_translation", (0, 0, 0), (4, 0, 3), z, (0, 0, 3), (1, 0, 0), (1, 0, 0), 0, 0, 0),
        ("B_upper_X_translation", (0, 0, 0), (4, 0, 3), z, (0, 0, 3), z, (0.01, 0, 0), 0, 0, 0.008),
        ("C_centerline_upper_torsion", (0, 0, 0), (4, 0, 3), z, (0, 0, 3), z, z, 0, 0.001, 0),
        ("D_offset_upper_torsion", (0, 3, 0), (4, 3, 3), z, (0, 0, 3), z, z, 0, 0.001, -0.0024),
        ("E_same_rigid_floor", (0, 3, 3), (4, 3, 3), (0, 0, 3), (0, 0, 3), z, z, 0.001, 0.001, 0),
    ]
    rows, records = [], []
    for name, i, j, oi, oj, ti, tj, ri, rj, expected in cases:
        chord = sub(j, i)
        length = norm(chord)
        axis = tuple(x / length for x in chord)
        ui = floor_motion(i, oi, ti, ri)
        uj = floor_motion(j, oj, tj, rj)
        du = sub(uj, ui)
        projection = dot(axis, du)
        assert abs(projection - expected) < 1e-14
        # Different calculation: directional derivative of Euclidean chord length.
        eps = 0.001
        plus = norm(tuple(x + eps * u for x, u in zip(chord, du)))
        minus = norm(tuple(x - eps * u for x, u in zip(chord, du)))
        finite_difference = (plus - minus) / (2 * eps)
        assert abs(finite_difference - projection) < 1e-9
        rows.append(dict(scenario=name, chord_length_m=length, nx=axis[0], ny=axis[1], nz=axis[2], dux_m=du[0], duy_m=du[1], duz_m=du[2], axial_first_order_m=projection, expected_m=expected, length_derivative_check_m=finite_difference))
        records.append(dict(scenario=name, I_xyz_m=i, J_xyz_m=j, I_floor_origin_m=oi, J_floor_origin_m=oj, I_translation_m=ti, J_translation_m=tj, I_theta_z_rad=ri, J_theta_z_rad=rj))
    # Exact rigid rotation preserves same-floor chord length, not just first order.
    angle = 0.001
    def rotate(point):
        x, y, height = point
        return (math.cos(angle) * x - math.sin(angle) * y, math.sin(angle) * x + math.cos(angle) * y, height)
    rigid_length_error = abs(norm(sub(rotate((4, 3, 3)), rotate((0, 3, 3)))) - 4)
    assert rigid_length_error < 1e-12
    with (out / "synthetic_layout.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = dict(recorded_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"), scope="synthetic first-order endpoint kinematics, not normalized modes or real model results", coordinates_and_translations="m", rotations="rad", cases=records, script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), max_projection_expected_error=max(abs(r["axial_first_order_m"] - r["expected_m"]) for r in rows), max_directional_derivative_error=max(abs(r["length_derivative_check_m"] - r["axial_first_order_m"]) for r in rows), exact_rigid_rotation_length_error_m=rigid_length_error, all_checks_passed=True)
    (out / "run_record.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(dict(out=str(out), rows=len(rows), max_directional_derivative_error=result["max_directional_derivative_error"], all_checks_passed=True)))


if __name__ == "__main__":
    main()
