
import React from "react";
import ReactDOM from "react-dom/client";
import "./style.css";

const DEFAULT_SOURCE = `int x = 2 + 3 * 4;
print x;`;

function ASTNode({ name, value }) {
  if (Array.isArray(value)) {
    return (
      <div className="ast-children">
        {value.map((item, index) => (
          <ASTNode key={`${name}-${index}`} name={`${name}[${index}]`} value={item} />
        ))}
      </div>
    );
  }

  if (value && typeof value === "object") {
    return (
      <div className="ast-node">
        <div className="ast-node-title">
          <span className="ast-type">{value.node_type || "Object"}</span>
          <span className="ast-name">{name}</span>
        </div>
        {Object.entries(value)
          .filter(([key]) => key !== "node_type")
          .map(([key, child]) => (
            <ASTNode key={key} name={key} value={child} />
          ))}
      </div>
    );
  }

  return (
    <div className="ast-leaf">
      <span className="ast-name">{name}</span>
      <span className="ast-value">{String(value)}</span>
    </div>
  );
}

function ResultPanel({ title, children }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

const OPPORTUNITY_LABELS = {
  division_by_zero: "Division or remainder by zero",
  constant_folding: "Constant expression",
  algebraic_simplification: "Simplifiable arithmetic",
  common_subexpression: "Repeated expression",
  strength_reduction: "Multiplication that may be simplified",
  copy_propagation: "Variable copy",
};

function formatLabel(value) {
  return String(value || "Unknown")
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function JsonDetails({ value }) {
  return (
    <details className="raw-json">
      <summary>View raw JSON</summary>
      <pre>{JSON.stringify(value, null, 2)}</pre>
    </details>
  );
}

function OptimizationOpportunities({ opportunities }) {
  const items = Array.isArray(opportunities) ? opportunities : [];

  return (
    <>
      <p className="muted section-description">
        Suggestions found by scanning the original instructions. These are
        opportunities to review, not guaranteed changes.
      </p>
      <p className="summary-count">
        {items.length === 0
          ? "No optimization opportunities found."
          : `${items.length} ${
              items.length === 1 ? "opportunity" : "opportunities"
            } found`}
      </p>
      {items.length > 0 && (
        <div className="opportunity-list">
          {items.map((item, index) => (
            <article className="opportunity-card" key={`${item.type}-${item.line}-${index}`}>
              <div className="card-heading">
                <h3>{OPPORTUNITY_LABELS[item.type] || formatLabel(item.type)}</h3>
                <span className="line-badge">
                  TAC line {Number.isInteger(item.line) ? item.line + 1 : "—"}
                </span>
              </div>
              {item.instruction && (
                <pre className="inline-code">{item.instruction}</pre>
              )}
              {item.why && (
                <p><strong>Why it matters:</strong> {item.why}</p>
              )}
              {item.suggestion && (
                <p><strong>Suggested action:</strong> {item.suggestion}</p>
              )}
              {Number.isInteger(item.previous_line) && (
                <p className="muted">
                  Matching expression first appeared on TAC line{" "}
                  {item.previous_line + 1}.
                </p>
              )}
            </article>
          ))}
        </div>
      )}
      <JsonDetails value={opportunities} />
    </>
  );
}

function PassExecutionHistory({ history }) {
  const passes = Array.isArray(history) ? history : [];

  return (
    <>
      <p className="muted section-description">
        Each pass transforms the instruction list produced by the previous
        step. Expand a pass to compare its input and output.
      </p>
      {passes.length === 0 ? (
        <p className="empty-state">No pass execution details are available.</p>
      ) : (
        <div className="pass-list">
          {passes.map((pass, index) => {
            const before = Array.isArray(pass.before) ? pass.before : [];
            const after = Array.isArray(pass.after) ? pass.after : [];
            const changed = JSON.stringify(before) !== JSON.stringify(after);
            const difference = before.length - after.length;
            const resultLabel = changed
              ? difference > 0
                ? `${difference} ${difference === 1 ? "instruction" : "instructions"} removed`
                : difference < 0
                  ? `${Math.abs(difference)} ${Math.abs(difference) === 1 ? "instruction" : "instructions"} added`
                  : "Instructions changed"
              : "No changes";

            return (
              <details className="pass-card" key={`${pass.pass_name}-${index}`}>
                <summary>
                  <span className="pass-name">
                    <span className="step-number">{index + 1}</span>
                    {formatLabel(pass.pass_name)}
                  </span>
                  <span className={`pass-result ${changed ? "changed" : ""}`}>
                    {resultLabel}
                  </span>
                </summary>
                <div className="pass-comparison">
                  <div>
                    <h4>Before <span>{before.length} {before.length === 1 ? "instruction" : "instructions"}</span></h4>
                    <pre>{before.join("\n") || "(No instructions)"}</pre>
                  </div>
                  <div>
                    <h4>After <span>{after.length} {after.length === 1 ? "instruction" : "instructions"}</span></h4>
                    <pre>{after.join("\n") || "(No instructions)"}</pre>
                  </div>
                </div>
              </details>
            );
          })}
        </div>
      )}
      <JsonDetails value={history} />
    </>
  );
}

function BasicBlocks({ blocks }) {
  const items = Array.isArray(blocks) ? blocks : [];

  return (
    <>
      <p className="muted section-description">
        Basic blocks are straight-line groups of instructions with one entry
        point. TAC line numbers below start at 1.
      </p>
      {items.length === 0 ? (
        <p className="empty-state">No basic blocks were generated.</p>
      ) : (
        <div className="block-grid">
          {items.map((block, index) => {
            const instructions = Array.isArray(block.instructions)
              ? block.instructions
              : [];
            const firstLine = Number.isInteger(block.start) ? block.start + 1 : null;
            const lastLine = Number.isInteger(block.end)
              ? block.end
              : firstLine === null
                ? null
                : firstLine + instructions.length - 1;

            return (
              <article className="basic-block-card" key={block.id || index}>
                <div className="card-heading">
                  <h3>{block.id || `Block ${index + 1}`}</h3>
                  <span className="line-badge">
                    {firstLine === null
                      ? `${instructions.length} ${instructions.length === 1 ? "instruction" : "instructions"}`
                      : firstLine === lastLine
                        ? `TAC line ${firstLine}`
                        : `TAC lines ${firstLine}–${lastLine}`}
                  </span>
                </div>
                <pre>{instructions.join("\n") || "(No instructions)"}</pre>
              </article>
            );
          })}
        </div>
      )}
      <JsonDetails value={blocks} />
    </>
  );
}

function App() {
  const [source, setSource] = React.useState(DEFAULT_SOURCE);
  const [result, setResult] = React.useState(null);
  const [error, setError] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [showJSON, setShowJSON] = React.useState(false);

  async function compile() {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Compilation failed.");
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message.includes("Failed to fetch")
          ? "Cannot reach the compiler API. Start api_server.py and try again."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <div className="eyebrow">EXPLAINABLE COMPILER</div>
      <h1>Compiler Workbench</h1>
      <p className="intro">
        Enter source code and inspect its AST, intermediate code,
        optimization opportunities, and pass execution results.
      </p>

      <section className="panel">
        <h2>Source Code</h2>
        <textarea
          className="source-editor"
          value={source}
          onChange={(event) => setSource(event.target.value)}
          spellCheck={false}
          aria-label="Compiler source code"
        />
        <button onClick={compile} disabled={loading}>
          {loading ? "Compiling..." : "Compile Source"}
        </button>
        {error && <p className="error-message">{error}</p>}
      </section>

      {result && (
        <>
          <ResultPanel title="Abstract Syntax Tree">
            <div className="panel-heading">
              <p className="muted">Generated from your source code</p>
              <button onClick={() => setShowJSON(!showJSON)}>
                {showJSON ? "Show tree" : "Show JSON"}
              </button>
            </div>
            {showJSON ? (
              <pre>{JSON.stringify(result.ast, null, 2)}</pre>
            ) : (
              <div className="ast-tree">
                <ASTNode name="root" value={result.ast} />
              </div>
            )}
          </ResultPanel>

          <ResultPanel title="Original Three-Address Code">
            <pre>{result.original_tac.join("\n") || "(No instructions)"}</pre>
          </ResultPanel>

          <ResultPanel title="Optimization Opportunities">
            <OptimizationOpportunities opportunities={result.opportunities} />
          </ResultPanel>

          <ResultPanel title="Pass Execution History">
            <PassExecutionHistory history={result.pass_history} />
          </ResultPanel>

          <ResultPanel title="LICM Safety Report">
            <pre>
              {JSON.stringify(result.licm_safety ?? [], null, 2)}
            </pre>
          </ResultPanel>

          <ResultPanel title="Optimized Three-Address Code">
            <pre>{result.optimized_tac.join("\n") || "(No instructions)"}</pre>
          </ResultPanel>

          <ResultPanel title="Basic Blocks">
            <BasicBlocks blocks={result.basic_blocks} />
          </ResultPanel>
        </>
      )}

      <footer>Explainable Compiler · Python + React</footer>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
