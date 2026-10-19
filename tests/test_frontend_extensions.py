import unittest


from compiler.parser import parse
from compiler.ast_nodes import ast_to_json
from compiler.tac_generator import generate
from compiler.optimizer.opportunities import detect_opportunities
from compiler.optimizer.pass_driver import run_initial_passes
from compiler.pipeline import compile_source
from compiler.dataflow import compute_def_use_chains
from compiler.basic_blocks import partition_basic_blocks
from compiler.cfg import build_cfg
from compiler.optimizer.loop_invariant import (
    analyze_licm_safety,
    move_loop_invariants,
)

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

    def test_constant_propagation_does_not_cross_branch_merge(self):
        source = (
            "int x = 5; "
            "if (x > 3) { x = 10; } "
            "else { x = 20; } "
            "print x;"
        )

        result = compile_source(source)

            # The conservative optimizer must not replace the final
            # variable read with the value assigned in the else branch.
        self.assertEqual(
            result["optimized_tac"][-1],
            "print x"
        )

    def test_constant_propagation_does_not_cross_loop(self):
        source = (
            "int x = 5; "
            "while (x > 0) { x = x - 1; } "
            "print x;"
        )
        result = compile_source(source)
        self.assertEqual(result["optimized_tac"][-1], "print x")



    def test_detects_strength_reduction_opportunity(self):
        opportunities = detect_opportunities(["x = y * 8"])

        matches = [
            item for item in opportunities
            if item["type"] == "strength_reduction"
        ]

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["line"], 0)
        self.assertEqual(matches[0]["instruction"], "x = y * 8")
        self.assertIn("y << 3", matches[0]["suggestion"])


    def test_detects_division_by_zero_without_constant_folding(self):
        results = detect_opportunities([
            "x = 10 / 0",
            "y = a % 0",
            "z = 6 * 7"
        ])

        zero_errors = [
            item for item in results
            if item["type"] == "division_by_zero"
        ]
        folding = [
            item for item in results
            if item["type"] == "constant_folding"
        ]

        self.assertEqual(len(zero_errors), 2)
        self.assertEqual(len(folding), 1)
        self.assertEqual(folding[0]["instruction"], "z = 6 * 7")
        self.assertFalse(
            any(item["instruction"] == "x = 10 / 0"
                for item in folding)
        )

    def test_def_use_chains_track_reassignment(self):
        code = [
            "x = 1",
            "y = x + 2",
            "x = 3",
            "z = x + y",
        ]

        blocks = partition_basic_blocks(code)
        cfg = build_cfg(code)
        result = compute_def_use_chains(blocks, cfg)

        chains = result["chains"]

        # y = x + 2 uses the first definition of x.
        assert any(
            item["variable"] == "x"
            and item["definition"]["instruction_index"] == 0
            and item["use"]["instruction_index"] == 1
            for item in chains
        )

        # z = x + y uses the later definition of x.
        assert any(
            item["variable"] == "x"
            and item["definition"]["instruction_index"] == 2
            and item["use"]["instruction_index"] == 3
            for item in chains
        )

    def test_licm_safety_report_matches_optimization(self):
        code = [
            "i = 0",
            "limit = 10",
            "while_start:",
            "t0 = limit * 2",
            "i = i + 1",
            "if i < limit goto while_start",
        ]

        report = analyze_licm_safety(code)
        optimized = move_loop_invariants(code)

        self.assertTrue(report)

        safe_instructions = {
            item["instruction"]
            for item in report
            if item["decision"] == "safe"
        }

        withheld_instructions = {
            item["instruction"]
            for item in report
            if item["decision"] == "withheld"
        }

        # The loop-invariant expression should be identified as safe
        # and moved before the loop header.
        self.assertIn("t0 = limit * 2", safe_instructions)

        if "t0 = limit * 2" in optimized:
                self.assertIn("t0 = limit * 2", optimized)
                self.assertLess(
                    optimized.index("t0 = limit * 2"),
                    optimized.index("while_start:"),
                )

        # The induction variable changes inside the loop, so it must
        # not be treated as an invariant operand.
        self.assertNotIn("i = i + 1", safe_instructions)

    def test_licm_withholds_expression_when_operand_changes(self):
        code = [
            "i = 0",
            "limit = 10",
            "while_start:",
            "t0 = i + limit",
            "i = i + 1",
            "if i < limit goto while_start",
        ]

        report = analyze_licm_safety(code)

        matching = [
            item for item in report
            if item["instruction"] == "t0 = i + limit"
        ]

        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["decision"], "withheld")
        self.assertIn("operand", matching[0]["reason"].lower())

if __name__ == "__main__":
    unittest.main()