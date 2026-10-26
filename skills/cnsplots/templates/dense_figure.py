#!/usr/bin/env python3
"""Template: dense publication figure, showcase style.

Demonstrates the techniques a full journal figure needs beyond a simple
multipanel: per-panel palettes, negative pad/margin to reclaim reserved space,
an embedded raster image, a composite plotter styled through its internal axes,
an upsetplot rescaled into a host panel, and reworked built-in annotations.

Runs as-is on the packaged showcase data. See references/dense-figures.md for
the reasoning behind each step.

    python3 dense_figure.py
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # headless; must precede pyplot import

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import cnsplots as cns

# --- CONFIGURE ---------------------------------------------------------------
MAX_WIDTH = 510
FIGURE_TITLE = "Figure 1"
OUTPUT = "dense_figure.svg"
# -----------------------------------------------------------------------------


def report_bands(mp, labels="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    """Group panels into visual rows so an unintended wrap is visible.

    Panels of differing heights share a row without sharing y0 or y1, so
    neither edge alone identifies a row. Two panels are in the same band when
    their vertical extents overlap by more than a quarter of the shorter one.
    Verified to reproduce multipanel's internal row grouping.
    """
    placed = []
    for label in labels:
        ax = mp.get_axes(label)
        if ax is None:
            continue
        box = ax.get_position()
        placed.append((label, box.y0, box.y1))
    placed.sort(key=lambda item: -item[2])

    bands = []
    for entry in placed:
        _, y0, y1 = entry
        for band in bands:
            if any(
                min(y1, other_y1) - max(y0, other_y0)
                > 0.25 * min(y1 - y0, other_y1 - other_y0)
                for _, other_y0, other_y1 in band
            ):
                band.append(entry)
                break
        else:
            bands.append([entry])
    return [[label for label, _, _ in band] for band in bands]


def embed_detached_axes(host_ax, detached_axes, *, xpad=0.03, ypad=0.03):
    """Rescale a detached plotter's axes into a host panel's rectangle.

    For plotters that lay out several axes on the figure and do not stay inside
    a single panel (upsetplot). Call this only after every mp.panel() call, and
    after a draw, or the host rectangle is still provisional.
    """
    detached_axes = [ax for ax in detached_axes if ax is not None]
    if not detached_axes:
        return

    host_ax.set_axis_off()
    host_box = host_ax.get_position().frozen()
    boxes = [ax.get_position().frozen() for ax in detached_axes]

    left = min(box.x0 for box in boxes)
    right = max(box.x1 for box in boxes)
    bottom = min(box.y0 for box in boxes)
    top = max(box.y1 for box in boxes)
    span_w = max(right - left, 1e-9)
    span_h = max(top - bottom, 1e-9)

    inner_x = host_box.x0 + host_box.width * xpad
    inner_y = host_box.y0 + host_box.height * ypad
    inner_w = host_box.width * (1 - 2 * xpad)
    inner_h = host_box.height * (1 - 2 * ypad)

    for ax, box in zip(detached_axes, boxes):
        ax.set_position(
            [
                inner_x + inner_w * ((box.x0 - left) / span_w),
                inner_y + inner_h * ((box.y0 - bottom) / span_h),
                inner_w * (box.width / span_w),
                inner_h * (box.height / span_h),
            ]
        )


def main() -> None:
    (
        iris_df,
        tips_df,
        survival_df,
        _blobs,
        _volcano_df,
        gene_sets,
        roc_df,
        _slope_df,
        _confusion_df,
        _line_df,
        _cumulative_df,
        _forest_df,
        upset_sets,
        showcase_images,
    ) = cns.datasets.get_showcase_data(include_showcase_images=True)

    # Panel titles normal, figure title bold: keeps the hierarchy legible at 8pt.
    cns.settings.title_fontweight = "normal"
    mp = cns.multipanel(
        max_width=MAX_WIDTH,
        title=FIGURE_TITLE,
        title_fontweight="bold",
        loc="left",
    )

    # --- Band 1: four tall narrow panels, then a stacked pair ----------------
    # Tall panels set the band height. A short panel beside them would leave
    # dead space above or below, so short panels go in `below=` stacks that
    # together fill the same vertical extent. This interlocking is what makes a
    # showcase figure dense; a flat row of mixed heights does not.

    # A: monochrome panel via a single-color cycle; anchored rotated ticks.
    ax = mp.panel("A", 45, 100, margin_right=6, color_cycle=[cns.VIOLET])
    cns.boxplot(data=tips_df, x="day", y="total_bill", pairs=[("Thur", "Sun")])
    ax.set_title("Boxplot")
    ax.set_xlabel("")
    ax.set_xticklabels(
        ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
    )

    # B: same height, so it shares the band cleanly.
    ax = mp.panel("B", 45, 100, margin_right=6, color_cycle=[cns.CHOCOLATE])
    cns.violinplot(data=iris_df, x="species", y="sepal_width")
    ax.set_title("Violin")
    ax.set_xlabel("")
    ax.set_xticklabels(
        ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor"
    )

    # C: two related colors pulled out of one palette by index.
    ax = mp.panel(
        "C",
        50,
        100,
        margin_right=6,
        color_cycle=cns.get_hexcolors_from_apalette([2, 4], "Bold"),
    )
    cns.stackplot(data=tips_df, x="day", stack="sex")
    ax.set_title("Stackplot")
    ax.get_legend().set_title(None)

    # D: image panel. No ticks or y-label, so reclaim the whole reserve with a
    # large negative pad_left. Title before set_axis_off; the title survives.
    ax = mp.panel("D", 120, 100, pad_left=-42, margin_right=6)
    ax.imshow(mpimg.imread(showcase_images / "image2.webp"))
    ax.set_title("Immunofluorescence")
    ax.set_axis_off()

    # E + F: a 45 + 45 stack occupying one column of the same band. Two short
    # panels fill the height of the 100-point panels beside them.
    ax = mp.panel("E", 80, 42, margin_right=0, color_cycle=[cns.VIOLET])
    cns.barplot(data=tips_df, y="day", x="total_bill", errorbar="se", width=0.7)
    ax.set_title("Barplot")
    ax.set_ylabel("")

    ax = mp.panel(
        "F", 44, 38, below="E", margin_right=0,
        color_cycle="Ecotyper3",
    )
    cns.pieplot(iris_df, "species", legend="right")
    ax.set_title("Pie")
    ax.get_legend().set_title(None)

    # --- Band 2: square panels, plus a venn/donut stack ----------------------
    # G: wrap the long ROC legend labels onto two lines.
    ax = mp.panel("G", 90, 90, margin_right=6, color_cycle="ECharts")
    ax = cns.rocplot(roc_df, "label", ["Model A", "Model B"])
    ax.legend(loc="lower right", bbox_to_anchor=(1.08, 0.0))
    for text in ax.get_legend().get_texts():
        text.set_text(text.get_text().replace(" (AUC=", "\n(AUC="))
        text.set_multialignment("left")
    ax.set_title("ROC")

    # H: survival curve, then shorten the generated HR annotation.
    ax = mp.panel("H", 90, 90, margin_right=6)
    ax = cns.survivalplot(
        data=survival_df,
        duration="time",
        event="event",
        hue="group",
        show_hazard_ratio=False,
    )
    for text in ax.texts:
        if text.get_text().startswith("HR ="):
            head, sep, tail = text.get_text().partition("\n")
            text.set_text(f"{head.split(' (', 1)[0]}{sep}{tail}" if sep else head)
            break
    ax.legend(loc="upper right", bbox_to_anchor=(1.03, 1.0), borderaxespad=0)
    ax.set_title("Survival")

    ax = mp.panel("I", 90, 90, margin_right=6, color_cycle="Ecotyper3")
    cns.kdeplot(data=iris_df, x="petal_length", hue="species")
    ax.get_legend().set_title(None)
    ax.set_title("KDE")

    # J + K: two 40-point round plots stacked to match the 88-point squares. vennplot
    # returns a venn object, so its title goes through mp.get_axes().
    mp.panel("J", 38, 38, pad_left=32, margin_right=0, color_cycle="Tableau")
    cns.vennplot(gene_sets, labels=("A", "B", "C"))
    mp.get_axes("J").set_title("Venn")

    ax = mp.panel(
        "K", 44, 44, below="J", margin_right=0,
        color_cycle="Ecotyper3",
    )
    cns.donutplot(iris_df, "species", legend="right")
    ax.set_title("Donut")
    ax.get_legend().set_title(None)

    # --- Band 3: composite plotters and reserved space ----------------------
    # L: dotplot styled through its internal axes. hm_ax and ax_heatmap are
    # different objects; the built-in title is blanked and replaced.
    host_g = mp.panel("L", 70, 90, pad_top=15, pad_left=35, margin_right=15)
    counts = tips_df.groupby(["day", "sex"], observed=True).agg(
        {"total_bill": ["min", "size"]}
    )
    counts.columns = ["min", "size"]
    counts = counts.reset_index()
    dp = cns.dotplot(
        counts,
        x="sex",
        y="day",
        color="size",
        size="min",
        value="size",
        legend=True,
        legend_width=10,
        legend_hpad=0,
        legend_vgap=0,
        xlabel="",
        ylabel="",
        xticklabels_rotation=25,
        xticklabels_fontsize=6,
        yticklabels_fontsize=6,
        max_s=40,
        ax=host_g,
    )
    for label in dp.hm_ax.get_xticklabels():
        label.set_ha("right")
        label.set_rotation_mode("anchor")
    dp.ax_heatmap.set_title("")
    dp.hm_ax.set_title("Dotplot")
    dp.dot_legend.get_title().set_fontsize(6)
    for text in dp.dot_legend.get_texts():
        text.set_fontsize(6)
    dp.cbar_ax.tick_params(labelsize=6, length=0)
    dp.cbar_ax.set_title("size", fontsize=6, pad=1, loc="right")
    dp.cbar_ax.set_ylabel("")

    # M: host for the upsetplot. Sized to sit beside the dotplot in the same
    # band. Declared before the placeholder so no panel follows the embed.
    host_h = mp.panel("M", 190, 90, pad_left=-70, pad_top=10, margin_right=8)

    # N: placeholder for content that does not exist yet.
    ax = mp.panel("N", 124, 90, margin_right=0)
    cns.placeholderplot("Reserved slot (124x90)\nFill this in later.")
    ax.set_title("Placeholder")

    # Every panel now exists. `ax=` does confine the group on 0.8.0, but it lays
    # out inside the host immediately and looks cramped when the host is small.
    # Laying out on the figure and rescaling onto the host gives control of the
    # padding, so that is the pattern used here.
    upset_axes = cns.upsetplot(
        upset_sets,
        fig=mp.fig,
        sort_by="cardinality",
        totals_plot_elements=0,
        facecolor="black",
        show_counts=False,
    )
    upset_axes["intersections"].set_title("UpSet")

    mp.fig.canvas.draw()  # settle before reading host geometry
    embed_detached_axes(host_h, list(upset_axes.values()), xpad=0.03, ypad=0.04)
    mp.fig.canvas.draw()

    cns.savefig(OUTPUT)

    print(f"wrote {OUTPUT}: {len(mp.axes)} panels in bands {report_bands(mp)}")


if __name__ == "__main__":
    main()
