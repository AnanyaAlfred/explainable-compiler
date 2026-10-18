import React from 'react';
import ReactDOM from 'react-dom/client';
import './style.css'; // Make sure style.css is imported!

function App() {
  return (
    <main>
      <div className="eyebrow">COMPILER PASS VISUALIZER</div>
      <h1>Explainable Compiler</h1>
      <p className="intro">
        Track step-by-step optimizations, inspect intermediate code transformations, and analyze performance benchmarks in real-time.
      </p>

      <section className="panel">
        <h2>Side-by-Side Diff Viewer</h2>
        <p>Original vs Optimized code differences will be highlighted here.</p>
      </section>

      <section className="panel">
        <h2>5-Question Explanation Log</h2>
        <p>Interactive timeline detailing WHAT, WHERE, WHY, HOW, and EFFECT for each optimization pass.</p>
      </section>

      <footer>
        Explainable Compiler Project &bull; Built with Vite & React
      </footer>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);