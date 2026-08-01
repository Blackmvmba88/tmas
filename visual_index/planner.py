from __future__ import annotations

from typing import Any


def build_change_plan(data: dict[str, Any], semantic: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    summary = data["summary"]
    high = sum(1 for item in data["recommendations"] if item["level"] == "high")
    medium = sum(1 for item in data["recommendations"] if item["level"] == "medium")
    failed_contrast = sum(audit["failed"] for audit in semantic["accessibility"]["themes"])
    risk_score = min(
        100,
        high * 20
        + medium * 8
        + min(summary["unique_color_literals"], 30)
        + min(summary["motion_declarations"], 20)
        + failed_contrast * 5,
    )
    risk = "critical" if risk_score >= 75 else "high" if risk_score >= 50 else "medium" if risk_score >= 25 else "low"
    token_files = [
        item["path"] for item in data["priority_files"]
        if "theme_or_tokens" in item["roles"] or "token_definition" in item["roles"]
    ]
    global_files = [
        item["path"] for item in data["priority_files"]
        if "global_or_entry" in item["roles"] or "theme_scope" in item["roles"]
    ]
    visual_surfaces = [
        item["path"] for item in data["priority_files"]
        if "ui_surface" in item["roles"] or "visual_test_surface" in item["roles"]
    ]
    return {
        "risk": {"score": risk_score, "level": risk},
        "entry_points": {
            "token_files": token_files[:50],
            "global_files": global_files[:50],
            "visual_surfaces": visual_surfaces[:100],
            "dependency_hotspots": graph["hotspots"][:20],
        },
        "phases": [
            {
                "id": 1,
                "name": "Baseline",
                "actions": ["Commit generated index", "Capture current screenshots", "Freeze visual acceptance routes"],
            },
            {
                "id": 2,
                "name": "Token contract",
                "actions": ["Review semantic-tokens.json", "Name tokens by purpose, not raw color", "Map existing variables and literals"],
            },
            {
                "id": 3,
                "name": "Theme integration",
                "actions": ["Import themes.css in one global entry", "Adopt BlackMamba theme first", "Validate light, dark and high-contrast variants"],
            },
            {
                "id": 4,
                "name": "Component migration",
                "actions": ["Start with dependency hotspots", "Replace literals incrementally", "Keep component APIs stable"],
            },
            {
                "id": 5,
                "name": "Motion system",
                "actions": ["Normalize duration/easing tokens", "Add prefers-reduced-motion", "Test animation loss does not block interaction"],
            },
            {
                "id": 6,
                "name": "Visual verification",
                "actions": ["Run contrast checks", "Compare screenshots", "Fail CI on unexplained visual diffs"],
            },
        ],
    }


def render_migration_plan(plan: dict[str, Any]) -> str:
    lines = [
        "# Visual Migration Plan",
        "",
        f"**Risk:** {plan['risk']['level'].upper()} ({plan['risk']['score']}/100)",
        "",
        "## Entry points",
        "",
    ]
    for label, values in plan["entry_points"].items():
        lines.append(f"### {label.replace('_', ' ').title()}")
        if not values:
            lines.append("- None detected")
        else:
            for value in values:
                if isinstance(value, dict):
                    lines.append(f"- `{value['path']}` — impact {value['impact_score']}")
                else:
                    lines.append(f"- `{value}`")
        lines.append("")
    lines.extend(["## Execution phases", ""])
    for phase in plan["phases"]:
        lines.append(f"### {phase['id']}. {phase['name']}")
        lines.extend(f"- [ ] {action}" for action in phase["actions"])
        lines.append("")
    return "\n".join(lines)
