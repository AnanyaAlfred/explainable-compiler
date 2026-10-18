
"""Benchmark harness and compiler evaluation compatibility."""

import os
import subprocess
import time


class BenchmarkHarness:
    def __init__(self, source_path: str):
        self.source_path = source_path

    def measure_execution(self, command: str) -> dict:
        """Measure command runtime and collect execution metrics."""
        start_time = time.perf_counter()

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True,
                timeout=5,
            )

            runtime_ms = (time.perf_counter() - start_time) * 1000
            file_size = (
                os.path.getsize(self.source_path)
                if os.path.exists(self.source_path)
                else 0
            )

            return {
                "success": result.returncode == 0,
                "runtime_ms": round(runtime_ms, 4),
                "file_size_bytes": file_size,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timed out.",
                "runtime_ms": (time.perf_counter() - start_time) * 1000,
                "file_size_bytes": (
                    os.path.getsize(self.source_path)
                    if os.path.exists(self.source_path)
                    else 0
                ),
                "stdout": "",
                "stderr": "Execution timed out.",
            }


def evaluate(source_path: str, command: str) -> dict:
    """Backward-compatible benchmark evaluation entry point."""
    return BenchmarkHarness(source_path).measure_execution(command)
