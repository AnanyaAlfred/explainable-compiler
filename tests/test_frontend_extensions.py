import unittest

from compiler.parser import parse
from compiler.ast_nodes import ast_to_json
from compiler.tac_generator import generate
from compiler.optimizer.opportunities import detect_opportunities
from compiler.optimizer.pass_driver import run_initial_passes
from compiler.pipeline import compile_source


class FrontendExtensionTests(unittest.TestCase):

    def test_typed_declaration(self):
        statements = parse("int x = 10;")
        self.assertEqual(len(statements), 1)

    def test_float_declaration(self):
        statements = parse("float price = 2.5;")
        self.assertEqual(len(statements), 1)

    def test_assignment(self):
        statements = parse("let x = 1; x = x + 2;")
        self.assertEqual(len(statements), 2)

    def test_if_else_tac(self):
        code = generate(
            parse("int x = 1; if (x < 2) { print x; } else { print 0; }")
        )
        self.assertTrue(any("ifFalse" in line for line in code))
        self.assertTrue(any(line.endswith(":") for line in code))

    def test_while_tac(self):
        code = generate(
            parse("int x = 0; while (x < 3) { x = x + 1; }")
        )
        self.assertTrue(any("WHILE" in line for line in code))

    def test_for_tac(self):
        code = generate(
            parse("for (int i = 0; i < 3; i = i + 1) { print i; }")
        )
        self.assertTrue(any("FOR" in line for line in code))

    def test_ast_json(self):
        tree = ast_to_json(parse("int x = 5;"))
        self.assertEqual(tree["node_type"], "Program")
        self.assertEqual(
            tree["statements"][0]["node_type"], "Declare"
        )

    def test_opportunity_detection(self):
        results = detect_opportunities(["t0 = 6 * 7"])
        self.assertEqual(results[0]["type"], "constant_folding")

    def test_pass_driver(self):
        result = run_initial_passes(["t0 = 6 * 7", "print t0"])
        self.assertIn("optimized_tac", result)
        self.assertIn("pass_history", result)

    def test_compilation_pipeline(self):
        result = compile_source("int x = 6 * 7; print x;")
        self.assertIn("ast", result)
        self.assertIn("original_tac", result)
        self.assertIn("optimized_tac", result)


if __name__ == "__main__":
    unittest.main()