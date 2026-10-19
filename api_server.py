
"""Minimal HTTP API for the Explainable Compiler frontend."""

import json
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from compiler.pipeline import compile_source


class CompilerHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "http://localhost:5173")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json(200, {"ok": True})

    def do_POST(self):
        if self.path != "/compile":
            self.send_json(404, {"error": "Endpoint not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1_000_000:
                self.send_json(400, {"error": "Provide source code under 1 MB."})
                return

            request = json.loads(self.rfile.read(length))
            source = request.get("source")

            if not isinstance(source, str) or not source.strip():
                self.send_json(400, {"error": "Enter some source code first."})
                return

            result = compile_source(source)
            self.send_json(200, result)

        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "Invalid JSON request."})
        except Exception as exc:
            traceback.print_exc()
            self.send_json(500, {
                "error": f"{type(exc).__name__}: {repr(exc)}"
            })

    def log_message(self, format, *args):
        print("[API]", format % args)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), CompilerHandler)
    print("Compiler API running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping compiler API.")
    finally:
        server.server_close()
