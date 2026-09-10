# Prior art: what was searched, where, and when

**Not finding something is not the same as it being new.**

Searched on **2026-09-10**.

---

## Positive control

A search that finds nothing is worthless unless it can be shown to find
something when there is something to find. So, before trusting any negative:

| control | query | expected | got |
|---|---|---|---|
| **positive** | the sequence `6, 24, 28, 40, 54, 96, 120, 135, 216, 224, 234, 270` submitted to the OEIS search API | should recover A175200, which exists | **A175200**, *"Numbers k such that rad(k) divides sigma(k)"*, with the comment *"Pollack and Pomerance call these numbers 'prime-abundant numbers'"* and the link to the paper |
| **negative** | the same list with six digits perturbed: `6, 24, 29, 41, 55, 97, 121, 137, 217, 225, 235, 271` | should find nothing | `NO_ESTA_EN_OEIS`, nothing |

The arbiter distinguishes a real sequence from noise. Only with that
established are the negatives below worth anything.

---

## What is established, and is cited as such

These are **not** claimed as findings here:

- **The object has a name and a paper.** Paul Pollack and Carl Pomerance,
  *Prime-Perfect Numbers*, INTEGERS **12A** (2012), paper A14: *"Call `n`
  prime-abundant if every prime dividing `n` divides `σ(n)`."* That is exactly
  `S(σ)`.
- **The upper bound is theirs.** Their Theorem 1.2: the number of prime-abundant
  `n ≤ x` is at most `x^{1/3+o(1)}`. Their Theorem 1.1 is the lower bound for
  prime-perfect.
- **The conjecture is Pomerance's** (ca. 1973, unpublished, stated as
  Conjecture 1.3 in [PP12]): `N_σ(x) = o(x^ε)` for every `ε > 0`.
- **The digraph is essentially theirs too.** Their trees `T(p)` — root `p`,
  children the odd prime divisors of `q+1` — are the covering digraph
  restricted to exponent 1 and odd primes.
- **The catalogue entry and its b-file** are OEIS A175200, submitted by Michel
  Lagneau in 2010, with a b-file of 10,000 terms computed by Donovan Johnson.

The full text of [PP12] was read, not just its abstract, specifically to check
whether it contains an enumeration algorithm. **Its Algorithm A is
constructive, not enumerative**: it takes an even prime-abundant `n₀` and
enlarges it until it is prime-perfect, in order to exhibit the family behind
their lower bound. There is no exhaustive listing and no table of values in it.

---

## What was searched, and found nothing

| where | query | result |
|---|---|---|
| OEIS (API) | the first terms of `S(σ*)`, `S(φ*)`, `S(Φ₃)`, `S(Φ₆)` | **not catalogued**, none of the four |
| web | `algorithm enumerate prime-perfect numbers "rad(n)" divides sigma(n) computation` | the [PP12] paper and unrelated work on perfect numbers |
| web | `Pollack Pomerance "Prime-Perfect Numbers" INTEGERS 2012 prime-abundant counting function` | [PP12] and its DOI; no enumeration method |
| web | `enumerate integers "rad(n) divides" f(n) directed graph primes cycles algorithm sieve-free` | generic material on the radical of an integer and on cycle enumeration in graphs; nothing on this object |
| a local corpus of 148,580 harvested works | `prime-perfect numbers, integers n with rad(n) dividing sigma(n)` | **nothing usable** — it returned the project's own notes and secondary-school algebra textbooks. This corpus has no literature at this level, and **its silence is not evidence of anything**. It is recorded here because a search that cannot find is not a search that found nothing. |

---

## What is therefore claimed as new, and what is not

**Claimed as new — the data.**

- The b-file of A175200 publishes 10,000 terms, the largest being
  **7,271,402,112**. This repository lists **85,695** terms up to `10^13`.
- [PP12] §1 publishes counts up to `10^9`. This repository gives them up to
  `10^13`, with the `10^9` row reproducing their two published numbers exactly.
- `S(σ*)`, `S(φ*)`, `S(Φ₃)` and `S(Φ₆)` are not in OEIS; their terms up to
  `10^13` (for the first two) are given here.

**Claimed as new — the negative results.** The six invariants that do *not*
predict `|S(f)(x)|` (RESULT.md §3.3) concern an object with no literature of its
own beyond `S(σ)`, and each was ruled out against a criterion fixed in advance.

**NOT claimed as new — the enumeration idea.** It follows directly from the
digraph characterisation, which is not new. No published statement of it was
found, but the searches above are what they are: an absence in five places, not
a proof. Anyone who knows of prior work on this is asked to open an issue.

**NOT claimed at all — any asymptotic.** RESULT.md §3.2 is measurement over a
finite range and settles nothing about the limit.
