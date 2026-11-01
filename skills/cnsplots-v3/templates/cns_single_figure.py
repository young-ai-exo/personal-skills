#!/usr/bin/env python3
"""Template: Single-panel publication figure using cnsplots (Mode A).

Styling: Cell Press standard (Arial font, Cell 10-color palette).
Axes Sizing: ~100 pt (around 80, 100, 120, 150 pt).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import cnsplots as cns

# --- House Style Configuration ------------------------------------------------
HOUSE_PALETTE = "Cell"
DENSITY_CMAP = "viridis"


def apply_house_style() -> None:
    """Configure cnsplots with project house style: Cell palette, viridis, Arial font."""
    cns.settings.font_sans_serif = ("Arial", "DejaVu Sans")
    cns.settings.panel_label_fontname = "Arial"
    cns.settings.pdf_fonttype = 42
    cns.settings.palette_qual = HOUSE_PALETTE
    cns.settings.palette_seq = DENSITY_CMAP
    cns.setup_matplotlib(color_cycle=HOUSE_PALETTE)


def main() -> None:
    # 1. Apply unified house style
    apply_house_style()

    # 2. Figure Creation & Plotting (~100 pt axes: 120 pt width x 110 pt height)
    fig = cns.figure(width=120, height=110)

    df = cns.datasets.load_dataset("tips")

    # Statistical comparison: Mann-Whitney U test automatically performed and annotated
    ax = cns.boxplot(
        data=df,
        x="day",
        y="total_bill",
        pairs=[("Thur", "Sun")],
        showoutliers=False,
    )
    ax.set(xlabel="Day of Week", ylabel="Total Bill (USD)")

    # Inspect exact statistical result values
    res = cns.get_comparison_results(ax)
    print("Statistical comparison table:")
    print(res[["group1", "group2", "test", "pvalue_raw", "significant", "annotation"]])

    cns.savefig("cell_single_box.svg", fig=fig)
    print("Saved cell_single_box.svg")


if __name__ == "__main__":
    main()
