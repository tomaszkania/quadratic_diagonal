#!/usr/bin/env python3
"""Run the full independent validation corpus reported in the paper."""

from __future__ import annotations

import json
import math
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from quadratic_diagonal import (
    RealQuadraticOrder,
    bounded_truants_batched,
    bounded_truants_naive,
    diagonal_representability_dp,
    diagonal_representability_mitm,
    enumerate_totally_positive_targets,
    enumerate_weighted_search,
    enumerate_weighted_search_box,
    verify_representation,
)

Pair = tuple[int, int]


def _squarefree_fields(max_D: int) -> list[int]:
    """Return all squarefree nonsquare radicands up to ``max_D``."""
    fields: list[int] = []
    for D in range(2, max_D + 1):
        if math.isqrt(D) ** 2 == D:
            continue
        if all(D % (p * p) for p in range(2, math.isqrt(D) + 1)):
            fields.append(D)
    return fields


def _explicit_representable(
    order: RealQuadraticOrder,
    coeffs: list[Pair],
    alpha: Pair,
) -> bool:
    """Decide representability by independent sharp-box value products."""
    value_lists: list[list[Pair]] = []
    for coeff in coeffs:
        search = enumerate_weighted_search_box(
            order,
            coeff,
            alpha,
            use_sharp_box=True,
            return_all_roots=False,
        )
        value_lists.append([order.zero, *search.values])
    for choices in product(*value_lists):
        total = order.zero
        for value in choices:
            total = order.add(total, value)
        if total == alpha:
            return True
    return False


def main() -> None:
    """Execute the full deterministic corpus and write its JSON summary."""
    fields = _squarefree_fields(41)
    weighted_search_instances = 0
    representability_instances = 0
    constructive_certificates = 0
    bounded_instances = 0
    mismatches = 0

    for D in fields:
        order = RealQuadraticOrder(D)
        targets = enumerate_totally_positive_targets(order, 16)
        coefficients = enumerate_totally_positive_targets(order, 8)[:5]

        for coeff in coefficients:
            for alpha in targets:
                exact = enumerate_weighted_search(order, coeff, alpha, return_all_roots=False)
                independent = enumerate_weighted_search_box(
                    order,
                    coeff,
                    alpha,
                    use_sharp_box=True,
                    return_all_roots=False,
                )
                weighted_search_instances += 1
                if set(exact.value_to_root) != set(independent.value_to_root):
                    mismatches += 1

        for alpha in targets:
            for rank in (2, 3, 4, 5):
                coeffs = [(1, 0)] * rank
                expected = _explicit_representable(order, coeffs, alpha)
                dp = diagonal_representability_dp(order, coeffs, alpha)
                mitm = diagonal_representability_mitm(order, coeffs, alpha)
                representability_instances += 1
                if dp.represented != expected or mitm.represented != expected:
                    mismatches += 1
                for result in (dp, mitm):
                    if result.represented:
                        if result.roots is None or not verify_representation(
                            order, coeffs, alpha, result.roots
                        ):
                            mismatches += 1
                        else:
                            constructive_certificates += 1

        for coeffs in ([(1, 0), (1, 0)], [(1, 0), (1, 0), (1, 0)]):
            for bound in (8, 16):
                batched = bounded_truants_batched(order, coeffs, bound)
                naive = bounded_truants_naive(order, coeffs, bound, method="mitm")
                bounded_instances += 1
                if batched != naive:
                    mismatches += 1

    summary = {
        "fields": len(fields),
        "max_D": 41,
        "trace_bound": 16,
        "coefficient_trace_bound": 8,
        "weighted_search_instances": weighted_search_instances,
        "representability_instances": representability_instances,
        "constructive_certificates": constructive_certificates,
        "bounded_instances": bounded_instances,
        "mismatches": mismatches,
    }
    output = ROOT / "data" / "validation_summary.json"
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
