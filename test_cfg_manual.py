
from compiler.cfg import build_cfg


def test_straight_line():
    code = [
        "x = 1",
        "y = x + 2",
        "print y"
    ]

    cfg = build_cfg(code)

    assert len(cfg["blocks"]) == 1
    assert cfg["edges"] == []


def test_if_else():
    code = [
        "x = 1",
        "ifFalse x goto ELSE",
        "x = 2",
        "goto END",
        "ELSE:",
        "x = 3",
        "END:",
        "print x"
    ]

    cfg = build_cfg(code)

    print("BLOCKS:")
    for block in cfg["blocks"]:
        print(block)

    print("EDGES:")
    for edge in cfg["edges"]:
        print(edge)

    assert len(cfg["blocks"]) == 4

    assert set(cfg["successors"]["B0"]) == {"B1", "B2"}
    assert cfg["successors"]["B1"] == ["B3"]
    assert cfg["successors"]["B2"] == ["B3"]
    assert cfg["successors"]["B3"] == []

    assert cfg["predecessors"]["B0"] == []
    assert cfg["predecessors"]["B1"] == ["B0"]
    assert cfg["predecessors"]["B2"] == ["B0"]
    assert set(cfg["predecessors"]["B3"]) == {"B1", "B2"}


def test_loop_back_edge():
    code = [
        "i = 0",
        "LOOP:",
        "i = i + 1",
        "ifFalse i < 5 goto END",
        "goto LOOP",
        "END:",
        "print i"
    ]

    cfg = build_cfg(code)

    print("\nLOOP BLOCKS:")
    for block in cfg["blocks"]:
        print(block)

    print("LOOP EDGES:")
    for edge in cfg["edges"]:
        print(edge)


if __name__ == "__main__":
    test_straight_line()
    test_if_else()
    test_loop_back_edge()
    print("All CFG tests passed!")
