"""Readonly source execution; exact rational challenges, not ODE certification."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json
import math
import runpy

HERE = Path(__file__).resolve().parent
freeze = json.loads((HERE / "input-freeze.json").read_text(encoding="utf-8"))
source = Path(freeze["inputs"][0]["path"])
assert hashlib.sha256(source.read_bytes()).hexdigest() == freeze["inputs"][0]["sha256"]
ns = runpy.run_path(str(source), run_name="immutable_helper_review")
I = ns["I"]
counts = {"basic_exact_checks": 0, "safe_rejections": 0, "root_exact_checks": 0,
          "rational_conversion_checks": 0, "nonlinear_exact_checks": 0, "sine_known_value_checks": 0}
tiny = math.nextafter(0., math.inf)
values = [0., -0., tiny, -tiny, 1e-300, -1e-300, .1, -.1, 1., -1.,
          math.nextafter(1., math.inf), 1e155, -1e155, 1e300]
for a in values:
    for b in values:
        for operation in ("add", "sub", "mul", "div"):
            if operation == "div" and b == 0:
                continue
            qa, qb = Q(a), Q(b)
            exact = {"add": lambda: qa+qb, "sub": lambda: qa-qb,
                     "mul": lambda: qa*qb, "div": lambda: qa/qb}[operation]()
            try:
                out = {"add": lambda: I.point(a)+I.point(b), "sub": lambda: I.point(a)-I.point(b),
                       "mul": lambda: I.point(a)*I.point(b), "div": lambda: I.point(a)/I.point(b)}[operation]()
            except (ArithmeticError, OverflowError, ValueError):
                counts["safe_rejections"] += 1
                continue
            assert Q(out.lo) <= exact <= Q(out.hi)
            counts["basic_exact_checks"] += 1
for value in [Q(0), Q(1,10), -Q(1,3), Q(2**53+1), Q(tiny)/3, Q(tiny)*Q(3,2), Q(1,10**400)]:
    out = I.rational(value)
    assert Q(out.lo) <= value <= Q(out.hi)
    counts["rational_conversion_checks"] += 1
for x in [0., tiny, 1e-300, 1e-200, .1, 1., 2., 1e155, 1e300]:
    for degree in (2,3):
        out = ns["root_endpoint"](x, degree)
        assert Q(out.lo)**degree <= Q(x) <= Q(out.hi)**degree
        counts["root_exact_checks"] += 1
for f in [-1.7,-tiny,0.,tiny,.88,1.7]:
    for c in [1.4,1.45,1.5]:
        out = ns["g_power_10_3"](I.point(f),I.point(c))
        ratio = Q(f)/Q(c)
        cube = (1 if ratio >= 0 else -1)*abs(ratio)**10
        assert Q(out.lo)**3 <= cube <= Q(out.hi)**3
        derivative_upper = ns["g_derivative_upper"](abs(f),I.point(c))
        derivative_cube = (Q(10,3)/Q(c))**3 * abs(ratio)**7
        assert Q(derivative_upper)**3 >= derivative_cube
        counts["nonlinear_exact_checks"] += 2
for n,d,exact in [(0,1,Q(0)),(1,2,Q(1)),(-1,2,Q(-1)),(1,6,Q(1,2)),
                  (5,6,Q(1,2)),(7,6,-Q(1,2)),(-7,6,Q(1,2)),(1,1,Q(0))]:
    for periods in [0,10**200,-10**200]:
        out = ns["sin_pi_ratio"](n+2*d*periods,d)
        assert Q(out.lo) <= exact <= Q(out.hi)
        counts["sine_known_value_checks"] += 1
for den in [I(-1.,1.),I.point(0.),I(-tiny,0.)]:
    try:
        I.point(1.)/den
    except ZeroDivisionError:
        counts["safe_rejections"] += 1
    else:
        raise AssertionError("zero-containing denominator accepted")
bad = ns["root_endpoint"](.1,2.0)
bad_contains = Q(bad.lo)**2 <= Q(.1) <= Q(bad.hi)**2
assert not bad_contains
point_rational = I.point(Q(1,10))
point_contains = Q(point_rational.lo) <= Q(1,10) <= Q(point_rational.hi)
assert not point_contains
limitations = {}
for label, call in [("unneeded_pow_square",lambda:I.point(1e155)**1),
                    ("reciprocal_overflow_finite_quotient",lambda:I.point(tiny)/I.point(tiny))]:
    try:
        call()
    except ArithmeticError as exc:
        limitations[label] = type(exc).__name__
    else:
        limitations[label] = "returned"
result = {"source_sha256":freeze["inputs"][0]["sha256"],"original_selfcheck":ns["selfcheck"](),
          "counts":counts,"mustfix":{"call":"root_endpoint(0.1, 2.0)","returned":[bad.lo,bad.hi],
          "exact_contains":bad_contains,"exact_endpoint_square":str(Q(bad.lo)**2),"exact_input":str(Q(.1)),
          "reason":"floating degree makes Fraction ** degree a floating operation; equality branch falsely certifies point",
          "recommended_new_version":"require type(degree) is int and degree in (2,3), or explicitly canonicalize a validated degree to int"},
          "usage_boundary":{"I.point(Fraction(1,10))_contains_original_rational":point_contains,
                            "contract":"point denotes converted binary64 point; exact rationals must use I.rational"},
          "safe_availability_limitations":limitations,
          "scope":"Finite regression only; no ODE, residual accumulation, full-time peak proof or source edits."}
(HERE/"challenge-results.json").write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
print(json.dumps(result,ensure_ascii=False,indent=2))
