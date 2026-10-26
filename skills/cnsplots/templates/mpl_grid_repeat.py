#!/usr/bin/env python3
"""Template: uniform repeated grid of one plot type, matplotlib layout.

Use when every panel is the same size and the same plot type, iterated over
groups, genes, or samples, and there are no heterogeneous panels in the figure.
GridSpec allots equal cells, so rows and columns align exactly regardless of tick
label width.

Runs as-is on a built-in dataset. Replace the CONFIGURE block with real data.

    python3 mpl_grid_repeat.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless; must precede any plotting import

import cnsplots as cns

# --- CONFIGURE ---------------------------------------------------------------
# Replace with the real frame, the column to facet on, and the measured column.
DATA = cns.datasets.load_dataset("tips")
FACET_COLUMN = "day"  # one panel per level of this column
X_COLUMN = "sex"
Y_COLUMN = "total_bill"
Y_LABEL = "Total bill (USD)"

NCOLS = 2
PANEL_W = 130  # points (1/72 inch), per panel
PANEL_H = 110
OUTPUT = "grid_repeat.svg"
# -----------------------------------------------------------------------------


def main() -> None:
    levels = list(DATA[FACET_COLUMN].unique())
    nrows = -(-len(levels) // NCOLS)  # ceiling division

    # cnsplots 0.8+ returns the styled Figure; on 0.7 and earlier use plt.gcf().
    fig = cns.figure(width=NCOLS * PANEL_W, height=nrows * PANEL_H)
    axes = fig.subplots(nrows, NCOLS, squeeze=False)

    for index, level in enumerate(levels):
        ax = axes[index // NCOLS][index % NCOLS]
        subset = DATA[DATA[FACET_COLUMN] == level]

        cns.boxplot(data=subset, x=X_COLUMN, y=Y_COLUMN, ax=ax)

        ax.set_title(str(level))
        ax.set_xlabel("")
        # Label the y axis only on the first column to avoid repetition.
        ax.set_ylabel(Y_LABEL if index % NCOLS == 0 else "")

    # Hide cells with no data rather than leaving empty frames.
    for index in range(len(levels), nrows * NCOLS):
        axes[index // NCOLS][index % NCOLS].set_visible(False)

    fig.tight_layout()
    cns.savefig(OUTPUT)
    print(f"wrote {OUTPUT}: {len(levels)} panels in {nrows}x{NCOLS}")


if __name__ == "__main__":
    main()
