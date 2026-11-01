#!/usr/bin/env python3
"""Template: Pure Seaborn with exported cns_cell.mplstyle (Mode B).

Use when cnsplots is NOT installed.
Applies Cell Press style sheet and maps categorical variables cleanly
to the Cell 10-color palette.

Run:
    python3 pure_seaborn_cell.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# Add styles directory to path for color definitions
SKILL_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_DIR / "styles"))
import cell_colors

# 1. Apply style sheet and seaborn color palette
STYLE_PATH = SKILL_DIR / "styles" / "cns_cell.mplstyle"
plt.style.use(str(STYLE_PATH))
cell_colors.apply_cell_palette_to_seaborn()

# Load seaborn example dataset or user dataframe
df = sns.load_dataset("tips")


def main() -> None:
    # Target axes: ~110 pt wide, ~100 pt high
    fig, ax = plt.subplots(figsize=(2.2, 1.8))

    # Boxplot with scatter strip overlay
    sns.boxplot(
        data=df,
        x="day",
        y="total_bill",
        ax=ax,
        fliersize=0,  # hide default fliers
        boxprops={"alpha": 0.8},
        linewidth=0.5,
    )

    # Individual observation points with jitter (marker size s=7 matches ~100 pt axes)
    sns.stripplot(
        data=df,
        x="day",
        y="total_bill",
        color="black",
        size=2.5,
        alpha=0.4,
        jitter=0.2,
        ax=ax,
    )

    ax.set_title("A", loc="left", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Total Bill (USD)")

    output = "pure_seaborn_cell.svg"
    fig.savefig(output)
    print(f"Generated Cell-compliant seaborn figure: {output}")


if __name__ == "__main__":
    main()
