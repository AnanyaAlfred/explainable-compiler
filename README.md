# Explainable Compiler

A starter repository for a small expression-language compiler with a lexer, recursive-descent parser, AST, three-address-code (TAC) generator, constant-folding optimizer, JSONL explainability recorder, test suite, runtime harness, and a minimal web dashboard.

## Features

- Lexer for identifiers, integer literals, operators, and punctuation
- Parser supporting `let`, `print`, parentheses, and arithmetic precedence
- AST nodes for expressions and statements
- Three-address-code generation
- Basic constant folding for literal TAC operations
- JSON Lines event recorder and JSON Schema
- Python CLI runner with output, intermediate code, and elapsed-time metric
- GitHub Actions workflow running unit tests
- Minimal React/Vite dashboard starter

## Requirements

- Python 3.10+
- Node.js/npm (only if running the web UI)

## Run the compiler demo

From the repository root:

```bash
python -m harness.runner tests/samples/basic.expr
python -m harness.runner tests/samples/basic.expr --json
python -m harness.runner tests/samples/basic.expr --events explainability/events.jsonl
```

Expected program output is `42`.

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Run the web dashboard

```bash
cd web-ui
npm install
npm run dev
```

The dashboard is a UI scaffold; it does not yet connect to a backend API.

## Language example

```text
let answer = 6 * 7;
print answer;
```

## Repository layout

```text
explainable-compiler/
├── .github/workflows/ci.yml
├── compiler/
│   ├── lexer.py
│   ├── parser.py
│   ├── ast_nodes.py
│   ├── tac_generator.py
│   └── optimizer/
├── explainability/
│   ├── recorder.py
│   └── schemas/event.schema.json
├── harness/runner.py
├── web-ui/
│   ├── public/
│   └── src/
├── tests/
├── .gitignore
└── README.md
```

## Scope and next steps

This is a runnable starter, not a production compiler. Possible extensions include richer types and diagnostics, control-flow statements, data-flow optimizations, a stable event taxonomy, benchmark baselines, and a dashboard API for browsing recorded runs.
