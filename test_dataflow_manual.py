
from compiler.basic_blocks import partition_basic_blocks
from compiler.dataflow import compute_use_def


def test_use_def():
    code = [
        "x = 1",
        "y = x + z",
        "x = y + 2",
        "print x"
    ]

    blocks = partition_basic_blocks(code)
    result = compute_use_def(blocks)

    assert result["B0"]["USE"] == {"z"}
    assert result["B0"]["DEF"] == {"x", "y"}

    print("USE/DEF test passed!")


if __name__ == "__main__":
    test_use_def()
