# Journal Figure Specifications

Comprehensive guide for preparing publication-quality figures across top scientific journals (**Cell Press**, **Nature**, **Science**). **Cell Press standards serve as the workspace default preset.**

> [!NOTE]
> **Submission targets vs. internal reports.** These values are guardrails for journal submission, where production editors check them. For internal reports and presentations, prioritize legible type, sensible proportions, and consistent layout; exact 5–7 pt caps and column widths are not required. Apply a Nature/Science preset only when a target journal is named.

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
> The default `savefig_bbox='tight'` crops whitespace to visible artists. When you need the saved output width to strictly equal the column width, pass `bbox_inches=None` to `savefig()`. Measured on cnsplots 0.8.0: a 519-pt (183 mm) canvas holding one 240×150 pt panel saves about **93 mm** wide with the default tight crop, and **183.1 mm** with `bbox_inches=None`. `pad_inches` applies only to the tight path.

---

## 2. Typography & Typeface Rules

| Property | Cell Press (Default) | Nature | Science |
| :--- | :--- | :--- | :--- |
| **Typeface** | **Arial** (Required) | Helvetica or Arial | Helvetica preferred |
| **In-figure Text Size** | **6–8 pt** | 5–7 pt | 5–7 pt (7 pt target) |
| **Panel Labels** | **Capital A, B, C** (Bold) | **8 pt bold lowercase a, b, c** | **10 pt bold capital A, B, C** |
| **Installed Default** | `title_fontsize=8`, `legend_fontsize=7` | *Note: Nature caps text at 7 pt; use `settings.context(title_fontsize=7, legend_fontsize=6)`* | *Note: 7 pt target; use `settings.context(title_fontsize=7, legend_fontsize=5)`* |

* **Arial-first Configuration (Workspace Default)**:
  ```python
  cns.settings.font_sans_serif = (
      "Arial",
      "Helvetica",
      "Nimbus Sans",
      "Liberation Sans",
      "DejaVu Sans",
  )
  cns.settings.panel_label_fontname = None  # inherit the resolved stack
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
  Color-distinct, but **not greyscale-safe on its own**: the first two colors have CIE L* 49.2 and 48.9 (ΔL* = 0.3), and 11 of the 45 color pairs are within 5 L*. When a figure will be printed in black and white, add marker or linestyle differences rather than relying on the palette alone.
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
* **cnsplots default**: `savefig_dpi = 288`, below the 300 DPI floor. The skill's `apply_house_style()` sets **360** for both display (`figure_dpi`) and export (`savefig_dpi`), and previews also use 360. Raise the export to 500–1000 for raster line art (Cell asks ≥1000).
* **Vector Formats**: **PDF** is the universal submission format; **SVG** is for Illustrator editing; **PNG** is for preview only. Live text must remain editable:
  * `pdf.fonttype = 42` (TrueType font embedding)
  * `svg.fonttype = 'none'` (Live text for Illustrator, avoiding path conversion)
* **Saving at an exact column width**: `cns.savefig(path, bbox_inches=None)` keeps the full canvas; the default `savefig_bbox='tight'` crops to the artists and can save much narrower than the configured column.

