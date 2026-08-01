from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

from . import __version__
from .catalog import DEFAULT_EXCLUDES
from .render import write_reports
from .scanner import scan_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a read-only index of a project's visual system.")
    parser.add_argument("project", nargs="?", default=".", help="Project directory")
    parser.add_argument("-o", "--output", default=".visual-index", help="Output directory")
    parser.add_argument("--max-file-mb", type=float, default=2.0, help="Largest text file to inspect")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden paths")
    parser.add_argument("--exclude", action="append", default=[], help="Extra directory name to exclude")
    parser.add_argument("--open", action="store_true", help="Open HTML dashboard on macOS")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"error: project directory does not exist: {root}", file=sys.stderr)
        return 2
    output = Path(args.output).expanduser()
    if not output.is_absolute():
        output = root / output
    print(f"[visual-index] scanning: {root}")
    data = scan_project(
        root=root,
        max_file_bytes=max(1, int(args.max_file_mb * 1_048_576)),
        excludes=DEFAULT_EXCLUDES | set(args.exclude),
        include_hidden=args.include_hidden,
    )
    data["meta"] = {
        "tool": "BlackMamba Visual Index", "version": __version__,
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "project_root": str(root), "file_count": len(data["files"]),
        "excluded_directories": sorted(DEFAULT_EXCLUDES | set(args.exclude)),
    }
    write_reports(data, output)
    print(f"[visual-index] indexed {len(data['files'])} files")
    print(f"[visual-index] dashboard: {output / 'visual-index.html'}")
    print(f"[visual-index] machine data: {output / 'visual-index.json'}")
    if args.open:
        if sys.platform == "darwin":
            subprocess.run(["open", str(output / "visual-index.html")], check=False)
        else:
            print("[visual-index] --open is currently available on macOS", file=sys.stderr)
    return 0
