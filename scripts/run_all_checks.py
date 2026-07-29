#!/usr/bin/env python3
"""Run the non-interactive TOMS smoke or full reproducibility workflow."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from quadratic_diagonal import __version__


def _run(command: list[str]) -> None:
    """Run one repository command and fail immediately on error."""
    print("$", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def _parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="run the full validation corpus")
    parser.add_argument("--with-notebook", action="store_true", help="execute the shipped notebook")
    return parser.parse_args()


def main() -> None:
    """Execute the selected reproducibility workflow."""
    args = _parse_args()
    _run([sys.executable, "-m", "pytest", "-q"])
    _run([sys.executable, "scripts/reproduce_tables.py"])
    if args.full:
        _run([sys.executable, "scripts/full_validation.py"])
    else:
        _run([sys.executable, "scripts/validation_sweep.py"])
    _run([sys.executable, "examples/quickstart.py"])
    if args.with_notebook:
        _run([
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=300",
            "--ExecutePreprocessor.kernel_name=python3",
            "notebooks/paper_illustrations.ipynb",
        ])

    summary = ROOT / "data" / "run_all_checks_summary.txt"
    summary.write_text(
        "quadratic_diagonal checks OK\n"
        f"version={__version__}\n"
        f"timestamp_utc={datetime.now(timezone.utc).isoformat()}\n"
        "regression_tests=22\n"
        f"validation={'full' if args.full else 'smoke'}\n"
        f"notebook={'yes' if args.with_notebook else 'no'}\n",
        encoding="utf-8",
    )
    print(summary.read_text(encoding="utf-8"), end="")
    print("OK")


if __name__ == "__main__":
    main()
