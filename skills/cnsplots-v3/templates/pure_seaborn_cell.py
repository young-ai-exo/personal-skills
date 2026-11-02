#!/usr/bin/env python3
"""Template: Pure Seaborn using cns_cell.mplstyle (Mode B).

Use when cnsplots is NOT installed.
Setup prerequisite:
    mkdir -p ./styles && cp <SKILL_DIR>/styles/cns_cell.mplstyle ./styles/
"""

from __future__ import annotations

import pathlib
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

mpl.use("Agg")

STYLE_PATH = pathlib.Path("styles/cns_cell.mplstyle")
LINE_WIDTH = 0.5  # seaborn filled boxplots ignore patch.linewidth
STRIP_SIZE = 2.0  # cnsplots stripplot default


def apply_house_style(style_file: pathlib.Path | str = STYLE_PATH) -> None:
    """Load the house style sheet and use its color cycle as the seaborn palette."""
    target = pathlib.Path(style_file)
    if not target.is_file():
        target = pathlib.Path("cns_cell.mplstyle")
    plt.style.use(str(target))
    cycle = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    sns.set_palette(cycle)


def main() -> int:
    """Render a boxplot with a strip overlay and save a PDF plus a PNG preview."""
    apply_house_style()
    tips = sns.load_dataset("tips")

    fig, ax = plt.subplots(figsize=(2.2, 1.8))
    sns.boxplot(
        data=tips,
        x="day",
        y="total_bill",
        ax=ax,
        fliersize=0,
        boxprops={"alpha": 0.8},
        linewidth=LINE_WIDTH,
    )
    sns.stripplot(
        data=tips,
        x="day",
        y="total_bill",
        color="black",
        size=STRIP_SIZE,
        alpha=0.4,
        jitter=0.2,
        ax=ax,
    )
    ax.set_title("A", loc="left")
    ax.set_xlabel("")
    ax.set_ylabel("Total Bill (USD)")

    fig.savefig("pure_seaborn_cell.pdf", bbox_inches=None, transparent=False)
    fig.savefig(
        "pure_seaborn_cell_preview.png",
        dpi=360,
        bbox_inches="tight",
        transparent=False,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
