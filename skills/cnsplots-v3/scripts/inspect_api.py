#!/usr/bin/env python3
"""Print installed signatures and docstrings for public cnsplots functions.

Uses stdout directly instead of loguru so the output stays clean and the
tool works in any environment where cnsplots is importable.

Usage:
    python3 inspect_api.py boxplot scatterplot multipanel
    python3 inspect_api.py --list
"""

from __future__ import annotations

import inspect
import sys

import cnsplots as cns


def emit(message: str = "") -> None:
    """Write one line to stdout without requiring a logging dependency."""
    sys.stdout.write(f"{message}\n")


def show(name: str) -> None:
    """Print the signature and docstring for one public cnsplots attribute."""
    obj = getattr(cns, name, None)
    if obj is None:
        emit(f"!! {name}: not a public cnsplots attribute")
        return

    emit("=" * 72)
    try:
        emit(f"{name}{inspect.signature(obj)}")
    except (TypeError, ValueError):
        emit(f"{name}: <no introspectable signature> ({type(obj)})")
    emit("-" * 72)
    emit(inspect.getdoc(obj) or "<no docstring>")
    emit()


def main(argv: list[str]) -> int:
    """Print signatures for the requested names, or list all public names."""
    emit(f"cnsplots {cns.__version__}\n")

    if not argv or argv[0] in {"--list", "-l"}:
        for name in sorted(getattr(cns, "__all__", [])):
            emit(name)
        return 0

    for name in argv:
        show(name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
