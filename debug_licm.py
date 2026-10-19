
from compiler.cfg import build_cfg
from compiler.optimizer.loop_invariant import _compute_dominators, _find_loops

code = [
    "a = 5",
    "b = 10",
    "LOOP:",
    "t = a + b",
    "x = x + t",
    "if x < 100 goto LOOP",
    "goto END",
    "END:",
    "print x",
]

cfg = build_cfg(code)

print("BLOCKS:")
for block in cfg["blocks"]:
    print(block)

print("\nEDGES:")
for edge in cfg["edges"]:
    print(edge)

print("\nDOMINATORS:")
print(_compute_dominators(cfg))

print("\nLOOPS:")
print(_find_loops(cfg))
