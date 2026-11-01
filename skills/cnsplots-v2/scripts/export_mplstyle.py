#!/usr/bin/env python3
"""Export and validate cnsplots Cell style rcParams to .mplstyle format.

Generates or validates skills/cnsplots-v2/styles/cns_cell.mplstyle.

Usage:
    python3 export_mplstyle.py [--validate-only]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TARGET_FILE = SKILL_DIR / "styles" / "cns_cell.mplstyle"

STYLE_TEMPLATE = """# =============================================================================
# cnsplots v2 - Cell Press Style Matplotlib Style Sheet
# Calibrated for publication figures with ~100 px/pt axes, Arial font,
# Cell 10-color palette, and 8 pt / 7 pt hierarchy.
# =============================================================================

# Typography (Cell Press Arial-first)
font.family: sans-serif
font.sans-serif: Arial, Helvetica, Helvetica Neue, DejaVu Sans
font.size: 8.0
mathtext.fontset: custom

# Axes & Spines
axes.linewidth: 0.5
axes.labelsize: 8.0
axes.labelpad: 2.0
axes.titlesize: 8.0
axes.titleweight: bold
axes.titlepad: 4.0
axes.spines.top: False
axes.spines.right: False
axes.edgecolor: black
axes.labelcolor: black
axes.xmargin: 0.05
axes.ymargin: 0.05

# Color cycle (Cell Press 10-color qualitative palette)
# In .mplstyle files, hex codes in cycler must omit the '#' character.
axes.prop_cycle: cycler('color', ['c84c3a', '2f7e8f', 'e1a22e', '4e5a8a', '5f9862', 'd07a6a', '8b6fa8', '7b8c9e', 'b85f7a', '6b6b6b'])

# Continuous Colormap (Perceptually uniform, avoiding gnuplot greyscale collapse)
image.cmap: viridis

# Ticks (compact, outward-facing)
xtick.labelsize: 7.0
xtick.major.size: 2.0
xtick.major.width: 0.6
xtick.major.pad: 1.0
xtick.color: black
xtick.bottom: True

ytick.labelsize: 7.0
ytick.major.size: 2.0
ytick.major.width: 0.6
ytick.major.pad: 1.0
ytick.color: black
ytick.left: True

# Legend (compact, unbordered)
legend.fontsize: 7.0
legend.title_fontsize: 8.0
legend.frameon: False
legend.handlelength: 0.7
legend.handleheight: 0.7
legend.handletextpad: 0.3
legend.markerscale: 0.5

# Figure canvas & Vector export (Cell Press standard: >=300 dpi, editable text)
figure.dpi: 144
savefig.dpi: 300
savefig.bbox: tight
savefig.pad_inches: 0.01
savefig.transparent: False
pdf.fonttype: 42
svg.fonttype: none
"""


def validate_style_file(path: Path) -> bool:
    try:
        import matplotlib.pyplot as plt

        plt.style.use(str(path))
        print(f"[OK] matplotlib successfully parsed {path}")
        print(f"     axes.linewidth  : {plt.rcParams['axes.linewidth']}")
        print(f"     font.sans-serif : {plt.rcParams['font.sans-serif']}")
        print(f"     prop_cycle len  : {len(plt.rcParams['axes.prop_cycle'])}")
        return True
    except (ValueError, OSError, RuntimeError) as e:
        print(f"[ERROR] Failed to load style from {path}: {e}", file=sys.stderr)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validate-only", action="store_true", help="Only validate existing file"
    )
    args = parser.parse_args()

    TARGET_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not args.validate_only:
        TARGET_FILE.write_text(STYLE_TEMPLATE, encoding="utf-8")
        print(f"[WROTE] {TARGET_FILE}")

    ok = validate_style_file(TARGET_FILE)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
