import time
import subprocess
import os

class BenchmarkHarness:
    def __init__(self, source_path: str):
        self.source_path = source_path

    def measure_execution(self, command: str) -> dict:
        """Measures execution time and checks binary/output metrics."""
        start_time = time.perf_counter()
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                shell=True, 
                timeout=5
            )
            end_time = time.perf_counter()
            runtime_ms = (end_time - start_time) * 1000

            # Get file size if applicable
            file_size_bytes = os.path.getsize(self.source_path) if os.path.exists(self.source_path) else 0

            return {
                "success": result.returncode == 0,
                "runtime_ms": round(runtime_ms, 4),
                "file_size_bytes": file_size_bytes,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timed out."
            }
    def evaluate(source_path: str, command: str) -> dict:
        """Convenience wrapper for BenchmarkHarness."""
        harness = BenchmarkHarness(source_path=source_path)
        return harness.measure_execution(command)    