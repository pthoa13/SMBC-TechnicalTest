"""Tiny OpenAI-compatible mock server for manual retry testing."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class MockOpenAIHandler(BaseHTTPRequestHandler):
    request_count = 0
    rate_limit_count = 1

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self._write_json(404, {"error": {"message": "Not found"}})
            return

        MockOpenAIHandler.request_count += 1
        request_number = MockOpenAIHandler.request_count

        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length:
            self.rfile.read(content_length)

        if request_number <= MockOpenAIHandler.rate_limit_count:
            self._write_json(
                429,
                {
                    "error": {
                        "message": "Mock rate limit. Retry this request.",
                        "type": "rate_limit_error",
                    }
                },
            )
            return

        self._write_json(
            200,
            {
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "content": json.dumps(
                                {
                                    "translations": {
                                        "es": "Resumen simulado despues de reintento.",
                                        "fr": "Resume simule apres nouvelle tentative.",
                                        "de": "Simulierte Zusammenfassung nach erneutem Versuch.",
                                    }
                                }
                            )
                        },
                    }
                ]
            },
        )

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")

    def _write_json(self, status_code: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local mock OpenAI-compatible server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--rate-limit-count", default=1, type=int)
    args = parser.parse_args()

    MockOpenAIHandler.request_count = 0
    MockOpenAIHandler.rate_limit_count = args.rate_limit_count

    server = ThreadingHTTPServer((args.host, args.port), MockOpenAIHandler)
    print(
        f"Mock OpenAI server listening at http://{args.host}:{args.port}/v1 "
        f"(429 responses before success: {args.rate_limit_count})"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Mock OpenAI server stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
