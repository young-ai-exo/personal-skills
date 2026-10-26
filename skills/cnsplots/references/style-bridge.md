# Bridging cnsplots style and plain matplotlib

cnsplots styles figures purely through `matplotlib.rcParams`, so any matplotlib,
seaborn, scanpy, or gseapy artist can carry the journal style. Use this when the
plot you need is not in the cnsplots catalog, or when another library owns the
drawing.

The exact rcParams involved, and the rules for not defeating them, are in
[rcparams.md](rcparams.md). Read that before writing custom artists.

## Pick the right entry point

| Situation | Call | Creates a figure? |
| --- | --- | --- |
| One cnsplots-sized figure | `cns.figure(width=, height=)` | yes |
| You create the figure yourself | `cns.setup_matplotlib()` | no |
| Whole script, many figures | `cns.setup_matplotlib()` once at the top | no |
| Axes already drawn by another library | `cns.setup_ax(ax)` | no |
| Scoped deviation from the style | `with cns.settings.context(...)` | no |
| scanpy / plotnine defaults | `cns.setup_scanpy()`, `cns.setup_ggplot()` | no |

`cns.figure()` applies the entire style, not just a size. After
`setup_matplotlib()`, a subsequent `cns.figure()` changes zero further rcParams
(measured on 0.8.0: 0 keys differ), so calling both is redundant, not additive.
`figure()` returns the styled `Figure` and makes it current, so
`ax = cns.figure(width=220, height=160).gca()` works. `setup_matplotlib()`,
`setup_ax()`, and `setup_scanpy()` return `None`; `setup_ggplot()` is the odd one
out and returns an R `theme()` code string, modifying nothing in matplotlib.

## Pattern 1: cnsplots canvas, matplotlib drawing

For plot types cnsplots does not provide (`fill_between`, `contourf`, `errorbar`,
custom artists).

```python
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import cnsplots as cns

ax = cns.figure(width=220, height=160).gca()       # plt.gca() also works

ax.plot(t, mean)                                  # prop_cycle picks the color
ax.fill_between(t, lo, hi, color=cns.BLUE, alpha=0.15, linewidth=0)
ax.set_xlabel("Time (h)")                         # 8pt from axes.labelsize
ax.set_ylabel("Signal (a.u.)")
ax.legend(["Mean", "95% CI"])                     # frameless, 7pt

cns.savefig("styled.svg")
```

Pass no `fontsize`, `linewidth`, or `frameon`: each one you supply overrides the
style. Colors come from `axes.prop_cycle`, `cns.BLUE`-style constants, or
`cns.palettes(name)`.

## Pattern 2: your own figure, cnsplots style

When you need `plt.subplots` semantics, or a figure size in inches.

```python
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import cnsplots as cns

cns.setup_matplotlib(color_cycle="Tableau")
fig, axes = plt.subplots(2, 2, figsize=(340 / 72, 240 / 72), dpi=144)

for ax, name in zip(axes.flat, names):
    cns.kdeplot(data=df, x=name, ax=ax)
    ax.set_title(name)

fig.tight_layout()
cns.savefig("subplots.svg")
```

Dividing by 72 keeps the point convention consistent with `cns.figure()`; pass
`dpi=144` to match `settings.figure_dpi`. Every cnsplots plot function accepts
`ax=` as a keyword argument, so they compose into any matplotlib layout. On 0.8.0
you can skip the arithmetic: `fig = cns.figure(width=340, height=240)` then
`fig.subplots(2, 2)` gives the same canvas with the style already applied.

## Pattern 3: retrofit axes from another library

seaborn, scanpy, and gseapy create their own axes, often before the style is
active. `cns.setup_ax(ax)` restyles one in place: fonts, spines, ticks, and any
attached colorbar.

```python
import cnsplots as cns
import seaborn as sns

cns.figure(width=240, height=180)
ax = plt.gca()
sns.heatmap(matrix, ax=ax, cbar=True)
cns.setup_ax(ax, colorbar_label="log2 FC")        # default label is 'FDR q-val'
cns.savefig("heatmap.svg")
```

Signature: `setup_ax(ax, title_fontsize=None, title_fontweight=None,
legend_fontsize=<sentinel>, axes_linewidth=None, colorbar_label=None)`. It
returns `None` and mutates in place. Always pass `colorbar_label` when a
colorbar is present, since the default is the GSEA-oriented `'FDR q-val'`.

## Pattern 4: scoped style deviation

```python
with cns.settings.context(palette_qual="Set2", axes_linewidth=1.0):
    cns.figure(width=200, height=150)
    ax = cns.boxplot(data=df, x="group", y="value")
    cns.savefig("thick_set2.svg")
# palette_qual is back to Ecotyper1 here
```

Assigning to `cns.settings.<field>` directly is persistent and leaks into every
later figure in the process. Reach for `cns.settings.reset()` only to recover
from that.

## Legends

`cns.take_legend_out(title=None, *, ax=None)` moves a legend outside the axes
using `settings.legend_out_loc` and `legend_out_bbox_to_anchor`.

`ax` is **keyword-only**. Calling `take_legend_out(ax)` positionally does not
raise: `ax` binds to `title`, and the legend title becomes the axes repr, e.g.
`Axes(0.125,0.11;0.775x0.77)`. Always write:

```python
cns.take_legend_out(ax=ax)
cns.take_legend_out(title="Species", ax=ax)
```

## Fonts and unicode

`font.sans-serif` is Helvetica-first, falling back to DejaVu Sans. The fallback
has different metrics, so identical code yields slightly different label widths
across machines; this matters for multipanel, whose layout measures rendered
decoration widths.

For CJK or symbol glyphs, call `cns.apply_unicode_font()`; otherwise missing
glyphs render as boxes. With `svg.fonttype = 'none'`, SVG text stays editable
text, which means the **viewer** must also have the font. Check output in a
different application before delivering.

## Sanity checks

```python
import matplotlib as mpl

print(mpl.rcParams["axes.linewidth"])       # 0.5 when the style is active
print(mpl.rcParams["legend.frameon"])       # False
print(mpl.get_backend())                    # Agg when headless
```

If these show matplotlib defaults, the style was never applied, or something
called `mpl.rcParams.update(mpl.rcParamsDefault)` or `plt.style.use(...)`
afterwards and clobbered it.
