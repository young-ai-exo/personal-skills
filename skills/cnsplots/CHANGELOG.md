# Changelog

All notable changes to the `cnsplots` skill. Versions follow SemVer.

This file continues the history of the former v1 skill (`skills/cnsplots`,
1.0.0–1.8.0) and v2 skill (`skills/cnsplots-v2`, 2.0.0). Both were removed when
v3 became the single, canonical skill under `skills/cnsplots`; the version
number deliberately stays on the 3.x line.

## [3.0.5] — 2026-11-02

Re-tuned both vendored upstream showcases to the skill's 360 dpi house style
and removed the remaining v3 naming from the package.

### Changed
- Both showcases now use the Cell palette, viridis, the Arial-first font stack,
  opaque backgrounds, explicit `unit="pt"`, and 360 dpi for display and export.
- Pixel-based `pad_left` / `pad_top` values are scaled by `360 / 144 = 2.5`, so
  the upstream physical geometry is preserved. Point-based `margin_*` values are
  unchanged.
- Figure 1 panel R grows to 110 pt; its heatmap legends are reordered
  (`Z-score`, `Ensemble`, `blobs`), widened, and spaced, and the colorbar keeps
  only endpoint ticks.
- Figure 2 panel C grows to 130 pt with 45° x tick labels and a larger legend
  gap; panel J uses 90° x tick labels so the day labels fit; the placeholder
  glyph changes from `⨯` to `×` for Arial coverage.
- The skill directory and all internal names are now `cnsplots`, not
  `cnsplots-v3`. The version remains 3.0.5.

### Fixed
- cnsplots 0.8.0 re-runs multipanel layout on every draw. Exporting at a dpi
  different from the build canvas made that relayout use stale text bounding
  boxes and shifted whole panels. Both scripts now detach the draw handler
  after the layout converges and before saving.
- Regenerated the checked-in Figure 1 and Figure 2 PDF/SVG artifacts.

### Verified
- `ruff check`, `ruff format --check`, `ty check` on the non-vendored Python,
  and `export_mplstyle.py --check` for Cell-palette drift.
- PDFs rendered with Ghostscript and SVGs rendered in Chrome; both match.
  sips/Quick Look mis-renders the live SVG text, so it is not a valid SVG
  verification tool for these files.

## [3.0.0 – 3.0.4] — 2026-11-01 → 2026-11-02

The v3 rewrite: a closed-loop workflow, an explicit 100 pt sizing contract, a
single house style, and dual execution modes.

- **3.0.0** — Replaced the reference-manual structure with the 6-step workflow
  (bootstrap → profile data → choose layout → build at ~100 pt → extract
  statistics → validate artifact). Added the no-font/marker-blow-up rule,
  `hue_order` vs `order`, the 100 pt panel baseline, and Mode A/B execution.
- **3.0.1** — Encapsulated the house style in `apply_house_style()`: Cell
  palette, viridis, Arial-first stack, PDF/SVG font types, opaque background,
  and 360 dpi.
- **3.0.2** — Generated `styles/cns_cell.mplstyle` and `styles/cell_colors.py`
  from `cns.palettes("Cell")` and added the `--check` drift test. Vendored the
  official Figure 1 and Figure 2 showcases with the official data preamble,
  pt units, and PDF/SVG output.
- **3.0.3** — Intermediate documentation revision, folded into 3.0.4.
- **3.0.4** — Unified display, preview, and export at 360 dpi; made `unit="pt"`
  explicit in `cns.figure()` and `cns.multipanel()`; renamed the sizing
  reference to `panel-sizing-100pt.md`; documented matplotlib 3.10 vs 3.11
  `figsize` units; standardized PDF as the primary artifact with SVG for
  editing and PNG for preview.

## [2.0.0] — 2026-11-01

Major revision of the v1 skill. Introduced the compact `SKILL.md` + focused
references layout and the dual-mode execution model that v3 inherits.

### Added
- Standalone `styles/cns_cell.mplstyle` and `cell_colors.py` for
  zero-dependency matplotlib/seaborn use.
- Proactive environment branching: install `cnsplots` (Mode A) or copy the
  style sheet and use pure matplotlib/seaborn (Mode B).
- The ~100 px/pt panel sizing baseline (80, 100, 120, 150) and a ban on manual
  font and marker overrides.
- Cell Press 10-color palette as the house qualitative palette, with Nature and
  Science presets.
- Arial-first typography across the workflow and templates.
- A streamlined `styles/`, `scripts/`, `templates/`, and `references/`
  structure with redundant v1 files removed.

## [1.8.0] — 2026-10-26

Tracks `cnsplots` 0.8.0, a units-and-export release: dimensions are documented
as points (1/72 inch), `figure()` returns the `Figure`, and `savefig()` gained
explicit export controls. Numerical geometry did not change.

- Documented `savefig(fig=, dpi=, transparent=, bbox_inches=, pad_inches=)` and
  the canvas-vs-tight-crop distinction (a 519 pt canvas holding one 240×150
  panel saves at 94.4 mm tight vs 183.1 mm with `bbox_inches=None`).
- Documented `unit="pt"|"in"|"mm"` and the fact that `pad_left`/`pad_top` stay
  in display pixels while margins stay in points.
- Added the statistics accessors (`get_comparison_results`,
  `get_survival_results`, `get_roc_results`, `get_precision_recall_results`,
  `get_calibration_results`) and the paired `test=`/`subject=` options.
- Added `precisionrecallplot` and `calibrationplot`; documented
  `available_palettes`, `register_palette`, and `get_palette_colors`.
- Documented `settings.context()`, fixed `mp.newline()` semantics, corrected
  `Ecotyper1` membership, and corrected the claim that diverging colormap names
  work as `color_cycle`.
- `journal_preset.py --code` now emits `max_width=<mm>, unit="mm"` with
  `bbox_inches=None`; verified 183 mm in, 183.0 mm out.
- Conformance pass: `$SKILL_DIR` helper paths, reference tables of contents,
  and removal of an accidental `__pycache__`.

## [1.7.0] — 2026-09-01

- Recommended overriding the installed `palette_seq="gnuplot"` with `viridis`
  and the Helvetica-first stack with Arial-first.
- Replaced the Rec. 601 luma approximation with CIE L* measurements for
  greyscale separability. `gnuplot` is non-monotonic (CV 0.66, 39 collisions);
  `viridis` is monotonic (CV 0.07, zero collisions).
- Added `scripts/recommended_overrides.py` and a `dump_style.py colormap` mode.
- Documented that `multipanel_max_width=540` exceeds all three journals' widest
  columns and that the installed Helvetica-first stack embeds Helvetica rather
  than Cell-required Arial.

## [1.6.0] — 2026-09-01

Added Cell/Nature/Science figure specifications: column widths, type sizes,
line weights, resolution, and journal presets.

## [1.5.0] — 2026-09-01

Explained multipanel's draw handler and corrected two long-standing claims
about panel decoration measurement and UpSet placement.

## [1.4.0] — 2026-09-01

Added cross-panel color strategy: palette assignment, category order, and
greyscale/color-vision checks.

## [1.3.0] — 2026-09-01

Vendored the upstream showcase source and tightened the dense-figure template.

## [1.2.0] — 2026-09-01

Added dense journal-figure techniques: negative offsets, embedded raster
images, composite plotter axes, and reworking generated annotations.

## [1.1.0] — 2026-09-01

Added the rcParams style contract and the grid/multipanel/GridSpec layout
patterns.

## [1.0.0] — 2026-08-12

Initial `cnsplots` skill: versioning, provenance, helper scripts, and the
documentation site.
