#!/usr/bin/env python3
"""Template: Multi-panel publication figure using cnsplots (Mode A).

Styling: Cell Press default (Arial-first font stack, Cell 10-color palette).
Panel Sizing Principle:
  - Panels can be added with default width/height (150 pt).
  - Explicit sizes should stay near 100 pt (common: 80, 100, 120, 150).
  - multipanel(..., unit="pt") makes every width/height a point value.
  - Do NOT pass fontsize= or enlarge markers; let cnsplots defaults govern.

Run:
    python3 cns_multipanel_cell.py
"""

from __future__ import annotations

import sys

import cnsplots as cns
import matplotlib as mpl

mpl.use("Agg")

HOUSE_PALETTE = "Cell"
DENSITY_CMAP = "viridis"
FONT_SANS_SERIF = (
    "Arial",
    "Helvetica",
    "Nimbus Sans",
    "Liberation Sans",
    "DejaVu Sans",
)

# Cell Press column limits: 1-column = 241 pt (85 mm), 2-column = 493 pt (174 mm)
MAX_WIDTH = 493
OUTPUT_PATH = "cell_multipanel.pdf"
PREVIEW_PATH = "cell_multipanel_preview.png"


def apply_house_style() -> None:
    """Configure cnsplots with Cell palette, viridis, Arial-first fonts, and print-safe export."""
    cns.settings.font_sans_serif = FONT_SANS_SERIF
    cns.settings.panel_label_fontname = None
    cns.settings.pdf_fonttype = 42
    cns.settings.svg_fonttype = "none"
    cns.settings.palette_qual = HOUSE_PALETTE
    cns.settings.palette_seq = DENSITY_CMAP
    cns.settings.figure_dpi = 360
    cns.settings.savefig_dpi = 360
    cns.settings.savefig_transparent = False
    cns.setup_matplotlib(color_cycle=HOUSE_PALETTE, color_map=DENSITY_CMAP)


def main() -> int:
    """Build the multipanel figure and save a PDF plus a PNG preview."""
    apply_house_style()
    tips = cns.datasets.load_dataset("tips")
    iris = cns.datasets.load_dataset("iris")

    mp = cns.multipanel(
        max_width=MAX_WIDTH,
        title="Cell Press Multi-panel Layout",
        loc="left",
        unit="pt",  # inherited by every mp.panel() call
    )

    # Panel A: Boxplot with statistical comparison (~100 pt wide)
    ax_a = mp.panel("A", width=110, height=110, margin_bottom=25)
    cns.boxplot(
        data=iris,
        x="species",
        y="sepal_length",
        pairs=[("setosa", "versicolor")],
        ax=ax_a,
    )
    ax_a.set(xlabel="", ylabel="Sepal Length (cm)")

    # Panel B: Scatterplot (~120 pt wide)
    ax_b = mp.panel("B", width=130, height=110)
    cns.scatterplot(data=iris, x="sepal_length", y="petal_length", hue="species", ax=ax_b)
    ax_b.set(xlabel="Sepal Length (cm)", ylabel="Petal Length (cm)")
    cns.take_legend_out(title="Species", ax=ax_b)

    # Panel C: Stacked below A (compact 85 pt height)
    ax_c = mp.panel("C", width=110, height=85, below="A")
    cns.barplot(data=tips, x="day", y="total_bill", ax=ax_c)
    ax_c.set(xlabel="", ylabel="Mean Bill (USD)")

    # Panel D: Default panel dimensions (cns.settings.panel_width/height = 150 pt)
    mp.newline()
    ax_d = mp.panel("D")
    cns.kdeplot(data=tips, x="total_bill", hue="time", ax=ax_d)
    ax_d.set(xlabel="Total Bill (USD)")

    # Remove the unrequested KDE Kolmogorov-Smirnov annotation.
    for text in list(ax_d.texts):
        if text.get_text().startswith("$P"):
            text.remove()

    # bbox_inches=None keeps the full 493 pt / 174 mm canvas.
    cns.savefig(OUTPUT_PATH, bbox_inches=None, transparent=False)
    cns.savefig(PREVIEW_PATH, dpi=360, bbox_inches="tight", transparent=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
