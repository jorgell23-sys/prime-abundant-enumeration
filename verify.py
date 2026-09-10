#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check everything in this repository.  No dependencies, seconds to run.

    python verify.py

Prints PASS or FAIL per check and exits 1 if anything fails.

The point of this file is that you do not have to take anyone's word for it.
Two of the checks are EXTERNAL: they compare against numbers published by other
people -- the DATA field of OEIS A175200, and the two counts stated in Pollack
and Pomerance, INTEGERS 12A (2012).  A file that only checks itself proves
nothing.
"""

import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))

import enumerate_sf as E          # noqa: E402

PASSED = 0
FAILED = 0


def check(name, ok, detail=""):
    global PASSED, FAILED
    if ok:
        PASSED += 1
        print("PASS  %s" % name)
    else:
        FAILED += 1
        print("FAIL  %s   %s" % (name, detail))


def read_terms(path):
    out = []
    with open(os.path.join(HERE, "data", path)) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(int(line))
    return out


def bisect_right(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x < a[mid]:
            hi = mid
        else:
            lo = mid + 1
    return lo


# ---------------------------------------------------------------------------
print("=" * 68)
print("1. The enumerator returns the same SET as brute force")
print("=" * 68)
print("Not the same size: the same set.  An enumerator that loses one element")
print("and gains another counts the same and is wrong.\n")

X = 20000
FUNCS = [
    ("sigma", E.SIGMA),
    ("sigma* = q^e+1", E.SIGMA_STAR),
    ("phi* = q^e-1", E.PHI_STAR),
    ("Phi3 = x^2+x+1", E.polynomial([1, 1, 1])),
    ("Phi6 = x^2-x+1", E.polynomial([1, -1, 1])),
    ("sigma_2", E.sigma_s(2)),
]
for name, f in FUNCS:
    mine = E.elements(f, X)
    brute = E.brute_force(f, X)
    check("enumerator == brute force up to %d for %s (%d elements)"
          % (X, name, len(mine)), mine == brute,
          "missing %s extra %s" % (sorted(set(brute) - set(mine))[:3],
                                   sorted(set(mine) - set(brute))[:3]))

# a control on the control: if the criterion is broken, this MUST notice
broken = E.polynomial([1, 0])          # f(q^e) = q^e, not local
check("negative control: a non-local f is rejected", not broken.is_local())
check("positive control: sigma* is local", E.SIGMA_STAR.is_local())


# ---------------------------------------------------------------------------
print("\n" + "=" * 68)
print("2. EXTERNAL CHECK -- the DATA field of OEIS A175200")
print("=" * 68)
print("49 terms up to 4320, catalogued in 2010 by Michel Lagneau.\n")

oeis = read_terms("oeis_A175200_data_field.txt")
ours = [1] + E.elements(E.SIGMA, oeis[-1])
check("our terms up to %d equal the %d published in A175200"
      % (oeis[-1], len(oeis)), ours == oeis,
      "ours=%s oeis=%s" % (ours[:6], oeis[:6]))


# ---------------------------------------------------------------------------
print("\n" + "=" * 68)
print("3. EXTERNAL CHECK -- the two counts published by Pollack and Pomerance")
print("=" * 68)
print('INTEGERS 12A (2012), paper A14, section 1: "up to 10^9, there are 198')
print('prime-perfect numbers and 5328 prime-abundant numbers."\n')

counts = json.load(open(os.path.join(HERE, "data", "counts.json")))
pa = read_terms("prime_abundant_1e13.txt")
pp = read_terms("prime_perfect_1e13.txt")

n_pa = 1 + bisect_right(pa, 10 ** 9)      # the file omits n = 1; they count it
n_pp = bisect_right(pp, 10 ** 9)
check("prime-abundant up to 10^9 == 5328 (published)", n_pa == 5328,
      "got %d" % n_pa)
check("prime-perfect up to 10^9 == 198 (published)", n_pp == 198,
      "got %d" % n_pp)
check("counts.json agrees with the term files",
      counts["by_decade"]["1e9"]["prime_abundant"] == n_pa
      and counts["by_decade"]["1e9"]["prime_perfect"] == n_pp)


# ---------------------------------------------------------------------------
print("\n" + "=" * 68)
print("4. Every published term really belongs")
print("=" * 68)
print("n is factored from scratch and rad(n) | f(n) is checked as integers,")
print("without using the configuration it was built from.\n")

random.seed(20260910)
for label, path, f in (("prime-abundant", "prime_abundant_1e13.txt", E.SIGMA),
                       ("sigma*", "sigma_star_1e13.txt", E.SIGMA_STAR),
                       ("phi*", "phi_star_1e13.txt", E.PHI_STAR)):
    terms = read_terms(path)
    sample = terms[:50] + random.sample(terms, 150) + terms[-25:]
    bad = [n for n in sample if not E.belongs(f, n)]
    check("%d sampled %s terms all belong (largest %d)"
          % (len(sample), label, max(sample)), not bad, "bad: %s" % bad[:3])

# and the negative control: a term that does NOT belong must be caught
check("negative control: 12 is not prime-abundant", not E.belongs(E.SIGMA, 12))
check("negative control: 7 is not in S(sigma*)", not E.belongs(E.SIGMA_STAR, 7))


# ---------------------------------------------------------------------------
print("\n" + "=" * 68)
print("5. Prime-perfect really means rad(n) = rad(sigma(n))")
print("=" * 68 + "\n")


def rad(n):
    r = 1
    for p in E.factor(n):
        r *= p
    return r


def sigma_of(n):
    s = 1
    for p, a in E.factor(n).items():
        s *= (p ** (a + 1) - 1) // (p - 1)
    return s


sample = pp[:40] + random.sample(pp, 60)
bad = [n for n in sample if n > 1 and rad(n) != rad(sigma_of(n))]
check("%d sampled prime-perfect terms satisfy rad(n) = rad(sigma(n))"
      % len(sample), not bad, "bad: %s" % bad[:3])
check("every prime-perfect term is also prime-abundant",
      all(n == 1 or n in set(pa) for n in sample))
# the six even perfect numbers below 10^10 must be there
perfect = [6, 28, 496, 8128, 33550336, 8589869056]
check("the six even perfect numbers below 10^10 are prime-perfect",
      all(n in set(pp) for n in perfect))


# ---------------------------------------------------------------------------
print("\n" + "=" * 68)
print("6. Theorem: infinitude, with an O(1) certificate")
print("=" * 68)
print("If nu is in S(f) and some prime r not dividing nu divides f(q^a) for a")
print("prime power q^a of nu, then nu*r^c is in S(f) for every c >= 1.\n")

for name, f in FUNCS[:5]:
    conf = E.configurations(f, 200000)
    found = None
    for n in sorted(conf):
        c = conf[n]
        for q, a in c.items():
            for r in E.factor(f(q, a)):
                if r not in c:
                    found = (n, q, a, r)
                    break
            if found:
                break
        if found:
            break
    if not found:
        check("certificate of infinitude for %s" % name, False, "none found")
        continue
    n, q, a, r = found
    # the certificate is only worth what its consequence is worth: check it
    ok = all(E.belongs(f, n * r ** c) for c in (1, 2, 3))
    check("%s: %d, %d | f(%d^%d) -> %d*%d^c in S(f) for c = 1,2,3"
          % (name, n, r, q, a, n, r), ok)


# ---------------------------------------------------------------------------
print("\n" + "=" * 68)
print("7. Theorem: two-prime elements are counted without searching")
print("=" * 68)
print("q | sigma(p^a) iff m | a+1, with m = ord_q(p) if that order is > 1,")
print("and m = q if q divides p-1.  A lattice under a hyperbola.\n")


def order(a, m):
    a %= m
    if a == 0:
        return 0
    o, x = 1, a
    while x != 1:
        x = x * a % m
        o += 1
    return o


def step(p, q):
    d = order(p, q)
    return None if d == 0 else (q if d == 1 else d)


def predict(p, q, X):
    mp, mq = step(p, q), step(q, p)
    if mp is None or mq is None:
        return set()
    out = set()
    a = mp - 1
    while p ** a * q <= X:
        b = mq - 1
        while p ** a * q ** b <= X:
            if a >= 1 and b >= 1:
                out.add(p ** a * q ** b)
            b += mq
        a += mp
    return out


LIM = 10 ** 6
conf = E.configurations(E.SIGMA, LIM)
two = {}
for n, c in conf.items():
    if len(c) == 2:
        two.setdefault(tuple(sorted(c)), set()).add(n)

wrong = []
for (p, q), real in two.items():
    if predict(p, q, LIM) != real:
        wrong.append((p, q))
check("the formula reproduces every two-prime element up to %d (%d pairs, "
      "%d elements)" % (LIM, len(two), sum(len(s) for s in two.values())),
      not wrong, "wrong pairs: %s" % wrong[:3])

# negative control: it must not invent elements for pairs that have none
invented = 0
small = E.primes_up_to(120)
for i, p in enumerate(small):
    for q in small[i + 1:]:
        if (p, q) not in two and predict(p, q, LIM):
            invented += 1
check("the formula invents nothing for the pairs with no elements",
      invented == 0, "invented for %d pairs" % invented)


# ---------------------------------------------------------------------------
print("\n" + "=" * 68)
print("8. The claims made in the README about the data")
print("=" * 68 + "\n")

check("prime_abundant_1e13.txt has 85695 terms and none exceeds 10^13",
      len(pa) == 85695 and pa[-1] <= 10 ** 13, "%d terms" % len(pa))
check("prime_perfect_1e13.txt has 1212 terms", len(pp) == 1212,
      "%d terms" % len(pp))
check("the published b-file stops at 7271402112, and we pass it",
      bisect_right(pa, 7271402112) + 1 == 10000 and pa[-1] > 7271402112,
      "%d up to the b-file limit" % (bisect_right(pa, 7271402112) + 1))
check("all term files are strictly increasing",
      all(a < b for a, b in zip(pa, pa[1:]))
      and all(a < b for a, b in zip(pp, pp[1:])))

byf = json.load(open(os.path.join(HERE, "data", "counts_by_function.json")))
check("counts_by_function.json covers 30 local functions",
      len(byf["functions"]) == 30, "%d" % len(byf["functions"]))
check("20 of them were not used to form the hypotheses",
      sum(1 for v in byf["functions"].values()
          if v["group"] == "fuera_de_muestra") == 20)


# ---------------------------------------------------------------------------
print("\n" + "=" * 68)
print("9. The numbers printed on the explanation pages")
print("=" * 68)
print("Every figure quoted in docs/ carries data-fact and is recomputed here.")
print("Without this the explanation ages in silence while the data moves on.\n")

import re                                                    # noqa: E402

facts = {
    "bfile_terms": 10000,
    "bfile_last": 7271402112,
    "pa_1e9": n_pa,
    "pp_1e9": n_pp,
    "terms_1e13": len(pa),
    "smallest_phi6": byf["functions"]["Phi6 = x^2-x+1"]["smallest"],
    "functions": len(byf["functions"]),
}

for page in ("docs/index.html", os.path.join("docs", "es", "index.html")):
    path = os.path.join(HERE, page)
    if not os.path.exists(path):
        check("%s exists" % page, False)
        continue
    html = open(path, encoding="utf-8").read()
    found = re.findall(r'data-fact="([a-z_0-9]+)"[^>]*>([^<]+)<', html)
    check("%s marks at least 4 numbers with data-fact (%d)"
          % (page, len(found)), len(found) >= 4)
    wrong = []
    for name, text in found:
        # both pages are checked, and they use different thousands separators
        shown = text.strip().replace(",", "").replace(".", "")
        shown = shown.replace(" ", "").replace(" ", "")
        if name not in facts:
            wrong.append("%s: unknown fact" % name)
        elif not shown.isdigit() or int(shown) != facts[name]:
            wrong.append("%s: page says %r, data says %d"
                         % (name, text.strip(), facts[name]))
    check("%s: every data-fact matches the recomputed data" % page,
          not wrong, "; ".join(wrong[:3]))

# and the control on the control: a fact that does not match must be caught
fake = '<span data-fact="terms_1e13">12345</span>'
m = re.findall(r'data-fact="([a-z_0-9]+)"[^>]*>([^<]+)<', fake)[0]
check("negative control: a wrong figure on the page would be caught",
      int(m[1]) != facts["terms_1e13"])


# ---------------------------------------------------------------------------
print("\n" + "=" * 68)
print("%d passed, %d failed" % (PASSED, FAILED))
print("=" * 68)
sys.exit(1 if FAILED else 0)
