#!/usr/bin/env python3
"""Environment and capability probe for the cnsplots-v3 skill.

Runs with the standard library only, so it can report on an environment
before cnsplots, matplotlib, seaborn, or loguru are installed. It uses stdout
directly instead of loguru for that bootstrap reason.

Usage:
    python3 check_env.py
"""

from __future__ import annotations

import importlib
import pathlib
import shutil
import sys

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
MPLSTYLE_PATH = SKILL_DIR / "styles" / "cns_cell.mplstyle"


def emit(message: str = "") -> None:
    """Write one line to stdout without requiring a logging dependency."""
    sys.stdout.write(f"{message}\n")


def check_module(name: str) -> tuple[bool, str]:
    """Return whether a module imports and its version string."""
    try:
        module = importlib.import_module(name)
    except ImportError:
        return False, "MISSING"
    return True, str(getattr(module, "__version__", "ok"))


def main() -> int:
    """Report Mode A / Mode B readiness; exit non-zero only when neither is usable."""
    emit(f"python      : {sys.version.split()[0]}")
    emit(f"executable  : {sys.executable}")

    cns_ok, cns_ver = check_module("cnsplots")
    mpl_ok, mpl_ver = check_module("matplotlib")
    sns_ok, sns_ver = check_module("seaborn")
    _, pd_ver = check_module("pandas")
    _, np_ver = check_module("numpy")

    cns_status = "(Mode A: native available)" if cns_ok else "(NOT installed)"
    emit(f"cnsplots    : {cns_ver} {cns_status}")
    emit(f"matplotlib  : {mpl_ver}")
    emit(f"seaborn     : {sns_ver}")
    emit(f"pandas      : {pd_ver}")
    emit(f"numpy       : {np_ver}")

    style_status = "found" if MPLSTYLE_PATH.is_file() else "MISSING"
    emit(f"mplstyle    : {style_status} ({MPLSTYLE_PATH})")

    mutool = shutil.which("mutool")
    mutool_status = (
        f"found at {mutool}"
        if mutool
        else "missing (SVG falls back to plain matplotlib)"
    )
    emit(f"mutool      : {mutool_status}")

    emit("\n--- Execution Mode Status ---")
    if cns_ok:
        emit("[READY] Mode A: full cnsplots available.")
        emit("  Package default palette: Ecotyper1; skill house style: Cell.")
        emit("  Package default font: Helvetica-first; skill house style: Arial-first.")
        return 0

    if mpl_ok:
        emit("[READY] Mode B: pure matplotlib available with cns_cell.mplstyle.")
        seaborn_status = (
            "available" if sns_ok else "MISSING (seaborn template unavailable)"
        )
        emit(f"  seaborn: {seaborn_status}")
        emit("  Copy styles/cns_cell.mplstyle into the project before running Mode B.")
        emit("  See SKILL.md Step 1 for the Mode A vs Mode B choice.")
        return 0

    emit("[BLOCKED] Neither cnsplots nor matplotlib is importable.")
    emit("  Install cnsplots (Mode A) or matplotlib (Mode B) before plotting.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
