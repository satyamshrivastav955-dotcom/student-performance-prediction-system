"""
Minimal pure-Python p-value functions, used only when SciPy is unavailable.

SciPy is listed in ``requirements.txt`` and is what runs in normal use. This
module exists for two reasons:

1. Slim deployment images (Render's free tier, for instance) sometimes ship
   without SciPy, and the statistics page should degrade gracefully rather than
   crash.
2. It gives the test suite a second, independent implementation to check SciPy's
   answers against — if the two ever disagree, something is wrong and we want to
   know.

The algorithms are the standard ones from *Numerical Recipes*: a series
expansion and a continued fraction for the regularised incomplete gamma
function, and Lentz's continued fraction for the regularised incomplete beta
function. Every survival function we need reduces to one of those two.

Accuracy is ~1e-12 relative, which is far tighter than anything a p-value in a
student-performance study needs.
"""

from __future__ import annotations

import math
from typing import Tuple

_EPS = 3.0e-16
_FPMIN = 1.0e-300
_MAX_ITER = 400


# -----------------------------------------------------------------------------
# Regularised incomplete gamma  ->  chi-square p-values
# -----------------------------------------------------------------------------

def _gser(a: float, x: float) -> float:
    """Lower regularised incomplete gamma P(a, x) via its series expansion.

    Converges quickly when x < a + 1.
    """
    ap = a
    total = 1.0 / a
    delta = total
    for _ in range(_MAX_ITER):
        ap += 1.0
        delta *= x / ap
        total += delta
        if abs(delta) < abs(total) * _EPS:
            break
    return total * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gcf(a: float, x: float) -> float:
    """Upper regularised incomplete gamma Q(a, x) via a continued fraction.

    Converges quickly when x >= a + 1, i.e. exactly where the series does not.
    """
    b = x + 1.0 - a
    c = 1.0 / _FPMIN
    d = 1.0 / b
    h = d
    for i in range(1, _MAX_ITER + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < _FPMIN:
            d = _FPMIN
        c = b + an / c
        if abs(c) < _FPMIN:
            c = _FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def gammainc_upper(a: float, x: float) -> float:
    """Q(a, x) — the upper regularised incomplete gamma function."""
    if x < 0 or a <= 0:
        raise ValueError("gammainc_upper requires a > 0 and x >= 0")
    if x == 0:
        return 1.0
    if x < a + 1.0:
        return 1.0 - _gser(a, x)
    return _gcf(a, x)


def chi2_sf(x: float, df: int) -> float:
    """Chi-square survival function: P(X > x) for X ~ chi2(df).

    Sanity anchor: ``chi2_sf(3.8415, 1)`` is 0.05 to four decimals — the
    critical value every statistics textbook prints.
    """
    if df <= 0:
        raise ValueError("Degrees of freedom must be positive")
    if x <= 0:
        return 1.0
    return float(gammainc_upper(df / 2.0, x / 2.0))


# -----------------------------------------------------------------------------
# Regularised incomplete beta  ->  F and t p-values
# -----------------------------------------------------------------------------

def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta function (Lentz's method)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < _FPMIN:
        d = _FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, _MAX_ITER + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < _FPMIN:
            d = _FPMIN
        c = 1.0 + aa / c
        if abs(c) < _FPMIN:
            c = _FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < _FPMIN:
            d = _FPMIN
        c = 1.0 + aa / c
        if abs(c) < _FPMIN:
            c = _FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            break
    return h


def betainc(a: float, b: float, x: float) -> float:
    """I_x(a, b) — the regularised incomplete beta function."""
    if x < 0.0 or x > 1.0:
        raise ValueError("betainc requires 0 <= x <= 1")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0
    front = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log(1.0 - x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def f_sf(f: float, dfn: int, dfd: int) -> float:
    """F-distribution survival function: P(F > f).

    Used for the ANOVA and Levene p-values.
    Sanity anchor: ``f_sf(3.0088, 2, 100)`` is 0.05 to three decimals.
    """
    if f <= 0:
        return 1.0
    x = dfd / (dfd + dfn * f)
    return float(betainc(dfd / 2.0, dfn / 2.0, x))


def t_sf_two_sided(t: float, df: float) -> float:
    """Two-sided p-value for a t statistic. Used for correlation significance."""
    if df <= 0:
        return float("nan")
    x = df / (df + t * t)
    return float(betainc(df / 2.0, 0.5, x))


# -----------------------------------------------------------------------------
# Exact binomial — used by McNemar's test on small discordant counts
# -----------------------------------------------------------------------------

def binom_test_two_sided(k: int, n: int, p: float = 0.5) -> float:
    """Exact two-sided binomial test.

    For p = 0.5 the distribution is symmetric, so the two-sided p-value is
    simply twice the smaller tail (capped at 1.0). This is what McNemar's exact
    test needs, and it is the correct choice when the number of discordant
    predictions is small — the chi-square approximation is unreliable below
    roughly 25 discordant pairs, and our test set has only 96 students.
    """
    if n == 0:
        return 1.0
    k = int(k)
    n = int(n)
    if p == 0.5:
        tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / (2.0 ** n)
        return float(min(1.0, 2.0 * tail))
    # General case: sum all outcomes no more likely than the observed one.
    def pmf(i: int) -> float:
        return math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    observed = pmf(k)
    return float(min(1.0, sum(pmf(i) for i in range(n + 1) if pmf(i) <= observed * (1 + 1e-9))))


# -----------------------------------------------------------------------------
# Rank helper — needed by Kruskal-Wallis and Spearman
# -----------------------------------------------------------------------------

def rankdata_average(values) -> Tuple[list, float]:
    """Rank values 1..n, averaging ranks within ties.

    Also returns the tie-correction factor ``1 - sum(t^3 - t) / (n^3 - n)`` that
    Kruskal-Wallis needs to stay valid when the data contain repeated values —
    and engagement counters have plenty of repeats.
    """
    vals = list(values)
    n = len(vals)
    order = sorted(range(n), key=lambda i: vals[i])
    ranks = [0.0] * n
    tie_sum = 0.0
    i = 0
    while i < n:
        j = i
        while j + 1 < n and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        span = j - i + 1
        if span > 1:
            tie_sum += span ** 3 - span
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    correction = 1.0 - tie_sum / (n ** 3 - n) if n > 1 and (n ** 3 - n) != 0 else 1.0
    return ranks, correction
