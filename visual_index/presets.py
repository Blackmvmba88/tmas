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
    "success": "#53d8ff",
}

NEON_GLASS_EFFECTS: dict[str, str] = {
    "mic-active": "#f2a13f",
    "send-idle": "#8b67ff",
    "send-active": "#53d8ff",
    "radius-panel": "36px",
    "radius-control": "999px",
    "radius-action": "999px",
    "border-width": "2px",
    "backdrop-blur": "18px",
    "panel-opacity": "0.94",
    "panel-max-width": "1180px",
    "panel-min-height": "164px",
    "panel-padding-x": "34px",
    "panel-padding-y": "28px",
    "glow-amber-soft": "0 0 10px rgba(255, 180, 92, 0.62)",
    "glow-amber-strong": "0 0 18px rgba(255, 180, 92, 0.88), 0 0 44px rgba(255, 132, 64, 0.44)",
    "glow-violet": "0 0 14px rgba(139, 103, 255, 0.58)",
    "glow-orange": "0 0 14px rgba(242, 161, 63, 0.52)",
    "glow-cyan": "0 0 14px rgba(83, 216, 255, 0.62)",
    "inner-highlight": "inset 0 1px 0 rgba(255, 255, 255, 0.08)",
    "control-height": "54px",
    "action-size": "58px",
    "toggle-width": "58px",
    "toggle-height": "32px",
    "focus-ring": "0 0 0 3px rgba(83, 216, 255, 0.28), 0 0 20px rgba(83, 216, 255, 0.54)",
}


def build_neon_glass_preset() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "name": "BlackMamba Neon Glass",
        "slug": "blackmamba-neon-glass",
        "source": "voice-player reference translated into reviewable semantic tokens",
        "theme": dict(NEON_GLASS_THEME),
        "effects": dict(NEON_GLASS_EFFECTS),
        "layout": {
            "composition": "mic | elastic waveform | send",
            "desktop_columns": "170px minmax(220px, 1fr) 76px",
            "panel_shape": "wide-low",
            "headline_alignment": "center",
            "helper_alignment": "center-below-panel",
        },
        "states": {
            "idle": {
                "headline": "Just start talking",
                "helper": "Hold to record",
                "mic_color": "neutral",
                "send_color": "send-idle",
                "border_glow": "glow-amber-soft",
                "waveform_activity": 0.18,
            },
            "recording": {
                "headline": "Just start talking",
                "helper": "Hold to record",
                "mic_color": "mic-active",
                "send_color": "send-active",
                "border_glow": "glow-amber-strong",
                "waveform_activity": 1.0,
            },
            "ready-to-send": {
                "headline": "Just start talking",
                "helper": "Release to send",
                "mic_color": "mic-active",
                "send_color": "send-active",
                "border_glow": "glow-amber-strong",
                "waveform_activity": 0.55,
            },
        },
        "components": {
            "voice-panel": {
                "description": "Wide, low, near-black glass panel with a continuous amber perimeter glow.",
                "tokens": [
                    "surface", "border", "panel-max-width", "panel-min-height",
                    "radius-panel", "border-width", "backdrop-blur",
                    "glow-amber-strong", "inner-highlight",
                ],
            },
            "microphone-toggle": {
                "description": "Left pill control; neutral while idle and orange while listening.",
                "tokens": [
                    "surface-raised", "text-muted", "mic-active", "radius-control",
                    "toggle-width", "toggle-height", "glow-orange",
                ],
            },
            "waveform": {
                "description": "Elastic centered white waveform occupying the flexible middle column.",
                "tokens": ["text", "control-height"],
            },
            "primary-action": {
                "description": "Right circular send control; violet while idle and cyan while active.",
                "tokens": [
                    "send-idle", "send-active", "radius-action", "action-size",
                    "glow-violet", "glow-cyan", "focus-ring",
                ],
            },
        },
        "principles": [
            "Amber defines structure, not action.",
            "Orange communicates an active microphone.",
            "Cyan communicates a ready send action.",
            "Violet communicates an available but idle action.",
            "Keep the panel wide, low and visually quiet inside the luminous boundary.",
            "Disable waveform motion under reduced motion.",
        ],
    }


def render_neon_glass_css(preset: dict[str, Any]) -> str:
    lines = [
        "/* Generated BlackMamba Neon Glass preset. Review before adoption. */",
        '[data-theme="blackmamba-neon-glass"] {',
    ]
    lines.extend(f"  --bm-{key}: {value};" for key, value in preset["theme"].items())
    lines.extend(f"  --bm-{key}: {value};" for key, value in preset["effects"].items())
    lines.extend([
        "}",
        "",
        '@media (prefers-reduced-motion: reduce) {',
        '  [data-theme="blackmamba-neon-glass"] * {',
        "    animation-duration: 1ms !important;",
        "    transition-duration: 1ms !important;",
        "  }",
        "}",
    ])
    return "\n".join(lines) + "\n"


def render_neon_glass_demo(preset: dict[str, Any]) -> str:
    variables = {
        **{f"color-{key}": value for key, value in preset["theme"].items()},
        **preset["effects"],
    }
    css_variables = "\n".join(
        f"      --bm-{html.escape(key)}: {html.escape(value)};"
        for key, value in variables.items()
    )
    states = html.escape(json.dumps(preset["states"], ensure_ascii=False), quote=True)
    bars = "".join("<i></i>" for _ in range(21))
    template = '''<!doctype html>
<html lang="en" data-theme="blackmamba-neon-glass">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>BlackMamba Neon Glass</title>
  <style>
    :root {
__CSS_VARIABLES__
      color-scheme: dark;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh;
      margin: 0;
      display: grid;
      place-items: center;
      color: var(--bm-color-text);
      background:
        radial-gradient(circle at 50% 12%, rgba(104, 43, 171, .25), transparent 40%),
        linear-gradient(180deg, #1a0a34 0%, var(--bm-color-canvas) 60%, #090711 100%);
    }
    .stage { width: min(1320px, 94vw); padding: 44px 20px; }
    .headline { text-align: center; margin-bottom: 28px; }
    .headline h1 { margin: 0; font-size: clamp(38px, 6vw, 72px); line-height: .95; letter-spacing: -.055em; }
    .voice-panel {
      width: 100%;
      max-width: var(--bm-panel-max-width);
      min-height: var(--bm-panel-min-height);
      margin: auto;
      display: grid;
      grid-template-columns: 170px minmax(220px, 1fr) 76px;
      align-items: end;
      gap: 28px;
      padding: var(--bm-panel-padding-y) var(--bm-panel-padding-x);
      border: var(--bm-border-width) solid var(--bm-color-border);
      border-radius: var(--bm-radius-panel);
      background: rgba(23, 20, 31, var(--bm-panel-opacity));
      box-shadow: var(--bm-glow-amber-soft), var(--bm-inner-highlight);
      backdrop-filter: blur(var(--bm-backdrop-blur));
      transition: box-shadow 180ms ease;
    }
    .voice-panel[data-state="recording"],
    .voice-panel[data-state="ready-to-send"] { box-shadow: var(--bm-glow-amber-strong), var(--bm-inner-highlight); }
    .mic-control {
      height: var(--bm-control-height);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 8px 10px 8px 18px;
      border: 1px solid rgba(255,255,255,.12);
      border-radius: var(--bm-radius-control);
      color: var(--bm-color-text-muted);
      background: rgba(21, 18, 29, .84);
      box-shadow: var(--bm-inner-highlight);
      font-size: 17px;
    }
    .toggle {
      position: relative;
      width: var(--bm-toggle-width);
      height: var(--bm-toggle-height);
      border: 0;
      border-radius: var(--bm-radius-control);
      background: rgba(255,255,255,.12);
      cursor: pointer;
      transition: background 180ms ease, box-shadow 180ms ease;
    }
    .toggle::after {
      content: "";
      position: absolute;
      width: 24px;
      height: 24px;
      left: 4px;
      top: 4px;
      border-radius: 50%;
      background: #fff;
      transition: transform 180ms ease;
    }
    .voice-panel[data-state="recording"] .toggle,
    .voice-panel[data-state="ready-to-send"] .toggle {
      background: var(--bm-mic-active);
      box-shadow: var(--bm-glow-orange);
    }
    .voice-panel[data-state="recording"] .toggle::after,
    .voice-panel[data-state="ready-to-send"] .toggle::after { transform: translateX(26px); }
    .waveform {
      min-width: 0;
      height: 52px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: clamp(3px, .55vw, 7px);
      overflow: hidden;
    }
    .waveform i {
      width: 3px;
      height: 7px;
      flex: 0 0 auto;
      border-radius: 99px;
      background: var(--bm-color-text);
      opacity: .92;
      transform-origin: center;
      animation: wave 820ms ease-in-out infinite alternate;
      animation-play-state: paused;
    }
    .waveform i:nth-child(3n) { animation-delay: -180ms; }
    .waveform i:nth-child(4n) { animation-delay: -360ms; }
    .waveform i:nth-child(5n) { animation-delay: -520ms; }
    .voice-panel[data-state="recording"] .waveform i,
    .voice-panel[data-state="ready-to-send"] .waveform i { animation-play-state: running; }
    .action {
      width: var(--bm-action-size);
      height: var(--bm-action-size);
      display: grid;
      place-items: center;
      justify-self: end;
      border-radius: var(--bm-radius-action);
      border: 2px solid var(--bm-send-idle);
      color: var(--bm-send-idle);
      background: rgba(29, 24, 42, .82);
      box-shadow: var(--bm-glow-violet), var(--bm-inner-highlight);
      cursor: pointer;
      font-size: 25px;
      transition: color 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
    }
    .voice-panel[data-state="recording"] .action,
    .voice-panel[data-state="ready-to-send"] .action {
      border-color: var(--bm-send-active);
      color: var(--bm-send-active);
      box-shadow: var(--bm-glow-cyan), var(--bm-inner-highlight);
    }
    .action:focus-visible, .toggle:focus-visible { outline: 0; box-shadow: var(--bm-focus-ring); }
    .helper { margin: 28px 0 0; text-align: center; color: var(--bm-color-text); font-size: 17px; }
    .hint { margin: 10px 0 0; text-align: center; color: var(--bm-color-text-muted); font-size: 13px; }
    @keyframes wave {
      from { height: 7px; opacity: .62; }
      to { height: 46px; opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) { .waveform i { animation: none; } }
    @media (max-width: 760px) {
      .stage { padding: 24px 12px; }
      .voice-panel { grid-template-columns: 1fr auto; align-items: center; }
      .waveform { grid-column: 1 / -1; grid-row: 1; }
      .mic-control { grid-column: 1; grid-row: 2; }
      .action { grid-column: 2; grid-row: 2; }
    }
  </style>
</head>
<body>
  <main class="stage" data-states="__STATES__">
    <header class="headline"><h1>Just start talking</h1></header>
    <section class="voice-panel" data-state="recording">
      <label class="mic-control">Mic <button class="toggle" type="button" aria-pressed="true" aria-label="Toggle microphone"></button></label>
      <div class="waveform" aria-label="Live audio waveform">__BARS__</div>
      <button class="action" type="button" aria-label="Send audio">➤</button>
    </section>
    <p class="helper">Hold to record</p>
    <p class="hint">Click Mic to cycle idle and recording. Click send to preview ready-to-send.</p>
  </main>
  <script>
    const panel = document.querySelector('.voice-panel');
    const toggle = document.querySelector('.toggle');
    const action = document.querySelector('.action');
    const helper = document.querySelector('.helper');
    toggle.addEventListener('click', () => {
      const active = panel.dataset.state === 'recording';
      panel.dataset.state = active ? 'idle' : 'recording';
      toggle.setAttribute('aria-pressed', String(!active));
      helper.textContent = 'Hold to record';
    });
    action.addEventListener('click', () => {
      panel.dataset.state = 'ready-to-send';
      toggle.setAttribute('aria-pressed', 'true');
      helper.textContent = 'Release to send';
    });
  </script>
</body>
</html>
'''
    return (
        template
        .replace("__CSS_VARIABLES__", css_variables)
        .replace("__STATES__", states)
        .replace("__BARS__", bars)
    )
