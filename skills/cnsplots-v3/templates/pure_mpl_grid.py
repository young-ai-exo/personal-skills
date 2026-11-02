#!/usr/bin/env python3
"""Template: Pure Matplotlib 2x2 grid using cns_cell.mplstyle (Mode B).

Use when cnsplots is NOT installed.
Setup prerequisite:
    mkdir -p ./styles && cp <SKILL_DIR>/styles/cns_cell.mplstyle ./styles/

The style sheet sets a 2.65 pt marker diameter (scatter area s ~= 7 pt^2) and
0.5 pt patch edges, matching the cnsplots house style. The 3.5 x 3.2 in canvas
is a ~100 pt axes-density example, not a full journal column.
"""

from __future__ import annotations

import pathlib
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.use("Agg")

STYLE_PATH = pathlib.Path("styles/cns_cell.mplstyle")
FIGSIZE_IN = (3.5, 3.2)  # inches; on matplotlib >=3.11 use (3.5, 3.2, "in")


def apply_house_style(style_file: pathlib.Path | str = STYLE_PATH) -> None:
    """Load the project-local cns_cell.mplstyle file."""
    target = pathlib.Path(style_file)
    if not target.is_file():
        target = pathlib.Path("cns_cell.mplstyle")
    plt.style.use(str(target))


def main() -> int:
    """Render a 2x2 grid and save a PDF plus a PNG preview."""
    apply_house_style()
    rng = np.random.default_rng(42)

    fig, axes = plt.subplots(2, 2, figsize=FIGSIZE_IN, constrained_layout=True)

    # Panel A: Multi-line plot
    x = np.linspace(0, 10, 100)
    ax_a = axes[0, 0]
    ax_a.plot(x, np.sin(x), label="Signal 1")
    # The first two Cell colors have nearly equal lightness; a dash keeps the
    # two series distinguishable in greyscale.
    ax_a.plot(x, np.cos(x), label="Signal 2", linestyle="--")
    ax_a.set_title("A", loc="left")
    ax_a.set_xlabel("Time (s)")
    ax_a.set_ylabel("Response (a.u.)")
    ax_a.legend(loc="upper right")

    # Panel B: Bar plot with error bars
    ax_b = axes[0, 1]
    ax_b.bar(
        ["Ctrl", "Treat-A", "Treat-B"],
        [12.4, 18.2, 22.5],
        yerr=[1.2, 1.5, 1.8],
        capsize=2,
        width=0.6,
    )
    ax_b.set_title("B", loc="left")
    ax_b.set_ylabel("Expression Level")

    # Panel C: Scatter plot (marker area comes from lines.markersize in the style)
    ax_c = axes[1, 0]
    scatter_x = rng.normal(5, 1.5, 40)
    scatter_y = 2.0 * scatter_x + rng.normal(0, 2, 40)
    ax_c.scatter(scatter_x, scatter_y, alpha=0.8)
    ax_c.set_title("C", loc="left")
    ax_c.set_xlabel("Biomarker X")
    ax_c.set_ylabel("Biomarker Y")

    # Panel D: Histogram / distribution
    ax_d = axes[1, 1]
    data_dist = rng.exponential(scale=2.0, size=200)
    ax_d.hist(data_dist, bins=15, density=True, edgecolor="black", alpha=0.7)
    ax_d.set_title("D", loc="left")
    ax_d.set_xlabel("Decay Time")
    ax_d.set_ylabel("Density")

    fig.savefig("pure_mpl_grid.pdf", bbox_inches=None, transparent=False)
    fig.savefig(
        "pure_mpl_grid_preview.png",
        dpi=360,
        bbox_inches="tight",
        transparent=False,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
