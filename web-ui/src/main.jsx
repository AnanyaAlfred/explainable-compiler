
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
            <pre>{JSON.stringify(result.opportunities, null, 2)}</pre>
          </ResultPanel>

          <ResultPanel title="Pass Execution History">
            <pre>{JSON.stringify(result.pass_history, null, 2)}</pre>
          </ResultPanel>

          <ResultPanel title="Optimized Three-Address Code">
            <pre>{result.optimized_tac.join("\n") || "(No instructions)"}</pre>
          </ResultPanel>

          <ResultPanel title="Basic Blocks">
            <pre>{JSON.stringify(result.basic_blocks, null, 2)}</pre>
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
