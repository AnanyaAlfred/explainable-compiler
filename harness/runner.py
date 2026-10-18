import time
import os
import subprocess

class BenchmarkHarness:
    def __init__(self, source_path: str):
        self.source_path = source_path

    def measure_execution(self, command: str) -> dict:
        """Measures execution time and checks binary/output metrics."""
        start_time = time.time()
        
        # Get file size if applicable
        file_size_bytes = os.path.getsize(self.source_path) if os.path.exists(self.source_path) else 0
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True,
                timeout=5
            )
            end_time = time.time()
            runtime_ms = (end_time - start_time) * 1000

            return {
                "success": result.returncode == 0,
                "runtime_ms": round(runtime_ms, 4),
                "file_size_bytes": file_size_bytes,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            end_time = time.time()
            runtime_ms = (end_time - start_time) * 1000
            return {
                "success": False,
                "runtime_ms": round(runtime_ms, 4),
                "file_size_bytes": file_size_bytes,
                "stdout": "",
                "stderr": str(e)
            }

def evaluate(source_path: str, command: str) -> dict:
    """Convenience wrapper function required by test_compiler.py."""
    harness = BenchmarkHarness(source_path=source_path)
    return harness.measure_execution(command)