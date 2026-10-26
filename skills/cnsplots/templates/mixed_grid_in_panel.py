#!/usr/bin/env python3
"""Template: heterogeneous figure containing an aligned repeated grid.

One mp.panel() is used as an empty host rectangle. Its coordinates bound a
GridSpec, so matplotlib lays out the repeated cells and their edges align
exactly, while multipanel still draws the host's panel letter.

Two ordering constraints, both load-bearing:
  1. Subdivide only after every mp.panel() call. Adding a panel later re-flows
     the host and the already-placed cells end up outside its rectangle.
  2. Call fig.canvas.draw() before reading host.get_position(); before the first
     draw the panel's decoration reserve is unmeasured.

Runs as-is on a built-in dataset. Replace the CONFIGURE block with real data.

    python3 mixed_grid_in_panel.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless; must precede pyplot import

import matplotlib.pyplot as plt

import cnsplots as cns

# --- CONFIGURE ---------------------------------------------------------------
TIPS = cns.datasets.load_dataset("tips")

GRID_FACET = "day"  # one grid cell per level
GRID_X = "sex"
GRID_Y = "total_bill"
GRID_ROWS, GRID_COLS = 2, 2

# max_width must exceed the sum of axes widths PLUS each panel's decoration
# reserve and margins, or a row wraps silently. That reserve grows once content
# is drawn: a 150- and a 300-point panel share a row from 507 empty, 519 with a
# boxplot in each. The assertion at the end of main() catches an unintended wrap.
MAX_WIDTH = 560
HOST_W, HOST_H = 300, 120  # host rectangle for the grid block
OUTPUT = "mixed_grid.svg"
# -----------------------------------------------------------------------------


def main() -> None:
    mp = cns.multipanel(max_width=MAX_WIDTH)

    # Panel A: ordinary heterogeneous panel.
    ax_a = mp.panel("A", width=150, height=120)
    cns.boxplot(data=TIPS, x="day", y="total_bill", ax=ax_a)
    ax_a.set_xlabel("")
    ax_a.set_ylabel("Total bill (USD)")

    # Panel B: host for the repeated grid. Nothing is drawn into it directly.
    host = mp.panel("B", width=HOST_W, height=HOST_H)

    # Panel C: stacked under A. Declared BEFORE subdividing the host.
    ax_c = mp.panel("C", width=150, height=90, below="A")
    cns.barplot(data=TIPS, x="day", y="tip", ax=ax_c)
    ax_c.set_xlabel("")
    ax_c.set_ylabel("Mean tip (USD)")

    # Every panel now exists. Settle the layout, then subdivide the host.
    fig = mp.fig
    fig.canvas.draw()

    # Confirm A and B share a row; if MAX_WIDTH is too small B wraps silently
    # and the grid lands under A instead of beside it.
    if abs(ax_a.get_position().y0 - host.get_position().y0) > 1e-6:
        raise SystemExit(
            f"panel B wrapped to a new row: raise MAX_WIDTH above {MAX_WIDTH}"
        )

    box = host.get_position()
    host.set_axis_off()  # hide the empty frame; the "B" label still draws

    gs = fig.add_gridspec(
        GRID_ROWS,
        GRID_COLS,
        left=box.x0,
        right=box.x1,
        bottom=box.y0,
        top=box.y1,
        wspace=0.5,
        hspace=0.6,
    )

    levels = list(TIPS[GRID_FACET].unique())[: GRID_ROWS * GRID_COLS]
    cells = []
    for index, level in enumerate(levels):
        ax = fig.add_subplot(gs[index // GRID_COLS, index % GRID_COLS])
        subset = TIPS[TIPS[GRID_FACET] == level]

        cns.boxplot(data=subset, x=GRID_X, y=GRID_Y, ax=ax)
        cns.setup_ax(ax)

        ax.set_title(str(level))
        ax.set_xlabel("")
        ax.set_ylabel("")
        cells.append(ax)

    cns.savefig(OUTPUT)

    # Alignment check: one distinct x0 per column, one y0 per row.
    columns = {index % GRID_COLS: set() for index in range(len(cells))}
    for index, ax in enumerate(cells):
        columns[index % GRID_COLS].add(round(ax.get_position().x0, 6))
    aligned = all(len(values) == 1 for values in columns.values())
    print(f"wrote {OUTPUT}: {len(cells)} grid cells, columns aligned: {aligned}")


if __name__ == "__main__":
    main()
