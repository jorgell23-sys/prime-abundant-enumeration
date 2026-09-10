# -*- coding: utf-8 -*-
"""Enumerate S(f) = { n : rad(n) | f(n) } without sieving.

Standard library only. No numpy, no sympy, no imports outside Python itself.

WHY IT WORKS
------------
n is in S(f) exactly when, in the covering digraph D_f(n) -- vertices are the
primes of n, with an arrow q -> p when p divides f(q^{v_q(n)}) -- every vertex
has an incoming arrow.

Two consequences make the search finite:

1. NO PRIME OF n IS FREE.  If p divides n then, by the condition itself, some
   q | n has p | f(q^{v_q(n)}).  So every prime of n shows up when factoring a
   value of f, and factoring is cheap.

2. EVERY VERTEX IS REACHABLE FROM A CYCLE.  A finite digraph whose in-degrees
   are all >= 1 contains a directed cycle, and walking backwards from any
   vertex reaches one.

So n is built by choosing directed cycles and adding descendants, pruning by
product <= X.  Nothing that does not belong is ever touched.

THE BOUND THAT KEEPS IT CHEAP
-----------------------------
If q^a divides n <= X, then every other prime of n is <= X/q^a.  So we do not
need all prime divisors of f(q^a), only those up to that bound -- and the two
quantities move in opposite directions, so one of the two routes is always
cheap: factor a small value, or sweep primes up to a small bound evaluating
f(q^a) mod p without ever building f(q^a).

COMPLETENESS
------------
Every intermediate step of the construction is already in S(f): adding a vertex
that is covered by what is already there cannot uncover anyone, because the
exponents of the vertices present do not change.  And every n in S(f) admits
that order of construction: first its simple cycles, then its descendants in
order of reachability.
"""

from math import isqrt

# ---------------------------------------------------------------------------
# Deterministic Miller-Rabin and Pollard rho.  Self-contained on purpose.
# ---------------------------------------------------------------------------
_SMALL = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n):
    if n < 2:
        return False
    for p in _SMALL:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in _SMALL:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _rho(n, seed=1):
    if n % 2 == 0:
        return 2
    c = seed
    while True:
        x = y = 2
        d = 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = _gcd(abs(x - y), n)
        if d != n:
            return d
        c += 1


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def factor(n):
    """{prime: exponent} of n >= 1."""
    out = {}
    for p in _SMALL:
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
    if n == 1:
        return out
    stack = [n]
    while stack:
        m = stack.pop()
        if m == 1:
            continue
        if is_prime(m):
            out[m] = out.get(m, 0) + 1
            continue
        d = _rho(m)
        stack.append(d)
        stack.append(m // d)
    return out


# ---------------------------------------------------------------------------
# The functions.  Each carries `residue(p, q, e)` = f(q^e) mod p, computed
# without building f(q^e).
# ---------------------------------------------------------------------------
class Function(object):
    """A multiplicative f, given by its value on prime powers."""

    def __init__(self, name, value, residue, coeffs=None):
        self.name = name
        self.value = value
        self.residue = residue
        self.coeffs = coeffs

    def __call__(self, q, e):
        return self.value(q, e)

    def is_local(self, primes=(2, 3, 5, 7, 11, 13), max_exp=6):
        """p does not divide f(p^a): without this the digraph is undefined."""
        for p in primes:
            for a in range(1, max_exp + 1):
                if self.value(p, a) % p == 0:
                    return False
        return True


def polynomial(coeffs):
    """f(q^e) = |F(q^e)|, coefficients from highest to lowest degree.

    The absolute value is not a patch: p | f(q^e) does not depend on the sign,
    and some local F go negative on small arguments (x^2-2x-1 is -1 at q=2).
    A ZERO value would break the object -- every prime would divide it -- so it
    is rejected rather than absorbed.
    """
    def value(q, e):
        x = q ** e
        r = 0
        for c in coeffs:
            r = r * x + c
        if r == 0:
            raise ValueError("F(%d^%d) = 0: the covering digraph is undefined"
                             % (q, e))
        return -r if r < 0 else r

    def residue(p, q, e):
        x = pow(q, e, p)
        r = 0
        for c in coeffs:
            r = (r * x + c) % p
        return r

    return Function("F=%s" % (list(coeffs),), value, residue, list(coeffs))


def sigma_s(s=1):
    """sigma_s(q^e) = 1 + q^s + ... + q^{se}.  Not polynomial in q^e."""
    def value(q, e):
        return (q ** (s * (e + 1)) - 1) // (q ** s - 1)

    def residue(p, q, e):
        b = pow(q, s, p)
        acc, pot = 0, 1
        for _ in range(e + 1):
            acc = (acc + pot) % p
            pot = pot * b % p
        return acc

    return Function("sigma_%d" % s, value, residue)


SIGMA = sigma_s(1)
SIGMA_STAR = polynomial([1, 1])      # q^e + 1
PHI_STAR = polynomial([1, -1])       # q^e - 1


# ---------------------------------------------------------------------------
# Small primes, sieved once.
# ---------------------------------------------------------------------------
_CACHE = {"limit": 0, "primes": []}


def primes_up_to(limit):
    if limit <= _CACHE["limit"]:
        ps = _CACHE["primes"]
        hi = len(ps)
        lo = 0
        while lo < hi:                       # bisect, without importing it
            mid = (lo + hi) // 2
            if ps[mid] <= limit:
                lo = mid + 1
            else:
                hi = mid
        return ps[:lo]
    n = max(limit, 1000)
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, isqrt(n) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, n + 1, i)))
    _CACHE["limit"] = n
    _CACHE["primes"] = [i for i in range(2, n + 1) if sieve[i]]
    return primes_up_to(limit)


# ---------------------------------------------------------------------------
# Outgoing arrows of one vertex.
# ---------------------------------------------------------------------------
BUDGET = 3 * 10 ** 7


class EffortExceeded(RuntimeError):
    """Neither factoring the value nor sweeping to the bound fits the budget."""


def outgoing(f, q, a, X, memo):
    """Primes p <= X/q^a with p | f(q^a).

    The bound is not a heuristic prune: if q^a | n and n <= X, every other
    prime of n divides n/q^a <= X/q^a.  A larger p cannot occur in any element
    containing q^a, so nothing is lost.
    """
    key = (q, a)
    hit = memo.get(key)
    if hit is not None:
        return hit
    bound = X // (q ** a)
    if bound < 2:
        memo[key] = ()
        return ()

    v = f(q, a)
    digits = len(str(v))
    cost_factor = 10.0 ** (digits / 4.0)      # Pollard rho, worst case
    cost_sweep = bound / max(2.0, _ln(bound))  # pi(bound)

    if cost_sweep < cost_factor:
        if cost_sweep > BUDGET:
            raise EffortExceeded("f(%d^%d) has %d digits, bound %d"
                                 % (q, a, digits, bound))
        res = tuple(p for p in primes_up_to(int(bound))
                    if f.residue(p, q, a) == 0)
    else:
        if cost_factor > BUDGET:
            raise EffortExceeded("f(%d^%d) has %d digits, bound %d"
                                 % (q, a, digits, bound))
        res = tuple(sorted(p for p in factor(v) if p <= bound))
    memo[key] = res
    return res


def _ln(x):
    """Natural log without importing math.log for a single call."""
    from math import log
    return log(x)


def product(conf):
    n = 1
    for p, a in conf.items():
        n *= p ** a
    return n


def covered(f, conf):
    """The criterion, recomputed from scratch on {prime: exponent}."""
    for p in conf:
        if not any(q != p and f(q, a) % p == 0 for q, a in conf.items()):
            return False
    return True


# ---------------------------------------------------------------------------
# Step 1 -- the simple directed cycles with product <= X.
# ---------------------------------------------------------------------------
def cycles(f, X, memo=None):
    """Every simple cycle p1 -> ... -> pk -> p1 with product <= X.

    Enumerated BY THEIR SMALLEST VERTEX: m runs over primes up to sqrt(X) and
    the rest of the chain only accepts larger primes, so each cycle appears
    once and rotations need no deduplication.
    """
    memo = memo if memo is not None else {}
    out = []
    for m in primes_up_to(isqrt(X)):
        a = 1
        while m ** a * m <= X:      # at least one more prime is needed, and > m
            _extend(f, X, m, {m: a}, m, a, out, memo)
            a += 1
    return out


def _extend(f, X, m, conf, last, last_exp, out, memo):
    part = product(conf)
    for r in outgoing(f, last, last_exp, X, memo):
        if r == m and len(conf) >= 2:
            out.append(dict(conf))
            continue
        if r <= m or r in conf:
            continue
        c = 1
        while part * r ** c <= X:
            conf[r] = c
            _extend(f, X, m, conf, r, c, out, memo)
            del conf[r]
            c += 1


# ---------------------------------------------------------------------------
# Step 2 -- close up: merge compatible cycles and add descendants.
# ---------------------------------------------------------------------------
def configurations(f, X, memo=None):
    """{n: {prime: exponent}} for every n in S(f) with 1 < n <= X."""
    memo = memo if memo is not None else {}
    seeds = cycles(f, X, memo)

    seen = {}
    stack = []
    for c in seeds:
        key = frozenset(c.items())
        if key not in seen:
            seen[key] = c
            stack.append(c)

    while stack:
        conf = stack.pop()
        part = product(conf)

        # a cycle can be merged if it agrees on the exponents of shared primes
        for c in seeds:
            if all(conf.get(p, a) == a for p, a in c.items()):
                new = dict(conf)
                new.update(c)
                _keep(new, X, seen, stack)

        targets = set()
        for q, a in conf.items():
            targets.update(outgoing(f, q, a, X, memo))
        for r in targets:
            if r in conf:
                continue
            c = 1
            while part * r ** c <= X:
                new = dict(conf)
                new[r] = c
                _keep(new, X, seen, stack)
                c += 1

    return dict((product(c), c) for c in seen.values())


def _keep(conf, X, seen, stack):
    if product(conf) > X:
        return
    key = frozenset(conf.items())
    if key in seen:
        return
    seen[key] = conf
    stack.append(conf)


def elements(f, X, memo=None):
    """Sorted list of every n in S(f) with 1 < n <= X."""
    return sorted(configurations(f, X, memo))


# ---------------------------------------------------------------------------
# The independent check: brute force, for the range where it is affordable.
# ---------------------------------------------------------------------------
def brute_force(f, X):
    """Every n <= X with rad(n) | f(n), by trying every integer.

    This is the check, not the method.  It knows nothing about digraphs: it
    factors n, multiplies out rad(n) and f(n), and divides.
    """
    out = []
    for n in range(2, X + 1):
        fac = factor(n)
        rad, fn = 1, 1
        for p, a in fac.items():
            rad *= p
            fn *= f(p, a)
        if fn % rad == 0:
            out.append(n)
    return out


def belongs(f, n):
    """rad(n) | f(n), computed from scratch for a single n."""
    fac = factor(n)
    rad, fn = 1, 1
    for p, a in fac.items():
        rad *= p
        fn *= f(p, a)
    return fn % rad == 0
