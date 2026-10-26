# Composition patterns

Three layout engines, three jobs. Picking the wrong one produces misaligned
panels that no amount of parameter tuning will fix.

| | matplotlib grid | `cns.multipanel` | grid inside a host panel |
| --- | --- | --- | --- |
| Panel sizes | uniform | per-panel | uniform within the grid |
| Cross-row/column alignment | guaranteed | **not guaranteed** | guaranteed |
| A/B/C labels | manual | automatic | automatic for the host |
| Layout flow | fixed rows x columns | wraps at `max_width` | fixed inside the host rect |
| Vertical stacking | rows | `below="A"` | rows |
| Per-panel palette | global only | `color_cycle=` | global only |
| Use for | one repeated plot | heterogeneous figure | heterogeneous + a repeated block |

**Contents**

- [Decision rule](#decision-rule) — which of the three engines
- [Why multipanel does not align panels](#why-multipanel-does-not-align-panels)
- [Pattern A: repeated grid, matplotlib](#pattern-a-repeated-grid-matplotlib)
- [Pattern B: heterogeneous figure, multipanel](#pattern-b-heterogeneous-figure-multipanel)
- [Pattern C: repeated grid inside a heterogeneous figure](#pattern-c-repeated-grid-inside-a-heterogeneous-figure)
- [Returned objects](#returned-objects)
- [The draw handler, and why `tight_layout` is not the analogue](#the-draw-handler-and-why-tight_layout-is-not-the-analogue)
- [Checking which panels share a row](#checking-which-panels-share-a-row)

## Decision rule

1. Every panel same size and same plot type, no other panels? **Pattern A**,
   matplotlib grid.
2. Panels differ in size or type, and you do not need them edge-aligned?
   **Pattern B**, `cns.multipanel`.
3. Both: a heterogeneous figure that contains a block of repeated panels?
   **Pattern C**, one host panel subdivided with `GridSpec`.

Never build a visual grid by calling `mp.panel()` once per cell. Read the next
section for why.

## Why multipanel does not align panels

`multipanel` sizes each panel as
`margin_left + left_reserve + width + margin_right`
(`_multipanels.py:460`, `_get_panel_total_size`), where `left_reserve` comes
from `_get_left_reserve_px()` (`:420`) and is derived from that panel's
**actually rendered** y-axis decoration width. Your `width=` constrains the axes
only; the panel's outer width is discovered at draw time.

Consequence: two panels whose y tick labels differ in width get different axes
left edges. Measured with three `below=`-stacked panels at y magnitudes 1, 1e5,
and 10, all `width=150`, `multipanel(max_width=420)` on 0.8.0:

```
A: x0=0.04390
B: x0=0.07619
C: x0=0.03943
```

With identical magnitudes they agree to within a tenth of a display pixel: A and
B both `0.04390`, C `0.04405`, the 0.13 display-pixel difference tracing to the
label glyph `C` measuring 11.625 display px against 11.5 for `A`/`B`. The same
applies to flow layout: six `140x100` panels forming a visual 3x2 grid at
`max_width=420` gave column-two left edges of `0.4449`, `0.4452`, `0.442` across
the three rows.

So `below=` stacks panels **vertically in the same column slot**, but does not
align their axes edges. Use it for semantic grouping where a few pixels do not
matter, or where the panels genuinely share tick formatting (a KM curve with its
risk table underneath).

Three fixes were tested; two do not work:

- Unify tick formatting with a shared `FuncFormatter`: gets to
  `0.03006 / 0.07619 / 0.03943`. It narrows the worst panel but does not
  equalize them, and it forces one tick format on every panel. (The formatter
  only re-measures panels whose rendered labels actually changed: panel A's
  reserve fell `25.375` -> `13.75` px while B and C were untouched.)
- Hand-tune `pad_left`: `pad_left` is **added on top of** the measured reserve,
  not substituted for it, so the panels stay unequal. Measured at the same
  `max_width=420`: `pad_left=0/20/40` moved the left reserve of a panel with
  `52.5` px of decorations from `32.0` to `42.0` to `52.0` points, and its `x0`
  from `0.07619` to `0.10000` to `0.12381`.
- `ax.set_position()` after all panels exist: aligns correctly at first, then is
  **discarded whenever the next draw remeasures the layout**. Measured on the
  ragged triple: setting all three to `x0=0.114` survives a plain
  `fig.canvas.draw()` but `cns.savefig()` reverts them to
  `0.04390 / 0.07619 / 0.03943`; forcing a re-measure with
  `fig.set_dpi(288)` and a draw reverts to `0.04412 / 0.07671 / 0.03951`. On a
  uniform-magnitude pair the same override also reverted exactly to `0.04390`
  for both on save. Either way the override does not survive, and the outcome is
  configuration-dependent rather than predictable. See the draw handler section
  below for when a remeasure is triggered.

Do not attempt to force alignment on multipanel axes. Use Pattern C.

How bad the raggedness is depends entirely on how much the y tick label widths
differ. At magnitudes 1 versus 1e5 the A/B gap measured `0.03229` in figure
coordinates, roughly 27 px on an 840 px canvas, and obvious. With three panels
at 1 / 1e6 / 10 the total span was only `0.00446`, about 4 px, because `1e6`
renders in offset notation and is no wider than a small plain number. So
`below=` is fine for stacking panels that share tick formatting or sit at
similar magnitudes; it is only unusable when you need guaranteed edge alignment
across differing label widths.

## Pattern A: repeated grid, matplotlib

Uniform panels, one plot type, no heterogeneous neighbours.

```python
import matplotlib

matplotlib.use("Agg")

import cnsplots as cns

groups = ["BRCA1", "TP53", "EGFR", "MYC", "KRAS", "PTEN"]
ncols = 3
nrows = -(-len(groups) // ncols)
panel_w, panel_h = 120, 100

# 0.8.0 returns the Figure; on 0.7.0 this was None and you needed plt.gcf().
fig = cns.figure(width=ncols * panel_w, height=nrows * panel_h)
axes = fig.subplots(nrows, ncols, squeeze=False)

for idx, name in enumerate(groups):
    ax = axes[idx // ncols][idx % ncols]
    cns.kdeplot(data=expr, x=name, hue="condition", ax=ax)
    ax.set_title(name)
    ax.set_xlabel("")

for idx in range(len(groups), nrows * ncols):
    axes[idx // ncols][idx % ncols].set_visible(False)

fig.tight_layout()
cns.savefig("grid.svg")
```

`cns.figure()` already applies the full style, so every subplot inherits it; do
not also call `setup_matplotlib()`. Panel letters, if needed, come from
`cns.add_panel_label("A")`, which labels the **current** axes and takes no `ax`
argument, so select the axes first with `plt.sca(ax)`.

`GridSpec` allots equal cells regardless of tick label width, so columns and rows
align exactly.

## Pattern B: heterogeneous figure, multipanel

Different sizes and plot types, automatic labels, alignment not required.

```python
import matplotlib

matplotlib.use("Agg")

import cnsplots as cns

mp = cns.multipanel(max_width=420, title="Cohort summary", loc="left")

ax_a = mp.panel("A", width=110, height=130)
cns.violinplot(data=iris, x="species", y="sepal_length", ax=ax_a)
ax_a.set_ylabel("Sepal length (cm)")

ax_b = mp.panel("B", width=180, height=130)
cns.scatterplot(data=iris, x="sepal_length", y="petal_length", hue="species", ax=ax_b)
cns.take_legend_out(title="Species", ax=ax_b)      # ax is keyword-only

ax_c = mp.panel("C", width=110, height=80, below="A")
cns.barplot(data=tips, x="day", y="total_bill", ax=ax_c)

cns.savefig("figure.svg")
```

- Panels flow left to right and wrap when the row exceeds `max_width`.
- `mp.newline()` forces a break. A panel attached with `below=` stays with its
  parent, and the new row starts beneath the whole stack. Repeated calls and
  empty layouts add no blank rows.
  **This only works from 0.8.0.** On 0.7.0 a single `newline()` did *not* break
  the row — three 100-wide panels at `max_width=420` all landed on
  `y0=0.0930`, and a `below=` stack plus `newline()` still put the next panel
  beside the stack (`B y0=0.6286`, level with `A`). Measured the same script on
  0.8.0: `A y0=0.5465`, `B y0=0.0465`, and with a two-deep `below=` stack
  `B y0=0.0270` sits below `A2 y0=0.3176`. Repeated `newline()` on 0.8.0 leaves
  one spacer (`len(mp._panels)==3` for two real panels), and calling it before
  any panel adds nothing.
- `below="A"` stacks under panel A instead of flowing.
- `mp.get_axes("A")` retrieves a panel's axes later; `mp.fig` is the figure.
- `panel_margin_bottom` and `panel_margin_right` default to `10`, so panels are
  not flush unless you pass `margin_*=0`.

## Pattern C: repeated grid inside a heterogeneous figure

One `mp.panel()` acts as a positioned, empty **host rectangle**. Its coordinates
become the bounds of a `GridSpec`, so matplotlib lays out the cells and
alignment is exact, while multipanel still draws the host's panel letter.

```python
import matplotlib

matplotlib.use("Agg")

import cnsplots as cns

mp = cns.multipanel(max_width=520)

ax_a = mp.panel("A", width=150, height=110)
cns.boxplot(data=df, x="group", y="value", ax=ax_a)

host = mp.panel("B", width=300, height=110)          # grid host, stays empty

ax_c = mp.panel("C", width=150, height=90, below="A")
cns.barplot(data=df, x="group", y="value", ax=ax_c)

# All panels exist. Only now subdivide the host.
fig = mp.fig
fig.canvas.draw()                                     # let the layout settle
box = host.get_position()
host.set_axis_off()                                   # hide the empty frame

gs = fig.add_gridspec(2, 3, left=box.x0, right=box.x1,
                      bottom=box.y0, top=box.y1,
                      wspace=0.5, hspace=0.6)

for idx, name in enumerate(genes):
    ax = fig.add_subplot(gs[idx // 3, idx % 3])
    cns.boxplot(data=frames[name], x="group", y="value", ax=ax)
    cns.setup_ax(ax)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(name)

cns.savefig("mixed.svg")
```

Measured with cell y magnitudes spanning 1 to 1e5: each column has a single
`x0`, each row a single `y0`, and the bounds are bit-identical before and after
`savefig`. The grid cells are not multipanel panels, so `_on_draw` never
repositions them.

Two ordering constraints, both load-bearing:

1. **Subdivide after every `mp.panel()` call.** Adding a panel afterwards
   re-flows the host; the already-placed grid stays put and ends up outside the
   host rectangle. Reproduced: adding panel C after subdividing moved host B
   from `y0=0.03922` to `y0=0.02759` while the cells kept their old
   coordinates exactly (`0.03546 / 0.03922` before and after).
2. **Call `fig.canvas.draw()` before reading `host.get_position()`.** Before the
   first draw, the reserve is unmeasured and the rectangle is a provisional
   value.

`cns.setup_ax(ax)` on each cell is belt-and-braces: cells created with
`add_subplot` already inherit the active rcParams. Call it when the axes came
from a library that overrode them, and pass `colorbar_label=` explicitly if a
colorbar is present, since the default is `'FDR q-val'`.

### Do not use `inset_axes` for this

The `mpl_toolkits.axes_grid1.inset_locator.inset_axes` approach with a tuple
`loc` constructs without error and then **crashes at draw time**:

```
TypeError: list indices must be integers or slices, not tuple
```

`loc` must be an int or a recognized string. Even with a valid `loc`, insets are
anchored relative to the host axes with `borderpad` padding, which does not
produce a regular grid. `GridSpec` is the correct tool.

## Returned objects

Most plot functions return the target `Axes`. `heatmapplot` and `dotplot` return
backend plotter objects, `vennplot` a matplotlib-venn object, and `upsetplot` a
`dict[str, Axes | None]`. In grid loops, do not assume the return value is an
`Axes`; pass `ax=` and keep using your own reference. These composite plotters
also manage their own internal axes, so they cooperate poorly with a `GridSpec`
cell.

`dotplot` accepts `ax=host` and stays inside the panel. `upsetplot` also takes
`ax=host`, and on 0.8.0 it does confine itself: all four returned axes measured
inside the host rectangle, so no rescale step is needed. It takes a **dict of
sets**, not a DataFrame. `ax=` and `fig=` are mutually exclusive. Styling their
internal axes and embedding a detached plotter are covered in
[dense-figures.md](dense-figures.md).

## The draw handler, and why `tight_layout` is not the analogue

`multipanel` cannot know how much horizontal space a panel's y-axis decorations
need until they have been rendered. So it lays out with a zero reserve, draws,
measures, and lays out again. The measuring step is `_on_draw`, registered on
matplotlib's standard `draw_event` from inside `panel()` (`_multipanels.py:504`
is `_connect_draw_handler`, called from `_create_or_update_figure` at `:802`,
which `panel()` reaches at `:1104`), and it iterates up to
`_RELAYOUT_MAX_PASSES = 3` times until the measurement stops changing.

Observable: for a panel whose y tick labels are wide, the cached reserve is
`0.0` and the axes sits at `x0 = 0.0` before any draw; after the first draw the
reserve is populated and `x0` moves right. Measured on 0.8.0 with a 150x90
panel at `max_width=420`: crowded tick labels (`0.0 / 100000.0 / 200000.0`) plus
a long y-label give a `83.125` px reserve and `x0 = 0.11265`; the plain
`100000 / 200000` default labels alone give `52.5` px and `0.07619`. A second
draw changes nothing, so it has converged. Without the handler, those labels
overlap the panel letter of the neighbour to the left.

**It is automatic, and multipanel-only.** There is nothing to enable. The first
`mp.panel()` call creates the figure and connects the handler; each `multipanel`
instance owns its own figure and its own handler. `cns.figure()`, the
single-panel path, connects nothing, since a lone panel has no neighbour to
collide with.

**Do not call `_on_draw` yourself.** It is private, and it expects a real
matplotlib `DrawEvent` carrying a renderer. Passing `None` fails the internal
`isinstance` check and returns silently, so it looks like it worked while doing
nothing. To make it run, cause a draw:

```python
mp.fig.canvas.draw()      # only needed before you READ get_position()
```

Even that is usually unnecessary. `cns.savefig()` draws internally, and the
reserve is correct by the time the file is written: measured `0.0` before
`savefig`, `25.375` px after, with no manual call anywhere.

**`tight_layout` is not the counterpart, and does nothing here.** The two
optimize opposite things: `tight_layout` resizes axes to fit a fixed figure,
while `_on_draw` keeps axes at exactly the requested size in points and adjusts
the figure and panel offsets around them. Verified: a panel requested at
`width=150, height=90` measures `300x180` rendered px at 144 dpi, exactly
150.0x90.0 points.

On a `multipanel` figure, `fig.tight_layout()` is a **no-op that emits a
warning**:

```
UserWarning: This figure includes Axes that are not compatible with tight_layout
```

Panel axes are placed with explicit coordinates and have no `SubplotSpec`
(`ax.get_subplotspec() is None`), so `tight_layout` skips them; measured panel
bounds are byte-identical before and after, with or without the handler
connected. It does not corrupt anything, it simply has no effect. Leave it out.

Reach for `tight_layout` on the matplotlib path only:

```python
# matplotlib grid: tight_layout applies
cns.setup_matplotlib()
fig, axes = plt.subplots(2, 2, figsize=(340 / 72, 240 / 72), dpi=144)
...
fig.tight_layout()
cns.savefig("grid.svg")

# multipanel: no layout call at all
mp = cns.multipanel(max_width=480)
...
cns.savefig("figure.svg")
```

One consequence for hand-tuning: the handler only relayouts when a left-side
measurement changes by more than an internal tolerance. Changing y tick
`labelsize` triggers it (measured `71.5` -> `105.25` px of reserve for
`labelsize` 7 -> 12), whereas replacing the y-axis *label text* does not
(`71.5` -> `71.5` px, unchanged), because that label is rotated 90 degrees and
its width depends on font size rather than string length. So whether a manual
`ax.set_position()` survives a draw depends on whether that draw also tripped a
remeasure; it is not unconditionally erased, which is why relying on it either
way is unsafe.

## Checking which panels share a row

Do not infer rows from `y0` or `y1`. Panels of differing heights share a row
while agreeing on neither edge, so both give false wraps. Group by vertical
overlap instead; `templates/dense_figure.py` has a `report_bands()` helper that
reproduces multipanel's internal grouping using public API only. See
[dense-figures.md](dense-figures.md).
