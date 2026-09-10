# Enumerating `S(f) = { n : rad(n) | f(n) }` without sieving

**Jorge Ellena Godoy** — 2026-09-10

> An explanation of all of this from scratch, for a reader new to the
> subject, is at <https://jorgell23-sys.github.io/prime-abundant-enumeration/> (Spanish at `/es/`).

<!-- hallazgo:que -->
## What was found

The prime-abundant numbers — the `n` with `rad(n) | σ(n)`, OEIS A175200 — can be
listed **without sieving**, because the defining condition forces every prime of
`n` to appear when factoring a value of `σ`; this puts the list at `10^13`
instead of `10^7`, giving 85,695 terms where 10,000 were published.

<!-- hallazgo:enunciado -->
## The statement

`n ∈ S(f)` iff every vertex of the covering digraph `D_f(n)` has an incoming
arrow (Lemma 1). Hence no prime of `n` is free (Corollary 2) and every vertex is
reachable from a cycle (Corollary 3), so `S(f)(X)` is enumerable by choosing
cycles and adding descendants (Proposition 4), with the cost controlled by: if
`q^a | n ≤ X` then every other prime of `n` is `≤ X/q^a` (Proposition 5).

| `x` | prime-abundant | prime-perfect |
|---:|---:|---:|
| `10^9` | **5,328** | **198** |
| `10^13` | 85,696 | 1,212 |

<!-- hallazgo:ejemplo -->
## The smallest case, done by hand

`n = 6 = 2·3`: `rad(6) = 6`, `σ(6) = 12`, and `6 | 12`. As a digraph, `σ(2) = 3`
gives `2 → 3` and `σ(3) = 4` gives `3 → 2` — both vertices covered, a cycle of
length 2.

From there the search does not try `7, 8, 9, …`. It factors `σ(2³) = 15 = 3·5`,
finds the prime `5` outside `24 = 2³·3`, and concludes `24·5^c ∈ S(σ)` for every
`c ≥ 1`: that is `120` (where `rad(120) = 30` and `σ(120) = 360 = 12·30`), then
`600`, then `3000`.

<!-- hallazgo:prueba -->
## Why it is proved

A prime divides a product iff it divides a factor; applied to
`rad(n) | ∏ f(q^{v_q(n)})` this *is* the digraph criterion. Read backwards, every
prime of `n` divides some `f(q^a)` with `q^a || n`. Walking backwards along
arrows must repeat a vertex, closing a cycle. And adding an already-covered
vertex cannot uncover anyone, since the exponents present do not change — so
every partial construction is itself in `S(f)`, which is completeness.

<!-- hallazgo:comprobar -->
## Check it yourself

```
python verify.py
```

38 `PASS` lines, no dependencies, seconds. Two are external: the 49 terms of the
A175200 DATA field, and the counts `198` and `5328` published in [PP12] §1.

<!-- hallazgo:nodice -->
## What it does not say

It does not claim the enumeration idea is new (§5), gives no asymptotic (§3.2),
offers no accurate predictor of `|S(f)(x)|` (§3.3), and its exhaustive
cross-check reaches `10^10`, not `10^13` (§4).

---

## 1. The objects

Let `f` be multiplicative with positive integer values, and **local**:
`p ∤ f(p^a)` for every prime `p` and every `a ≥ 1`. Set

    S(f) = { n ≥ 1 : rad(n) | f(n) },

where `rad(n)` is the product of the distinct primes of `n`.

For `f = σ` this is the set of **prime-abundant** numbers of Pollack and
Pomerance [PP12] — every prime dividing `n` divides `σ(n)` — catalogued as
**OEIS A175200**. The **prime-perfect** numbers, the subject of [PP12], are the
`n` with `rad(n) = rad(σ(n))`; they form a subset.

The **covering digraph** `D_f(n)` has the primes of `n` as vertices and an arrow

    q → p    when    p | f(q^{v_q(n)}).

Two more families appear throughout: `σ*(q^e) = q^e + 1`, `φ*(q^e) = q^e − 1`,
and the cyclotomic `Φ_m` evaluated at `q^e`, all of which are local because
`F(0) = ±1` forces `F(p^a) ≡ ±1 (mod p)`.

---

## 2. The result

### 2.1 The criterion, and the two consequences that make enumeration finite

**Lemma 1.** `n ∈ S(f)` if and only if every vertex of `D_f(n)` has an incoming
arrow.

*Proof.* `rad(n) = ∏_{p|n} p` and `f(n) = ∏_{q|n} f(q^{v_q(n)})` by
multiplicativity. A prime `p` divides a product iff it divides one of the
factors, so `p | f(n)` iff `p | f(q^{v_q(n)})` for some `q | n`, which is
precisely an arrow into `p`. Requiring it for every `p | n` is `rad(n) | f(n)`.
Locality is what makes `q = p` unavailable. ∎

**Corollary 2 (no prime is free).** If `n ∈ S(f)` then every prime of `n` is a
prime divisor of `f(q^a)` for some prime power `q^a` exactly dividing `n`.

**Corollary 3 (cycles).** A finite digraph with all in-degrees `≥ 1` contains a
directed cycle, and every vertex is reachable from the set of its cycles;
walking backwards along arrows cannot continue forever without repeating.

### 2.2 The enumeration

**Proposition 4 (completeness).** Every `n ∈ S(f)` can be built as: choose the
simple cycles of `D_f(n)`, one at a time, then add the remaining vertices in
order of reachability. Every intermediate stage is itself in `S(f)`.

*Proof.* Adding a vertex covered by what is already present cannot uncover
anyone: the exponents of the vertices present do not change, so the arrows that
existed still exist. By Corollary 3 the vertices outside the cycles admit a
topological order in which each has an already-present predecessor. ∎

**Proposition 5 (the bound).** If `q^a | n` and `n ≤ X`, then every other prime
of `n` is `≤ X/q^a`.

This is what keeps the cost down, and it is not a heuristic prune: a larger
prime cannot occur in any element containing `q^a`. The two magnitudes move in
opposite directions, so one of the two routes is always cheap — factor `f(q^a)`
when it is small, or sweep the primes up to `X/q^a` evaluating `f(q^a) mod p`
without ever building `f(q^a)`. Without this, `Φ₅` at `q^e ≈ 10^10` requires
factoring a forty-digit integer and the enumeration does not terminate.

Cycles are enumerated **by their smallest vertex**: a cycle of length `k` with
product `≤ X` has its least prime `≤ X^{1/k} ≤ √X` (since `k ≥ 2`, locality
forbidding loops), and the rest of the chain is reached by following outgoing
arrows, which is factoring. Walking a cycle backwards would instead require the
`q` with `m | f(q^b)` — a congruence condition on `q`, not a factorisation.

### 2.3 Three theorems about the sets

**Theorem 6 (factorisation into atoms).** Let `n ∈ S(f)` and let `C₁,…,C_r` be
the **weakly** connected components of `D_f(n)`, with `n_j = ∏_{p∈C_j} p^{v_p(n)}`.
Then each `n_j ∈ S(f)`, its digraph is connected, `n = ∏ n_j` with the factors
pairwise coprime, and the decomposition is unique. Conversely a product of
pairwise coprime elements of `S(f)` lies in `S(f)`.

*Proof.* If `p ∈ C_j` then some `q | n` has `p | f(q^{v_q(n)})`; that arrow puts
`q` in `C_j`, and `v_q(n_j) = v_q(n)`, so the arrow survives in `D_f(n_j)`.
Components of a graph are unique. The converse: `rad` and `f` are both
multiplicative over coprime factors and the radicals are coprime. ∎

**And it is almost always trivial**, which is the part that was not expected: up
to `10^6` **no element decomposes at all**. The smallest decomposable element of
`S(σ*)` is `14,031,225 = 4,225 · 3,321`, and of `S(Φ₃)` is
`2,003,911 = 793 · 2,527`; up to `10^10` only 7 of the 7,683 elements of `S(σ*)`
have two components. `S(f)` is not a free monoid on its atoms in any useful
sense.

**Theorem 7 (infinitude, with an `O(1)` certificate).** If `ν ∈ S(f)` and there
is a prime `r ∤ ν` with `r | f(q^{v_q(ν)})` for some `q | ν`, then
`ν·r^c ∈ S(f)` for every `c ≥ 1`, so `S(f)` is infinite.

*Proof.* In `D_f(ν r^c)` the vertices of `ν` keep their exponents and hence
their incoming arrows, and `r` receives the arrow from `q`. ∎

All **30** local functions tested carry such a certificate: 27 already in their
smallest element. For `σ*`: `ν = 18`, `f(3²) = 10`, `5 | 10`, `5 ∤ 18`, so
`18·5^c ∈ S(σ*)` — and `90` is indeed in the list.

**Theorem 8 (two-prime elements are counted, not searched).** For `f`
polynomial, `q^b mod p` is periodic in `b` with period `ord_p(q)`, so
`{ b : p | f(q^b) }` is a union of congruence classes mod `ord_p(q)`. The
`n = p^a q^b ≤ X` of a given pair are therefore the lattice points under a
hyperbola. For `σ` the congruence is explicit:

    q | σ(p^a)   ⟺   m | a+1,   where m = ord_q(p) if that order is > 1,
                                and m = q if q | p−1.

*Verified*: the formula produces **exactly** the 276 two-prime elements of
`S(σ)` up to `10^10`, spread over 51 pairs of primes, with **zero** misses; and
over the **996** pairs that have no element at all, it invents **none**.

---

## 3. The data

### 3.1 Counts

| `x` | prime-abundant | prime-perfect | `S(σ*)` | `S(φ*)` |
|---:|---:|---:|---:|---:|
| `10^6` | 475 | 40 | 461 | 465 |
| `10^9` | **5,328** | **198** | 3,913 | 4,654 |
| `10^10` | 11,051 | 333 | 7,683 | 9,405 |
| `10^11` | 22,295 | 513 | — | — |
| `10^12` | 44,157 | 796 | — | — |
| `10^13` | 85,696 | 1,212 | 54,239 | 67,350 |

Counts of prime-abundant and prime-perfect include `n = 1`, as [PP12] does. The
`10^9` row is the one stated in [PP12] §1 and is reproduced exactly.

### 3.2 Growth

The effective exponent `α = d log|S|/d log x` for `σ`, decade by decade:

| tramo | `10^3→10^4` | `10^5→10^6` | `10^7→10^8` | `10^9→10^10` | `10^11→10^12` | `10^12→10^13` |
|---|---:|---:|---:|---:|---:|---:|
| `α` | 0.4533 | 0.3947 | 0.3456 | 0.3169 | 0.2968 | **0.2880** |

Monotone, with no sign of settling. Fitting `|S(x)| = exp(c·(log x)^γ)` gives
`γ = 0.832` over the whole range and `γ = 0.758` over the last three decades:
that is `x^{o(1)}`, consistent with both bounds of [PP12] — lower
`exp((log x)^{c/log₃x})`, upper `x^{1/3+o(1)}` — and already below `x^{1/3}`
from `10^6` on.

### 3.3 What does **not** predict `|S(f)(x)|`

Measured across 30 local functions, 20 of which were not used to form any
hypothesis. Each candidate had its refutation criterion fixed **before** the
data that decided it was looked at.

| candidate | verdict |
|---|---|
| density of arrows in the global digraph | **ruled out** — `Φ₃` and `Φ₆` share their coverable primes and differ by a factor 27 |
| density of uncoverable primes | **ruled out** — same two functions share it |
| density of reciprocal pairs | **ruled out** — the excess over independence is real (6 of 10 functions, bootstrap **over primes**) but `≤ 0.027`, two orders below what a factor 27 needs |
| the fraction with `ω = 2` | **ruled out** — it *falls*, from 0.41 to 0.025 for `σ` |
| the smallest element `m₁` alone | **ruled out** — it orders well (Spearman `−0.849` out of sample) but at fixed `log X / log m₁` the spread reaches ×75 |
| a universal growth exponent | **ruled out** — χ² of homogeneity gives `p = 8·10⁻³⁷` |

The best predictor found, `log m₁` together with the arrow density, fitted on
the ten functions that suggested it and evaluated on the twenty that did not, is
off by a factor **2.29** (Spearman `+0.884`). **No accurate predictor was
found.** That is the honest state of the question.

### 3.4 Why no density could have worked

`Φ₃ = x²+x+1` and `Φ₆ = x²−x+1` have the **same** coverable primes and counts
of 2,220 against 81 at `10^10`. By Theorem 8:

| | smallest pair | condition on the exponents | smallest element |
|---|---|---|---:|
| `Φ₃` | `{3, 13}` | `a ≡ 1, 2 (mod 3)`, `b ≡ 0 (mod 1)` | `3·13 = 39` |
| `Φ₆` | `{7, 73}` | `a ≡ 4, 20 (mod 24)`, `b ≡ 1, 5 (mod 6)` | `7⁴·73 = 175,273` |

`Φ₆` does not have fewer arrows. It has the **same** arrows demanding exponent 4
where `Φ₃` demands exponent 1 — and a high exponent is a large number. A density
counts whether the arrow exists and **not at what height**, which is exactly the
information that decides the count.

---

## 4. How it was checked

Every check compares **sets, element by element**, not sizes: an enumerator that
loses one element and gains another counts the same and is wrong. (That is not
hypothetical — during this work a cross-check reported the three correct totals
with all three sets shifted by a constant.)

| # | against | reach | result |
|---|---|---|---|
| 1 | a direct sieve over every integer | `10^7` | identical sets |
| 2 | an independent segmented sieve | **`10^10`** | identical sets (11,050 / 7,683 / 9,405) |
| 3 | the b-file of A175200 (10,000 terms, by Donovan Johnson) | 7,271,402,112 | identical, term by term |
| 4 | the DATA field of A175200 (49 terms) | 4,320 | identical |
| 5 | **[PP12] §1**, published counts | `10^9` | 198 and 5,328 — exact |

Beyond `10^10` every term is verified individually: `n` is factored from
scratch and `rad(n) | f(n)` checked as integers, without using the configuration
it was built from. **0 false positives in 207,284 terms.**

`verify.py` reruns 38 of these checks in seconds, with no dependencies.

---

## 5. What this does not claim

- **Not that the enumeration idea is new.** It follows directly from Lemma 1,
  which is not new: [PP12] already work with the trees `T(p)` — root `p`,
  children the odd prime divisors of `q+1` — which are a restriction of the
  covering digraph. Their Algorithm A is **constructive, not enumerative**: it
  takes an even prime-abundant `n₀` and enlarges it until it is prime-perfect,
  to build the examples behind their lower bound. No published statement of the
  enumeration was found; that is not evidence of absence. See `PRIOR_ART.md`.
- **What is new is the data.** The published b-file stops at 7,271,402,112 and
  the published counts stop at `10^9`.
- **No asymptotic is proved.** §3.2 is measurement.
- **No accurate predictor of `|S(f)(x)|` is offered.** §3.3 is a list of six
  things that do **not** work, plus one that works badly.
- **Exhaustive cross-checking reaches `10^10`, not `10^13`.** Individual
  verification of every term rules out false positives; it does not rule out
  false negatives. Anyone extending this should re-run check #2 further.
- **Locality is required.** Without `p ∤ f(p^a)` the digraph is not defined and
  none of this applies. Euler's `φ` is not local.

---

## References

**[PP12]** Paul Pollack and Carl Pomerance, *Prime-Perfect Numbers*, INTEGERS
**12A** (2012), paper A14. <https://doi.org/10.1515/integers-2012-0044>

**[OEIS]** OEIS Foundation Inc., *The On-Line Encyclopedia of Integer
Sequences*, sequence **A175200**. <https://oeis.org/A175200>

---

## Citing

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22692700.svg)](https://doi.org/10.5281/zenodo.22692700)

> Ellena Godoy, Jorge (2026). *Prime-abundant numbers enumerated without
> sieving, to 10^13*. Zenodo. https://doi.org/10.5281/zenodo.22692700

The DOI above is the **concept** DOI and always resolves to the latest version.

---

## Author

**Jorge Ellena Godoy** — responsible for the correctness of everything
published here.

## How this was produced

System design and research direction are the author's. The mathematical results
were produced by an automated system (Claude, Anthropic) under that direction.
All computations were verified by two independent implementations and
cross-checked against published work. The author is responsible for the
correctness of everything published here.
