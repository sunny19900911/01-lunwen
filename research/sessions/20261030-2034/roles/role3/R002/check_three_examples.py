"""Three scalar harmonic checks only; no model, time integration, or scan."""
from pathlib import Path
import math
import json

def main():
    rows = []
    for beta in (0.5, 1.0, 2.0):
        a = (1.0 - beta * beta) ** 2
        ratio = math.sqrt((a + (0.1 * beta) ** 2) /
                          (a + (0.16 * beta) ** 2))
        old_phase = -math.degrees(math.atan2(0.1 * beta, 1.0 - beta * beta))
        new_phase = -math.degrees(math.atan2(0.16 * beta, 1.0 - beta * beta))
        assert 0.625 - 1e-14 <= ratio <= 1.0 + 1e-14
        rows.append({"beta": beta, "amplitude_ratio_8pct_to_5pct": ratio,
                     "amplitude_reduction_percent": 100.0 * (1.0 - ratio),
                     "flexibility_phase_5pct_degrees": old_phase,
                     "flexibility_phase_8pct_degrees": new_phase,
                     "phase_change_degrees": new_phase - old_phase})
    assert abs(rows[1]["amplitude_ratio_8pct_to_5pct"] - 0.625) < 1e-14
    assert rows[1]["phase_change_degrees"] == 0.0
    assert abs(rows[0]["amplitude_ratio_8pct_to_5pct"] -
               rows[2]["amplitude_ratio_8pct_to_5pct"]) < 1e-14
    result = {"identity": "three scalar arithmetic illustrations; analytic proof separate",
              "phase_convention": "e^(i*Omega*t), displacement flexibility relative to generalized harmonic force",
              "zeta_old": 0.05, "zeta_new": 0.08, "example_count": 3, "rows": rows}
    out = Path(__file__).resolve().parent / "three-examples.json"
    with out.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
