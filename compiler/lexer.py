"""A small lexer for the explainable compiler starter project."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    position: int

def tokenize(source: str) -> list[Token]:
    """Tokenize identifiers, integers, operators, punctuation, and whitespace."""
    tokens: list[Token] = []
    i = 0
    while i < len(source):
        ch = source[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isalpha() or ch == "_":
            start = i
            i += 1
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1
            value = source[start:i]
            tokens.append(Token("KEYWORD" if value in {"let", "print"} else "IDENT", value, start))
            continue
        if ch.isdigit():
            start = i
            i += 1
            while i < len(source) and source[i].isdigit():
                i += 1
            tokens.append(Token("INT", source[start:i], start))
            continue
        if source.startswith(("==", "!=", "<=", ">="), i):
            tokens.append(Token("OP", source[i:i+2], i))
            i += 2
            continue
        if ch in "+-*/=<>":
            tokens.append(Token("OP", ch, i))
        elif ch in "();":
            tokens.append(Token("PUNCT", ch, i))
        else:
            raise SyntaxError(f"Unexpected character {ch!r} at position {i}")
        i += 1
    tokens.append(Token("EOF", "", len(source)))
    return tokens
