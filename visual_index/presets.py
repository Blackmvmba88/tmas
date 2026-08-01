from __future__ import annotations

import html
import json
from typing import Any

NEON_GLASS_THEME: dict[str, str] = {
    "canvas": "#120824",
    "surface": "#17141f",
    "surface-raised": "#211b2d",
    "text": "#f7f1ff",
    "text-muted": "#b9afc8",
    "border": "#ffb45c",
    "accent": "#ffb45c",
    "accent-secondary": "#8b67ff",
    "danger": "#ff5c7a",
    "warning": "#ffd27a",
    "success": "#63f2c1",
}

NEON_GLASS_EFFECTS: dict[str, str] = {
    "radius-panel": "34px",
    "radius-control": "999px",
    "radius-action": "999px",
    "border-width": "2px",
    "backdrop-blur": "18px",
    "panel-opacity": "0.92",
    "glow-amber-soft": "0 0 10px rgba(255, 180, 92, 0.62)",
    "glow-amber-strong": "0 0 18px rgba(255, 180, 92, 0.88), 0 0 42px rgba(255, 132, 64, 0.42)",
    "glow-violet": "0 0 14px rgba(139, 103, 255, 0.58)",
    "inner-highlight": "inset 0 1px 0 rgba(255, 255, 255, 0.08)",
    "control-height": "54px",
    "action-size": "58px",
    "toggle-width": "58px",
    "toggle-height": "32px",
    "focus-ring": "0 0 0 3px rgba(139, 103, 255, 0.32), 0 0 20px rgba(139, 103, 255, 0.58)",
}


def build_neon_glass_preset() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "name": "BlackMamba Neon Glass",
        "slug": "blackmamba-neon-glass",
        "source": "voice-player visual reference translated into reviewable semantic tokens",
        "theme": dict(NEON_GLASS_THEME),
        "effects": dict(NEON_GLASS_EFFECTS),
        "states": {
            "idle": {
                "label": "Just start talking",
                "border_glow": "glow-amber-soft",
                "waveform_activity": 0.18,
                "action_emphasis": "quiet",
            },
            "recording": {
                "label": "Hold to record",
                "border_glow": "glow-amber-strong",
                "waveform_activity": 1.0,
                "action_emphasis": "armed",
            },
            "ready-to-send": {
                "label": "Release to send",
                "border_glow": "glow-amber-strong",
                "waveform_activity": 0.55,
                "action_emphasis": "primary",
            },
        },
        "components": {
            "voice-panel": {
                "description": "Dark translucent panel with a continuous amber perimeter glow.",
                "tokens": [
                    "canvas", "surface", "border", "radius-panel", "border-width",
                    "backdrop-blur", "glow-amber-strong", "inner-highlight",
                ],
            },
            "microphone-toggle": {
                "description": "Pill control with white thumb and restrained inactive contrast.",
                "tokens": [
                    "surface-raised", "text-muted", "radius-control", "toggle-width",
                    "toggle-height", "inner-highlight",
                ],
            },
            "waveform": {
                "description": "Centered white waveform with state-driven amplitude.",
                "tokens": ["text", "control-height"],
            },
            "primary-action": {
                "description": "Circular violet send control with luminous ring and directional glyph.",
                "tokens": [
                    "accent-secondary", "radius-action", "action-size", "glow-violet",
                    "focus-ring",
                ],
            },
        },
        "principles": [
            "Use amber glow for structural emphasis and active boundaries.",
            "Use violet for actions, focus and directional intent.",
            "Keep content surfaces nearly black so the glow remains legible.",
            "Prefer broad radii and quiet interior contrast over excessive decoration.",
            "Disable pulsing and waveform animation under reduced motion.",
        ],
    }


def render_neon_glass_css(preset: dict[str, Any]) -> str:
    theme = preset["theme"]
    effects = preset["effects"]
    lines = [
        "/* Generated BlackMamba Neon Glass preset. Review before adoption. */",
        '[data-theme="blackmamba-neon-glass"] {',
    ]
    lines.extend(f"  --bm-{key}: {value};" for key, value in theme.items())
    lines.extend(f"  --bm-{key}: {value};" for key, value in effects.items())
    lines.append("}")
    lines.append("")
    lines.append('@media (prefers-reduced-motion: reduce) {')
    lines.append('  [data-theme="blackmamba-neon-glass"] * {')
    lines.append("    animation-duration: 1ms !important;")
    lines.append("    transition-duration: 1ms !important;")
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_neon_glass_demo(preset: dict[str, Any]) -> str:
    theme = preset["theme"]
    effects = preset["effects"]
    variables = {
        **{f"color-{key}": value for key, value in theme.items()},
        **effects,
    }
    css_variables = "\n".join(
        f"      --bm-{html.escape(key)}: {html.escape(value)};"
        for key, value in variables.items()
    )
    preset_json = html.escape(json.dumps(preset["states"], ensure_ascii=False))
    return f'''<!doctype html>
<html lang="en" data-theme="blackmamba-neon-glass">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>BlackMamba Neon Glass</title>
  <style>
    :root {{
{css_variables}
      color-scheme: dark;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      min-height: 100vh;
      margin: 0;
      display: grid;
      place-items: center;
      color: var(--bm-color-text);
      background:
        radial-gradient(circle at 50% 15%, rgba(102, 44, 166, .24), transparent 38%),
        linear-gradient(180deg, #1b0b36 0%, var(--bm-color-canvas) 58%, #090711 100%);
    }}
    .stage {{ width: min(900px, 92vw); padding: 56px; }}
    .headline {{ text-align: center; margin-bottom: 28px; }}
    .headline small {{ color: var(--bm-color-accent); font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }}
    .headline h1 {{ margin: 8px 0 0; font-size: clamp(34px, 7vw, 72px); line-height: .95; letter-spacing: -.05em; }}
    .panel {{
      min-height: 260px;
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 24px;
      padding: 34px;
      border: var(--bm-border-width) solid var(--bm-color-border);
      border-radius: var(--bm-radius-panel);
      background: rgba(23, 20, 31, var(--bm-panel-opacity));
      box-shadow: var(--bm-glow-amber-strong), var(--bm-inner-highlight);
      backdrop-filter: blur(var(--bm-backdrop-blur));
    }}
    .copy {{ align-self: center; max-width: 420px; }}
    .copy p {{ margin: 0; color: var(--bm-color-text-muted); }}
    .copy strong {{ display: block; margin-bottom: 10px; color: var(--bm-color-text); font-size: 24px; }}
    .controls {{ display: flex; align-items: center; gap: 14px; flex-wrap: wrap; justify-content: flex-end; }}
    .mic-control {{
      height: var(--bm-control-height);
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 8px 12px 8px 18px;
      border: 1px solid rgba(255,255,255,.12);
      border-radius: var(--bm-radius-control);
      color: var(--bm-color-text-muted);
      background: rgba(21, 18, 29, .82);
      box-shadow: var(--bm-inner-highlight);
    }}
    .toggle {{
      position: relative;
      width: var(--bm-toggle-width);
      height: var(--bm-toggle-height);
      border: 0;
      border-radius: var(--bm-radius-control);
      background: rgba(255,255,255,.11);
      cursor: pointer;
    }}
    .toggle::after {{
      content: "";
      position: absolute;
      width: 24px;
      height: 24px;
      left: 4px;
      top: 4px;
      border-radius: 50%;
      background: #fff;
      transition: transform 180ms ease, box-shadow 180ms ease;
    }}
    .toggle[aria-pressed="true"] {{ background: rgba(139,103,255,.54); }}
    .toggle[aria-pressed="true"]::after {{ transform: translateX(26px); box-shadow: var(--bm-glow-violet); }}
    .waveform {{ height: 48px; display: flex; align-items: center; gap: 4px; padding: 0 8px; }}
    .waveform i {{ width: 3px; border-radius: 99px; background: var(--bm-color-text); opacity: .92; animation: pulse 900ms ease-in-out infinite alternate; }}
    .waveform i:nth-child(1), .waveform i:nth-child(9) {{ height: 8px; }}
    .waveform i:nth-child(2), .waveform i:nth-child(8) {{ height: 16px; }}
    .waveform i:nth-child(3), .waveform i:nth-child(7) {{ height: 27px; }}
    .waveform i:nth-child(4), .waveform i:nth-child(6) {{ height: 38px; }}
    .waveform i:nth-child(5) {{ height: 46px; }}
    .action {{
      width: var(--bm-action-size);
      height: var(--bm-action-size);
      display: grid;
      place-items: center;
      border-radius: var(--bm-radius-action);
      border: 2px solid rgba(139,103,255,.86);
      color: var(--bm-color-accent-secondary);
      background: rgba(29, 24, 42, .78);
      box-shadow: var(--bm-glow-violet), var(--bm-inner-highlight);
      cursor: pointer;
      font-size: 25px;
    }}
    .action:focus-visible, .toggle:focus-visible {{ outline: 0; box-shadow: var(--bm-focus-ring); }}
    .meta {{ margin-top: 22px; text-align: center; color: var(--bm-color-text-muted); font-size: 13px; }}
    @keyframes pulse {{ from {{ transform: scaleY(.62); opacity: .64; }} to {{ transform: scaleY(1); opacity: 1; }} }}
    @media (prefers-reduced-motion: reduce) {{ .waveform i {{ animation: none; }} }}
    @media (max-width: 760px) {{ .stage {{ padding: 24px; }} .panel {{ align-items: stretch; flex-direction: column; }} .controls {{ justify-content: flex-start; }} }}
  </style>
</head>
<body>
  <main class="stage" data-states="{preset_json}">
    <header class="headline">
      <small>BlackMamba voice interface</small>
      <h1>Just start talking</h1>
    </header>
    <section class="panel">
      <div class="copy">
        <strong>Hold to record</strong>
        <p>Amber structural glow, near-black glass, restrained typography and a violet action state.</p>
      </div>
      <div class="controls">
        <label class="mic-control">Mic <button class="toggle" type="button" aria-pressed="false" aria-label="Toggle microphone"></button></label>
        <div class="waveform" aria-label="Audio waveform"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
        <button class="action" type="button" aria-label="Send audio">➤</button>
      </div>
    </section>
    <p class="meta">Preset generated as a reviewable artifact. It does not modify application source.</p>
  </main>
  <script>
    const toggle = document.querySelector('.toggle');
    toggle.addEventListener('click', () => {
      toggle.setAttribute('aria-pressed', String(toggle.getAttribute('aria-pressed') !== 'true'));
    });
  </script>
</body>
</html>
'''
