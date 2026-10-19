
from compiler.basic_blocks import partition_basic_blocks
from compiler.cfg import build_cfg
from compiler.dataflow import compute_use_def, compute_liveness


def test_liveness():
    code = [
        "x = 1",
        "y = x + z",
        "print y"
    ]

    blocks = partition_basic_blocks(code)
    cfg = build_cfg(code)
    use_def = compute_use_def(blocks)
    result = compute_liveness(blocks, use_def, cfg)

    assert result["B0"]["IN"] == {"z"}
    assert result["B0"]["OUT"] == set()

    print("Liveness test passed!")


def test_branching_liveness():
    code = [
        "x = 1",
        "ifFalse x goto ELSE",
        "y = 10",
        "goto END",
        "ELSE:",
        "y = 20",
        "END:",
        "print y"
    ]

    blocks = partition_basic_blocks(code)
    cfg = build_cfg(code)
    use_def = compute_use_def(blocks)
    result = compute_liveness(blocks, use_def, cfg)

    assert result["B0"]["IN"] == set()
    assert result["B0"]["OUT"] == set()
    assert result["B1"]["IN"] == set()
    assert result["B1"]["OUT"] == {"y"}
    assert result["B2"]["IN"] == set()
    assert result["B2"]["OUT"] == {"y"}
    assert result["B3"]["IN"] == {"y"}
    assert result["B3"]["OUT"] == set()

    print("Branching liveness test passed!")


if __name__ == "__main__":
    test_liveness()
    test_branching_liveness()
