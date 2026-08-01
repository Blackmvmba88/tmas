#!/usr/bin/env python3
"""Serve BlackMamba UI Lab over loopback HTTP without external dependencies."""

from __future__ import annotations

import argparse
import contextlib
import os
import sys
import threading
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

DEFAULT_PORT = 8770


class QuietHandler(SimpleHTTPRequestHandler):
    """Static handler with concise request logging."""

    def log_message(self, format: str, *args: object) -> None:
        sys.stdout.write(f"[ui-lab] {format % args}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve BlackMamba UI Lab on localhost.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Loopback port (default: {DEFAULT_PORT})")
    parser.add_argument("--no-open", action="store_true", help="Do not open the browser automatically")
    return parser


def validate_port(port: int) -> int:
    if not 1024 <= port <= 65535:
        raise ValueError("port must be between 1024 and 65535")
    return port


def main() -> int:
    args = build_parser().parse_args()
    try:
        port = validate_port(args.port)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parent / "ui-lab"
    index = root / "index.html"
    if not index.is_file():
        print(f"error: UI Lab assets not found at {root}", file=sys.stderr)
        return 2

    handler = partial(QuietHandler, directory=str(root))
    url = f"http://127.0.0.1:{port}/"

    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError as error:
        print(f"error: cannot bind {url}: {error}", file=sys.stderr)
        print(f"try: python3 serve-ui-lab.py --port {port + 1}", file=sys.stderr)
        return 1

    print("BlackMamba UI Component Lab")
    print(url)
    print("Press Ctrl+C to stop.")

    if not args.no_open:
        timer = threading.Timer(0.35, lambda: webbrowser.open(url, new=2))
        timer.daemon = True
        timer.start()

    try:
        server.serve_forever(poll_interval=0.25)
    except KeyboardInterrupt:
        print("\n[ui-lab] stopping")
    finally:
        with contextlib.suppress(Exception):
            server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
