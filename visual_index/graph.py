from __future__ import annotations

import posixpath
from pathlib import PurePosixPath
from typing import Any

RESOLVABLE_EXTENSIONS = (
    "", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".css", ".scss",
    ".sass", ".less", ".vue", ".svelte", ".astro", ".json",
)
INDEX_NAMES = tuple(f"index{extension}" for extension in RESOLVABLE_EXTENSIONS if extension)


def _resolve(source: str, reference: str, known: set[str]) -> str | None:
    clean = reference.split("?", 1)[0].split("#", 1)[0]
    if not clean.startswith("."):
        return None
    parent = str(PurePosixPath(source).parent)
    base = posixpath.normpath(posixpath.join(parent, clean))
    candidates = [base + extension for extension in RESOLVABLE_EXTENSIONS]
    candidates.extend(posixpath.join(base, name) for name in INDEX_NAMES)
    return next((candidate for candidate in candidates if candidate in known), None)


def build_dependency_graph(data: dict[str, Any]) -> dict[str, Any]:
    files = {item["path"]: item for item in data["files"]}
    known = set(files)
    incoming = {path: 0 for path in known}
    outgoing = {path: 0 for path in known}
    internal_edges: list[dict[str, str]] = []
    external_edges: list[dict[str, str]] = []

    for source, references in data["visual_system"].get("imports", {}).items():
        for reference in references:
            target = _resolve(source, reference, known)
            if target:
                internal_edges.append({"source": source, "target": target, "reference": reference})
                outgoing[source] += 1
                incoming[target] += 1
            else:
                external_edges.append({"source": source, "package": reference})

    nodes = []
    for path, item in files.items():
        score = incoming[path] * 3 + outgoing[path]
        if "theme_or_tokens" in item["roles"]:
            score += 8
        if "global_or_entry" in item["roles"]:
            score += 5
        nodes.append({
            "path": path,
            "category": item["category"],
            "roles": item["roles"],
            "incoming": incoming[path],
            "outgoing": outgoing[path],
            "impact_score": score,
        })
    nodes.sort(key=lambda item: (-item["impact_score"], item["path"]))

    packages: dict[str, int] = {}
    for edge in external_edges:
        package = edge["package"]
        if package.startswith("@"):
            package = "/".join(package.split("/")[:2])
        else:
            package = package.split("/", 1)[0]
        packages[package] = packages.get(package, 0) + 1

    return {
        "schema_version": 1,
        "summary": {
            "nodes": len(nodes),
            "internal_edges": len(internal_edges),
            "external_edges": len(external_edges),
            "external_packages": len(packages),
        },
        "hotspots": nodes[:30],
        "nodes": nodes,
        "internal_edges": internal_edges,
        "external_dependencies": [
            {"package": package, "references": count}
            for package, count in sorted(packages.items(), key=lambda item: (-item[1], item[0]))
        ],
    }


def render_dot(graph: dict[str, Any]) -> str:
    lines = [
        "digraph visual_system {",
        '  graph [rankdir="LR", bgcolor="transparent"];',
        '  node [shape="box", style="rounded"];',
    ]
    active = {edge["source"] for edge in graph["internal_edges"]} | {
        edge["target"] for edge in graph["internal_edges"]
    }
    for node in graph["nodes"]:
        if node["path"] in active:
            label = node["path"].replace('"', '\\"')
            lines.append(f'  "{label}" [label="{label}\\nimpact={node["impact_score"]}"];')
    for edge in graph["internal_edges"]:
        source = edge["source"].replace('"', '\\"')
        target = edge["target"].replace('"', '\\"')
        lines.append(f'  "{source}" -> "{target}";')
    lines.append("}")
    return "\n".join(lines) + "\n"
