#!/usr/bin/env python3
"""Environment and capability probe for cnsplots-v2 skill.

Detects whether native cnsplots (Mode A) is available or if fallback to
bundled cns_cell.mplstyle (Mode B) should be used.

Usage:
    python3 check_env.py
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
MPLSTYLE_PATH = SKILL_DIR / "styles" / "cns_cell.mplstyle"


def check_module(name: str) -> tuple[bool, str]:
    try:
        mod = importlib.import_module(name)
        ver = getattr(mod, "__version__", "ok")
        return True, str(ver)
    except ImportError:
        return False, "MISSING"


def main() -> int:
    print(f"python      : {sys.version.split()[0]}")
    print(f"executable  : {sys.executable}")

    cns_ok, cns_ver = check_module("cnsplots")
    _, mpl_ver = check_module("matplotlib")
    _, sns_ver = check_module("seaborn")
    _, pd_ver = check_module("pandas")
    _, np_ver = check_module("numpy")

    print(
        f"cnsplots    : {cns_ver} {'(Mode A: Native available)' if cns_ok else '(NOT installed)'}"
    )
    print(f"matplotlib  : {mpl_ver}")
    print(f"seaborn     : {sns_ver}")
    print(f"pandas      : {pd_ver}")
    print(f"numpy       : {np_ver}")

    style_exists = MPLSTYLE_PATH.is_file()
    print(f"mplstyle    : {'found' if style_exists else 'MISSING'} ({MPLSTYLE_PATH})")

    mutool = shutil.which("mutool")
    print(
        f"mutool      : {'found at ' + mutool if mutool else 'missing (SVG falls back to plain matplotlib)'}"
    )

    print("\n--- Execution Mode Status ---")
    if cns_ok:
        print("[READY] Mode A: Full cnsplots active.")
        print("  Can use cns.multipanel(), cns.figure(), auto statistical annotations.")
        print(
            "  Default palette: cns.settings.palette_qual = 'Cell' (Nature/Science/etc. also supported)"
        )
        print(
            "  Default font   : cns.settings.font_sans_serif = ('Arial', 'Helvetica', ...)"
        )
        return 0
    else:
        print("[FALLBACK] cnsplots is not installed.")
        print(
            "  Mode B is available using pure matplotlib / seaborn with cns_cell.mplstyle."
        )
        print("\nACTION REQUIRED for Agent:")
        print("  Prompt the user with the following choice before proceeding:")
        print("  '检测到当前 Python 环境未安装 cnsplots 包。请问您希望：'")
        print(
            "  '  1. (推荐) 安装 cnsplots (pip install cnsplots)，获得自动多子图排版与统计标注？'"
        )
        print(
            "  '  2. 使用内置导出的出版级样式表 (cns_cell.mplstyle)，通过原生 matplotlib / seaborn 绘制顶刊出版风格图表（默认采用 Cell 样式，无需安装新包）？'"
        )
        return 1


if __name__ == "__main__":
    import importlib

    sys.exit(main())
