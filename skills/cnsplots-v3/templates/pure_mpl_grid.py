#!/usr/bin/env python3
"""Template: Pure Matplotlib 2x2 grid using project-local cns_cell.mplstyle (Mode B).

Use when cnsplots is NOT installed.
Setup prerequisite:
    Copy 'cns_cell.mplstyle' from the skill styles directory to your local project:
    $ mkdir -p ./styles && cp <SKILL_DIR>/styles/cns_cell.mplstyle ./styles/

Axes Sizing Principle (~100 pt):
  - In matplotlib, figsize is specified in inches.
  - 1 inch = 72 points. A 100 pt axes is ~1.39 inches.
  - For a 2x2 grid of ~100 pt axes plus tick labels/margins, figsize=(3.5, 3.2) is ideal.
  - Cell 1-column limit is 85 mm (~3.35 inches / 241 pt); 1.5-column is 114 mm (~4.49 inches).

Run:
    python3 pure_mpl_grid.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# --- Project-Local Style Configuration ----------------------------------------
STYLE_PATH = Path("styles/cns_cell.mplstyle")


def apply_house_style(style_file: Path | str = STYLE_PATH) -> None:
    """Load project house style sheet for pure matplotlib."""
    target = Path(style_file)
    if not target.is_file():
        # Also check current working directory
        if Path("cns_cell.mplstyle").is_file():
            target = Path("cns_cell.mplstyle")
        else:
            raise FileNotFoundError(
                f"Style file not found at {target}. Please copy 'cns_cell.mplstyle' "
                "from the skill into your project folder: 'cp <SKILL_DIR>/styles/cns_cell.mplstyle ./styles/'"
            )
    plt.style.use(str(target))


# Reproducible sample data
np.random.seed(42)
x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)
groups = ["Ctrl", "Treat-A", "Treat-B"]
means = [12.4, 18.2, 22.5]
errors = [1.2, 1.5, 1.8]


def main() -> None:
    # 1. Apply unified house style
    apply_house_style()

    # 2. Build 2x2 grid (~100 pt axes per cell)
    fig, axes = plt.subplots(2, 2, figsize=(3.5, 3.2), constrained_layout=True)

    # Panel A: Multi-line plot (auto-advances through Cell 10-color cycle)
    ax_a = axes[0, 0]
    ax_a.plot(x, y1, label="Signal 1")
    ax_a.plot(x, y2, label="Signal 2")
    ax_a.set_title("A", loc="left", fontweight="bold")
    ax_a.set_xlabel("Time (s)")
    ax_a.set_ylabel("Response (a.u.)")
    ax_a.legend(loc="upper right")

    # Panel B: Bar plot with error bars
    ax_b = axes[0, 1]
    ax_b.bar(groups, means, yerr=errors, capsize=2, width=0.6)
    ax_b.set_title("B", loc="left", fontweight="bold")
    ax_b.set_ylabel("Expression Level")

    # Panel C: Scatter plot
    # Crucial: Default marker size s=7 fits ~100 pt axes perfectly.
    ax_c = axes[1, 0]
    scatter_x = np.random.normal(5, 1.5, 40)
    scatter_y = 2.0 * scatter_x + np.random.normal(0, 2, 40)
    ax_c.scatter(scatter_x, scatter_y, s=7, alpha=0.8)
    ax_c.set_title("C", loc="left", fontweight="bold")
    ax_c.set_xlabel("Biomarker X")
    ax_c.set_ylabel("Biomarker Y")

    # Panel D: Histogram / Distribution
    ax_d = axes[1, 1]
    data_dist = np.random.exponential(scale=2.0, size=200)
    ax_d.hist(
        data_dist,
        bins=15,
        density=True,
        edgecolor="black",
        linewidth=0.5,
        alpha=0.7,
    )
    ax_d.set_title("D", loc="left", fontweight="bold")
    ax_d.set_xlabel("Decay Time")
    ax_d.set_ylabel("Density")

    # Save artifact
    output = "pure_mpl_grid.pdf"
    fig.savefig(output)
    print(f"Generated Cell-compliant pure matplotlib figure: {output}")


if __name__ == "__main__":
    main()
