# BlackMamba Visual Index

A macOS-friendly visual engineering control system that maps a repository before themes, colors, typography, motion or component styling are changed.

Source files remain untouched. Every proposal, graph, theme, baseline manifest, pixel comparison and test template is written into `.visual-index/` for review.

## Current engine — v0.6.2

- Inventories CSS/Sass/Less, components, layouts, assets, fonts and design files.
- Detects frameworks, visual libraries, Storybook, Playwright and Cypress signals.
- Finds color literals, CSS variables, keyframes, transitions and duplicate assets.
- Resolves local imports and ranks dependency hotspots by visual impact.
- Infers semantic tokens and generates light, dark, BlackMamba, Neon Glass and high-contrast themes.
- Corrects generated contrast pairs and records WCAG evidence.
- Discovers Next.js, Nuxt, SvelteKit, Astro and static HTML routes.
- Generates a Playwright screenshot matrix across themes and viewports.
- Calculates the transitive visual blast radius of changed files.
- Inventories screenshot baselines with SHA-256, byte size and PNG dimensions.
- Compares real image pixels and creates normalized diff and heatmap evidence.
- Validates Python 3.10, 3.11, 3.12 and 3.13.
- Publishes the full self-scan as a workflow artifact.
- Creates or updates one persistent visual report comment on every pull request.
- Produces safe preview and Playwright runners that never install dependencies silently.

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

## BlackMamba Neon Glass

The preset translates the voice-interface reference into a reusable component contract:

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

The panel is intentionally wide and low. Its border has a thin amber core and a restrained halo along straight sections. Additional bloom is localized to the four rounded corners so the line does not become uniformly thick.

Every scan produces:

```text
.visual-index/
├── blackmamba-neon-glass.json
├── blackmamba-neon-glass.css
├── blackmamba-neon-glass-corner-bloom.css
├── blackmamba-neon-glass-demo.html
└── serve-neon-glass-demo.sh
```

### Open the preview safely

Do not open the HTML through a blocked popup or `file://` navigation. Serve it through loopback HTTP:

```bash
.visual-index/serve-neon-glass-demo.sh
```

The launcher:

- Binds only to `127.0.0.1`.
- Uses Python's built-in HTTP server.
- Opens `http://127.0.0.1:8765/blackmamba-neon-glass-demo.html` on macOS.
- Does not access the network, microphone or external services.
- Stops when you press `Ctrl+C`.

Use a different local port when needed:

```bash
BM_PREVIEW_PORT=8877 .visual-index/serve-neon-glass-demo.sh
```

The demo cycles through `idle`, `recording` and `ready-to-send`. Reduced-motion mode disables waveform animation and glow transitions.

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

The comment uses a hidden marker, so later pushes update the existing report instead of creating duplicates.

## Run generated screenshots

Start the target application first, then execute:

```bash
.visual-index/run-visual-baseline.sh
```

The runner uses `npx --no-install`; it stops with explicit setup instructions when Playwright is missing. It never downloads packages or browsers on its own.

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

`--check` exits non-zero when a configured screenshot breaches its pixel threshold, changes dimensions, cannot be read, or when any aggregate visual risk reaches `critical`.

## Safety contract

1. Source projects are read-only.
2. Generated themes and presets never overwrite application code.
3. Dynamic routes remain disabled until concrete examples are supplied.
4. Baseline comparison does not mutate screenshots.
5. Pixel artifacts are written only under the selected report output directory.
6. CI repository content permission is read-only; write permission is limited to issue and pull-request reporting.
7. Generated runners refuse implicit dependency installation.
8. The preview server binds only to loopback.
9. Reduced-motion behavior is built into every generated theme.

## Development

```bash
python3 -m pip install -e .
python3 -m compileall -q visual_index
python3 -m unittest discover -s tests -v
python3 -m visual_index . --output /tmp/tmas-self-scan --check
```

## Next layer

- CI baseline artifact retrieval and cross-run comparison
- Controlled token adoption with preview/apply/undo
- Figma token export/import adapters
- Cross-repository visual system inventory
