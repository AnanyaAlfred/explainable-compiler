
from compiler.pipeline import compile_source, compile_file


SOURCE = "let x = 2 + 3; print x;"


def test_compile_source_returns_expected_fields():
    result = compile_source(SOURCE)

    assert result["source"] == SOURCE
    assert result["ast"] is not None
    assert result["original_tac"]
    assert result["optimized_tac"]
    assert "opportunities" in result
    assert "pass_history" in result
    assert "basic_blocks" in result


def test_compile_source_records_optimization_passes():
    result = compile_source(SOURCE)

    pass_names = [
        item["pass_name"]
        for item in result["pass_history"]
    ]

    assert "constant_folding" in pass_names
    assert "dead_code_elimination" in pass_names


def test_compile_file_reads_source(tmp_path):
    source_file = tmp_path / "sample.txt"
    source_file.write_text(SOURCE, encoding="utf-8")

    result = compile_file(str(source_file))

    assert result["source"] == SOURCE
    assert result["source_file"] == str(source_file)
    assert result["optimized_tac"]
    assert any(
        line.strip().startswith("print ")
        for line in result["optimized_tac"]
    )


def test_compile_source_reports_division_by_zero():
    result = compile_source(
        "int x = 10 / (3 - 3); print x;"
    )

    assert any(
        item["type"] == "division_by_zero"
        for item in result["diagnostics"]
    )


def test_compile_source_has_no_diagnostics_for_valid_arithmetic():
    result = compile_source("int x = 10 / 2; print x;")

    assert result["diagnostics"] == []



def test_division_by_zero_diagnostic_includes_operator_position():
    source = "int x = 10 / (3 - 3); print x;"
    result = compile_source(source)

    diagnostic = next(
        item for item in result["diagnostics"]
        if item["type"] == "division_by_zero"
    )

    assert diagnostic["position"] == source.index("/")
    assert source[diagnostic["position"]] == diagnostic["operator"]



def test_division_by_zero_diagnostic_includes_line_and_column():
    source = "int x = 10 / (3 - 3);\nprint x;"
    result = compile_source(source)

    diagnostic = next(
        item for item in result["diagnostics"]
        if item["type"] == "division_by_zero"
    )

    assert diagnostic["line"] == 1
    assert diagnostic["column"] == 12
