#!/usr/bin/env python3
"""Print cnsplots figure dimensions and style overrides for a target journal.

Converts published column widths into the point values cnsplots expects
(1 pt = 1/72 inch) and reports where the package defaults violate the journal's
stated limits.

The numbers come from the publishers' author pages as read in September 2026 and
are documented with sources in references/journal-specs.md. Publishers revise
these; confirm against the journal's current page before submitting.

A journal width is a canvas width: the default `savefig_bbox='tight'` crops the
saved file to its artists, so use `cns.savefig(..., bbox_inches=None)` when the
printed width must match the column width.

Usage:
  python3 journal_preset.py                 # all journals
  python3 journal_preset.py nature          # one journal
  python3 journal_preset.py nature --code   # emit a settings.context block
"""

from __future__ import annotations

import argparse

PT_PER_INCH = 72.0
MM_PER_INCH = 25.4

# Published limits. font/line are (min, max) in pt; None means not stated.
JOURNALS: dict[str, dict] = {
    "cell": {
        "label": "Cell Press",
        "widths_mm": {"1-column": 85, "1.5-column": 114, "2-column": 174},
        "max_height_mm": 200,
        "font_pt": (6, 8),
        "line_pt": (0.5, 1.5),
        "dpi_min": 300,
        "dpi_note": "500 for B&W and combination art, 1000 for raster line art",
        "panel_labels": "capital A, B, C",
        "typeface": "Arial",
        "vector": "PDF or EPS preferred",
    },
    "nature": {
        "label": "Nature",
        "widths_mm": {"1-column": 89, "1.5-column": 120, "2-column": 183},
        "max_height_mm": 170,
        "font_pt": (5, 7),
        "line_pt": (0.25, 1.0),
        "dpi_min": 300,
        "dpi_note": "300-600 for photographic; vector required for main figures",
        "panel_labels": "8 pt bold LOWERCASE a, b, c",
        "typeface": "Helvetica or Arial",
        "vector": ".ai/.eps/.pdf with editable layers REQUIRED; no jpeg/tiff/png",
    },
    "science": {
        "label": "Science",
        "widths_mm": {"1-column": 57, "2-column": 121, "3-column": 184},
        "max_height_mm": None,
        "font_pt": (5, 7),
        "line_pt": (0.5, None),
        "dpi_min": 300,
        "dpi_note": "300 for line art, grayscale and colour alike",
        "panel_labels": "10 pt bold capital A, B, C, upper left",
        "typeface": "Helvetica preferred",
        "vector": "PDF, EPS or AI preferred",
    },
}


def mm_to_pt(mm: float) -> int:
    return round(mm / MM_PER_INCH * PT_PER_INCH)


def describe(key: str, spec: dict) -> None:
    import cnsplots as cns

    print(f"\n=== {spec['label']} ===")
    print("  widths (max_width / figure width):")
    for name, mm in spec["widths_mm"].items():
        print(f"    {name:<12} {mm:>4} mm  ->  {mm_to_pt(mm):>4} pt")
    if spec["max_height_mm"]:
        mm = spec["max_height_mm"]
        print(f"    {'max height':<12} {mm:>4} mm  ->  {mm_to_pt(mm):>4} pt")
    else:
        print(f"    {'max height':<12} not stated")

    print(f"  typeface      : {spec['typeface']}")
    print(f"  panel labels  : {spec['panel_labels']}")
    print(f"  vector format : {spec['vector']}")

    font_min, font_max = spec["font_pt"]
    line_min, line_max = spec["line_pt"]
    print(f"  font in figure: {font_min}-{font_max} pt")
    print(f"  line weight   : {line_min}-{line_max or 'unstated'} pt")
    print(f"  resolution    : >= {spec['dpi_min']} dpi ({spec['dpi_note']})")

    # Compare against the installed defaults rather than assuming them.
    print("  installed cnsplots defaults vs this journal:")
    title = cns.settings.title_fontsize
    legend = cns.settings.legend_fontsize
    line = cns.settings.axes_linewidth
    dpi = cns.settings.savefig_dpi

    def verdict(ok: bool) -> str:
        return "ok" if ok else "VIOLATES"

    print(f"    title_fontsize  = {title:<5} {verdict(font_min <= title <= font_max)}")
    print(f"    legend_fontsize = {legend:<5} {verdict(font_min <= legend <= font_max)}")
    line_ok = line >= line_min and (line_max is None or line <= line_max)
    print(f"    axes_linewidth  = {line:<5} {verdict(line_ok)}")
    print(f"    savefig_dpi     = {dpi:<5} {verdict(dpi >= spec['dpi_min'])}")


def emit_code(key: str, spec: dict) -> None:
    import cnsplots as cns

    font_min, font_max = spec["font_pt"]
    title = min(cns.settings.title_fontsize, font_max)
    legend = min(cns.settings.legend_fontsize, max(font_min, font_max - 1))
    dpi = max(cns.settings.savefig_dpi, spec["dpi_min"])
    # Prefer a whole multiple of 72 at or above the journal floor.
    dpi = ((int(dpi) + 71) // 72) * 72
    widest = max(spec["widths_mm"].values())
    lower = spec["panel_labels"].lower().startswith("8 pt bold lowercase")

    print(f"# {spec['label']}: {spec['typeface']}, {font_min}-{font_max} pt, "
          f">= {spec['dpi_min']} dpi")
    print(f"with cns.settings.context(title_fontsize={title}, "
          f"legend_fontsize={legend}, savefig_dpi={dpi}):")
    print(f'    mp = cns.multipanel(max_width={widest}, unit="mm")'
          f"  # {widest} mm, widest column")
    print(f'    ax = mp.panel("{"a" if lower else "A"}", 240, 150)'
          f"  # {spec['panel_labels']}")
    print("    ...")
    print('    # bbox_inches=None keeps the full canvas; default tight cropping')
    print('    # would save narrower than the column width above.')
    print('    cns.savefig("figure1.pdf", bbox_inches=None)'
          '  # vector keeps text editable')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("journal", nargs="*", choices=sorted(JOURNALS),
                        help="journal key (default: all)")
    parser.add_argument("--code", action="store_true",
                        help="emit a settings.context block instead of a table")
    args = parser.parse_args()

    try:
        import cnsplots  # noqa: F401
    except ImportError:
        print("cnsplots is not importable; run scripts/check_env.py")
        return 1

    keys = args.journal or sorted(JOURNALS)
    for key in keys:
        if args.code:
            emit_code(key, JOURNALS[key])
        else:
            describe(key, JOURNALS[key])

    if not args.code:
        print("\nWidths are points at 72/inch: mm = pt / 72 * 25.4")
        print("Sources and caveats: references/journal-specs.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
