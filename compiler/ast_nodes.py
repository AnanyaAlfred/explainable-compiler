"""AST node definitions."""
from dataclasses import dataclass
from typing import Union

@dataclass
class Number:
    value: int

@dataclass
class Variable:
    name: str

@dataclass
class BinaryOp:
    op: str
    left: "Expr"
    right: "Expr"

@dataclass
class Let:
    name: str
    value: "Expr"

@dataclass
class Print:
    value: "Expr"

Expr = Union[Number, Variable, BinaryOp]
Statement = Union[Let, Print]
