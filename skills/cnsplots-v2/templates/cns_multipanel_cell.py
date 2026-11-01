#!/usr/bin/env python3
"""Template: Multi-panel publication figure using cnsplots (Mode A).

Styling: Cell Press standard (Arial font, Cell 10-color palette, ~100 pt panel baseline).
Panel Sizing Principle:
  - Panels can be added with default width/height (150 pt).
  - Explicit sizes should stay near 100 pt (common: 80, 100, 120, 150).
  - Do NOT pass fontsize= or alter point size (s=); let cnsplots defaults govern.

Run:
    python3 cns_multipanel_cell.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless environment

import cnsplots as cns

# --- 1. Global Journal Styling (Arial + Cell Palette + Viridis) ---------------
cns.settings.font_sans_serif = ("Arial", "Helvetica", "Helvetica Neue", "DejaVu Sans")
cns.settings.palette_qual = "Cell"
cns.settings.palette_seq = "viridis"
cns.setup_matplotlib()

# --- 2. Target Dimension Configuration ----------------------------------------
# Cell Press column limits: 1-column = 241 pt (85 mm), 2-column = 493 pt (174 mm)
MAX_WIDTH = 493  # Cell double column width in points
OUTPUT_PATH = "cell_multipanel.svg"

# Sample data
TIPS = cns.datasets.load_dataset("tips")
IRIS = cns.datasets.load_dataset("iris")


def main() -> None:
    mp = cns.multipanel(
        max_width=MAX_WIDTH, title="Cell Press Multi-panel Layout", loc="left"
    )

    # Panel A: Boxplot with statistical comparison (~100 pt wide)
    # Note: No explicit fontsize; cnsplots defaults (8 pt title/label, 7 pt ticks) fit 100 pt axes.
    ax_a = mp.panel("A", width=110, height=110, margin_bottom=25)
    cns.boxplot(
        data=IRIS,
        x="species",
        y="sepal_length",
        pairs=[("setosa", "versicolor")],
        ax=ax_a,
    )
    ax_a.set(xlabel="", ylabel="Sepal Length (cm)")

    # Panel B: Scatterplot (~120 pt wide)
    # Note: s=7 default marker size is already calibrated for ~100 pt axes.
    ax_b = mp.panel("B", width=130, height=110)
    cns.scatterplot(
        data=IRIS, x="sepal_length", y="petal_length", hue="species", ax=ax_b
    )
    ax_b.set(xlabel="Sepal Length (cm)", ylabel="Petal Length (cm)")
    cns.take_legend_out(title="Species", ax=ax_b)

    # Panel C: Stacked below A (compact 85 pt height)
    ax_c = mp.panel("C", width=110, height=85, below="A")
    cns.barplot(data=TIPS, x="day", y="total_bill", ax=ax_c)
    ax_c.set(xlabel="", ylabel="Mean Bill (USD)")

    # Panel D: Default panel dimensions (cns.settings.panel_width/height = 150 pt)
    mp.newline()
    ax_d = mp.panel("D")  # uses default dimensions without explicit width/height
    cns.kdeplot(data=TIPS, x="total_bill", hue="time", ax=ax_d)
    ax_d.set(xlabel="Total Bill (USD)")

    # Clean unrequested automated KS annotations if present
    for text in list(ax_d.texts):
        if text.get_text().startswith("$P"):
            text.remove()

    # Save artifact (bbox_inches=None ensures printed width matches column width)
    cns.savefig(OUTPUT_PATH, bbox_inches=None)
    print(f"Successfully generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
