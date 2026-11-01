# Cell Press Figure Specifications

Comprehensive guide for preparing publication-quality figures compliant with Cell Press guidelines.

---

## 1. Column Widths and Dimensions

Cell Press figures are laid out according to fixed column widths. In `cnsplots` (and PostScript/PDF), **1 point = 1/72 inch = 0.3528 mm**.

| Layout Format | Physical Width (mm) | PostScript Points (pt) | Typical Usage |
| :--- | :--- | :--- | :--- |
| **1-column** | **85 mm** | **241 pt** | Single focus figure, 1–2 small panels |
| **1.5-column** | **114 mm** | **323 pt** | Medium multi-panel figure, 2–3 panels |
| **2-column (Full width)** | **174 mm** | **493 pt** | Full journal page width, 3–6 panels |
| **Max Page Height** | **200 mm** | **567 pt** | Leaves space for figure legend below |

> [!IMPORTANT]
> **Canvas Size vs. Saved Size**:
> When using `cnsplots`, `savefig_bbox='tight'` crops whitespace to the drawn artists. If your figure must precisely span a full column width, save with `cns.savefig(..., bbox_inches=None)`.

---

## 2. Typography & Font Rules

* **Typeface**: **Arial** is explicitly required by Cell Press.
  * In `cnsplots`:
    ```python
    cns.settings.font_sans_serif = ("Arial", "Helvetica", "Helvetica Neue", "DejaVu Sans")
    ```
  * In matplotlib: Configured via `font.sans-serif: Arial, Helvetica...` in `cns_cell.mplstyle`.
* **Font Size**:
  * Body text inside figures (axis labels, tick labels, legends): **6–8 pt**.
  * `cnsplots` defaults: `axes.labelsize = 8.0 pt`, `axes.titlesize = 8.0 pt`, `xtick.labelsize = 7.0 pt`, `legend.fontsize = 7.0 pt`.
  * **Rule**: Never manually increase font size (e.g. to 12 pt or 14 pt); 8 pt matches publication scale.
* **Panel Labels**:
  * Capital letters: **A, B, C, D** in bold.

---

## 3. Stroke Weights & Line Properties

* **Axes Spines & Tick Marks**: **0.5 pt** (Cell allows 0.5–1.5 pt; `cnsplots` default `0.5 pt` is optimal).
* **Tick Marks**: Outward-facing, 2.0 pt length, 0.6 pt stroke.
* **Top & Right Spines**: Omitted (`axes.spines.top = False`, `axes.spines.right = False`).

---

## 4. Color Palette & Accessibility

* **Cell 10-Color Qualitative Palette**:
  1. `#c84c3a` (Cell Red)
  2. `#2f7e8f` (Teal / Ocean Blue)
  3. `#e1a22e` (Ochre / Gold)
  4. `#4e5a8a` (Slate / Indigo)
  5. `#5f9862` (Sage Green)
  6. `#d07a6a` (Salmon)
  7. `#8b6fa8` (Lavender Purple)
  8. `#7b8c9e` (Steel Grey-Blue)
  9. `#b85f7a` (Berry Rose)
  10. `#6b6b6b` (Neutral Dark Grey)
* **Accessibility Constraint**:
  Cell guidelines explicitly state: *"Avoid red/green together"* (red-green colorblindness affects 5–10% of readers). The Cell palette pairs red (`#c84c3a`) with ocean teal (`#2f7e8f`) or slate (`#4e5a8a`) rather than bright green.
* **Continuous Data**: Always use `viridis` instead of rainbow scales (`jet`/`gnuplot`).

---

## 5. Resolution & Export Formats

* **Resolution Floor**: **≥ 300 DPI** for halftones/color photographic images; 500–1000 DPI for line art.
* **Vector Output**:
  * Prefer **PDF** or **SVG**.
  * Keep text live and editable (do not rasterize or convert glyphs to paths):
    * `pdf.fonttype = 42` (TrueType font embedding)
    * `svg.fonttype = 'none'` (Live text for Adobe Illustrator)
