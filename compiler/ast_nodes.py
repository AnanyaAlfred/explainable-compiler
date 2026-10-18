"""AST node definitions for the Explainable Compiler."""

from dataclasses import dataclass, fields
from typing import Union, Any


@dataclass
class Number:
    value: Union[int, float]


@dataclass
class Variable:
    name: str


@dataclass
class BinaryOp:
    op: str
    left: "Expr"
    right: "Expr"


@dataclass
class UnaryOp:
    op: str
    operand: "Expr"


@dataclass
class Let:
    name: str
    value: "Expr"


@dataclass
class Declare:
    name: str
    data_type: str
    value: "Expr"


@dataclass
class Assign:
    name: str
    value: "Expr"


@dataclass
class Print:
    value: "Expr"


@dataclass
class Block:
    statements: list["Statement"]


@dataclass
class IfElse:
    condition: "Expr"
    then_branch: Block
    else_branch: Block | None = None


@dataclass
class While:
    condition: "Expr"
    body: Block


@dataclass
class For:
    initializer: "Statement | None"
    condition: "Expr | None"
    update: "Statement | None"
    body: Block


Expr = Union[Number, Variable, BinaryOp, UnaryOp]

Statement = Union[
    Let, Declare, Assign, Print, Block, IfElse, While, For
]


def to_dict(node):
    """Recursively serialize AST nodes with their node types."""
    if isinstance(node, list):
        return [to_dict(item) for item in node]

    if hasattr(node, "__dataclass_fields__"):
        result = {"node_type": type(node).__name__}

        for field in fields(node):
            result[field.name] = to_dict(
                getattr(node, field.name)
            )

        return result

    return node


def ast_to_json(statements: list[Statement]) -> dict:
    return {
        "node_type": "Program",
        "statements": to_dict(statements),
    }