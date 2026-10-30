#!/usr/bin/env python3

# =============================================================================
# CHECKLIST BEFORE FINALIZING (delete this block when done):
# - [ ] Replace the module docstring: title, description, Input, Output, Usage
# - [ ] Resolve every `REPLACE THIS` marker below
# - [ ] Update REQUIRED_COLUMNS / DataCol to match the real input
# - [ ] Validate schema once at I/O boundary (Fail-Fast)
# - [ ] Implement core logic without defensive schema checks (Trusted Zone)
# - [ ] Use named boolean masks and vectorized methods (np.where, np.select)
# - [ ] Update parse_args() with the actual CLI parameters
# - [ ] Verify every import is used, and that none sit inside a function body
# - [ ] Walk the full checklist in the skill's SKILL.md section 7
# =============================================================================

# (Optional) PEP 723 inline script metadata for self-contained execution with `uv`.
# Remove or adjust if managing dependencies via a traditional virtual environment.
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pandas",
#     "loguru",
# ]
# ///

"""
Script Template for Data Processing                    # REPLACE THIS: One-line title
===================================================

A template script that demonstrates the standard layout for AI-generated
Python scripts in this workspace. Replace this description with the
script's actual business logic, core algorithm, and context.
                                                        # REPLACE THIS: Full description

Input
-----
- Input file path (CSV, TSV, or XLSX) with required columns.
- See ``--input`` / ``--help`` for exact format.      # REPLACE THIS: Actual input spec

Output
------
- Filtered results saved to the configured output directory.
- File format depends on the script's core logic.     # REPLACE THIS: Actual output spec

Usage
-----
    mamba run -n bioinformatics python script_template.py \
        --input data/raw/file.csv \
        --output-dir outputs/ \
        --keywords growth morphology \
        --verbose                                      # REPLACE THIS: Real usage examples

Author: Yusheng Yang (guidance) + Agent (implementation)  # REPLACE THIS: Actual author
Date:   YYYY-MM-DD                                     # REPLACE THIS: Today's date
Version: 1.0.0
"""

# ==================== §1 IMPORTS ====================
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

# ==================== §2 TYPE HINTS & DECORATORS ====================
# (Optional) Custom type aliases and decorators used throughout the script

# ==================== §3 CONSTANTS ====================
# Module-level constants: filenames, magic numbers, defaults, etc.
DEFAULT_OUTPUT_DIR = Path("outputs")


class DataCol(StrEnum):
    """Dataset column name constants."""

    GENE_ID = "gene_id"
    DESCRIPTION = "description"
    CATEGORY = "category"
    STATUS = "status"


# Columns required at the I/O boundary
REQUIRED_COLUMNS = [DataCol.GENE_ID, DataCol.DESCRIPTION, DataCol.CATEGORY]

# ==================== §4 CONFIG ====================


@dataclass(kw_only=True, slots=True, frozen=True)
class Config:
    """Immutable configuration container for script execution."""

    input_path: Path
    output_dir: Path
    keywords: list[str]
    verbose: bool = False
    # kw_only=True → forces keyword arguments (prevents positional confusion)
    # slots=True → reduces memory footprint (no __dict__ per instance)
    # frozen=True → makes instances immutable (config shouldn't change after creation)


# ==================== §5 LOGGING ====================


def setup_logger(verbose: bool) -> None:
    """Configure loguru for this script's needs."""
    logger.remove()  # Clear default handler
    level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:<8}</level> | {message}",
    )


# ==================== §6 CORE LOGIC ====================


@logger.catch
def filter_dataframe(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    """Filter DataFrame using named boolean masks and vectorized assignment."""
    # Guard clause: legitimate semantic state (empty data), NEVER for schema paranoia
    if df.empty:
        logger.warning("Input DataFrame is empty; returning empty result.")
        return df

    # REPLACE THIS: Implement domain logic in Trusted Zone (assumes columns are valid)
    if not config.keywords:
        logger.info("No keywords provided; returning all rows.")
        return df

    # Named boolean mask: break conditions into clear domain Series
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


# ==================== §7 MAIN EXECUTION ====================


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process data and filter by keywords.",  # REPLACE THIS: Your actual description
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to input CSV/TSV/XLSX file.",
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
    """Main execution flow orchestrating boundary validation and processing."""
    args = parse_args()
    setup_logger(args.verbose)

    # Build config from CLI args
    config = Config(
        input_path=args.input,
        output_dir=args.output_dir,
        keywords=args.keywords,
        verbose=args.verbose,
    )

    # Prepare output directory
    config.output_dir.mkdir(parents=True, exist_ok=True)

    # Execute core logic
    logger.info(f"Starting processing for file: {config.input_path}")
    try:
        df_raw = pd.read_csv(config.input_path)

        # Boundary Validation (Fail-Fast: validate required columns ONCE at I/O boundary)
        missing_cols = set(REQUIRED_COLUMNS) - set(df_raw.columns)
        if missing_cols:
            logger.error(f"Missing required columns in {config.input_path}: {sorted(missing_cols)}")
            return 1

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
