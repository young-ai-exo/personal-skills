# Journal Figure Specifications

Comprehensive guide for preparing publication-quality figures across top scientific journals (**Cell Press**, **Nature**, **Science**). **Cell Press standards serve as the workspace default preset.**

---

## 1. Column Widths and Canvas Dimensions

In `cnsplots` (and standard PDF/PostScript), **1 point = 1/72 inch = 0.3528 mm**.
Formula: $\text{points} = \frac{\text{mm}}{25.4} \times 72$

| Specification | Cell Press (Default) | Nature | Science |
| :--- | :--- | :--- | :--- |
| **1-column** | **85 mm / 241 pt** | 89 mm / 252 pt | 57 mm / 162 pt |
| **1.5-column** | **114 mm / 323 pt** | 120–136 mm / 340–386 pt | — |
| **2-column (Full)** | **174 mm / 493 pt** | 183 mm / 519 pt | 121 mm / 343 pt (2-col) / 184 mm / 522 pt (full) |
| **Max Height** | **200 mm / 567 pt** | 170 mm / 482 pt | Unstated (leave room for legend) |

> [!IMPORTANT]
> **Canvas Width vs Saved Width**:
> The default `savefig_bbox='tight'` crops whitespace to visible artists. When you need the saved output width to strictly equal the column width, pass `bbox_inches=None` to `savefig()`.

---

## 2. Typography & Typeface Rules

| Property | Cell Press (Default) | Nature | Science |
| :--- | :--- | :--- | :--- |
| **Typeface** | **Arial** (Required) | Helvetica or Arial | Helvetica preferred |
| **In-figure Text Size** | **6–8 pt** | 5–7 pt | 5–7 pt (7 pt target) |
| **Panel Labels** | **Capital A, B, C** (Bold) | **8 pt bold lowercase a, b, c** | **10 pt bold capital A, B, C** |
| **Installed Default** | `title_fontsize=8`, `legend_fontsize=7` | *Note: Nature caps text at 7 pt* | Fits requirements |

* **Arial-first Configuration (Workspace Default)**:
  ```python
  cns.settings.font_sans_serif = ("Arial", "Helvetica", "Helvetica Neue", "DejaVu Sans")
  ```

---

## 3. Stroke Weights & Line Properties

| Property | Cell Press (Default) | Nature | Science |
| :--- | :--- | :--- | :--- |
| **Spine & Line Width** | **0.5–1.5 pt** | 0.25–1.0 pt | ≥ 0.5 pt |
| **cnsplots Default** | `axes_linewidth = 0.5` | Exact match | Exact match |

* Top and right spines are removed across all CNS styles (`axes.spines.top = False`, `axes.spines.right = False`).

---

## 4. Built-in Journal Qualitative Palettes

`cnsplots` ships native palettes matching each major journal:

* **`"Cell"` (Workspace Default)**:
  `['#c84c3a', '#2f7e8f', '#e1a22e', '#4e5a8a', '#5f9862', '#d07a6a', '#8b6fa8', '#7b8c9e', '#b85f7a', '#6b6b6b']`
  Designed to prevent red-green clashes while maintaining distinct lightness separation.
* **`"Nature"`**:
  `[(0.90, 0.29, 0.21), (0.30, 0.73, 0.84), (0.0, 0.63, 0.53), ...]` (Nature Reviews Cancer-inspired).
* **`"Science"`**:
  `[(0.23, 0.29, 0.57), (0.93, 0.0, 0.0), (0.0, 0.55, 0.27), ...]` (Science journal-inspired).

To switch palettes in Mode A:
```python
cns.settings.palette_qual = "Nature"  # or "Science", "NEJM", "Tableau", etc.
```

---

## 5. Resolution & Vector Export

* **Raster Resolution**: **≥ 300 DPI** across all three publishers; 500–1000 DPI for line art.
* **Vector Formats**: **PDF** or **SVG** preferred. Live text must remain editable:
  * `pdf.fonttype = 42` (TrueType font embedding)
  * `svg.fonttype = 'none'` (Live text for Illustrator, avoiding path conversion)

