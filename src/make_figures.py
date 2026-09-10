# -*- coding: utf-8 -*-
"""Draw the three SVG figures of docs/, from the data in data/.

Standard library only.  SVG on purpose: it stays sharp at any zoom, it prints,
it works on light and dark themes, and -- the reason that decides it -- it can
be checked against the data, which a bitmap cannot.

    python src/make_figures.py
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
DATA = os.path.join(ROOT, "data")

CSS = """
  <style>
    .bg   { fill: none; }
    .axis { stroke: #888; stroke-width: 1; fill: none; }
    .grid { stroke: #ccc; stroke-width: .5; fill: none; stroke-dasharray: 3 3; }
    .lbl  { font: 11px system-ui, sans-serif; fill: #666; }
    .ttl  { font: bold 13px system-ui, sans-serif; fill: #333; }
    .a    { stroke: #1f77b4; stroke-width: 2.5; fill: none; }
    .b    { stroke: #d62728; stroke-width: 2.5; fill: none; }
    .c    { stroke: #2ca02c; stroke-width: 2.5; fill: none; }
    .dot  { fill: #1f77b4; }
    .dotb { fill: #d62728; }
    .node { fill: #fff; stroke: #1f77b4; stroke-width: 2; }
    .nlbl { font: bold 13px system-ui, sans-serif; fill: #1f77b4;
            text-anchor: middle; }
    .arr  { stroke: #555; stroke-width: 1.8; fill: none;
            marker-end: url(#head); }
    @media (prefers-color-scheme: dark) {
      .lbl { fill: #aaa; } .ttl { fill: #eee; } .node { fill: #222; }
    }
  </style>
"""

HEAD = """  <defs>
    <marker id="head" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#555"/>
    </marker>
  </defs>
"""


def write(name, body, w=640, h=380):
    path = os.path.join(DOCS, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write('<svg xmlns="http://www.w3.org/2000/svg" '
                 'viewBox="0 0 %d %d" width="%d" height="%d" '
                 'role="img">\n' % (w, h, w, h))
        fh.write(CSS)
        fh.write(HEAD)
        fh.write(body)
        fh.write("</svg>\n")
    print("  %s" % name)


def log10(x):
    from math import log10 as L
    return L(x)


# ---------------------------------------------------------------------------
def fig_growth(counts):
    """How many there are, decade by decade -- and how the slope falls."""
    ks = [k for k in range(2, 14)]
    pa = [counts["by_decade"]["1e%d" % k]["prime_abundant"] for k in ks]
    pp = [counts["by_decade"]["1e%d" % k]["prime_perfect"] for k in ks]
    L, R, T, B = 70, 610, 40, 320
    xs = lambda k: L + (R - L) * (k - ks[0]) / (ks[-1] - ks[0])
    ymax = log10(max(pa)) * 1.05
    ys = lambda v: B - (B - T) * (log10(max(v, 1)) / ymax)

    out = ['<text class="ttl" x="16" y="22">How many are there below x?</text>']
    for g in range(0, 6):
        y = ys(10 ** g)
        out.append('<path class="grid" d="M%d %.1f H%d"/>' % (L, y, R))
        out.append('<text class="lbl" x="%d" y="%.1f" text-anchor="end">10^%d'
                   '</text>' % (L - 8, y + 4, g))
    out.append('<path class="axis" d="M%d %d V%d H%d"/>' % (L, T, B, R))
    for k in ks:
        if k % 2 == 0:
            out.append('<text class="lbl" x="%.1f" y="%d" '
                       'text-anchor="middle">10^%d</text>'
                       % (xs(k), B + 18, k))
    for cls, vals in (("a", pa), ("b", pp)):
        d = " ".join(("M" if i == 0 else "L") + "%.1f %.1f"
                     % (xs(k), ys(v)) for i, (k, v) in enumerate(zip(ks, vals)))
        out.append('<path class="%s" d="%s"/>' % (cls, d))
        for k, v in zip(ks, vals):
            out.append('<circle class="%s" cx="%.1f" cy="%.1f" r="3"/>'
                       % ("dot" if cls == "a" else "dotb", xs(k), ys(v)))
    out.append('<text class="lbl" x="%.1f" y="%.1f" fill="#1f77b4">'
               'prime-abundant (%d at 10^13)</text>'
               % (xs(6), ys(pa[-1]) - 14, pa[-1]))
    out.append('<text class="lbl" x="%.1f" y="%.1f" fill="#d62728">'
               'prime-perfect (%d at 10^13)</text>'
               % (xs(6), ys(pp[4]) + 22, pp[-1]))
    out.append('<text class="lbl" x="16" y="%d">The published b-file stops at '
               '7,271,402,112; the published counts stop at 10^9.</text>'
               % (B + 46))
    write("growth.svg", "\n".join(out) + "\n")


# ---------------------------------------------------------------------------
def fig_digraph():
    """The criterion itself: every vertex needs an incoming arrow."""
    out = ['<text class="ttl" x="16" y="22">The rule, drawn: '
           'every prime needs an arrow coming in</text>']

    def node(cx, cy, label):
        return ('<circle class="node" cx="%d" cy="%d" r="22"/>'
                '<text class="nlbl" x="%d" y="%d">%s</text>'
                % (cx, cy, cx, cy + 5, label))

    def curve(x1, y1, x2, y2, bend):
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + bend
        return '<path class="arr" d="M%d %d Q%.0f %.0f %d %d"/>' % (
            x1, y1, mx, my, x2, y2)

    # left: n = 6, a 2-cycle
    out.append('<text class="lbl" x="60" y="60">n = 6 = 2 &#183; 3 &#8212; '
               'belongs</text>')
    out.append(node(90, 140, "2"))
    out.append(node(230, 140, "3"))
    out.append(curve(114, 128, 208, 128, -34))
    out.append(curve(208, 152, 114, 152, 34))
    out.append('<text class="lbl" x="120" y="96">&#963;(2) = 3</text>')
    out.append('<text class="lbl" x="118" y="200">&#963;(3) = 4 = 2&#178;'
               '</text>')
    out.append('<text class="lbl" x="60" y="250">Both covered. '
               'A cycle of length 2.</text>')

    # right: n = 12, fails.  sigma(3) = 4, so 3 -> 2 DOES exist; what is
    # missing is an arrow into 3, because sigma(2^2) = 7 and 3 does not
    # divide 7.  (Drawn the other way round at first, and it was wrong.)
    out.append('<text class="lbl" x="390" y="60">n = 12 = 2&#178; &#183; 3 '
               '&#8212; does not</text>')
    out.append(node(420, 140, "2"))
    out.append(node(560, 140, "3"))
    out.append(curve(538, 152, 444, 152, 34))
    out.append('<text class="lbl" x="436" y="200">&#963;(3) = 4 = 2&#178;, '
               'so 3 &#8594; 2</text>')
    out.append('<text class="lbl" x="392" y="96">but &#963;(2&#178;) = 7, and '
               '3 &#8942; 7:</text>')
    out.append('<text class="lbl" x="392" y="114">nothing covers the 3</text>')
    out.append('<text class="lbl" x="390" y="250">&#963;(12) = 28, and '
               '6 does not divide 28.</text>')
    write("digraph.svg", "\n".join(out) + "\n", 640, 290)


# ---------------------------------------------------------------------------
def fig_gap(byf):
    """Same arrows, different heights: why no density could predict."""
    f3 = byf["functions"]["Phi3 = x^2+x+1"]
    f6 = byf["functions"]["Phi6 = x^2-x+1"]
    out = ['<text class="ttl" x="16" y="22">Same primes, same arrows &#8212; '
           'and 27 times fewer elements</text>']
    rows = [
        ("&#934;&#8323; = x&#178;+x+1", f3["smallest"],
         f3["counts"]["10000000000"], "smallest pair {3, 13}, exponent 1",
         "a"),
        ("&#934;&#8326; = x&#178;&#8722;x+1", f6["smallest"],
         f6["counts"]["10000000000"], "smallest pair {7, 73}, exponent 4",
         "b"),
    ]
    y = 70
    for name, small, cnt, note, cls in rows:
        out.append('<text class="ttl" x="30" y="%d">%s</text>' % (y, name))
        out.append('<text class="lbl" x="30" y="%d">smallest element: '
                   '%s</text>' % (y + 20, "{:,}".format(small)))
        out.append('<text class="lbl" x="30" y="%d">%s</text>'
                   % (y + 38, note))
        w = 380.0 * (log10(cnt) / log10(rows[0][2]))
        out.append('<rect x="300" y="%d" width="%.0f" height="26" rx="4" '
                   'fill="%s" opacity=".75"/>'
                   % (y - 16, w, "#1f77b4" if cls == "a" else "#d62728"))
        out.append('<text class="lbl" x="%.0f" y="%d">%s elements below '
                   '10^10</text>' % (306 + w, y + 3, "{:,}".format(cnt)))
        y += 110
    out.append('<text class="lbl" x="30" y="290">A density counts whether an '
               'arrow exists.</text>')
    out.append('<text class="lbl" x="30" y="308">It cannot see at what '
               'exponent &#8212; and that is what decides the count.</text>')
    write("gap.svg", "\n".join(out) + "\n", 640, 330)


def main():
    counts = json.load(open(os.path.join(DATA, "counts.json")))
    byf = json.load(open(os.path.join(DATA, "counts_by_function.json")))
    print("figures:")
    fig_growth(counts)
    fig_digraph()
    fig_gap(byf)


if __name__ == "__main__":
    main()
