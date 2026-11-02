# Upstream cnsplots showcase sources

Vendored source for the two official cnsplots gallery figures:

- `figure1.py` — 18 panels covering most plot functions, `max_width=485`
- `figure2.py` — 13 panels including micrographs, composite plotters, and an
  embedded UpSet plot, `max_width=540`

Source: <https://cnsplots.farid.one/latest/examples/showcase.html>  
Copyright Farid Rashidi, BSD-3-Clause. These are **reference material, not our
work**; when this directory and the upstream page disagree, the upstream page
wins.

## Adaptations for this skill

Only the following changes were made:

- `cns.multipanel(..., unit="pt")` is explicit; panel widths/heights were
  already in points.
- `savefig_dpi = 360` and `savefig_transparent = False`; final files are SVG.
- `figure_dpi` is pinned to **144** because the upstream showcase uses
  pixel-based `pad_left` / `pad_top` offsets tuned for that display dpi.
  Setting `figure_dpi = 360` changes those offsets and breaks panel placement.
  The skill's own templates use 360 display/export; this directory is the
  documented exception.
- `figure2.py` adds `import numpy as np` for the `np.log(marker)` term in the
  Cox model.

All other code, offsets, and manual styling are upstream and intentionally
left alone.

## Preamble

Both scripts include the official load-data and helper preamble:

- `cns.datasets.get_showcase_data(include_showcase_images=True)` loads all
  DataFrames and the micrograph directory.
- `_read_showcase_image()` reads the packaged images.
- `_embed_detached_axes()` repositions the detached UpSet axes.

`figure2.py` additionally imports `numpy as np` for the `np.log(marker)` term.

## Running

The scripts need the showcase data (including the micrograph images) that
ships with cnsplots, plus `scipy`:

```bash
cd /tmp
CNSPLOTS_GALLERY_OUTPUT_DIR=/tmp/showcase \
  python3 <SKILL_DIR>/templates/upstream-showcase/figure1.py

CNSPLOTS_GALLERY_OUTPUT_DIR=/tmp/showcase \
  python3 <SKILL_DIR>/templates/upstream-showcase/figure2.py
```

Without `CNSPLOTS_GALLERY_OUTPUT_DIR`, outputs go next to the scripts.

Outputs per script: a PDF and an SVG. PDF is the primary artifact; SVG is kept
for editing. Both use `bbox_inches=None` so the canvas width is preserved.

## Caveats

- These are **not house-style templates**. They intentionally use manual
  `pad_left` / `pad_top` / `margin_*` offsets, `fontsize=6`, `s=1`, and other
  upstream overrides. Use the four top-level templates for the skill's style.
- The pixel/font-metric-tuned layout can differ from the online gallery on a
  different machine. The previous vendoring noted overlapping heatmap legends
  in Figure 1; re-tune `legend_hpad` / `legend_hgap` / `legend_width` if needed.
- `figure1.py` and `figure2.py` call `cns.utils._capture_detached_axes_layout`,
  a private helper still present in cnsplots 0.8.0. Prefer the public pattern
  in the top-level templates for new code.
- Without `mutool`, `cns.savefig` falls back to a standard matplotlib SVG; the
  output is still readable, but the Illustrator-oriented SVG path is not used.
