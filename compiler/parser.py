"""Recursive-descent parser for the C-like language subset."""

from .ast_nodes import (
    Assign, BinaryOp, Block, Declare, For,
    IfElse, Let, Number, Print, UnaryOp,
    Variable, While
)
from .lexer import tokenize


class Parser:
    def __init__(self, source: str):
        self.tokens = tokenize(source)
        self.index = 0

    def current(self):
        return self.tokens[self.index]

    def check(self, value):
        return self.current().value == value

    def consume(self, value=None, kind=None):
        token = self.current()

        if value is not None and token.value != value:
            raise SyntaxError(
                f"Expected {value!r} at position {token.position}"
            )

        if kind is not None and token.kind != kind:
            raise SyntaxError(
                f"Expected {kind} at position {token.position}"
            )

        self.index += 1
        return token

    def parse(self):
        statements = []

        while self.current().kind != "EOF":
            previous = self.index
            statements.append(self.statement())

            # Prevent accidental infinite loops if the grammar changes.
            if self.index == previous:
                raise SyntaxError(
                    f"Parser made no progress at position "
                    f"{self.current().position}"
                )

        return statements

    def statement(self):
        value = self.current().value

        if value == "{":
            return self.block()

        if value == "let":
            self.consume("let")
            name = self.consume(kind="IDENT").value
            self.consume("=")
            result = Let(name, self.expression())
            self.consume(";")
            return result

        if value in {"int", "float"}:
            data_type = self.consume().value
            name = self.consume(kind="IDENT").value

            initializer = None
            if self.check("="):
                self.consume("=")
                initializer = self.expression()

            self.consume(";")
            return Declare(
                name,
                data_type,
                initializer if initializer is not None else Number(0)
            )

        if value == "print":
            self.consume("print")
            self.consume("(") if self.check("(") else None
            expr = self.expression()
            if self.check(")"):
                self.consume(")")
            self.consume(";")
            return Print(expr)

        if value == "if":
            return self.if_statement()

        if value == "while":
            return self.while_statement()

        if value == "for":
            return self.for_statement()

        if self.current().kind == "IDENT":
            name = self.consume(kind="IDENT").value
            self.consume("=")
            expr = self.expression()
            self.consume(";")
            return Assign(name, expr)

        raise SyntaxError(
            f"Unexpected token {self.current().value!r} "
            f"at position {self.current().position}"
        )

    def block(self):
        self.consume("{")
        statements = []

        while not self.check("}"):
            if self.current().kind == "EOF":
                raise SyntaxError("Unterminated block")
            statements.append(self.statement())

        self.consume("}")
        return Block(statements)

    def if_statement(self):
        self.consume("if")
        self.consume("(")
        condition = self.expression()
        self.consume(")")
        then_branch = self.block()

        else_branch = None
        if self.check("else"):
            self.consume("else")
            else_branch = self.block()

        return IfElse(condition, then_branch, else_branch)

    def while_statement(self):
        self.consume("while")
        self.consume("(")
        condition = self.expression()
        self.consume(")")
        return While(condition, self.block())

    def for_statement(self):
        self.consume("for")
        self.consume("(")

        initializer = None

        if not self.check(";"):
            if self.current().value in {"int", "float", "let"}:
                keyword = self.consume().value

                if keyword == "let":
                    name = self.consume(kind="IDENT").value
                    self.consume("=")
                    initializer = Let(name, self.expression())
                else:
                    name = self.consume(kind="IDENT").value
                    self.consume("=")
                    initializer = Declare(
                        name, keyword, self.expression()
                    )
            else:
                name = self.consume(kind="IDENT").value
                self.consume("=")
                initializer = Assign(name, self.expression())

        self.consume(";")

        condition = None
        if not self.check(";"):
            condition = self.expression()

        self.consume(";")

        update = None
        if not self.check(")"):
            name = self.consume(kind="IDENT").value
            self.consume("=")
            update = Assign(name, self.expression())

        self.consume(")")
        return For(initializer, condition, update, self.block())

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        node = self.logical_and()
        while self.check("||"):
            operator_token = self.consume()
            op = operator_token.value
            node = BinaryOp(op, node, self.logical_and(),position=operator_token.position)
        return node

    def logical_and(self):
        node = self.equality()
        while self.check("&&"):
            operator_token = self.consume()
            op = operator_token.value
            node = BinaryOp(op, node, self.equality(),position=operator_token.position)
        return node

    def equality(self):
        node = self.comparison()
        while self.current().value in {"==", "!="}:
            operator_token = self.consume()
            op = operator_token.value
            node = BinaryOp(op, node, self.comparison(),position=operator_token.position)
        return node

    def comparison(self):
        node = self.additive()
        while self.current().value in {"<", ">", "<=", ">="}:
            operator_token = self.consume()
            op = operator_token.value
            node = BinaryOp(op, node, self.additive(),position=operator_token.position)
        return node

    def additive(self):
        node = self.term()
        while self.current().value in {"+", "-"}:
            operator_token = self.consume()
            op = operator_token.value
            node = BinaryOp(op, node, self.term(),position=operator_token.position)
        return node

    def term(self):
        node = self.unary()
        while self.current().value in {"*", "/", "%"}:
            operator_token = self.consume()
            op = operator_token.value
            node = BinaryOp(op, node, self.unary(),position=operator_token.position)
        return node

    def unary(self):
        if self.current().value in {"-", "!"}:
            operator_token = self.consume()
            return UnaryOp(
                operator_token.value,
                self.unary(),
                position=operator_token.position
            )
        return self.factor()


    def factor(self):
        token = self.current()

        if token.kind == "INT":
            token = self.consume(kind="INT")
            return Number(int(token.value), position=token.position)

        if token.kind == "FLOAT":
            token = self.consume(kind="FLOAT")
            return Number(float(token.value), position=token.position)

        if token.kind == "IDENT":
            token = self.consume(kind="IDENT")
            return Variable(token.value, position=token.position)

        if self.check("("):
            self.consume("(")
            node = self.expression()
            self.consume(")")
            return node

        raise SyntaxError(
            f"Expected expression at position {token.position}"
        )


def parse(source: str):
    return Parser(source).parse()