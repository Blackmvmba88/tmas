# BlackMamba Visual Index

A macOS-friendly visual engineering control system that maps a repository before themes, colors, typography, motion or component styling are changed.

Source files remain untouched. Every proposal, graph, theme, baseline manifest, pixel comparison and test template is written into `.visual-index/` for review.

## Current engine — v0.7.0

- Inventories CSS/Sass/Less, components, layouts, assets, fonts and design files.
- Detects frameworks, visual libraries, Storybook, Playwright and Cypress signals.
- Finds color literals, CSS variables, keyframes, transitions and duplicate assets.
- Resolves local imports and ranks dependency hotspots by visual impact.
- Infers semantic tokens and generates light, dark, BlackMamba, Neon Glass and high-contrast themes.
- Corrects generated contrast pairs and records WCAG evidence.
- Discovers application routes and generates a Playwright screenshot matrix.
- Calculates transitive visual impact for changed files.
- Inventories and compares screenshot baselines with real pixel evidence.
- Generates normalized diff images and heatmaps.
- Publishes visual evidence and one persistent report comment on every pull request.
- Includes an interactive UI Component Lab for designing, comparing and scoring components.
- Validates Python 3.10, 3.11, 3.12 and 3.13.

## Install on Mac

```bash
git clone https://github.com/Blackmvmba88/tmas.git
cd tmas
python3 -m pip install --user -e .
```

Scan a project:

```bash
visual-index /path/to/project --open
```

## UI Component Lab

The lab is the visual approval room. It starts with twelve candidates across buttons, inputs, toggles, chips and cards.

Included workflows:

- Search and category filters.
- Neon, Chrome and Aurora environments.
- Global glow-intensity control.
- Real hover, active, selected and disabled states.
- Score from 1 to 10.
- Approve, revise or reject verdicts.
- Per-component review notes.
- Two-component comparison mode.
- Browser-local persistence.
- Review export as JSON.
- Reduced-motion and keyboard-focus behavior.

Run it safely over loopback HTTP:

```bash
python3 serve-ui-lab.py
```

The browser opens:

```text
http://127.0.0.1:8770/
```

Use another port when needed:

```bash
python3 serve-ui-lab.py --port 8771
```

The server binds only to `127.0.0.1`, installs nothing and stops with `Ctrl+C`.

### First review round

```text
BM-BTN-001  Neon Amber Core
BM-BTN-002  Liquid Chrome
BM-BTN-003  Aurora Border
BM-BTN-004  Holographic Solid
BM-BTN-005  Glass Ghost
BM-BTN-006  Coquette Ribbon
BM-ICO-001  Cyan Send Orb
BM-INP-001  Neon Search Field
BM-TGL-001  Orange Listening Toggle
BM-CHP-001  Pink Filter Chip
BM-CRD-001  Glass Action Card
BM-BTN-007  Disabled System State
```

## BlackMamba Neon Glass

The voice-interface preset uses this component contract:

```text
headline: Just start talking
panel:    Mic | elastic waveform | send
helper:   Hold to record
```

State colors:

```text
idle action       violet
active microphone orange
ready send        cyan
panel structure   amber
waveform          white
```

The panel remains wide and low. Its border has a thin amber core and a restrained halo along straight sections. Additional bloom is localized to the four rounded corners.

Every scan produces:

```text
.visual-index/
├── blackmamba-neon-glass.json
├── blackmamba-neon-glass.css
├── blackmamba-neon-glass-corner-bloom.css
├── blackmamba-neon-glass-demo.html
└── serve-neon-glass-demo.sh
```

Open the generated preview through loopback HTTP:

```bash
.visual-index/serve-neon-glass-demo.sh
```

## Changed-file impact

```bash
visual-index . --git-base origin/main --open
```

Or pass files explicitly:

```bash
visual-index . \
  --changed src/theme/tokens.ts \
  --changed src/components/Button.tsx
```

## Baseline lifecycle

Inventory current screenshots:

```bash
visual-index . --baseline-dir tests/visual-snapshots
```

Compare current screenshots with a previous directory and manifest:

```bash
visual-index . \
  --baseline-dir tests/visual-current \
  --previous-baseline-dir tests/visual-previous \
  --compare-baseline reports/previous/baseline-manifest.json \
  --pixel-threshold 16 \
  --max-diff-ratio 0.01 \
  --check \
  --open
```

Defaults:

- A pixel counts as changed when any RGB channel differs by more than `16`.
- A screenshot passes when no more than `1%` of its pixels changed.
- Dimension changes always require review.

## Pull-request reporting

On every pull request, GitHub Actions:

1. Checks out full git history.
2. Runs the visual scanner against the PR base commit.
3. Executes the Python 3.10–3.13 validation matrix.
4. Adds `PR_VISUAL_SUMMARY.md` to the Actions Job Summary.
5. Uploads the complete `.visual-index` report as `visual-index-self-scan`.
6. Creates or updates one bot comment containing migration, changed-file, baseline and pixel risk.

## Generated control room

```text
.visual-index/
├── visual-index.html
├── VISUAL_INDEX.md
├── visual-index.json
├── semantic-tokens.json
├── themes.css
├── accessibility-audit.json
├── dependency-graph.json
├── dependency-graph.dot
├── MIGRATION_PLAN.md
├── visual-regression-plan.json
├── visual-regression.spec.ts
├── playwright.visual.config.ts
├── VISUAL_REGRESSION.md
├── change-impact.json
├── CHANGE_IMPACT.md
├── baseline-manifest.json
├── baseline-diff.json
├── BASELINE.md
├── pixel-diff.json
├── PIXEL_DIFF.md
├── pixel-diffs/
├── blackmamba-neon-glass.json
├── blackmamba-neon-glass.css
├── blackmamba-neon-glass-corner-bloom.css
├── blackmamba-neon-glass-demo.html
├── serve-neon-glass-demo.sh
├── PR_VISUAL_SUMMARY.md
└── run-visual-baseline.sh
```

## CI guard

```bash
visual-index . --check
```

`--check` exits non-zero when a configured screenshot breaches its pixel threshold, changes dimensions, cannot be read, or when aggregate visual risk reaches `critical`.

## Safety contract

1. Source projects remain read-only.
2. Generated themes and presets never overwrite application code.
3. Dynamic routes remain disabled until concrete examples are supplied.
4. Baseline comparison does not mutate screenshots.
5. Pixel artifacts are written only under the selected report output directory.
6. CI repository content permission is read-only; write permission is limited to pull-request reporting.
7. Generated runners refuse implicit dependency installation.
8. Preview servers bind only to loopback.
9. UI Lab reviews remain local until explicitly exported.
10. Reduced-motion behavior is built into generated themes and the UI Lab.

## Development

```bash
python3 -m pip install -e .
python3 -m compileall -q visual_index serve-ui-lab.py
python3 -m unittest discover -s tests -v
python3 -m visual_index . --output /tmp/tmas-self-scan --check
```

## Next layer

- Approved-component promotion into semantic design tokens.
- Controlled token adoption with preview/apply/undo.
- Screenshot baselines for every approved UI Lab candidate.
- Figma token export/import adapters.
- Cross-repository visual-system inventory.
