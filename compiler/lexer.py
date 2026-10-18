"""Lexer for the Explainable Compiler."""

from dataclasses import dataclass


KEYWORDS = {
    "let", "print", "int", "float",
    "if", "else", "while", "for"
}

TWO_CHAR_OPERATORS = {
    "==", "!=", "<=", ">=", "&&", "||"
}

SINGLE_CHAR_OPERATORS = {
    "+", "-", "*", "/", "%", "=",
    "<", ">", "!"
}

PUNCTUATION = {
    "(", ")", "{", "}", ";", ","
}


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    position: int


def tokenize(source: str) -> list[Token]:
    tokens = []
    i = 0

    while i < len(source):
        ch = source[i]

        if ch.isspace():
            i += 1
            continue

        # Single-line comments.
        if source.startswith("//", i):
            newline = source.find("\n", i)
            i = len(source) if newline == -1 else newline + 1
            continue

        # Block comments.
        if source.startswith("/*", i):
            end = source.find("*/", i + 2)
            if end == -1:
                raise SyntaxError(
                    f"Unterminated comment at position {i}"
                )
            i = end + 2
            continue

        if ch.isalpha() or ch == "_":
            start = i
            i += 1

            while i < len(source) and (
                source[i].isalnum() or source[i] == "_"
            ):
                i += 1

            value = source[start:i]
            kind = "KEYWORD" if value in KEYWORDS else "IDENT"
            tokens.append(Token(kind, value, start))
            continue

        if ch.isdigit():
            start = i
            i += 1

            while i < len(source) and source[i].isdigit():
                i += 1

            if i < len(source) and source[i] == ".":
                i += 1

                if i >= len(source) or not source[i].isdigit():
                    raise SyntaxError(
                        f"Invalid number at position {start}"
                    )

                while i < len(source) and source[i].isdigit():
                    i += 1

                tokens.append(
                    Token("FLOAT", source[start:i], start)
                )
            else:
                tokens.append(
                    Token("INT", source[start:i], start)
                )

            continue

        matched = None

        for operator in TWO_CHAR_OPERATORS:
            if source.startswith(operator, i):
                matched = operator
                break

        if matched is not None:
            tokens.append(Token("OP", matched, i))
            i += len(matched)
            continue

        if ch in SINGLE_CHAR_OPERATORS:
            tokens.append(Token("OP", ch, i))
            i += 1
            continue

        if ch in PUNCTUATION:
            tokens.append(Token("PUNCT", ch, i))
            i += 1
            continue

        raise SyntaxError(
            f"Unexpected character {ch!r} at position {i}"
        )

    tokens.append(Token("EOF", "", len(source)))
    return tokens