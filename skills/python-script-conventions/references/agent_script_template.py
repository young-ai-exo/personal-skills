#!/usr/bin/env python3

# =============================================================================
# CHECKLIST BEFORE FINALIZING (delete this block when done):
# - [ ] Replace module docstring: title, description, Input, Output, Usage
# - [ ] Resolve every `REPLACE THIS` marker below
# - [ ] Update DataCol / REQUIRED_COLUMNS to match actual dataset schema
# - [ ] Validate schema once at I/O boundary in main() (Fail-Fast)
# - [ ] Implement core logic without defensive schema checks (Trusted Zone)
# - [ ] Use named boolean masks and native vectorized methods (np.where, np.select)
# - [ ] Update parse_args() with actual CLI parameters
# - [ ] Verify every import is used, and that none sit inside function bodies
# - [ ] Verify ruff check, ruff format --check, and ty check pass cleanly
# =============================================================================

"""
Script Template for Data Processing                    # REPLACE THIS: One-line title
===================================================

A template script demonstrating the Functional Core, Imperative Shell (FC/IS)
architecture for AI-assisted Python scripts in this workspace. Replace this
description with the script's actual analytical logic, core algorithm, and context.
                                                        # REPLACE THIS: Full description

Input
-----
- Input file path (CSV, TSV, or Parquet) with required columns.
- See ``--input`` / ``--help`` for exact format.      # REPLACE THIS: Actual input spec

Output
------
- Filtered results and audit summaries saved to configured output directory.
- File format depends on the script's core logic.     # REPLACE THIS: Actual output spec

Usage
-----
    python script_template.py \
        --input data/raw/file.csv \
        --output-dir outputs/ \
        --keywords growth morphology \
        --verbose                                      # REPLACE THIS: Real usage examples

Author: Yusheng Yang (guidance) + Agent (implementation)  # REPLACE THIS: Actual author
Date:   YYYY-MM-DD                                     # REPLACE THIS: Today's date
Version: 1.0.0
"""

# =============================================================================
# 1. IMPORTS (Standard Library -> Third-Party -> Local Project)
# =============================================================================
# Standard library
import argparse
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
import sys

# Third-party (alphabetical)
from loguru import logger

# Data manipulation / numerical (alphabetical)
import numpy as np
import pandas as pd

# (Optional) Dynamic project path setup when importing from src/ in a subfolder:
# SCRIPT_DIR = Path(__file__).resolve().parent
# SRC_DIR = SCRIPT_DIR.parent / "src"
# if str(SRC_DIR) not in sys.path:
#     sys.path.insert(0, str(SRC_DIR))
# from utils.logging import setup_logger

# =============================================================================
# 2. CONSTANTS & ENUMS (Domain Markers & Column Definitions)
# =============================================================================
DEFAULT_OUTPUT_DIR = Path("outputs")


class DataCol(StrEnum):
    """Dataset column name constants."""

    GENE_ID = "gene_id"
    DESCRIPTION = "description"
    CATEGORY = "category"
    STATUS = "status"


# Columns required at the I/O boundary (validated once at entry)
REQUIRED_COLUMNS = [DataCol.GENE_ID, DataCol.DESCRIPTION, DataCol.CATEGORY]

# =============================================================================
# 3. CONFIGURATION (Immutable Runtime Parameters)
# =============================================================================


@dataclass(kw_only=True, frozen=True)
class Config:
    """Immutable runtime configuration container (default slots=False)."""

    input_path: Path
    output_dir: Path
    keywords: list[str]
    verbose: bool = False
    # kw_only=True → forces keyword arguments (prevents positional confusion)
    # frozen=True  → makes instances immutable (configuration shouldn't change at runtime)


# =============================================================================
# 4. FUNCTIONAL CORE (Pure, Trusted Transformations)
# =============================================================================


@logger.catch
def filter_dataframe(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Filter DataFrame using named boolean masks and vectorized assignment."""
    # Semantic Guard Clause: legitimate empty data state, NEVER for schema paranoia
    if df.empty:
        logger.warning("Input DataFrame is empty; returning empty result.")
        return df

    # REPLACE THIS: Implement domain logic in Trusted Zone (assumes schema is validated)
    if not config.keywords:
        logger.info("No keywords provided; returning all rows.")
        return df

    # Named boolean mask: break compound criteria into self-documenting Series
    keyword_pattern = "|".join(config.keywords)
    has_keyword = df[DataCol.DESCRIPTION].str.contains(keyword_pattern, case=False, na=False)

    # Idiomatic vectorized filter & assignment (no .apply(axis=1) or row loops)
    result = df.loc[has_keyword].copy()
    result = result.assign(
        **{DataCol.STATUS: np.where(has_keyword.loc[result.index], "matched", "unmatched")}
    )

    logger.info(
        f"Filtered {len(df):,} rows down to {len(result):,} matching keywords: {config.keywords}"
    )
    return result


# =============================================================================
# 5. IMPERATIVE SHELL (Boundary Validation, I/O & CLI Entry Point)
# =============================================================================


def setup_logger(verbose: bool) -> None:
    """Configure Loguru output formatting for standalone execution."""
    # In shared multi-script projects, prefer: from utils.logging import setup_logger
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process data and filter by keywords.",  # REPLACE THIS: Real description
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to input CSV/TSV/Parquet file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for results (default: {DEFAULT_OUTPUT_DIR})",
    )
    # REPLACE THIS: Your CLI params
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=[],
        help="Keywords to filter descriptions (e.g., 'growth', 'morphology')",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug-level logging.",
    )
    return parser.parse_args()


def main() -> int:
    """Main execution flow orchestrating boundary validation and core execution."""
    args = parse_args()
    setup_logger(args.verbose)

    # Build immutable configuration from CLI arguments
    config = Config(
        input_path=args.input.resolve(),
        output_dir=args.output_dir.resolve(),
        keywords=args.keywords,
        verbose=args.verbose,
    )

    # Prepare output directory
    config.output_dir.mkdir(parents=True, exist_ok=True)

    # Execute workflow within the Imperative Shell
    logger.info(f"Starting processing for file: {config.input_path}")
    try:
        df_raw = pd.read_csv(config.input_path)

        # Fail-Fast Boundary Contract: validate schema ONCE at I/O entry
        missing_cols = set(REQUIRED_COLUMNS) - set(df_raw.columns)
        if missing_cols:
            logger.error(f"Missing required columns in {config.input_path}: {sorted(missing_cols)}")
            return 1

        # Hand over to 100% Trusted Functional Core
        df_filtered = filter_dataframe(df_raw, config)

        out_file = config.output_dir / "filtered_results.csv"
        df_filtered.to_csv(out_file, index=False)
        logger.info(f"Results successfully saved to {out_file} ({len(df_filtered):,} rows)")

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
