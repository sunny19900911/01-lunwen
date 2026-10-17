"""Small fail-closed outward binary64 helpers for a candidate residual audit.

Basic operations widen with nextafter; sqrt/cbrt candidates are verified by
exact Fraction powers. This module alone is not an ODE or peak certificate.
Version v002 rejects non-integer root degrees; v001 and its API counterexample remain preserved.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import cbrt, factorial, inf, isfinite, nextafter, sqrt
import sys

# The basic-operation proof contract is round-to-nearest IEEE binary64.
# This does not rely on libm sin/pow/root having directed rounding.
assert (sys.float_info.radix, sys.float_info.mant_dig,
        sys.float_info.max_exp, sys.float_info.rounds) == (2, 53, 1024, 1)


def down(x):
    if not isfinite(x):
        raise ArithmeticError('Nonfinite interval operation')
    return nextafter(x, -inf)


def up(x):
    if not isfinite(x):
        raise ArithmeticError('Nonfinite interval operation')
    return nextafter(x, inf)


@dataclass(frozen=True)
class I:
    lo: float
    hi: float

    def __post_init__(self):
        if not (isfinite(self.lo) and isfinite(self.hi) and self.lo <= self.hi):
            raise ArithmeticError('Invalid finite interval')

    @staticmethod
    def point(x):
        x = float(x)
        return I(x, x)

    @staticmethod
    def rational(q):
        q = Fraction(q)
        x = float(q)
        if not isfinite(x):
            raise ArithmeticError('Rational outside finite binary64 range')
        fx = Fraction(x)
        return I(nextafter(x, -inf) if fx > q else x,
                 nextafter(x, inf) if fx < q else x)

    def __add__(self, other):
        other = interval(other)
        return I(down(self.lo + other.lo), up(self.hi + other.hi))

    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + (-interval(other))

    def __rsub__(self, other):
        return interval(other) - self

    def __mul__(self, other):
        other = interval(other)
        corners = [a * b for a in (self.lo, self.hi)
                   for b in (other.lo, other.hi)]
        return I(down(min(corners)), up(max(corners)))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = interval(other)
        if other.lo <= 0 <= other.hi:
            raise ZeroDivisionError('Interval denominator contains zero')
        return self * I(down(1 / other.hi), up(1 / other.lo))

    def __rtruediv__(self, other):
        return interval(other) / self

    def __pow__(self, n):
        if not isinstance(n, int) or n < 0:
            raise TypeError('Only nonnegative integer interval powers')
        result = I.point(1)
        base = self
        while n:
            if n & 1:
                result = result * base
            base = base * base
            n //= 2
        return result

    def abs_upper(self):
        return max(abs(self.lo), abs(self.hi))


def interval(x):
    return x if isinstance(x, I) else I.point(x)


def root_endpoint(x, degree):
    """Enclose a nonnegative FLOAT endpoint root, without trusting libm error."""
    if type(degree) is not int:
        raise TypeError('Root degree must be a built-in int')
    if x < 0 or degree not in (2, 3):
        raise ValueError('Nonnegative square/cube root endpoints only')
    if x == 0:
        return I.point(0)
    q = Fraction(x)
    guess = sqrt(x) if degree == 2 else cbrt(x)
    for _ in range(32):
        power = Fraction(guess) ** degree
        if power == q:
            return I.point(guess)
        if power > q:
            lower = nextafter(guess, -inf)
            if lower < 0:
                raise ArithmeticError('Negative candidate root lower endpoint')
            if Fraction(lower) ** degree <= q:
                return I(lower, guess)
            guess = lower
        else:
            higher = nextafter(guess, inf)
            if Fraction(higher) ** degree >= q:
                return I(guess, higher)
            guess = higher
    raise ArithmeticError('Root candidate failed exact endpoint certification')


def root(x, degree):
    if type(degree) is not int:
        raise TypeError('Root degree must be a built-in int')
    if degree not in (2, 3):
        raise ValueError('Only square/cube root degrees supported')
    x = interval(x)
    if x.lo < 0:
        raise ValueError('Root requires an established nonnegative interval')
    return I(root_endpoint(x.lo, degree).lo, root_endpoint(x.hi, degree).hi)


def atan_reciprocal_bounds(denominator, terms=100):
    """Exact alternating arctan(1/d) sum and next-term enclosure, d>=2."""
    if denominator < 2 or terms < 1:
        raise ValueError('Convergent alternating reciprocal arctangent required')
    total = sum((Fraction((-1) ** j, (2*j + 1) * denominator ** (2*j + 1))
                 for j in range(terms)), Fraction(0))
    other = total + Fraction((-1) ** terms,
                             (2*terms + 1) * denominator ** (2*terms + 1))
    return min(total, other), max(total, other)


_a5 = atan_reciprocal_bounds(5)
_a239 = atan_reciprocal_bounds(239)
PI_RATIONAL_BOUNDS = (16*_a5[0] - 4*_a239[1],
                      16*_a5[1] - 4*_a239[0])
# Machin identity: tan(4 atan(1/5))=120/119 and subtracting atan(1/239)
# gives tangent 1 in the first quadrant. Hence pi=16 atan(1/5)-4 atan(1/239).
PI = I(I.rational(PI_RATIONAL_BOUNDS[0]).lo,
       I.rational(PI_RATIONAL_BOUNDS[1]).hi)
assert Fraction(3) < PI_RATIONAL_BOUNDS[0] < PI_RATIONAL_BOUNDS[1] < Fraction(4)

_SIN_COEFFICIENTS = [I.rational(Fraction((-1) ** j, factorial(2*j + 1)))
                     for j in range(13)]
_SIN_REMAINDER = I.rational(Fraction(2 ** 27, factorial(27))).hi


def sin_pi_ratio(numerator, denominator):
    """Enclose sin(pi*n/d), integer range reduction plus Taylor remainder."""
    if denominator <= 0:
        raise ValueError('Positive denominator required')
    n = numerator % (2 * denominator)
    if n > denominator:
        n -= 2 * denominator
    if 2*n > denominator:
        n = denominator - n
    elif 2*n < -denominator:
        n = -denominator - n
    assert 2 * abs(n) <= denominator
    x = PI * I.rational(Fraction(n, denominator))
    z = x * x
    p = _SIN_COEFFICIENTS[-1]
    for coefficient in reversed(_SIN_COEFFICIENTS[:-1]):
        p = p * z + coefficient
    result = x * p
    return result + I(-_SIN_REMAINDER, _SIN_REMAINDER)


def signed_power_10_3_endpoint(x):
    if x == 0:
        return I.point(0)
    a = I.point(abs(x))
    result = (a ** 3) * root(a, 3)
    return result if x > 0 else -result


def g_power_10_3(force, c):
    c = interval(c)
    if c.lo <= 0:
        raise ValueError('Strictly positive c required')
    x = interval(force) / c
    # The signed power is increasing on the entire real line.
    return I(signed_power_10_3_endpoint(x.lo).lo,
             signed_power_10_3_endpoint(x.hi).hi)


def g_derivative_upper(max_abs_force, c):
    c = interval(c)
    if max_abs_force < 0 or c.lo <= 0:
        raise ValueError('Known nonnegative force magnitude and positive c')
    if max_abs_force == 0:
        return 0.
    x = I.point(max_abs_force) / c
    # Intersect with independently known nonnegativity of |F|/c.
    x = I(max(0., x.lo), max(0., x.hi))
    return ((I.rational(Fraction(10, 3)) / c) * (x ** 2) * root(x, 3)).hi


def selfcheck():
    """Finite exact-rational regression checks, not a general machine proof."""
    import random
    randomizer = random.Random(20261018)
    checks = 0
    for _ in range(100):
        a, b = [randomizer.uniform(-10, 10) for _ in range(2)]
        qa, qb = Fraction(a), Fraction(b)
        for out, exact in [(I.point(a)+b, qa+qb), (I.point(a)-b, qa-qb),
                           (I.point(a)*b, qa*qb), (I.point(a)/b, qa/qb)]:
            assert Fraction(out.lo) <= exact <= Fraction(out.hi)
            checks += 1
    for x in [0., 1e-200, 1e-20, .1, .5, 1., 2., 10.]:
        for degree in (2, 3):
            out = root_endpoint(x, degree)
            assert Fraction(out.lo)**degree <= Fraction(x) <= Fraction(out.hi)**degree
            checks += 1
    for f in [-1.7, -.88, -.1, -1e-9, 0., 1e-9, .1, .88, 1.7]:
        c = 1.45
        out = g_power_10_3(I.point(f), I.point(c))
        exact_cube = (1 if f >= 0 else -1) * abs(Fraction(f)/Fraction(c))**10
        assert Fraction(out.lo)**3 <= exact_cube <= Fraction(out.hi)**3
        upper = g_derivative_upper(abs(f), I.point(c))
        exact_derivative_cube = (Fraction(10, 3)/Fraction(c))**3 * abs(Fraction(f)/Fraction(c))**7
        assert Fraction(upper)**3 >= exact_derivative_cube
        checks += 2
    for n, d, exact in [(0, 1, 0), (1, 2, 1), (-1, 2, -1), (1, 1, 0),
                         (1, 6, Fraction(1, 2)), (-1, 6, -Fraction(1, 2)),
                         (5, 6, Fraction(1, 2)), (7, 6, -Fraction(1, 2))]:
        out = sin_pi_ratio(n, d)
        assert Fraction(out.lo) <= exact <= Fraction(out.hi)
        checks += 1
    try:
        I.point(1) / I(-1, 1)
    except ZeroDivisionError:
        checks += 1
    else:
        raise AssertionError('Zero denominator did not fail closed')
    for bad_degree in [2.0, 3.0, Fraction(2, 1), '2', True]:
        for function, argument in [(root_endpoint, .1), (root, I.point(.1))]:
            try:
                function(argument, bad_degree)
            except TypeError:
                checks += 1
            else:
                raise AssertionError('Non-integer root degree was accepted')
    return {'passed': True, 'exact_rational_regression_checks': checks,
            'pi_float_interval': [PI.lo, PI.hi],
            'basic_operation_contract': 'round-to-nearest IEEE binary64; finite arithmetic, nextafter widening; unsupported/nonfinite operations fail closed',
            'scope': 'Helper regression only; endpoint powers and Taylor/alternating bounds explicit. Not an ODE residual implementation or a continuous/fulltail peak certificate.'}


if __name__ == '__main__':
    import json
    print(json.dumps(selfcheck(), ensure_ascii=False))
