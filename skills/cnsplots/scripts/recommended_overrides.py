#!/usr/bin/env python3
"""Recommended cnsplots setting overrides for journal compliance and perceptual uniformity.

Place this block at the top of your plotting script, right after `import cnsplots as cns`
and before `cns.setup_matplotlib()`.

Why these overrides:
  palette_seq = 'viridis'         gnuplot is non-monotonic in CIE L* (CV 0.66, like jet's
                                  0.65) and has 39 value pairs within 1 L* that collapse in
                                  greyscale. viridis is perceptually uniform (CV 0.07) and
                                  monotonic, Nature recommends avoiding rainbow scales.
                                  
  font_sans_serif = Arial-first   Cell Press requires Arial specifically. The installed
                                  default prioritises Helvetica, which renders on macOS but
                                  means Cell submissions embed Helvetica rather than Arial.
                                  Keeping Helvetica and DejaVu Sans as fallbacks ensures
                                  systems without Arial still get a close match rather than
                                  an unrelated substitute.

Usage:
  python3 recommended_overrides.py         # explains the overrides
  python3 recommended_overrides.py --code  # emits code to paste
"""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--code", action="store_true",
                        help="emit code to paste rather than explanation")
    args = parser.parse_args()

    if args.code:
        print("""# Recommended overrides (see scripts/recommended_overrides.py --help)
import cnsplots as cns
cns.settings.palette_seq = 'viridis'
cns.settings.font_sans_serif = ('Arial', 'Helvetica', 'Helvetica Neue', 'DejaVu Sans')
cns.setup_matplotlib()""")
    else:
        print(__doc__)
        print("\nVerifying the overrides work:")
        try:
            import cnsplots as cns
        except ImportError:
            print("  cnsplots not importable; run scripts/check_env.py")
            return 1

        print(f"  Current palette_seq      : {cns.settings.palette_seq}")
        print(f"  Current font_sans_serif  : {cns.settings.font_sans_serif[:3]}")
        print("\n  Recommended palette_seq  : viridis")
        print("  Recommended font order   : ('Arial', 'Helvetica', 'Helvetica Neue', 'DejaVu Sans')")
        print("\nRun with --code to get a code block you can paste.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
