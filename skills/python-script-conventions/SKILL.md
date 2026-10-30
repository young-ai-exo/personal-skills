---
name: python-script-conventions
description: Use when generating, modifying, or reviewing Python scripts (3.12+). Specifies section layout, boundary validation vs. trusted core (anti-bloat), DataFrame transformation reviewability patterns, import ordering (including project module imports via Path(__file__)), type system, logging, dataclass patterns, and AI-agent-friendly design principles. Load this skill whenever creating or editing a .py file — especially for bioinformatics/data-science scripts.
version: 1.7.0
author: Yusheng Yang
license: MIT
metadata:
  hermes:
    tags: [python, conventions, style-guide, code-quality, ai-design, anti-bloat]
    related_skills: [plan, writing-plans, test-driven-development, project-scaffolding, systematic-debugging]
---

# Python Script Conventions (Modern Python 3.12+)

## Overview

This skill defines the coding standards, anti-bloat guidelines, and design patterns to follow when generating or modifying Python scripts in this workspace. It codifies a consistent layout, modern Python 3.12+ idioms, and AI-agent-friendly design so that every script reads like it belongs to the same codebase and maximizes human code-review speed and cognitive clarity.

**Core Philosophy (The Reviewability Sweet Spot):**
AI coding agents naturally gravitate toward two review-taxing extremes: defensive bloat (layering paranoid `if col in df.columns`, `isinstance()`, and `.fillna()` fallbacks on every function) or cryptic code-golf (dense, deeply nested one-liners). This skill enforces the golden middle: **high-signal, declarative step-by-step code** where structure is predictable, boundary validation protects a trusted core, and data transformations are flat and readable.

**Domain focus:** Developed for bioinformatics data-processing workflows, but the patterns (section layout, boundary contracts, vectorized pipelines, type system, logging, dataclass config) apply to any data-science or analysis script that reads files, processes data, and writes outputs.

The companion files:
- `$SKILL_DIR/templates/agent_script_template.py` provides a concrete reference implementation of these principles. **Always open that template as a starting point when writing a new script from scratch.**
- `$SKILL_DIR/templates/pyproject.toml` provides the reference configuration for deterministic linter and type-checker gates (`ruff` + `ty`).

Apply these rules thoughtfully — if a rule would make a particular script worse, adapt accordingly.

---

## Hard Rules

- **All imports in the top-level IMPORTS section** — never in function bodies or class definitions
- **Project module imports via `Path(__file__).resolve().parent` + `sys.path.insert(0, ...)`** — avoid hardcoded workflow paths and guarantee local-first import priority (see §1.4)
- **Fail-Fast boundary contract** — validate file paths and required DataFrame `StrEnum` columns ONCE at the I/O boundary (`load_*` or `main()`); treat all `CORE LOGIC` functions as a 100% Trusted Zone with zero defensive checks (`if col in df.columns:`, `isinstance()`, or `.get()` fallbacks)
- **Strict column scoping** — touch, validate, cast, or transform ONLY the DataFrame columns explicitly required by the prompt; leave all other columns completely untouched
- **Native vectorized idioms** — use built-in `pandas` and `numpy` vectorized methods (`np.where`, `np.select`, `pd.cut`, `.isin`, `.map`, `.groupby().transform()`) instead of custom row-wise helper functions, `.apply(axis=1)`, or Python `for` loops over rows
- **Use `loguru` exclusively** — no `print()` or stdlib `logging`
- **Type hints on every function signature** — both parameters and return value
- **Single-line docstrings** — type hints carry the type information
- **`pathlib.Path` everywhere** — no `os.path.join()` or `os.path.exists()`
- **`@dataclass(kw_only=True, slots=True, frozen=True)`** for configuration objects
- **`if __name__ == "__main__": sys.exit(main())`** entry point pattern

---

## Workflow

### 1. Choose script type

**Standalone script** (7 sections: IMPORTS → DECORATORS → CONSTANTS → CONFIG → LOGGING → CORE → MAIN) or **library module** (3 sections: IMPORTS → CONSTANTS → CORE only). See §1.1 below for details.

### 2. Start from the template

Copy `$SKILL_DIR/templates/agent_script_template.py` as your starting point. The template demonstrates every pattern described below. If starting in a project lacking quality gate configs, copy `$SKILL_DIR/templates/pyproject.toml` to the project root.

### 3. Fill sections in dependency order

Constants → data models → functions → CLI → main. Each section depends only on what came before it.

### 4. Verify before finalizing

Walk the checklist in §7 against the finished file. Read the whole script top to bottom rather than checking items from memory — the layout rules are about the file as a whole, and the most commonly missed violations (an import added inside a function, a leftover unused import) are invisible when you only look at the lines you just edited.

For the mechanical subset, lean on real deterministic tooling rather than bespoke scripts:
- `ruff check` enforces unused imports (`F401`), top-level import placement (`PLC0415`), `print` ban (`T201`), pathlib enforcement (`PTH`), cyclomatic complexity ceiling (`C901` max 8), function structural size limits (`PLR09`), and banned APIs (`TID251`).
- `ruff format --check` verifies formatting compliance.
- `ty check` verifies static type consistency and catches redundant defensive `cast()` calls.

The rules that carry the most weight here — single-line docstrings, section layout, boundary contract vs. trusted core, and high-signal readable transformations — are judgement calls guided by this skill and verified against §7.

---

## When to Use

- **Creating any new `.py` script** in this workspace — load this skill first, then open `$SKILL_DIR/templates/agent_script_template.py` as the starting structure.
- **Modifying an existing script** — refactor to match these conventions when the edit is substantial (layout, imports, logging, etc.).
- **Reviewing a PR or diff that includes Python files** — use the checklist (§7) as review criteria.
- **Generating a single-file script** meant for `uv` or standalone execution.

### When NOT to Use

- Libraries or packages with multiple modules (those follow their own structure; this skill targets standalone scripts).
- Jupyter notebooks (use the jupyter-live-kernel skill instead).
- Code snippets in markdown docs (unless they're illustrative of the template).

### Modifying an Existing Script

When *modifying* a script that was written before this skill was applied (or
that partially follows it), **treat the edit as a section-layout review**:

1. Re-read the entire script's section structure before editing — don't just
   jump to the line you want to change.
2. If you're adding a new import, put it in the top-level IMPORTS section,
   **not** next to where it's used in the body. The skill's import ordering
   rules apply to modifications as much as to new files.
3. If the edit is substantial (10+ lines changed, new imports, new functions),
   refactor the file to match the full section layout. This repays quickly
   — the next edit benefits from the structure.
4. Run the verification checklist after the edit, not just before it.

---

## 1. Script Structure & Layout

### 1.1 Standalone Scripts vs Library Modules

A file in ``src/`` is either a **standalone script** (invoked from the
command line) or a **library module** (imported by other scripts). They
have different structures:

**Standalone script** — follows the full 7-section layout (IMPORTS →
DECORATORS → CONSTANTS → CONFIG → LOGGING → CORE → MAIN). Contains
``parse_args()`` + ``if __name__ == "__main__": sys.exit(main())``.

**Library module** — omits the LOGGING, CONFIG, and MAIN sections.
Contains only IMPORTS, CONSTANTS (including enums and dataclasses), and
CORE LOGIC. No ``parse_args()``, no ``main()``, no ``setup_logger()``.
The module-level docstring omits the CLI Usage block from the §3.2
format, but keeps the title, description, I/O spec, and metadata.

For a concrete example of a library module following these conventions, see any shared utility module in a project following this skill (e.g., a `growth_signals.py` that defines classification logic imported by multiple scripts).

### 1.2 Section Order

Scripts should follow this section order, reflecting a natural information **dependency hierarchy** — constants → data models → core logic → CLI → main — so each section only depends on what came before it. Omit sections that a script does not need (e.g., no enums, no decorators).

Always use the `$SKILL_DIR/templates/agent_script_template.py` as the starting point:

```python
# =============================================================================
# IMPORTS
# =============================================================================
...
# =============================================================================
# DECORATORS
# =============================================================================
...
# =============================================================================
# GLOBAL CONSTANTS & ENUMS
# =============================================================================
...
# =============================================================================
# CONFIGURATION & DATACLASSES
# =============================================================================
...
# =============================================================================
# LOGGING SETUP
# =============================================================================
...
# =============================================================================
# CORE LOGIC (FUNCTIONS / CLASSES)
# =============================================================================
...
# =============================================================================
# MAIN EXECUTION
# =============================================================================
...
```

### 1.3 Import Ordering

Group imports into blocks, sorted alphabetically within each block. When importing project modules, use the path setup pattern described in §1.4.

```python
# 1. Standard Library Imports
import argparse
import sys
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

# 2. Data Processing Imports
import pandas as pd

# 3. Third-party Imports
from loguru import logger
```

### 1.4 Project Module Imports

When a script needs to import modules from the project's `src/` directory, use dynamic path resolution to avoid hardcoding workflow paths:

```python
# =============================================================================
# IMPORTS
# =============================================================================
# Standard Library
import sys
from pathlib import Path

# Project path setup (must come before project imports)
SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Project imports
from io_table import read_parquet  # noqa: E402
from figures import (  # noqa: E402
    apply_house_style,
    grid_axes,
    fit_panels,
    save_dual,
)

# Third-party imports
from loguru import logger
import pandas as pd
```

**Key points:**

- Use `Path(__file__).resolve().parent` to get the script's physical directory (resolving symlinks robustly)
- Resolve `SRC_DIR = SCRIPT_DIR.parent / "src"` (adjusting relative depth as appropriate for the script's folder)
- Use `sys.path.insert(0, str(SRC_DIR))` to ensure local project modules take absolute priority over any identically named third-party or system packages
- Guard with `if str(SRC_DIR) not in sys.path:` to ensure idempotency across module reloads or interactive sessions
- Add `# noqa: E402` to project imports — E402 (module level import not at top of file) is unavoidable here since `sys.path` must be modified first
- This pattern stays within the IMPORTS section — it's import-related setup, not a separate section

**When to use this pattern:**

- Workflow scripts in `scripts/` or similar that need to import from `src/`
- Any script outside the package structure that needs project modules

**When NOT to use:**

- Scripts already inside `src/` (use relative imports: `from . import module`)
- Projects installed as packages (`pip install -e .` makes imports available directly)
- Standalone scripts with no project dependencies

**Anti-pattern to avoid:**

```python
# ❌ Don't hardcode the workflow path
from workflow.src.io_table import read_parquet
```

This breaks when:
- The script is moved to a different location
- The project is renamed
- The script is run from a different working directory

### 1.5 Entry Point Pattern

All scripts must use the following pattern at the bottom:

```python
if __name__ == "__main__":
    sys.exit(main())
```

This ensures:
- The script can be imported without executing
- Exit codes are propagated correctly
- `main()` returns an integer (0 for success, non-zero for error)

### 1.6 Configuration Dataclass

Use `@dataclass(kw_only=True, slots=True, frozen=True)` for configuration:

```python
@dataclass(kw_only=True, slots=True, frozen=True)
class AppConfig:
    """Configuration for the script's runtime parameters."""
    input_path: Path
    output_dir: Path
    p_value_threshold: float
    keywords: list[str]
```

- `kw_only=True` → forces keyword arguments (prevents positional confusion)
- `slots=True` → reduces memory footprint
- `frozen=True` → makes the instance immutable (most configs shouldn't change after creation)

### 1.7 Logging with Loguru

Use `loguru` for all output. Never use `print()` or `logging` stdlib:

```python
from loguru import logger

def setup_logger(log_level: str = "INFO") -> None:
    """Configure the Loguru logger."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level:<8} | {message}",
        level=log_level
    )

setup_logger()
```

Add `@logger.catch` to core logic functions for automatic exception logging.

---

## 2. Type System & Modern Python Features

### Type Hints Everywhere

Every function signature must include type hints for parameters and return values:

```python
def filter_dataframe(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    """Filter the Pandas DataFrame based on configured P-value thresholds."""
    ...
```

Use `-> None` for procedures that don't return a value.

### StrEnum for String Constants

When you have a fixed set of related string markers (e.g., column names, operation modes), use `StrEnum`:

```python
from enum import StrEnum

class DataCol(StrEnum):
    GENE_ID = "systematic_name"
    PHENOTYPE = "phenotype"
    PVALUE = "p_value"
```

**Do NOT use StrEnum for:**
- Single unrelated constants (just use a module-level variable)
- Dynamic values that come from user input or config files

### Pathlib Over os.path

Always use `pathlib.Path` instead of `os.path`:

```python
from pathlib import Path

config = AppConfig(
    input_path=args.input.resolve(),  # .resolve() for absolute path
    output_dir=args.outdir.resolve()
)

config.output_dir.mkdir(parents=True, exist_ok=True)
```

### F-strings Only

Use f-strings for all string interpolation. Never use `.format()` or `%`:

```python
logger.info(f"Initial raw data shape: {df.shape}")
logger.info(f"Results saved to {out_file} ({len(df_filtered):,} rows)")
```

---

## 3. Documentation Standards

### 3.1 Single-Line Docstrings for Functions

Function docstrings should be **one line** — type hints carry the type information:

```python
def filter_dataframe(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    """Filter the Pandas DataFrame based on configured P-value thresholds and keywords."""
    ...
```

**Do NOT write multi-line NumPy/Sphinx-style docstrings** with Parameters/Returns blocks. The type annotations already document the types.

### 3.2 Module-Level Docstring Format

Every script must have a comprehensive module-level docstring at the top, following this structure:

```python
"""
Script Title (One Line, Human-Readable)
========================================

1-3 paragraphs describing the business logic, algorithm, and context.
Use bullet lists for multi-step processes.

Input
-----
- Input file path (CSV, TSV, or XLSX) with required columns.
- See ``--input`` / ``--help`` for exact format.

Output
------
- Filtered results saved to the configured output directory.
- File format depends on the script's core logic.

Usage
-----
    mamba run -n bioinformatics python script_name.py
    mamba run -n bioinformatics python script_name.py --input path/to/data.csv --verbose

Author:   [Name] (guidance) + [AI Agent] (implementation)
Date:     YYYY-MM-DD
Version:  X.Y.Z
"""
```

See `references/module-level-docstring.md` for real-world examples.

### 3.3 Change Documentation Format

When documenting code changes (in commit messages, PR descriptions, or change logs), use a **three-column table** format:

```markdown
| Problem | Root Cause | Fix |
|---|---|---|
| Script fails when input CSV is empty | `filter_dataframe()` doesn't check for empty DataFrame | Added guard clause: `if df.empty: return df` |
| P-value filter returns wrong results | Used `<=` instead of `<` for threshold comparison | Changed to `df[DataCol.PVALUE] < config.p_value_threshold` |
```

This format surfaces *why* a change was needed, not just *what* changed.

---

## 4. Control Flow & Error Handling

### 4.1 Guard Clauses

Use guard clauses sparingly to handle legitimate edge cases early and reduce nesting:

```python
def filter_dataframe(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    """Filter the Pandas DataFrame based on configured P-value thresholds."""
    # Guard clause: Return early if the dataframe is empty
    if df.empty:
        logger.warning("Received empty DataFrame. Skipping filtering.")
        return df
    
    # Main logic here (assumes valid schema)
    ...
```

> [!IMPORTANT]
> **Use Guard Clauses for semantic data states, NEVER for schema paranoia.**
> Only guard against valid empty inputs or zero-row filter outputs. Do NOT use guard clauses to check `if col in df.columns:` or `isinstance()` inside core logic. Schema guarantees belong at the I/O boundary.

### 4.2 Match-Case Over If-Elif Chains

For categorical logic with 3+ branches, use `match...case` instead of `if-elif-else`:

```python
match phenotype_type:
    case "growth":
        return process_growth(data)
    case "morphology":
        return process_morphology(data)
    case "viability":
        return process_viability(data)
    case _:
        logger.warning(f"Unknown phenotype type: {phenotype_type}")
        return None
```

### 4.3 Exception Handling

Wrap `main()` logic in a try-except block and return non-zero on error:

```python
def main() -> int:
    """Main orchestrator function for the script execution."""
    try:
        df_raw = pd.read_csv(config.input_path)
        df_filtered = filter_dataframe(df_raw, config)
        ...
    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return 1
    
    return 0
```

### 4.4 Boundary Validation vs. Trusted Core (Anti-Bloat Rule)

Do NOT scatter defensive checks across core logic functions. Enforce a strict separation between **I/O Boundary** and **Trusted Core**:

1. **At the I/O Boundary (`load_*` or `main()`)**:
   Verify file existence and check required `StrEnum` columns ONCE:
   ```python
   missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
   if missing_cols:
       raise ValueError(f"Missing required columns: {sorted(missing_cols)}")
   ```

2. **Inside `CORE LOGIC` Functions (100% Trusted Zone)**:
   - **Assume valid schema**: Never write `if DataCol.X in df.columns:`, `isinstance()`, or `.get()` fallback logic inside core transformation functions. If inputs violate the contract, let the code fail immediately (Fail-Fast).
   - **Use Guard Clauses sparingly**: Only guard against semantically meaningful data states (e.g., `if df.empty: return df` when an upstream filter might legitimately yield 0 rows), NEVER for schema or type paranoia.
   - **Strict Column Scoping**: Do NOT clean, cast, `.fillna()`, or rename columns that are not directly used in the calculation or explicitly requested by the prompt. Unrelated columns must remain untouched.

---

## 5. Advanced Patterns

### 5.1 Signal-Based Classification

Replace deep `if-elif` chains with a declarative signal table + resolution engine. 

**When to use:** Rule-based text classifiers with 8+ branches where ordering matters and rules can conflict. Examples: phenotype classification, keyword-driven categorization, multi-label tagging.

**Key idea:** Define all rules as data (a list of `Signal` dataclasses), detect all matches independently, then resolve conflicts in post-processing.

→ Full pattern: [references/signal-based-classification.md](references/signal-based-classification.md)

### 5.2 Stem-Prefix Text Classification

For keyword-profile analysis (categorizing every word in a corpus), use exact match + stem-prefix fallback.

**When to use:** Quality inspection, vocabulary analysis, word categorization across semantic groups (growth signals, morphology, modifiers, stop words).

**Key idea:** 
1. Exact match for compound/hyphenated tokens
2. Short canonical stems (≥3 chars) for plurals and inflections
3. Multi-word phrase pre-tokenization (convert "small colonies" → "small-colonies" before splitting)

→ Full pattern: [references/stem-prefix-classification.md](references/stem-prefix-classification.md)

### 5.3 DataFrame Transformation & Reviewability Patterns

Write DataFrame transformations at a granularity that maximizes human review speed — avoid both verbose imperative loops/helpers and cryptic 5-level nested one-liners:

1. **Named Boolean Masks for Filtering & Classification**:
   Break complex conditions into 2–4 named boolean Series with clear domain meaning before combining them:
   ```python
   # ✅ Easy to review: clear domain conditions with explicit names
   is_essential = df[DataCol.FITNESS] < config.essential_cutoff
   is_high_conf = df[DataCol.PVALUE] < config.p_value_threshold
   df_hits = df.loc[is_essential & is_high_conf].copy()
   ```

2. **Idiomatic Vectorized APIs over Custom Helpers**:
   Never write a custom helper function + `.apply(..., axis=1)` or `.iterrows()` when a native pandas/numpy operation exists:
   - **Binary / multi-branch assignment** $\rightarrow$ `np.where()` or `np.select(condlist, choicelist, default=...)`
   - **Binning continuous values** $\rightarrow$ `pd.cut()` or `pd.qcut()`
   - **Lookup / dictionary replacement** $\rightarrow$ `.map(mapping_dict)` or `.replace()`
   - **Group-level statistics broadcast back to rows** $\rightarrow$ `.groupby(col)[val].transform("median")`
   - **Set membership** $\rightarrow$ `.isin(valid_set)`

3. **Readable Step-by-Step Pipelines**:
   Keep each transformation step to 1–3 lines. When chaining more than 3 operations, either assign intermediate DataFrames with descriptive names (`df_valid`, `df_normalized`, `df_summary`) or format `.assign()` / `.pipe()` with one logical column per line. Never pack 4+ operations into an unreadable one-liner.

---

## 6. Common Pitfalls

### 6.1 Layout & Imports (⚠️ Most Frequent)

1. **Using `print()` instead of `logger`.** All output must go through `loguru`. The only exception: piping structured data to stdout for shell consumption (rare).

2. **Adding a new import inside a function body, class definition, or section header instead of the top-level IMPORTS section.** This happens most often when *patching* an existing script — the natural instinct is to add the import next to where the new code goes. Every import must live in the IMPORTS block at file scope. Imports placed elsewhere confuse the section structure, bypass the linting pass, and make the next editor hunt for where a symbol is imported. Fix: before applying a patch that needs a new import, scroll to the IMPORTS block, add it in the correct group (see §1.3 and §1.4 for grouping), then reference it in the body.

3. **Hardcoding workflow paths in imports** (e.g., `from workflow.src.io_table import read_parquet`). This breaks when the script is moved, the project is renamed, or the working directory changes. Use the §1.4 pattern instead: `Path(__file__).parent.resolve()` + relative path to `src/` + `sys.path.append`.

4. **Unused imports left after refactoring.** Imports that were added during development but became unused after the code was refactored are easy to miss — the linter only catches them if a type checker like Pyright or `ruff check` is configured. Before finalising a script, scan the import block and verify every symbol is actually referenced in the body. The checklist below catches this; the pitfall section reminds you to look for it even when no linter is active.

### 6.2 Type System & Configuration

5. **Forgetting `frozen=True` on config dataclasses.** Most configs should be immutable after creation. Only use `frozen=False` if the application genuinely needs hot-reloading.

6. **Using `os.path.join()` / `os.path.exists()` instead of `pathlib.Path`.** The template imports `Path` and uses it throughout. Keep that consistent — `pathlib` is more readable, composable, and less error-prone.

7. **Hardcoded string markers instead of `StrEnum`.** When the script uses column names, operation modes, or categorical statuses that appear in multiple places, define them as a `StrEnum`. This prevents silent breakage when a string changes in one place but not another.

8. **Creating decorators for single-use abstractions.** A decorator with only one consumer adds indirection without benefit. The rule: only create a custom decorator when it eliminates repetitive boilerplate across **3+** functions.

9. **Writing multi-line docstrings with formal Parameters/Returns blocks.** Section 3.1 mandates single-line docstrings — type hints carry the type information. When a core function has complex arguments, the natural instinct is to write NumPy-style or Sphinx-style docstrings with `Parameters\n----------\n...\nReturns\n-------\n...`. This violates the rule. The fix: keep the docstring to one concise line and let the type annotations do the rest. If the function genuinely needs narrative context, put it in a comment block inside the function body rather than in the docstring. This is the most commonly-violated rule because "important" functions feel like they deserve more documentation — resist the urge.

### 6.3 Control Flow & Domain Logic

10. **Not returning exit codes from `main()`.** Shells, CI pipelines, and scripts that check `$?` can detect errors. The template already does this — just remember to return non-zero from `main()` on failure branches.

11. **Deep `if-elif-else` chains for categorical logic.** Two alternatives depending on the problem:

   - **Fixed enum variants** (the category set is known and closed): use
     `match...case` instead of a chain. It's more readable and the type
     checker can help ensure exhaustiveness.

   - **Rule-based classification from free-text** (keywords in a
     description drive the category): use the **signal-based
     classification** pattern instead. See [references/signal-based-classification.md](references/signal-based-classification.md)
     under this skill for the full recipe. Pay special attention to
     **contextual signal suppression** — a keyword within a compound
     phrase (e.g. "spores" in "germinated spores") may not be an
     independent signal.

   - **Keyword‑profile / vocabulary analysis** (counting and categorising
     every word across category groups): use **stem‑prefix matching** —
     short canonical stems with an exact‑match fallback, plus hyphenated
     phrase pre‑tokenisation. See [references/stem-prefix-classification.md](references/stem-prefix-classification.md)
     under this skill.

12. **Forgetting to re-check domain-specific classification logic after expanding keyword lists.** When adding words to modifier or category keyword lists in domain-specific scripts (e.g., bioinformatics phenotype classification), fewer items may be classified as one category and more as another (e.g., Multiple → Single shift). After any expansion, re-run the full pipeline and verify the count deltas are expected and justified. Verify with appropriate summary statistics in the merged output.

13. **Writing defensive schema checks or processing unused columns inside core functions.** AI agents routinely add paranoid checks like `if col in df.columns:`, `if isinstance(val, float):`, or `.fillna("Unknown")` across all columns because training penalties bias them toward avoiding errors at any cost. This bloats code, obscures the actual business logic, and makes human review painful. Fix: validate required columns (`set(REQUIRED_COLUMNS) - set(df.columns)`) once at the I/O boundary (§4.4). Inside core transformation functions, treat the DataFrame as a 100% Trusted Zone and touch ONLY the columns explicitly required for the calculation.

14. **Using `.apply(axis=1)` or `.iterrows()` instead of vectorized pandas/numpy operations.** Defaulting to row-wise iteration or custom helper functions with `.apply(axis=1)` is an AI anti-pattern driven by conversational safety rather than idiomatic Python. It degrades runtime performance by 10x–100x and produces boilerplate helper functions that dilute review clarity. Fix: check the §5.3 lookup table and always use native vectorized operations (`np.where`, `np.select`, `pd.cut`, `.isin`, `.map`, `.groupby().transform()`).

---

## 7. Verification Checklist

- [ ] Sections follow the ordered layout (IMPORTS → DECORATORS → CONSTANTS → CONFIG → LOGGING → CORE → MAIN)
- [ ] Imports grouped: standard library → path setup (if needed) → project imports → data processing → third-party, sorted alphabetically within each group
- [ ] All imports are in the top-level IMPORTS section — none in function bodies, class definitions, or section headers
- [ ] Project module imports use `Path(__file__).resolve().parent` + `sys.path.insert(0, ...)` with `# noqa: E402` (§1.4)
- [ ] No unused imports — every imported module/name is referenced in the script body
- [ ] No `print()` calls — all runtime output uses `loguru`
- [ ] `pathlib.Path` used everywhere (no `os.path`)
- [ ] F-strings for interpolation (no `.format()` or `%`)
- [ ] `@dataclass(kw_only=True, slots=True, frozen=True)` for configuration objects
- [ ] `StrEnum` for grouped string markers, not for singleton constants
- [ ] Fail-Fast Boundary Contract: file existence and required columns validated ONCE at I/O boundary (§4.4)
- [ ] Core logic functions operate as a 100% Trusted Zone: no defensive `if col in df.columns:`, `isinstance()`, or `.get()` fallbacks
- [ ] Strict column scoping: only columns explicitly required by the business logic are processed, transformed, or cleaned
- [ ] Guard clauses used sparingly for semantically valid empty data states, NEVER for schema paranoia
- [ ] Named boolean masks used for compound filtering and multi-criteria classification (§5.3)
- [ ] Native vectorized operations (`np.where`, `np.select`, `pd.cut`, `.map`) used instead of `.apply(axis=1)` or `.iterrows()`
- [ ] Library modules (imported, not run directly) omit LOGGING, CONFIG, MAIN sections — no `parse_args()`, no `main()`, no `setup_logger()`
- [ ] `parse_args()` function + `if __name__ == "__main__": sys.exit(main())` guard
- [ ] Module-level docstring follows the §3.2 format (title → description → Input → Output → Usage → metadata)
- [ ] Change documentation uses three-column table (Problem → Root Cause → Fix) when summarising code modifications
- [ ] Single-line docstrings on functions and classes
- [ ] `@logger.catch` on core logic functions
- [ ] `--verbose` CLI flag for debug-level logging
- [ ] No deep `if-elif-else` chains — use `match...case` for categorical branches
- [ ] Deterministic quality gates pass: `ruff check` (complexity C901 ≤ 8, function limits PLR09), `ruff format --check`, and `ty check`
