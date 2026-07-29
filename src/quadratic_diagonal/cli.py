"""Command-line interface for :mod:`quadratic_diagonal`.

The interface emits JSON so that examples and certificates can be consumed by
shell scripts, notebooks, and independent validation tools without parsing
human-oriented prose.
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Sequence

from .weighted_diagonal_exact import (
    Pair,
    RealQuadraticOrder,
    bounded_truants_batched,
    diagonal_representability_dp,
    diagonal_representability_mitm,
    enumerate_weighted_search,
    verify_representation,
)


def _parse_pair(value: str) -> Pair:
    """Parse a coefficient pair written as ``a,b``.

    Parameters
    ----------
    value : str
        Pair in comma-separated notation.

    Returns
    -------
    tuple[int, int]
        Parsed coefficient pair.

    Raises
    ------
    argparse.ArgumentTypeError
        If the value is not a pair of integers.
    """
    parts = value.split(",")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("Expected a coefficient pair of the form a,b")
    try:
        return (int(parts[0].strip()), int(parts[1].strip()))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Both pair coordinates must be integers") from exc


def _emit(payload: dict[str, Any], compact: bool) -> None:
    """Write a deterministic JSON object to standard output."""
    if compact:
        print(json.dumps(payload, sort_keys=True, separators=(",", ": ")))
    else:
        print(json.dumps(payload, sort_keys=True, indent=2))


def _pair_list(values: Sequence[Pair] | None) -> list[list[int]] | None:
    """Convert a sequence of coefficient pairs to JSON-compatible lists."""
    if values is None:
        return None
    return [[a, b] for a, b in values]


def _build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="quadratic-diagonal",
        description="Exact diagonal representability over maximal real quadratic orders.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    enumerate_parser = subparsers.add_parser(
        "enumerate", help="Enumerate distinct non-zero weighted values below a target."
    )
    enumerate_parser.add_argument("--D", type=int, required=True, help="Squarefree radicand.")
    enumerate_parser.add_argument("--coeff", type=_parse_pair, required=True, help="Coefficient a,b.")
    enumerate_parser.add_argument("--alpha", type=_parse_pair, required=True, help="Target a,b.")
    enumerate_parser.add_argument("--all-roots", action="store_true", help="Return both roots of every value.")
    enumerate_parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")

    represent_parser = subparsers.add_parser(
        "represent", help="Decide and construct diagonal representability."
    )
    represent_parser.add_argument("--D", type=int, required=True, help="Squarefree radicand.")
    represent_parser.add_argument("--alpha", type=_parse_pair, required=True, help="Target a,b.")
    represent_parser.add_argument(
        "--coeff", type=_parse_pair, action="append", required=True,
        help="Diagonal coefficient a,b; repeat once per coefficient.",
    )
    represent_parser.add_argument("--method", choices=("dp", "mitm"), default="dp")
    represent_parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")

    bounded_parser = subparsers.add_parser(
        "bounded-truants", help="Compute all bounded truants for a fixed diagonal lattice."
    )
    bounded_parser.add_argument("--D", type=int, required=True, help="Squarefree radicand.")
    bounded_parser.add_argument(
        "--coeff", type=_parse_pair, action="append", required=True,
        help="Diagonal coefficient a,b; repeat once per coefficient.",
    )
    bounded_parser.add_argument("--trace-bound", type=int, required=True)
    bounded_parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface.

    Parameters
    ----------
    argv : sequence[str] or None, optional
        Arguments excluding the executable name. ``None`` uses ``sys.argv``.

    Returns
    -------
    int
        Process status code. Mathematical non-representability is reported in
        JSON and is not treated as a command failure.
    """
    args = _build_parser().parse_args(argv)
    order = RealQuadraticOrder(args.D)

    if args.command == "enumerate":
        result = enumerate_weighted_search(
            order, args.coeff, args.alpha, return_all_roots=args.all_roots
        )
        payload: dict[str, Any] = {
            "D": args.D,
            "coefficient": list(args.coeff),
            "target": list(args.alpha),
            "distinct_values": result.stats.distinct_values,
            "accepted_roots": result.stats.accepted_roots,
            "trace_candidates": result.stats.trace_candidates,
            "rows_scanned": result.stats.rows_scanned,
            "values": _pair_list(result.values),
        }
        if args.all_roots:
            payload["roots"] = _pair_list(result.roots)
        _emit(payload, args.compact)
        return 0

    if args.command == "represent":
        solver = diagonal_representability_dp if args.method == "dp" else diagonal_representability_mitm
        result = solver(order, args.coeff, args.alpha)
        certified = bool(
            result.represented
            and result.roots is not None
            and verify_representation(order, args.coeff, args.alpha, result.roots)
        )
        payload = {
            "D": args.D,
            "target": list(args.alpha),
            "coefficients": _pair_list(args.coeff),
            "method": args.method,
            "represented": result.represented,
            "certified": certified,
            "roots": _pair_list(result.roots),
            "values": _pair_list(result.values),
            "coefficient_order": list(result.coefficient_order),
            "distinct_value_counts": list(result.distinct_value_counts),
            "state_counts": list(result.state_counts),
            "left_states": result.left_states,
            "right_states": result.right_states,
        }
        _emit(payload, args.compact)
        return 0

    if args.command == "bounded-truants":
        truants = bounded_truants_batched(order, args.coeff, args.trace_bound)
        _emit(
            {
                "D": args.D,
                "coefficients": _pair_list(args.coeff),
                "trace_bound": args.trace_bound,
                "truant_count": len(truants),
                "truants": _pair_list(truants),
            },
            args.compact,
        )
        return 0

    raise RuntimeError("Unreachable command dispatch")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
