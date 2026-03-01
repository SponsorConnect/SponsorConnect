#!/usr/bin/env python3
"""OFF AI backend (Python).

Provides:
- GET /api/submissions
- POST /api/submissions
- POST /api/save-html
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "submissions.json"
INDEX_FILE = ROOT / "index.html"


def read_data() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def write_data(rows: list[dict]) -> None:
    DATA_FILE.write_text(json.dumps(rows, indent=2), encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):  # noqa: N802
        if self.path == "/api/submissions":
            self._send_json(read_data())
            return
        self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length or 0)
        payload = json.loads(raw.decode("utf-8") or "{}") if raw else {}

        if self.path == "/api/submissions":
            rows = read_data()
            rows.append(payload)
            write_data(rows)
            self._send_json({"ok": True, "count": len(rows)})
            return

        if self.path == "/api/save-html":
            content = payload.get("content", "")
            INDEX_FILE.write_text(content, encoding="utf-8")
            self._send_json({"ok": True, "saved": str(INDEX_FILE.name)})
            return

        self._send_json({"error": "Not found"}, status=404)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8000), Handler)
    print("Python backend running on http://0.0.0.0:8000")
    server.serve_forever()
