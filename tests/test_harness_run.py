import os
import sys

# Add the project root directory to Python's module path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from harness.runner import BenchmarkHarness

def test_benchmark():
    print("Initializing Benchmark Harness...")
    sample_path = "tests/samples/basic.expr"
    
    # Ensure sample folder exists and write a test expression
    os.makedirs(os.path.dirname(sample_path), exist_ok=True)
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write("x = 10 + 20\nprint(x)\n")

    # Instantiate the harness
    harness = BenchmarkHarness(source_path=sample_path)
    
    # Measure execution of a test python command
    metrics = harness.measure_execution("python -c \"print(30)\"")
    
    print("\n--- Benchmark Results ---")
    print(f"Success: {metrics.get('success')}")
    print(f"Runtime: {metrics.get('runtime_ms')} ms")
    print(f"File Size: {metrics.get('file_size_bytes')} bytes")
    print(f"Stdout: {metrics.get('stdout').strip()}")

if __name__ == "__main__":
    test_benchmark()
    