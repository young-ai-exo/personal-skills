---
name: cnsplots
description: Generate, revise, and debug publication-quality scientific figures in Python with the cnsplots package (Cell/Nature/Science styling, precise physical figure dimensions, built-in statistical annotations, editable SVG/PDF export). Also covers applying the cnsplots style to plain matplotlib, seaborn, or scanpy axes, repeated grid panels, heterogeneous multi-panel layouts, and the rcParams contract for custom artists. Use when a user asks for cnsplots code, journal-style plots, multi-panel or grid figures, survival/volcano/GSEA/ROC/heatmap plots, or Illustrator-editable vector figure output.
---

# cnsplots

Produce a runnable script that plots the user's real data with `cnsplots` and
saves a verified artifact. Never hand back untested plotting code.

Docs: <https://cnsplots.farid.one/latest/api.html> · Gallery:
<https://cnsplots.farid.one/latest/examples/index.html>

## Bundled scripts

The helper scripts live next to this file. Invoke them with paths relative
to this skill's directory (written as `$SKILL_DIR` below), not the user's
project root:

- `$SKILL_DIR/scripts/check_env.py` — environment and dependency probe
- `$SKILL_DIR/scripts/inspect_api.py` — installed signatures and docstrings
- `$SKILL_DIR/scripts/dump_style.py` — measured rcParams, settings, palettes, colors
- `$SKILL_DIR/scripts/recommended_overrides.py` — Arial-first font order and viridis
  sequential colormap overrides, with measured perceptual-uniformity reasoning;
  `--code` emits a ready block to paste at script top
- `$SKILL_DIR/scripts/journal_preset.py` — Cell/Nature/Science figure limits in
  points, and which installed defaults violate them; `--code` emits a ready
  `settings.context(...)` block
- `$SKILL_DIR/scripts/validate_output.py` — post-save artifact validation

## Bundled templates

Each runs unmodified on a built-in dataset, then adapts via its `CONFIGURE`
block. Start from one instead of writing a layout from scratch:

- `$SKILL_DIR/templates/mpl_grid_repeat.py` — uniform grid, one plot type
- `$SKILL_DIR/templates/multipanel_heterogeneous.py` — labeled A/B/C figure
- `$SKILL_DIR/templates/mixed_grid_in_panel.py` — aligned grid inside a labeled figure
- `$SKILL_DIR/templates/dense_figure.py` — showcase-style dense figure: per-panel
  palettes, `below=` interlocking, negative offsets, embedded image, composite
  plotters, embedded upsetplot
- `$SKILL_DIR/templates/upstream-showcase/` — the upstream showcase Figure 1 and
  Figure 2 source, vendored verbatim. Consult when a distilled rule looks wrong;
  these files are authoritative over our prose.

## Hard rules

- `import cnsplots as cns` and use only public `cns.*` names. Never import
  `cnsplots._utils`, `cnsplots.plots._distribution`, or any other private module.
- Verify every function signature against the *installed* version before writing
  final code (step 2). The API changes between releases; do not trust memory.
- Sizes in `cns.figure()` / `mp.panel()` are **points (1/72 inch)**, not inches.
  Pass `unit="in"` or `unit="mm"` for physical dimensions; an omitted dimension
  uses its `cns.settings` value in points regardless of `unit`. Display DPI is
  144 (so a 200-pt figure shows a 400-px canvas); export DPI is 288.
- Never invent data, labels, units, group orders, thresholds, or statistical
  tests. If a choice changes scientific meaning and cannot be inferred, ask.
- One palette per figure, and one color per meaning. Pass `hue_order` on every
  panel sharing a categorical variable, or the same category drifts color between
  panels. See [references/color-strategy.md](references/color-strategy.md).
- When a target journal is known, size the figure to its column width and apply
  its type and resolution limits. Two package defaults are **not** universally
  compliant: `title_fontsize=8` exceeds Nature's 7 pt cap, and `savefig_dpi=288`
  is below the 300 dpi floor Cell, Nature, and Science all require. Run
  `python3 $SKILL_DIR/scripts/journal_preset.py <journal>` and see
  [references/journal-specs.md](references/journal-specs.md).
- Never hardcode a style value the package already sets. Inherit it, or read it
  from `mpl.rcParams` / `cns.settings`. See
  [references/rcparams.md](references/rcparams.md).
- Do not build a visual grid by calling `mp.panel()` per cell; multipanel does
  not align panel edges. See
  [references/composition-patterns.md](references/composition-patterns.md).
- Always run the script and confirm the output file exists and is non-empty
  before reporting success.

## Workflow

### 1. Bootstrap the environment

```bash
python3 $SKILL_DIR/scripts/check_env.py
```

Reports the interpreter, `cnsplots` version, backend availability, and whether
`mutool` is present. If `cnsplots` is missing, ask before installing, then:

```bash
python3 -m pip install cnsplots     # or: uv pip install cnsplots
```

### 2. Apply recommended overrides

Place these three lines at the top of every plotting script, before
`cns.setup_matplotlib()`:

```python
import cnsplots as cns
cns.settings.palette_seq = 'viridis'
cns.settings.font_sans_serif = ('Arial', 'Helvetica', 'Helvetica Neue', 'DejaVu Sans')
cns.setup_matplotlib()
```

Why: the installed `palette_seq='gnuplot'` is non-monotonic in perceptual
lightness (CIE L* coefficient of variation 0.66, identical to jet's 0.65) and
has 39 value pairs separated by more than 0.1 in data space that collapse to
within 1 L* in greyscale, making quantitative heatmaps misleading. `viridis` is
perceptually uniform (CV 0.07) and strictly monotonic. The installed
`font_sans_serif` prioritises Helvetica, which means Cell Press submissions
embed Helvetica rather than the required Arial; moving Arial to the front while
keeping Helvetica and DejaVu Sans as fallbacks ensures compliance without
breaking on systems that lack Arial. Full measurements and reasoning:
[references/journal-specs.md](references/journal-specs.md). Emit the block with
`python3 $SKILL_DIR/scripts/recommended_overrides.py --code`.

### 3. Verify the target journal's requirements

Read the column width, type limits, and resolution floor from
[references/journal-specs.md](references/journal-specs.md) before choosing
dimensions, and emit a compliant preset with
`python3 $SKILL_DIR/scripts/journal_preset.py <journal> --code`. Without MuPDF's
`mutool`, `cns.savefig("f.svg")` still works but falls back to plain matplotlib
SVG with a warning (no Illustrator post-processing).

### 4. Inspect the data, then the API

Print columns, dtypes, null counts, category levels, and event coding for the
real input. Then confirm the signature of each function you plan to call:

```bash
python3 $SKILL_DIR/scripts/inspect_api.py boxplot survivalplot multipanel
```

Pick the narrowest suitable function from
[references/plot-catalog.md](references/plot-catalog.md).

### 5. Choose the layout before writing code

Four cases. Getting this wrong costs a rewrite, because the layout engines are
not interchangeable.

| Figure | Approach | Start from |
| --- | --- | --- |
| One panel | `cns.figure(width=, height=)` | baseline below |
| Same plot repeated, uniform cells | `cns.figure()` + `fig.subplots()` | `templates/mpl_grid_repeat.py` |
| Different sizes/types, A/B/C labels | `cns.multipanel()` + `mp.panel()` | `templates/multipanel_heterogeneous.py` |
| Heterogeneous **and** a repeated block | one host `mp.panel()` + `fig.add_gridspec()` | `templates/mixed_grid_in_panel.py` |
| Full journal figure: many panels, images, composite plotters | `cns.multipanel()` + hand-tuned offsets | `templates/dense_figure.py` |

`multipanel` sizes each panel from its *rendered* axis decorations, so panels
whose y tick labels differ in width get different axes left edges. Measured:
three `below=`-stacked panels at y magnitudes 1, 1e5, 10 landed at
`x0 = 0.065 / 0.114 / 0.075`. `below=` groups panels vertically; it does not
align them, and `ax.set_position()` does not survive the next relayout. When
edges must line up, use the host-panel plus `GridSpec` pattern.

`multipanel` self-corrects its layout through a `draw_event` handler that it
connects automatically; do not call it yourself, and do not call
`fig.tight_layout()` on a multipanel figure, where it is a no-op that only emits
a warning. `tight_layout` belongs to the matplotlib grid path. Full reasoning and
measurements:
[references/composition-patterns.md](references/composition-patterns.md).

### 6. Build the figure

```python
import matplotlib

matplotlib.use("Agg")  # required for headless runs

import cnsplots as cns

fig = cns.figure(width=180, height=150, color_cycle="Ecotyper1")
ax = cns.boxplot(data=df, x="group", y="value", pairs=[("A", "B")])
ax.set(xlabel="Group", ylabel="Value (a.u.)")
cns.savefig("outputs/figure.svg", fig=fig)
```

- `cns.figure()` applies the full style **and** creates the figure; it returns
  the matplotlib `Figure`, which also becomes current, so keep the handle:
  `fig = cns.figure(...)`. `plt.gcf()` still works but is no longer needed. Do
  not also call `setup_matplotlib()`.
- Sizing is in points; for a physical size pass `unit=` instead of converting by
  hand: `cns.figure(183, 100, unit="mm")`, `cns.multipanel(max_width=183,
  unit="mm")`, `mp.panel("A", width=2, height=1, unit="in")`. Panel `unit`
  overrides the constructor's. Margins stay in points and `pad_left`/`pad_top`
  stay in display pixels regardless of `unit`.
- Creating the figure yourself, or drawing with plain matplotlib, seaborn, or
  scanpy? Use `cns.setup_matplotlib()` first, or `cns.setup_ax(ax)` to retrofit
  existing axes. Patterns: [references/style-bridge.md](references/style-bridge.md).
- Titles and labels go through the returned matplotlib `Axes`. Pass no
  `fontsize`, `linewidth`, or `frameon`; every value you supply overrides the
  journal style.
- Temporary style changes: `with cns.settings.context(...):` — do not mutate
  global settings permanently. Call `cns.figure()` / `setup_matplotlib()`
  **inside** the block for the temporary values to reach rcParams; the context
  now restores rcParams on exit too, including nested contexts and exceptions.
- Read statistics back instead of trusting the annotation. `cns.boxplot`,
  `violinplot`, `barplot`, `lollipopplot`, and `stackplot` accept `pairs=` as a
  list, `"all"`, or `"hue"`; after the call, `cns.get_comparison_results(ax)`
  returns a DataFrame of group1/group2, test, `n1`/`n2`, raw and adjusted
  p-values, `significant`, and the rendered label, without rerunning anything.
  Paired designs: pass `test="t-test_paired"` or `"Wilcoxon"` with
  `subject=<id column>`; this aligns by subject and raises on duplicate
  subjects, so plot summaries and matched-test counts can differ. Read survival
  estimates with `cns.get_survival_results(ax)`, and ROC / precision-recall /
  calibration results with `get_roc_results` / `get_precision_recall_results` /
  `get_calibration_results`.
- `cns.take_legend_out(ax=ax)` — `ax` is **keyword-only**. Written positionally
  it silently sets the legend *title* to the axes repr string.
- `heatmapplot` / `dotplot` return backend plotter objects, `vennplot` returns a
  matplotlib-venn object, `upsetplot` returns panel axes — not a plain `Axes`.
  Guard `.set(...)` calls accordingly.

### 7. Save and validate

```bash
python3 $SKILL_DIR/scripts/validate_output.py outputs/figure.svg
```

Prefer SVG or PDF for submission, PNG for preview. `cns.savefig(path)` saves the
current figure; pass `fig=fig` to save a retained figure without changing which
one is current. Per-save `dpi=`, `transparent=`, `bbox_inches=`, and
`pad_inches=` override the `savefig_*` settings for that call only.

**The canvas size is not the saved size.** The default `savefig_bbox='tight'`
crops to the artists, so a figure laid out to a journal column width saves
narrower than that width. Measured: a 519-pt (183 mm) multipanel canvas holding
one 240x150 panel saves at about 94 mm. Whenever the printed width must equal the
column width, save with `bbox_inches=None`; `pad_inches` then no longer applies.

A clean script exit is not evidence the figure is correct: every layout defect
found while building this skill (a silently wrapped multipanel row, tick labels
crashing into the panel below, an unrequested p-value annotation) exited zero and
produced a valid file.

Render a PNG and look at it. `savefig_transparent` is `True` by default, so set
`cns.settings.savefig_transparent = False` for the preview or the figure may
look blank on a dark background. Check: text clipping, overlapping tick labels,
legend collisions, misleading or truncated axes, indistinguishable colors, panel
misalignment, and annotations you did not ask for.

Also confirm the same category carries the same color in every panel, and check
the figure in greyscale, since figures get printed:

```python
from PIL import Image

Image.open("figure.png").convert("L").save("figure_grey.png")
```

For multipanel, confirm the row structure is what you intended. `max_width` must
exceed the sum of axes widths **plus** each panel's decoration reserve and
margins; otherwise a panel wraps to the next row with no warning. Measured: two
panels of 150 and 300 points need `max_width=519` once a boxplot is drawn in
each (507 for empty panels), so budget from the rendered version, not the bare
widths. Compare `y0` values to verify which panels share a row. `mp.newline()`
forces a row break; repeated calls add no blank rows, and a `below=` stack stays
with its parent.

### 8. Report

Return the full runnable script, the absolute output path, the palette/size
choices made, and every scientific assumption (tests, comparison direction,
event coding, transformations).

## Statistical integrity

- `pairs`, event codes, reference groups, transforms, and thresholds are
  analysis decisions. Surface them explicitly; never add them for decoration.
- Name the test actually used by the installed function's docstring (e.g.
  two-sided Mann-Whitney U for `boxplot`, Welch's t-test for `barplot`,
  Fisher's exact for `stackplot`), not an assumed one. Paired tests
  (`t-test_paired`, `Wilcoxon`) require `subject=`; without it the package
  refuses rather than silently testing independent samples.
- Confirm what was tested from the result table rather than the drawn label.
  `cns.get_comparison_results(ax)` reports the sample sizes the test actually
  used, which differ from the plotted counts when rows are dropped or subjects
  are matched.
- **Some functions annotate a test you did not request.** `cns.kdeplot` with a
  two-level `hue` runs a two-sample Kolmogorov-Smirnov test and prints
  `P = ...` on the axes; `add_mode=False` does not suppress it, and with three
  or more levels no annotation appears. Always inspect `ax.texts` after
  plotting. Either report that test by name in the caption, or remove the
  annotation deliberately:

  ```python
  for text in list(ax.texts):
      if text.get_text().startswith("$P"):
          text.remove()
  ```
- Keep raw observations when requested; do not silently swap distributions for
  summary bars.
- Do not imply causality or significance beyond what the data and test support.

## Reference index

Load these on demand; do not read them all up front.

- [references/plot-catalog.md](references/plot-catalog.md) — pick a plot function
- [references/composition-patterns.md](references/composition-patterns.md) — grid
  vs multipanel, panel alignment, mixed layouts
- [references/dense-figures.md](references/dense-figures.md) — full journal
  figures: negative offsets, embedded images, composite plotter internals,
  reworking generated annotations
- [references/color-strategy.md](references/color-strategy.md) — one palette per
  figure, keeping a variable on one color, qualitative vs sequential vs diverging,
  color-vision and greyscale checks
- [references/journal-specs.md](references/journal-specs.md) — Cell, Nature, and
  Science column widths, type and line limits, resolution and format
  requirements, and which package defaults violate them
- [references/style-bridge.md](references/style-bridge.md) — matplotlib, seaborn,
  scanpy, and plotnine integration
- [references/rcparams.md](references/rcparams.md) — the rcParams contract; read
  before writing custom artists or hardcoding any style value
- [references/settings-catalog.md](references/settings-catalog.md) — every
  `cns.settings` field
- [references/troubleshooting.md](references/troubleshooting.md) — backend errors,
  blank figures, clipped labels, palette misuse, SVG font issues
