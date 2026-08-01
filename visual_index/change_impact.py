from __future__ import annotations

import subprocess
from collections import deque
from pathlib import Path
from typing import Any


def git_changed_paths(root: Path, base: str) -> tuple[list[str], str | None]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()}), None
    except (OSError, subprocess.CalledProcessError) as error:
        return [], str(error)


def build_change_impact(data: dict[str, Any], graph: dict[str, Any], changed_paths: list[str]) -> dict[str, Any]:
    nodes = {node["path"]: node for node in graph["nodes"]}
    reverse: dict[str, set[str]] = {}
    for edge in graph["internal_edges"]:
        reverse.setdefault(edge["target"], set()).add(edge["source"])

    impacted = {path for path in changed_paths if path in nodes}
    distance = {path: 0 for path in impacted}
    queue = deque(impacted)
    while queue:
        target = queue.popleft()
        if distance[target] >= 3:
            continue
        for dependent in reverse.get(target, set()):
            if dependent not in distance:
                distance[dependent] = distance[target] + 1
                impacted.add(dependent)
                queue.append(dependent)

    impacted_nodes = [{**nodes[path], "distance": distance[path]} for path in impacted]
    impacted_nodes.sort(key=lambda item: (item["distance"], -item["impact_score"], item["path"]))
    direct_score = sum(nodes[path]["impact_score"] for path in changed_paths if path in nodes)
    roles = sorted({role for item in impacted_nodes for role in item["roles"]})
    score = min(
        100,
        direct_score
        + len(impacted_nodes) * 3
        + (20 if "theme_or_tokens" in roles else 0)
        + (15 if "global_or_entry" in roles else 0),
    )
    level = "critical" if score >= 75 else "high" if score >= 50 else "medium" if score >= 25 else "low"
    unknown = sorted(set(changed_paths) - set(nodes))
    return {
        "schema_version": 1,
        "changed_paths": changed_paths,
        "unknown_paths": unknown,
        "risk": {"score": score, "level": level},
        "impacted_files": impacted_nodes,
        "impacted_roles": roles,
    }


def render_change_impact_markdown(impact: dict[str, Any]) -> str:
    lines = [
        "# Visual Change Impact", "",
        f"**Risk:** {impact['risk']['level'].upper()} ({impact['risk']['score']}/100)", "",
        "## Changed files", "",
    ]
    lines.extend(f"- `{path}`" for path in impact["changed_paths"] or ["No changed paths supplied"])
    lines += [
        "", "## Impacted files", "",
        "| File | Distance | Impact | Roles |", "|---|---:|---:|---|",
    ]
    for item in impact["impacted_files"]:
        lines.append(
            f"| `{item['path']}` | {item['distance']} | {item['impact_score']} | {', '.join(item['roles'])} |"
        )
    if not impact["impacted_files"]:
        lines.append("| _None resolved_ | | | |")
    if impact["unknown_paths"]:
        lines += ["", "## Unresolved changed paths", ""]
        lines.extend(f"- `{path}`" for path in impact["unknown_paths"])
    return "\n".join(lines) + "\n"
