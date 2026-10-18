"""End-to-end source compilation pipeline."""

from pathlib import Path

from .parser import parse
from .ast_nodes import ast_to_json
from .tac_generator import generate
from .optimizer.pass_driver import run_initial_passes


def compile_source(source: str) -> dict:
    """Compile source text and return structured compilation results."""
    statements = parse(source)
    original_tac = generate(statements)
    optimization = run_initial_passes(original_tac)

    return {
        "source": source,
        "ast": ast_to_json(statements),
        "original_tac": original_tac,
        "opportunities": optimization["opportunities"],
        "pass_history": optimization["pass_history"],
        "optimized_tac": optimization["optimized_tac"],
        "basic_blocks": optimization["basic_blocks"]
    }


def compile_file(path: str) -> dict:
    """Compile a source file from disk."""
    source_path = Path(path)
    source = source_path.read_text(encoding="utf-8")
    result = compile_source(source)
    result["source_file"] = str(source_path)
    return result