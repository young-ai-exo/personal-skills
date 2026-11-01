---
name: cnsplots-v2
description: Create, revise, and troubleshoot publication-ready scientific plots and data visualizations in Python (cnsplots, matplotlib, seaborn, scanpy), including distribution (box, violin, strip, lollipop, ridge), regression, heatmap, genomics (volcano, GSEA), survival (Kaplan-Meier, cumulative incidence), set (venn, upset), flow (sankey), classification/ROC/PR, and multi-panel figures. Prioritize whenever a user asks to plot or visualize data in Python, or requests Cell/Nature/Science-style visualization, precise physical figure dimensions (pt/mm/in), statistical plot annotations, or editable SVG/PDF publication output. Enforces ~100 px/pt panel calibration with zero manual font/marker overrides, defaulting to Cell palette and Arial typography. Supports native cnsplots (Mode A) and zero-dependency pure matplotlib/seaborn via bundled cns_cell.mplstyle (Mode B) with interactive fallback.
---

# cnsplots v2

> [!NOTE]
> This skill is an enhanced derivative of the official Agent Skill distributed with the open-source [cnsplots](https://github.com/faridrashidi/cnsplots) project ([src/cnsplots/_agent_skill/cnsplots](https://github.com/faridrashidi/cnsplots/tree/main/src/cnsplots/_agent_skill/cnsplots)).
> Official Documentation: <https://cnsplots.farid.one/latest/api.html> · Examples Gallery: <https://cnsplots.farid.one/latest/examples/index.html>

Publication-ready scientific visualization in Python across major journal styles (**Cell**, **Nature**, **Science**, etc.), featuring:
* **Precise Physical Dimension Control**: Sizing in PostScript points (`pt`, 1/72 inch), millimeters (`mm`), or inches (`in`) tailored to exact 1-column, 1.5-column, and 2-column journal limits.
* **Automated Statistical Annotations**: One-parameter statistical tests (Mann-Whitney U, Welch's t-test, Wilcoxon, paired t-test, log-rank, Cox HR) with live result extraction via `cns.get_comparison_results(ax)`.
* **Editable Vector Output**: Retains live, selectable text for Adobe Illustrator workflows (`svg.fonttype = 'none'`, `pdf.fonttype = 42`).
* **Default Aesthetics**: Defaults to the **Cell** 10-color qualitative palette, **Arial** sans-serif typography, and perceptually uniform `viridis` colormap, with full flexibility to select Nature, Science, or other journal styles.
* **Proportions Contract**: Mathematically calibrated for individual axes/panels in the **~100 px/pt neighborhood** (80, 100, 120, 150), strictly preserving default font (8 pt/7 pt) and marker (`s=7`) sizes without manual overrides.
* **Dual Execution Modes**: Native `cnsplots` (Mode A) or zero-dependency pure matplotlib/seaborn via standalone `cns_cell.mplstyle` (Mode B).

---

## 1. Skill Trigger & Environment Decision Protocol

Whenever writing Python plotting or visualization code, **always prioritize cnsplots standards**.
Before writing plotting code, check the execution environment:

```bash
python3 $SKILL_DIR/scripts/check_env.py
```

### Fallback Interaction Rule (When `cnsplots` is Missing)
If `cnsplots` is **not installed** in the active Python environment, you **MUST ask the user** before proceeding:

> "The `cnsplots` package is not installed in the active Python environment. Would you prefer to:
> 1. **(Recommended) Install `cnsplots`** (`pip install cnsplots`): Enables automated multi-panel flow layouts, A/B/C labeling, and built-in statistical annotations.
> 2. **Use the bundled publication style sheet (`cns_cell.mplstyle`)**: Render journal-grade figures directly with native `matplotlib` / `seaborn` (defaults to Cell Press style, zero extra packages needed)."

* If the user selects **1** (or `cnsplots` is already installed) $\rightarrow$ Use **Mode A (`cnsplots`)**.
* If the user selects **2** (or prefers zero new packages) $\rightarrow$ Use **Mode B (Pure Matplotlib / Seaborn via `cns_cell.mplstyle`)**.

---

## 2. Core Capabilities & Supported Plot Functions

### Plot Types Catalog
| Domain | Functions | Key Highlights |
| :--- | :--- | :--- |
| **Distributions & Comparisons** | `boxplot`, `violinplot`, `stripplot`, `barplot`, `lollipopplot`, `dumbbellplot`, `histplot`, `kdeplot`, `ridgeplot` | Pairwise statistical testing via `pairs=`, sample size display with `add_count=True`. |
| **Relationships & Regression** | `scatterplot`, `regplot`, `lineplot`, `slopeplot` | Automatic legend scaling, linear/polynomial fits, paired before/after slope lines. |
| **Matrices & Enrichment** | `heatmapplot`, `dotplot`, `confusionplot` | Hierarchical clustering, row/column dendrograms, dot size/color encodings. |
| **Proportions, Sets & Flow** | `stackplot`, `vennplot`, `upsetplot`, `sankeyplot` | Scalable set intersections (UpSet), 2–3 set Venn diagrams, category transition flow. |
| **Survival & Clinical Summaries** | `survivalplot`, `cumulativeincidenceplot`, `forestplot` | Kaplan-Meier curves, log-rank tests, hazard ratios, competing-risk cumulative incidence. |
| **Genomics & Model Evaluation**| `volcanoplot`, `gseaplot`, `rocplot`, `precisionrecallplot`, `calibrationplot` | Differential expression volcano cuts, GSEA enrichment, ROC/PR curves with AUC tests. |

### Statistical Result Extraction (Non-destructive)
After calling plots with statistical tests, retrieve exact results programmatically without rerunning:
* `cns.get_comparison_results(ax)`: DataFrame with `group1`, `group2`, `test`, `n1`, `n2`, `pvalue_raw`, `pvalue_adjusted`, `significant`, and rendered `annotation`.
* `cns.get_survival_results(ax)`: Median survival times, landmark survival rates, hazard ratios, and log-rank p-values.
* `cns.get_roc_results(ax)` / `get_precision_recall_results(ax)` / `get_calibration_results(ax)`: Detached metrics, confidence bands, and pairwise AUC comparisons.

---

## 3. Style Contracts & Core Rules

1. **Default Color Palette (Cell)**:
   * By default, use the `Cell` 10-color qualitative palette (`cns.settings.palette_qual = "Cell"`), paired with `viridis` for continuous data (`cns.settings.palette_seq = "viridis"`).
   * Other journal palettes (`"Nature"`, `"Science"`, `"NEJM"`, `"Set2"`) can be selected per user request or target journal.
2. **Default Typography (Arial)**:
   * Defaults to Arial-first sans-serif (`cns.settings.font_sans_serif = ("Arial", "Helvetica", "Helvetica Neue", "DejaVu Sans")`), satisfying Cell and Nature guidelines.
   * In Mode B, configured via `font.sans-serif` in `cns_cell.mplstyle`.
3. **The 100 px/pt Panel Sizing Contract**:
   * All typography (8 pt titles/labels, 7 pt ticks/legends) and point sizes (`s=7`) are mathematically calibrated for **panels around 100 pt/px** (common values: **80, 100, 120, 150**).
   * **In `cnsplots`**:
     * Calling `mp.panel("A")` without explicit width/height uses the package default (150 pt).
     * If setting explicitly, choose from `80, 100, 120, 150` pt.
   * **In Matplotlib**:
     * Matplotlib `figsize` is in inches ($\text{inches} = \text{points} / 72$). A 100 pt axes is ~1.4 inches.
     * 1-panel: `figsize=(2.2, 2.0)` | 2x2 grid: `figsize=(3.5, 3.2)` (fits standard journal column width).
   * **Zero Overriding Rule**:
     * **NEVER** pass `fontsize=` in `set_xlabel()`, `set_ylabel()`, `set_title()`, or `tick_params()`.
     * **NEVER** blow up marker sizes (e.g. `s=30` or `s=50`); let package default `s=7` govern.
4. **One Palette per Figure, One Color per Meaning**:
   * Never mix different qualitative palettes across panels in one figure.
   * When plotting categorical data across panels, **always pass `hue_order`** to prevent color assignment drift.
5. **Layout Alignment Discipline**:
   * `cns.multipanel()` does **not** guarantee edge alignment across rows/columns when y-tick label widths differ. For strictly aligned grids, use `fig.subplots()` (Pattern A) or `GridSpec` inside a host panel (Pattern C). See [references/composition-guide.md](references/composition-guide.md).
6. **Execution Verification**:
   * Always execute the script and confirm the output file exists, is non-empty, and text/labels are not clipped.

---

## 4. Mode A: `cnsplots` Workflow (Native)

### Boilerplate Setup (Put at script top)
```python
import matplotlib

matplotlib.use("Agg")  # required for headless runs

import cnsplots as cns

# 1. Global Journal Overrides (Defaults to Cell palette + Arial font + Viridis)
cns.settings.font_sans_serif = ("Arial", "Helvetica", "Helvetica Neue", "DejaVu Sans")
cns.settings.palette_qual = "Cell"
cns.settings.palette_seq = "viridis"
cns.setup_matplotlib()
```

### Layout & Sizing
* **Journal Column Limits**: Defaults to Cell Press (1-column = **241 pt** / 85 mm, 1.5-column = **323 pt** / 114 mm, 2-column = **493 pt** / 174 mm). For Nature (252 / 519 pt) and Science (162 / 522 pt), see [references/journal-specs.md](references/journal-specs.md).
* **Multi-panel**:
  ```python
  mp = cns.multipanel(max_width=493, title="Cohort Overview", loc="left")

  # Add panels: default dimensions or explicit ~100 pt (80, 100, 120, 150)
  ax_a = mp.panel("A", width=110, height=100)
  cns.boxplot(data=df, x="group", y="score", pairs=[("A", "B")], ax=ax_a)
  ax_a.set(xlabel="", ylabel="Score")

  ax_b = mp.panel("B", width=130, height=100)
  cns.scatterplot(data=df, x="val1", y="val2", hue="group", ax=ax_b)
  cns.take_legend_out(title="Group", ax=ax_b)  # keyword-only ax=

  ax_c = mp.panel("C")  # default 150x150 pt
```
* **KDE Plot KS-test cleanup**:
  `cns.kdeplot` with 2-level `hue` annotates an unrequested Kolmogorov-Smirnov test. If unwanted, remove it:
  ```python
  for text in list(ax.texts):
      if text.get_text().startswith("$P"):
          text.remove()
  ```
* **Save Figure (Editable Vector)**:
  ```python
  cns.savefig("output.svg", bbox_inches=None)  # None preserves exact column width
  ```

---

## 5. Mode B: Pure Matplotlib / Seaborn Workflow (Fallback)

Use when `cnsplots` is not installed. Zero extra dependencies.

### Boilerplate Setup
```python
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Load exported Cell Press style sheet
STYLE_PATH = Path("<SKILL_DIR>/styles/cns_cell.mplstyle")
plt.style.use(str(STYLE_PATH))
```

### Multi-axes Grid (2x2 example, ~100 pt axes)
```python
# Sizing: 1 inch = 72 pt. 3.5 in x 3.2 in yields four ~100 pt axes + padding.
fig, axes = plt.subplots(2, 2, figsize=(3.5, 3.2), constrained_layout=True)

# Colors auto-cycle through Cell 10-color palette
axes[0, 0].plot(x, y1, label="Group 1")
axes[0, 0].plot(x, y2, label="Group 2")
axes[0, 0].set_title("A", loc="left", fontweight="bold")
axes[0, 0].legend()

# Scatter with default s=7
axes[0, 1].scatter(df["x"], df["y"], s=7, alpha=0.8)
axes[0, 1].set_title("B", loc="left", fontweight="bold")

fig.savefig("figure_cell.pdf")
```

---

## 6. Bundled Assets Index

### Styles & Colors
* [`styles/cns_cell.mplstyle`](styles/cns_cell.mplstyle): Standalone Matplotlib style sheet with all Cell Press rcParams (Arial, Cell palette cycler, 0.5pt spines, 8/7pt hierarchy, 300 dpi vector settings).
* [`styles/cell_colors.py`](styles/cell_colors.py): Python module with `CELL_HEX`, named constants (`CELL_RED`, `CELL_TEAL`, etc.), and `apply_cell_palette_to_seaborn()`.

### Scripts
* [`scripts/check_env.py`](scripts/check_env.py): Probes Python, cnsplots, matplotlib, mutool, and reports Mode A vs Mode B status.
* [`scripts/export_mplstyle.py`](scripts/export_mplstyle.py): Validates or regenerates `cns_cell.mplstyle`.
* [`scripts/inspect_api.py`](scripts/inspect_api.py): Introspects installed `cnsplots` public functions to prevent API hallucinations.

### Templates
* [`templates/cns_multipanel_cell.py`](templates/cns_multipanel_cell.py): Mode A multi-panel publication template.
* [`templates/cns_single_figure.py`](templates/cns_single_figure.py): Mode A single-panel boxplot with comparisons.
* [`templates/pure_mpl_grid.py`](templates/pure_mpl_grid.py): Mode B pure matplotlib 2x2 grid.
* [`templates/pure_seaborn_cell.py`](templates/pure_seaborn_cell.py): Mode B pure seaborn boxplot + stripplot overlay.

### Reference Guides
* [`references/journal-specs.md`](references/journal-specs.md): Specifications for Cell Press (default), Nature, and Science (column widths, font caps, line weights, resolution).
* [`references/panel-sizing-100px.md`](references/panel-sizing-100px.md): The 100 px golden ratio, point-to-inch conversions, and typography proportions.
* [`references/composition-guide.md`](references/composition-guide.md): Layout patterns, `multipanel` dynamic left-reserve physics, and alignment rules.
