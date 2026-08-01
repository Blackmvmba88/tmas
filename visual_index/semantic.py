from __future__ import annotations

import colorsys
from typing import Any

from .presets import NEON_GLASS_THEME

FALLBACK = {
    "canvas": "#090b11", "surface": "#151a2a", "surface-raised": "#202740",
    "text": "#f5f7ff", "text-muted": "#9da8c1", "border": "#29314a",
    "accent": "#2fe0b6", "accent-secondary": "#8d7bff", "danger": "#ff5c7a",
    "warning": "#ffc857", "success": "#2fe0b6",
}


def parse_hex(value: str) -> tuple[int, int, int] | None:
    raw = value.strip().lstrip("#")
    if len(raw) in {3, 4}:
        raw = "".join(char * 2 for char in raw[:3])
    elif len(raw) in {6, 8}:
        raw = raw[:6]
    else:
        return None
    try:
        return tuple(int(raw[index:index + 2], 16) for index in (0, 2, 4))  # type: ignore[return-value]
    except ValueError:
        return None


def canonical_hex(value: str) -> str | None:
    rgb = parse_hex(value)
    return None if rgb is None else "#{:02x}{:02x}{:02x}".format(*rgb)


def relative_luminance(value: str) -> float:
    rgb = parse_hex(value)
    if rgb is None:
        raise ValueError(f"unsupported color: {value}")
    channels = []
    for channel in rgb:
        normalized = channel / 255
        channels.append(normalized / 12.92 if normalized <= 0.04045 else ((normalized + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(first: str, second: str) -> float:
    high, low = sorted((relative_luminance(first), relative_luminance(second)), reverse=True)
    return round((high + 0.05) / (low + 0.05), 2)


def _saturation(value: str) -> float:
    rgb = parse_hex(value)
    if rgb is None:
        return 0.0
    return colorsys.rgb_to_hsv(*(channel / 255 for channel in rgb))[1]


def _mix(first: str, second: str, weight: float) -> str:
    a = parse_hex(first)
    b = parse_hex(second)
    if a is None or b is None:
        raise ValueError("mix only supports hex colors")
    result = tuple(round(a[index] * (1 - weight) + b[index] * weight) for index in range(3))
    return "#{:02x}{:02x}{:02x}".format(*result)


def _observed_hex(data: dict[str, Any]) -> list[dict[str, Any]]:
    observed: dict[str, dict[str, Any]] = {}
    for entry in data["visual_system"]["colors"].get("hex", []):
        value = canonical_hex(entry["value"])
        if value is None:
            continue
        current = observed.setdefault(value, {"value": value, "count": 0, "locations": []})
        current["count"] += entry["count"]
        current["locations"] = sorted(set(current["locations"]) | set(entry["locations"]))[:20]
    return sorted(observed.values(), key=lambda item: (-item["count"], item["value"]))


def _select_palette(observed: list[dict[str, Any]]) -> dict[str, str]:
    if not observed:
        return {**FALLBACK, "light-canvas": "#ffffff", "light-text": "#111318"}
    values = [entry["value"] for entry in observed]
    darkest = min(values, key=relative_luminance)
    lightest = max(values, key=relative_luminance)
    chromatic = sorted(
        values,
        key=lambda value: (_saturation(value), next(e["count"] for e in observed if e["value"] == value)),
        reverse=True,
    )
    accent = chromatic[0] if chromatic and _saturation(chromatic[0]) >= 0.25 else FALLBACK["accent"]
    secondary = next((value for value in chromatic[1:] if contrast_ratio(value, accent) > 1.25), FALLBACK["accent-secondary"])
    dark_canvas = darkest if relative_luminance(darkest) <= 0.12 else FALLBACK["canvas"]
    light_text = lightest if contrast_ratio(lightest, dark_canvas) >= 4.5 else FALLBACK["text"]
    light_canvas = lightest if relative_luminance(lightest) >= 0.75 else "#ffffff"
    dark_text = darkest if contrast_ratio(darkest, light_canvas) >= 4.5 else "#111318"
    return {
        "canvas": dark_canvas, "surface": _mix(dark_canvas, "#ffffff", 0.08),
        "surface-raised": _mix(dark_canvas, "#ffffff", 0.14), "text": light_text,
        "text-muted": _mix(light_text, dark_canvas, 0.35), "border": _mix(dark_canvas, "#ffffff", 0.18),
        "accent": accent, "accent-secondary": secondary, "danger": FALLBACK["danger"],
        "warning": FALLBACK["warning"], "success": accent,
        "light-canvas": light_canvas, "light-text": dark_text,
    }


def _ensure_contrast(foreground: str, background: str, target: float) -> str:
    if contrast_ratio(foreground, background) >= target:
        return foreground
    destination = "#000000" if relative_luminance(background) > 0.45 else "#ffffff"
    for step in range(1, 21):
        candidate = _mix(foreground, destination, step / 20)
        if contrast_ratio(candidate, background) >= target:
            return candidate
    return destination


def _normalize_theme(tokens: dict[str, str]) -> dict[str, str]:
    normalized = dict(tokens)
    normalized["text"] = _ensure_contrast(normalized["text"], normalized["canvas"], 4.5)
    normalized["text-muted"] = _ensure_contrast(normalized["text-muted"], normalized["canvas"], 4.5)
    normalized["accent"] = _ensure_contrast(normalized["accent"], normalized["canvas"], 3.0)
    normalized["accent-secondary"] = _ensure_contrast(normalized["accent-secondary"], normalized["canvas"], 3.0)
    return normalized


def _theme_audit(name: str, tokens: dict[str, str]) -> dict[str, Any]:
    checks = []
    for foreground, background, threshold in (
        ("text", "canvas", 4.5), ("text", "surface", 4.5),
        ("text-muted", "canvas", 4.5), ("accent", "canvas", 3.0),
        ("accent-secondary", "canvas", 3.0),
    ):
        ratio = contrast_ratio(tokens[foreground], tokens[background])
        checks.append({
            "foreground": foreground, "background": background, "ratio": ratio,
            "threshold": threshold, "pass": ratio >= threshold,
        })
    return {
        "theme": name, "checks": checks,
        "passed": sum(1 for check in checks if check["pass"]),
        "failed": sum(1 for check in checks if not check["pass"]),
    }


def build_semantic_system(data: dict[str, Any]) -> dict[str, Any]:
    observed = _observed_hex(data)
    selected = _select_palette(observed)
    blackmamba = {key: selected.get(key, value) for key, value in FALLBACK.items()}
    dark = dict(blackmamba)
    light = {
        "canvas": selected["light-canvas"], "surface": _mix(selected["light-canvas"], "#000000", 0.035),
        "surface-raised": "#ffffff", "text": selected["light-text"],
        "text-muted": _mix(selected["light-text"], selected["light-canvas"], 0.38),
        "border": _mix(selected["light-canvas"], "#000000", 0.16), "accent": selected["accent"],
        "accent-secondary": selected["accent-secondary"], "danger": FALLBACK["danger"],
        "warning": "#8a5a00", "success": "#087f5b",
    }
    high_contrast = {
        "canvas": "#000000", "surface": "#000000", "surface-raised": "#111111",
        "text": "#ffffff", "text-muted": "#ffffff", "border": "#ffffff",
        "accent": "#00ffff", "accent-secondary": "#ffff00", "danger": "#ff6680",
        "warning": "#ffff00", "success": "#00ff88",
    }
    themes = {
        name: _normalize_theme(tokens)
        for name, tokens in {
            "light": light,
            "dark": dark,
            "blackmamba": blackmamba,
            "blackmamba-neon-glass": dict(NEON_GLASS_THEME),
            "high-contrast": high_contrast,
        }.items()
    }
    audits = [_theme_audit(name, tokens) for name, tokens in themes.items()]
    return {
        "schema_version": 1,
        "source": "inferred from scanned literals plus reviewable BlackMamba presets; generated files never modify source code",
        "observed_palette": [
            {**entry, "luminance": round(relative_luminance(entry["value"]), 4), "saturation": round(_saturation(entry["value"]), 4)}
            for entry in observed
        ],
        "themes": themes,
        "accessibility": {
            "standard": "WCAG contrast thresholds: 4.5 normal text, 3.0 large text/UI",
            "themes": audits, "all_required_checks_pass": all(audit["failed"] == 0 for audit in audits),
        },
        "motion": {
            "duration-fast": "120ms", "duration-normal": "220ms", "duration-slow": "360ms",
            "easing-standard": "cubic-bezier(0.2, 0, 0, 1)",
            "easing-emphasized": "cubic-bezier(0.2, 0, 0, 1.4)",
            "reduced-motion-duration": "1ms",
        },
    }


def render_theme_css(system: dict[str, Any]) -> str:
    blocks = ["/* Generated by BlackMamba Visual Index. Review before adoption. */"]
    for name, tokens in system["themes"].items():
        selector = ":root" if name == "blackmamba" else f'[data-theme="{name}"]'
        lines = [f"{selector} {{"]
        lines.extend(f"  --bm-{key}: {value};" for key, value in tokens.items())
        lines.extend(f"  --bm-{key}: {value};" for key, value in system["motion"].items())
        lines.append("}")
        blocks.append("\n".join(lines))
    blocks.append("""@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: var(--bm-reduced-motion-duration) !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: var(--bm-reduced-motion-duration) !important;
  }
}""")
    return "\n\n".join(blocks) + "\n"
