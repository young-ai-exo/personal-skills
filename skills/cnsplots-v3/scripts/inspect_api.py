#!/usr/bin/env python3
"""Print installed signatures and docstrings for public cnsplots functions.

Usage:
    python3 inspect_api.py boxplot scatterplot multipanel
    python3 inspect_api.py --list
"""

from __future__ import annotations

import inspect
import sys

try:
    import cnsplots as cns
except ModuleNotFoundError:
    sys.exit("cnsplots is not installed; run check_env.py first.")


def show(name: str) -> None:
    obj = getattr(cns, name, None)
    if obj is None:
        print(f"!! {name}: not a public cnsplots attribute")
        return

    print("=" * 72)
    try:
        print(f"{name}{inspect.signature(obj)}")
    except (TypeError, ValueError):
        print(f"{name}: <no introspectable signature> ({type(obj)})")
    print("-" * 72)
    print(inspect.getdoc(obj) or "<no docstring>")
    print()


def main(argv: list[str]) -> int:
    print(f"cnsplots {cns.__version__}\n")

    if not argv or argv[0] in {"--list", "-l"}:
        for name in sorted(getattr(cns, "__all__", [])):
            print(name)
        return 0

    for name in argv:
        show(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
