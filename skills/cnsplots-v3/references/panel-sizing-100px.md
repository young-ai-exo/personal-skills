# The 100 px/pt Panel Sizing Principle & Proportion Contract

The styling contract in `cnsplots` (and Cell Press guidelines) is based on **compact, high-density panels**. All default font sizes, line widths, and marker sizes are proportioned to fit an axes whose width and height sit in the **~100 px/pt neighborhood**.

---

## 1. Why 100 px/pt is the Golden Baseline

In publication figures, figures are printed at actual physical sizes (e.g. 85 mm column width). A single column comfortably accommodates 1 to 2 panels.

When an axes content area is sized to **80–150 pt (1.1–2.1 inches)**:
* **8 pt Title / Axis Labels** occupy ~7–10% of the panel dimension — clear, legible, and unobtrusive.
* **7 pt Tick Labels & Legend Items** fit neatly without overlapping adjacent panels.
* **Marker Size `s=7`** (or ~2.5–3 pt radius) provides sharp visual density for 50–500 sample points without crowding.
* **0.5 pt Spines** provide clean framing without visual heaviness.

> [!CAUTION]
> **The Matplotlib 10x Trap**:
> Matplotlib defaults to 8x6 inch canvases (576x432 pt) with 10–12 pt fonts. When an agent creates a 600 pt axes or sets `fontsize=14` and `s=50`, the plot looks monstrous and is immediately rejected by journal production editors.
> **Rule**: Never override `fontsize=` or blow up `s=`. Sizing the axes to ~100 pt makes package defaults look perfect.

---

## 2. Standard Recommended Dimensions

| Target Size | Width x Height (pt) | Best Suited For |
| :--- | :--- | :--- |
| **80 pt** | `80 x 80` ~ `90 x 90` | Dense micro-grids, single-column distribution strips, mini sparklines |
| **100 pt (Standard)** | `100 x 100` ~ `110 x 110` | Standard boxplots, categorical comparisons, scatterplots, ROC curves |
| **120 pt (Wide)** | `120 x 100` ~ `130 x 100` | Categories with longer horizontal labels, correlation regressions |
| **150 pt (Default)** | `150 x 150` ~ `180 x 140` | Clustered heatmaps, Kaplan-Meier survival curves, volcano plots |

---

## 3. Applying in Mode A (`cnsplots`)

In `cnsplots`, dimensions in `mp.panel()` describe the **axes content area in points**:

```python
# 1. Zero-configuration (Uses cns.settings.panel_width/height = 150 pt)
ax_a = mp.panel("A")

# 2. Explicit standard sizing (Recommended)
ax_b = mp.panel("B", width=100, height=100)
ax_c = mp.panel("C", width=120, height=100)
ax_d = mp.panel("D", width=80, height=80)
```

**Font & Marker Discipline**:
* Do **NOT** pass `fontsize=` in `ax.set_xlabel()`, `ax.set_title()`, or `ax.tick_params()`.
* Do **NOT** pass large `s=` in `cns.scatterplot()`; default `s=7` is already optimal.

---

## 4. Applying in Mode B (Pure Matplotlib / Seaborn)

Matplotlib expects `figsize=(width_in_inches, height_in_inches)`.
Conversion formula:
$$\text{inches} = \frac{\text{points}}{72}$$

To yield an axes area of ~100 pt with standard margins:
* **Single Panel Figure**:
  ```python
  fig, ax = plt.subplots(figsize=(2.2, 2.0))  # ~110 pt axes + labels
  ```
* **2 x 1 Panels (Vertical or Horizontal)**:
  ```python
  # Horizontal pair (fits Cell 2-column ~493 pt width)
  fig, axes = plt.subplots(1, 2, figsize=(4.0, 2.0), constrained_layout=True)
  ```
* **2 x 2 Panels Grid**:
  ```python
  # 2x2 grid (each axes ~100 pt)
  fig, axes = plt.subplots(2, 2, figsize=(3.5, 3.2), constrained_layout=True)
  ```
With `plt.style.use("cns_cell.mplstyle")`, the 8 pt labels, 7 pt ticks, and Cell color cycle apply automatically without manual configuration.

