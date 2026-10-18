
import os
import sys
import tempfile
import unittest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.tac_generator import generate
from compiler.optimizer import optimize
from harness.runner import BenchmarkHarness, evaluate


class CompilerTests(unittest.TestCase):

    def test_lexer(self):
        tokens = tokenize("let x = 2;")
        self.assertEqual(
            [t.value for t in tokens[:-1]],
            ["let", "x", "=", "2", ";"]
        )

    def test_precedence_and_tac(self):
        tac = generate(parse("let x = 2 + 3 * 4;"))
        self.assertEqual(
            tac,
            ["t0 = 3 * 4", "t1 = 2 + t0", "x = t1"]
        )

    def test_constant_folding(self):
        result = optimize(["t0 = 6 * 7", "print t0"])
        self.assertEqual(result, ["t0 = 42", "print t0"])

    def test_benchmark_success(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as source:
            source.write("benchmark test")
            source_path = source.name

        try:
            result = evaluate(
                source_path,
                f'"{sys.executable}" -c "print(30)"'
            )

            self.assertTrue(result["success"])
            self.assertIn("30", result["stdout"])
            self.assertGreater(result["file_size_bytes"], 0)
            self.assertGreaterEqual(result["runtime_ms"], 0)
        finally:
            os.unlink(source_path)

    def test_benchmark_failure(self):
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False
        ) as source:
            source.write("test")
            source_path = source.name

        try:
            result = BenchmarkHarness(source_path).measure_execution(
                f'"{sys.executable}" -c "raise SystemExit(1)"'
            )
            self.assertFalse(result["success"])
        finally:
            os.unlink(source_path)


if __name__ == "__main__":
    unittest.main()
