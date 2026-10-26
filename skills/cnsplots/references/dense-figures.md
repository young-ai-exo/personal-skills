# Dense publication figures

Techniques for a full journal figure: 15 to 20 panels, mixed plot types, embedded
images, composite plotters, and hand-tuned spacing. Modeled on the upstream
showcase, <https://cnsplots.farid.one/latest/examples/showcase.html>, which was
run and inspected against 0.8.0 while writing this. The vendored source itself is
byte-identical between v0.7.0 and v0.8.0 (`git diff v0.7.0 v0.8.0 --
examples/showcase.py` is empty), so the observations below carry over unchanged.

Read [composition-patterns.md](composition-patterns.md) first for the layout
engines. This file covers what a *dense* figure needs beyond them.

The verbatim upstream source is vendored at
`templates/upstream-showcase/figure1.py` and `figure2.py`. When this description
and those files disagree, the files win.

**Contents**

- [Panels are hand-tuned, not uniform](#panels-are-hand-tuned-not-uniform)
- [Density comes from interlocking, not from small margins](#density-comes-from-interlocking-not-from-small-margins)
- [Offsets: reserve, then reclaim](#offsets-reserve-then-reclaim)
- [Embedding raster images](#embedding-raster-images)
- [Composite plotters own their own axes](#composite-plotters-own-their-own-axes)
- [Embedding an upsetplot](#embedding-an-upsetplot)
- [Reworking built-in annotations](#reworking-built-in-annotations)
- [Verifying the band structure](#verifying-the-band-structure)
- [Figure-level conventions](#figure-level-conventions)
- [Working order](#working-order)
- [Files](#files)

## Panels are hand-tuned, not uniform

A showcase-grade figure gives every panel its own size and spacing. Sizes are not
tidy round numbers: `45x100`, `60x100`, `90x90`, `190x90`, `319x160`. Set them
from what the panel's content needs, then adjust the offsets until nothing
collides. This is iterative; expect to render and look several times.

## Density comes from interlocking, not from small margins

The single biggest lever on how packed a figure looks is **stacking short panels
into the vertical space a tall neighbour occupies**, using `below=`. A flat row of
mixed-height panels leaves dead space above or below every short one.

Both showcase figures use three `below=` stacks each. Figure 1 pairs a 40x40
venn over a 50x50 donut beside 90x90 squares, and an 80x40 barplot over a 40x40
pie beside 100-pt-tall panels. In each case two short panels together span one
tall panel's band. Sizes in these calls are points, now that `panel()` takes
`unit="pt"` by default.

Measured on the rendered PNGs, as the fraction of interior rows that are entirely
empty:

| Figure | Panels | `below=` stacks | Interior empty rows |
| --- | --- | --- | --- |
| upstream Figure 1 | 18 | 3 | 4.77% |
| upstream Figure 2 | 13 | 3 | 5.44% |
| `templates/dense_figure.py` | 14 | 2 | 4.22% |

An earlier draft of that template had 9 panels, no stacks, and 7.96% empty rows
with a 62-px sliver band where a stack had fallen out of its row. Adding the
stacks and trimming `margin_right` from the default 10 to 6 closed it. Use this
measurement as the acceptance check:

```python
import numpy as np
from PIL import Image

a = np.array(Image.open("figure.png").convert("L"))
empty = ~(a < 250).any(axis=1)
# contiguous interior runs of empty rows; anything above ~6% is loose,
# and a run under ~5% of the height is usually a stray sliver band
```

A sliver band means a `below=` stack's total height did not match its
neighbours', so it was pushed onto its own row. Adjust the two stacked heights
and re-render; the stack's subtree height, not the individual panel heights, is
what sets the row.

Per-panel palette assignment carries meaning. `color_cycle` accepts a palette
name, a color list, or a single-color list to make one panel monochrome:

```python
mp.panel("A", 45, 100, color_cycle=[cns.VIOLET])          # one color
mp.panel("C", 60, 100, color_cycle="BlueRed")             # named palette
mp.panel("D", 50, 100,
         color_cycle=cns.get_hexcolors_from_apalette([2, 4], "Bold"))
```

`get_palette_colors(indices, palette)` pulls specific entries out of a palette,
which is how you give two panels distinguishable but related colors. It returns
hex strings; `get_hexcolors_from_apalette` is the older spelling of the same
call, still supported. Either way `palette` defaults to `Set1`, so pass the name.

**Do not copy the showcase's palette variety.** It switches palette on nearly
every panel because it is demonstrating the catalog, with the result that iris
`species` renders in four different colors across four panels of one figure. A
real figure uses one palette and one color per meaning. See
[color-strategy.md](color-strategy.md).

## Offsets: reserve, then reclaim

Four knobs, and the sign matters:

| Parameter | Effect |
| --- | --- |
| `margin_*` | outer spacing; counts toward the row's `max_width` budget |
| `pad_left` / `pad_top` | gap between the panel label and the axes decorations |
| negative `pad_*` | **reclaims** reserved space, pulling the axes toward the label |
| negative `margin_top` | pulls the panel up into the previous row's space |

Negative values are the main tool for tightening a dense figure. Measured on
0.8.0 with a boxplot drawn into a 120x90 panel at `max_width=300`, after a canvas
draw (`cns.boxplot(data=tips, x="day", y="total_bill", ax=ax)`): `pad_left=0`
puts the axes at `x0=0.0867`, `pad_left=40` at `0.1533`, `pad_left=-30` at
`0.0367`. The figure width does not change, so the axes slides within it. The
same three values come back after `savefig`, and 0.7.0 gives them too (identical
to four decimals), so the unit change did not move them.

Two things to know before re-using those numbers:

- **They depend on the content, through the y-axis decorations.** The reserve is
  the panel label plus the rendered width of ticks and y-label. An *empty* panel
  of the same size measures `0.0615` at `pad_left=0` — 0.025 lower than the tips
  boxplot. Widen the tick labels and it climbs further: the same boxplot with
  3-character y-ticks (`700`, `800`, `900`) measures `0.1125`, and with 4-character
  ticks (`7000`, …) `0.1254`. Quote a triple only with the plot that produced it.
- **`pad_left` is display pixels, the canvas is points**, so the delta scales with
  `settings.figure_dpi`: `pad_left=40` shifts the axes 0.0667 of a 300-pt canvas at
  the default 144, 0.1333 at 72, and 0.0333 at 288 (and `pad_left=-30` gives
  -0.05, -0.10, -0.025 respectively). The panel label's own width contributes too —
  with the tips boxplot, labels `A` / `AB` / `ABC` give `0.0867 / 0.1058 / 0.1252`
  at `pad_left=0`.

The deltas are the reliable part: 0.0667 across `pad_left` 0→40 and -0.0500
across 0→-30 at the default dpi, in every configuration tested.

The showcase leans on this hard: `pad_left=-30` on a sankey panel, `-70` and
`-50` on image panels whose axes need no y-label reserve at all, `-100` on an
upset host, `margin_top=-10` to close a row gap, `pad_top=-5` to lift a stacked
panel.

**Negative `pad_left` does not fix panel misalignment.** It narrows the gap
without closing it, and the result is not stable: correcting three
`below=`-stacked panels by their measured offsets gave `x0 = 0.065 / 0.090 /
0.070` instead of the intended single value, and `savefig` shifted all three
again. For aligned repeated panels use the host-panel plus `GridSpec` pattern.

## Embedding raster images

An image panel is a normal panel with the axes furniture switched off:

```python
import matplotlib.image as mpimg

ax = mp.panel("A", 149, 237, pad_left=-70)
ax.imshow(mpimg.imread(path))
ax.set_title("Pathology")
ax.set_axis_off()
```

Set the panel's aspect ratio to the image's, or `imshow` letterboxes it. Because
there are no ticks or y-label, reclaim the reserve with a large negative
`pad_left`. Keep `set_title()` before `set_axis_off()`; the title survives, the
spines and ticks do not.

## Composite plotters own their own axes

`heatmapplot`, `dotplot`, `upsetplot`, and `vennplot` do not return an `Axes` and
do not confine themselves to one. Their internal axes are what you style.

For `dotplot` and `heatmapplot`, the useful attributes are `ax` (the whole
block), `ax_heatmap`, `hm_ax`, `cbar_ax`, `dot_legend`, plus `ax_row_dendrogram`,
`ax_col_dendrogram`, and the `ax_*_annotation` family. Note `hm_ax` and
`ax_heatmap` are **different objects** that can share a rectangle; the showcase
titles `hm_ax` and blanks `ax_heatmap`:

```python
dp = cns.dotplot(..., ax=host)
dp.ax_heatmap.set_title("")            # suppress the built-in title
dp.hm_ax.set_title("Dotplot")          # place your own
dp.dot_legend.get_title().set_fontsize(6)
for text in dp.dot_legend.get_texts():
    text.set_fontsize(6)
dp.cbar_ax.tick_params(labelsize=6, length=0)
dp.cbar_ax.set_title("size", fontsize=6, pad=1, loc="right")
dp.cbar_ax.set_ylabel("")
```

Passing `ax=host` does place a `dotplot` inside a panel. Its legend and colorbar
are laid out relative to that host using `legend_width`, `legend_hpad`,
`legend_vpad`, `legend_hgap`, `legend_vgap`, and `legend_order`. Those are
absolute nudges tuned for one figure size: they do not rescale, and at a
different size or font the heatmap legends **will** overlap. Re-tune them
whenever you change panel geometry, and verify by looking.

`vennplot` draws into the current panel; reach the axes with
`mp.get_axes("G").set_title(...)`.

## Embedding an upsetplot

`upsetplot` returns `dict[str, Axes | None]` with keys `matrix`, `shading`,
`totals`, `intersections` (`totals` is `None` when
`totals_plot_elements=0`), and it takes either `ax=` or `fig=`. Measured on
0.8.0, `ax=host` **does** confine the group: all four axes landed inside the host
rectangle and stayed inside through a later `canvas.draw()` relayout, at every
host size tried (190x90, 200x120, 240x100). Same result on 0.7.0, so older
descriptions of it "spilling out" do not hold.

The reason to prefer `fig=` anyway is layout, not containment: an `ax=`-embedded
group is laid out inside the host immediately, which leaves the host's own
contents cramped when the host is small. The showcase pattern lets the group size
itself on the figure and then scales it onto the host rectangle, which gives
control over the padding. Use `ax=host` for a quick embed; use the rescale below
when you are tuning a dense figure.

```python
host = mp.panel("M", 200, 120, margin_right=0, pad_left=-100, pad_top=10)
axes = cns.upsetplot(upset_sets, fig=mp.fig, sort_by="cardinality",
                     totals_plot_elements=0, show_counts=False)
axes["intersections"].set_title("UpSetplot")
```

then, **after every `mp.panel()` call**, map the group's bounding box onto the
host's:

```python
detached = [ax for ax in axes.values() if ax is not None]
fig.canvas.draw()                       # settle the layout first
host.set_axis_off()
hb = host.get_position().frozen()
boxes = [ax.get_position().frozen() for ax in detached]
left, right = min(b.x0 for b in boxes), max(b.x1 for b in boxes)
bottom, top = min(b.y0 for b in boxes), max(b.y1 for b in boxes)
width, height = max(right - left, 1e-9), max(top - bottom, 1e-9)
xpad = ypad = 0.03
x0, y0 = hb.x0 + hb.width * xpad, hb.y0 + hb.height * ypad
w, h = hb.width * (1 - 2 * xpad), hb.height * (1 - 2 * ypad)
for ax, box in zip(detached, boxes):
    ax.set_position([x0 + w * ((box.x0 - left) / width),
                     y0 + h * ((box.y0 - bottom) / height),
                     w * (box.width / width), h * (box.height / height)])
```

Verified with public API only: the axes land inside the host rectangle and their
bounds are unchanged across `savefig`. The showcase additionally calls
`cns.utils._capture_detached_axes_layout(host, detached_axes=detached)`. That is
private, and it is not needed when you embed last. It registers the group to
follow the host through later relayouts, but the tracking is not exact: adding a
panel afterwards moved the host by `+0.334` in figure coordinates while the
embedded axes moved `+0.200`. Embed last and skip it.

## Reworking built-in annotations

Statistical annotations and legends are generated, then edited. All of these are
from the showcase and run as written.

Shorten a survival hazard-ratio annotation by rewriting the text artist:

```python
for text in ax.texts:
    if text.get_text().startswith("HR ="):
        head, sep, tail = text.get_text().partition("\n")
        text.set_text(f"{head.split(' (', 1)[0]}{sep}{tail}" if sep else head)
        break
```

Wrap a long ROC legend label onto two lines:

```python
for text in ax.get_legend().get_texts():
    text.set_text(text.get_text().replace(" (AUC=", "\n(AUC="))
    text.set_multialignment("left")
```

Rebuild a legend to reposition it, preserving handles and labels:

```python
legend = ax.get_legend()
ax.legend(handles=legend.legend_handles,
          labels=[t.get_text() for t in legend.get_texts()],
          title=legend.get_title().get_text(),
          loc="upper left", bbox_to_anchor=(-0.02, 1.0),
          borderaxespad=0, markerscale=1)
```

Other idioms: `ax.get_legend().set_title(None)` drops a redundant legend title,
`ax.get_legend().remove()` drops the legend where the panel is self-explanatory,
`legend.set_loc("lower right")` moves it, and `cns.take_legend_out()` with no
arguments operates on the current axes. Strip a parenthetical from each label
with `text.set_text(text.get_text().split(" (", 1)[0])`.

Rotating tick labels needs the anchor form, or long labels drift away from their
ticks:

```python
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right",
                   rotation_mode="anchor")
```

This emits a matplotlib `UserWarning` about `FixedFormatter`. It is benign here
because the categorical ticks are already fixed.

## Verifying the band structure

Panels in one row are aligned at neither edge when their heights differ: a 90-pt
and a 70-pt panel sharing a row gave `y0 = 0.093 / 0.279` and `y1 = 0.930 /
0.930` in one case, but with per-panel `pad_top` and composite plotters in play
neither edge is reliable. Grouping by `y0` reported three separate bands for
three panels that visibly shared one.

Group by vertical **overlap** instead. Two panels are in the same band when their
extents overlap by more than a quarter of the shorter panel's height:

```python
placed = sorted(
    ((label, ax.get_position().y0, ax.get_position().y1)
     for label, ax in ((L, mp.get_axes(L)) for L in "ABCDEFGH") if ax),
    key=lambda item: -item[2],
)
bands = []
for entry in placed:
    _, y0, y1 = entry
    for band in bands:
        if any(min(y1, b1) - max(y0, b0) > 0.25 * min(y1 - y0, b1 - b0)
               for _, b0, b1 in band):
            band.append(entry)
            break
    else:
        bands.append([entry])
```

This reproduced multipanel's internal row grouping on every case tested, using
only public API. `templates/dense_figure.py` ships it as `report_bands()` and
prints the result on save, which is how you catch a silent wrap without opening
the file.

## Figure-level conventions

```python
cns.settings.title_fontweight = "normal"        # panel titles: normal weight
mp = cns.multipanel(max_width=485, title="Figure 1",
                    title_fontweight="bold", loc="left")
```

Setting panel titles to normal while the figure title stays bold keeps the
hierarchy readable at 8pt. Panel *letters* stay bold via
`settings.panel_label_fontweight`.

`mp.newline()` starts a new band when a row is logically complete rather than
full. Use `cns.placeholderplot("...")` to hold a slot whose content does not
exist yet; it draws a captioned box at the panel's size.

## Working order

1. Sketch the bands and give each panel a provisional size.
2. Declare **every** `mp.panel()` call, including hosts for grids and detached
   plotters.
3. Draw content into each panel.
4. Embed anything detached (upset, grid-in-panel), after all panels exist.
5. `cns.savefig(...)`, then render a PNG with
   `cns.settings.savefig_transparent = False` and look at it.
6. Fix collisions with negative `pad_*` / `margin_*`, re-render, repeat.

Step 5 is not optional at this density. Every defect found while validating this
material, including overlapping heatmap legends and a silently wrapped row, was
invisible in a zero exit code and a valid SVG.

## Files

- `templates/dense_figure.py` — runnable 14-panel adaptation of these techniques,
  with a `report_bands()` acceptance check.
- `templates/upstream-showcase/figure1.py`, `figure2.py` — the upstream source,
  verbatim and unmodified. Read these when a distilled rule here looks wrong or
  you need an offset the prose does not cover. Both run against 0.8.0; the source
  is byte-identical to the 0.7.0 copy.
