import React from "react";
import ReactDOM from "react-dom/client";
import "./style.css";

const sampleAST = {
  node_type: "Program",
  statements: [
    {
      node_type: "Declare",
      name: "x",
      data_type: "int",
      value: {
        node_type: "BinaryOp",
        op: "+",
        left: { node_type: "Number", value: 2 },
        right: {
          node_type: "BinaryOp",
          op: "*",
          left: { node_type: "Number", value: 3 },
          right: { node_type: "Number", value: 4 },
        },
      },
    },
    {
      node_type: "Print",
      value: { node_type: "Variable", name: "x" },
    },
  ],
};

function ASTNode({ name, value }) {
  if (Array.isArray(value)) {
    return (
      <div className="ast-children">
        {value.map((item, index) => (
          <ASTNode
            key={`${name}-${index}`}
            name={`${name}[${index}]`}
            value={item}
          />
        ))}
      </div>
    );
  }

  if (value && typeof value === "object") {
    const nodeType = value.node_type || "Object";

    return (
      <div className="ast-node">
        <div className="ast-node-title">
          <span className="ast-type">{nodeType}</span>
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

function App() {
  const [showJSON, setShowJSON] = React.useState(false);

  return (
    <main>
      <div className="eyebrow">EXPLAINABLE COMPILER</div>
      <h1>AST Explorer</h1>
      <p className="intro">
        Explore how source code becomes a structured syntax tree.
        Each node represents a language construct or expression.
      </p>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <h2>Abstract Syntax Tree</h2>
            <p className="muted">
              Demo AST for: int x = 2 + 3 * 4; print x;
            </p>
          </div>
          <button onClick={() => setShowJSON(!showJSON)}>
            {showJSON ? "Show tree" : "Show JSON"}
          </button>
        </div>

        {showJSON ? (
          <pre>{JSON.stringify(sampleAST, null, 2)}</pre>
        ) : (
          <div className="ast-tree">
            <ASTNode name="root" value={sampleAST} />
          </div>
        )}
      </section>

      <footer>
        Explainable Compiler · AST visualization prototype
      </footer>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
