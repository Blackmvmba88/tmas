from __future__ import annotations

import collections
import datetime as dt
import hashlib
import os
import re
from pathlib import Path
from typing import Any, Iterable

from .catalog import (
    ASSET_EXTENSIONS, CATEGORY_EXTENSIONS, COLOR_PATTERNS, CSS_VAR_DEF,
    CSS_VAR_USE, FONT_EXTENSIONS, FRAMEWORK_PATTERNS, IMPORT_RE, KEYFRAMES,
    MOTION_DECLARATION, PRIORITY_NAMES, TEXT_EXTENSIONS,
)


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _skip(path: Path, root: Path, excludes: set[str], include_hidden: bool) -> bool:
    for part in path.relative_to(root).parts:
        if part in excludes or (not include_hidden and part.startswith(".")):
            return True
    return False


def _walk(root: Path, excludes: set[str], include_hidden: bool) -> Iterable[Path]:
    for current, directories, filenames in os.walk(root):
        current_path = Path(current)
        directories[:] = [
            name for name in directories
            if not _skip(current_path / name, root, excludes, include_hidden)
        ]
        for name in filenames:
            path = current_path / name
            if not _skip(path, root, excludes, include_hidden):
                yield path


def _read(path: Path, limit: int) -> str | None:
    try:
        if path.stat().st_size > limit:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _digest(path: Path, limit: int = 5_000_000) -> str | None:
    try:
        if path.stat().st_size > limit:
            return None
        hasher = hashlib.sha1()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1_048_576), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return None


def _category(path: Path) -> str:
    extension = path.suffix.lower()
    if extension in ASSET_EXTENSIONS:
        return "assets"
    if extension in FONT_EXTENSIONS:
        return "fonts"
    for category, extensions in CATEGORY_EXTENSIONS.items():
        if extension in extensions:
            return category
    return "other"


def _roles(relative_path: str, filename: str, text: str | None) -> list[str]:
    lower = relative_path.lower()
    stem = Path(filename).stem.lower()
    roles: set[str] = set()
    if filename in PRIORITY_NAMES:
        roles.add("priority")
    if any(value in lower for value in ("/theme", "/themes", "theme.", "/tokens", "token.", "design-system")):
        roles.add("theme_or_tokens")
    if any(value in stem for value in ("global", "root", "app", "layout", "theme", "token", "palette")):
        roles.add("global_or_entry")
    if any(value in lower for value in ("/components/", "/ui/", "/views/", "/screens/", "/pages/", "/app/")):
        roles.add("ui_surface")
    if any(value in lower for value in ("/assets/", "/images/", "/icons/", "/fonts/", "/public/", "/static/")):
        roles.add("asset_source")
    if text:
        if ":root" in text or "[data-theme" in text or ".dark" in text:
            roles.add("theme_scope")
        if KEYFRAMES.search(text):
            roles.add("animation_source")
        if CSS_VAR_DEF.search(text):
            roles.add("token_definition")
    return sorted(roles)


def scan_project(root: Path, max_file_bytes: int, excludes: set[str], include_hidden: bool) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    frameworks: collections.Counter[str] = collections.Counter()
    colors = {kind: collections.Counter() for kind in COLOR_PATTERNS}
    color_locations: dict[str, list[str]] = collections.defaultdict(list)
    variable_definitions: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    variable_uses: collections.Counter[str] = collections.Counter()
    keyframes: dict[str, list[str]] = collections.defaultdict(list)
    motion_files: collections.Counter[str] = collections.Counter()
    imports: dict[str, list[str]] = {}
    skipped_large: list[str] = []
    unreadable: list[str] = []

    for path in _walk(root, excludes, include_hidden):
        relative_path = _relative(path, root)
        try:
            info = path.stat()
        except OSError:
            unreadable.append(relative_path)
            continue

        extension = path.suffix.lower()
        category = _category(path)
        is_text = extension in TEXT_EXTENSIONS or path.name in PRIORITY_NAMES
        text = _read(path, max_file_bytes) if is_text else None
        if is_text and text is None and info.st_size > max_file_bytes:
            skipped_large.append(relative_path)

        record: dict[str, Any] = {
            "path": relative_path,
            "name": path.name,
            "extension": extension,
            "category": category,
            "size_bytes": info.st_size,
            "modified_at": dt.datetime.fromtimestamp(info.st_mtime).isoformat(timespec="seconds"),
            "roles": _roles(relative_path, path.name, text),
        }
        if category in {"assets", "fonts"}:
            record["sha1"] = _digest(path)

        if text is not None:
            record["line_count"] = text.count("\n") + 1
            for framework, patterns in FRAMEWORK_PATTERNS.items():
                hits = sum(len(re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)) for pattern in patterns)
                if hits:
                    frameworks[framework] += hits
            literal_count = 0
            for kind, pattern in COLOR_PATTERNS.items():
                for value in pattern.findall(text):
                    normalized = re.sub(r"\s+", " ", value.strip()).lower()
                    colors[kind][normalized] += 1
                    literal_count += 1
                    if len(color_locations[normalized]) < 20:
                        color_locations[normalized].append(relative_path)
            if literal_count:
                record["color_literal_count"] = literal_count
            for name, value in CSS_VAR_DEF.findall(text):
                variable_definitions[name].append({"path": relative_path, "value": value.strip()})
            variable_uses.update(CSS_VAR_USE.findall(text))
            for name in KEYFRAMES.findall(text):
                keyframes[name].append(relative_path)
            declaration_count = len(MOTION_DECLARATION.findall(text))
            if declaration_count:
                motion_files[relative_path] += declaration_count
                record["motion_declaration_count"] = declaration_count
            found_imports = sorted(set(IMPORT_RE.findall(text)))
            if found_imports:
                imports[relative_path] = found_imports[:200]
        files.append(record)

    categories = collections.Counter(item["category"] for item in files)
    roles = collections.Counter(role for item in files for role in item["roles"])
    hashes: dict[str, list[str]] = collections.defaultdict(list)
    for item in files:
        if item.get("sha1"):
            hashes[item["sha1"]].append(item["path"])
    duplicates = [{"sha1": digest, "paths": paths} for digest, paths in hashes.items() if len(paths) > 1]
    priority_files = sorted(
        (item for item in files if item["roles"]),
        key=lambda item: (
            "priority" not in item["roles"],
            "theme_or_tokens" not in item["roles"],
            "global_or_entry" not in item["roles"],
            item["path"],
        ),
    )
    color_total = sum(sum(counter.values()) for counter in colors.values())
    unique_colors = sum(len(counter) for counter in colors.values())
    undefined_variables = sorted(set(variable_uses) - set(variable_definitions))

    recommendations: list[dict[str, str]] = []
    if color_total:
        recommendations.append({
            "level": "high" if unique_colors > 20 else "medium",
            "title": "Centralize color literals",
            "detail": f"Found {color_total} usages across {unique_colors} unique color literals.",
        })
    if undefined_variables:
        recommendations.append({
            "level": "high", "title": "Resolve undefined CSS variables",
            "detail": f"{len(undefined_variables)} variables are used without a scanned definition.",
        })
    if keyframes or motion_files:
        recommendations.append({
            "level": "medium", "title": "Create a motion policy",
            "detail": "Standardize duration, easing and reduced-motion behavior before expanding animation.",
        })
    if duplicates:
        recommendations.append({
            "level": "low", "title": "Deduplicate visual assets",
            "detail": f"Found {len(duplicates)} groups of byte-identical assets.",
        })

    return {
        "summary": {
            "categories": dict(categories.most_common()),
            "roles": dict(roles.most_common()),
            "frameworks": dict(frameworks.most_common()),
            "color_usage_total": color_total,
            "unique_color_literals": unique_colors,
            "css_variables_defined": len(variable_definitions),
            "css_variables_used": len(variable_uses),
            "keyframes": len(keyframes),
            "motion_declarations": sum(motion_files.values()),
            "duplicate_asset_groups": len(duplicates),
        },
        "priority_files": priority_files,
        "files": sorted(files, key=lambda item: item["path"]),
        "visual_system": {
            "colors": {
                kind: [
                    {"value": value, "count": count, "locations": color_locations[value]}
                    for value, count in counter.most_common()
                ] for kind, counter in colors.items()
            },
            "css_variables": {
                "definitions": dict(sorted(variable_definitions.items())),
                "usage_counts": dict(variable_uses.most_common()),
                "used_but_not_defined": undefined_variables,
                "defined_but_not_used": sorted(set(variable_definitions) - set(variable_uses)),
            },
            "motion": {"keyframes": dict(sorted(keyframes.items())), "files": dict(motion_files.most_common())},
            "imports": dict(sorted(imports.items())),
            "duplicate_assets": duplicates,
        },
        "recommendations": recommendations,
        "diagnostics": {"large_text_files_skipped": skipped_large, "unreadable_files": unreadable},
    }
