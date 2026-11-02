---
name: cnsplots-v3
version: 3.0.4
upstream: https://github.com/faridrashidi/cnsplots
description: Create, revise, and troubleshoot publication-ready scientific plots and data visualizations in Python (cnsplots, matplotlib, seaborn, scanpy), including distribution (box, violin, strip, lollipop, ridge), regression, heatmap, genomics (volcano, GSEA), survival (Kaplan-Meier, cumulative incidence), set (venn, upset), flow (sankey), classification/ROC/PR, and multi-panel figures. Prioritize whenever a user asks to plot or visualize data in Python, or requests Cell/Nature/Science-style visualization, precise physical figure dimensions (pt/mm/in), statistical plot annotations, or editable SVG/PDF publication output. Enforces a closed-loop 6-step workflow, ~100 pt panel calibration with no font or marker blow-ups, defaulting to Cell palette and Arial-first typography. Supports native cnsplots (Mode A) and pure matplotlib/seaborn via bundled cns_cell.mplstyle (Mode B) with interactive fallback.
---
# cnsplots v3

Publication-ready scientific visualization in Python across major journal styles (**Cell**, **Nature**, **Science**, etc.).
Always execute the **6-Step Closed-Loop Workflow** below when fulfilling plotting tasks.
For internal reports, keep the same proportions and legibility but treat exact journal caps (5–7 pt type, strict column widths) as optional; apply a journal preset only when a target journal is named.

---

## Hard Rules & Aesthetic Contracts

1. **Default Journal Styling**:
   * Qualitative palette in the skill's house style is the **`Cell`** 10-color palette (`apply_house_style()` sets `cns.settings.palette_qual = "Cell"`; the cnsplots package default remains `Ecotyper1`).
   * Continuous colormap defaults to **`viridis`** (`cns.settings.palette_seq = "viridis"`).
   * Typography defaults to an **`Arial`-first** stack (`cns.settings.font_sans_serif = ("Arial", "Helvetica", "Nimbus Sans", "Liberation Sans", "DejaVu Sans")`). The Nimbus/Liberation entries are metric-compatible Linux fallbacks; leave `panel_label_fontname = None` so panel labels inherit the same resolved stack.
   * Display and export dpi default to **360** (`cns.settings.figure_dpi = 360`, `cns.settings.savefig_dpi = 360`); previews also use 360.
   * *Flexibility*: Other journal palettes (`"Nature"`, `"Science"`, `"NEJM"`) or fonts can be selected if explicitly requested.
2. **The 100 pt Panel Sizing Contract**:
   * All typography (8 pt titles/labels, 7 pt ticks/legends) and the scatter marker size (`s=7`) are calibrated for **panels around 100 pt** (common values: **80, 100, 120, 150**). 100 means **100 pt**, not screen pixels; at 360 dpi, 100 pt = 500 px.
   * **In `cnsplots`**: `mp.panel()` defaults to 150 pt; explicit widths/heights should stay in the 80–150 pt range.
   * **In Matplotlib**: `figsize` is in inches ($\text{inches} = \text{points} / 72$). A 100 pt axes is ~1.4 inches.
3. **No Manual Font or Marker Blow-Ups**:
   * **NEVER** pass `fontsize=` in `set_xlabel()`, `set_ylabel()`, `set_title()`, or `tick_params()`.
   * **NEVER** enlarge markers (e.g., `s=30` or `s=50`). Keep the cnsplots defaults: `scatterplot(s=7)`, `stripplot(size=2)`, `lollipopplot(markersize=20)`.
   * In Mode B, set marker and patch geometry once in `cns_cell.mplstyle` (`lines.markersize`, `patch.linewidth`). Seaborn's filled boxplot ignores those rcParams for its edge width, so `linewidth=0.5` is allowed there as a house-style constant.
4. **Color & Meaning Consistency**:
   * One qualitative palette per figure.
   * Fix category order explicitly. When a categorical variable is mapped to color (`hue=`), pass `hue_order=` on every panel. When it is only on the x-axis, pass `order=`. **Never pass `hue_order` without `hue`**; it has no effect.
5. **Statistical Integrity**:
   * Surface statistical assumptions (test names, contrasts, paired design) explicitly. Retrieve results programmatically via `cns.get_comparison_results(ax)`.

---

## The 6-Step Closed-Loop Workflow

Follow these steps in strict sequence for every plotting request:

```mermaid
flowchart LR
    S1["1. Bootstrap<br>Environment & Style"] --> S2["2. Profile Data &<br>Select Plot Type"]
    S2 --> S3["3. Choose Layout &<br>Budget Canvas"]
    S3 --> S4["4. Build Figure with<br>~100 pt Proportions"]
    S4 --> S5["5. Extract Stats &<br>Clean Annotations"]
    S5 --> S6["6. Validate Artifact &<br>Deliver Code"]
```

### Step 1: Bootstrap Environment & Style

Check whether native `cnsplots` (Mode A) is available or if fallback to standalone `cns_cell.mplstyle` (Mode B) is needed:

```bash
python3 $SKILL_DIR/scripts/check_env.py
```

After upgrading `cnsplots`, run `python3 $SKILL_DIR/scripts/export_mplstyle.py --check` to catch Cell-palette drift in the bundled style files.

* **If `cnsplots` is installed** $\rightarrow$ Proceed in **Mode A (`cnsplots`)**.
* **If `cnsplots` is NOT installed** $\rightarrow$ Prompt the user with this exact choice before writing code:
  > "The `cnsplots` package is not installed in the active Python environment. Would you prefer to:
  > 1. **(Recommended) Install `cnsplots`** (`pip install cnsplots`): Enables automated multi-panel flow layouts, A/B/C labeling, and built-in statistical annotations.
  > 2. **Copy `cns_cell.mplstyle` into your project**: Render journal-grade figures with native `matplotlib` (seaborn optional; `check_env.py` reports which Mode B templates are usable)."

  If the user selects **2**, **copy `cns_cell.mplstyle` from the skill into the current project directory** (e.g. `./styles/cns_cell.mplstyle`) rather than directly referencing `$SKILL_DIR`:
  ```bash
  mkdir -p ./styles
  cp $SKILL_DIR/styles/cns_cell.mplstyle ./styles/cns_cell.mplstyle
  ```

---

### Step 2: Profile Data & Select Plot Type

Never invent plot structures. Inspect the actual input DataFrame columns, dtypes, missing values, and category counts first:

```python
print(df.info())
print(df.nunique())
print(df.head(3))
```

#### Data-to-Plot Decision Guide

Match the data structure to the scientific intent (consult [references/plot-catalog.md](references/plot-catalog.md) for full options):

* **Categorical Group vs Continuous Value**:
  * $\le 5$ groups $\rightarrow$ `cns.boxplot` or `cns.violinplot` + `cns.stripplot` (use `pairs=` for group comparisons).
  * Many groups ($>10$) $\rightarrow$ `cns.lollipopplot` or `cns.ridgeplot`.
* **Two Continuous Variables**:
  * Relationship $\rightarrow$ `cns.scatterplot` (keep default `s=7`).
  * Trend / Fit $\rightarrow$ `cns.regplot` or `cns.lineplot`.
* **Matrices & High-Dimensional Expression**:
  * Clustered expression $\rightarrow$ `cns.heatmapplot` (returns `ClusterMapPlotterNew`).
  * Enrichment by size + color $\rightarrow$ `cns.dotplot` (returns `DotClustermapPlotterNew`).
* **Time-to-Event / Clinical Outcome**:
  * Kaplan-Meier curve $\rightarrow$ `cns.survivalplot` (requires event & duration columns).
  * Odds / Hazard ratios with 95% CI $\rightarrow$ `cns.forestplot`.
* **Set Intersections**:
  * 2–3 sets $\rightarrow$ `cns.vennplot`.
  * $\ge 4$ sets $\rightarrow$ `cns.upsetplot`.
* **Genomics & Differential Analysis**:
  * Effect size vs significance $\rightarrow$ `cns.volcanoplot`.
  * Gene set enrichment $\rightarrow$ `cns.gseaplot`.

#### Verify Function Signature

Before calling an unfamiliar function, inspect the real installed signature to prevent API hallucination:

```bash
python3 $SKILL_DIR/scripts/inspect_api.py <function_name>
```

---

### Step 3: Determine Layout Architecture & Canvas Budget

Select the layout pattern based on panel heterogeneity and alignment requirements (see [references/composition-guide.md](references/composition-guide.md)):

| Layout Case                                 | Recommended Engine                                      | Canvas Sizing / Column Limits           |
| :------------------------------------------ | :------------------------------------------------------ | :-------------------------------------- |
| **Single Panel**                      | `cns.figure(width=..., height=..., unit="pt")`        | Submission: 241 / 493 / 519 / 522 pt canvas; report: 120–180 pt canvas; axes ~100 pt |
| **Uniform Repeated Grid**             | `fig = cns.figure()` + `fig.subplots(nrows, ncols)` | Guarantees row/column edge alignment    |
| **Heterogeneous Multi-panel (A/B/C)** | `mp = cns.multipanel(max_width=..., unit="pt")`       | Cell: 1-col = 241 pt, 2-col = 493 pt    |
| **Hybrid Grid in Multi-panel**        | Host `mp.panel()` + `fig.add_gridspec()`            | Prevents y-tick decoration misalignment |

> [!IMPORTANT]
> `cns.figure(width, height)` sizes the **full canvas**, while `mp.panel(width, height)` sizes the **axes content area**. The 80–150 pt guidance applies to axes; a full journal column is 241 / 493 / 519 / 522 pt. Do not copy a canvas width into `mp.panel()` or vice versa.

`unit` is explicit in cnsplots 0.8. These three canvas sizes are physically identical:

```python
cns.figure(144, 72, unit="pt")
cns.figure(2, 1, unit="in")
cns.figure(50.8, 25.4, unit="mm")
```

`cns.multipanel(..., unit="pt")` sets the unit for every subsequent `mp.panel()`; an individual panel can set it explicitly with `mp.panel(..., unit="pt")`.

> [!WARNING]
> In `cns.multipanel()`, outer widths vary with y-axis tick label width. Never build a visual grid by calling `mp.panel()` once per cell; use `fig.subplots()` or `GridSpec` when edges must strictly align.

---

### Step 4: Build Figure with ~100 pt Proportions

Encapsulate default house styling into a dedicated `apply_house_style()` function, then construct panels adhering to the ~100 pt sizing baseline:

* **Mode A (`cnsplots`)**:
  ```python
  import cnsplots as cns
  import matplotlib as mpl

  mpl.use("Agg")  # required for headless runs

  HOUSE_PALETTE = "Cell"
  DENSITY_CMAP = "viridis"
  FONT_SANS_SERIF = (
      "Arial",
      "Helvetica",
      "Nimbus Sans",
      "Liberation Sans",
      "DejaVu Sans",
  )


  def apply_house_style() -> None:
      """Configure cnsplots with Cell palette, viridis, Arial-first fonts, and print-safe export."""
      cns.settings.font_sans_serif = FONT_SANS_SERIF
      cns.settings.panel_label_fontname = None  # inherit the resolved font stack
      cns.settings.pdf_fonttype = 42  # TrueType embedding for Illustrator
      cns.settings.svg_fonttype = "none"  # keep SVG text editable
      cns.settings.palette_qual = HOUSE_PALETTE
      cns.settings.palette_seq = DENSITY_CMAP
      cns.settings.figure_dpi = 360  # on-screen rendering
      cns.settings.savefig_dpi = 360  # export
      cns.settings.savefig_transparent = False  # white background for print/preview

      # Both are needed: setup_matplotlib sets rcParams cycle for bare matplotlib calls,
      # palette_qual is what cns.* plot functions and multipanel read.
      cns.setup_matplotlib(color_cycle=HOUSE_PALETTE, color_map=DENSITY_CMAP)


  def main() -> None:
      apply_house_style()

      # Add panels (~100 pt axes baseline)
      mp = cns.multipanel(max_width=493, unit="pt")  # Cell 2-column limit
      ax_a = mp.panel("A", width=110, height=100)  # unit="pt" inherited from multipanel
      cns.boxplot(
          data=df,
          x="group",
          y="score",
          pairs=[("Ctrl", "Treat")],
          order=["Ctrl", "Treat"],  # x-axis order; use hue_order only with hue=
          ax=ax_a,
      )
      ax_a.set(xlabel="", ylabel="Score (a.u.)")
  ```

* **Mode B (Pure Matplotlib / Seaborn Fallback)**:
  Prerequisite: Copy `cns_cell.mplstyle` into `./styles/cns_cell.mplstyle`.
  ```python
  from pathlib import Path

  import matplotlib as mpl
  import matplotlib.pyplot as plt

  mpl.use("Agg")

  STYLE_PATH = Path("styles/cns_cell.mplstyle")
  FIGSIZE_IN = (3.5, 3.2)  # inches (matplotlib <3.11); use (3.5, 3.2, "in") on 3.11+


  def apply_house_style(style_file: Path | str = STYLE_PATH) -> None:
      """Load project house style sheet for pure matplotlib."""
      target = Path(style_file)
      if not target.is_file():
          target = Path("cns_cell.mplstyle")
      plt.style.use(str(target))


  def main() -> None:
      apply_house_style()

      # 2x2 grid (~100 pt per axes + padding); figsize uses inches here (3.11+: add "in")
      fig, axes = plt.subplots(2, 2, figsize=FIGSIZE_IN, constrained_layout=True)
      ...
  ```

  Matplotlib `figsize` units:
  * **3.10.x**: `(width_in, height_in)` only; no `unit=` argument.
  * **3.11+**: `(width, height, unit)` with `"in"`, `"cm"`, or `"px"`; use `(width, height, "in")` to make the unit explicit. A 2-tuple still means inches. `set_size_inches()` remains inches-only.
  Convert with `pt / 72`. The installed cnsplots 0.8.0 environment uses matplotlib 3.10.9, so the templates keep the 2-tuple; add `"in"` when you run on 3.11+. The `(width, height, unit)` form also belongs to `cns.figure(..., unit="pt" | "in" | "mm")`, which is a cnsplots API independent of matplotlib. The style sheet sets `figure.dpi` and `savefig.dpi` to 360.

---

### Step 5: Extract Statistical Truth & Clean Annotations

1. **Extract Programmatic Test Results**:
   After plotting with `pairs=`, retrieve verified statistical values without rerunning:
   ```python
   stats_df = cns.get_comparison_results(ax_a)
   print(
       stats_df[
           [
               "group1",
               "group2",
               "test",
               "pvalue_raw",
               "pvalue_adjusted",
               "pvalue_annotation",
               "significant",
               "annotation",
           ]
       ]
   )
   ```

2. **KDE KS-Test Cleanup**:
   `cns.kdeplot` with a 2-level `hue` annotates an unrequested Kolmogorov-Smirnov test. If unwanted, remove it:
   ```python
   for text in list(ax.texts):
       if text.get_text().startswith("$P"):
           text.remove()
   ```

---

### Step 6: Validate Artifact & Deliver Deliverables

1. **Save the Deliverable**:
   ```python
   # PDF is the universal submission format; SVG is for Illustrator editing.
   # bbox_inches=None keeps the full canvas at the configured column width.
   cns.savefig("outputs/figure.pdf", bbox_inches=None, transparent=False)
   ```
   Save an SVG only when the user needs to edit the figure in Illustrator. Do not submit PNG or JPEG as the primary artifact.

2. **Render a Preview and Inspect It Visually**:
   ```python
   # 360 dpi matches the display and final export; only bbox_inches differs.
   cns.savefig(
       "outputs/figure_preview.png",
       dpi=360,
       bbox_inches="tight",
       transparent=False,
   )
   ```
   Open the PNG and look at it. Use the model's visual inspection, not a script that checks file existence or emptiness. Check:
   * no clipped text, tick labels, or legends;
   * no overlapping labels or annotations;
   * the same category has the same color in every panel;
   * no unrequested statistical annotation (for example, the KDE KS test);
   * greyscale readability: series remain distinguishable by lightness, marker, or linestyle. The Cell palette does not guarantee this on its own; its first two colors have nearly identical CIE L*.

3. **Report**: Deliver the full runnable script, output paths, and all statistical assumptions (tests, comparison direction, group orders).

---

## Bundled Assets Index

### Styles & Colors

* [`styles/cns_cell.mplstyle`](styles/cns_cell.mplstyle): Standalone Matplotlib style sheet generated from the cnsplots Cell palette (Arial-first fallbacks, Cell cycler, 0.5 pt spines and patch edges, 8/7 pt hierarchy, s=7 pt² markers, 360 dpi display/export, white background).
* [`styles/cell_colors.py`](styles/cell_colors.py): Generated module with `CELL_HEX`, `CELL_RGB`, named constants (`CELL_RED`, `CELL_TEAL`, etc.), and `get_cell_colors()`; use it when you need the Cell palette without cnsplots.

### Scripts

* [`scripts/check_env.py`](scripts/check_env.py): Zero-dependency probe for Python, cnsplots, matplotlib, seaborn, mutool, and Mode A vs Mode B readiness.
* [`scripts/export_mplstyle.py`](scripts/export_mplstyle.py): Regenerates `cns_cell.mplstyle` and `cell_colors.py` from `cns.palettes("Cell")`; `--check` is the drift test.
* [`scripts/inspect_api.py`](scripts/inspect_api.py): Introspects installed `cnsplots` public functions to prevent API hallucinations.

### Templates

* [`templates/cns_multipanel_cell.py`](templates/cns_multipanel_cell.py): Mode A multi-panel publication template.
* [`templates/cns_single_figure.py`](templates/cns_single_figure.py): Mode A single-panel boxplot with comparisons.
* [`templates/pure_mpl_grid.py`](templates/pure_mpl_grid.py): Mode B pure matplotlib 2x2 grid.
* [`templates/pure_seaborn_cell.py`](templates/pure_seaborn_cell.py): Mode B pure seaborn boxplot + stripplot overlay.

### Reference Showcases

* [`templates/upstream-showcase/README.md`](templates/upstream-showcase/README.md): vendored cnsplots Figure 1 and Figure 2 sources, with run notes. These keep the upstream 144 display dpi because their pixel offsets are tuned for it; export is 360.
* [`templates/upstream-showcase/figure1.py`](templates/upstream-showcase/figure1.py): 18-panel upstream showcase.
* [`templates/upstream-showcase/figure2.py`](templates/upstream-showcase/figure2.py): 13-panel upstream showcase with images and detached axes.

### Reference Guides

* [`references/plot-catalog.md`](references/plot-catalog.md): Complete catalog of 30+ plot functions, returns, and statistical accessors.
* [`references/journal-specs.md`](references/journal-specs.md): Specifications for Cell Press (default), Nature, and Science (column widths, font caps, line weights, resolution).
* [`references/panel-sizing-100pt.md`](references/panel-sizing-100pt.md): The 100 pt golden baseline, point-to-inch conversions, and typography proportions.
* [`references/composition-guide.md`](references/composition-guide.md): Layout patterns, `multipanel` dynamic left-reserve physics, and alignment rules.
