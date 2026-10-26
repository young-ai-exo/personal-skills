# Journal figure specifications

Figure requirements for Cell Press, Nature, and Science, with the `cnsplots`
point values that satisfy them. Read from the publishers' own author pages in
September 2026; sources at the bottom.

**These are moving targets.** Verify against the journal's current page before
submitting, and check the specific journal rather than the family: sibling titles
diverge materially (see "Sibling journals differ" below).

`cnsplots` sizes are **points** (1/72 inch, the 0.8.0 size unit), so
`mm = pt / 72 * 25.4` and `pt = mm / 25.4 * 72`.

## Column widths

| | Cell Press | Nature | Science |
| --- | --- | --- | --- |
| 1 column | 85 mm / **241 pt** | 89 mm / **252 pt** | 57 mm / **162 pt** |
| 1.5 column | 114 mm / **323 pt** | 120-136 mm / **340-386 pt** | — |
| 2 column | 174 mm / **493 pt** | 183 mm / **519 pt** | 121 mm / **343 pt** |
| 3 column (full page) | — | — | 184 mm / **522 pt** |
| Max height | 200 mm / **567 pt** | 170 mm / **482 pt** | not stated |

Verified on 0.8.0: `cns.multipanel(max_width=519)` produces a canvas 183.09 mm
wide. Every pt value above is `mm / 25.4 * 72` rounded to the nearest integer.

**Those are canvas widths, not artifact widths.** The default save crops to the
artists (`savefig_bbox="tight"`, `pad_inches=0.01`), so a 519-pt canvas whose only
content is one 240x150 panel saves at about **93 mm**, half the column — and the
exact figure moves with the panel's content, because the crop follows the
artists. Measured on 0.8.0 at 288 dpi, `cns.multipanel(max_width=519)` plus
`mp.panel("a", 240, 150)`:

| Panel content | Tight save | `bbox_inches=None` |
| --- | --- | --- |
| empty | 1054 px / 92.96 mm | 2076 px / 183.09 mm |
| `cns.boxplot(tips, x="day", y="total_bill")` | 1064 px / 93.84 mm | 2076 px / 183.09 mm |

The full-canvas save is stable at the canvas width; the tight one is not. For
submission, when the printed width must equal the column width, pass
`cns.savefig(path, bbox_inches=None)` and size the canvas to the column;
otherwise the tight crop silently delivers roughly half the width you configured.

Science counts the printed page as three columns, so its "2 column" is a
mid-width figure, not full width. Its full width (184 mm) is within a millimetre
of Nature's double column (183 mm).

Nature's own pages contradict each other on widths: `final-submission` and the
dedicated figure guide say 89/183 mm, while `formatting-guide` and
`initial-submission` say 90/180 mm. Treat 89/183 as current. Nature's 170 mm
height cap exists specifically to leave room for the legend beneath; the 247 mm
figure quoted elsewhere is the full physical page depth, not usable figure
height.

## Type and line weight

| | Cell Press | Nature | Science |
| --- | --- | --- | --- |
| Font size in figure | 6-8 pt | **5-7 pt** | 7 pt target, ≥5 pt |
| Typeface | Arial | Helvetica or Arial | Helvetica preferred |
| Panel labels | capital A, B, C | **8 pt bold lowercase a, b, c** | 10 pt bold capital A, B, C, upper left |
| Line/stroke weight | 0.5-1.5 pt | 0.25-1 pt | ≥0.5 pt |
| Min symbol size | not stated | not stated | 6 pt |

`cnsplots` defaults are `title_fontsize=8`, `legend_fontsize=7`,
`axes_linewidth=0.5`. Line weight satisfies all three. Font size satisfies Cell
(8 pt is its ceiling) but **exceeds Nature's 7 pt cap**; see the presets below.

Science's 10 pt panel labels are an outlier: they are larger than its own 7 pt
body target, and larger than Nature's 8 pt.

## Resolution and format

| | Cell Press | Nature | Science |
| --- | --- | --- | --- |
| Photographic / halftone | ≥300 dpi | ≥300 dpi (300-600) | ≥300 dpi |
| Black & white | ≥500 dpi | — | — |
| Line art (raster) | ≥1000 dpi | vector required | ≥300 dpi |
| Combination | ≥500 dpi | — | ≥300 dpi |
| Vector | PDF, EPS preferred | **.ai/.eps/.pdf required, editable layers** | PDF/EPS/AI preferred |
| Colour mode | RGB preferred | RGB recommended, CMYK allowed | not stated |

**`cnsplots` defaults to `savefig_dpi = 288`, which is below the 300 dpi floor
all three require.** 288 is 72x4; the nearest compliant multiple is 360 (72x5).
Raise it for any raster deliverable.

Nature is the strictest on format: editable vector with live layers is required
for main figures, and `.jpeg`, `.tiff`, `.png` are explicitly **not accepted**.
It also requires TrueType font embedding, `pdf.fonttype = 42` — which cnsplots
already sets, along with `svg.fonttype = 'none'` to keep SVG text editable. Do
not outline or flatten text.

Science does not state a colour mode anywhere accessible; its detailed prep guide
is CAPTCHA-gated, so treat RGB-vs-CMYK as unverified there.

## Colour accessibility

All three converge on one instruction: **do not pair red and green.**

- Cell: "Avoid red/green together", noting 5-10% of the population is affected.
- Nature: "Avoiding red/green combinations and rainbow scales helps readers with
  colour blindness"; requires an accessible palette and cites Wong, B. *Points of
  view: Colour blindness.* Nature Methods 8, 441 (2011); requires >4.5 text
  contrast ratio; forbids coloured text, telling authors to use keys or keylines
  in the figure instead of naming colours in the caption, because colour-blind
  readers cannot follow those descriptions.
- Science: "Avoid using red and green together"; "Do not use colors that are
  similar in hue"; "Avoid using grayscale"; use white type and scale bars over
  dark image regions; in colour figures, type over a colour region should be
  bold.

Nature's Wong palette, published with hex values: `#000000` black, `#e69f00`
orange, `#56b4e9` sky blue, `#009e73` bluish green, `#f0e442` yellow, `#0072b2`
blue, `#d55e00` vermillion, `#cc79a7` reddish purple. 0.8.0 ships it as
`cns.palettes("OkabeIto")` — the same eight hexes, but black moved to the end
(`#e69f00` first), so `color_cycle="OkabeIto"` gives the published set in a
different order. Reorder explicitly if the first series must be black.

`cnsplots` ships `Cell`, `Nature`, `Science`, `NEJM`, `Lancet`, `JAMA`, `JCO`,
`OkabeIto`, `TolBright`, and `TolMuted`, but the four journal-*named* ones are
styled after those journals, not the publishers' accessibility recommendations. The
`Science` palette contains `#ee0000` red and `#008b45` green at entries 1 and 2,
adjacent in the cycle, which the journal's own guidance says not to pair. **Do not
assume a palette named after a journal satisfies that journal's colour advice.**
Check adjacent entries before using the first N colours of any of them, and see
[color-strategy.md](color-strategy.md).

The installed `palette_seq='gnuplot'` is unsuitable for quantitative data:
measured across 64 samples in CIE L* (perceptual lightness), it is non-monotonic
(4 descending steps out of 63, maximum dip -0.62 L*) with a step-size coefficient
of variation of 0.66, essentially identical to the canonical rainbow counterexample
`jet` at 0.65. It produces 39 value pairs separated by more than 0.1 in data space
that collapse to within 1 L* in greyscale (e.g. data values 0.19 and 0.43 render
at L* 97.5 and 98.2). `viridis` is strictly monotonic (all 63 steps ascending) with
CV 0.07 and zero greyscale collisions. Override at script top:
`cns.settings.palette_seq = 'viridis'`. See
`$SKILL_DIR/scripts/recommended_overrides.py`.

## Statistics in legends

- Cell: "Plot the individual data points in addition to indicating the average ±
  error for graphs displaying quantitation of a dataset."
- Nature: "All error bars and statistics must be defined in the figure legend."
  Legends under 300 words, beginning with a brief title. Requires **exact n**
  values (individual values, not a range, when n varied), exact P values for both
  significant and non-significant results, F values and degrees of freedom for
  ANOVA, t and df for t-tests, and whether tests were one- or two-tailed.
- Science: "The values for N, P, and the specific statistical test(s) performed
  for each experiment should be included in the appropriate figure caption or main
  text." Captions capped at 200 words with a bold title line. Error bar
  conventions are not stated.

This is why the skill treats `pairs`, test choice, and error bar meaning as
analysis decisions that must be surfaced rather than defaulted. See the
statistical integrity section of `SKILL.md`.

## Presets

Apply with `cns.settings.context(...)` so the change is scoped. Widths go to
`max_width` on `multipanel`, or `width` on `cns.figure`.

**The context only reaches matplotlib if `cns.figure()` or
`cns.setup_matplotlib()` runs inside the block.** Verified on 0.8.0: a block that
only assigns settings and exits leaves `axes.labelsize` at `medium` and
`savefig.dpi` at `figure`. Calling `cns.figure()` or `mp.panel(...)` inside the
block applies them, and everything reverts on exit. `cns.multipanel(...)` on its
own does *not* apply them — the first `mp.panel()` call does.

```python
# Nature: 7 pt type cap, 300+ dpi, double column
with cns.settings.context(title_fontsize=7, legend_fontsize=6, savefig_dpi=600):
    mp = cns.multipanel(max_width=519)          # 183 mm canvas
    ax = mp.panel("a", 240, 150)                # lowercase labels
    ...
    cns.savefig("figure1.pdf", bbox_inches=None)   # keep the 183 mm canvas

# Cell Press: defaults already fit 6-8 pt; only dpi needs raising
with cns.settings.context(savefig_dpi=500):
    mp = cns.multipanel(max_width=493)          # 174 mm, 2 column

# Science: 1 column is very narrow at 57 mm
with cns.settings.context(title_fontsize=7, legend_fontsize=5, savefig_dpi=600):
    cns.figure(width=162, height=140)           # 57 mm
```

Verified on 0.8.0: `settings.context(title_fontsize=7, legend_fontsize=6)` sets
`axes.labelsize`, `axes.titlesize` to 7.0 and `legend.fontsize` to 6.0, and
restores on exit. `savefig_dpi=600` reaches `rcParams["savefig.dpi"]`.
`mp.panel("a", ...)` accepts lowercase labels and `mp.get_axes("a")` retrieves
them. The three presets produce canvases of 183.09 mm (`max_width=519`),
173.92 mm (`max_width=493`), and 57.15 mm (`figure(width=162)`).

Without `bbox_inches=None` the Nature preset does **not** save at 183 mm. With a
tips boxplot in the single 240x150 panel it saves at 92.96 mm (2196 px at 600
dpi), and at 91.99 mm with the panel left empty; `bbox_inches=None` gives the full
183.09 mm (4325 px). The exact tight width tracks the artists, so check the saved
PNG rather than assuming the canvas number.

The installed `settings.multipanel_max_width=540` (190.5 mm) exceeds all three
journals' widest columns (Cell 174, Nature 183, Science 184). It is a canvas upper
bound rather than a target size, so exceeding it does not automatically violate a
journal requirement, but the default does not guide toward compliance. Set it
explicitly for the target journal.

`python3 $SKILL_DIR/scripts/journal_preset.py` prints these numbers for a named
journal so you do not have to transcribe them.

## Sibling journals differ

Do not generalise from the flagship:

- **Nature Communications**: 88/180 mm columns, thinnest line 1 pt (not 0.25),
  1200 dpi fallback for raster line art.
- **Scientific Reports**: thinnest line 1 pt, accepts CMYK without conversion,
  and requires stating whether a value after ± is s.e.m. or s.d.
- **Science Advances / Science Immunology**: prefer **Myriad** rather than
  Helvetica, and 9 pt panel labels rather than 10 pt. Science Advances states the
  1000 dpi raster line-art tier that Science itself does not.
- **Nature Extended Data** inverts the main-figure rules: raster only
  (`.jpeg` preferred), 300 dpi as a *maximum*, RGB mandatory, 10 MB cap.

## Sources

- Cell Press figure guidelines: <https://www.cell.com/figureguidelines>
- Cell journal policies: <https://www.cell.com/cell/information-for-authors/journal-policies>
- Elsevier artwork instructions: <https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/>
- Nature final submission: <https://www.nature.com/nature/for-authors/final-submission>
- Nature figure guide: <https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/>
- Nature formatting guide: <https://www.nature.com/nature/for-authors/formatting-guide>
- Science initial manuscript: <https://www.science.org/content/page/instructions-preparing-initial-manuscript>
- Science revised manuscript: <https://www.science.org/content/page/instructions-preparing-revised-manuscript>

Not verifiable at the time of writing: Science's colour mode, maximum figure
height, and error bar conventions, which appear to live only in a CAPTCHA-gated
prep-guide PDF.
