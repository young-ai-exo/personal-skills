# Composition & Multi-panel Layout Guide

Selecting the appropriate layout architecture avoids costly refactors and ensures clean alignment.

---

## 1. The Three Composition Patterns

| Pattern | Engine | When to Use | Edge Alignment |
| :--- | :--- | :--- | :--- |
| **Pattern A: Uniform Grid** | `cns.figure()` + `fig.subplots()` (or pure `plt.subplots`) | Same plot type repeated over categories / genes / conditions | **Guaranteed exact** |
| **Pattern B: Heterogeneous Layout** | `cns.multipanel()` + `mp.panel()` | Mixed plot types (e.g. Boxplot + Scatter + Bar), labeled A/B/C/D | Flow layout, wrapped at `max_width` |
| **Pattern C: Hybrid Grid inside Panel** | `mp.panel()` as host + `fig.add_gridspec()` | Large multi-panel figure where one sub-block is a repeated grid | **Guaranteed inside host** |

---

## 2. Critical Rule: Why Multipanel Does Not Align Axes Edges

In `cns.multipanel()`, each panel's outer footprint is calculated at render time:
$$\text{Total Width} = \text{margin\_left} + \text{left\_reserve} + \text{width} + \text{margin\_right}$$

`left_reserve` is **measured from the rendered y-axis decoration width** (tick labels + ylabel).
* Panel A with y-values `0 to 1` has a narrow left reserve (~25 pt).
* Panel B with y-values `0 to 100,000` has a wider left reserve (~45 pt).
* **Consequence**: If both have `width=100`, their left axes edges will NOT line up vertically.

> [!WARNING]
> Never build a visual grid by calling `mp.panel()` once per cell.
> When columns must strictly line up, use **Pattern A** (`fig.subplots()`) or **Pattern C** (`GridSpec` inside host panel).

---

## 3. Row Wrapping & Newline

In `cns.multipanel(max_width=493, unit="pt")`:
* Panels flow left to right and wrap to the next row when the cumulative width exceeds `max_width`.
* **Budgeting**: Budget not just axes `width`, but also labels and margins (~30–50 pt extra per panel). Two 100 pt panels typically need ~280 pt total width.
* **Force New Row**: Call `mp.newline()` to immediately break to the next row.
* **Vertical Stacking**: Pass `below="A"` to attach a panel directly under panel A without consuming a normal column slot.

