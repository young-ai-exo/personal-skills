#!/usr/bin/env python3
"""Dump the style contract cnsplots applies, read from the installed package.

Nothing here is hardcoded from documentation. Every value is measured from the
live `cnsplots.settings` object and from a real before/after diff of
`matplotlib.rcParams`, so the output is always true for the *installed*
version.

Sections:
  rcparams  diff of matplotlib.rcParams caused by cns.setup_matplotlib()
  settings  every public cns.settings field and its current value
  palettes  qualitative palette names that cns.palettes() accepts
  colors    module-level color constants (cns.RED, ...)
  greyscale CIE L* (perceptual lightness) for a discrete palette
  colormap  perceptual uniformity metrics for a continuous colormap

Usage:
  python3 dump_style.py                 # all sections, human readable
  python3 dump_style.py rcparams        # one section
  python3 dump_style.py greyscale       # palette_qual (default)
  python3 dump_style.py greyscale Ecotyper1
  python3 dump_style.py colormap gnuplot
  python3 dump_style.py colormap viridis
  python3 dump_style.py --markdown      # markdown tables, for reference docs
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

SECTIONS = ("rcparams", "settings", "palettes", "colors", "greyscale", "colormap")

# Candidate palette names probed against the installed package. Names that the
# installed cns.palettes() rejects are reported as unavailable rather than
# assumed present.
PALETTE_CANDIDATES = (
    # Qualitative
    "Ecotyper1", "Ecotyper2", "Ecotyper3", "Ecotyper4", "Ecotyper5", "Ecotyper6",
    "Cell", "Nature", "Science", "NEJM", "Tableau", "Bold", "ECharts",
    "Set1", "Set2", "Set3", "Pastel1", "Pastel2", "Paired", "Dark2", "Accent",
    # Sequential / diverging that palettes() also accepts
    "BlueRed", "BuRd_custom", "OrBu_custom", "WhYlOrRd_custom", "YlGnBu_custom",
    "parula",
    # Probed to confirm they are rejected: plain matplotlib colormap names
    "gnuplot", "viridis", "Blues",
)

COLOR_CONSTANTS = (
    "RED", "BLUE", "GREEN", "ORANGE", "PURPLE", "YELLOW",
    "PINK", "GRAY", "BROWN", "VIOLET", "CHOCOLATE",
)


def measure_rcparams() -> list[tuple[str, Any, Any]]:
    """Diff matplotlib.rcParams before and after cns.setup_matplotlib()."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib as mpl

    mpl.rcParams.update(mpl.rcParamsDefault)
    matplotlib.use("Agg")
    before = dict(mpl.rcParams)

    import cnsplots as cns

    cns.setup_matplotlib()
    after = dict(mpl.rcParams)

    rows = []
    for key in sorted(after):
        old, new = before.get(key), after[key]
        if str(old) == str(new) or key == "backend":
            continue
        rows.append((key, old, new))
    return rows


def collect_settings() -> list[tuple[str, Any]]:
    import cnsplots as cns

    out = []
    for name in sorted(dir(cns.settings)):
        if name.startswith("_"):
            continue
        value = getattr(cns.settings, name)
        if callable(value):
            continue
        out.append((name, value))
    return out


def palette_kinds() -> dict[str, str]:
    """Map palette name to 'qualitative' or 'continuous' from the registry.

    cnsplots 0.8.0 added ``available_palettes(kind)``, which enumerates the
    installed registry instead of relying on this file's hardcoded list. Older
    versions lack it, so fall back to probing the candidates below.
    """
    import cnsplots as cns

    kinds: dict[str, str] = {}
    if hasattr(cns, "available_palettes"):
        for kind in ("qualitative", "continuous"):
            for name in cns.available_palettes(kind):
                kinds[name] = kind
        return kinds

    for name in PALETTE_CANDIDATES:
        try:
            value = cns.palettes(name)
        except Exception:  # noqa: BLE001 - probing, any failure means unavailable
            continue
        kinds[name] = "continuous" if hasattr(value, "N") else "qualitative"
    return kinds


def probe_palettes() -> tuple[list[str], list[str]]:
    import cnsplots as cns

    seen: set[str] = set()
    names: list[str] = []
    for name in (*palette_kinds(), *PALETTE_CANDIDATES):
        if name not in seen:
            seen.add(name)
            names.append(name)

    ok, missing = [], []
    for name in names:
        try:
            cns.palettes(name)
        except Exception:  # noqa: BLE001 - probing, any failure means unavailable
            missing.append(name)
        else:
            ok.append(name)
    return ok, missing


def collect_colors() -> list[tuple[str, str]]:
    import cnsplots as cns

    return [(n, getattr(cns, n)) for n in COLOR_CONSTANTS if hasattr(cns, n)]


def srgb_to_Lstar(rgb):
    """Convert sRGB to CIE L* (perceptual lightness).
    
    rgb: array-like of shape (..., 3) with values in [0, 1].
    Returns L* in [0, 100], where 0 is black and 100 is white.
    """
    import numpy as np
    rgb = np.asarray(rgb)
    # Linearise sRGB
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    # Relative luminance Y (D65 illuminant)
    Y = 0.2126 * linear[..., 0] + 0.7152 * linear[..., 1] + 0.0722 * linear[..., 2]
    # CIE L*
    epsilon = (6 / 29) ** 3
    kappa = (29 / 3) ** 3
    f = np.where(Y > epsilon, np.cbrt(Y), (kappa * Y + 16) / 116)
    return 116 * f - 16


def check_greyscale(palette: str, count: int | None = None) -> tuple:
    """Report CIE L* (perceptual lightness) of a palette and flag close pairs.

    Series that differ only in hue collapse when printed in greyscale. This
    computes CIE L* for each entry and flags pairs within 5 L*, which are hard to
    tell apart without color. Replaces the old Rec. 601 luma with the rigorous
    perceptual measure.
    """
    import matplotlib.colors as mcolors
    import numpy as np

    import cnsplots as cns

    colors = cns.palettes(palette)
    if count:
        colors = list(colors)[:count]

    rows = []
    for index, color in enumerate(colors):
        rgb = np.array(mcolors.to_rgb(color))
        Lstar = float(srgb_to_Lstar(rgb))
        rows.append((index, mcolors.to_hex(color), Lstar))

    clashes = [
        (a[0], b[0], abs(a[2] - b[2]))
        for i, a in enumerate(rows)
        for b in rows[i + 1 :]
        if abs(a[2] - b[2]) < 5.0
    ]
    return rows, clashes


def check_colormap(name: str, samples: int = 64) -> dict:
    """Measure perceptual uniformity of a colormap across its range.
    
    Returns a dict with:
      samples: number of points sampled
      Lstar_range: (min, max) CIE L*
      monotonic: True if L* never decreases by more than 0.5
      step_cv: coefficient of variation of |ΔL*| between adjacent samples
      descending_steps: count of steps where L* drops by >0.5
      collisions: list of (data_a, data_b, delta_Lstar) for pairs >0.1 apart
                  in data space that are within 1 L* in greyscale
    """
    import matplotlib.pyplot as plt
    import numpy as np

    cmap = plt.get_cmap(name)
    xs = np.linspace(0, 1, samples)
    rgb = np.array(cmap(xs))[:, :3]
    Lstar = srgb_to_Lstar(rgb)
    
    d = np.diff(Lstar)
    monotonic = (d >= -0.5).all()
    descending = int((d < -0.5).sum())
    step_cv = float(np.std(np.abs(d)) / np.mean(np.abs(d)))
    
    collisions = [
        (round(xs[i], 2), round(xs[j], 2), round(abs(Lstar[i] - Lstar[j]), 2))
        for i in range(len(xs))
        for j in range(i + 8, len(xs))
        if abs(Lstar[i] - Lstar[j]) < 1.0
    ]
    
    return {
        "samples": samples,
        "Lstar_range": (round(float(Lstar.min()), 1), round(float(Lstar.max()), 1)),
        "monotonic": bool(monotonic),
        "step_cv": round(step_cv, 2),
        "descending_steps": descending,
        "collisions": len(collisions),
        "collision_examples": collisions[:5],
    }


def emit_plain(sections: tuple[str, ...], extra_args: list[str]) -> None:
    import cnsplots as cns

    print(f"cnsplots {cns.__version__}  python {sys.version.split()[0]}")

    if "rcparams" in sections:
        rows = measure_rcparams()
        print(f"\n== rcParams changed by setup_matplotlib() ({len(rows)}) ==")
        for key, old, new in rows:
            print(f"{key:<26} {old!r}  ->  {new!r}")

    if "settings" in sections:
        rows = collect_settings()
        print(f"\n== cns.settings ({len(rows)}) ==")
        for name, value in rows:
            print(f"{name:<32} {value!r}")

    if "palettes" in sections:
        ok, missing = probe_palettes()
        print(f"\n== palettes accepted ({len(ok)}) ==")
        print("  " + ", ".join(ok))
        if missing:
            print(f"== probed but unavailable ({len(missing)}) ==")
            print("  " + ", ".join(missing))

    if "colors" in sections:
        print("\n== color constants ==")
        for name, value in collect_colors():
            print(f"cns.{name:<10} {value}")

    if "greyscale" in sections:
        target = extra_args[0] if extra_args else cns.settings.palette_qual
        rows, clashes = check_greyscale(target)
        print(f"\n== greyscale separation: {target} ==")
        for index, hex_value, Lstar in rows:
            bar = "#" * max(1, round(Lstar / 100 * 40))
            print(f"  [{index}] {hex_value}  L*={Lstar:5.1f}  {bar}")
        if clashes:
            print(f"  pairs within 5 L* (hard to distinguish in greyscale): {len(clashes)}")
            for a, b, delta in clashes[:5]:
                print(f"    [{a}] vs [{b}]  ΔL*={delta:.1f}")
            if len(clashes) > 5:
                print(f"    ... and {len(clashes) - 5} more")
        else:
            print("  no pairs within 5 L*")

    if "colormap" in sections:
        target = extra_args[0] if extra_args else cns.settings.palette_seq
        result = check_colormap(target)
        print(f"\n== colormap uniformity: {target} ==")
        print(f"  L* range       : {result['Lstar_range'][0]:.1f} - {result['Lstar_range'][1]:.1f}")
        print(f"  monotonic      : {result['monotonic']}")
        print(f"  step CV        : {result['step_cv']:.2f}  (0 = perfectly uniform)")
        print(f"  descending     : {result['descending_steps']} / {result['samples']-1} steps")
        print(f"  collisions     : {result['collisions']} value pairs >0.1 apart within 1 L*")
        if result["collision_examples"]:
            print("  examples:")
            for a, b, dL in result["collision_examples"]:
                print(f"    data {a} vs {b} -> ΔL* {dL}")
        verdict = "uniform" if result["monotonic"] and result["step_cv"] < 0.35 else (
            "monotonic, uneven" if result["monotonic"] else "NON-monotonic")
        print(f"  verdict        : {verdict}")


def emit_markdown(sections: tuple[str, ...]) -> None:
    import cnsplots as cns

    print(f"<!-- generated by scripts/dump_style.py against cnsplots "
          f"{cns.__version__} -->")

    if "rcparams" in sections:
        print("\n### rcParams set by `setup_matplotlib()`\n")
        print("| rcParam | matplotlib default | cnsplots |")
        print("| --- | --- | --- |")
        for key, old, new in measure_rcparams():
            print(f"| `{key}` | `{old!r}` | `{new!r}` |")

    if "settings" in sections:
        print("\n### `cns.settings`\n")
        print("| Setting | Value |")
        print("| --- | --- |")
        for name, value in collect_settings():
            print(f"| `{name}` | `{value!r}` |")

    if "palettes" in sections:
        ok, _ = probe_palettes()
        print("\n### Qualitative palettes\n")
        print(", ".join(f"`{n}`" for n in ok))

    if "colors" in sections:
        print("\n### Color constants\n")
        print("| Name | Hex |")
        print("| --- | --- |")
        for name, value in collect_colors():
            print(f"| `cns.{name}` | `{value}` |")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("section", nargs="?", choices=SECTIONS,
                        help="section to dump (default: all)")
    parser.add_argument("args", nargs="*",
                        help="arguments for greyscale (palette name) or colormap (colormap name)")
    parser.add_argument("--markdown", action="store_true",
                        help="emit markdown tables for reference docs")
    args = parser.parse_args()

    try:
        import cnsplots  # noqa: F401
    except ImportError:
        print("cnsplots is not importable in this interpreter; "
              "run scripts/check_env.py", file=sys.stderr)
        return 1

    sections = (args.section,) if args.section else SECTIONS
    if args.markdown:
        emit_markdown(sections)
    else:
        emit_plain(sections, args.args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
