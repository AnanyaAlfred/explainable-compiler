
from compiler.basic_blocks import partition_basic_blocks
from compiler.cfg import build_cfg
from compiler.dataflow import compute_def_use_chains


def test_def_use_chains_across_branches():
    code = [
        "x = 1",
        "if condition goto branch_a",
        "x = 2",
        "goto merge",
        "branch_a:",
        "x = 3",
        "merge:",
        "y = x + 1",
    ]

    blocks = partition_basic_blocks(code)
    cfg = build_cfg(code)
    result = compute_def_use_chains(blocks, cfg)

    def location_of(instruction):
        for block in blocks:
            if instruction in block["instructions"]:
                return (
                    block["id"],
                    block["instructions"].index(instruction),
                )
        raise AssertionError(f"Instruction not found: {instruction}")

    expected_definitions = {
        location_of("x = 2"),
        location_of("x = 3"),
    }
    expected_use = location_of("y = x + 1")

    reaching_definitions = {
        (
            chain["definition"]["block"],
            chain["definition"]["instruction_index"],
        )
        for chain in result["chains"]
        if chain["variable"] == "x"
        and (
            chain["use"]["block"],
            chain["use"]["instruction_index"],
        ) == expected_use
    }

    assert expected_definitions.issubset(reaching_definitions)


def test_def_use_chains_across_loop():
    code = [
        "x = 0",
        "loop_start:",
        "x = x + 1",
        "if x < 5 goto loop_start",
        "y = x + 2",
    ]

    blocks = partition_basic_blocks(code)
    cfg = build_cfg(code)
    result = compute_def_use_chains(blocks, cfg)

    def location_of(instruction):
        for block in blocks:
            if instruction in block["instructions"]:
                return (
                    block["id"],
                    block["instructions"].index(instruction),
                )
        raise AssertionError(f"Instruction not found: {instruction}")

    expected_use = location_of("y = x + 2")
    expected_definitions = {
        location_of("x = x + 1"),
    }

    reaching_definitions = {
        (
            chain["definition"]["block"],
            chain["definition"]["instruction_index"],
        )
        for chain in result["chains"]
        if chain["variable"] == "x"
        and (
            chain["use"]["block"],
            chain["use"]["instruction_index"],
        ) == expected_use
    }

    assert expected_definitions.issubset(reaching_definitions)
