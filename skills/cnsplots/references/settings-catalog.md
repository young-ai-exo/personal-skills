# cnsplots settings catalog

`cns.settings` holds the defaults that `setup_matplotlib()` and `cns.figure()`
translate into rcParams, plus the layout constants `multipanel` reads. Most
`settings.*` fields map onto the rcParam of the same name with dots replaced by
underscores (`axes_linewidth` to `axes.linewidth`); the `panel_*`,
`multipanel_*`, `pvalue_*`, `legend_out_*`, `ggplot_*`, and `scanpy_*` groups
have no rcParam counterpart and are read directly by cnsplots.

**Never trust a value copied from documentation.** Dump the installed truth:

```bash
python3 $SKILL_DIR/scripts/dump_style.py settings
```

Values below are measured from **cnsplots 0.8.0**.

## Usage

```python
import cnsplots as cns

cns.settings.palette_qual = "Tableau"          # persistent, leaks to later figures
cns.settings.reset()                           # back to package defaults

with cns.settings.context(palette_qual="Set2", figure_width=300):
    cns.figure()                               # scoped; restored on exit
    ...
```

Prefer `context(...)` in any script that produces more than one figure. Verified:
`palette_qual` returns to `Ecotyper1` after the block exits.

## Figure defaults

Consumed when you call `cns.figure()` with no explicit size. Sizes are
**points** (1/72 inch); see [rcparams.md](rcparams.md) for the point-to-inch
contract. A dimension you omit always takes the value here **in points**, even
when you pass `unit=`: `cns.figure(height=60, unit="mm")` is 60 mm tall but
150 points (52.9 mm) wide, not 150 mm.

| Setting | Value |
| --- | --- |
| `figure_width` | `150` |
| `figure_height` | `150` |
| `figure_dpi` | `144` |

## Panel and multipanel layout

`panel_*` are the per-panel defaults for `mp.panel()`; `multipanel_*` apply to
the container. Note `panel_margin_bottom` and `panel_margin_right` default to
`10`, so panels are **not** flush by default.

| Setting | Value |
| --- | --- |
| `panel_width` | `150` |
| `panel_height` | `150` |
| `panel_pad_left` | `0` |
| `panel_pad_top` | `0` |
| `panel_margin_top` | `0` |
| `panel_margin_bottom` | `10` |
| `panel_margin_left` | `0` |
| `panel_margin_right` | `10` |
| `panel_label_fontname` | `None` |
| `panel_label_fontweight` | `'bold'` |
| `multipanel_max_width` | `540` |
| `multipanel_title_loc` | `'center'` |
| `multipanel_title_height_min` | `12` |
| `multipanel_title_height_pad` | `4` |

`pad_left` / `pad_top` add to an internally measured reserve for axis
decorations rather than replacing it, which is why they cannot be used to force
panels into alignment. See [composition-patterns.md](composition-patterns.md).

As of 0.8.0 these tables mix three units, and only the first group responds to
`unit=`:

- **Points, scaled by `unit=` when supplied explicitly** — `figure_width`,
  `figure_height`, `multipanel_max_width`, `panel_width`, `panel_height`.
  Verified: `mp.panel(width=2, unit="in")` and `width=50.8, unit="mm"` both land
  at 144 points of axes width.
- **Points, never scaled** — every `panel_margin_*`, and the default for an
  omitted dimension. Verified: `margin_right=2` stores `2` under `pt`, `in`, and
  `mm` alike, and omitting `panel_width` gives `150` points even when the
  multipanel was built with `unit="mm"`.
- **Display pixels, never scaled** — `panel_pad_left`, `panel_pad_top`. These
  are rendered-pixel offsets added on top of the measured decoration
  width/height.

So `unit=` moves the axes box and the canvas, not the gaps around them. Measured:
`pad_left=20` on a panel whose decorations already reserve 52.5 px took the left
reserve from 32.0 to 42.0 points, and `pad_left=40` to 52.0 — the `pad_left` is
added, never substituted. Verified panel axis size is exact too:
a `width=150, height=90` panel measures 300x180 rendered px at 144 dpi, i.e.
exactly 150x90 points.

## Palettes

| Setting | Value |
| --- | --- |
| `palette_qual` | `'Ecotyper1'` |
| `palette_seq` | `'gnuplot'` |

`palette_qual` feeds `axes.prop_cycle`; `palette_seq` feeds `image.cmap`. Only
`palette_qual`-style names are valid arguments to `cns.palettes()`.

## Typography

| Setting | Value |
| --- | --- |
| `font_family` | `'sans-serif'` |
| `font_sans_serif` | `('Helvetica', 'Helvetica Neue', 'Arial', 'Nimbus Sans', 'Liberation Sans', 'DejaVu Sans')` |
| `mathtext_fontset` | `'custom'` |
| `title_fontsize` | `8` |
| `title_fontweight` | `'bold'` |
| `legend_fontsize` | `7` |
| `legend_title_fontsize` | `None` |

`legend_title_fontsize = None` means "inherit `title_fontsize`", which is why
the measured `legend.title_fontsize` rcParam is `8.0`.

## Axes and ticks

| Setting | Value |
| --- | --- |
| `axes_linewidth` | `0.5` |
| `axes_edgecolor` | `'black'` |
| `axes_labelcolor` | `'black'` |
| `axes_labelpad` | `2` |
| `axes_titlelocation` | `'center'` |
| `axes_titlepad` | `4` |
| `axes_spines_top` | `False` |
| `axes_spines_right` | `False` |
| `axes_grid` | `False` |
| `axes_xmargin` | `0.05` |
| `axes_ymargin` | `0.05` |
| `xtick_major_size` / `ytick_major_size` | `2` |
| `xtick_major_width` / `ytick_major_width` | `0.6` |
| `xtick_major_pad` / `ytick_major_pad` | `1` |
| `xtick_color` / `ytick_color` | `'black'` |
| `xtick_bottom` / `ytick_left` | `True` |
| `xtick_labelrotation` / `ytick_labelrotation` | `0` |
| `xtick_alignment` | `'center'` |
| `ytick_alignment` | `'center_baseline'` |

## Legend

| Setting | Value |
| --- | --- |
| `legend_frameon` | `False` |
| `legend_markerscale` | `0.5` |
| `legend_handlelength` | `0.7` |
| `legend_handleheight` | `0.7` |
| `legend_handletextpad` | `0.3` |
| `legend_out_loc` | `'upper left'` |
| `legend_out_bbox_to_anchor` | `(1, 1.02)` |
| `legend_out_markerscale` | `1` |

`legend_out_*` are used by `cns.take_legend_out(title=None, *, ax=None)`. `ax`
is keyword-only: `take_legend_out(ax)` does not raise, it sets the legend
*title* to the axes repr string. Always write `take_legend_out(ax=ax)`.

## Statistical annotation

| Setting | Value |
| --- | --- |
| `pvalue_loc` | `'inside'` |
| `pvalue_format` | `'star'` |
| `pvalue_fontsize` | `'small'` |
| `annotation_auto_contrast` | `True` |

`pvalue_format='star'` prints significance stars. The accepted values are
`'star'`, `'threshold'`, and `'full'` (`_P_VALUE_FORMATS` in `_settings.py`);
anything else raises. Use `'threshold'` or `'full'` when a reviewer needs exact
p-values. `pvalue_loc` accepts only `'inside'` and `'outside'`
(`_P_VALUE_LOCS`). Both are validated on assignment, so a typo fails
immediately rather than at draw time.

## Export

| Setting | Value |
| --- | --- |
| `savefig_dpi` | `288` |
| `savefig_bbox` | `'tight'` |
| `savefig_pad_inches` | `0.01` |
| `savefig_transparent` | `True` |
| `svg_fonttype` | `'none'` |
| `pdf_fonttype` | `42` |

## Third-party integration

| Setting | Value |
| --- | --- |
| `scanpy_figsize` | `(2.5, 2.5)` |
| `scanpy_facecolor` | `'none'` |
| `scanpy_use_default_style` | `False` |
| `ggplot_font_family` | `'sans'` |
| `ggplot_font_face` | `'plain'` |
| `ggplot_fontsize` | `10` |
| `ggplot_text_color` | `'black'` |
| `setup_ax_colorbar_label` | `'FDR q-val'` |
| `verbosity` | `1` |

Applied through `cns.setup_scanpy()` and `cns.setup_ggplot()`. Note
`setup_ax_colorbar_label` defaults to `'FDR q-val'`, and `cns.setup_ax(ax)`
relabels whatever colorbar it finds to that: verified, an unlabelled scatter
colorbar became `'FDR q-val'` after a bare `setup_ax(ax)`. Pass
`colorbar_label="Expression"` — or `""` to leave it blank — explicitly.

The lookup is `ax.collections[0].colorbar`, so it only fires for colormapped
**collections** (scatter with `c=`), not `imshow` / `pcolormesh` images, which
live in `ax.images` and are left alone.
