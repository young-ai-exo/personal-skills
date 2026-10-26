#!/usr/bin/env python3
"""Template: heterogeneous publication figure via cns.multipanel.

Use when panels differ in size or plot type and you want automatic A/B/C labels.
Panels flow left to right and wrap at max_width; below= stacks one under another.

multipanel does NOT align axes edges across panels whose y tick labels differ in
width. If you need a visually aligned block of repeated panels, use
mixed_grid_in_panel.py instead.

Runs as-is on built-in datasets. Replace the CONFIGURE block with real data.

    python3 multipanel_heterogeneous.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless; must precede pyplot import

import cnsplots as cns

# --- CONFIGURE ---------------------------------------------------------------
TIPS = cns.datasets.load_dataset("tips")
IRIS = cns.datasets.load_dataset("iris")

MAX_WIDTH = 420  # row wraps beyond this many points
TITLE = "Cohort summary"
OUTPUT = "multipanel.svg"
# -----------------------------------------------------------------------------


def main() -> None:
    mp = cns.multipanel(max_width=MAX_WIDTH, title=TITLE, loc="left")

    # Panel A: distribution across categories, narrow and tall.
    # margin_bottom reserves space for the tick labels; without it they collide
    # with panel C below. Rotating labels needs more: 30 was still overlapping,
    # 30 points of margin cleared it. Prefer short category names over rotation.
    ax_a = mp.panel("A", width=110, height=130, margin_bottom=30)
    cns.violinplot(data=IRIS, x="species", y="sepal_length", ax=ax_a)
    ax_a.set_xlabel("")
    ax_a.set_ylabel("Sepal length (cm)")
    ax_a.tick_params(axis="x", rotation=30)

    # Panel B: relationship, wider. Legend moved out so it cannot cover points.
    ax_b = mp.panel("B", width=190, height=130)
    cns.scatterplot(
        data=IRIS, x="sepal_length", y="petal_length", hue="species", ax=ax_b
    )
    ax_b.set_xlabel("Sepal length (cm)")
    ax_b.set_ylabel("Petal length (cm)")
    cns.take_legend_out(title="Species", ax=ax_b)  # ax is keyword-only

    # Panel C: stacked directly under A, shorter.
    ax_c = mp.panel("C", width=110, height=85, below="A")
    cns.barplot(data=TIPS, x="day", y="total_bill", ax=ax_c)
    ax_c.set_xlabel("")
    ax_c.set_ylabel("Mean bill (USD)")

    # Panel D: new row. newline() consumes the rest of the current row.
    #
    # WARNING: kdeplot with a two-level hue silently runs a two-sample
    # Kolmogorov-Smirnov test and annotates "P = ...". add_mode does not
    # disable it. Keep it only if that test is the one you intend to report,
    # and state it in the caption. To drop it, remove the annotation:
    #     for text in list(ax_d.texts):
    #         if text.get_text().startswith("$P"):
    #             text.remove()
    mp.newline()
    ax_d = mp.panel("D", width=190, height=85)
    cns.kdeplot(data=TIPS, x="total_bill", hue="time", ax=ax_d)
    ax_d.set_xlabel("Total bill (USD)")

    cns.savefig(OUTPUT)
    print(f"wrote {OUTPUT}: {len(mp.axes)} labeled panels")


if __name__ == "__main__":
    main()
