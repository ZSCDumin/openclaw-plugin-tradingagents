#!/usr/bin/env python3
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from tradingagents_runner import _analyze, _health


def _json_default(value: Any) -> str:
    return str(value)


class Handler(BaseHTTPRequestHandler):
    server_version = "TradingAgentsOpenClaw/0.1"

    def do_GET(self) -> None:
        if self.path.rstrip("/") == "/health":
            self._send(200, _health())
            return
        self._send(404, {"ok": False, "error": "Not found"})

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/run":
            self._send(404, {"ok": False, "error": "Not found"})
            return

        try:
            length = int(self.headers.get("content-length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            action = payload.get("action")
            if action == "health":
                self._send(200, _health())
                return
            if action == "analyze":
                self._send(200, _analyze(payload))
                return
            self._send(400, {"ok": False, "error": f"Unknown action: {action!r}"})
        except Exception as exc:
            self._send(500, {"ok": False, "error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send(self, status: int, body: dict[str, Any]) -> None:
        encoded = json.dumps(body, ensure_ascii=False, default=_json_default).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


def main() -> int:
    parser = argparse.ArgumentParser(description="TradingAgents local HTTP service for OpenClaw.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"TradingAgents service listening on http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
