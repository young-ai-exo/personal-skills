"""Upstream cnsplots showcase, Figure 2. Vendored verbatim as reference.

Source: https://cnsplots.farid.one/latest/examples/showcase.html
Copyright Farid Rashidi, BSD-3-Clause. Not our work; do not edit.
See README.md in this directory.

Shares the preamble and helpers with figure1.py, which the upstream page
presents as one continuous script.
"""

import os
from pathlib import Path

import cnsplots as cns
import matplotlib.image as mpimg
from scipy import stats

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


cns.settings.title_fontweight = "normal"
gallery_output_dir = Path(os.environ.get("CNSPLOTS_GALLERY_OUTPUT_DIR", "."))
gallery_output_dir.mkdir(parents=True, exist_ok=True)

mp = cns.multipanel(
    max_width=540, title="Figure 2", title_fontweight="bold", loc="left"
)
detached_panel_layouts = []

# Panel A: load pathology image
ax = mp.panel("A", 149, 237, pad_left=-70)
ax.imshow(_read_showcase_image("image1.webp"))
ax.set_title("Pathology Image")
ax.set_axis_off()

# Panel B: load immunofluorescence image
ax = mp.panel("B", 116, 102, pad_left=-50)
ax.imshow(_read_showcase_image("image2.webp"))
ax.set_title("Immunofluorescence")
ax.set_axis_off()

# Panel C: dotplot
host_c = mp.panel("C", 80, 90, pad_top=20, pad_left=40, margin_right=20)
tips_minmax = tips_df.groupby(["day", "sex"]).agg({"total_bill": ["min", "size"]})
tips_minmax.columns = ["min", "size"]
tips_minmax = tips_minmax.reset_index()
dp = cns.dotplot(
    tips_minmax,
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
    ax=host_c,
)
hm_ax = dp.hm_ax
for label in hm_ax.get_xticklabels():
    label.set_ha("right")
    label.set_rotation_mode("anchor")
dp.ax_heatmap.set_title("")
hm_ax.set_title("Dotplot")
dp.dot_legend.get_title().set_fontsize(6)
for text in dp.dot_legend.get_texts():
    text.set_fontsize(6)
dp.cbar_ax.tick_params(labelsize=6, length=0)
dp.cbar_ax.set_title("size", fontsize=6, pad=1, loc="right")
dp.cbar_ax.set_ylabel("")

# Panel D: cumulativeincidenceplot
ax = mp.panel("D", 85, 85, margin_right=0, color_cycle="BlueRed")
ax = cns.cumulativeincidenceplot(
    data=cumulative_incidence_df,
    duration="time",
    event="event",
    hue="group",
    hue_order=["Control", "Treatment"],
    pvalue_position=(0, 0.9),
    show_risk_table=False,
)
legend = ax.get_legend()
legend.set_loc("lower right")
if legend is not None:
    legend.set_title(None)
    for text in legend.get_texts():
        text.set_text(text.get_text().split(" (", 1)[0])
ax.set_xlabel("Time")
ax.set_ylabel("Incidence")
ax.set_title("Cumulative Incidence")

# Panel E: load western blot image
ax = mp.panel("E", 116, 102, below="B", pad_left=-50)
ax.imshow(_read_showcase_image("image4.webp"))
ax.set_title("Western Blot")
ax.set_axis_off()

# Panel F: lineplot
ax = mp.panel("F", 80, 80, below="C", margin_top=15)
ax = cns.lineplot(
    data=line_df,
    x="timepoint",
    y="signal",
    hue="condition",
    marker="o",
    errorbar=None,
)
legend = ax.get_legend()
if legend is not None:
    legend.remove()
ax.set_title("Lineplot")

# Panel G: qqplot
ax = mp.panel("G", 80, 80, below="D", margin_top=15, margin_right=0)
ax = cns.qqplot(iris_df, x="sepal_length", dist=stats.norm, fit=True, line="45")
ax.set_title("Qqplot")

mp.newline()

# Panel H: h&e histology image
ax = mp.panel("H", 319, 160, pad_left=-60)
ax.imshow(_read_showcase_image("image3.webp"))
ax.set_title("H&E Histology")
ax.set_axis_off()

# Panel I: placeholder plot
ax = mp.panel("I", 175, 155, margin_right=0)
cns.placeholderplot("A placeholder plot (155⨯175)\nYou can use to fill it up later.")
ax.set_title("Placeholder")

mp.newline()

# Panel J: lollipopplot
ax = mp.panel("J", 40, 80, color_cycle="NEJM", margin_right=15, margin_bottom=20)
ax = cns.lollipopplot(data=tips_df, x="day", y="total_bill", pairs="all")
ax.set_title("Lollipopplot")
ax.set_xticklabels(
    ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor"
)

# Panel K: confusionplot
ax = mp.panel("K", 60, 60, pad_top=30, margin_right=10)
ax = cns.confusionplot(
    data=confusion_df,
    x="pred",
    y="truth",
    add_pvalue=False,
    x_order=["Neg", "Pos"],
    y_order=["Neg", "Pos"],
    cmap="Blues",
    # pvalue_x_pad=-0.3,
    # pvalue_y_pad=3.8,
)
ax.set_title("Confusionplot")

# Panel L: forestplot
host_l = mp.panel(
    "L", 100, 100, color_cycle=[cns.CHOCOLATE], pad_left=15, pad_top=10, margin_right=20
)
forest_model = cns.methods.CoxModel(
    data=forest_df,
    duration="time",
    event="event",
    variates=[
        "age",
        "C(risk, levels=['Low', 'High'])",
        "C(stage, levels=['I', 'II'])",
        "np.log(marker)",
    ],
)
forest_model.fit()
forest_ax = cns.forestplot(forest_model, add_pvalue=False, ax=host_l)
forest_ax.set_title("Forestplot")

# Panel M: upsetplot
host_m = mp.panel("M", 200, 120, margin_right=0, pad_left=-100, pad_top=10)
upset_axes = cns.upsetplot(
    upset_sets,
    fig=mp.fig,
    sort_by="cardinality",
    totals_plot_elements=0,
    facecolor="black",
    show_counts=False,
)
upset_axes["intersections"].set_title("UpSetplot")
detached_panel_layouts.append((host_m, list(upset_axes.values()), 0.03, 0.04))

for host_ax, detached_axes, xpad, ypad in detached_panel_layouts:
    _embed_detached_axes(host_ax, detached_axes, xpad=xpad, ypad=ypad)
if mp.fig is not None:
    mp.fig.canvas.draw()

# Save final figure
cns.savefig(gallery_output_dir / "Figure2.svg")
