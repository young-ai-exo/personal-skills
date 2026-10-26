## [1.8.0] — 2026-10-26

Tracks `cnsplots` 0.8.0, a units-and-export release: dimensions are now
documented as **points (1/72 inch)** rather than pixels, `figure()` returns the
`Figure` instead of `None`, and `savefig()` gained explicit export controls.
Also fixes two claims that were already wrong before this release.

The numerical geometry did not change, so every measured figure size and journal
conversion in this skill carries over unchanged; what changed is the vocabulary,
the figure handle, and the export workflow.

### Added
- `SKILL.md` documents `savefig()`'s `fig=`/`dpi=`/`transparent=`/`bbox_inches=`/
  `pad_inches=` and the rule that matters in practice: a journal column width is
  a **canvas** width, and the default `savefig_bbox='tight'` crops the saved file
  to its artists. Measured: a 519-pt (183 mm) canvas holding one 240x150 panel
  saves at 94.4 mm wide, and at 183.1 mm with `bbox_inches=None`.
- `SKILL.md` documents `unit="pt"|"in"|"mm"` on `figure()`/`multipanel()`/
  `panel()`, and that panel `unit` overrides the constructor's while margins stay
  in points and `pad_left`/`pad_top` stay in display pixels.
- `SKILL.md` documents the statistics accessors: `get_comparison_results`,
  `get_survival_results`, `get_roc_results`, `get_precision_recall_results`,
  `get_calibration_results`, plus the paired `test=`/`subject=` options.
- `references/plot-catalog.md` adds `precisionrecallplot` and `calibrationplot`
  with their accessors, `get_comparison_results`, and the three palette functions
  `available_palettes`, `register_palette`, `get_palette_colors`.
- `references/journal-specs.md` documents that the context only reaches rcParams
  when `cns.figure()`/`setup_matplotlib()` is called inside the block.
- `scripts/journal_preset.py --code` now emits `max_width=<mm>, unit="mm"` and
  `bbox_inches=None`, so the emitted block produces the exact column width.
  Verified: 183 mm in, 183.0 mm out.

### Changed
- **Unit vocabulary changed from pixels to points throughout.** No number
  changed: `inches = points / 72` is the same conversion the skill already used,
  and 0.8.0's settings defaults are byte-identical to 0.7.0, re-measured across
  all 78 settings and the 33-key rcParams diff.
- `cns.figure()` returns the `Figure` (also current). Every example that reached
  the figure through `plt.gcf()` now binds the return value instead;
  `templates/mpl_grid_repeat.py` dropped its now-unused pyplot import.
- `settings.context()` wraps `matplotlib.rc_context()`, so rcParams are restored
  on exit too, including nested contexts and exception paths.
- `mp.newline()` is a true row break. It was **broken** in 0.7.0: a single call
  on an A+B row did not break it (measured rows = 1); on 0.8.0 it does (rows = 2).
  Repeated calls and empty layouts still add no blank rows.
- `scripts/dump_style.py` enumerates palettes through `available_palettes()` when
  present, recovering six names the hardcoded probe had been omitting (`Lancet`,
  `JAMA`, `JCO`, `OkabeIto`, `TolBright`, `TolMuted`) and classifying each as
  qualitative or continuous.
- Re-pinned `composition-patterns.md` source citations to the 0.8.0 package:
  `_multipanels.py` lines 460 / 420 / 504.

### Fixed
- **`Ecotyper1` membership was stated wrongly.** `PINK` is not a member and
  `GRAY` is; the constants that belong to the default palette are `RED`, `BLUE`,
  `GREEN`, `ORANGE`, `PURPLE`, `YELLOW`, and `GRAY`.
- **Diverging colormap names were claimed to be valid `color_cycle` values.**
  Measured: `BuRd_custom`, `OrBu_custom`, `WhYlOrRd_custom`, `YlGnBu_custom`, and
  `parula` return colormap objects and raise `ValueError` there; only `BlueRed`
  works as a cycle. Both errors predate 0.8.0 and were found while re-checking.
- `SKILL.md` workflow step numbering repeated 2 and 3 after the journal step,
  which also had no body; steps now run 1 through 8 with the journal check
  implemented.
- `references/color-strategy.md` described the greyscale check with Rec. 601 luma
  while the shipped script had already moved to CIE L*; restated with measured
  CIE L* values.
- **`upsetplot` "spills outside its panel" was wrong, and pre-dated 0.8.0.** It
  takes a dict of sets, not a DataFrame (`TypeError`), and `ax=` does confine the
  group: all four returned axes land inside the host at every host size tried and
  stay there through a later `draw()`. `ax=` is now documented as sufficient; the
  `fig=` plus rescale recipe is kept only as the way to control internal padding
  in a dense figure. `dense_figure.py`'s comment no longer gives the wrong reason
  for its (still correct) approach.
- **The multipanel wrap threshold was quoted without its content dependence.**
  The reserve includes rendered decorations, so a 150- and a 300-point panel share
  a row from `max_width=507` when empty but need **519** with a boxplot in each.
  Both numbers are now stated with their condition, in `SKILL.md`,
  `troubleshooting.md`, and `templates/mixed_grid_in_panel.py`.
- `scripts/journal_preset.py` said "pixels" in its docstring and output, and
  still emitted the pre-0.8.0 `savefig` form; both corrected.
- `references/journal-specs.md` had the Wong palette paragraph duplicated
  verbatim; the duplicate is removed and `OkabeIto` is noted as the built-in
  equivalent (same eight hexes, black last rather than first).
- `setup_ggplot()` returns an R theme string, not `None`; the docs had grouped it
  with the `None`-returning setup helpers.
- `references/composition-patterns.md` had two code blocks importing pyplot after
  the move to `fig = cns.figure(...)` made it unused.
- `references/journal-specs.md` and `references/composition-patterns.md` now carry
  re-pinned source line numbers for the installed 0.8.0 package.

### Conformance
Packaging fixes against the skill-authoring conventions, found by auditing the
skill with the `skill-creator` validator and the `writing-for-agents` guidance.
`quick_validate.py` reported the skill valid both before and after; these are
soft-convention fixes, not spec violations.

- **Helper-script paths were spelled two ways.** Ten references across four
  files (`troubleshooting`, `plot-catalog`, `journal-specs`, `color-strategy`)
  wrote `python3 scripts/<name>.py`, which resolves against the user's project
  root and fails with `FileNotFoundError`; `SKILL.md` mandates the `$SKILL_DIR`
  prefix. All now use `python3 $SKILL_DIR/scripts/<name>.py`, and
  `troubleshooting.md` states the rule at the top of the file.
- **The two 300-plus-line references had no contents list.**
  `composition-patterns.md` (8 sections) and `dense-figures.md` (11 sections) now
  open with an anchor-linked table of contents; all 19 anchors were checked
  against GitHub's slug rules.
- **A `scripts/__pycache__/` with a `.pyc` had accumulated** from importing
  `dump_style.py` as a module during verification. Gitignored, so never committed,
  but a recursive install copy would have shipped it. Removed; running the scripts
  as scripts does not recreate it.

### Verified
`cnsplots` 0.8.0 on Python 3.12.14 / matplotlib 3.10.9, in the mamba env upgraded
in place from 0.7.0. All six scripts and all six templates exit zero, including
both vendored upstream showcase figures. No API break affected any bundled file.
See `skill.json` → `verification`.

## [1.7.0] — 2026-09-01

Recommends overriding two installed defaults (`palette_seq='gnuplot'` and
Helvetica-first `font_sans_serif`) that conflict with journal requirements and
perceptual uniformity, and replaces the Rec. 601 luma approximation with rigorous
CIE L* measurements.

### Added
- `scripts/recommended_overrides.py` — explains why `palette_seq='viridis'` and
  Arial-first font order are recommended, with measured perceptual-uniformity
  reasoning. `--code` emits a ready three-line block to paste at script top.
- `scripts/dump_style.py` gains `colormap <name>` mode, which measures perceptual
  uniformity of a continuous colormap: CIE L* range, monotonicity, step-size
  coefficient of variation, descending-step count, and greyscale collisions (value
  pairs >0.1 apart in data space that fall within 1 L* and become
  indistinguishable when printed). Verified: `gnuplot` reports CV 0.66, 4
  descending steps, 39 collisions; `viridis` reports CV 0.07, 0 descending, 0
  collisions.
- Workflow section 2 in `SKILL.md` now mandates applying the overrides at the top
  of every plotting script, with the full reasoning inline.

### Changed
- **`scripts/dump_style.py greyscale` now uses CIE L*** (perceptual lightness)
  rather than Rec. 601 luma, and reports pairs within 5 L* rather than 0.10 luma.
  The Rec. 601 approximation is too crude: it reported `gnuplot` as monotonic when
  rigorous CIE L* shows it is non-monotonic with 4 descending steps and CV 0.66.
  `Ecotyper1` has 6 pairs within 5 L* (e.g. entries 0 and 3 differ by 0.4 L*,
  entries 2 and 6 by 0.2 L*), meaning those hues collapse in greyscale.
- `references/journal-specs.md` and `references/color-strategy.md` replace the
  incorrect "gnuplot is a rainbow" reasoning with measured CIE L* data: gnuplot is
  non-monotonic (CV 0.66, identical to the canonical counterexample `jet` at 0.65)
  and produces 39 value pairs separated by >0.1 in data space that collapse to
  within 1 L* in greyscale (e.g. data 0.19 and 0.43 render at L* 97.5 and 98.2).
  `viridis` is strictly monotonic (CV 0.07, zero collisions) and starts dark (L*
  14.9, readable on white). Both documents now recommend overriding
  `palette_seq='viridis'` at script top.
- `references/journal-specs.md` adds that the installed
  `settings.multipanel_max_width=540` (190.5 mm) exceeds all three journals'
  widest columns (Cell 174, Nature 183, Science 184), and that
  `font_sans_serif` prioritises Helvetica, which means Cell Press submissions
  embed Helvetica rather than the required Arial. Moving Arial to the front while
  keeping fallbacks ensures compliance without breaking on systems that lack Arial.
- `references/troubleshooting.md` adds "Quantitative heatmap looks misleading in
  greyscale" and notes that `multipanel_max_width=540` exceeds all journals.

### Rationale
The installed `palette_seq='gnuplot'` makes equal data steps look unequal and
collapses distinct values in greyscale, which is a **data integrity issue** rather
than a style preference. The installed `font_sans_serif` order means macOS users
silently submit Helvetica to Cell Press rather than the required Arial. Both
issues survive into publication unless caught, and neither is obvious without
measurement. The skill now surfaces them at workflow step 2 with measured
reasoning, provides a ready override block, and gives the tools (`dump_style.py
colormap`) to verify claims rather than trust documentation.

The CIE L* upgrade replaces a 1990s TV-era luma approximation with the perceptual
standard that actually predicts whether two colours are distinguishable. Rec. 601
told us gnuplot was fine; CIE L* shows it collapses 39 value pairs and is
non-monotonic. That is why the correction matters.

### Verified
Against `cnsplots` 0.7.0 on Python 3.12.14 / matplotlib 3.10.9: all six scripts
including `recommended_overrides.py` and the new `dump_style.py colormap` mode, all
four templates, both vendored upstream scripts, and a full override block that sets
`palette_seq='viridis'` and moves Arial first. See `skill.json` → `verification`.

## [1.6.0] — 2026-09-01
