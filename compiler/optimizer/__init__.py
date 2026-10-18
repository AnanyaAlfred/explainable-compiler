"""Public optimization interfaces."""

from .constant_folding import optimize, constant_propagation

__all__ = ["optimize", "constant_propagation"]