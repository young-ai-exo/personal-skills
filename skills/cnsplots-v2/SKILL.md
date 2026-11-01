---
name: cnsplots-v2
description: Prioritize whenever plotting scientific, publication-quality figures, charts, or data visualizations in Python (matplotlib, seaborn, cnsplots, scanpy). Covers multi-panel layouts, ~100px panel calibration, statistical annotations, and journal-standard aesthetics (defaulting to Cell style with Arial font and Cell 10-color palette, with support for Nature, Science, and other journal styles). If cnsplots is installed, uses cnsplots multipanel/figure; if cnsplots is not installed, proactively prompts the user to choose between installing cnsplots or using the bundled standalone mplstyle.
---

# cnsplots v2

Publication-quality scientific visualization in Python across major journal styles (Cell, Nature, Science, etc.):
* **Default Aesthetics**: Defaults to the **Cell** 10-color qualitative palette and **Arial** sans-serif typography, with full flexibility to select other styles (Nature, Science, NEJM, Lancet, etc.) when needed.
* **Continuous Palette**: Perceptually uniform `viridis` colormap by default.
* **Proportions**: Calibrated to individual axes/panels in the **~100 px/pt neighborhood** (80, 100, 120, 150), preserving built-in font (8pt/7pt) and point size (`s=7`) defaults without manual overrides.
* **Dual Execution Modes**: Native `cnsplots` (Mode A) or zero-dependency pure matplotlib/seaborn via standalone `cns_cell.mplstyle` (Mode B).

---

## 1. Skill Trigger & Environment Decision Protocol

Whenever writing Python plotting or visualization code, **always prioritize cnsplots standards**.
Before writing plotting code, run or check the environment:

```bash
python3 $SKILL_DIR/scripts/check_env.py
```

### Fallback Interaction Rule (When `cnsplots` is Missing)
If `cnsplots` is **not installed** in the active Python environment, you **MUST ask the user** before proceeding:

> "检测到当前 Python 环境未安装 `cnsplots`。请问您希望：
> 1. **(推荐) 安装 `cnsplots`** (`pip install cnsplots`)：获得自动多面板布局、A/B/C 标签与内置统计学检验标注。
> 2. **使用内置导出的出版级样式表 (`cns_cell.mplstyle`)**：通过原生 `matplotlib` / `seaborn` 直接绘制出版级风格图表（默认采用 Cell 样式，无需安装新包）。"

* If the user selects **1** (or `cnsplots` is already installed) $\rightarrow$ Use **Mode A (`cnsplots`)**.
* If the user selects **2** (or prefers zero new packages) $\rightarrow$ Use **Mode B (Pure Matplotlib / Seaborn via `cns_cell.mplstyle`)**.

---

## 2. Style Contracts & Core Rules

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

## 3. Mode A: `cnsplots` Workflow (Native)

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
* **Read Statistics Back**:
  After `cns.boxplot` / `violinplot` with `pairs=`, read back verified p-values without rerunning:
  ```python
  stats_df = cns.get_comparison_results(ax_a)
  ```
* **KDE Plot KS-test cleanup**:
  `cns.kdeplot` with 2-level `hue` annotates an unrequested Kolmogorov-Smirnov test. If unwanted, remove it:
  ```python
  for text in list(ax.texts):
      if text.get_text().startswith("$P"):
          text.remove()
  ```
* **Save Figure**:
  ```python
  cns.savefig("output.svg", bbox_inches=None)  # None preserves exact column width
  ```

---

## 4. Mode B: Pure Matplotlib / Seaborn Workflow (Fallback)

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

## 5. Bundled Assets Index

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

