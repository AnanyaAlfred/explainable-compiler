import unittest
from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.tac_generator import generate
from compiler.optimizer import optimize
from harness.runner import evaluate

class CompilerTests(unittest.TestCase):
    def test_lexer(self):
        self.assertEqual([t.value for t in tokenize("let x = 2;")[:-1]],
                         ["let", "x", "=", "2", ";"])

    def test_precedence_and_tac(self):
        tac = generate(parse("let x = 2 + 3 * 4;"))
        self.assertEqual(tac, ["t0 = 3 * 4", "t1 = 2 + t0", "x = t1"])

    def test_constant_folding(self):
        self.assertEqual(optimize(["t0 = 6 * 7", "print t0"]),
                         ["t0 = 42", "print t0"])

    def test_runner(self):
        result = evaluate("let x = 6 * 7; print x;")
        self.assertEqual(result["output"], [42])
        self.assertEqual(result["optimized_tac"], ["t0 = 42", "x = t0", "print x"])

if __name__ == "__main__":
    unittest.main()
