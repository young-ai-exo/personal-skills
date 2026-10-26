# cnsplots plot catalog

Select the narrowest fitting function, then verify its installed signature with
`python3 $SKILL_DIR/scripts/inspect_api.py <name>` before writing code.

## Distributions and group comparison

| Function | Use for |
| --- | --- |
| `boxplot` | quartiles/medians across categories; optional pairwise tests |
| `violinplot` | full distribution shape across categories |
| `stripplot` | individual observations, often overlaid on box/violin |
| `barplot` | group estimates as bars (with error bars) |
| `lollipopplot` | values with stems and markers, dense categories |
| `dumbbellplot` | two endpoints per category connected by a line |
| `histplot` | binned univariate or bivariate distributions |
| `kdeplot` | smoothed density estimates |
| `distplot` | compact combined distribution view |
| `ridgeplot` | stacked densities across many groups |
| `qqplot` | observed vs theoretical quantiles |

## Relationships and change

- `scatterplot`: relationship between numeric variables.
- `regplot`: fitted regression with confidence context.
- `lineplot`: trends or repeated measures over an ordered axis.
- `slopeplot`: paired change between two conditions or time points.

## Matrices and classification

- `heatmapplot`: annotated / hierarchically clustered matrices.
- `dotplot`: matrix values encoded by dot size + color (enrichment style).
- `confusionplot`: predicted vs observed classes.

`heatmapplot` and `dotplot` return backend-native plotter objects, not `Axes`.
Style them through their internal axes (`ax`, `ax_heatmap`, `hm_ax`, `cbar_ax`,
`dot_legend`, `ax_row_dendrogram`, `ax_col_dendrogram`, `ax_*_annotation`); note
`hm_ax` and `ax_heatmap` are different objects. See
[dense-figures.md](dense-figures.md).

## Proportions, sets, flows

- `stackplot`: categorical composition across groups (supports Fisher tests).
- `pieplot`, `donutplot`: parts of a whole, few categories only.
- `vennplot`: overlap among 2-3 sets; returns a matplotlib-venn object.
- `upsetplot`: scalable set intersections; returns panel axes.
- `sankeyplot`: flow between source and target categories.

## Survival and model summaries

- `survivalplot`: Kaplan-Meier curves, log-rank tests, pairwise hazard ratios.
  `p_adjust=` corrects the pairwise Cox family; `descriptive_only=True` drops the
  tests and keeps the curves.
- `get_survival_results(ax)`: detached DataFrame of what the latest
  `survivalplot` annotated — one row per estimate/test, `kind` in `overall`,
  `pairwise_cox`, `median_survival`, `landmark_survival`, `landmark_test`,
  `rmst`. `estimate` is the HR, median, survival probability, or RMST;
  `pvalue_raw`/`pvalue_adjusted` carry the correction. Does not rerun models.
- `cumulativeincidenceplot`: competing-risk cumulative incidence.
- `forestplot`: effect estimates with confidence intervals.
- `CoxModel`, `LogisticModel`: fitted models feeding the plots above.

Confirm event coding (1 = event vs censored), time units, reference group, and
requested contrasts before plotting.

`boxplot`, `violinplot`, `barplot`, `lollipopplot`, and `stackplot` accept
`pairs=` (plus `test=` and `p_adjust=`); `get_comparison_results(ax)` returns the
comparison table for the latest such call on that axes — `group1`, `group2`,
`test`, `alternative`, `paired`, `n1`, `n2`, `pvalue_raw`,
`pvalue_adjusted`, `p_adjust`, `pvalue_annotation`, `significant`,
`annotation`. It reads the rendered annotation, so it does not rerun the tests,
and a later plot without `pairs=` does not replace it. The continuous plots take
`test=` of `'Mann-Whitney'`, `'t-test_welch'`, `'t-test_paired'`, or
`'Wilcoxon'` — `Mann-Whitney` is the default on `boxplot` and `violinplot`,
`t-test_welch` on `barplot` and `lollipopplot`. The two paired choices need
`subject=` naming the column that pairs observations; without it the call raises
`ValueError`.

## Genomics and evaluation

- `volcanoplot`: effect size vs transformed adjusted significance.
- `gseaplot` / `prerank`: gene-set enrichment results.
- `rocplot`: ROC curves with AUC; `pairs=` / `p_adjust=` test AUC differences,
  `ci_show=` adds pointwise bands. `get_roc_results(ax)` returns a `ROCResults`
  dict of DataFrames keyed `curves`, `metrics`, `bands`, `comparisons`
  (`bands` and `comparisons` are empty unless requested).
- `precisionrecallplot`: PR curves with average precision;
  `get_precision_recall_results(ax)` returns `curves` and `metrics`.
- `calibrationplot`: reliability bins with Brier score;
  `get_calibration_results(ax)` returns `bins` and `metrics`.
- `phyloplot`: phylogenetic visualization from `AnnData`.

The three `get_*_results` accessors read a snapshot the plot already computed;
they do not rerun the analysis, and they return empty tables with the right
columns when no matching plot was drawn on that axes.

Never infer log transforms or significance cutoffs; read the installed
signature for the exact expected columns.

## Composition, style, export

Figure and layout:

- `figure(width, height, color_cycle=..., color_map=..., *, unit="pt")`:
  point-sized canvas (1 pt = 1/72 inch). Applies the full style and **returns the
  `Figure`**, which also becomes the current figure. An omitted dimension falls
  back to the matching `settings` value in points, whatever `unit` is; `unit`
  only rescales the numbers you pass (`unit="mm"` is millimetres).
- `multipanel(max_width=..., title=..., loc=..., title_fontweight=..., *, unit="pt")`
  with `.panel(...)`, `.newline()`, `.get_axes(label)`, `.fig`, `.axes`.
  Same `unit` contract; panels can override it per call.
- `add_panel_label(name, pad_left, pad_top)`: labels the **current** axes; there
  is no `ax` parameter, so call `plt.sca(ax)` first.
- `savefig(path, *, fig=None, dpi=None, transparent=None, bbox_inches=...,
  pad_inches=None)` (alias `save`): saves and creates parent directories. Every
  argument is keyword-only. Omitted ones fall back to `settings`
  (`savefig_dpi=288`, `savefig_transparent`, `savefig_bbox="tight"`).
  `bbox_inches=None` saves the **full canvas** instead of cropping to the
  artists; `"tight"` crops; a `Bbox` fixes a region in inches.

Style:

- `setup_matplotlib`, `setup_ax`, `setup_scanpy`: apply cnsplots styling to
  figures built with other libraries, and all return `None`.
  `setup_ggplot()` is different: it returns an R `theme()` code string to paste
  into a ggplot2 script, and touches no matplotlib state.
- `settings.context(...)`: scoped style overrides. `settings.reset()`: restore
  defaults.
- `take_legend_out(title=None, *, ax=None)`: `ax` is keyword-only.
- `apply_unicode_font()`: CJK and symbol coverage.

Color:

- `palettes(name_or_list)`: returns RGB float tuples for **qualitative** names
  only; the 5 sequential/diverging names return `LinearSegmentedColormap`
  objects instead (see below). Plain matplotlib names such as `gnuplot` raise
  `RuntimeError`.
- `available_palettes(kind=None)`: list every name `palettes()` accepts; `kind`
  is `"qualitative"` or `"continuous"`. Includes user palettes in registration
  order. 28 qualitative and 5 continuous built-ins on 0.8.0.
- `register_palette(name, colors)`: add a qualitative palette for the session;
  the name then works in `color_cycle=` and `palettes()`.
- `get_palette_colors(indices, palette=None)`: specific colors, as hex strings.
  `palette=None` means `Set1`, not the active palette.
- `get_hexcolors_from_apalette(indices, palette=None)`: compat wrapper that
  forwards to `get_palette_colors` and returns the same list.
- Constants: `RED`, `BLUE`, `GREEN`, `ORANGE`, `PURPLE`, `YELLOW`, `PINK`, `GRAY`,
  `BROWN`, `VIOLET`, `CHOCOLATE`. Seven of the eleven are `Ecotyper1` members —
  `RED` [0], `BLUE` [1], `GREEN` [2], `PURPLE` [3], `ORANGE` [4], `YELLOW` [5],
  `GRAY` [6]. `PINK`, `BROWN`, `VIOLET`, and `CHOCOLATE` are **not** in it and
  read as non-palette colors.

Choosing and coordinating colors across panels:
[color-strategy.md](color-strategy.md).

Models and data:

- `CoxModel`, `LogisticModel`: fitted models feeding `forestplot` and survival
  plots.
- `prerank`: GSEA prerank input for `gseaplot`.
- `datasets.load_dataset(name)` for built-in demo frames;
  `datasets.get_showcase_data`; `datasets.gallery` is a submodule.
- `placeholderplot(description, *, ax=None)`: draw a captioned placeholder in a
  panel whose real content does not exist yet.
- `utils`, `validation`, `methods`: helper namespaces.

Names accepted by `palettes()`, probed against 0.8.0. Qualitative (28):
`Ecotyper1`-`Ecotyper6`, `Cell`, `Nature`, `Science`, `NEJM`, `Lancet`, `JAMA`,
`JCO`, `OkabeIto`, `TolBright`, `TolMuted`, `Tableau`, `Bold`, `ECharts`,
`Set1`-`Set3`, `Pastel1`, `Pastel2`, `Paired`, `Dark2`, `Accent`, `BlueRed`.
Use `cns.available_palettes("qualitative")` for the live list. Continuous (5),
which return a colormap object and therefore are **not** usable as a
`color_cycle`: `BuRd_custom`, `OrBu_custom`, `WhYlOrRd_custom`, `YlGnBu_custom`,
`parula` — each raises `ValueError` as a cycle. Route them through `color_map=` or
`cmap=`. `BlueRed` is the one diverging name that *is* a qualitative list (6
colors) and does work as a `color_cycle`. Plain matplotlib colormap names are
**rejected** by `palettes()`: `gnuplot`, `viridis`, and `Blues` all raise
`RuntimeError`. Re-probe with `python3 $SKILL_DIR/scripts/dump_style.py palettes`.

Full style contract: [rcparams.md](rcparams.md) and
[settings-catalog.md](settings-catalog.md).

### Layout skeletons

Pick the engine deliberately; see
[composition-patterns.md](composition-patterns.md) for why these are not
interchangeable, and start from `templates/`.

```python
import matplotlib

matplotlib.use("Agg")

import cnsplots as cns

mp = cns.multipanel(max_width=540)

ax_a = mp.panel("A", width=150, height=150)
cns.boxplot(data=grouped, x="group", y="value", ax=ax_a)

ax_b = mp.panel("B", width=150, height=150)
cns.scatterplot(data=continuous, x="x", y="y", ax=ax_b)

cns.savefig("outputs/multipanel.svg")
```

For a uniform repeated grid use `cns.figure(...)` plus `fig.subplots(...)` on the
returned figure (`axes = cns.figure(width=340, height=240).subplots(2, 2)`)
instead; `multipanel` does not align panel edges.
