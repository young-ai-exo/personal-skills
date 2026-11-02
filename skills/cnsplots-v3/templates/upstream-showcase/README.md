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

The upstream layout is tuned for 144 display dpi. To run it at the skill's
360 dpi house style, the following changes were made:

- `cns.multipanel(..., unit="pt")` is explicit; panel widths/heights were
  already in points.
- House style is applied in each script: Cell qualitative palette, viridis
  continuous palette, Arial-first font stack, `panel_label_fontname=None`,
  PDF/SVG font types, opaque background, and 360 display/export dpi.
- Pixel-based `pad_left` / `pad_top` values are multiplied by
  `360 / 144 = 2.5`, so their physical offsets match the upstream layout.
  Point-based `margin_*` values are unchanged.
- Figure 1 panel R grows from 90 to 110 pt. Its heatmap legends are reordered
  (`Z-score`, `Ensemble`, `blobs`), widened, and spaced so the three legend
  blocks no longer overlap; the colorbar shows endpoint ticks only.
- Figure 2 panel C grows from 90 to 130 pt and uses 45° x tick labels and a
  larger legend gap. Panel J rotates its x tick labels to 90° so the four day
  labels fit in the narrow panel.
- The Figure 2 placeholder uses `×` instead of `⨯`, because Arial has no glyph
  for U+2A2F.
- `figure2.py` adds `import numpy as np` for the `np.log(marker)` term in the
  Cox model.

The remaining code, offsets, and manual styling are upstream and intentionally
left alone.

## Export workaround

cnsplots 0.8.0 re-measures the multipanel layout on every draw. If
`cns.savefig` exports at a different dpi than the canvas used to build the
layout, that relayout runs with stale text bounding boxes and shifts entire
panels. Both scripts therefore disconnect the multipanel draw handler after
the layout has converged and before saving. This is a library workaround, not
a style choice.

Because of the same relayout behavior, run these scripts with the default
matplotlib backend. Forcing `Agg` changes cnsplots's pixel measurements and
can change the row wrapping; the checked-in PDFs were generated with the
macOS backend.

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
for editing. Both use `bbox_inches=None` so the canvas size is preserved.
Checked-in canvases: Figure 1 is 479.8 × 578.9 pt (169.3 × 204.3 mm);
Figure 2 is 530.1 × 611.3 pt (187.0 × 215.7 mm).

## Caveats

- These are **not house-style templates**. They intentionally use manual
  `pad_left` / `pad_top` / `margin_*` offsets, `fontsize=6`, `s=1`, and other
  upstream overrides. Use the four top-level templates for the skill's style.
- Figure layout can still differ slightly across machines because the upstream
  design depends on font metrics and pixel offsets. Re-tune `legend_*` or
  `pad_*` if a label collides on another platform.
- `figure1.py` and `figure2.py` call `cns.utils._capture_detached_axes_layout`,
  a private helper still present in cnsplots 0.8.0. Prefer the public pattern
  in the top-level templates for new code.
- The upstream code has nullability warnings under `ty check` (for example,
  `ax.get_legend()` can return `None`). They are left as upstream wrote them;
  only the export workaround is type-checked.
- Without `mutool`, `cns.savefig` falls back to a standard matplotlib SVG; the
  output is still readable, but the Illustrator-oriented SVG path is not used.
