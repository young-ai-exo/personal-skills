---
name: python-script-conventions
description: Use when generating, modifying, or reviewing Python scripts (3.12+). Enforces Functional Core / Imperative Shell architecture, fail-fast boundary validation, trusted core execution (anti-bloat), native pandas/numpy vectorized idioms, and deterministic quality gates (Ruff + ty). Load whenever creating or editing a .py file — especially for data processing and scientific workflows.
version: 2.0.0
---

# Python Script Conventions: Architecture, Anti-Bloat & Reviewability (Python 3.12+)

## 1. Core Philosophy: The Reviewability Sweet Spot

In agentic software engineering, generating code is fast, but human code review and long-term maintenance impose a heavy cognitive tax. AI models naturally drift toward two review-taxing extremes:

1. **Defensive Bloat (Paranoid Over-Engineering)**: Driven by reinforcement learning penalties for runtime errors, models pepper core logic with redundant `if col in df.columns`, defensive `isinstance()` checks, speculative `.fillna()` fallbacks on unused columns, and clumsy row-wise `.apply(axis=1)` helpers. This dilutes the signal-to-noise ratio and turns Code Review into an exhausting audit of defensive scaffolding.
2. **Cryptic Code-Golf (Dense One-Liners)**: Cramming 4+ transformation steps into deeply nested Pandas chains forces the reviewer to mentally simulate intermediate DataFrame shapes, column names, and indices.

```
       [ ❌ Defensive Bloat ]                 [ ✅ Reviewability Sweet Spot ]                 [ ❌ Cryptic Code-Golf ]
  50 lines of paranoid checks,          High signal-to-noise ratio, declarative          5 nested chained operations,
  row-wise loops, unused column         step-by-step logic, trusted pure core,           no intermediate names,
  cleaning, and repetitive try-except.  fail-fast I/O boundary, native vectorization.    impossible to debug or inspect.
```

**The Reviewability Sweet Spot** demands **Declarative Step-by-Step Code**:
- **Predictable Macro-Architecture**: A standard two-layer model separating the I/O Shell from the Pure Core.
- **Fail-Fast Boundary Contract**: Inputs and schemas are verified once at the threshold. Core computation is a 100% Trusted Zone.
- **Moderate Transformation Granularity**: Each logical transformation takes 1–3 readable lines using descriptive intermediate names or named boolean masks.
- **Shared Infrastructure & Reusable Decorators**: Cross-cutting concerns (logging, timing, exception handling) are extracted to shared utilities and clean decorators rather than duplicated across scripts.

---

## 2. Hard Rules & Quality Gate Contract

These rules are non-negotiable. Every rule directly maps to a deterministic linting or type-checking threshold configured in `$SKILL_DIR/templates/pyproject.toml`.

### 2.1 The Non-Negotiable Hard Rules

1. **All Imports at File Scope (Top-Level)**: Never place `import` statements inside functions, classes, or control flow branches.
2. **Deterministic Project Path Setup**: For standalone scripts needing modules from `src/`, resolve the path dynamically via `Path(__file__).resolve().parent` and use `sys.path.insert(0, ...)` with an idempotency guard.
3. **Fail-Fast Boundary Contract**: Validate file paths and required DataFrame columns (`StrEnum`) ONCE at the I/O boundary (`load_*` or `main()`). Core functions must never perform speculative column existence checks (`if col in df.columns:`) or defensive `.get()` fallbacks.
4. **Strict Column Scoping**: Touch, validate, cast, or transform ONLY the DataFrame columns explicitly required by the business logic. Leave all unrelated columns completely untouched.
5. **Native Vectorized Idioms**: Prefer built-in `pandas` and `numpy` vectorized operations (`np.where`, `np.select`, `pd.cut`, `.isin`, `.map`, `.groupby().transform()`) over custom row-wise helpers, `.apply(axis=1)`, or Python row loops (`.iterrows()`).
6. **Exclusive Logging via Loguru**: Never use `print()` or standard library `logging`.
7. **Type Hints on All Function Signatures**: Annotate all arguments and explicit return types (`-> None` for side-effect procedures).
8. **Single-Line Function Docstrings**: Let type hints document parameter types. Keep function docstrings to a concise, high-signal single line describing the business intent.
9. **`pathlib.Path` Everywhere**: Never use `os.path` functions or manual string concatenation for filesystem paths.
10. **Immutable Configuration Objects**: Use `@dataclass(kw_only=True, frozen=True)` for runtime configuration. Leave `slots=False` (default) to avoid unnecessary inheritance friction and mocking issues.
11. **Proper Exit Code Propagation**: All CLI entry points must terminate via `if __name__ == "__main__": sys.exit(main())`, where `main() -> int` returns `0` on success and non-zero on failure.

---

### 2.2 Deterministic Quality Gate Mapping

Do not guess whether code is clean; let deterministic tools enforce compliance before code is submitted for human review:

| Design Dimension | Enforced Convention | `pyproject.toml` Rule / Gate | Enforcement Behavior & AI Remediation |
| :--- | :--- | :--- | :--- |
| **Complexity Ceiling** | Ban nested defensive branching & pyramids | `C901` (`max-complexity = 8`) | Ruff rejects functions with >8 execution paths. AI must flatten logic into vectorized expressions. |
| **Function Volume** | Ban monolithic multi-responsibility scripts | `PLR09` (`max-args = 20`, `max-branches = 10`, `max-returns = 4`, `max-statements = 40`) | Excess branches or returns fail linting. Forces bundling parameters into `Config` and using lookup tables. |
| **Architecture Boundaries** | Enforce file-scope imports only | `PLC0415` (`import-outside-top-level`) | Rejects imports hidden inside function bodies. |
| **API Bans** | Strict ban on `print`, `logging`, and `os.path` | `T201` (`print`), `PTH` (`pathlib`), `TID251` (`banned-api`) | Rejects deprecated APIs with explicit instructions (e.g., use `loguru.logger`, use `pathlib.Path`). |
| **Modern Syntax** | Modern Python 3.12+ syntax standards | `UP` (`pyupgrade`), `B` (`flake8-bugbear`) | Rejects legacy `Optional[T]` / `Union[X, Y]` in favor of `T \| None` and `X \| Y`; flags mutable default args. |
| **Type Integrity** | Guarantee typed contracts and catch cast bloat | `ANN` (`annotations`), `ty check` | Fails on missing signatures or type mismatches. Flags unnecessary defensive `typing.cast()` calls. |

---

## 3. Macro-Architecture: Functional Core, Imperative Shell (FC/IS)

Instead of rigid comment banners, organize all scripts according to the **Functional Core, Imperative Shell (FC/IS)** architecture. This unifies standalone CLI scripts and reusable modules into a single, elegant mental model.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. IMPERATIVE SHELL (Outer Boundary)                                        │
│    - CLI argument parsing (parse_args)                                      │
│    - Environment & configuration setup (AppConfig)                          │
│    - I/O: Reading raw files & Fail-Fast Schema Validation (set difference)  │
│    - Writing output artifacts & Exit Code Propagation                       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Validated Data & Config
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. FUNCTIONAL CORE (Inner Trusted Zone)                                     │
│    - Pure data transformation functions (DataFrame -> DataFrame)            │
│    - Zero filesystem I/O, zero CLI arguments, zero sys.argv                 │
│    - 100% Trusted: Zero speculative schema checks or fallback cleaning      │
│    - Declarative step-by-step pipelines with Named Boolean Masks            │
│    - Natively importable by other scripts and testable via pytest           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Standalone Script vs. Reusable Module
* **Standalone Script**: Contains both the **Functional Core** (pure data transformation functions) and the **Imperative Shell** (`parse_args()`, boundary validation, and `main()`).
* **Library / Utility Module**: Contains only the **Functional Core** and shared constants. It omits CLI parsing, logging setup, and `if __name__ == "__main__"`. Any function in a standalone script's core is inherently designed to be extracted into a library module without modifying its logic.

### 3.2 Standard Script Section Layout

Maintain a predictable top-to-bottom dependency hierarchy:

```python
# 1. IMPORTS (Standard library -> Third-party -> Local project)
import argparse
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from loguru import logger

# 2. CONSTANTS & ENUMS (Domain markers, column name definitions)
class DataCol(StrEnum):
    GENE_ID = "gene_id"
    PVALUE = "p_value"
    LOG2FC = "log2fc"
    STATUS = "status"

REQUIRED_COLUMNS = [DataCol.GENE_ID, DataCol.PVALUE, DataCol.LOG2FC]

# 3. CONFIGURATION (Immutable parameter container)
@dataclass(kw_only=True, frozen=True)
class AppConfig:
    """Immutable runtime configuration container."""
    input_path: Path
    output_dir: Path
    p_value_threshold: float = 0.05
    log2fc_cutoff: float = 1.0

# 4. FUNCTIONAL CORE (Pure, trusted transformation functions)
def annotate_hits(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    """Annotate significant hits using named boolean masks and vectorized assignment."""
    if df.empty:
        return df

    is_sig = df[DataCol.PVALUE] < config.p_value_threshold
    is_strong = df[DataCol.LOG2FC].abs() >= config.log2fc_cutoff

    return df.assign(
        **{DataCol.STATUS: np.where(is_sig & is_strong, "hit", "non_hit")}
    )

# 5. IMPERATIVE SHELL (Boundary validation, I/O orchestration, CLI entry point)
def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Process bioinformatics hits.")
    parser.add_argument("--input", type=Path, required=True, help="Input CSV path.")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Output directory.")
    return parser.parse_args()

def main() -> int:
    """Orchestrate I/O boundary, validate schema, and execute functional core."""
    args = parse_args()
    config = AppConfig(input_path=args.input.resolve(), output_dir=args.output_dir.resolve())
    config.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        df_raw = pd.read_csv(config.input_path)

        # Fail-Fast Boundary Contract: validate schema ONCE at entry
        missing_cols = set(REQUIRED_COLUMNS) - set(df_raw.columns)
        if missing_cols:
            logger.error(f"Missing required columns in {config.input_path}: {sorted(missing_cols)}")
            return 1

        # Execute Trusted Functional Core
        df_processed = annotate_hits(df_raw, config)

        out_path = config.output_dir / "annotated_results.csv"
        df_processed.to_csv(out_path, index=False)
        logger.info(f"Results successfully saved to {out_path} ({len(df_processed):,} rows)")
        return 0
    except Exception as e:
        logger.exception(f"Fatal execution error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 4. Shared Infrastructure & Reusable Decorators

Do not copy-paste 15 lines of boilerplate logging setup, execution timers, or exception handling across multiple scripts. Extract cross-cutting concerns into modular utilities under `src/utils/`.

### 4.1 Shared Logging Infrastructure (`src/utils/logging.py`)

In projects with a shared `src/` directory, centralize logging configuration rather than defining bespoke loggers in each script:

```python
# src/utils/logging.py
import sys
from loguru import logger

def setup_logger(verbose: bool = False) -> None:
    """Configure unified Loguru output format across all workflow scripts."""
    logger.remove()
    log_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
    )
```

Standalone scripts simply import and call:
```python
from utils.logging import setup_logger
```

### 4.2 Reusable Decorators (`src/utils/decorators.py`)

When repetitive cross-cutting patterns appear across 3+ functions or scripts (e.g., performance timing, automatic retry, standardized boundary exception logging), encapsulate them in clean, type-preserving decorators.

```python
# src/utils/decorators.py
from collections.abc import Callable
import functools
import time
from typing import Any, ParamSpec, TypeVar
from loguru import logger

P = ParamSpec("P")
R = TypeVar("R")

def timeit(func: Callable[P, R]) -> Callable[P, R]:
    """Log the wall-clock execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start_time
        logger.debug(f"{func.__name__} executed in {duration:.3f}s")
        return result
    return wrapper
```

**Decorator Rules of Engagement**:
1. **Always use `functools.wraps`**: Preserves function names, signatures, and docstrings for type checkers and linters.
2. **Preserve Type Signatures**: Use `ParamSpec` and `TypeVar` so static checkers (`ty`, `mypy`) do not lose parameter hints.
3. **No Single-Use Abstractions**: Never create a custom decorator for a single function. Use decorators only when encapsulating shared infrastructure across multiple modules.

---

## 5. Architectural Contract: Boundary Validation vs. Trusted Core

The single most effective weapon against AI code bloat is the strict separation between the **I/O Boundary** and the **Trusted Core**.

### 5.1 The Fail-Fast Boundary Contract (I/O Shell)
At the outer boundary (`main()` or dedicated `load_*` functions), assume external input is untrusted and messy. Verify paths, formats, and required columns ONCE:

```python
# ✅ Validate once at entry using set difference
missing_cols = set(REQUIRED_COLUMNS) - set(df_raw.columns)
if missing_cols:
    logger.error(f"Missing required columns in {input_path}: {sorted(missing_cols)}")
    return 1
```

### 5.2 The 100% Trusted Core Execution Zone
Once data passes the boundary validation, core transformation functions treat the DataFrame as a **100% Trusted Zone**:
* **Assume Valid Schema**: NEVER write `if col in df.columns:`, `if isinstance(...)`, or `.get()` fallbacks inside core transformation functions.
* **Strict Column Scoping**: NEVER clean, fill, cast, or rename columns not required by the requested calculation. Leave unmentioned columns untouched.
* **Fail Fast**: If unexpected nulls or invalid types occur in trusted core calculations, let the code fail immediately so the root cause is exposed.

### 5.3 Semantic Guard Clauses vs. Schema Paranoia

```python
# ❌ BAD: Paranoid defensive checking inside core logic (AI Bloat)
def calculate_enrichment(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    """Calculate enrichment scores."""
    if df is None or df.empty:
        return pd.DataFrame()
    # Paranoid checks that pollute review
    if "p_value" not in df.columns:
        raise ValueError("Missing p_value")
    for col in ["notes", "extra_info"]:  # Unrelated column cleaning!
        if col in df.columns:
            df[col] = df[col].fillna("N/A")
    ...

# ✅ GOOD: Trusted Core logic (High-signal & clean)
def calculate_enrichment(df: pd.DataFrame, config: AppConfig) -> pd.DataFrame:
    """Calculate enrichment scores."""
    # Guard clause permitted ONLY for legitimate semantic data states (e.g. 0 rows from filter)
    if df.empty:
        return df

    # Core logic immediately operates on validated columns
    is_valid = df[DataCol.PVALUE] < config.p_value_threshold
    return df.loc[is_valid].copy()
```

---

## 6. Micro-Implementation: Declarative Dataflow & Pandas Idioms

Reviewable data transformation code tells a clear scientific story. Follow these guidelines to maintain optimal review granularity.

### 6.1 Named Boolean Masks for Complex Conditions
Do not bury multiple conditional expressions in a single unreadable line. Assign each distinct domain condition to a self-documenting boolean Series:

```python
# ❌ Hard to review: dense inline conditions
df_hits = df.loc[(df["p_val"] < 0.05) & (df["fc"].abs() >= 1.5) & (df["count"] > 10)].copy()

# ✅ Easy to review: named domain conditions
is_significant = df[DataCol.PVALUE] < config.p_value_threshold
has_strong_effect = df[DataCol.LOG2FC].abs() >= config.log2fc_cutoff
has_sufficient_coverage = df[DataCol.READ_COUNT] >= config.min_read_count

df_hits = df.loc[is_significant & has_strong_effect & has_sufficient_coverage].copy()
```

### 6.2 Idiomatic Vectorized Operators vs. Row-Wise Helpers

Never write custom row-wise iteration functions combined with `.apply(axis=1)` or `.iterrows()`. Use native vectorized alternatives:

| Transformation Pattern | ❌ Prohibited Anti-Pattern | ✅ Idiomatic Vectorized Operator |
| :--- | :--- | :--- |
| **Binary Classification** | `def _check(row): ...`<br/>`df.apply(_check, axis=1)` | `np.where(condition, "hit", "non_hit")` |
| **Multi-Condition Branching** | Long `if-elif-else` helper with `.apply(axis=1)` | `np.select(condlist, choicelist, default="other")` |
| **Continuous Binning** | Custom conditional function checking ranges | `pd.cut(df[col], bins=[...], labels=[...])` |
| **Value / Dictionary Mapping** | Iterating over rows to translate keys | `df[col].map(mapping_dict)` or `.replace()` |
| **Groupwise Broadcast** | Iterating over groups to attach aggregate values | `df.groupby("group")["val"].transform("median")` |
| **Set Membership** | `df[col].apply(lambda x: x in valid_set)` | `df[col].isin(valid_set)` |

### 6.3 Declarative Step-by-Step Pipelines
Keep each step to 1–3 lines. When chaining operations, format multi-line `.assign()` blocks cleanly (leveraging Ruff's trailing comma convention) or assign intermediate DataFrames with descriptive domain names:

```python
# ✅ Highly reviewable: formatted .assign() with one logical transformation per line
df_annotated = (
    df_raw
    .loc[is_quality_pass]
    .assign(
        **{
            DataCol.NORM_COUNT: lambda d: d[DataCol.RAW_COUNT] / d[DataCol.TOTAL_READS] * 1e6,
            DataCol.STATUS: np.where(is_sig_effect, "enriched", "depleted"),
        }
    )
)
```

---

## 7. Hygiene & Modern Infrastructure

### 7.1 Deterministic Dynamic Path Resolution
When a script lives in `scripts/` or a subfolder and needs to import from `src/`, configure paths dynamically without relying on the current working directory:

```python
# Standard Library
from pathlib import Path
import sys

# Project path setup (must precede local project imports)
SCRIPT_DIR = Path(__file__).resolve().parent
SRC_DIR = SCRIPT_DIR.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Local project imports
from utils.logging import setup_logger  # noqa: E402
```

### 7.2 Immutable Configurations with Standard Dataclasses
Use `@dataclass(kw_only=True, frozen=True)`. Do NOT set `slots=True` by default:

```python
@dataclass(kw_only=True, frozen=True)
class AppConfig:
    """Runtime configuration container."""
    input_path: Path
    output_dir: Path
    min_reads: int = 10
```

### 7.3 Concise Single-Line Docstrings
Because every function signature must carry comprehensive type hints, do not duplicate type information in verbose multi-line Sphinx/NumPy docstring blocks:

```python
# ❌ BAD: Redundant multi-line docstring repeating type annotations
def compute_metrics(df: pd.DataFrame, cutoff: float) -> pd.DataFrame:
    """
    Compute QC metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.
    cutoff : float
        Filtering cutoff.

    Returns
    -------
    pd.DataFrame
        Filtered metrics.
    """
    ...

# ✅ GOOD: High-signal, single-line docstring
def compute_metrics(df: pd.DataFrame, cutoff: float) -> pd.DataFrame:
    """Compute QC metrics and filter records exceeding the error cutoff."""
    ...
```

---

## 8. Anti-Patterns Catalog & Verification Checklist

### 8.1 Common Anti-Patterns vs. Recommended Practices

| Anti-Pattern (What to Avoid) | Root Cause / AI Bias | Recommended Practice |
| :--- | :--- | :--- |
| **Defensive checking in core functions** (`if col in df:`) | AI fear of runtime exceptions | Move all schema checks to I/O entry point (`set(cols) - set(df.columns)`). Keep core functions 100% trusted. |
| **Speculative column cleaning** (`df.fillna()` on unused cols) | AI assumes all columns are dirty | Touch, validate, and transform ONLY columns required for the requested calculation. |
| **Row-wise helpers with `.apply(axis=1)`** | AI defaults to conversational loop logic | Use `np.where()`, `np.select()`, or `.map()`. |
| **Nested `if-else` cascades (Cyclomatic Complexity > 8)** | AI stacks condition on condition | Break into named boolean masks or declarative signal mapping tables. |
| **Local imports inside functions** | Lazy patching without inspecting file top | All imports must reside in the top-level IMPORTS section (`PLC0415`). |
| **Monolithic functions (>40 statements)** | Dumping all workflow logic into one block | Separate Imperative Shell (`main()`) from Functional Core (`df -> df`). |

---

### 8.2 Pre-Flight Verification Checklist

Before finalizing any script or submitting code for human review, verify each item:

- [ ] **Architecture**: Separation of Imperative Shell (I/O, CLI, validation) and Functional Core (pure data transformations).
- [ ] **Boundary Contract**: Input file existence and required `StrEnum` columns validated ONCE at I/O entry via set difference.
- [ ] **Trusted Core**: Zero defensive `if col in df.columns:`, `isinstance()`, or `.get()` checks inside core logic functions.
- [ ] **Strict Scoping**: Unused columns left completely untouched; no speculative `.fillna()` on unrequested columns.
- [ ] **Vectorization**: Zero `.apply(axis=1)`, `.iterrows()`, or Python row loops; native vectorized operators used throughout.
- [ ] **Named Masks**: Compound filtering conditions broken into 2–4 domain-named boolean Series.
- [ ] **Imports & Pathing**: All imports at file top; project imports use `Path(__file__).resolve().parent` + `sys.path.insert(0, ...)`.
- [ ] **Logging & Output**: `loguru.logger` used exclusively; no `print()` or stdlib `logging`.
- [ ] **Configuration**: Runtime config encapsulated in `@dataclass(kw_only=True, frozen=True)` (default `slots=False`).
- [ ] **Docstrings**: Single-line docstrings on all functions and classes; comprehensive module-level docstring at top.
- [ ] **Deterministic Quality Gates**:
  - [ ] `ruff check` passes with 0 errors (including `C901` complexity ≤ 8, `PLR09` size limits, `PLC0415`, `TID251`).
  - [ ] `ruff format --check` reports zero formatting diffs.
  - [ ] `ty check` passes with zero type errors and zero redundant casts.

---

### 8.3 Domain References & Companion Assets

- **Reference Script Implementation**: `$SKILL_DIR/templates/agent_script_template.py` (concrete reference demonstrating all conventions).
- **Quality Gate Specification**: `$SKILL_DIR/templates/pyproject.toml` (deterministic Ruff and ty configuration).
- **Rule-Based Signal Classification**: [`references/signal-based-classification.md`](references/signal-based-classification.md) (declarative signal table pattern for text/phenotype categorization with 8+ conflicting branches).
- **Stem-Prefix Vocabulary Matching**: [`references/stem-prefix-classification.md`](references/stem-prefix-classification.md) (exact-match + stem fallback for corpus word profiling).
- **Module-Level Docstrings**: [`references/module-level-docstring.md`](references/module-level-docstring.md) (real-world bioinformatics script docstring examples).
