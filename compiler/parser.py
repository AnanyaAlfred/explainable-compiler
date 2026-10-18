"""Recursive-descent parser for a tiny expression language."""
from .ast_nodes import BinaryOp, Let, Number, Print, Variable
from .lexer import tokenize

class Parser:
    def __init__(self, source: str):
        self.tokens = tokenize(source)
        self.index = 0

    def current(self):
        return self.tokens[self.index]

    def consume(self, value=None, kind=None):
        token = self.current()
        if value is not None and token.value != value:
            raise SyntaxError(f"Expected {value!r} at position {token.position}")
        if kind is not None and token.kind != kind:
            raise SyntaxError(f"Expected {kind} at position {token.position}")
        self.index += 1
        return token

    def parse(self):
        statements = []
        while self.current().kind != "EOF":
            statements.append(self.statement())
            if self.current().value == ";":
                self.consume(";")
            elif self.current().kind != "EOF":
                raise SyntaxError(f"Expected ';' at position {self.current().position}")
        return statements

    def statement(self):
        if self.current().value == "let":
            self.consume("let")
            name = self.consume(kind="IDENT").value
            self.consume("=")
            return Let(name, self.expression())
        if self.current().value == "print":
            self.consume("print")
            return Print(self.expression())
        raise SyntaxError(f"Expected 'let' or 'print' at position {self.current().position}")

    def expression(self):
        node = self.term()
        while self.current().value in {"+", "-"}:
            op = self.consume().value
            node = BinaryOp(op, node, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.current().value in {"*", "/"}:
            op = self.consume().value
            node = BinaryOp(op, node, self.factor())
        return node

    def factor(self):
        token = self.current()
        if token.kind == "INT":
            return Number(int(self.consume(kind="INT").value))
        if token.kind == "IDENT":
            return Variable(self.consume(kind="IDENT").value)
        if token.value == "(":
            self.consume("(")
            node = self.expression()
            self.consume(")")
            return node
        raise SyntaxError(f"Expected expression at position {token.position}")

def parse(source: str):
    return Parser(source).parse()
