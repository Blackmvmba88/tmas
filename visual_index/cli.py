from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

from . import __version__
from .baseline import compare_baselines, inventory_baseline, load_manifest
from .catalog import DEFAULT_EXCLUDES
from .change_impact import git_changed_paths
from .render import write_reports
from .scanner import scan_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a visual-system control map for a software project.")
    parser.add_argument("project", nargs="?", default=".", help="Project directory")
    parser.add_argument("-o", "--output", default=".visual-index", help="Output directory")
    parser.add_argument("--max-file-mb", type=float, default=2.0, help="Largest text file to inspect")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden paths")
    parser.add_argument("--exclude", action="append", default=[], help="Extra directory name to exclude")
    parser.add_argument("--open", action="store_true", help="Open HTML dashboard on macOS")
    parser.add_argument("--check", action="store_true", help="Exit non-zero when critical visual risks are detected")
    parser.add_argument("--git-base", help="Analyze changed-file impact against a Git ref, for example origin/main")
    parser.add_argument("--changed", action="append", default=[], help="Explicit changed path; repeatable")
    parser.add_argument("--baseline-dir", help="Screenshot directory to inventory")
    parser.add_argument("--compare-baseline", help="Previous baseline-manifest.json to compare")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _resolve_from_root(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else root / path


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"error: project directory does not exist: {root}", file=sys.stderr)
        return 2
    output = Path(args.output).expanduser()
    if not output.is_absolute():
        output = root / output
    excludes = DEFAULT_EXCLUDES | set(args.exclude)
    print(f"[visual-index] scanning: {root}")
    data = scan_project(
        root=root,
        max_file_bytes=max(1, int(args.max_file_mb * 1_048_576)),
        excludes=excludes,
        include_hidden=args.include_hidden,
    )
    data["meta"] = {
        "tool": "BlackMamba Visual Index",
        "version": __version__,
        "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "project_root": str(root),
        "file_count": len(data["files"]),
        "excluded_directories": sorted(excludes),
    }

    changed_paths = list(args.changed)
    if args.git_base:
        discovered, git_error = git_changed_paths(root, args.git_base)
        changed_paths.extend(discovered)
        if git_error:
            data["diagnostics"]["git_diff_error"] = git_error
            print(f"[visual-index] git diff warning: {git_error}", file=sys.stderr)
    changed_paths = sorted(set(changed_paths))

    baseline_dir = _resolve_from_root(root, args.baseline_dir)
    baseline_manifest = inventory_baseline(baseline_dir)
    previous_manifest = None
    previous_path = _resolve_from_root(root, args.compare_baseline)
    if previous_path:
        try:
            previous_manifest = load_manifest(previous_path)
        except (OSError, ValueError) as error:
            data["diagnostics"]["baseline_manifest_error"] = str(error)
            print(f"[visual-index] baseline warning: {error}", file=sys.stderr)
    baseline_diff = compare_baselines(previous_manifest, baseline_manifest)

    write_reports(
        data,
        output,
        changed_paths=changed_paths,
        baseline_manifest=baseline_manifest,
        baseline_diff=baseline_diff,
    )
    risks = (
        data["derived"]["change_plan"]["risk"],
        data["derived"]["change_impact"]["risk"],
        data["derived"]["baseline_diff"]["risk"],
    )
    risk = max(risks, key=lambda item: item["score"])
    print(f"[visual-index] indexed {len(data['files'])} files · risk {risk['level']} ({risk['score']}/100)")
    for filename in (
        "visual-index.html", "VISUAL_INDEX.md", "visual-index.json", "semantic-tokens.json",
        "themes.css", "accessibility-audit.json", "dependency-graph.json", "MIGRATION_PLAN.md",
        "visual-regression-plan.json", "visual-regression.spec.ts", "playwright.visual.config.ts",
        "VISUAL_REGRESSION.md", "change-impact.json", "CHANGE_IMPACT.md",
        "baseline-manifest.json", "baseline-diff.json", "BASELINE.md",
        "PR_VISUAL_SUMMARY.md", "run-visual-baseline.sh",
    ):
        print(f"[visual-index] generated: {output / filename}")
    if args.open:
        if sys.platform == "darwin":
            subprocess.run(["open", str(output / "visual-index.html")], check=False)
        else:
            print("[visual-index] --open is currently available on macOS", file=sys.stderr)
    if args.check and risk["level"] == "critical":
        print("[visual-index] critical visual risk detected", file=sys.stderr)
        return 1
    return 0
