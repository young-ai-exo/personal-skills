#!/usr/bin/env python3
"""Template: Single-panel publication figure using cnsplots (Mode A).

Styling: Cell Press default (Arial-first font stack, Cell 10-color palette).
Sizing: ~100 pt axes baseline; the canvas is not automatically a journal column.
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
    """Render a single-panel boxplot and save a PDF plus a PNG preview."""
    apply_house_style()

    fig = cns.figure(width=120, height=110, unit="pt")
    tips = cns.datasets.load_dataset("tips")
    ax = cns.boxplot(
        data=tips,
        x="day",
        y="total_bill",
        pairs=[("Thur", "Sun")],
        order=["Thur", "Fri", "Sat", "Sun"],
        showoutliers=False,
    )
    ax.set(xlabel="Day of Week", ylabel="Total Bill (USD)")

    cns.savefig("cell_single_box.pdf", fig=fig, bbox_inches=None, transparent=False)
    cns.savefig(
        "cell_single_box_preview.png",
        fig=fig,
        dpi=360,
        bbox_inches="tight",
        transparent=False,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
