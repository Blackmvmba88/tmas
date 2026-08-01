from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .baseline import compare_baselines, inventory_baseline, load_manifest
from .catalog import DEFAULT_EXCLUDES
from .change_impact import git_changed_paths
from .corner_bloom import enhance_neon_glass_demo, render_corner_bloom_css
from .pixel_diff import compare_pixel_baselines
from .presets import build_neon_glass_preset, render_neon_glass_css, render_neon_glass_demo
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
    parser.add_argument("--check", action="store_true", help="Exit non-zero when visual policy checks fail")
    parser.add_argument("--git-base", help="Analyze changed-file impact against a Git ref, for example origin/main")
    parser.add_argument("--changed", action="append", default=[], help="Explicit changed path; repeatable")
    parser.add_argument("--baseline-dir", help="Current screenshot directory to inventory and compare")
    parser.add_argument("--compare-baseline", help="Previous baseline-manifest.json to compare")
    parser.add_argument("--previous-baseline-dir", help="Previous screenshot directory for real pixel comparison")
    parser.add_argument(
        "--pixel-threshold",
        type=int,
        default=16,
        help="Minimum per-channel difference counted as a changed pixel (0-255)",
    )
    parser.add_argument(
        "--max-diff-ratio",
        type=float,
        default=0.01,
        help="Maximum changed-pixel ratio accepted per screenshot (0.0-1.0)",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _resolve_from_root(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else root / path


def _write_neon_glass_artifacts(output: Path) -> None:
    preset = build_neon_glass_preset()
    demo = enhance_neon_glass_demo(render_neon_glass_demo(preset))
    (output / "blackmamba-neon-glass.json").write_text(
        json.dumps(preset, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (output / "blackmamba-neon-glass.css").write_text(
        render_neon_glass_css(preset),
        encoding="utf-8",
    )
    (output / "blackmamba-neon-glass-corner-bloom.css").write_text(
        render_corner_bloom_css(),
        encoding="utf-8",
    )
    (output / "blackmamba-neon-glass-demo.html").write_text(
        demo,
        encoding="utf-8",
    )


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.project).expanduser().resolve()
    if not root.is_dir():
        print(f"error: project directory does not exist: {root}", file=sys.stderr)
        return 2
    if not 0 <= args.pixel_threshold <= 255:
        print("error: --pixel-threshold must be between 0 and 255", file=sys.stderr)
        return 2
    if not 0.0 <= args.max_diff_ratio <= 1.0:
        print("error: --max-diff-ratio must be between 0.0 and 1.0", file=sys.stderr)
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

    current_dir = _resolve_from_root(root, args.baseline_dir)
    previous_dir = _resolve_from_root(root, args.previous_baseline_dir)
    baseline_manifest = inventory_baseline(current_dir)
    previous_manifest = None
    previous_path = _resolve_from_root(root, args.compare_baseline)
    if previous_path:
        try:
            previous_manifest = load_manifest(previous_path)
        except (OSError, ValueError) as error:
            data["diagnostics"]["baseline_manifest_error"] = str(error)
            print(f"[visual-index] baseline warning: {error}", file=sys.stderr)
    elif previous_dir:
        previous_manifest = inventory_baseline(previous_dir)

    baseline_diff = compare_baselines(previous_manifest, baseline_manifest)
    pixel_diff = compare_pixel_baselines(
        previous_manifest=previous_manifest,
        current_manifest=baseline_manifest,
        previous_dir=previous_dir,
        current_dir=current_dir,
        artifact_dir=output / "pixel-diffs",
        pixel_threshold=args.pixel_threshold,
        max_diff_ratio=args.max_diff_ratio,
    )

    write_reports(
        data,
        output,
        changed_paths=changed_paths,
        baseline_manifest=baseline_manifest,
        baseline_diff=baseline_diff,
        pixel_diff=pixel_diff,
    )
    _write_neon_glass_artifacts(output)

    risks = (
        data["derived"]["change_plan"]["risk"],
        data["derived"]["change_impact"]["risk"],
        data["derived"]["baseline_diff"]["risk"],
        data["derived"]["pixel_diff"]["risk"],
    )
    risk = max(risks, key=lambda item: item["score"])
    pixel_failures = (
        pixel_diff["summary"]["failed"]
        + pixel_diff["summary"]["dimension_mismatches"]
        + pixel_diff["summary"]["errors"]
    )
    print(f"[visual-index] indexed {len(data['files'])} files · risk {risk['level']} ({risk['score']}/100)")
    for filename in (
        "visual-index.html", "VISUAL_INDEX.md", "visual-index.json", "semantic-tokens.json",
        "themes.css", "accessibility-audit.json", "dependency-graph.json", "MIGRATION_PLAN.md",
        "visual-regression-plan.json", "visual-regression.spec.ts", "playwright.visual.config.ts",
        "VISUAL_REGRESSION.md", "change-impact.json", "CHANGE_IMPACT.md",
        "baseline-manifest.json", "baseline-diff.json", "BASELINE.md",
        "pixel-diff.json", "PIXEL_DIFF.md", "PR_VISUAL_SUMMARY.md", "run-visual-baseline.sh",
        "blackmamba-neon-glass.json", "blackmamba-neon-glass.css",
        "blackmamba-neon-glass-corner-bloom.css", "blackmamba-neon-glass-demo.html",
    ):
        print(f"[visual-index] generated: {output / filename}")
    if pixel_diff["enabled"]:
        print(
            "[visual-index] pixel diff: "
            f"{pixel_diff['summary']['passed']} passed · "
            f"{pixel_diff['summary']['unchanged']} unchanged · "
            f"{pixel_failures} require review"
        )
    if args.open:
        if sys.platform == "darwin":
            subprocess.run(["open", str(output / "visual-index.html")], check=False)
        else:
            print("[visual-index] --open is currently available on macOS", file=sys.stderr)
    if args.check and pixel_diff["enabled"] and pixel_failures:
        print("[visual-index] pixel comparison threshold failed", file=sys.stderr)
        return 1
    if args.check and risk["level"] == "critical":
        print("[visual-index] critical visual risk detected", file=sys.stderr)
        return 1
    return 0