from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
        if len(header) >= 24 and header[:8] == PNG_SIGNATURE and header[12:16] == b"IHDR":
            return struct.unpack(">II", header[16:24])
    except OSError:
        return None
    return None


def inventory_baseline(directory: Path | None) -> dict[str, Any]:
    if directory is None:
        return {
            "schema_version": 1,
            "source_dir": None,
            "exists": False,
            "files": [],
            "summary": {"files": 0, "bytes": 0},
        }
    root = directory.expanduser().resolve()
    files: list[dict[str, Any]] = []
    if root.is_dir():
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SCREENSHOT_EXTENSIONS:
                continue
            dimensions = _png_dimensions(path)
            files.append({
                "path": path.relative_to(root).as_posix(),
                "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "width": dimensions[0] if dimensions else None,
                "height": dimensions[1] if dimensions else None,
            })
    return {
        "schema_version": 1,
        "source_dir": str(root),
        "exists": root.is_dir(),
        "files": files,
        "summary": {
            "files": len(files),
            "bytes": sum(item["size_bytes"] for item in files),
        },
    }


def load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.expanduser().read_text(encoding="utf-8"))


def compare_baselines(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    old = {item["path"]: item for item in (previous or {}).get("files", [])}
    new = {item["path"]: item for item in current.get("files", [])}
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    changed = sorted(
        path for path in set(old) & set(new)
        if old[path].get("sha256") != new[path].get("sha256")
    )
    unchanged = sorted(
        path for path in set(old) & set(new)
        if old[path].get("sha256") == new[path].get("sha256")
    )
    score = min(100, len(removed) * 15 + len(changed) * 5 + len(added) * 2)
    level = "critical" if score >= 75 else "high" if score >= 50 else "medium" if score >= 25 else "low"
    return {
        "schema_version": 1,
        "has_previous": previous is not None,
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "unchanged": len(unchanged),
        },
        "risk": {"score": score, "level": level},
        "added": [{"path": path, "current": new[path]} for path in added],
        "removed": [{"path": path, "previous": old[path]} for path in removed],
        "changed": [
            {"path": path, "previous": old[path], "current": new[path]}
            for path in changed
        ],
        "unchanged": unchanged,
    }


def render_baseline_markdown(manifest: dict[str, Any], diff: dict[str, Any]) -> str:
    lines = [
        "# Visual Baseline", "",
        f"**Directory:** `{manifest.get('source_dir') or 'not supplied'}`", "",
        f"**Screenshots:** {manifest['summary']['files']}", "",
        f"**Diff risk:** {diff['risk']['level'].upper()} ({diff['risk']['score']}/100)", "",
        "## Comparison", "",
        "| State | Count |", "|---|---:|",
        f"| Added | {diff['summary']['added']} |",
        f"| Removed | {diff['summary']['removed']} |",
        f"| Changed | {diff['summary']['changed']} |",
        f"| Unchanged | {diff['summary']['unchanged']} |", "",
    ]
    for label in ("added", "removed", "changed"):
        lines.extend([f"## {label.title()}", ""])
        entries = diff[label]
        if entries:
            lines.extend(f"- `{entry['path']}`" for entry in entries)
        else:
            lines.append("- None")
        lines.append("")
    return "\n".join(lines)


def render_pr_visual_summary(data: dict[str, Any]) -> str:
    derived = data["derived"]
    migration = derived["change_plan"]["risk"]
    change = derived["change_impact"]["risk"]
    baseline = derived["baseline_diff"]
    pixel = derived["pixel_diff"]
    regression = derived["visual_regression"]
    pixel_failures = (
        pixel["summary"]["failed"]
        + pixel["summary"]["dimension_mismatches"]
        + pixel["summary"]["errors"]
    )
    lines = [
        "# PR Visual Summary", "",
        "| Signal | Result |", "|---|---|",
        f"| Migration risk | {migration['level']} ({migration['score']}/100) |",
        f"| Changed-file risk | {change['level']} ({change['score']}/100) |",
        f"| Baseline diff risk | {baseline['risk']['level']} ({baseline['risk']['score']}/100) |",
        f"| Pixel diff risk | {pixel['risk']['level']} ({pixel['risk']['score']}/100) |",
        f"| Routes discovered | {len(regression['routes'])} |",
        f"| Planned captures | {regression['capture_count']} |",
        f"| Pixel comparisons | {pixel['summary']['compared']} |",
        f"| Pixel comparisons passed | {pixel['summary']['passed'] + pixel['summary']['unchanged']} |",
        f"| Pixel comparisons requiring review | {pixel_failures} |",
        f"| Maximum changed-pixel ratio | {pixel['summary']['maximum_changed_ratio']:.6f} |",
        f"| Changed screenshots | {baseline['summary']['changed']} |",
        f"| Added screenshots | {baseline['summary']['added']} |",
        f"| Removed screenshots | {baseline['summary']['removed']} |", "",
        "## Changed paths", "",
    ]
    paths = derived["change_impact"]["changed_paths"]
    lines.extend(f"- `{path}`" for path in paths) if paths else lines.append("- None supplied")

    failed_items = [item for item in pixel["results"] if not item.get("passes", False)]
    if failed_items:
        lines += ["", "## Pixel differences requiring review", ""]
        for item in failed_items:
            evidence = item.get("heatmap_image") or item.get("diff_image") or "no artifact"
            lines.append(
                f"- `{item['path']}` — {item['status']} · "
                f"ratio `{item.get('changed_ratio', 'n/a')}` · `{evidence}`"
            )
    return "\n".join(lines) + "\n"
