# cnsplots troubleshooting

Run every helper script through `$SKILL_DIR`, the skill's own directory — not
the user's project root, where these paths do not exist.

**`ModuleNotFoundError: No module named 'cnsplots'`** — not installed in the
active interpreter. Confirm with `python3 $SKILL_DIR/scripts/check_env.py`, then
ask the user before `python3 -m pip install cnsplots`. Watch for venv mismatch.

**Backend / display errors, or the process hangs** — set the backend before any
plotting import:

```python
import matplotlib
matplotlib.use("Agg")
import cnsplots as cns
```

or export `MPLBACKEND=Agg`.

**Figure is blank or tiny** — `width`/`height` are **points**. `cns.figure(6, 4)`
is a 6x4 *point* figure: measured `get_size_inches() == (0.083, 0.056)` and a
12x8 display canvas at 144 dpi. Use millimetres with `unit=` and it is hard to
be wrong: `cns.figure(180, 150, unit="mm")`. In the default point unit the same
figure is `cns.figure(510.2, 425.2)` (measured 179.9 x 149.9 mm for the rounded
`510, 425`).

**Figure looks blank in a dark viewer** — `settings.savefig_transparent` is
`True`, so there is no background. Set
`cns.settings.savefig_transparent = False` for previews, or open the file over
white.

**`AttributeError: 'NoneType' object has no attribute ...` after `cns.figure()`**
— a 0.7.0-era idiom. On **<= 0.7.0** `cns.figure()` returned `None` (it created
and styled the current figure), so you had to write `fig = plt.gcf()`. From
**0.8.0** it returns the `Figure`, which is also the current pyplot figure, so
`fig = cns.figure(...)` is the supported form. Verified on 0.8.0:
`type(cns.figure(200, 160)).__name__ == 'Figure'`.

`setup_matplotlib()`, `setup_ax()`, and `take_legend_out()` still return `None`
on 0.8.0 — verified — so keep `plt.gcf()` / your own `ax` reference for those.
Old code that ignores the return value keeps working; only code or type checks
that asserted `None` need updating.

**Multipanel produced more rows than expected** — `max_width` is compared
against each panel's *total* width, which is
`margin_left + left_reserve + width + margin_right`, not the `width=` you
passed. `left_reserve` is the rendered width of the panel label plus the y-axis
decorations, so it **grows once you draw into the panel**. Empty, a 150-point and
a 300-point panel measure 178.44 and 328.44 points and share a row from
`max_width=507` up (scanned 500-520); with a boxplot in each they need **519**.
Budget from the rendered version, which is what ships. Summing the raw `width=`
values would have said 450. Nothing warns. Compare panel `y0`
values to see which panels actually share a row.

**Row check reports panels on separate rows that clearly share one** — you
grouped by `y0` or `y1`. Panels of differing heights share a row while agreeing on
neither edge. Group by vertical overlap; see `report_bands()` in
`templates/dense_figure.py`.

**An `upsetplot` spills outside its panel** — *not on 0.8.0.* The signature
takes a **dict of sets**, not a DataFrame (`TypeError: [upsetplot] Parameter
'sets' must be a dictionary, got DataFrame`), and `ax=` does confine the
layout: measured on a 240x160 canvas, all four returned axes (`matrix`,
`shading`, `totals`, `intersections`) lie inside the host `ax` bounds
(`60.0-432.0 x 35.2-281.6`) and stay inside through a later `draw()`. So
`ax=host` is enough to keep it in its panel; `ax=` and `fig=` are mutually
exclusive. The `fig=` plus rescale recipe in
[dense-figures.md](dense-figures.md) is only worth it when you want to control
the internal padding of a dense figure. Its dict has a `totals` key that is
`None` when `totals_plot_elements=0` (verified), so filter `None` before
iterating.

**`heatmapplot` or `dotplot` legends overlap each other or the next panel** —
`legend_hpad`, `legend_vpad`, `legend_hgap`, `legend_vgap`, `legend_width` are
**absolute nudges in millimetres**, not fractions of the panel: the source
converts them with `mm2inch * figure.dpi` (`helpers/_heatmap.py`), so they do not
rescale when the figure grows and a value copied from another figure will
usually collide. Re-tune them after any geometry change and confirm visually.

**Composite plotter title appears twice or in the wrong place** — `dotplot` and
`heatmapplot` expose several internal axes, and `hm_ax` is not the same object as
`ax_heatmap` even when they share a rectangle. Blank the built-in title with
`dp.ax_heatmap.set_title("")` and set your own on `dp.hm_ax`.

**Image panel has thick white margins** — the panel aspect ratio does not match
the image, so `imshow` letterboxes it. Size the panel to the image, and reclaim
the unused decoration space with a negative `pad_left` since an image axes has no
ticks or y-label.

**Panels in a visual grid have ragged left edges** — expected: multipanel derives
each panel's reserve from its rendered y tick label width, so differing
magnitudes shift the axes. Do not fix it with `pad_left` (it adds to the reserve)
or `ax.set_position()` (discarded by the next relayout). Use a single host panel subdivided
with `fig.add_gridspec()`; see
[composition-patterns.md](composition-patterns.md).

**`UserWarning: This figure includes Axes that are not compatible with
tight_layout`** — `tight_layout()` was called on a `multipanel` figure. Panel axes
are positioned explicitly and have no `SubplotSpec`, so `tight_layout` skips them
entirely: measured panel bounds are identical before and after. It is a harmless
no-op, but drop the call. `multipanel` already self-corrects through its
`draw_event` handler, and `tight_layout` belongs to the `plt.subplots` path. See
[composition-patterns.md](composition-patterns.md).

**Panel geometry looks wrong when read right after plotting** — the decoration
reserve is measured during a draw, so before the first draw it is `0.0` and the
axes sits at its uncorrected position. Call `mp.fig.canvas.draw()` before reading
`get_position()`. You do not need it before `cns.savefig()`, which draws
internally.

**`TypeError` from `inset_axes(..., loc=(x, y))` at save time** — `loc` must be
an int or a known string, not a tuple. Construction succeeds silently; the error
only appears at draw. On matplotlib 3.10.9 the message is
`TypeError: _compat_get_offset.<locals>.<lambda>() missing 2 required positional
arguments: 'bbox' and 'renderer'` — the older
`list indices must be integers or slices, not tuple` text is from earlier
matplotlib. Reproduced on 3.10.9 for both `width="30%"` and `width=1.0` forms
with a tuple `loc`; `loc="upper right"` draws fine. Use `GridSpec` for grid
layouts instead of insets.

**`AttributeError` on the returned object** — `heatmapplot`, `dotplot`,
`vennplot`, and `upsetplot` do not return a plain `Axes`. Inspect with
`type(result)` and reach for the matplotlib axes through the returned object or
`plt.gca()`.

**`TypeError: unexpected keyword argument`** — the signature changed between
releases. Run `python3 $SKILL_DIR/scripts/inspect_api.py <function>` and match the
installed signature instead of copying older examples.

**Clipped labels or overlapping ticks** — increase panel width/height, rotate
tick labels via the returned axes (`ax.tick_params(axis="x", rotation=45)`),
shorten category names, or move the legend out with
`cns.take_legend_out(ax=ax)`.

**Legend overlaps the data** — `cns.take_legend_out(ax=ax)`, or widen the canvas
so the legend has dedicated space.

**Legend title became `Axes(0.125,0.11;0.775x0.77)`** — `take_legend_out(ax)` was
called positionally. The signature is `take_legend_out(title=None, *, ax=None)`,
so the axes bound to `title`. Nothing raises. Always write
`cns.take_legend_out(ax=ax)`.

**Rotated tick labels collide with the panel below** — a multipanel panel's
decoration reserve does not grow enough for steeply rotated labels. Add
`margin_bottom=` to the upper panel. Measured with 30-degree rotated species
names: `margin_bottom=15` still overlapped, `30` cleared it. Prefer shortening
category names over rotating them.

**An unrequested `P = ...` appeared on the figure** — some functions test
automatically. `cns.kdeplot` with a two-level `hue` runs a two-sample
Kolmogorov-Smirnov test and annotates it; `add_mode=False` does not disable it,
and three or more levels produce no annotation. Inspect `ax.texts`, then either
report that test by name in the caption or remove it deliberately:

```python
for text in list(ax.texts):
    if text.get_text().startswith("$P"):
        text.remove()
```

**Missing statistical annotations** — pass `pairs=[("A", "B")]` or `pairs="all"`
on functions that support it. The p-value method is printed to stdout; capture
it for the figure legend.

**Journal rejected the figure for low resolution** — `settings.savefig_dpi`
defaults to `288`, below the 300 dpi floor Cell, Nature, and Science all require.
Raise it: `with cns.settings.context(savefig_dpi=600):`. Note Cell wants 500 for
combination art and 1000 for raster line art, and Nature requires editable vector
for main figures rather than any raster at all. Run
`python3 $SKILL_DIR/scripts/journal_preset.py <journal>` and see
[journal-specs.md](journal-specs.md).

**Journal rejected the figure for oversized text** — `settings.title_fontsize`
defaults to `8`, which exceeds Nature's 7 pt cap for in-figure text (Cell allows
6-8, Science targets 7). Lower it with
`cns.settings.context(title_fontsize=7, legend_fontsize=6)`.

**Figure is the wrong physical width** — sizes are points (1/72 inch), so
convert the journal's millimetres: `pt = mm / 25.4 * 72`. Nature double column
183 mm is `max_width=519`, Cell 2-column 174 mm is `493`, Science full width
184 mm is `522`. Verified: `max_width=519` yields a 183.1 mm figure. The
installed `settings.multipanel_max_width=540` (190.5 mm) exceeds all three
journals' widest columns; set it explicitly.

A second trap sits behind that one: **the canvas width is not the saved width.**
`settings.savefig_bbox` defaults to `'tight'`, so `cns.savefig()` crops to the
drawn artists. Measured on a single `240x150` panel in a 519-point (183.1 mm)
canvas, the saved PDF was **93.1 mm** wide, not 183.1 — the 150-point panel plus
its margins and decorations is all that survived the crop. Trimming
`max_width` to hit a print width therefore under-delivers. From 0.8.0 the fix
is explicit:

```python
cns.savefig("figure.pdf", bbox_inches=None)   # keeps the full 183.1 mm canvas
```

Verified: the same figure with `bbox_inches=None` saves at 519.0 x 167.8 pt =
183.1 mm. Note `pad_inches` applies **only** to the tight path: raising it to
`0.5` grew the tight PDF from 92.6 to 118.0 mm wide, while the
`bbox_inches=None` output stayed at 183.1 mm. If the on-disk size must match the
journal's column width, set `bbox_inches=None` *and* check the result — a tight
crop is the default and silently rescales the page.

**Quantitative heatmap looks misleading in greyscale, or equal data steps look
unequal** — the installed `palette_seq='gnuplot'` is non-monotonic in perceptual
lightness (CIE L*) and collapses distinct values. Measured on mpl 3.10.9: across
16 samples, L\* falls from 41.4 to 37.9 through the mid-range before climbing
again (0.0, 16.2, 29.5, 38.0, **41.4, 40.6, 38.2, 37.9**, 41.1, 45.2, ...,
97.1), and the minimum adjacent step is `-0.16` L\* — 15 of 255 step pairs move
by less than 0.05. `viridis` over the same 16 samples is monotonic
(14.9 ... 90.9, max step 5.78). Override at script top:
`cns.settings.palette_seq = 'viridis'`. See
`$SKILL_DIR/scripts/recommended_overrides.py`.

**SVG text became outlines, or the warning about `mutool`** — install MuPDF
(`brew install mupdf-tools`) for Illustrator-optimized SVG post-processing.
Without it, output is a standard matplotlib SVG.

**Missing glyphs / CJK or unicode boxes** — call `cns.apply_unicode_font()` or
supply a font that covers the characters.

**Global style leaked into later figures** — wrap overrides in
`with cns.settings.context(...):` instead of assigning to `cns.settings`. From
0.8.0 the block also wraps `matplotlib.rc_context()`, so rcParams set inside it
are restored on exit too. Verified: `axes.linewidth` reads `1.5` inside
`context(axes_linewidth=1.5)` and `0.5` after, including on an exception path
and across nested contexts. Two things are *not* undone: backend changes and
font/colormap registrations.

**Colors indistinguishable** — switch `color_cycle` (`Ecotyper1`, `Cell`,
`Nature`, `Science`, `Set1`) and check greyscale/color-vision legibility for
categorical series. List the accepted names with
`python3 $SKILL_DIR/scripts/dump_style.py palettes`. Red-green pairs are the usual
offender: prefer blue-orange for a two-level contrast, or add a non-color
channel.

**The same category is a different color in different panels** — the hue order
came from each panel's data, so a panel missing a category shifts every color
after it. Define the order once and pass `hue_order=` on every panel that shares
the variable. For a subset panel, also pass a matching `color_cycle` built from
your category-to-color map. See [color-strategy.md](color-strategy.md).

**Diverging colormap looks misleading** — the scale is not centered, so the
midpoint color sits at an arbitrary value. Set `vmin`/`vmax` symmetrically about
the meaningful midpoint (usually 0) whenever you use `BuRd_custom`,
`OrBu_custom`, or `BlueRed` for signed values.

**`RuntimeError: Wrong Choice!` from `cns.palettes()`** — a sequential colormap
name was passed to a qualitative-palette function. `settings.palette_seq`
defaults to `'gnuplot'`, which `cns.palettes()` rejects. For continuous data use
`color_map=` on `cns.figure()` / `mp.panel()`, or `plt.get_cmap(name)`.

**Custom artist ignores the journal style** — you passed the property
explicitly. `fontsize=`, `frameon=`, `linewidth=` on spines, and
`tick_params(width=)` all override rcParams that cnsplots set. Omit them, or
read the value from `mpl.rcParams` / `cns.settings`. See
[rcparams.md](rcparams.md).

**Style silently reverted mid-script** — something called
`plt.style.use(...)` or `mpl.rcParams.update(mpl.rcParamsDefault)` after the
cnsplots setup, or another library reset the defaults on import. Check
`mpl.rcParams["axes.linewidth"]`: `0.5` means the style is active, `0.8` means it
was clobbered. Re-apply with `cns.setup_matplotlib()`.

**Labels shift between machines** — `font.sans-serif` is Helvetica-first with a
DejaVu Sans fallback. The fallback has different metrics, and multipanel measures
rendered decoration widths, so panel geometry differs where Helvetica is absent.

**Survival results look inverted** — verify the event column codes 1 = event,
0 = censored, and confirm the reference group and time units with the user.
