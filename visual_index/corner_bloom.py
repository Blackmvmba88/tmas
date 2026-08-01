from __future__ import annotations

CORNER_BLOOM_CSS = r'''
[data-theme="blackmamba-neon-glass"] {
  --bm-edge-core: rgba(255, 225, 174, 0.96);
  --bm-corner-bloom-mid: rgba(255, 145, 69, 0.72);
  --bm-corner-bloom-outer: rgba(255, 91, 0, 0.28);
  --bm-corner-bloom-size: 88px;
  --bm-corner-bloom-inset: 18px;
  --bm-corner-bloom-blur: 12px;
  --bm-corner-bloom-idle-opacity: 0.54;
  --bm-corner-bloom-active-opacity: 0.96;
}

.voice-panel {
  position: relative;
  isolation: isolate;
  overflow: visible;
}

.voice-panel::before {
  content: "";
  position: absolute;
  inset: calc(-1 * var(--bm-corner-bloom-inset));
  z-index: -1;
  pointer-events: none;
  border-radius: calc(var(--bm-radius-panel) + var(--bm-corner-bloom-inset));
  background:
    radial-gradient(circle at 0 0,
      var(--bm-edge-core) 0 4%,
      var(--bm-corner-bloom-mid) 13%,
      var(--bm-corner-bloom-outer) 34%,
      transparent 70%) top left / var(--bm-corner-bloom-size) var(--bm-corner-bloom-size) no-repeat,
    radial-gradient(circle at 100% 0,
      var(--bm-edge-core) 0 4%,
      var(--bm-corner-bloom-mid) 13%,
      var(--bm-corner-bloom-outer) 34%,
      transparent 70%) top right / var(--bm-corner-bloom-size) var(--bm-corner-bloom-size) no-repeat,
    radial-gradient(circle at 0 100%,
      var(--bm-edge-core) 0 4%,
      var(--bm-corner-bloom-mid) 13%,
      var(--bm-corner-bloom-outer) 34%,
      transparent 70%) bottom left / var(--bm-corner-bloom-size) var(--bm-corner-bloom-size) no-repeat,
    radial-gradient(circle at 100% 100%,
      var(--bm-edge-core) 0 4%,
      var(--bm-corner-bloom-mid) 13%,
      var(--bm-corner-bloom-outer) 34%,
      transparent 70%) bottom right / var(--bm-corner-bloom-size) var(--bm-corner-bloom-size) no-repeat;
  filter: blur(var(--bm-corner-bloom-blur));
  opacity: var(--bm-corner-bloom-idle-opacity);
  transition: opacity 180ms ease;
}

.voice-panel[data-state="recording"]::before,
.voice-panel[data-state="ready-to-send"]::before {
  opacity: var(--bm-corner-bloom-active-opacity);
}

@media (prefers-reduced-motion: reduce) {
  .voice-panel::before { transition: none; }
}
'''.strip() + "\n"


def render_corner_bloom_css() -> str:
    """Return the optional corner-localized glow layer for Neon Glass."""
    return "/* Corner-localized refinement for BlackMamba Neon Glass. */\n" + CORNER_BLOOM_CSS


def enhance_neon_glass_demo(document: str) -> str:
    """Inject the corner bloom layer into the generated standalone demo."""
    marker = "  </style>"
    if marker not in document:
        raise ValueError("Neon Glass demo is missing its closing style tag")
    return document.replace(marker, f"\n{CORNER_BLOOM_CSS}\n{marker}", 1)
