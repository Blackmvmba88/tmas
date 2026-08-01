# BlackMamba Visual Index

A macOS-friendly visual engineering control system that maps a repository before themes, colors, typography, motion or component styling are changed.

Source files remain untouched. Every proposal, graph, theme and test template is written into `.visual-index/` for review.

## Current engine — v0.3

- Inventories CSS/Sass/Less, components, layouts, assets, fonts and design files.
- Detects frameworks, visual libraries, Storybook, Playwright and Cypress signals.
- Finds color literals, CSS variables, keyframes, transitions and duplicate assets.
- Resolves local imports and ranks dependency hotspots by visual impact.
- Infers a semantic token contract from the existing palette.
- Generates `light`, `dark`, `blackmamba` and `high-contrast` themes.
- Corrects generated contrast pairs and records WCAG evidence.
- Discovers Next.js, Nuxt, SvelteKit, Astro and static HTML routes.
- Generates a Playwright screenshot matrix across themes and viewports.
- Calculates the transitive visual blast radius of changed files.
- Produces a phased migration plan instead of blindly rewriting a project.

## Install on Mac

```bash
git clone https://github.com/Blackmvmba88/tmas.git
cd tmas
python3 -m pip install --user -e .
```

Scan a project and open its control dashboard:

```bash
visual-index /path/to/project --open
```

## Changed-file impact

Analyze a branch against `main`:

```bash
visual-index . --git-base origin/main --open
```

Or pass paths explicitly:

```bash
visual-index . \
  --changed src/theme/tokens.ts \
  --changed src/components/Button.tsx
```

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
└── CHANGE_IMPACT.md
```

Dynamic routes such as `/artists/:id` are detected but remain disabled until a real example URL is supplied.

## CI guard

```bash
visual-index . --check
```

`--check` exits non-zero when either repository migration risk or changed-file impact reaches `critical`.

## Architecture

```text
Repository
   ↓
Scanner
   ├── files / roles / assets
   ├── colors / variables / motion
   ├── imports / dependency edges
   └── routes / stories / test surfaces
   ↓
Dependency graph + impact scoring
   ├── semantic themes + WCAG audit
   ├── visual regression matrix
   └── changed-file blast radius
   ↓
Dashboard + plans + Playwright templates + CI signal
```

## Safety contract

1. The scanner is read-only.
2. Generated themes never overwrite application source.
3. Dynamic routes are not guessed into active screenshot runs.
4. Tokens remain proposals until reviewed and integrated.
5. Changed-file impact follows reverse dependencies up to three levels.
6. Reduced-motion behavior is built into every generated theme.

## Development

```bash
python3 -m compileall -q visual_index
python3 -m unittest discover -s tests -v
python3 -m visual_index . --output /tmp/tmas-self-scan --check
```

## Next layer

- Screenshot execution orchestration and baseline storage
- GitHub PR annotations with visual risk summaries
- Controlled token adoption with preview/apply/undo
- Figma token export/import adapters
- Cross-repository visual system inventory
