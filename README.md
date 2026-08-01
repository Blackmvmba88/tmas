# BlackMamba Visual Index

A macOS-friendly visual engineering system that maps a repository before themes, colors, typography, motion or component styling are changed.

Source files remain untouched. Every proposal is written into `.visual-index/` for review.

## Current engine

- Inventories CSS/Sass/Less, components, layouts, assets, fonts and design files.
- Detects frameworks, visual libraries, Storybook, Playwright and Cypress signals.
- Finds color literals, CSS variables, keyframes, transitions and duplicate assets.
- Resolves local imports and ranks dependency hotspots by visual impact.
- Infers a semantic token contract from the existing palette.
- Generates `light`, `dark`, `blackmamba` and `high-contrast` themes.
- Audits generated foreground/background pairs against WCAG contrast thresholds.
- Produces a phased migration plan instead of blindly rewriting a project.

## Install on Mac

```bash
git clone https://github.com/Blackmvmba88/tmas.git
cd tmas
python3 -m pip install --user -e .
```

Then scan any repository:

```bash
visual-index /path/to/project --open
```

Or scan the current project:

```bash
visual-index . --open
```

## Generated control room

```text
.visual-index/
├── visual-index.html          # Visual dashboard
├── VISUAL_INDEX.md            # Human-readable architecture map
├── visual-index.json          # Complete machine-readable model
├── semantic-tokens.json       # Inferred semantic contract
├── themes.css                 # Four generated themes + reduced motion
├── accessibility-audit.json   # Contrast evidence
├── dependency-graph.json      # Nodes, edges and impact scores
├── dependency-graph.dot       # Graphviz source
└── MIGRATION_PLAN.md          # Ordered rollout plan
```

## CI guard

```bash
visual-index . --check
```

`--check` exits non-zero when the migration risk reaches `critical`, allowing repositories to block unsafe visual changes.

## Architecture

```text
Repository
   ↓
Scanner
   ├── files / roles / assets
   ├── colors / variables / motion
   └── imports / visual test surfaces
   ↓
Dependency graph + impact scoring
   ↓
Semantic token inference
   ↓
Theme generator + WCAG audit
   ↓
Dashboard + migration plan + CI signal
```

## Safety contract

1. The scanner is read-only.
2. Generated themes never overwrite application source.
3. Tokens are proposals until reviewed and integrated.
4. High-impact files are migrated first and verified with screenshots.
5. Reduced-motion behavior is part of the theme contract, not an afterthought.

## Development

```bash
python3 -m compileall -q visual_index
python3 -m unittest discover -s tests -v
python3 -m visual_index . --output /tmp/tmas-self-scan --check
```

## Roadmap

- Screenshot route discovery and Playwright baseline generation
- Git diff-aware visual impact reports
- Controlled token adoption with preview/apply/undo
- Figma token export/import adapters
- Pull-request annotations for visual risk and contrast regressions
