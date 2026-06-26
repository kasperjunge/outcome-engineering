#!/usr/bin/env python3
"""Compatibility wrapper for creating the example product graph."""

from __future__ import annotations

import argparse
from pathlib import Path

from outcome_engineering.example import create_example


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("examples/delegation-product-graph"),
        help="Directory to create. Defaults to examples/delegation-product-graph.",
    )
    parser.add_argument("--force", action="store_true", help="Replace the output directory if it already exists.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    create_example(args.output, args.force)
    print(f"Created example product graph at {args.output}")


if __name__ == "__main__":
    main()
