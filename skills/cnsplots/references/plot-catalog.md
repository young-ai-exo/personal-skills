# Plot Functions Catalog & Capabilities Reference

Comprehensive reference for selecting and configuring plotting functions in `cnsplots`.
Before writing code, verify the real installed signature with:
```bash
python3 $SKILL_DIR/scripts/inspect_api.py <function_name>
```

---

## 1. Distributions & Group Comparisons

| Function | Primary Use Case | Key Parameters & Statistical Highlights |
| :--- | :--- | :--- |
| `boxplot` | Quartiles, medians, and outliers across categories | `pairs=[("A", "B")]` or `"all"`, `test="Mann-Whitney"`, `"t-test_welch"`, `"t-test_paired"`, `"Wilcoxon"`, `p_adjust="holm"`, `add_count=True`, `showoutliers=False`. |
| `violinplot` | Full distribution density shape across categories | `pairs=` supported, `width=0.6`, `add_box=True`, `add_count=True`; pass `inner_kws`/`linewidth` through `**kwargs` for violin styling. |
| `stripplot` | Individual observation points, often overlaid on box/violin | `jitter=0.2`, `size=2` (default), `alpha=0.6`. |
| `barplot` | Group means (error bars are not displayed by default) | `pairs=` supported (defaults to Welch's t-test), `add_tip=True` to label means. |
| `lollipopplot` | Stem-and-marker plot for dense categories | `pairs=` supported, default `markersize=20`, cleaner than bar plots for >10 categories. |
| `dumbbellplot` | Two paired endpoints per category connected by a line | Shows before/after or condition contrasts clearly. |
| `histplot` | Binned univariate or bivariate distributions | e.g. `bins=20`, `kde=True`, `element="step"`; `bins` defaults to `"auto"`. |
| `kdeplot` | Continuous smoothed kernel density estimates | *Note: 2-level hue automatically annotates a two-sample Kolmogorov-Smirnov test ($P = ...$). Clean if unrequested.* |
| `ridgeplot` | Stacked joyplot/ridgeline densities across many groups | Compact visualization for 5–20 categorical groups. |
| `qqplot` | Observed vs theoretical quantiles | Normality assessment. |

---

## 2. Relationships, Trends & Regression

| Function | Primary Use Case | Key Parameters |
| :--- | :--- | :--- |
| `scatterplot` | Correlation between two continuous variables | `s=7` (default marker size), `hue=`, `hue_order=`, `alpha=0.8`. |
| `regplot` | Scatterplot with fitted linear/polynomial regression line | `order=1`, `ci=95`, default `s=3` (not the scatterplot default of 7). |
| `lineplot` | Time series or ordered longitudinal trends | `err_style="band"`, `markers=True`. |
| `slopeplot` | Paired change across two time points or treatments | Highlights direction and magnitude of individual shifts. |

---

## 3. Matrices, Heatmaps & Enrichment

| Function | Primary Use Case | Return Type & Axis Details |
| :--- | :--- | :--- |
| `heatmapplot` | Annotated, hierarchically clustered matrix | **Returns `ClusterMapPlotterNew`** (not `Axes`). After rendering, use `.ax_heatmap`, `.ax_row_dendrogram`, `.ax_col_dendrogram`, and `.cbars` (a list of `Colorbar` objects); there is no `.cbar_ax` attribute. |
| `dotplot` | Matrix where size encodes frequency and color encodes intensity | **Returns `DotClustermapPlotterNew` object**. Internal handles: `.ax`, `.cbar_ax`, `.dot_legend`. |
| `confusionplot` | Classification predicted vs observed confusion matrix | Returns `Axes` with normalized counts and annotations. |

> [!IMPORTANT]
> `heatmapplot` and `dotplot` delegate their color legends to PyComplexHeatmap, which defaults every colorbar to `extend="both"` (triangular caps). The house default is square: pass `legend_kws={"extend": "neither"}` to `heatmapplot` and `cmap_legend_kws={"extend": "neither"}` to `dotplot`. Add `extend="both"` back only when the user asks to flag out-of-range values.

---

## 4. Proportions, Sets & Flow

| Function | Primary Use Case | Key Parameters |
| :--- | :--- | :--- |
| `stackplot` | Proportional composition across categories | Accepts `pairs=`; `test='auto'` by default (Fisher exact for a 2x2 table, chi-squared otherwise). |
| `vennplot` | Overlap among 2 or 3 sets | Returns `matplotlib-venn` object. Best for $\le 3$ sets. |
| `upsetplot` | Scalable set intersections | Returns panel axes. The publication standard for $\ge 4$ intersecting sets. |
| `sankeyplot` | Flow network between source and target categories | Visualizes transitions and allocation proportions. |

---

## 5. Survival, Clinical & Model Summaries

| Function | Primary Use Case | Statistical Highlights |
| :--- | :--- | :--- |
| `survivalplot` | Kaplan-Meier survival curves | Log-rank test p-values, pairwise hazard ratios (`p_adjust=`), at-risk table. `descriptive_only=True` suppresses tests. |
| `cumulativeincidenceplot` | Competing-risk cumulative incidence | Gray's test for subdistribution hazards. |
| `forestplot` | Effect estimates (odds/hazard ratios) with 95% CIs | Displays point estimates, confidence bars, and reference null line. |
| `CoxModel`, `LogisticModel` | Regression models directly feeding the plots above | Programmatic model fitting. |

---

## 6. Genomics & Model Evaluation

| Function | Primary Use Case | Key Parameters |
| :--- | :--- | :--- |
| `volcanoplot` | Differential expression: fold change vs significance | `fold_change_threshold=0.5`, `pvalue_threshold=0.05`, `n_show=10`, automated gene labeling. |
| `gseaplot` | Gene Set Enrichment Analysis running enrichment score | Peak ES line, hit bar, rank metric ranking plot. |
| `rocplot` | Receiver Operating Characteristic (ROC) curves | Displays AUC, pointwise confidence intervals, pairwise AUC contrast tests. |
| `precisionrecallplot` | Precision-Recall (PR) curves | Average Precision (AP) metrics, ideal for imbalanced classification. |
| `calibrationplot` | Probability reliability diagrams | Brier score, calibration curve with perfect calibration diagonal. |

---

## 7. Statistical Result Accessors (Non-Destructive)

Never attempt to parse p-values or sample counts from drawn text labels. Use `cnsplots` built-in programmatic accessors:

### Group Comparisons (`boxplot`, `violinplot`, `barplot`, `lollipopplot`, `stackplot`)
```python
stats_df = cns.get_comparison_results(ax)
# Columns (13): ['group1', 'group2', 'test', 'alternative', 'paired', 'n1', 'n2',
#                'pvalue_raw', 'pvalue_adjusted', 'p_adjust',
#                'pvalue_annotation', 'significant', 'annotation']
```

### Survival Analysis (`survivalplot`)
```python
survival_df = cns.get_survival_results(ax)
# Detached DataFrame containing median survival, landmark survival rates, hazard ratios, and log-rank p-values.
```

### Diagnostic Evaluation (`rocplot`, `precisionrecallplot`, `calibrationplot`)
```python
roc_results = cns.get_roc_results(
    ax
)  # dict with 'curves', 'metrics', 'bands', 'comparisons'
pr_results = cns.get_precision_recall_results(ax)
cal_results = cns.get_calibration_results(ax)
```
