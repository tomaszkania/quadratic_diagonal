"""Minimal constructive diagonal-representability example."""
from quadratic_diagonal import RealQuadraticOrder, diagonal_representability_mitm, verify_representation

order = RealQuadraticOrder(21)
coeffs = [(2, 1), (1, 0), (1, 0), (1, 0)]
alpha = (30, 0)
result = diagonal_representability_mitm(order, coeffs, alpha)
assert result.roots is not None
assert verify_representation(order, coeffs, alpha, result.roots)
print(result.roots)
