#!/usr/bin/env python3
"""Template: Single-panel publication figure using cnsplots (Mode A).

Styling: Cell Press standard (Arial font, Cell 10-color palette).
Axes Sizing: ~100 pt (around 80, 100, 120, 150 pt).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import cnsplots as cns

# --- 1. Global Journal Styling ------------------------------------------------
cns.settings.font_sans_serif = ("Arial", "Helvetica", "Helvetica Neue", "DejaVu Sans")
cns.settings.palette_qual = "Cell"
cns.settings.palette_seq = "viridis"

# --- 2. Figure Creation & Plotting --------------------------------------------
# 120 pt width x 110 pt height (axes around 100 pt)
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
