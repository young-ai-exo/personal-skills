# Changelog — python-script-conventions skill

## [1.7.0] — 2026-10-30

### Added
- **Fail-Fast Boundary Contract vs. Trusted Core (§4.4)** — Strictly separates boundary I/O validation from core data processing logic. Mandates validating file existence and required DataFrame columns (`StrEnum` / schema) once at the I/O boundary (`load_*` or `main()`), while treating all `CORE LOGIC` functions as a 100% Trusted Zone with zero defensive checks (`if col in df.columns:`, `isinstance()`, `.get()` fallbacks).
- **Strict Column Scoping** — Hard rule requiring agents to touch, validate, cast, or transform ONLY columns explicitly required by the prompt; all unrelated columns remain untouched.
- **DataFrame Transformation & Reviewability Patterns (§5.3)** — Establishes human review speed standards for tabular data:
  - **Named Boolean Masks**: Break complex conditions into 2-4 named boolean Series with clear domain semantics.
  - **Idiomatic Vectorized APIs**: Comprehensive lookup table mapping domain transformations to native vectorized operators (`np.where`, `np.select`, `pd.cut`, `.isin`, `.map`, `.groupby().transform()`), explicitly barring row-wise helpers, `.apply(axis=1)`, and loops over rows.
  - **Readable Step-by-Step Pipelines**: Enforces 1-3 lines per transformation step and descriptive intermediate names over cryptic 5-level nested one-liners.
- **Common Pitfalls 13 & 14 (§6.3)** — Documents defensive schema check bloat in core logic and misuse of `.apply(axis=1)` / `.iterrows()`.
- **Quality Gate Template (`templates/pyproject.toml`)** — Bundles full Ruff configuration with explicit rule catalog (C901 complexity ≤ 8, PLR09 size limits, TID251 banned APIs, strict print/logging bans) and Astral's `ty` static type checker.

### Changed
- **Hard Rules expanded** — Codified boundary validation contract, strict column scoping, and native vectorized idioms.
- **Project Module Imports pattern (§1.4)** — Upgraded to `Path(__file__).resolve().parent` + `sys.path.insert(0, str(SRC_DIR))` with idempotency check (`if str(SRC_DIR) not in sys.path:`), ensuring symlink robustness and local-first import priority.
- **Guard Clauses guidance (§4.1)** — Clarified that guard clauses must be used sparingly for valid empty data states, never for schema paranoia or type checking in core functions.
- **Reference Template (`templates/agent_script_template.py`)** — Refactored to demonstrate the boundary contract (validating required columns at the I/O boundary in `main()`) and idiomatic vectorized assignment in the Trusted Zone.
- **Verification Checklist (§7)** — Added boundary contract, trusted zone purity, strict column scoping, named masks, and deterministic quality gate checks.

## [1.6.0] — 2026-09-22

### Added
- **Project module import pattern (§1.4)** — Standardized dynamic path resolution using `Path(__file__).parent.resolve()` and `sys.path.append()`.

## [1.5.0] — 2026-09-01

### Added
- **Hard Rules section** — Non-negotiable conventions listed upfront (imports location, loguru usage, type hints, pathlib, dataclass flags, entry point pattern)
- **Workflow section** — Clear 4-step process (choose script type → start from template → fill sections → verify)
- **Template enhancements** — Added checklist at top, `REPLACE THIS` markers throughout, inline comments explaining dataclass flags (`kw_only`, `slots`, `frozen`)

### Changed
- **Restructured main SKILL.md** — Consistent section numbering (§1-7), improved navigation flow
- **Common Pitfalls reorganized** — Split into 3 categories: Layout & Imports (most frequent), Type System & Configuration, Control Flow & Domain Logic
- **Advanced Patterns section** — Streamlined with summaries and clear links to reference docs (signal-based classification, stem-prefix classification)
- **Domain scope clarified** — Explicitly states "developed for bioinformatics data-processing workflows, but patterns apply to any data-science script"
- **Path references standardized** — All template references now use `$SKILL_DIR/templates/agent_script_template.py`
- **Template section header** — Renamed "MAIN ENTRY POINT" to "MAIN EXECUTION" for consistency with documentation
- **Verification step (§Workflow 4)** — Now points at the §7 checklist plus `ruff check` for the mechanical rules, instead of a bundled script

### Removed
- **`scripts/verify_conventions.py`** — Added and then removed within this same release. A regex implementation was written first, and testing against six fixtures found five defects: nested imports were undetectable in files lacking section banners (the check keyed off the banner itself), a `@dataclass(kw_only=True)` config missing `slots`/`frozen` passed cleanly, `print` appearing in a docstring or string literal was reported as a violation, and a script following the three-line banner format documented in §1.2 was rejected because only the template's one-line format was matched. An AST rewrite fixed those cases, but the result still only covered the mechanically checkable rules, and it needed a `Convention-exempt` escape hatch to pass its own checks — a marker any script could add to silence the checker. `ruff` already covers unused imports, module-level import placement (E402), and `print` calls (T201) with far more rigor, and the rules that matter most here (single-line docstrings, section layout, docstring quality) are judgement calls. Shipping a bespoke checker that is weaker than `ruff` on the overlap and silent on the rest was not worth the maintenance surface.

### Improved
- Progressive disclosure — Advanced patterns summarized in main doc, details in references/
- Usability — Matches cnsplots skill structure (Hard Rules → Workflow → detailed sections)

## [1.4.0] — 2026-08-12
Migrated from Sotdo/personal_skills. Original work by Yusheng Yang.
