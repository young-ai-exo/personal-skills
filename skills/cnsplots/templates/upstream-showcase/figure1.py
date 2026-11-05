"""Upstream cnsplots showcase, Figure 1. Vendored as reference.

Source: https://cnsplots.farid.one/latest/examples/showcase.html
Copyright Farid Rashidi, BSD-3-Clause. Not our work.
Adapted for the cnsplots house style: unit="pt", 360 display/export dpi,
Cell palette, Arial-first fonts, opaque background. Pixel-based pad_left and
pad_top values are rescaled by 360/144 = 2.5 to keep the upstream geometry.
See README.md in this directory.

All mp.panel(width, height, ...) values below are in points.
"""

import os
from pathlib import Path

import cnsplots as cns
import matplotlib.image as mpimg

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
    """Configure cnsplots with the skill's Cell palette, Arial fonts, and 360 dpi."""
    cns.settings.font_sans_serif = FONT_SANS_SERIF
    cns.settings.panel_label_fontname = None
    cns.settings.pdf_fonttype = 42
    cns.settings.svg_fonttype = "none"
    cns.settings.palette_qual = HOUSE_PALETTE
    cns.settings.palette_seq = DENSITY_CMAP
    cns.settings.figure_dpi = 360
    cns.settings.savefig_dpi = 360
    cns.settings.savefig_transparent = False
    cns.setup_matplotlib(color_cycle=HOUSE_PALETTE, color_map=DENSITY_CMAP)


(
    iris_df,
    tips_df,
    survival_df,
    blobs,
    volcano_df,
    gene_sets,
    roc_df,
    slope_df,
    confusion_df,
    line_df,
    cumulative_incidence_df,
    forest_df,
    upset_sets,
    showcase_images,
) = cns.datasets.get_showcase_data(
    include_showcase_images=True,
)


def _read_showcase_image(filename):
    with (showcase_images / filename).open("rb") as image_file:
        return mpimg.imread(image_file)


def _embed_detached_axes(host_ax, detached_axes, *, xpad=0.0, ypad=0.0):
    detached_axes = [ax for ax in detached_axes if ax is not None]
    if not detached_axes:
        return

    host_ax.set_axis_off()
    host_box = host_ax.get_position().frozen()
    detached_boxes = [ax.get_position().frozen() for ax in detached_axes]
    left = min(box.x0 for box in detached_boxes)
    right = max(box.x1 for box in detached_boxes)
    bottom = min(box.y0 for box in detached_boxes)
    top = max(box.y1 for box in detached_boxes)
    width = max(right - left, 1e-9)
    height = max(top - bottom, 1e-9)

    inner_x0 = host_box.x0 + host_box.width * xpad
    inner_y0 = host_box.y0 + host_box.height * ypad
    inner_width = host_box.width * (1 - 2 * xpad)
    inner_height = host_box.height * (1 - 2 * ypad)

    for ax, box in zip(detached_axes, detached_boxes):
        ax.set_position(
            [
                inner_x0 + inner_width * ((box.x0 - left) / width),
                inner_y0 + inner_height * ((box.y0 - bottom) / height),
                inner_width * (box.width / width),
                inner_height * (box.height / height),
            ]
        )

    cns.utils._capture_detached_axes_layout(host_ax, detached_axes=detached_axes)


apply_house_style()
cns.settings.title_fontweight = "normal"
mp = cns.multipanel(
    max_width=485, title="Figure 1", title_fontweight="bold", loc="left", unit="pt"
)

# Panel A: boxplot
mp.panel("A", 45, 100, color_cycle=[cns.VIOLET])
ax = cns.boxplot(
    data=tips_df, x="day", y="total_bill", pairs=[("Thur", "Sun"), ("Thur", "Fri")]
)
ax.set_title("Barplot")
ax.set_xlabel("")
ax.set_xticklabels(
    ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
)

# Panel B: violinplot
mp.panel("B", 45, 100, color_cycle=[cns.CHOCOLATE])
ax = cns.violinplot(data=iris_df, x="species", y="sepal_width", pairs="all")
ax.set_title("Violinplot")
ax.set_xlabel("")
ax.set_xticklabels(
    ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor"
)

# Panel C: stripplot
mp.panel("C", 60, 100, color_cycle="BlueRed")
ax = cns.stripplot(data=tips_df, x="day", y="tip", hue="sex")
legend = ax.get_legend()
ax.legend(
    handles=legend.legend_handles,
    labels=[text.get_text() for text in legend.get_texts()],
    title=legend.get_title().get_text(),
    loc="upper left",
    bbox_to_anchor=(-0.02, 1.0),
    borderaxespad=0,
    markerscale=1,
)
ax.set_title("Stripplot")

# Panel D: stackplot
mp.panel("D", 50, 100, color_cycle=cns.get_hexcolors_from_apalette([2, 4], "Bold"))
ax = cns.stackplot(data=tips_df, x="day", stack="sex", pairs=[("Thur", "Sun")])
ax.set_title("Stackplot")
ax.get_legend().set_title(None)

# Panel E: barplot
mp.panel("E", 80, 40, margin_left=35, margin_right=0, color_cycle=[cns.VIOLET])
ax = cns.barplot(
    data=tips_df,
    y="day",
    x="total_bill",
    errorbar="se",
    width=0.7,
    pairs=[("Thur", "Sun"), ("Thur", "Fri")],
)
ax.set_title("Barplot")
ax.set_ylabel("")

# Panel F: pieplot (stacked below E)
mp.panel(
    "F",
    40,
    40,
    margin_left=35,
    margin_top=10,
    margin_right=0,
    below="E",
    color_cycle="Ecotyper3",
)
ax = cns.pieplot(iris_df, "species", legend="right")
ax.set_title("Pieplot")
ax.get_legend().set_title(None)

# Panel G: vennplot
mp.panel("G", 40, 40, pad_left=137.5, margin_right=45, color_cycle="Tableau")
cns.vennplot(gene_sets, labels=("Set A", "Set B", "Set C"))
mp.get_axes("G").set_title("Vennplot")

# Panel H: donutplot
mp.panel("H", 50, 50, below="G", color_cycle="Ecotyper3")
ax = cns.donutplot(iris_df, "species", legend="right")
ax.set_title("Donutplot")
ax.get_legend().set_title(None)

# Panel I: regplot
mp.panel("I", 90, 90)
ax = cns.regplot(data=tips_df, x="total_bill", y="tip", s=1)
ax.set_title("Regplot")

# Panel J: survivalplot
mp.panel("J", 90, 90)
ax = cns.survivalplot(
    data=survival_df,
    duration="time",
    event="event",
    hue="group",
    show_hazard_ratio=False,
)
# Keep the showcase annotation compact by dropping the CI from the HR line.
for text in ax.texts:
    label = text.get_text()
    if label.startswith("HR ="):
        hr_line, sep, remainder = label.partition("\n")
        text.set_text(
            f"{hr_line.split(' (', 1)[0]}{sep}{remainder}" if sep else hr_line
        )
        break
ax.legend(loc="upper right", bbox_to_anchor=(1.03, 1.0), borderaxespad=0)
ax.set_title("Survivalplot")

# Panel K: kdeplot
mp.panel("K", 90, 90, color_cycle="Ecotyper3", margin_right=0)
ax = cns.kdeplot(data=iris_df, x="petal_length", hue="species")
ax.get_legend().set_title(None)
ax.set_title("Kdeplot")

# Panel L: volcanoplot
mp.panel("L", 90, 90, margin_right=60)
ax = cns.volcanoplot(volcano_df)
ax.set_title("Volcanoplot")

# Panel M: rocplot
mp.panel("M", 90, 90, margin_right=5, color_cycle="ECharts")
ax = cns.rocplot(roc_df, "label", ["Model A", "Model B"])
ax.legend(loc="lower right", bbox_to_anchor=(1.1, 0.0))
for text in ax.get_legend().get_texts():
    text.set_text(text.get_text().replace(" (AUC=", "\n(AUC="))
    text.set_multialignment("left")
ax.set_title("Rocplot")

# Panel N: sankeyplot
mp.panel("N", 30, 100, pad_left=-75, color_cycle="Ecotyper4")
ax = cns.sankeyplot(tips_df, x=["day", "sex"], label_rotation=90)
ax.set_title("Sankeyplot")

# Panel O: ridgeplot
mp.panel("O", 80, 35, pad_left=275, margin_right=0)
ax = cns.ridgeplot(data=iris_df, x="petal_length", y="species")
ax.set_title("Ridgeplot")

# Panel P: slopeplot
mp.panel("P", 80, 65, below="O", margin_top=10, pad_top=-12.5, margin_right=0)
ax = cns.slopeplot(data=slope_df, x="site", y="value", hue="label", pair="pair")
ax.set_title("Slopeplot")

# Panel Q: scatterplot
mp.panel(
    "Q",
    90,
    90,
    margin_right=50,
    margin_top=-10,
    margin_bottom=20,
    color_cycle="Set1",
)
ax = cns.scatterplot(
    data=iris_df, x="sepal_length", y="sepal_width", hue="species", s=5
)
ax.set_title("Scatterplot")
ax.get_legend().set_title(None)
ax.axhline(
    y=iris_df["sepal_width"].mean(),
    color="gray",
    linestyle="--",
    dashes=(4, 3),
    linewidth=0.7,
)
ax.axvline(
    x=iris_df["sepal_length"].mean(),
    color="gray",
    linestyle="--",
    dashes=(4, 3),
    linewidth=0.7,
)
cns.take_legend_out()

# Panel R: heatmapplot (taller panel so the three legends have room)
mp.panel("R", 190, 110, margin_top=-10, margin_right=0)
cmp = cns.heatmapplot(
    blobs,
    label="Z-score",
    cmap="BuRd_custom",
    row_annotation=["Ensemble"],
    col_annotation=["blobs"],
    row_cluster=True,
    col_cluster=True,
    show_rownames=True,
    show_colnames=False,
    row_dendrogram=True,
    xlabel="Genes",
    ylabel="Patients",
    legend_hpad=1,
    legend_vpad=2,
    legend_hgap=6.0,
    legend_vgap=2.0,
    legend_width=25.0,
    legend_order=["Z-score", "Ensemble", "blobs"],
    legend_kws={"extend": "neither", "ticks": [-12.0, 11.0], "format": "%.0f"},
    xticklabels_rotation=20,
    xlabel_labelpad=0,
)
cmp.ax.set_title("Heatmapplot")

# cnsplots 0.8.0 relayouts on every draw. Exporting at a different dpi than the
# build canvas would trigger that relayout and shift panels, so detach the draw
# handler after the layout has converged.
assert mp.fig is not None
assert mp._draw_event_cid is not None
mp.fig.canvas.mpl_disconnect(mp._draw_event_cid)
mp._draw_event_cid = None

# Save final figure next to this script unless the gallery env var is set.
gallery_output_dir = Path(
    os.environ.get("CNSPLOTS_GALLERY_OUTPUT_DIR", str(Path(__file__).resolve().parent))
)
gallery_output_dir.mkdir(parents=True, exist_ok=True)
cns.savefig(gallery_output_dir / "Figure1.pdf", bbox_inches=None, transparent=False)
cns.savefig(gallery_output_dir / "Figure1.svg", bbox_inches=None, transparent=False)
