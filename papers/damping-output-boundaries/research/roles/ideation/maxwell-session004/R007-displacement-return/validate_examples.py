"""Analytic alpha=1 endpoint examples, not a parameter sweep or real model."""
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path


def simpson(function, end, n=2000):
    h = end / n
    return h / 3 * (function(0) + function(end)
        + 4 * sum(function(i * h) for i in range(1, n, 2))
        + 2 * sum(function(i * h) for i in range(2, n, 2)))


def main():
    k = c = v = 1.0
    peak = 0.5
    up, down = -math.log1p(-peak), math.log1p(peak)
    tau = up + down
    lower = math.log((1 + peak) / (1 - peak)) - 2 * peak
    residual = v * (up - down)
    up_force = lambda t: 1 - math.exp(-t)
    down_force = lambda t: (1 + peak) * math.exp(-t) - 1
    integral_force = simpson(up_force, up) + simpson(down_force, down)
    integral_dissipation = simpson(lambda t: up_force(t)**2, up) + simpson(lambda t: down_force(t)**2, down)
    assert abs(integral_force-residual) < 1e-12
    assert abs(integral_dissipation-lower) < 1e-12
    # A mirrored negative lobe uses negative F and negative velocity.
    double_residual = integral_force + simpson(lambda t: -up_force(t), up) + simpson(lambda t: -down_force(t), down)
    assert abs(double_residual) < 1e-12
    period = 2 * math.pi
    omega = 2 * math.pi / period
    speed_max = peak * math.sqrt((omega/k)**2 + 1/c**2)
    sine_dissipation = peak**2 * period / (2*c)
    force = lambda t: peak * math.sin(omega*t)
    displacement = lambda t: force(t)/k + peak/(c*omega)*(1-math.cos(omega*t))
    sine_quad = simpson(lambda t: force(t)**2/c, period)
    assert abs(displacement(period)-displacement(0)) < 1e-12
    assert abs(sine_quad-sine_dissipation) < 1e-12 and speed_max < v
    report = dict(checked_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"), all_checks_passed=True, units=dict(force="kN", length="m", time="s"), synthetic_parameters=dict(k_kN_per_m=k,c_kN_s_per_m=c,V_m_per_s=v,M_kN=peak,alpha=1), single_positive_lobe=dict(tau_s=tau, residual_displacement_m=residual, L_kNm=lower, numerical_integral_g=integral_force,numerical_integral_D=integral_dissipation), mirrored_double_lobe=dict(total_time_s=2*tau,D_kNm=2*lower,delta_residual_m=double_residual), continuous_sine=dict(T_s=period,maximum_speed_m_per_s=speed_max,D_kNm=sine_dissipation,delta_residual_m=displacement(period)-displacement(0),endpoint_speed_m_per_s=peak*omega/k), script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), scope="one analytic endpoint example; no new exact closed-state feasible set, no real data or sweep")
    path = Path(__file__).with_name("example_validation.json")
    with path.open("x",encoding="utf-8",newline="\n") as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2);stream.write("\n")
    print(json.dumps(report,ensure_ascii=False))


if __name__ == "__main__": main()
