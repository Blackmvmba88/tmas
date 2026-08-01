from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageOps, ImageStat, UnidentifiedImageError


def _manifest_map(manifest: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    return {item["path"]: item for item in (manifest or {}).get("files", [])}


def _source_dir(manifest: dict[str, Any] | None, explicit: Path | None) -> Path | None:
    if explicit is not None:
        return explicit.expanduser().resolve()
    value = (manifest or {}).get("source_dir")
    return Path(value).expanduser().resolve() if value else None


def _artifact_stem(path: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "__", path).strip("._-") or "image"
    digest = hashlib.sha1(path.encode("utf-8")).hexdigest()[:8]
    return f"{slug[:100]}--{digest}"


def _relative_artifact(path: Path, artifact_dir: Path) -> str:
    try:
        return path.relative_to(artifact_dir.parent).as_posix()
    except ValueError:
        return str(path)


def _compare_pair(
    previous_path: Path,
    current_path: Path,
    logical_path: str,
    artifact_dir: Path,
    pixel_threshold: int,
    max_diff_ratio: float,
) -> dict[str, Any]:
    try:
        with Image.open(previous_path) as previous_image, Image.open(current_path) as current_image:
            previous = previous_image.convert("RGB")
            current = current_image.convert("RGB")
    except (OSError, UnidentifiedImageError) as error:
        return {
            "path": logical_path,
            "status": "error",
            "passes": False,
            "error": str(error),
        }

    if previous.size != current.size:
        return {
            "path": logical_path,
            "status": "dimension_mismatch",
            "passes": False,
            "previous_size": {"width": previous.width, "height": previous.height},
            "current_size": {"width": current.width, "height": current.height},
            "changed_pixels": None,
            "changed_ratio": 1.0,
        }

    difference = ImageChops.difference(previous, current)
    red, green, blue = difference.split()
    maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    total_pixels = previous.width * previous.height
    changed_pixels = sum(1 for value in maximum.getdata() if value > pixel_threshold)
    changed_ratio = changed_pixels / total_pixels if total_pixels else 0.0
    maximum_delta = maximum.getextrema()[1]
    mean_delta = float(ImageStat.Stat(maximum).mean[0])
    bbox = maximum.getbbox()

    status = "unchanged" if changed_pixels == 0 else "pass" if changed_ratio <= max_diff_ratio else "fail"
    result: dict[str, Any] = {
        "path": logical_path,
        "status": status,
        "passes": status in {"unchanged", "pass"},
        "width": previous.width,
        "height": previous.height,
        "total_pixels": total_pixels,
        "changed_pixels": changed_pixels,
        "changed_ratio": round(changed_ratio, 8),
        "mean_channel_delta": round(mean_delta, 4),
        "maximum_channel_delta": maximum_delta,
        "bounding_box": (
            {"left": bbox[0], "top": bbox[1], "right": bbox[2], "bottom": bbox[3]}
            if bbox else None
        ),
    }

    if changed_pixels:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        stem = _artifact_stem(logical_path)
        diff_path = artifact_dir / f"{stem}.diff.png"
        heatmap_path = artifact_dir / f"{stem}.heatmap.png"

        normalized = ImageOps.autocontrast(difference)
        normalized.save(diff_path, format="PNG")

        mask = maximum.point(lambda value: 255 if value > pixel_threshold else 0)
        darkened = Image.blend(current, Image.new("RGB", current.size, "black"), 0.55).convert("RGBA")
        red_overlay = Image.new("RGBA", current.size, (255, 40, 30, 0))
        red_overlay.putalpha(mask)
        heatmap = Image.alpha_composite(darkened, red_overlay)
        heatmap.save(heatmap_path, format="PNG")

        result["diff_image"] = _relative_artifact(diff_path, artifact_dir)
        result["heatmap_image"] = _relative_artifact(heatmap_path, artifact_dir)

    return result


def compare_pixel_baselines(
    previous_manifest: dict[str, Any] | None,
    current_manifest: dict[str, Any],
    artifact_dir: Path,
    previous_dir: Path | None = None,
    current_dir: Path | None = None,
    pixel_threshold: int = 16,
    max_diff_ratio: float = 0.01,
) -> dict[str, Any]:
    pixel_threshold = max(0, min(255, int(pixel_threshold)))
    max_diff_ratio = max(0.0, min(1.0, float(max_diff_ratio)))
    previous_root = _source_dir(previous_manifest, previous_dir)
    current_root = _source_dir(current_manifest, current_dir)
    old = _manifest_map(previous_manifest)
    new = _manifest_map(current_manifest)
    common = sorted(set(old) & set(new))

    diagnostics: list[str] = []
    if previous_manifest is None:
        diagnostics.append("No previous baseline manifest was supplied.")
    if previous_root is None or not previous_root.is_dir():
        diagnostics.append("Previous screenshot directory is unavailable.")
    if current_root is None or not current_root.is_dir():
        diagnostics.append("Current screenshot directory is unavailable.")

    enabled = previous_manifest is not None and previous_root is not None and previous_root.is_dir() and current_root is not None and current_root.is_dir()
    results: list[dict[str, Any]] = []
    if enabled:
        for logical_path in common:
            previous_path = previous_root / logical_path
            current_path = current_root / logical_path
            if not previous_path.is_file() or not current_path.is_file():
                results.append({
                    "path": logical_path,
                    "status": "error",
                    "passes": False,
                    "error": "Screenshot file is missing from one of the resolved directories.",
                })
                continue
            results.append(
                _compare_pair(
                    previous_path,
                    current_path,
                    logical_path,
                    artifact_dir,
                    pixel_threshold,
                    max_diff_ratio,
                )
            )

    passed = sum(1 for item in results if item["status"] == "pass")
    unchanged = sum(1 for item in results if item["status"] == "unchanged")
    failed = sum(1 for item in results if item["status"] == "fail")
    dimension_mismatches = sum(1 for item in results if item["status"] == "dimension_mismatch")
    errors = sum(1 for item in results if item["status"] == "error")
    changed_pixels = sum(item.get("changed_pixels") or 0 for item in results)
    total_pixels = sum(item.get("total_pixels") or 0 for item in results)
    aggregate_ratio = changed_pixels / total_pixels if total_pixels else 0.0
    maximum_ratio = max((item.get("changed_ratio") or 0.0 for item in results), default=0.0)

    score = min(
        100,
        failed * 20
        + dimension_mismatches * 30
        + errors * 25
        + round(maximum_ratio * 100),
    )
    level = "critical" if score >= 75 else "high" if score >= 50 else "medium" if score >= 25 else "low"

    return {
        "schema_version": 1,
        "enabled": enabled,
        "thresholds": {
            "pixel_channel_delta": pixel_threshold,
            "maximum_changed_ratio": max_diff_ratio,
        },
        "directories": {
            "previous": str(previous_root) if previous_root else None,
            "current": str(current_root) if current_root else None,
            "artifacts": str(artifact_dir),
        },
        "summary": {
            "common_images": len(common),
            "compared": len(results),
            "passed": passed,
            "unchanged": unchanged,
            "failed": failed,
            "dimension_mismatches": dimension_mismatches,
            "errors": errors,
            "changed_pixels": changed_pixels,
            "total_pixels": total_pixels,
            "aggregate_changed_ratio": round(aggregate_ratio, 8),
            "maximum_changed_ratio": round(maximum_ratio, 8),
        },
        "risk": {"score": score, "level": level},
        "diagnostics": diagnostics,
        "results": results,
    }


def render_pixel_diff_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Pixel Difference Report", "",
        f"**Enabled:** {report['enabled']}", "",
        f"**Risk:** {report['risk']['level'].upper()} ({report['risk']['score']}/100)", "",
        "## Thresholds", "",
        f"- Per-channel delta: `{report['thresholds']['pixel_channel_delta']}`",
        f"- Maximum changed ratio: `{report['thresholds']['maximum_changed_ratio']:.4f}`", "",
        "## Summary", "",
        "| Metric | Value |", "|---|---:|",
        f"| Images compared | {summary['compared']} |",
        f"| Passed | {summary['passed']} |",
        f"| Unchanged | {summary['unchanged']} |",
        f"| Failed | {summary['failed']} |",
        f"| Dimension mismatches | {summary['dimension_mismatches']} |",
        f"| Errors | {summary['errors']} |",
        f"| Changed pixels | {summary['changed_pixels']} |",
        f"| Aggregate changed ratio | {summary['aggregate_changed_ratio']:.6f} |",
        f"| Maximum changed ratio | {summary['maximum_changed_ratio']:.6f} |", "",
        "## Images", "",
        "| Screenshot | Status | Changed pixels | Ratio | Artifacts |",
        "|---|---|---:|---:|---|",
    ]
    for item in report["results"]:
        artifacts = ", ".join(
            f"`{item[key]}`" for key in ("diff_image", "heatmap_image") if item.get(key)
        )
        lines.append(
            f"| `{item['path']}` | {item['status']} | {item.get('changed_pixels', '')} | "
            f"{item.get('changed_ratio', '')} | {artifacts} |"
        )
    if not report["results"]:
        lines.append("| _No comparable images_ | | | | |")
    if report["diagnostics"]:
        lines += ["", "## Diagnostics", ""]
        lines.extend(f"- {message}" for message in report["diagnostics"])
    return "\n".join(lines) + "\n"
